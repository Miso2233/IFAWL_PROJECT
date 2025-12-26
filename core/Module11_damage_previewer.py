import random

BROKEN_SHELTER_LIST = ["-x `-","~ - -"," -` -"," ~ x-"]

class DamagePreviewer:

    def __init__(self):
        self.my_ship_shelter = 0
        self.enemy_shelter = 0

    def initialize(self,my_ship_shelter,enemy_shelter):
        self.my_ship_shelter = my_ship_shelter
        self.enemy_shelter = enemy_shelter

    def update(self,my_ship_shelter,enemy_shelter):
        self.my_ship_shelter = my_ship_shelter
        self.enemy_shelter = enemy_shelter

    def print_my_ship_dmg(self, my_ship_shelter_now):
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

    def print_enemy_dmg(self, enemy_shelter_now):
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

damage_previewer = DamagePreviewer()