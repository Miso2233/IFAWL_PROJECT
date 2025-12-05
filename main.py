from __future__ import annotations

import random
import time
import json
import os
import shelve
from typing import Literal
from copy import deepcopy

from myPackages import Module1_txt as Txt

class JsonLoader:

    def __init__(self):
        self.dir = "resources"

    def load(self,title):
        file_path = os.path.join("resources", f'{title}.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
json_loader = JsonLoader()

class Voices:

    def __init__(self):
        self.voices:dict[str,dict[str,list[str]]] = json_loader.load("voices")

    def report(self, who:str, theme:str, print_who=True):
        """
        展示voices.json中记录的语音内容
        :param who: 语音发出者
        :param theme: 语音主题
        :param print_who: 是否打印语音发出者
        :return:
        """
        try:
            if print_who:
                txt = f"[{who}]" + random.choice(self.voices[who][theme])
            else:
                txt = random.choice(self.voices[who][theme])
            Txt.print_plus(txt)
        except KeyError:
            print(f"语音未定义-[{who}]{theme}")
voices = Voices()

class Dice:

    def __init__(self):
        self.probability_current = 0.5
        self.di = 0.2

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
        :return:
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
        for al in self.al_list:
            try:
                atk = al.add_atk(atk)
            except AttributeError:
                pass
        enemy.shelter -= atk

    def heal(self,hp:int):
        """
        根据原始回血量进行加减并进行治疗
        :param hp: 原始回血量
        :return: 无
        """
        for al in self.al_list:
            try:
                hp = al.add_hp(hp)
            except AttributeError:
                pass
        self.shelter += hp

    def load(self,num:int):
        """
        根据原始上弹量进行加减并进行上弹
        :param num: 原始上弹量
        :return: 无
        """
        for al in self.al_list:
            try:
                num = al.add_num(num)
            except AttributeError:
                pass
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
                voices.report("导弹","上弹")
            case "1":
                self.attack(1)
                self.load(-1)
                voices.report("导弹","发射")
            case "2":
                self.heal(1)
                voices.report("护盾","上盾")
            case "q":
                self.al_list[0].react()
            case "w":
                self.al_list[1].react()
            case "e":
                self.al_list[2].react()
            case _:
                Txt.print_plus("你跳过了这一天！")
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
        if atk <= 0:
            voices.report("护盾","未受伤")
        elif atk <=1:
            voices.report("护盾","受击")
        else:
            voices.report("护盾","受重击")

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
                Txt.print_plus("敌人跳过了这一天！")
enemy = EnemyShip()

class Al_manager:

    def __init__(self):
        self.al_meta_data: dict[str,dict[str,str|int]] = json_loader.load("al_meta_data")
        self.all_al_list:dict[str,Al_general] = {}

    def choose_al(self,type_choosing:Literal["q","w","e","all"]):
        if type_choosing == "all":
            self.choose_al("q")
            self.choose_al("w")
            self.choose_al("e")
            return
        for al in self.all_al_list.values():
            if al.type == type_choosing:
                al.print_description()
        cn_type = {"q":"主武器","w":"生存位","e":"战术装备"}[type_choosing]
        al_position = {"q":0,"w":1,"e":2}[type_choosing]
        while 1:
            inp = Txt.input_plus(f"\n指挥官，请输入数字选择本场战斗的{cn_type}（对局中输入{type_choosing}来使用）[-1=不使用{cn_type}]>>>")
            if inp not in self.al_meta_data or self.al_meta_data[inp]["type"] != type_choosing:
                if inp == "":
                    break
                elif inp == "-1":
                    my_ship.al_list[al_position] = None
                    break
                print(f"请在{cn_type}库中进行选择")
            else:
                print(f"{self.al_meta_data[inp]['short_name']}#{self.al_meta_data[inp]['index']}", "已确认装备")
                my_ship.al_list[al_position] = self.all_al_list[inp]
                print("")
                time.sleep(0.4)
                break
al_manager = Al_manager()

class Al_general:
    #Apocalypse-Linked 明日尘埃装备体系

    def __init__(self,index:int):
        # metadata 字段
        self.index:int                  = index
        self.short_name:str             = al_manager.al_meta_data[str(index)]["short_name"]
        self.len_name:str               = al_manager.al_meta_data[str(index)]["len_name"]
        self.type:str                   = al_manager.al_meta_data[str(index)]["type"]
        self.rank_num:int               = al_manager.al_meta_data[str(index)]["rank_num"]
        self.skin_list:list[str]        = al_manager.al_meta_data[str(index)].get("skin_list",[])
        self.platform:str               = al_manager.al_meta_data[str(index)]["platform"]
        self.metadata:dict[str,str|int] = al_manager.al_meta_data[str(index)]
        al_manager.all_al_list[str(self.index)] = self

        # operation 字段
        self.state = 0

    def report(self, theme:str):
        """
        Al所包装的说话函数，省去了说话者名字
        :param theme: 主题
        :return: 无
        """
        voices.report(self.short_name,theme)

    def print_description(self):
        """
        打印Al的描述，用于装备选择界面
        :return: 无
        """
        tag0: str = self.metadata["origin"]
        tag1: str = self.platform

        print(
            f"[{self.index}] {tag0}{self.len_name + ' ' * (40 - Txt.get_shell_len(self.len_name + tag0 + str(self.index)))}[{tag1}平台] [{self.metadata['rank']}]")
        print(f">>>>\"{self.short_name}\"")
        print(self.metadata["description_txt"])
        # [30] 岩河军工“湾区铃兰”饱和式蜂巢突击粒子炮      [粒子炮平台] [VIII] 1在仓库 >>[可以离站使用]<<
        print()

    def add_atk(self,atk:int):
        """
        为atk提供加成
        :param atk: 加成前atk
        :return: 加成后atk
        """
        return atk

    def add_hp(self,hp:int):
        """
        为heal提供加成
        :param hp: 加成前hp
        :return: 加成后hp
        """
        return hp

    def add_load(self,num:int):
        """
        为load提供加成
        :param num: 加成前num
        :return: 加成后num
        """
        return num

    def operate_in_morning(self):
        pass

    def operate_in_afternoon(self):
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

    def suggest(self) -> str|None:
        return None

    def operate_in_our_turn(self):
        pass
class Al3(Al_general):

    def react(self):
        if dice.probability(0.3*enemy.shelter):
            my_ship.attack(1)
            self.report("命中")
        else:
            self.report("未命中")

    def suggest(self) -> str|None:
        prob=enemy.shelter*30
        if prob != 0:
            return f"[e]发射巡飞弹|命中率{prob}%"
        else:
            return "[无命中率]不建议发射巡飞弹"
al3 = Al3(3)

class Al4(Al_general):

    def react(self):
        if self.state<2:
            self.state+=2
            self.report("收到")
            time.sleep(0.4)
            if self.state == 2:
                self.report("准备好")

    def operate_in_afternoon(self):
        if self.state>=2:
            self.state+=1
            if self.state==4:
                self.state=0
            if dice.probability(0.7):
                my_ship.attack(1)
                self.report("命中")
            else:
                self.report("未命中")
                my_ship.load(1)
                self.report("回流")

    def suggest(self) -> str|None:
        return \
        ["[q]部署发射台",
         "[q]挂载铜芯导弹 2/2",
         "[自动攻击中]回流系统正在生效",
         "[自动攻击中]回流系统正在生效"][self.state]
al4 = Al4(4)

class Al5(Al_general):#水银

    def react(self):
        if self.state == 0:
            self.state+=1
            self.report("收到")
        elif self.state == 1:
            self.state+=1
            self.report("准备好")
        else:
            self.state=0
            if random.randint(0,9)>-1:
                my_ship.attack(2)
                self.report("命中")
            else:
                self.report("未命中")

    def add_load(self,num) -> int:
        if self.state == 2 and dice.probability(0.5):
            self.report("协助上弹")
            return num + 1
        else:
            return num

    def suggest(self):
        return \
        ["[q]建立汞弹推进器 1/2",
         "[q]加注液态汞 2/2",
         "[q]发射汞弹|[0/space]上弹效率加成中"][self.state]
al5 = Al5(5)

class Al6(Al_general):
    def react(self):
        if self.state == 0:
            if my_ship.shelter > 0:
                self.state += 1
                self.report("收到")
            else:
                self.state = 2
                self.report("生之帝国")
        elif self.state == 1:
            self.state += 1
            self.report("准备好")

    def operate_in_afternoon(self):
        if self.state == 2 and my_ship.shelter <= 0:
            self.state = 0
            my_ship.heal(2)
            self.report("急救")

    def suggest(self):
        return ["[w]建立安全屋1/2", "[w]派遣维修小队2/2", "[保护中]急救已就绪"][self.state]
al6 = Al6(6)

class Al7(Al_general):
    def react(self):
        if self.state == 0:
            if dice.probability(0.7):
                if enemy.missile > 0:
                    self.state = 1
                    enemy.missile -= 1
                    self.report("骇入成功")
            else:
                self.report("骇入失败")

    def operate_in_morning(self):
        if self.state == 1:
            if dice.probability(0.6):
                my_ship.attack(1)
                self.state-=1
                time.sleep(0.4)
                self.report("引爆成功")
            else:
                self.state-=1
                time.sleep(0.4)
                self.report("引爆失败")
        self.state = 0

    def suggest(self):
        if enemy.missile == 0:
            return "[休息中]对面没有导弹"
        else:
            return "[e]入侵敌方导弹让他们倒大霉"
al7 = Al7(7)

class Al30(Al_general):  # 湾区铃兰

    def react(self):
        if self.state == 0:
            my_ship.attack(2)
            self.state -= 5
            self.report("正常攻击")
            #p_c_manager.boom_now()
        else:
            enemy.attack(2)
            voices.report("护盾","湾区铃兰导致扣血")
            self.report("牺牲护盾发射")
            my_ship.attack(2)
            #p_c_manager.boom_now()

    def add_atk(self, atk: int) -> int:
        if self.state < 0 < my_ship.missile and Dice.probability(0.8):
            self.report("增伤")
            my_ship.missile -= 1
            return atk + 1
        else:
            return atk

    def operate_in_our_turn(self):
        if self.state < 0:
            self.state += 1

    def suggest(self):
        if self.state == 0:
            return "[q]粒子炮倾巢发射"
        else:
            if my_ship.shelter >= 2:
                return f"[冷却中]剩余{-self.state}天|伤害加成中|[q]牺牲护盾强行攻击"
            else:
                return f"[冷却中]剩余{-self.state}天|伤害加成中"
al30 = Al30(30)

class StorageManager:

    def __init__(self):
        self.username:str = ""
        # 建立模板
        self.template:dict[str,dict[str,str|int]] = json_loader.load("storage_template")
        for al in al_manager.all_al_list.values():
            self.template["als"][str(al.index)] = 0
        # 建立空模板
        self.template_empty = deepcopy(self.template)
        # 建立映射表
        self.item_to_key_table:dict[str,str] = {}
        for key in self.template:
            for item in self.template[key]:
                self.item_to_key_table[item] = key
        # 启动主仓库
        self.repository_for_all_users = shelve.open('userdata/game_save',writeback=True)

    def sync(self):
        self.repository_for_all_users.sync()

    def login(self):
        """
        登录|将硬盘数据写入模板|新建用户|重灌入硬盘
        :return: 无
        """
        self.username = Txt.input_plus("指挥官，请输入您的代号")
        if self.username in self.repository_for_all_users.keys():
            for key in self.repository_for_all_users[self.username]:
                if key in self.template:
                    for item in self.repository_for_all_users[self.username][key]:
                        if item in self.template[key]:
                            self.template[key][item] = self.repository_for_all_users[self.username][key][item]
        else:
            Txt.print_plus("初次登录|欢迎指挥官")
        self.repository_for_all_users[self.username] = self.template
        self.sync()

    def logout(self):
        Txt.print_plus(f"指挥官{self.username}请求登出")
        Txt.print_plus("登出完毕")
        self.repository_for_all_users.close()

    def modify(self,item:str,delta:int):
        """
        增减仓库物品数量|最终业务封装
        :param item:需要改变数量的物品
        :param delta:物品数量改变量
        :return: 无
        """
        key:str = self.item_to_key_table[item]
        self.repository_for_all_users[self.username][key][item] += delta
        self.sync()

    def clear(self):
        """
        清空当前登录玩家的仓库
        :return: 无
        """
        self.repository_for_all_users[self.username] = self.template_empty
        self.sync()
storage_manager = StorageManager()

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
        print()
        try:
            me.al_list[2].print_self()
        except AttributeError:
            pass
        try:
            me.al_list[0].print_self()
        except AttributeError:
            pass
        print()

    @classmethod
    def print_basic_info(cls,days):
        """
        打印战场基本信息
        :param days: 当前天数
        :return: 无
        """
        print("~~~~~~~~~~~~~~~~~~~~~~~~")
        Txt.print_plus(f"指挥官，今天是战线展开的第{days}天。", 0)
        if days < 5:
            Txt.print_plus("当前舰船位置>>正在离港")
        elif days < 10:
            Txt.print_plus("当前舰船位置>>我方领土边缘")
        elif days <= 20:
            Txt.print_plus("当前舰船位置>>边境核心战场")
        elif days > 20:
            Txt.print_plus("当前舰船位置>>敌方腹地危险区域")

    @classmethod
    def print_suggestion(cls):
        suggestion_list = []
        for al in my_ship.al_list:
            try:
                suggest = al.suggest()
                if not suggest:
                    continue
                suggestion_list.append(suggest)
            except AttributeError:
                pass
        if not suggestion_list:
            suggestion_list.append("空闲")
        Txt.Tree("战斗辅助面板", suggestion_list).print_self()

    @classmethod
    def print_key_prompt(cls):
        key_prompt = "0/space 装弹  1 发射  2 上盾  "
        for al in my_ship.al_list:
            try:
                key_prompt += f"{al.type} {al.short_name}#{al.index}  "
            except AttributeError:
                key_prompt += "[NO INFO]  "
        print(key_prompt)

class MainLoops:

    def __init__(self):
        self.days = 0

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

    def initialize_before_fight(self):
        my_ship.initialize()
        enemy.initialize()
        self.days = 1

    def fight_mainloop(self):
        while 1:
            # dawn
            time.sleep(0.4)
            FieldPrinter.print_basic_info(self.days)
            FieldPrinter.print_for_fight(my_ship, enemy)
            FieldPrinter.print_suggestion()
            FieldPrinter.print_key_prompt()

            # morning
            for al in my_ship.al_list:
                if al:
                    al.operate_in_morning()

            # noon
            who = dice.decide_who()
            if who==1:
                Txt.print_plus("今天由我方行动")
                my_ship.react()
            else:
                Txt.print_plus("今天由敌方行动")
                enemy.react()

            # afternoon
            for al in my_ship.al_list:
                if al:
                    al.operate_in_afternoon()
                    if who==1:
                        al.operate_in_our_turn()

            # dusk
            if (result := self.is_over()) != 0:
                if result == 1:
                    Txt.print_plus("我方胜利")
                else:
                    Txt.print_plus("敌方胜利")
                return
            self.days += 1
main_loops = MainLoops()

if __name__ == "__main__":
    al_manager.choose_al("all")
    main_loops.initialize_before_fight()
    main_loops.fight_mainloop()