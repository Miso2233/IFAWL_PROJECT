from __future__ import annotations
import time
from typing import Literal
from core.Module10_sound_manager import sounds_manager

def get_shell_len(txt: str) -> int:
    """
    计算字符串在Shell中的显示长度（ASCII字符宽度1，其他宽度2）
    :param txt:
    :return: 字符串在Shell中的显示长度
    """
    total = 0
    for char in txt:
        # ASCII可打印字符通常宽度为1
        if ord(char) < 128 and char.isprintable():
            total += 1
        else:
            total += 2
    return total

def adjust(txt:str,width:int,mode:Literal["left","right"]="left"):
    """
    用空格将原始文本填充至指定的宽度
    :param txt: 根据shell宽度进行文本对齐
    :param width: 目标占据宽度
    :param mode: left|左对齐 right|右对齐
    :return: 调整后的文本
    """
    match mode:
        case "left":
            return txt + " "*(width-get_shell_len(txt))
        case "right":
            return " " * (width-get_shell_len(txt)) + txt

def print_plus(txt:str, sec:float=0.3):
    """
    增强视觉print函数
    :param txt: 文本
    :param sec: 打印总时长
    :return:
    """
    i=len(txt)
    if i<10:
        sec-=0.1
    if sec != 0:
        for j in txt:
            print(j,end="")
            time.sleep(sec/i)
        print("")
        time.sleep(0.2)
    else:
        print(txt)

def input_plus(txt:str,sec:float=0.3):
    """
    增强视觉input函数。如果提示文本没有以>>>结尾则自动加上>>>
    :param txt: 提示文本
    :param sec: 打印总时长
    :return:
    """
    length=len(txt)
    for j in txt:
        print(j,end="")
        time.sleep(sec/length)
    if not txt.endswith(">>>"):
        print(">>>",end="")
    inp = input("")
    return inp

class Tree:#打印用tree对象

    def __init__(self,title,*ag:str|int|list|dict|Tree):
        if not title:
            return
        self.title=title
        self.body=[]
        for i in ag:
            if type(i) == str or type(i) == int:
                self.body.append(i)
            elif isinstance(i, list):
                for j in i:
                    self.body.append(j)
            elif isinstance(i, dict):
                for j in i:
                    self.body.append(adjust(j,10)+f" *{i[j]}")
            elif type(i) == Tree:
                i:Tree
                self.body.append(i.title)
                for j in i.body:
                    self.body.append(f" -{j}")

    def print_self(self, can_be_folded=False):
        print(self.title)
        if can_be_folded and len(self.body) > 3:
            for i in self.body[0:3]:
                print("|")
                print("|-"+str(i))
            print("|")
            print("|>>[已折叠]")
            print("")
        else:
            for i in self.body:
                print("|")
                print("|-"+str(i))
            print("")

    def generate_line_list(self, can_be_folded=False):
        """
        生成Tree对象的行切片
        :param can_be_folded:
        :return: 一个字符串列表，包含Tree的每一行
        """
        line_list= [self.title]
        if can_be_folded and len(self.body) > 3:
            for i in self.body[0:3]:
                line_list.append("|")
                line_list.append("|-"+str(i))
            line_list.append("|")
            line_list.append("|>>[已折叠]")
            line_list.append("")
        else:
            for i in self.body:
                line_list.append("|")
                line_list.append("|-"+i)
            line_list.append("")
        return line_list

class Advanced_tree(Tree):

    def __init__(self, metadata: dict[str, list[str] | str | int], title=None, *ag):
        """
        [注意]这个子类完全重写了父类的构造方法
        :param metadata: 初始化元数据字典
        """
        super().__init__(title, *ag)
        self.title_raw:str = metadata["title"]
        self.body_raw:list[str] = metadata["line_list"]
        self.title = ""
        self.body = ["" for _ in range(len(self.body_raw))]
        self.col:int = metadata["col"]
        self.row:int = metadata["row"]
        self.metadata = metadata
        self.can_be_folded = metadata.get("can_be_folded",False)

    def inject(self,inject_data:dict[str,str|int]):
        self.title = self.title_raw.format_map(inject_data)
        for i in range(len(self.body_raw)):
            try:
                self.body[i] = self.body_raw[i].format_map(inject_data)
            except KeyError:
                pass

    def rewrite_lines(self,lines:list[str]):
        """
        重写（注入）新的行
        :param lines: 注入的行
        :return: 无
        """
        self.body = lines

    def generate_line_list(self,can_be_folded=False):
        """
        生成Advanced_tree对象的行切片，将读取该树内置的can_be_folded属性
        :return: 一个字符串列表，包含Tree的每一行
        """
        line_list= [self.title]
        if self.can_be_folded and len(self.body) > 3:
            for i in self.body[0:3]:
                line_list.append("|")
                line_list.append("|-"+str(i))
            line_list.append("|")
            line_list.append("|>>[已折叠]")
            line_list.append("")
        else:
            for i in self.body:
                line_list.append("|")
                line_list.append("|-"+i)
            line_list.append("")
        return line_list

def n_column_print(columns: list[list[str]], di_list: tuple[int]|int = ()):
    """
    IFAWL N栏打印引擎
    columns: 二维列表。将要打印的一栏制成行切片（参考Tree.line_list() ），作为该列表的一项
    di_list: 栏左端间距列表。上过小学四年级的都学过植树问题，都知道长度要比columns少1
    """

    len_list = [len(i) for i in columns]
    max_len = max(len_list)

    if di_list == ():
        di_list = [50 for _ in range(len(columns) - 1)]
    elif type(di_list) == int:
        di = di_list
        di_list = [di for i in range(len(columns) - 1)]

    for i in range(len(columns)):
        for p in range(len(columns[i]), max_len):
            columns[i].append("")

    for line_index in range(0, len(columns[0])):
        line_str = ""
        column_index = 0
        for line_list in columns[:-1]:
            line_str += adjust(line_list[line_index], di_list[column_index])
            column_index += 1
        line_str += columns[-1][line_index]
        print(line_str)


def dict_give_and_get_print(father: dict, get: dict, give: dict):
    def print_main(zoom):
        print(i,end=" "*(12-get_shell_len(i)))
        if i in give:
            print("-"*((father[i]-give[i])//zoom),end="")
            print("<"*(give[i]//zoom),end="")
            print(f"  {father[i]}-{give[i]}")
        elif i in get:
            print("-"*(father[i]//zoom),end="")
            print(">"*(get[i]//zoom),end="")
            print(f"  {father[i]}+{get[i]}")
        else:
            print("-"*(father[i]//zoom),end="")
            print(f"  {father[i]}")

    for i in father:
        if i not in ["联邦信用点","合约纪念点","保险点"]:
            print_main(5)
        elif i == "联邦信用点":
            print_main(400)
        elif i == "保险点":
            print_main(1)
    print()

def ask_plus(txt:str,kword:list):
    kword_str = kword.copy()
    kword_str = [str(j) for j in kword]
    while 1:
        inp=input_plus(txt)
        if inp in kword_str:
            break
        else:
            print("请在可选范围内输入")
    return  inp