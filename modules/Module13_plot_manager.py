from __future__ import annotations

from core.Module1_txt import print_plus,input_plus,ask_plus
from core.Module2_json_loader import json_loader

ALL_POLT_DATA:dict[str,dict[str,dict[str,str]]|str] = json_loader.load("plots")

class Paragraph:

    def __init__(self, session_str:str, paragraph_str:str):
        # 元数据字段
        self.title = ALL_POLT_DATA[session_str][paragraph_str]["title"]
        self.raw_txt = ALL_POLT_DATA[session_str][paragraph_str]["raw_txt"]
        # 原始文本
        self.lines = self.raw_txt.split("\n\n")
        # 下一段落
        self.next_paragraphs:list[Paragraph] = []

    @staticmethod
    def __processed(line:str):
        """
        处理文本行
        :param line: 原始文本行
        :return: 处理后文本。具有开头协议来传输必要数据
        """
        out = line
        if line.startswith("-"):
            out = "[" + line[1:]
            out = out.replace("-","]")
            return out
        if line.startswith("【") and line.endswith("】"):
            content = line[1:-1]
            out = "[enter]" + content
            return out
        if line.startswith("+"):
            count = 0
            while "+" in out:
                out = out.replace("+",f" |[{count}] ",1)
                count += 1
            return f"+{count}+" + out
        if line.startswith("/"):
            count = 0
            while "/" in out:
                out = out.replace("/",f" |[{count}] ",1)
                count += 1
            return f"/{count}/" + out
        return out

    def play(self,info_map) -> Paragraph:
        """
        播放一个段落，并返回应播放的下一个段落
        :param info_map: 注入信息字典
        :return: 下一个段落
        """
        next_index = 0
        for line in self.lines:
            processed = self.__processed(line)
            processed = processed.format_map(info_map)
            if processed.startswith("[enter]"): # 非输入回车
                input_plus(processed)
                print()
            elif processed.startswith("+"): # 剧情分支的多选项
                count = int(processed[1])
                content = processed[3:]
                next_index = int(ask_plus(content,list(range(0,count))))
                print()
            elif processed.startswith("/"):  # 非剧情分支的多选项
                count = int(processed[1])
                content = processed[3:]
                ask_plus(content, list(range(0, count)))
                print()
            else:
                print_plus(processed)
                print()
        return self.next_paragraphs[next_index]


class Session:
    """
    会话类，封装一个会话的所有段落
    """
    def __init__(self, session_str: str):
        # 元数据字段
        self.title:str = ALL_POLT_DATA[session_str]["session_title"]
        self.session_index:int = int(session_str)
        self.paragraphs: dict[int, Paragraph] = {}
        self.has_been_played:bool = False
        
        # 创建段落对象
        for paragraph in ALL_POLT_DATA[session_str]:
            if not paragraph.isdigit(): # 跳过段落元数据
                continue
            self.paragraphs[int(paragraph)] = Paragraph(session_str, paragraph)
        
        # 设置每个段落的后续段落链接
        for paragraph_key, paragraph_data in ALL_POLT_DATA[session_str].items():
            if not paragraph_key.isdigit(): # 跳过段落元数据
                continue
            paragraph_id = int(paragraph_key)
            current_plot = self.paragraphs[paragraph_id]

            # 如果明确定义了下一个段落，则使用它
            if "next_paragraph" in paragraph_data:
                for next_paragraph_index in paragraph_data["next_paragraph"]:
                    next_plot = self.paragraphs[int(next_paragraph_index)]
                    current_plot.next_paragraphs.append(next_plot)
            # 否则，自动链接到下一个段落（如果是最后一个段落则链接到None）
            else:
                is_last_paragraph = (paragraph_id == len(self.paragraphs) - 1)
                next_plot = None if is_last_paragraph else self.paragraphs[paragraph_id + 1]
                current_plot.next_paragraphs.append(next_plot)
                
        # 第一个段落
        self.first_paragraph = self.paragraphs[0] if 0 in self.paragraphs else None

    def play(self, info_map: dict):
        """
        播放整个会话，同时更新已播放标签
        :param info_map: 注入信息字典
        :return: 无
        """
        current = self.first_paragraph
        while current is not None:
            current = current.play(info_map)
        self.has_been_played = True

class PlotManager:
    def __init__(self):
        self.sessions: dict[int, Session] = {}
        
        # 创建每个会话对象
        for session in ALL_POLT_DATA:
            session_index = int(session)
            self.sessions[session_index] = Session(session)
            
        # 信息映射表
        self.information_map = {}

        # 存储管理器
        self.storage_manager = None

    # ==================== 依赖注入 ====================

    def set_information_map(self, info_map: dict):
        self.information_map = info_map

    def set_storage_manager(self, storage_manager):
        self.storage_manager = storage_manager

    # ==================== 剧情保存 ====================

    def save_session(self, session_index: int):
        """
        将一个会话保存为已播放。storage_manager.save_story_progress()的封装
        :param session_index: 会话整数编号
        :return: 无
        """
        self.storage_manager.save_session_progress(str(session_index))

    def load_session(self):
        """
        从存储管理器中加载会话播放状态
        :return: 无
        """
        for session,state in self.storage_manager.get_session_progress().items():
            self.sessions[int(session)].has_been_played = state

    # ==================== 剧情播放 ====================

    def play_session(self, session: int):
        """
        播放一个会话|核心业务封装
        :param session: 会话编号
        :return: 无
        """
        self.sessions[session].play(self.information_map)
        self.save_session(session)

    def try_to_play_when_login(self):
        """
        尝试在登录时播放会话
        :return: 无
        """
        if not self.sessions[0].has_been_played:
            self.play_session(0)

plot_manager = PlotManager()