import random
import shelve
import os
from copy import deepcopy

from core import Module1_txt as Txt
from core.Module2_json_loader import json_loader
from core.Module8_al_industry import recipe_for_all_al

AL_META_DATA = json_loader.load("al_meta_data")
ENTRY_META_DATA = json_loader.load("entries_meta_data")
ALL_POLT_DATA:dict[str,dict[str,dict[str,str]]|str] = json_loader.load("plots")

class StorageManager:
    
    # ==================== 初始化与基础设置 ====================
    
    def __init__(self):
        self.username:str = ""
        # 建立模板
        self.template:dict[str,dict[str,str|int|dict[str,int]]] = json_loader.load("storage_template")
        for al_str in AL_META_DATA:
            self.template["als"][al_str] = 0
        for entry_str in ENTRY_META_DATA:
            self.template["metadata"]["entry_rank"][entry_str] = 0
        for session_str in ALL_POLT_DATA:
            self.template["metadata"]["plot_progress"][session_str] = False
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
    
    # ==================== 用户管理 ====================
    
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
        # hello
        Txt.print_plus(f"指挥官代号识别成功·{self.get_value_of('ship_name')}号护卫舰正在启动·欢迎来到浅草寺")
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
    
    # ==================== 数据存取与同步 ====================
    
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
    
    def clear(self):
        """
        清空当前登录玩家的仓库
        :return: 无
        """
        self.repository_for_all_users[self.username] = self.template_empty
        self.sync()
    
    # ==================== 仓库资产管理 ====================
    
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
        :param item: 需查找的物品或键
        :return: 物品在仓库中的数量或元数据值
        """
        key: str = self.item_to_key_table[item]
        return self.repository_for_all_users[self.username][key][item]
    
    def set_value_of(self,item:str,val):
        """
        设置仓库内物品或元数据的值|核心业务封装
        :param item: 需设置的物品或键
        :param val: 需设置的值
        :return: 无
        """
        key: str = self.item_to_key_table[item]
        self.repository_for_all_users[self.username][key][item] = val
    
    def transaction(self,give_list:dict[str,int],get_list:dict[str,int]):
        """
        进行一次交易|核心业务封装
        :param give_list: 交付 字典
        :param get_list: 得到 字典
        :return: 无
        """
        for item in give_list:
            self.modify(item,-give_list[item])
        for item in get_list:
            self.modify(item,get_list[item])
        self.sync()
    
    def print_storage(self):
        al_list = {}
        for al,num in self.repository_for_all_users[self.username]["als"].items():
            if num != 0:
                al_list[AL_META_DATA[al]["len_name"]] = num
        Txt.n_column_print(
            [
                Txt.Tree("基本物资 Basic Materials", self.repository_for_all_users[self.username]["materials"]).generate_line_list(),
                Txt.Tree("终焉结 Apocalypse-Linked", al_list).generate_line_list()
            ]
        )
        input("[enter]离开仓库>>>")

    def estimate_total_assets(self):
        out = 0
        out += self.repository_for_all_users[self.username]["currency"]["联邦信用点"] // 2200
        out += self.repository_for_all_users[self.username]["currency"]["保险点"]
        out += sum(self.repository_for_all_users[self.username]["materials"].values()) // 50
        for al_index,num in self.repository_for_all_users[self.username]["als"].items():
            out += num * AL_META_DATA[al_index]["rank_num"]
        return out

    # ==================== 终焉结跟踪器 ======================

    def set_tracing_al(self,al_index:str):
        self.set_value_of("tracing_al", al_index)
        self.sync()

    def clear_tracing_al(self):
        self.set_value_of("tracing_al", "")
        self.sync()

    def get_the_gap(self) -> dict[str,int]:
        """
        计算当前玩家与追踪的终焉结之间的差距
        :return: 字典。键为物资与信用点，值为差距。若无差距或无跟踪，返回空字典
        """
        if not self.get_value_of("tracing_al"):
            return {}
        al_index = self.get_value_of("tracing_al")
        al_recipe = recipe_for_all_al[al_index]
        gap = {}
        for item,value in al_recipe.items():
            if value > self.get_value_of(item):
                gap[item] = value - self.get_value_of(item)
        return gap

    def generate_gap_list(self) -> list[str]:
        """
        生成追踪终焉结所需的物资字符串列表
        :return: 字符串列表，描述终焉结所需物资
        """
        if not self.get_value_of("tracing_al"):
            return ["[无跟踪]"]
        gap = self.get_the_gap()
        if not gap:
            return ["[可合成]"]
        out = []
        for item,value in gap.items():
            out.append(f"{Txt.adjust(item,10)}*{value}")
        return out

    # ==================== 终焉结相关功能 ====================
    
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
    
    # ==================== 词条相关功能 ====================
    
    def save_entry_rank(self,all_entry_rank:dict[str,int]):
        self.repository_for_all_users[self.username]["metadata"]["entry_rank"] = all_entry_rank
        self.sync()
    
    def get_entry_rank(self) -> dict[str,int]:
        return self.repository_for_all_users[self.username]["metadata"]["entry_rank"]
    
    # ==================== 战斗相关功能 ====================
    
    def drop_for_fight(self, times:int=1):
        """
        单局战斗后掉落物结算|1100信用点|物品掉落量随倍数变化
        :param times: 掉落物倍数
        :return: 无
        """
        money = random.randint(1000, 1200)
        self.modify("联邦信用点",money*times)
        isk_str = f"联邦信用点*{money*times}"

        # 根据倍数确定物品种类数量
        if times <= 4:
            item_count = min(times*2, 8)  # 1倍2种，2倍4种，3倍6种，4倍8种
        else:
            item_count = 8  # 4倍以上保持8种物品

        # 随机选择物品
        items = random.sample(list(self.template["materials"].keys()), item_count)
        item_dict = {}

        # 计算基础总掉落数量（2种物品，每种10-15个）
        base_total = 2 * 12.5  # 平均每种12.5个

        # 根据times倍数调整物品数量
        if times <= 4:
            # 1-4倍，每种物品数量不变
            for item in items:
                num = random.randint(10, 15)
                self.modify(item, num)
                item_dict[item] = num
        else:
            # 4倍以上，物品数量增加以满足总掉落量为times倍
            target_total = base_total * times
            current_total = 0

            # 先给每种物品分配基础数量
            for item in items:
                num = random.randint(10, 15)
                item_dict[item] = num
                current_total += num

            # 计算还需要增加的数量
            remaining = int(target_total - current_total)

            # 将剩余数量随机分配到物品上
            if remaining > 0:
                for _ in range(remaining):
                    item = random.choice(items)
                    item_dict[item] += 1

            # 应用修改
            for item, num in item_dict.items():
                self.modify(item, num)

        Txt.Tree(
            "收益统计",
            "赏金到账>>",
            isk_str,
            "战利品收集>>",
            item_dict
        ).print_self()
        self.sync()
    
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

    # ==================== 剧情进度保存 ====================

    def save_session_progress(self,session_str):
        """
        将某个会话的进度在硬盘中设置为已播放
        :param session_str: 会话编号
        :return: 无
        """
        self.repository_for_all_users[self.username]["metadata"]["plot_progress"][session_str] = True
        self.sync()

    def get_session_progress(self) -> dict[str,bool] :
        """
        获取所有会话的播放进度
        :return: 一个字典，键为会话编号
        """
        return self.repository_for_all_users[self.username]["metadata"]["plot_progress"]

storage_manager = StorageManager()