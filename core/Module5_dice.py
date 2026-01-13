import random
import math
from typing import Literal

from .Module0_enums_exceptions import Side

class Dice:

    def __init__(self):
        self.probability_current = 0.8
        self.di = 0.3
        self.additional_di = 0
        # 注意：根据用户说明，1代表我方，0代表敌方，与Side枚举一致
        self.current_who:Side = Side.ENEMY

    def set_probability(self,val:float):
        """
        设置当前的动态概率(摇到我方的概率)
        :param val: 动态概率的取值
        :return: 无
        """
        self.probability_current = val

    def set_di(self,val:float):
        """
        设置当前的概率波动值
        :param val: 概率波动取值
        :return: 无
        """
        self.di = val

    def set_additional_di(self,val:float):
        """
        设置当前的敌方行动概率追加值
        :param val: 概率波动取值
        :return: 无
        """
        self.additional_di = val

    def decide_who(self,force_advance:Literal[-1,0,1]=0) -> Side:
        """
        决定谁来进行下一回合，并进行马尔科夫链变化
        :param force_advance: 强制决定行动，1表示我方，-1表示敌方，0表示无强制
        :return: Side.PLAYER表示我方，Side.ENEMY表示敌方
        """
        match force_advance:
            case 1:
                self.current_who = Side.PLAYER
            case -1:
                self.current_who = Side.ENEMY
            case 0:
                if random.random()<self.probability_current:
                    self.current_who = Side.PLAYER
                else:
                    self.current_who = Side.ENEMY
            case _:
                assert False,"[IFAWL开发者断言错误]force_advance必须为某些值-若你看到此行句子，请立即联系开发者"

        if self.current_who == Side.PLAYER:
            self.probability_current -= self.di
            self.probability_current -= self.additional_di
        else:
            self.probability_current += self.di 

        return self.current_who

    @staticmethod
    def probability(pro:float) -> bool:
        """
        这一函数有pro概率为真，反之为假
        :param pro: 概率值，介于0和1之间
        :return:
        """
        if random.random() < pro:
            return True
        else:
            return False

    @staticmethod
    def sample_from_distribution(self,distribution:dict[int,float]) -> int:
        standard = random.random()
        total = sum(distribution.values())
        if not math.isclose(total, 1.0, rel_tol=1e-9):
            distribution = {k: v / total for k, v in distribution.items()}
        current = 0
        for val in distribution:
            current += distribution[val]
            if current >= standard:
                return val
        return 0
dice = Dice()