from abc import abstractmethod, abstractproperty
import random

from core.Module1_txt import print_plus
from core.Module2_json_loader import json_loader


class Mining:
    PREFIX = ["贫矿", "原生", "饱和"]
    EXTRA_PREFIX = ["流体", "致密", "固态", "折射", "光学", "熔融"]
    NAMES = ["凡晶石", "灼烧岩", "干焦岩", "长流石", "铱金"]

    def __init__(self):
        # 设置产出量
        self.richness = random.randint(0, 2)
        self.output_quantity = random.randint(20 + self.richness * 40, 100 + self.richness * 40)
        # 设置名称
        mining_type = random.choice(self.NAMES)
        self.output_item = mining_type + "原矿"
        self.name = self.PREFIX[self.richness] + random.choice(self.EXTRA_PREFIX) + mining_type
        # 操作字段
        self.is_exploited = False
        self.is_locked = False
        # 元数据字段
        self.mining_distance = random.randint(0, 50)

    def exploit_waiting(self) -> dict[str, int]:
        """
        对小行星进行开采|挂机方式
        :return: 一个字典，键为小行星内设掉落物，值为内设掉落量
        """
        if self.is_exploited:
            return {}
        mining_time = 3 if self.is_locked else 6
        print("正在开采", self.name, "预估收益", str(self.output_quantity * 1), "原矿")
        print("0        25        50        75       100")
        print("|         |         |         |         |")
        print_plus("`````````````````````````````````````````", mining_time)
        print("开采完成")
        print()
        self.is_exploited = True
        self.is_locked = False
        return {self.output_item: self.output_quantity}
