from typing import Literal
import random

from core.Module1_txt import print_plus,Tree
from core.Module2_json_loader import json_loader

ALL_CARD_METADATA = json_loader.load("cards_meta_data")

class CardManager:

    def __init__(self,my_ship,enemy,entry_manager):
        self.my_ship = my_ship
        self.enemy = enemy
        self.entry_manager = entry_manager
        self.all_cards:dict[str,CardGeneral] = {
            index:CardGeneral(index,self.my_ship,self.enemy,self.entry_manager)
            for index in ALL_CARD_METADATA
        }

class CardGeneral:

    def __init__(self,index,my_ship,enemy,entry_manager):
        # 元数据字段
        self.index = str(index)
        self.metadata = ALL_CARD_METADATA[index]
        self.title = self.metadata["title"]
        self.story_txt = self.metadata["story_txt"]
        self.description_txt = self.metadata["description_txt"]
        # 依赖字段
        self.my_ship = my_ship
        self.enemy = enemy
        self.entry_manager = entry_manager

    def react(self):
        ...

class Card1(CardGeneral): # 紧急回站

    def react(self):
        shelter = random.randint(1,5)
        self.my_ship.heal(shelter)
        self.my_ship.load(5-shelter)
        print_plus(f"护盾回充>{shelter}")
        print_plus(f"导弹装载>{5-shelter}")

class Card2(CardGeneral): # 抑制剂

    def react(self):
        self.entry_manager.pull_down()