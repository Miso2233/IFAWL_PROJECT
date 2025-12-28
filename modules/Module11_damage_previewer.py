import random

from core.Module1_txt import Tree

BROKEN_SHELTER_LIST = ["-x `-","~ - -"," -` -"," ~ x-"]

class DamagePreviewer:

    def __init__(self):
        self.my_ship_shelter = 0
        self.enemy_shelter = 0
        self.total_dmg_from_me = 0
        self.total_dmg_from_enemy = 0

    def initialize(self,my_ship_shelter,enemy_shelter):
        self.my_ship_shelter = my_ship_shelter
        self.enemy_shelter = enemy_shelter
        self.total_dmg_from_me = 0
        self.total_dmg_from_enemy = 0

    def update(self,my_ship_shelter,enemy_shelter):
        self.my_ship_shelter = my_ship_shelter
        self.enemy_shelter = enemy_shelter

    def print_my_ship_dmg(self, my_ship_shelter_now, mute=False):
        if (dmg := self.my_ship_shelter - my_ship_shelter_now) > 0:
            self.total_dmg_from_enemy += dmg
        if mute:
            return
        if (dmg := self.my_ship_shelter - my_ship_shelter_now) > 0:
            for i in range(dmg,0,-1):
                print(
                    random.choice(
                        BROKEN_SHELTER_LIST
                    ),
                    end=""
                )
                if i == 1:
                    print(f" 有效伤害>{dmg}.0")
                else:
                    print()

    def print_enemy_dmg(self, enemy_shelter_now, mute=False):
        if (dmg := self.enemy_shelter - enemy_shelter_now) > 0:
            self.total_dmg_from_me += dmg
        if mute:
            return
        if (dmg := self.enemy_shelter - enemy_shelter_now) > 0:
            for i in range(dmg):
                print(
                    random.choice(
                        BROKEN_SHELTER_LIST
                    ),
                    end=""
                )
                if i == 0:
                    print(f" 有效伤害>{dmg}.0")
                else:
                    print()

    def show_total_dmg(self, my_ship_shelter_now, enemy_shelter_now):
        if (dmg := self.my_ship_shelter - my_ship_shelter_now) > 0:
            self.total_dmg_from_enemy += dmg
        if (dmg := self.enemy_shelter - enemy_shelter_now) > 0:
            self.total_dmg_from_me += dmg
        Tree(
            "战斗总伤害估计",
            f"对敌方有效伤害>>{self.total_dmg_from_me}",
            f"我方护盾总承伤>>{self.total_dmg_from_enemy}"
        ).print_self()

damage_previewer = DamagePreviewer()