from __future__ import annotations

import random
import time
from typing import Literal
import json
import os

from myPackages import Module1_txt as Txt

class Voices:
    file_path = os.path.join('resources', 'voices.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        voices:dict[str:dict[str:list[str]]] = json.load(f)

    @classmethod
    def report(cls,who:str,theme:str,print_who=True):
        """
        展示voices.json中记录的语音内容
        :param who: 语音发出者
        :param theme: 语音主题
        :param print_who: 是否打印语音发出者
        :return:
        """
        try:
            if print_who:
                txt = f"[{who}]" + random.choice(cls.voices[who][theme])
            else:
                txt = random.choice(cls.voices[who][theme])
            Txt.printplus(txt)
        except KeyError:
            pass

class Dice:
    """
    Dice.set_probability(0.7)
    Dice.decide_who()
    """

    probability_current = 0.5
    di = 0.2

    @classmethod
    def set_probability(cls,val:float):
        """
        设置当前的动态概率(摇到我方的概率)
        :param val: 动态概率的取值
        :return: 无
        """
        cls.probability_current = val

    @classmethod
    def decide_who(cls) -> Literal[0,1]:
        """
        决定谁来进行下一回合，并进行马尔科夫链变化
        :return:
        """
        if random.random()<cls.probability_current:
            cls.probability_current -= cls.di
            return 1
        else:
            cls.probability_current += cls.di
            return 0

    @staticmethod
    def probability(pro) -> bool:  # 概率为真
        if random.random() < pro:
            return True
        else:
            return False

class Al_manager:
    file_path = os.path.join('resources', 'al_meta_data.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        al_meta_data: dict[str:any] = json.load(f)

class Al_general:
    #Apocalypse-Linked 明日尘埃装备体系

    def __init__(self,index:int):
        # metadata 字段
        self.index:int                  = index
        self.short_name:str             = Al_manager.al_meta_data[str(index)]["short_name"]
        self.len_name:str               = Al_manager.al_meta_data[str(index)]["len_name"]
        self.type:Literal["q","w","e"]  = Al_manager.al_meta_data[str(index)]["type"]
        self.rank_num:int               = Al_manager.al_meta_data[str(index)]["rank_num"]
        self.metadata:dict[str:str|int] = Al_manager.al_meta_data[str(index)]

        # operation 字段
        self.state = 0

    def report(self, theme:str):
        """
        Al所包装的说话函数，省去了说话者名字
        :param theme: 主题
        :return: 无
        """
        Voices.report(self.short_name,theme)

    def add_atk(self,atk:int):
        """
        为atk提供加成
        :param atk: 加成前atk
        :return: 加成后atk
        """
        return atk

    def add_atk(self,hp:int):
        """
        为hp提供加成
        :param hp: 加成前hp
        :return: 加成后hp
        """
        return hp

    def operate_morning(self):
        pass

    def operate_afternoon(self):
        pass
class Al3(Al_general):

    def react(self):
        if Dice.probability(0.3*enemy.shelter):
            my_ship.attack(1)
            self.report("命中")
        else:
            self.report("未命中")
al3 = Al3(3)


class Printer:

    @classmethod
    def print_for_fight(cls, me:My_ship, enemy:Enemy_ship):
        enemy.print_self()
        print("\n\n\n")
        me.print_self()
        print("\n")

class My_ship:
    """
    ship.print_self()
    ship.attack(3,enemy)
    ship.heal(2)
    """

    def __init__(self):
        self.shelter = 0
        self.missile = 0
        self.al_list = [None,None,al3]

    def print_self(self):
        for _ in range(self.shelter):
            print("-----")
        for _ in range(self.missile):
            print("[]",end="")

    def initialize(self):
        self.missile = 1
        self.shelter = 1

    def attack(self,atk:int):
        """
        根据原始伤害进行加减并对目标造成攻击
        :param atk: 原始伤害
        :return: 无
        """
        enemy.shelter -= atk

    def heal(self,hp:int):
        """
        根据原始回血量进行加减并进行治疗
        :param hp: 原始回血量
        :return: 无
        """
        self.shelter += hp

    def load(self,num:int):
        """
        根据原始上弹量进行加减并进行上弹
        :param num: 原始上弹量
        :return: 无
        """
        self.missile += num

    def react(self):
        """
        进行回合中响应
        :return: 无
        """
        operation = input(">>>")
        if self.missile < 1 and operation == "1":
            operation = "0"
        match operation:
            case "0"|" " :
                self.load(1)
                Voices.report("导弹","上弹")
            case "1":
                self.attack(1)
                self.load(-1)
                Voices.report("导弹","发射")
            case "2":
                self.heal(1)
                Voices.report("护盾","上盾")
            case "e":
                self.al_list[2].react()
            case _:
                Txt.printplus("你跳过了这一天！")
my_ship = My_ship()

class Enemy_ship:
    def __init__(self):
        self.shelter = 0
        self.missile = 0

    def print_self(self):
        for _ in range(self.missile):
            print("[]",end="")
        print()
        for _ in range(self.shelter):
            print("-----")

    def attack(self,atk:int):
        """
        根据原始伤害进行加减并对目标造成攻击
        :param atk: 原始伤害
        :return: 无
        """
        my_ship.shelter -= atk

    def heal(self,hp:int):
        """
        根据原始回血量进行加减并进行治疗
        :param hp: 原始回血量
        :return: 无
        """
        self.shelter += hp

    def load(self,num:int):
        """
        根据原始上弹量进行加减并进行上弹
        :param num: 原始上弹量
        :return: 无
        """
        self.missile += num

    def initialize(self):
        self.missile = 2
        self.shelter = 2

    def react(self):
        operation = random.choice(["0","1","2"])
        if self.missile < 1 and operation == "1":
            operation = "0"
        match operation:
            case "0":
                self.load(1)
            case "1":
                self.attack(1)
                self.load(-1)
            case "2":
                self.heal(1)
            case _:
                Txt.printplus("敌人跳过了这一天！")

enemy = Enemy_ship()

class Main_loops:

    days = 0

    @staticmethod
    def is_over() -> Literal[-1,0,1]:
        """
        判定是否有一方死亡
        :return: -1代表敌方胜利 0表示游戏继续 1表示我方胜利
        """
        if my_ship.shelter<0:
            return -1
        if enemy.shelter<0:
            return 1
        return 0

    @classmethod
    def initialize_before_fight(cls):
        my_ship.initialize()
        enemy.initialize()
        cls.days = 1

    @classmethod
    def fight_mainloop(cls):
        while 1:
            # dawn
            time.sleep(0.4)
            Txt.printplus(f"指挥官，今天是战线展开的第{cls.days}天。")
            Printer.print_for_fight(my_ship, enemy)

            # morning
            for al in my_ship.al_list:
                if al:
                    al.operate_morning()

            # noon
            who = Dice.decide_who()
            if who==1:
                Txt.printplus("今天由我方行动")
                my_ship.react()
            else:
                Txt.printplus("今天由敌方行动")
                enemy.react()

            # afternoon
            for al in my_ship.al_list:
                if al:
                    al.operate_afternoon()

            # dusk
            if (result := cls.is_over()) != 0:
                if result == 1:
                    Txt.printplus("我方胜利")
                else:
                    Txt.printplus("敌方胜利")
                return
            cls.days += 1

if __name__ == "__main__":
    Main_loops.initialize_before_fight()
    Main_loops.fight_mainloop()