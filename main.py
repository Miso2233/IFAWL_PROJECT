from __future__ import annotations

import random
from typing import Literal
import Module1_txt
import json
import os

class Voices:
    file_path = os.path.join('resources', 'voices.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        voices:dict[str:dict[str:list[str]]] = json.load(f)

    @classmethod
    def report(cls,who:str,theme:str):
        try:
            Module1_txt.printplus(random.choice(cls.voices[who][theme]))
        except KeyError:
            pass

class Dice:
    """
    Dice.set_probability(0.7)
    Dice.decide_who()
    """

    probability = 0.5
    di = 0.2

    @classmethod
    def set_probability(cls,val:float):
        """
        设置当前的动态概率(摇到我方的概率)
        :param val: 动态概率的取值
        :return: 无
        """
        cls.probability = val

    @classmethod
    def decide_who(cls) -> Literal[0,1]:
        """
        决定谁来进行下一回合，并进行马尔科夫链变化
        :return:
        """
        if random.random()<cls.probability:
            cls.probability -= cls.di
            return 1
        else:
            cls.probability += cls.di
            return 0

class Printer:
    def __init__(self):
        ...
    @classmethod
    def print_single_day(cls,me:My_ship,enemy:Enemy_ship):
        enemy.print_self()
        me.print_self()

class Initializer:
    """
    me,enemy = Initializer.generate_me_and_enemy()
    """

    @classmethod
    def generate_me_and_enemy(cls) -> tuple[My_ship, Enemy_ship]:
        """
        生成我方和敌方两个船只对象，并进行护盾和导弹的初始化
        :return: 双方船只对象。使用两个变量来接住
        """
        me = My_ship()
        me.shelter = 1
        me.missile = 1
        enemy = Enemy_ship()
        enemy.shelter = 3
        enemy.missile = 1
        return me,enemy

class My_ship:
    """
    ship.print_self()
    ship.attack(3,enemy)
    ship.heal(2)
    """

    def __init__(self):
        self.shelter = 0
        self.missile = 0

    def print_self(self):
        for _ in range(self.shelter):
            print("-----")
        for _ in range(self.missile):
            print("[] ",end="")

    def attack(self,atk:int,target:Enemy_ship):
        """
        根据原始伤害进行加减并对目标造成攻击
        :param atk: 原始伤害
        :param target: 承受攻击的敌方船只
        :return: 无
        """
        target.shelter -= atk

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

    def react(self,enemy:Enemy_ship):
        """
        进行回合中响应
        :param enemy: 当前敌方
        :return: 无
        """
        operation = input(">>>")
        if self.missile < 1 and operation == "1":
            operation = "0"
        match operation:
            case "0":
                self.load(1)
            case "1":
                self.attack(1,enemy)
                self.load(-1)
            case "2":
                self.heal(1)
            case _:
                Module1_txt.printplus("你跳过了这一天！")

class Enemy_ship:
    def __init__(self):
        self.shelter = 0
        self.missile = 0

    def print_self(self):
        for _ in range(self.missile):
            print("[] ",end="")
        print()
        for _ in range(self.shelter):
            print("-----")

    def attack(self,atk:int,target:My_ship):
        """
        根据原始伤害进行加减并对目标造成攻击
        :param atk: 原始伤害
        :param target: 承受攻击的我方船只
        :return: 无
        """
        target.shelter -= atk


if __name__ == "__main__":
    Voices.report("导弹","上弹")