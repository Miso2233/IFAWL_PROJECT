import random
from typing import Literal

class Dice:

    def __init__(self):
        self.probability_current = 0.8
        self.di = 0.3
        self.current_who:Literal[0,1] = 0

    def set_probability(self,val:float):
        """
        设置当前的动态概率(摇到我方的概率)
        :param val: 动态概率的取值
        :return: 无
        """
        self.probability_current = val

    def decide_who(self,force_advance:Literal[-1,0,1]=0) -> Literal[0,1]:
        """
        决定谁来进行下一回合，并进行马尔科夫链变化
        :param force_advance: 强制决定行动，1表示我方，-1表示敌方，0表示无强制
        :return: 1表示我方，0表示敌方
        """
        match force_advance:
            case 1:
                self.current_who = 1
            case -1:
                self.current_who = 0
            case 0:
                if random.random()<self.probability_current:
                    self.current_who = 1
                else:
                    self.current_who = 0
            case _:
                assert False,"[IFAWL开发者断言错误]force_advance必须为某些值-若你看到此行句子，请立即联系开发者"

        if self.current_who == 1:
            self.probability_current -= self.di
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
dice = Dice()