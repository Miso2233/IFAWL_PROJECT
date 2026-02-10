from abc import abstractmethod, abstractproperty
import random

from core.Module1_txt import print_plus, Tree, input_plus
from core.Module2_json_loader import json_loader
from modules.Module3_storage_manager import storage_manager

MINING_AMOUNT = 12


class Mining:
    PREFIX = ["贫矿", "原生", "饱和"]
    EXTRA_PREFIX = ["流体", "致密", "固态", "折射", "光学", "熔融"]
    NAMES = ["凡晶石", "灼烧岩", "干焦岩", "长流石", "铱金"]

    def __init__(self, index: str):
        # 设置产出量
        self.richness = random.randint(0, 2)
        self.output_quantity = random.randint(20 + self.richness * 40, 100 + self.richness * 40)
        # 设置名称
        self.name = random.choice(self.NAMES)
        self.output_item = self.name + "原矿"
        self.title = self.PREFIX[self.richness] + random.choice(self.EXTRA_PREFIX) + self.name
        # 操作字段
        self.is_exploited = False
        self.is_locked = False
        # 元数据字段
        self.mining_distance = random.randint(0, 50)
        self.index = index

    def exploit_waiting(self) -> dict[str, int]:
        """
        对小行星进行开采|挂机方式
        :return: 一个字典，键为小行星内设掉落物，值为内设掉落量
        """
        if self.is_exploited:
            return {}
        mining_time = 3 if self.is_locked else 6
        print("正在开采", self.title, "预估收益", str(self.output_quantity * 1), "原矿")
        print("0        25        50        75       100")
        print("|         |         |         |         |")
        print_plus("`````````````````````````````````````````", mining_time)
        print("开采完成")
        print()
        self.is_exploited = True
        self.is_locked = False
        return {self.output_item: self.output_quantity}

    def generate_line_list(self, is_watched=False) -> list[str]:
        """
        生成小行星的文本描述
        :param is_watched: 是否正在被注视
        :return: 行切片，与其他同名方法一致
        """
        basic_info = f"[{self.index}]{self.title}({self.mining_distance}km)"
        if not self.is_exploited:  # 对于未被开采的小行星
            if is_watched:  # 临时锁定
                return Tree(
                    f"-[临时锁定]{basic_info}-",
                    "[q][开采]双向渗透法",
                    "[w][开采]简谐共振法",
                    "[e][锁定]部署/取消主锁定"
                ).generate_line_list()

            elif self.is_locked:  # 主锁定
                return [f"+[主雷达已锁定]{basic_info}+",""]
            else:  # 其它
                return [f"{basic_info}",""]
        # 对于已被开采的小行星
        if is_watched:  # 临时锁定
            out = [
                f"-[临时锁定]{basic_info}-",
                "|",
                "|-[已被开采]",
                ""
            ]
            return out
        else:  # 其它
            return [f"[已被开采]{basic_info}",""]

    def print_self(self, is_watched=False) -> None:
        line_list = self.generate_line_list(is_watched)
        for line in line_list:
            print(line)


class MiningManager:

    def __init__(self):
        self.all_mining = {
            index: Mining(index) for index in [
                str(i) for i in range(MINING_AMOUNT)
            ]
        }
        self.current_watching = "-1"

    def re_generate_all_mining(self):
        self.all_mining = {
            index: Mining(index) for index in [
                str(i) for i in range(MINING_AMOUNT)
            ]
        }

    def print_all_mining(self):
        for index, mining in self.all_mining.items():
            mining.print_self(index == self.current_watching)

    def mainloop(self):
        while True:
            self.print_all_mining()
            command = input_plus("请输入操作")
            match command:
                case "q":
                    if self.current_watching == "-1":
                        for index, mining in self.all_mining.items():
                            if mining.is_locked:
                                result = mining.exploit_waiting()
                                storage_manager.transaction({}, result)
                    else:
                        try:
                            result = self.all_mining[self.current_watching].exploit_waiting()
                        except KeyError:
                            print_plus("未选择小行星")
                        else:
                            storage_manager.transaction({}, result)
                        finally:
                            self.current_watching = "-1"
                case "w":
                    ...
                case "e":
                    try:
                        self.all_mining[self.current_watching].is_locked = not self.all_mining[
                            self.current_watching].is_locked
                    except KeyError:
                        print_plus("未选择小行星")
                    finally:
                        self.current_watching = "-1"
                case _:
                    if command == self.current_watching:
                        self.current_watching = "-1"
                        continue
                    if command in self.all_mining.keys():
                        self.current_watching = command


mining_manager = MiningManager()
