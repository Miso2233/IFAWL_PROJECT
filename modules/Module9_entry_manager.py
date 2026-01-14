from typing import Literal
import random

from core.Module0_enums_exceptions import Modes
from core.Module1_txt import print_plus,Tree
from core.Module2_json_loader import json_loader
from core.Module5_dice import dice
from core.Module14_communication import Server

ALL_ENTRY_METADATA = json_loader.load("entries_meta_data")

# Modes 枚举已移至 core.Module0_enums 模块


class Entry:

    def __init__(self,index:str):
        # 元数据字段
        self.index:str                  = index
        self.metadata:dict              = ALL_ENTRY_METADATA[index]
        self.max_rank:int               = len(self.metadata["points"]) - 1
        self.title:str                  = self.metadata["title"]
        self.points_list:list[int]      = self.metadata["points"]
        self.description_list:list[str] = self.metadata["description_txt"]
        self.summary:str                = self.metadata["summary"]
        self.reaction:str               = self.metadata["reaction"]
        self.can_flow:bool              = self.metadata["can_flow"]

        # 通用查表字段
        self.RANK_STR_LIST = ["","I","II","III","IV","V"]

        # 调用字段
        self.selected_rank = 0
        self.flow_rank = 0
        self.point = 0

    def set_rank(self,rank:int):
        """
        设置词条等级，若输入非法则报ValueError
        :param rank: 要设置的等级
        :return: 无
        """
        if rank < 0 or rank > self.max_rank:
            raise ValueError
        self.selected_rank = rank
        self.point = self.points_list[rank]

    def print_description(self):
        title = f"[{self.index}]“{self.title}”：{self.summary}"
        body = []
        for rank in range(1,len(self.description_list)):
            is_chosen="[●已选中]" if rank == self.selected_rank else ""
            body.append(f"[{self.RANK_STR_LIST[rank]}]{self.description_list[rank]}[{self.points_list[rank]}分]{is_chosen}")

        Tree(title,body).print_self()

    def print_when_react(self):
        if entry_manager.server:
            entry_manager.server.send_str(f"[警告] 词条 {self.title} 被触发 >>> {self.reaction}")
            print_plus(f"[警告] 词条 {self.title} 被触发 >>> {self.reaction}",should_wait=False)
            return
        print_plus(f"[警告] 词条 {self.title} 被触发 >>> {self.reaction}")

    def is_not_full(self) -> bool:
        """
        检查自己的flow_rank是否满级
        :return: True代表未满级（可升级）。若词条元数据写明"can_flow": false，则必然返回False
        """
        return self.flow_rank < self.max_rank and self.can_flow

