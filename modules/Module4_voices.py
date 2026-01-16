import random

from core import Module1_txt as Txt
from core.Module2_json_loader import json_loader
from core.Module14_communication import Server

class Voices:

    def __init__(self):
        self.voices:dict[str,dict[str,list[str]]] = json_loader.load("voices")

        self.server:Server|None = None

    def report(self, who:str, theme:str, print_who=True):
        """
        展示voices.json中记录的语音内容
        :param who: 语音发出者
        :param theme: 语音主题
        :param print_who: 是否打印语音发出者
        :return:
        """
        try:
            if print_who:
                txt = f"[{who}]" + random.choice(self.voices[who][theme])
            else:
                txt = random.choice(self.voices[who][theme])
            Txt.print_plus(txt)
            if self.server:
                self.server.send_str(txt)
        except KeyError:
            print(f"语音未定义-[{who}]{theme}")

    def set_server(self, server:Server):
        self.server = server

    def clear_server(self):
        self.server = None

    #def send_and_report(self, who:str, theme:str,server:Server,print_who=True):
    #    """
    #    展示voices.json中记录的语音内容
    #    :param who: 语音发出者
    #    :param theme: 语音主题
    #    :param print_who: 是否打印语音发出者
    #    :param server: 语音发送服务器
    #    :return:
    #    """
    #    try:
    #        if print_who:
    #            txt = f"[{who}]" + random.choice(self.voices[who][theme])
    #        else:
    #            txt = random.choice(self.voices[who][theme])
    #        server.send_str(txt)
    #        Txt.print_plus(txt,should_wait=False)
    #    except KeyError:
    #        print(f"语音未定义-[{who}]{theme}")
    #        server.send_str(f"语音未定义-[{who}]{theme}")

    def inject_and_report(self, who:str, theme:str, data_injected=None, print_who=True):
        """
        注入数据并展示voices.json中记录的语音内容
        :param who: 语音发出者
        :param theme: 语音主题
        :param print_who: 是否打印语音发出者
        :param data_injected: 注入字典
        :return:
        """
        if data_injected is None:
            data_injected = {}
        try:
            if print_who:
                txt:str = f"[{who}]" + random.choice(self.voices[who][theme])
            else:
                txt:str = random.choice(self.voices[who][theme])
            formatted_txt = txt.format_map(data_injected)
            Txt.print_plus(formatted_txt)
        except KeyError:
            print(f"语音未定义-[{who}]{theme}")
voices = Voices()