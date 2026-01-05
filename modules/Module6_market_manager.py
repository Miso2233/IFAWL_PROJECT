import random

from core.Module10_sound_manager import sounds_manager
from core.Module1_txt import print_plus,Tree,adjust,n_column_print
from core.Module2_json_loader import json_loader

ALL_MATERIALS:list[str] = list(
    json_loader.load("storage_template")["materials"].keys()
)

AL_META_DATA = json_loader.load("al_meta_data")
"""所有AL的元数据"""

AL_RANK_LIST:dict[str,int] = {}
"""
从AL的字符串序号获取其级数
"""
for key in AL_META_DATA:
    AL_RANK_LIST[key] = AL_META_DATA[key]["rank_num"]

AL_NAME_LIST:dict[str,int] = {}
"""
从AL的字符串序号获取其短名称
"""
for key in AL_META_DATA:
    AL_NAME_LIST[key] = AL_META_DATA[key]["short_name"] + f"#{key}"

TOTAL_CONTRACT_NUM = 24

class Tools:

    @staticmethod
    def create_material_list(total:int) -> dict[str,int]:
        """
        创建一个八种材料中选择的materials字典，材料总量大致与total相当
        :param total: 需求的材料总量
        :return: 一个材料字典，键为材料名，值为材料的数目
        """
        output_list = {}
        material_num = random.randint(2, 4)
        num_expect = total // material_num

        material_list = random.sample(ALL_MATERIALS, material_num)

        for material in material_list:
            output_list[material] = random.randint(num_expect - 3, num_expect + 3)
        return output_list

    @staticmethod
    def is_affordable(cost:dict[str,int],budget:dict[str,int]) -> bool:
        """
        判断cost中的每一项是否小于budget中的对应项。若cost出现budget没有的项目，直接抛出KeyError
        :param cost: 账单
        :param budget: 预算
        :return: True表示cost可以被budget支付，False反之
        """
        for item in cost:
            if cost[item] > budget[item]:
                return False
        return True

    @staticmethod
    def clear_0_in(dic: dict[any,int]) -> None:
        """
        在 原 地 清除字典中值为0的项目
        :param dic:
        :return: 无
        """
        for key in list(dic.keys()):
            if dic[key] == 0:
                dic.pop(key)
tools = Tools()

class Contract:

    def __init__(self,index,storage_manager):
        self.index = index
        self.title = ""
        self.rank = random.randint(1,8)
        self.is_traded = False
        self.get_list = {}
        self.give_list = {}
        self.give_tree:Tree = Tree("")
        self.get_tree:Tree = Tree("")
        self.storage_manager = storage_manager

    def is_affordable(self):
        """
        判断这个合同是否和支付
        :return: True表示该合同可支付，False反之
        """
        return tools.is_affordable(self.give_list,self.storage_manager.show_assets())

    def refresh_affordable_tag(self):
        """
        刷新该合同的可支付标签
        :return: 无
        """
        aff_tag = " [●]" if self.is_affordable() else ""
        self.give_tree.title = f"你将支付>>>{aff_tag}"

    def transaction(self):
        """
        尝试交易这个合同，需要满足：合同可支付&&合同未被支付
        :return: 无
        """
        if not self.is_affordable():
            print("物品不足-交易失败")
            return
        if self.is_traded:
            print("合同已被交易")
            return
        else:
            self.storage_manager.transaction(self.give_list, self.get_list)
            self.is_traded = True
            sounds_manager.play_sfx("contract_dealt")
            print_plus("交易成功")

    def print_self(self):
        print("┌──────────┐")
        print(adjust(f"│{self.title}",22)+"│")
        print(adjust(f"│", 22) + "│")
        for line in self.give_tree.generate_line_list():
            print(adjust(f"│{line}",22)+"│")
        for line in self.get_tree.generate_line_list():
            print(adjust(f"│{line}",22)+"│")
        print("└──────────┘")

    def generate_line_list(self) -> list[str]:
        """
        生成Contract对象的行切片
        :return: 一个字符串列表，包含Contract的每一行
        """
        line_list = ["┌──────────┐", adjust(f"│{self.title}", 22) + "│",adjust(f"│", 22) + "│"]
        if self.is_traded:
            for _ in self.give_tree.generate_line_list():
                line_list.append(adjust(f"│", 22) + "│")
            for _ in range(len(self.get_tree.generate_line_list())-1):
                line_list.append(adjust(f"│", 22) + "│")
            line_list.append(adjust(f"│[已交易]", 22) + "│")
        else:
            for line in self.give_tree.generate_line_list():
                line_list.append(adjust(f"│{line}", 22) + "│")
            for line in self.get_tree.generate_line_list():
                line_list.append(adjust(f"│{line}", 22) + "│")
        line_list.append("└──────────┘")
        return line_list

class MaterialContract(Contract):
    """
    易物合同
    """
    def __init__(self,index,storage_manager):
        super().__init__(index,storage_manager)
        self.title = f"[{self.index}] 易物合同 [{self.rank}]级"

        # 生成交接物品列表
        self.give_list = tools.create_material_list(25 * self.rank)
        self.get_list = tools.create_material_list(30 * self.rank)

        # 去除重复
        common_items = set(self.give_list.keys()) & set(self.get_list.keys())
        for item in common_items:
            give_qty = self.give_list[item]
            get_qty = self.get_list[item]
            min_qty = min(give_qty,get_qty)
            self.get_list[item] -= min_qty
            self.give_list[item] -= min_qty
        tools.clear_0_in(self.get_list)
        tools.clear_0_in(self.give_list)

        # 打印树构建
        self.get_tree=Tree("你将得到>>>",self.get_list)
        self.give_tree = Tree("你将支付>>>", self.give_list)


