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
            print(f"语音未定义-[{who}]{theme}")

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

class MyShip:
    """
    ship.print_self()
    ship.attack(3,enemy)
    ship.heal(2)
    """

    def __init__(self):
        self.shelter = 0
        self.missile = 0
        self.al_list:list[Al_general|None] = [None,None,None]

    def print_self(self):
        for _ in range(self.shelter):
            print("-----")
        for _ in range(self.missile):
            print("[]",end="")
        print()

    def initialize(self):
        self.missile = 1
        self.shelter = 1
        for al in self.al_list:
            try:
                al.initialize()
            except AttributeError:
                pass

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
            case "q":
                self.al_list[0].react()
            case "w":
                self.al_list[1].react()
            case "e":
                self.al_list[2].react()
            case _:
                Txt.printplus("你跳过了这一天！")
my_ship = MyShip()

class EnemyShip:
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
enemy = EnemyShip()

class Al_manager:
    file_path = os.path.join('resources', 'al_meta_data.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        al_meta_data: dict[str:dict[str:str|int]] = json.load(f)

class Al_general:
    #Apocalypse-Linked 明日尘埃装备体系

    def __init__(self,index:int):
        # metadata 字段
        self.index:int                  = index
        self.short_name:str             = Al_manager.al_meta_data[str(index)]["short_name"]
        self.len_name:str               = Al_manager.al_meta_data[str(index)]["len_name"]
        self.type:Literal["q","w","e"]  = Al_manager.al_meta_data[str(index)]["type"]
        self.rank_num:int               = Al_manager.al_meta_data[str(index)]["rank_num"]
        self.skin_list:list[str]        = Al_manager.al_meta_data[str(index)].get("skin_list",[])
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

    def add_hp(self,hp:int):
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

    def initialize(self):
        self.state = 0

    def print_self(self):
        if self.state != 0:
            try:
                print(self.skin_list[self.state])
                print()
            except IndexError:
                pass
class Al3(Al_general):

    def react(self):
        if Dice.probability(0.3*enemy.shelter):
            my_ship.attack(1)
            self.report("命中")
        else:
            self.report("未命中")
al3 = Al3(3)

class Al4(Al_general):

    def react(self):
        if self.state<2:
            self.state+=2
            self.report("收到")
            time.sleep(0.4)
            if self.state == 2:
                self.report("准备好")

    def operate_afternoon(self):
        if self.state>=2:
            self.state+=1
            if self.state==4:
                self.state=0
            if Dice.probability(0.7):
                my_ship.attack(1)
                self.report("命中")
            else:
                self.report("未命中")
                my_ship.load(1)
                self.report("回流")
al4 = Al4(4)

class FieldPrinter:

    @classmethod
    def print_for_fight(cls, me:MyShip, opposite:EnemyShip):
        """
        打印双方护盾和导弹，以及我方Al
        :param me:
        :param opposite:
        :return: 无
        """
        opposite.print_self()
        print("\n\n\n")
        try:
            me.al_list[1].print_self()
        except AttributeError:
            pass
        me.print_self()
        try:
            me.al_list[2].print_self()
        except AttributeError:
            pass
        try:
            me.al_list[0].print_self()
        except AttributeError:
            pass
        print("\n")

    @classmethod
    def print_basic_info(cls,days):
        """
        打印战场基本信息
        :param days: 当前天数
        :return: 无
        """
        print("~~~~~~~~~~~~~~~~~~~~~~~~")
        Txt.printplus(f"指挥官，今天是战线展开的第{days}天。",0)
        if days < 5:
            Txt.printplus("当前舰船位置>>正在离港")
        elif days < 10:
            Txt.printplus("当前舰船位置>>我方领土边缘")
        elif days <= 20:
            Txt.printplus("当前舰船位置>>边境核心战场")
        elif days > 20:
            Txt.printplus("当前舰船位置>>敌方腹地危险区域")

class MainLoops:

    days = 0
    key_prompt = ""

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
            FieldPrinter.print_basic_info(cls.days)
            FieldPrinter.print_for_fight(my_ship, enemy)

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
    my_ship.al_list = [al4,None,al3]
    MainLoops.initialize_before_fight()
    MainLoops.fight_mainloop()