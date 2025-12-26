import random
import shelve
import os
from copy import deepcopy

from core import Module1_txt as Txt
from core.Module2_json_loader import json_loader

AL_META_DATA = json_loader.load("al_meta_data")
ENTRY_META_DATA = json_loader.load("entries_meta_data")

class StorageManager:

    def __init__(self):
        self.username:str = ""
        # 建立模板
        self.template:dict[str,dict[str,str|int|dict[str,int]]] = json_loader.load("storage_template")
        for al_index_str in AL_META_DATA.keys():
            self.template["als"][al_index_str] = 0
        for entry_index in ENTRY_META_DATA:
            self.template["metadata"]["entry_rank"][entry_index] = 0
        # 建立空模板
        self.template_empty = deepcopy(self.template)
        # 建立映射表
        self.item_to_key_table:dict[str,str] = {}
        for key in self.template:
            for item in self.template[key]:
                self.item_to_key_table[item] = key
        # 建立统计字段
        self.total_materials_num = 0
        self.total_als_num = 0
        # 启动主仓库
        if not os.path.exists('userdata'):
            os.makedirs('userdata')
        self.repository_for_all_users = shelve.open('userdata/game_save',writeback=True)

    def update_statistical_data(self):
        """
        更新统计字段
        :return: 无
        """
        self.total_materials_num = sum(self.repository_for_all_users[self.username]["materials"].values())
        self.total_als_num = sum(self.repository_for_all_users[self.username]["als"].values())

    def sync(self):
        """
        将仓库同步至硬盘
        :return: 无
        """
        self.update_statistical_data()
        self.repository_for_all_users.sync()

    def login(self):
        """
        登录|将硬盘数据写入模板|新建用户|重灌入硬盘
        :return: 无
        """
        self.username = Txt.input_plus("指挥官，请输入您的代号")
        if self.username in self.repository_for_all_users.keys():
            for key in self.repository_for_all_users[self.username]:
                if key not in self.template:
                    continue
                for item in self.repository_for_all_users[self.username][key]:
                    if item not in self.template[key]:
                        continue
                    self.template[key][item] = self.repository_for_all_users[self.username][key][item]
        else:
            Txt.print_plus("初次登录|欢迎指挥官")
        self.repository_for_all_users[self.username] = self.template
        # 更新统计字段
        self.update_statistical_data()
        self.sync()

    def logout(self):
        Txt.print_plus(f"指挥官{self.username}请求登出")
        Txt.print_plus("登出完毕")
        self.repository_for_all_users.close()

    def set_ship_name(self):
        """
        设置舰船名字
        :return: 无
        """
        new_name = Txt.input_plus("请输入舰船的新名称|[enter]取消")
        if new_name == "":
            return
        self.repository_for_all_users[self.username]["metadata"]["ship_name"] = new_name
        self.sync()


    def show_assets(self) -> dict[str:int]:
        """
        展示现有仓库资产
        :return: 字典，键为所有的materials|currency|Als，值为它们的数目
        """
        out = {}
        for key in ["materials","als","currency"]:
            for item in self.repository_for_all_users[self.username][key]:
                out[item] = self.repository_for_all_users[self.username][key][item]
        return out

    def show_assets_except_al(self) -> dict[str:int]:
        """
        展示现有仓库资产,Als除外
        :return: 字典，键为所有的materials|currency，值为它们的数目
        """
        out = {}
        for key in ["materials","currency"]:
            for item in self.repository_for_all_users[self.username][key]:
                out[item] = self.repository_for_all_users[self.username][key][item]
        return out

    def modify(self,item:str,delta:int):
        """
        增减仓库物品数量|核心业务封装
        :param item:需要改变数量的物品
        :param delta:物品数量改变量
        :return: 无
        """
        key:str = self.item_to_key_table[item]
        self.repository_for_all_users[self.username][key][item] += delta
        self.sync()

    def get_value_of(self,item:str) -> int|str:
        """
        查找仓库物品数量或元数据值|核心业务封装
        :param item:需查找的物品或键
        :return: 物品在仓库中的数量或元数据值
        """
        key: str = self.item_to_key_table[item]
        return self.repository_for_all_users[self.username][key][item]

    def drop_for_fight(self):
        """
        单局战斗后掉落物结算|1100信用点|2种物品各12.5个
        :return: 无
        """
        money = random.randint(1000, 1200)
        self.modify("联邦信用点",money)
        print(f"[赏金到账]信用点x{money}")
        items = random.sample(list(self.template["materials"].keys()),2)
        for item in items:
            num = random.randint(10,15)
            self.modify(item,num)
            print(f"[战利品收集] {item}x{num}")
        self.sync()

    def transaction(self,give_list:dict[str,int],get_list:dict[str,int]):
        for item in give_list:
            self.modify(item,-give_list[item])
        for item in get_list:
            self.modify(item,get_list[item])
        self.sync()

    def clear(self):
        """
        清空当前登录玩家的仓库
        :return: 无
        """
        self.repository_for_all_users[self.username] = self.template_empty
        self.sync()

    def save_al_on_ship(self,al_on_ship):
        al_str_list = ["","",""]
        for position in range(len(al_on_ship)):
            try:
                al_str_list[position] = str(al_on_ship[position].index)
            except AttributeError:
                al_str_list[position] = ""
        self.repository_for_all_users[self.username]["metadata"]["al_on_ship"] = al_str_list
        self.sync()

    def get_al_on_ship(self):
        return self.repository_for_all_users[self.username]["metadata"]["al_on_ship"]

    def print_storage(self):
        al_list = {}
        for al,num in self.repository_for_all_users[self.username]["als"].items():
            if num != 0:
                al_list[AL_META_DATA[al]["len_name"]] = num
        Txt.n_column_print(
            [
                Txt.Tree("基本物资", self.repository_for_all_users[self.username]["materials"]).generate_line_list(),
                Txt.Tree("终焉结", al_list).generate_line_list()
            ]
        )
        input("[enter]离开仓库>>>")

    def have_all_al_on_ship(self,al_on_ship:list) -> bool:
        """
        判断是否拥有船上所有的终焉结
        :param al_on_ship: list[Al_general|None]，my_ship对象的属性
        :return: True表示船上所有终焉结在仓库里都有存货
        """
        count = 0
        for al in al_on_ship:
            if not al:
                count += 1
                continue
            if al.rank_num == 0:
                count += 1
                continue
            al_str = str(al.index)
            if self.get_value_of(al_str) > 0:
                count += 1
        return count == len(al_on_ship)

    def has_enough_ssd(self,total_rank:int):
        """
        判断是否有足够的保险点，一并打印结果。
        :param total_rank: 舰船终焉结总级数
        :return: True表示信用点足够，False反之。
        """
        ssd = self.get_value_of("保险点")
        if ssd >= total_rank:
            print("当前信用点已覆盖所有终焉结>所有终焉结已保全")
            return True
        else:
            print("当前信用点未覆盖舰船")
            return False

    def cost_ssd(self,total_rank:int):
        self.modify("保险点",-total_rank)
        print(f"{total_rank}保险点从账户扣除·感谢使用星际保险服务")

    def destroy_al(self, al_on_ship:list):
        """
        损毁船上所有的终焉结
        :param al_on_ship: list[Al_general|None]，my_ship对象的属性
        :return: 无
        """
        for al in al_on_ship:
            if not al:
                continue
            if al.rank_num == 0:
                continue
            al_str = str(al.index)
            self.modify(al_str,-1)
            print(f"{al.len_name} 已损毁")
            self.sync()

    def save_entry_rank(self,all_entry_rank:dict[str,int]):
        self.repository_for_all_users[self.username]["metadata"]["entry_rank"] = all_entry_rank
        self.sync()

    def get_entry_rank(self) -> dict[str,int]:
        return self.repository_for_all_users[self.username]["metadata"]["entry_rank"]

storage_manager = StorageManager()