class GoodsContract(Contract):
    """
    货品合同
    """

    def __init__(self, index,storage_manager):
        super().__init__(index,storage_manager)
        self.title = f"[{self.index}] 货品合同 [{self.rank}]级"

        # 生成支付物品列表（25倍rank）
        self.give_list = tools.create_material_list(25 * self.rank)

        # 生成获取的信用点（1100倍rank，有±100浮动）
        self.get_list = {
            "联邦信用点": random.randint(
                1100 * self.rank - 100,
                1100 * self.rank + 100
            )
        }

        # 50%概率交换give和get列表
        if random.random() < 0.5:
            self.give_list, self.get_list = self.get_list, self.give_list

        # 清理数量为0的物品
        tools.clear_0_in(self.get_list)
        tools.clear_0_in(self.give_list)

        # 打印树构建
        self.get_tree = Tree("你将得到>>>", self.get_list)
        self.give_tree = Tree("你将支付>>>", self.give_list)

class FinanceContract(Contract):
    """
    金融合同
    """

    def __init__(self, index,storage_manager):
        super().__init__(index,storage_manager)
        self.title = f"[{self.index}] 金融合同 [{self.rank}]级"

        # 生成支付的信用点
        self.give_list = {
            "联邦信用点": random.randint(
                1100 * self.rank - 100,
                1100 * self.rank + 100
            )
        }

        # 生成获取的信用点（1100倍rank，有±1000浮动）
        self.get_list = {
            "联邦信用点": random.randint(
                1100 * self.rank - 1000,
                1100 * self.rank + 1000
            )
        }

        # 50%概率交换give和get列表
        if random.random() < 0.5:
            self.give_list, self.get_list = self.get_list, self.give_list

        # 打印树构建
        self.get_tree = Tree("你将得到>>>", "[风险投资回报]ISK")
        self.give_tree = Tree("你将支付>>>", self.give_list)

class SsdContract(Contract):
    """
    保险合同
    """

    def __init__(self, index, storage_manager):
        super().__init__(index, storage_manager)
        self.title = f"[{self.index}] 保险合同 [{self.rank}]级"

        self.get_list = {"保险点": self.rank}
        self.give_list = {"联邦信用点": self.rank * 1100 + random.randint(-50, 50)}

        # 打印树构建
        self.get_tree = Tree("你将得到>>>", self.get_list)
        self.give_tree = Tree("你将支付>>>", self.give_list)

class IndustryContract(Contract):
    """
    工业合同
    """

    def __init__(self, index,storage_manager):
        super().__init__(index,storage_manager)
        al = random.choice(list(AL_META_DATA.keys()))
        while AL_META_DATA[al]["rank_num"] == 0:
            al = random.choice(list(AL_META_DATA.keys()))
        self.rank = AL_META_DATA[al]["rank_num"]
        self.title = f"[{self.index}] 工业合同 [{self.rank}]级"

        self.get_list = {al:1}
        self.give_list = tools.create_material_list(20*self.rank)
        self.give_list["联邦信用点"] = random.randint(1000*self.rank-300,1000*self.rank+100)

        # 打印树构建
        self.get_tree = Tree("你将得到>>>", {AL_NAME_LIST[al]:1})
        self.give_tree = Tree("你将支付>>>", self.give_list)

class RepurchaseContract(Contract):
    """
    回购合同
    """
    def __init__(self, index,storage_manager):
        super().__init__(index,storage_manager)
        al = random.choice(list(AL_META_DATA.keys()))
        while AL_META_DATA[al]["rank_num"] == 0:
            al = random.choice(list(AL_META_DATA.keys()))
        self.rank = AL_META_DATA[al]["rank_num"]
        self.title = f"[{self.index}] 回购合同 [{self.rank}]级"

        self.give_list = {al:1}
        self.get_list = tools.create_material_list(20*self.rank)
        self.get_list["联邦信用点"] = random.randint(1000*self.rank-300,1000*self.rank+100)

        # 打印树构建
        self.get_tree = Tree("你将得到>>>", self.get_list)
        self.give_tree = Tree("你将支付>>>", {AL_NAME_LIST[al]:1})

class Contract_manager:

    def __init__(self,storage_manager,all_al_str_list:list[str]):
        self.storage_manager = storage_manager
        self.contract_type_list = [
            MaterialContract,
            GoodsContract,
            FinanceContract,
            IndustryContract,
            SsdContract,
            RepurchaseContract
        ]
        self.all_contracts_list = []
        for key in AL_META_DATA.copy():
            if key not in all_al_str_list:
                AL_META_DATA.pop(key)

    def generate_all_contracts(self):
        self.all_contracts_list.clear()
        for i in range(TOTAL_CONTRACT_NUM):
            self.all_contracts_list.append(
                random.choice(
                    self.contract_type_list
                )(i,self.storage_manager)
            )

    def print_all_contracts(self):
        for contract in self.all_contracts_list:
            contract.refresh_affordable_tag()
        line_list = [[] for _ in range(6)]
        for contract in self.all_contracts_list:
            line_list[contract.index%6] += contract.generate_line_list()
        n_column_print(line_list,24)




if __name__ == "__main__":
    ...