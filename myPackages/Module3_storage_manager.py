import random
import shelve
from copy import deepcopy

from . import Module1_txt as Txt
from .Module2_json_loader  import json_loader

class StorageManager:

    def __init__(self):
        self.username:str = ""
        # 建立模板
        self.template:dict[str,dict[str,str|int]] = json_loader.load("storage_template")
        for al_index_str in json_loader.load("al_meta_data").keys():
            self.template["als"][al_index_str] = 0
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
        self.repository_for_all_users = shelve.open('userdata/game_save',writeback=True)
        # 更新统计字段
        self.update_statistical_data()

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
                if key in self.template:
                    for item in self.repository_for_all_users[self.username][key]:
                        if item in self.template[key]:
                            self.template[key][item] = self.repository_for_all_users[self.username][key][item]
        else:
            Txt.print_plus("初次登录|欢迎指挥官")
        self.repository_for_all_users[self.username] = self.template
        self.sync()

    def logout(self):
        Txt.print_plus(f"指挥官{self.username}请求登出")
        Txt.print_plus("登出完毕")
        self.repository_for_all_users.close()

    def modify(self,item:str,delta:int):
        """
        增减仓库物品数量|最终业务封装
        :param item:需要改变数量的物品
        :param delta:物品数量改变量
        :return: 无
        """
        key:str = self.item_to_key_table[item]
        self.repository_for_all_users[self.username][key][item] += delta
        self.sync()

    def drop_for_fight(self):
        """
        单局战斗后掉落物结算|1100信用点|2种物品各13.5个
        :return: 无
        """
        money = random.randint(1000, 1200)
        self.modify("联邦信用点",money)
        print(f"[赏金到账]信用点x{money}")
        items = random.sample(list(self.template["materials"].keys()),2)
        for item in items:
            num = random.randint(11,16)
            self.modify(item,num)
            print(f"[战利品收集] {item}x{num}")
        self.sync()

    def clear(self):
        """
        清空当前登录玩家的仓库
        :return: 无
        """
        self.repository_for_all_users[self.username] = self.template_empty
        self.sync()
storage_manager = StorageManager()