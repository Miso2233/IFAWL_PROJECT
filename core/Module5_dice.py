import random
from typing import Literal

class Dice:

    def __init__(self):
        self.probability_current = 0.2
        self.di = 0.3

    def set_probability(self,val:float):
        """
        设置当前的动态概率(摇到我方的概率)
        :param val: 动态概率的取值
        :return: 无
        """
        self.probability_current = val

    def decide_who(self) -> Literal[0,1]:
        """
        决定谁来进行下一回合，并进行马尔科夫链变化
        :return: 1表示我方，0表示敌方
        """
        if random.random()<self.probability_current:
            self.probability_current -= self.di
            return 1
        else:
            self.probability_current += self.di
            return 0

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
dice = Dice()