class EntryManager:

    def __init__(self):
        self.all_entries = {index:Entry(index) for index in ALL_ENTRY_METADATA}
        self.current_mode:Literal["FIGHT","DISASTER","INFINITY"] = "FIGHT"
        self.server = None

    # 设置模式

    def set_mode(self,mode:Literal["FIGHT","DISASTER","INFINITY"]):
        self.current_mode = mode

    def set_server(self,server:Server):
        self.server = server

    def clear_server(self):
        self.server = None
    # 静态词条方法

    def print_all_descriptions(self):
        for entry in self.all_entries.values():
            entry.print_description()

    def print_chosen_as_tree(self):
        title = f"当前选择的词条 [总分:{self.count_total_points()}]"
        body = self.generate_entry_summary_lines()
        Tree(
            title,
            body
        ).print_self()

    def clear_all_selected(self):
        for entry in self.all_entries.values():
            entry.selected_rank = 0

    def push_all_full(self):
        for entry in self.all_entries.values():
            entry.selected_rank = entry.max_rank

    def set_all_rank(self,all_entry_rank:dict[str,int]):
        for entry_index,rank in all_entry_rank.items():
            self.all_entries[entry_index].selected_rank = rank

    def get_all_rank(self) -> dict[str,int]:
        """
        取得所有词条的静态等级字典
        :return: 一个字典，键为词条的字符串编号，值为其等级
        """
        return {entry_index: entry.selected_rank for entry_index, entry in self.all_entries.items()}

    def count_total_points(self) -> int:
        """
        计算所有已选择词条的总分
        :return: 总分
        """
        out = 0
        for entry in self.all_entries.values():
            out += entry.points_list[entry.selected_rank]
        return out

    def generate_entry_summary_lines(self):
        out = []
        for entry in self.all_entries.values():
            if entry.selected_rank != 0:
                out.append(f"[{entry.index}]{entry.title}{entry.RANK_STR_LIST[entry.selected_rank]}:{entry.description_list[entry.selected_rank]}[{entry.points_list[entry.selected_rank]}分]")
        return out

    def print_all_selected_rank(self):
        out = ""
        for entry in self.all_entries.values():
            if entry.selected_rank != 0:
                out += f"{entry.title}[{entry.RANK_STR_LIST[entry.selected_rank]}]  "
        if not out:
            out = "[无激活词条]"
        print(out)
        print()

    def generate_str_of_all_selected_rank(self):
        out = ""
        for entry in self.all_entries.values():
            if entry.selected_rank != 0:
                out += f"{entry.title}[{entry.RANK_STR_LIST[entry.selected_rank]}]  "
        if not out:
            out = "[无激活词条]"
        return out + "\n\n"

    # 级别检索

    def get_rank_of(self,index:str) -> int:
        """
        基于当前模式得到词条的正确等级
        :param index: 词条编号
        :return: 词条等级。战死之地返回selected_rank，其它则返回flow_rank
        """
        if self.current_mode == Modes.DISASTER  or self.current_mode == Modes.PPVE:
            return self.all_entries[index].selected_rank
        return self.all_entries[index].flow_rank

    # 动态词条方法

    def push_up(self):
        """
        将词条库中的某个词条上推一级
        :return: 无
        """
        entry_list = list(self.all_entries.values())
        random.shuffle(entry_list)
        for entry in entry_list:
            if entry.is_not_full():
                entry.flow_rank += 1
                print_plus(f"[警告]{entry.title} 等级{entry.RANK_STR_LIST[entry.flow_rank]} 已被激活 >>> {entry.description_list[entry.flow_rank]}")
                break

    def pull_down(self):
        """
        将一个已激活词条下拉一级
        :return: 无
        """
        entry_list = list(self.all_entries.values())
        random.shuffle(entry_list)
        for entry in entry_list:
            if entry.flow_rank > 0:
                entry.flow_rank -= 1
                print_plus(f"[抑制剂启动]{entry.title} 已被抑制 >>> {entry.description_list[entry.flow_rank]}")
                break

    def clear_all_flow(self):
        for entry in self.all_entries.values():
            entry.flow_rank = 0

    def print_all_flow_rank(self):
        out = ""
        for entry in self.all_entries.values():
            if entry.flow_rank != 0:
                out += f"{entry.title}[{entry.RANK_STR_LIST[entry.flow_rank]}]  "
        if not out:
            out = "[无激活词条]"
        print(out)
        print()

    # 战斗方法

    def check_and_add_atk(self,atk) -> int:
        """烈风"""
        if dice.probability(self.get_rank_of("1")*0.2):
            atk += 1
            self.all_entries["1"].print_when_react()
        return atk

    def check_and_reduce_atk(self,atk) -> int:
        """虚弱"""
        if self.get_rank_of("3") == 1 and atk > 1 and dice.probability(0.3):
            atk -= 1
            self.all_entries["3"].print_when_react()
        elif self.get_rank_of("3") == 2 and dice.probability(0.3):
            atk -= 1
            self.all_entries["3"].print_when_react()
        return atk

    def check_and_reduce_hp(self,hp:int):
        """灯塔已灭"""
        if dice.probability(self.get_rank_of("6")*0.2):
            hp -= 1
            self.all_entries["6"].print_when_react()
        return hp

    def check_and_add_enemy_hp(self,hp:int,enemy):
        """滋生"""
        if dice.probability(self.get_rank_of("8")*0.2):
            enemy.heal(1)
            self.all_entries["8"].print_when_react()
        return hp

    def check_and_attack_me(self,atk:int,enemy):
        """极限爆发"""
        if self.get_rank_of("9") == 0:
            return atk
        if atk >= enemy.shelter:
            enemy.attack(self.get_rank_of("9"))
            self.all_entries["9"].print_when_react()
        return atk

    def check_and_add_num(self,num:int):
        """烛燃"""
        if num < 0:
            return num
        if dice.probability(self.get_rank_of("10")*0.3):
            num += 1
            self.all_entries["10"].print_when_react()
        return num

    def check_and_reduce_missile(self,atk:int,my_ship):
        """海啸"""
        if dice.probability(self.get_rank_of("12") * 0.2) and my_ship.missile > 0 and atk > 1:
            my_ship.load(-1)
            self.all_entries["12"].print_when_react()
        return atk

    def check_and_get_launch_num(self,enemy):
        """狂怒"""
        if (rank := self.get_rank_of("14")) == 0:
            num = 1
        elif enemy.missile > 4 - rank:
            num = 2
            self.all_entries["14"].print_when_react()
        else:
            num = 1
        return num

entry_manager = EntryManager()