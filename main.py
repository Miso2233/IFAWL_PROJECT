from __future__ import annotations

import random
import time
from typing import Literal

from core import Module1_txt as Txt
from core.Module1_txt import input_plus
from core.Module2_json_loader import json_loader
from modules.Module3_storage_manager import storage_manager
from modules.Module4_voices import voices
from core.Module5_dice import dice
from modules.Module6_market_manager import Contract_manager, Contract,tools
from modules.Module7_auto_pilot import auto_pilot
from modules.Module8_al_industry import recipe_for_all_al
from modules.Module9_entry_manager import entry_manager
from core.Module10_sound_manager import sounds_manager

__VERSION__ = "IFAWL 1.1.0 'TOWARDS DAWN'"

class DamageType:
    """伤害类型枚举"""
    MISSILE_LAUNCH = "missile_launch"            # 导弹射击
    PARTICLE_CANNON_SHOOTING = "particle_cannon_shooting"  # 粒子炮射击
    ENEMY_MISSILE_BOOM = "enemy_missile_boom"    # 敌方导弹殉爆
    ORDINARY_ATTACK = "ordinary_attack"          # 杂项攻击

class Modes:
    """游戏模式枚举"""
    FIGHT = "FIGHT"
    DISASTER = "DISASTER"
    INFINITY = "INFINITY"

class MyShip:

    def __init__(self):
        self.shelter = 0
        self.missile = 0
        self.al_list: list[Al_general | None] = [None, None, None]
        self.total_al_rank = 0
        self.platform = "导弹"

    def load_al(self):
        al_str_list = storage_manager.get_al_on_ship()
        for position in range(len(al_str_list)):
            self.al_list[position] = al_manager.all_al_list.get(al_str_list[position], None)
        self.update_total_al_rank()
        self.update_platform()

    def update_total_al_rank(self):
        self.total_al_rank = 0
        for al in self.al_list:
            try:
                self.total_al_rank += al.rank_num
            except AttributeError:
                pass

    def update_platform(self):
        if not self.al_list[0]:
            self.platform = "导弹"
            return
        self.platform = self.al_list[0].platform

    def print_self_shelter(self,blind=False):
        if blind:
            print("[No Info]")
            return
        for _ in range(self.shelter):
            print("-----")

    def print_self_missile(self,blind=False):
        if blind:
            print("[No Info]")
            return
        ammunition_type = {
            "导弹": "[]",
            "粒子炮": "|| "
        }[self.platform]
        for _ in range(self.missile):
            print(ammunition_type, end="")
        print()

    def initialize(self):
        self.missile = 1
        self.shelter = 1
        for al in al_manager.all_al_list.values():
            try:
                al.initialize()
            except AttributeError:
                pass

    def attack(self, atk: int, type: str) -> int:
        """
        根据原始伤害进行加减并对目标造成攻击
        :param atk: 原始伤害
        :param type: 伤害种类
        :return: 经过加成减弱后的atk
        """
        match type:
            case DamageType.MISSILE_LAUNCH:
                sounds_manager.play_sfx("missile_launch")
            case DamageType.PARTICLE_CANNON_SHOOTING:
                sounds_manager.play_sfx("particle_cannon_shooting")
            case _:
                pass
        for al in self.al_list:
            try:
                atk = al.add_atk(atk, type)
            except AttributeError:
                pass
        atk = entry_manager.check_and_reduce_atk(atk)
        atk = entry_manager.check_and_attack_me(atk,enemy)
        enemy.shelter -= atk
        return atk

    def heal(self, hp: int) -> int:
        """
        根据原始回血量进行加减并进行治疗
        :param hp: 原始回血量
        :return: 经过加成减弱后的hp
        """
        for al in self.al_list:
            try:
                hp = al.add_hp(hp)
            except AttributeError:
                pass
        hp = entry_manager.check_and_reduce_hp(hp)
        hp = entry_manager.check_and_add_enemy_hp(hp,enemy)
        self.shelter += hp
        if hp > 0:
            sounds_manager.play_sfx("shelter_heal")
        return hp

    def load(self, num: int):
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
        operation = auto_pilot.get_operation([self.shelter, self.missile, enemy.shelter, enemy.missile, 0])
        #print(operation)
        if self.missile < 1 and operation == "1":
            operation = "0"
        if self.al_list[1] == al18 and operation == "2":
            operation = "w"
        if self.al_list[1] == al21 and operation == "2":
            al21.heal()
            operation = "pass"
        if al12.state != 0 and operation != "q" and not (self.al_list[1]==al16 and operation in ["w","2"]):
            al12.attack()
        if al39.state in [11,9] and operation == "q":
            operation = "1"
        if al15.state != 0 and operation == "1":
            voices.report("暴雨", "常规发射器离线")
            operation = ""
        if al16.state != 0 and operation == "2":
            al16.heal()
        match operation:
            case "0" | " ":
                self.load(1)
                voices.report(self.platform, "上弹")
            case "1":
                match self.platform:
                    case "导弹":
                        atk_type = DamageType.MISSILE_LAUNCH
                    case "粒子炮":
                        atk_type = DamageType.PARTICLE_CANNON_SHOOTING
                    case _:
                        atk_type = DamageType.MISSILE_LAUNCH
                result =  self.attack(1, atk_type)
                self.load(-1)
                if result > 0:
                    voices.report(self.platform, "发射")
            case "2":
                result = self.heal(1)
                if result > 0:
                    voices.report("护盾", "上盾")
            case "q":
                try:
                    self.al_list[0].react()
                except AttributeError:
                    Txt.print_plus("注意·船上没有q系终焉结")
            case "w":
                try:
                    self.al_list[1].react()
                except AttributeError:
                    Txt.print_plus("注意·船上没有w系终焉结")
            case "e":
                try:
                    self.al_list[2].react()
                except AttributeError:
                    Txt.print_plus("注意·船上没有e系终焉结")
            case "pass":
                pass
            case _:
                Txt.print_plus("你跳过了这一天！")


my_ship = MyShip()


class EnemyShip:
    def __init__(self):
        self.shelter = 0
        self.missile = 0

    def print_self_missile(self,blind=False):
        if blind:
            print("[No Info]")
            return
        for _ in range(self.missile):
            print("[]", end="")

    def print_self_shelter(self,blind=False):
        if blind:
            print("[No Info]")
            return
        for _ in range(self.shelter):
            print("-----")

    def attack(self, atk: int):
        """
        根据原始伤害进行加减并对目标造成攻击
        :param atk: 原始伤害
        :return: 无
        """
        atk = entry_manager.check_and_add_atk(atk)
        atk = entry_manager.check_and_reduce_missile(atk,my_ship)
        for al in my_ship.al_list:
            try:
                atk = al.reduce_enemy_attack(atk)
            except AttributeError:
                pass
        my_ship.shelter -= atk
        if atk <= 0:
            voices.report("护盾", "未受伤")
        elif atk <= 1:
            voices.report("护盾", "受击")
            sounds_manager.play_sfx("shelter_damaged")
        else:
            voices.report("护盾", "受重击")
            sounds_manager.play_sfx("shelter_damaged")

    def heal(self, hp: int):
        """
        根据原始回血量进行加减并进行治疗
        :param hp: 原始回血量
        :return: 无
        """
        for al in my_ship.al_list:
            try:
                hp = al.reduce_enemy_heal(hp)
            except AttributeError:
                pass
        self.shelter += hp
        if hp > 0:
            voices.report("战场播报", "敌上盾", False)

    def load(self, num: int):
        """
        根据原始上弹量进行加减并进行上弹
        :param num: 原始上弹量
        :return: 无
        """
        num = entry_manager.check_and_add_num(num)
        self.missile += num
        if num > 0:
            voices.report("战场播报", "敌上弹", False)

    def initialize(self,adj_shelter,adj_missile):
        self.missile = 2 + adj_missile
        self.shelter = 2 + adj_shelter

    def react(self):
        al35.check_if_extra_act()
        if self.shelter < 1:  # 如果护盾已被削弱
            operation = "2"  # 优先治疗
        elif self.missile < 1:  # 如果导弹没有了
            operation = "0"  # 优先上弹
        elif self.shelter < 2:  # 如果护盾不满
            operation = random.choice(["1", "2"])  # 有一定概率进行攻击或治疗
        else:
            operation = random.choice(["0", "1", "2"])  # 正常情况下随机选择操作
        if dice.probability(0.4):
            operation = random.choice(["0", "1", "2"])
        operation = al26.get_controlled_operation(operation) # 眠雀控制
        if self.missile < 1 and operation == "1":
            operation = "0"
        match operation:
            case "0":
                self.load(1)
            case "1":
                num = entry_manager.check_and_get_launch_num(self)
                self.attack(num)
                self.load(-num)
            case "2":
                self.heal(1)
            case _:
                Txt.print_plus("敌人跳过了这一天！")


enemy = EnemyShip()


class Al_manager:

    def __init__(self):
        self.al_meta_data: dict[str, dict[str, str | int]] = json_loader.load("al_meta_data")
        self.all_al_list: dict[str, Al_general] = {}

    def choose_al(self, type_choosing: str | Literal["q", "w", "e", "all"]):
        if type_choosing == "all":
            self.choose_al("q")
            self.choose_al("w")
            self.choose_al("e")
            return
        for al in self.all_al_list.values():
            if al.type == type_choosing:
                al.print_description()
        cn_type = {"q": "主武器", "w": "生存位", "e": "战术装备"}[type_choosing]
        al_position = {"q": 0, "w": 1, "e": 2}[type_choosing]
        while 1:
            inp = Txt.input_plus(
                f"\n指挥官，请输入数字选择本场战斗的{cn_type}（对局中输入{type_choosing}来使用）[-1=不使用{cn_type}]>>>")
            if inp not in self.al_meta_data or self.al_meta_data[inp]["type"] != type_choosing:
                if inp == "":
                    break
                elif inp == "-1":
                    my_ship.al_list[al_position] = None
                    break
                print(f"请在{cn_type}库中进行选择")
            else:
                Txt.print_plus(f"{self.al_meta_data[inp]['short_name']}#{self.al_meta_data[inp]['index']} 已确认装备")
                my_ship.al_list[al_position] = self.all_al_list[inp]
                print("")
                if not self.check_if_kick_e() or type_choosing == "q":
                    time.sleep(0.4)
                    break
        storage_manager.save_al_on_ship(my_ship.al_list)
        my_ship.update_platform()
        my_ship.update_total_al_rank()

    def clear_al(self):
        for index in range(len(my_ship.al_list)):
            if my_ship.al_list[index] is None:
                continue
            if my_ship.al_list[index].rank_num == 0:
                continue
            my_ship.al_list[index] = None
        storage_manager.save_al_on_ship(my_ship.al_list)
        my_ship.update_platform()
        my_ship.update_total_al_rank()

    @staticmethod
    def get_total_al_rank() -> int:
        """
        计算我方舰船上终焉结的总等级
        :return: 总等级
        """
        out = 0
        for al in my_ship.al_list:
            try:
                out += al.rank_num
            except AttributeError:
                pass
        return out

    def check_if_kick_e(self) -> bool:
        q = my_ship.al_list[0]
        e = my_ship.al_list[2]
        if not q or not e:
            return False
        if e.metadata["platform"] == "通用":
            return False
        if q.metadata["platform"] != e.metadata["platform"]:
            Txt.print_plus(
                f"注意·主武器和战术区的终焉结不匹配|[{q.short_name}]{q.metadata['platform']}|[{e.short_name}]{e.metadata['platform']}"
            )
            Txt.print_plus(f"{e.len_name}将被卸下")
            my_ship.al_list[2] = None
            Txt.print_plus(f"请选用平台相同的终焉结或选择通用终焉结")
            return True
        return False

al_manager = Al_manager()


class Al_general:
    # Apocalypse-Linked 终焉结

    def __init__(self, index: int):
        # metadata 字段
        self.index: int = index
        self.short_name: str = al_manager.al_meta_data[str(index)]["short_name"]
        self.len_name: str = al_manager.al_meta_data[str(index)]["len_name"]
        self.type: str = al_manager.al_meta_data[str(index)]["type"]
        self.rank_num: int = al_manager.al_meta_data[str(index)]["rank_num"]
        self.skin_list: list[str] = al_manager.al_meta_data[str(index)].get("skin_list", [])
        self.platform: str = al_manager.al_meta_data[str(index)]["platform"]
        self.metadata: dict[str, str | int] = al_manager.al_meta_data[str(index)]

        # industry字段
        self.recipe = recipe_for_all_al[str(self.index)]
        self.recipe["联邦信用点"] = 1100 * self.rank_num
        self.is_craftable = False

        # 签名
        al_manager.all_al_list[str(self.index)] = self

        # operation 字段
        self.state = 0

    def report(self, theme: str):
        """
        Al所包装的说话函数，省去了说话者名字
        :param theme: 主题
        :return: 无
        """
        voices.report(self.short_name, theme)

    def inject_and_report(self, theme:str, data_injected:dict[str,str]):
        """
        Al所包装的注入数据说话函数，省去了说话者名字
        :param theme: 主题
        :param data_injected: 需注入的键值对
        :return: 无
        """
        voices.inject_and_report(self.short_name,theme,data_injected)

    def print_description(self):
        """
        打印Al的描述，用于装备选择界面
        :return: 无
        """
        tag0: str = self.metadata["origin"]
        tag1: str = self.platform

        print(
            Txt.adjust(f"[{self.index}] {tag0}{self.len_name}", 60),
            Txt.adjust(f"[{tag1}平台] [{self.metadata['rank']}]", 20),
            f"{storage_manager.get_value_of(str(self.index))}在仓库"
        )
        print(f">>>>\"{self.metadata['short_name_en']}\"")
        print(self.metadata["description_txt"])
        # [30] 岩河军工“湾区铃兰”饱和式蜂巢突击粒子炮      [粒子炮平台] [VIII] 1在仓库 >>[可以离站使用]<<
        print()

    def is_on_my_ship(self):
        return self in my_ship.al_list

    def add_atk(self, atk: int, type: str):
        """
        为atk提供加成
        :param atk: 加成前atk
        :param type: 伤害种类，各Al决定是否加成
        :return: 加成后atk
        """
        return atk

    def add_hp(self, hp: int):
        """
        为heal提供加成
        :param hp: 加成前hp
        :return: 加成后hp
        """
        return hp

    def add_num(self, num: int):
        """
        为load提供加成
        :param num: 加成前num
        :return: 加成后num
        """
        return num

    def reduce_enemy_attack(self, atk):
        """
        削弱敌方attack
        :param atk: 削弱前atk
        :return: 削弱后atk
        """
        return atk

    def reduce_enemy_heal(self, hp):
        """
        削弱敌方heal
        :param hp: 削弱前hp
        :return: 削弱后hp
        """
        return hp

    def operate_in_morning(self):
        pass

    def operate_in_afternoon(self):
        pass

    def initialize(self):
        self.state = 0

    def react(self):
        pass

    def print_self(self):
        if self.state != 0:
            try:
                print(self.skin_list[self.state])
                print()
            except IndexError:
                pass

    def print_self_behind_shelter(self):
        pass

    def print_self_before_shelter(self):
        pass

    def suggest(self) -> str | None:
        return None

    def operate_in_our_turn(self):
        pass

    def refresh_craftable_tag(self):
        """
        刷新自己能否被合成
        :return: 无
        """
        self.is_craftable = tools.is_affordable(self.recipe,storage_manager.show_assets())

    def print_recipe(self,assets:dict[str,int]):
        """
        打印合成配方
        :param assets: 当前仓库资产
        :return: 无
        """
        if self.rank_num == 0:
            return
        # 基本信息
        line1 = ""
        str1 = f"[{self.index}]{self.len_name} [{self.metadata['rank']}]"
        line1 += Txt.adjust(str1,45)
        # 可合成性
        if self.is_craftable:
            craftable_tag = "[可合成●]"
        else:
            craftable_tag = "[不可合成]"
        line1 += Txt.adjust(craftable_tag,12)
        # 本终焉结存货
        line1 += f"现有 {assets[str(self.index)]} 在仓库"
        print(line1)
        # 物品存货
        line2 = ""
        for item,require in self.recipe.items():
            inventory = assets[item]
            note = "[▲]" if require > inventory else ""
            str0 = f"|-{item}x{require}/{inventory}{note}"
            line2 += Txt.adjust(str0,22)
        print(line2)
        print()

    def craft_self(self):
        """
        制造自己
        :return: 无
        """
        storage_manager.transaction(self.recipe,{str(self.index):1})

class Al3(Al_general):

    def react(self):
        if dice.probability(0.3 * enemy.shelter):
            my_ship.attack(1, DamageType.ORDINARY_ATTACK)
            self.report("命中")
        else:
            self.report("未命中")

    def suggest(self) -> str | None:
        prob = enemy.shelter * 30
        if prob != 0:
            return f"[e]发射巡飞弹|命中率{prob}%"
        else:
            return "[无命中率]不建议发射巡飞弹"


al3 = Al3(3)


class Al4(Al_general):

    def react(self):
        if self.state < 2:
            self.state += 2
            self.report("收到")
            time.sleep(0.4)
            if self.state == 2:
                self.report("准备好")

    def operate_in_afternoon(self):
        if self.state >= 2:
            self.state += 1
            if self.state == 4:
                self.state = 0
            if dice.probability(0.7):
                my_ship.attack(1, "missile_launch")
                self.report("命中")
            else:
                self.report("未命中")
                my_ship.load(1)
                self.report("回流")

    def suggest(self) -> str | None:
        return \
            ["[q]部署发射台",
             "[q]挂载铜芯导弹 2/2",
             "[自动攻击中]回流系统正在生效",
             "[自动攻击中]回流系统正在生效"][self.state]


al4 = Al4(4)


class Al5(Al_general):  # 水银

    def react(self):
        if self.state == 0:
            self.state += 1
            self.report("收到")
        elif self.state == 1:
            self.state += 1
            self.report("准备好")
        else:
            self.state = 0
            if random.randint(0, 9) > -1:
                my_ship.attack(2, DamageType.MISSILE_LAUNCH)
                self.report("命中")
            else:
                self.report("未命中")

    def add_num(self, num) -> int:
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
                self.state = 1
                self.report("收到")
            else:
                self.state = 2
                self.report("生之帝国")
        elif self.state == 1:
            self.state = 2
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
                my_ship.attack(1, DamageType.ENEMY_MISSILE_BOOM)
                time.sleep(0.4)
                self.report("引爆成功")
            else:
                time.sleep(0.4)
                self.report("引爆失败")
        self.state = 0

    def suggest(self):
        if enemy.missile == 0:
            return "[休息中]对面没有导弹"
        else:
            return "[e]入侵敌方导弹让他们倒大霉"


al7 = Al7(7)


class Al8(Al_general):

    def react(self):
        if self.state < 2:
            self.state += 1
            self.report("收到")
            if self.state == 2:
                self.state = 3
                self.report("准备好")
        elif self.state == 2:
            self.state = 3
            self.report("续杯")

    def add_atk(self, atk, type):
        if type != DamageType.MISSILE_LAUNCH:
            return atk
        if dice.probability(0.8):
            atk += 1
            self.report("成功")
        else:
            self.report("失败")
        self.state -= 1
        if self.state == 1:
            self.state = 0
        return atk

    def suggest(self):
        return ["[q]建造发射架基础 1/2", "[q]建成发射架炮管 2/2", "[q]续杯|导弹伤害加成中", "[已建立]导弹伤害加成中"][
            self.state]


al8 = Al8(8)


class Al9(Al_general):

    def react(self):
        if self.state == 0:
            if my_ship.shelter <= 1:
                my_ship.heal(1)
                self.report("护盾学急救")
            self.state += 1
            self.report("收到")

    def add_hp(self, hp):
        if self.state == 1:
            hp += 2
            self.state = 0
            self.report("急救")
        return hp

    def suggest(self):
        if self.state == 0:
            if my_ship.shelter <= 1:
                return "[w]建立吊舱|护盾学急救就绪"
            else:
                return "[w]建立吊舱"
        else:
            return "[已就绪]|[2]释放护盾"


al9 = Al9(9)


class Al10(Al_general):

    def react(self):
        if my_ship.shelter >= 2:
            my_ship.shelter -= 1
            my_ship.load(2)
            self.report("牺牲护盾")
        elif my_ship.shelter <= 1:
            if my_ship.missile != 0:
                my_ship.heal(2)
                my_ship.load(-1)
                self.report("拆解导弹")
            else:
                my_ship.heal(1)
                self.report("护盾不足")

    def suggest(self):
        if my_ship.shelter >= 2:
            return "[e]拆除护盾|获取2枚导弹"
        elif my_ship.shelter <= 1:
            if my_ship.missile != 0:
                return "[e]拆除导弹|获取2层护盾"
            else:
                return "[资源耗竭]|[2]回充护盾|[0]回充导弹"


al10 = Al10(10)


class Al11(Al_general):

    def react(self):
        if self.state == 0:
            self.state += 2
            my_ship.heal(1)
            self.report("收到")
            self.report("归来")
        elif self.state == 2:
            my_ship.attack(1, DamageType.ORDINARY_ATTACK)
            my_ship.heal(1)
            self.state -= 1
            self.report("为了身后的苍生")

    def reduce_enemy_heal(self, hp):
        if self.state == 0:
            return hp
        my_ship.heal(1)
        self.state -= 1
        self.report("汲取成功")
        hp -= 1
        return hp

    def suggest(self):
        return ["[w]建立汲能器", "[剩余一次]敌方护盾锁定中", "[就绪]敌方护盾锁定中|[w]主动汲取敌方护盾"][self.state]


al11 = Al11(11)


class Al12(Al_general):

    def __init__(self, index):
        super().__init__(index)
        self.atk_list: list[int] = [0, 0, 1, 2, 4, 5, 7, 8]

    def react(self):
        if self.state < 7:
            self.state += 1
            self.report("充能中")
        else:
            my_ship.attack(self.atk_list[self.state], DamageType.PARTICLE_CANNON_SHOOTING)
            # p_c_manager.boom_now()
            self.state = 0
            self.report("过热")

    def attack(self):
        if self.atk_list[self.state] != 0:
            my_ship.attack(self.atk_list[self.state], DamageType.PARTICLE_CANNON_SHOOTING)
            # p_c_manager.boom_now()
            self.state = 0
            self.report("攻击")
        elif self.atk_list[self.state] == 0:
            self.state = 0
            self.report("十四行赞美诗与一首绝望的歌")
            my_ship.heal(1)

    def print_self(self):
        if self.state != 0:
            print(self.skin_list[self.state // 3], end="")
            print(f"[晴空]粒子炮集群伤害水准：{self.atk_list[self.state]}")
            print()

    def suggest(self):
        if self.state == 0:
            return "[q]开始充能"
        elif self.state == 7:
            return f"[q/任意键]最高功率开火|{self.atk_list[self.state]}伤害"
        elif self.atk_list[self.state] == 0:
            return "[q]继续充能|[任意键]放弃开火并触发回盾|0伤害"
        else:
            return f"[q]继续充能|[任意键]粒子炮开火|{self.atk_list[self.state]}伤害"


al12 = Al12(12)


class Al13(Al_general):

    def react(self):
        if my_ship.missile == 0:
            my_ship.missile += 1
            self.report("导弹不足")
        elif my_ship.missile == 1:
            my_ship.missile -= 1
            my_ship.attack(1, DamageType.MISSILE_LAUNCH)
            self.report("单导弹导航")
        else:
            my_ship.missile -= 2
            my_ship.attack(2, DamageType.MISSILE_LAUNCH)
            self.report("全功率导航")

    def suggest(self):
        if my_ship.missile == 0:
            return "[无导弹]不能使用北极|[0]装弹"
        elif my_ship.missile == 1:
            return "[e]导航单颗导弹|[0]装弹"
        else:
            return "[e]全功率导航"


al13 = Al13(13)


class Al14(Al_general):

    def react(self):
        if my_ship.shelter > 0:
            self.report("强化成功")
            self.state += 3
            my_ship.shelter -= 1
        else:
            my_ship.heal(1)
            self.report("护盾不足")
        if dice.probability(0.2) and my_ship.shelter > 0:
            self.react()

    def reduce_enemy_attack(self, atk):
        minor = min(self.state, atk)
        if minor == self.state:
            self.report("信风清空")
        self.state -= minor
        atk -= minor
        return atk

    def print_self(self):
        print(self.skin_list[self.state % 3], end="")
        print("\n//\\\\//" * (self.state // 3))

    def suggest(self):

        if my_ship.shelter == 0:
            return "[护盾不足]不能使用信风|[2]回充护盾"
        else:
            return "[w]强化护盾"


al14 = Al14(14)


class Al15(Al_general):

    def react(self):
        if self.state == 0:
            self.state = 2
            self.report("上线")
            my_ship.missile += 1
        else:
            self.state = 0
            self.report("下线")

    def add_num(self, num) -> int:
        if self.state > 0:
            self.report("弹雨滂沱")
            return num + 1
        else:
            return num

    def operate_in_afternoon(self):
        if self.state > 0:  # 暴雨
            if self.state == 1:
                if my_ship.missile > 0:
                    my_ship.missile -= 1
                    my_ship.attack(1, DamageType.MISSILE_LAUNCH)
                    self.state = 2
                    self.report("攻击")
                else:
                    self.state = 0
                    self.report("下线")
            else:
                self.state -= 1

    def suggest(self):
        return ["[q]发射台开机|激活预备导弹", "[自动攻击中]当日发射|[q]发射台关机|[0]辅助上弹",
                "[自动攻击中]次日发射|[q]发射台关机"][self.state]


al15 = Al15(15)


class Al16(Al_general):
    cure_list = [0, 3, 6, 8, 10]

    def react(self):
        if self.state < 4:
            self.state += 1
            self.report("收到")
        else:
            my_ship.heal(self.cure_list[4]-1)
            self.report("超载")
            self.state = 0

    def heal(self):
        if self.state != 0:  # 情诗
            my_ship.heal(self.cure_list[self.state]-1)
            self.report("释放")
            self.state = 0

    def print_self(self):
        if self.state != 0:
            print(self.skin_list[self.state // 2], end="")
            print(f"[情诗]大规模护盾存量：{self.cure_list[self.state]}")

    def suggest(self):
        if self.state == 0:
            return "[w]开始充能"
        elif self.state == 4:
            return f"[w/2]极限存量护盾|{self.cure_list[self.state]}层"
        else:
            return f"[w]继续充能|[2]释放大规模护盾|{self.cure_list[self.state]}层"


al16 = Al16(16)


class Al17(Al_general):

    def react(self):
        if my_ship.missile == 0:
            my_ship.missile += 1
            self.report("无导弹")
        elif my_ship.shelter <= 0:
            my_ship.heal(1)
            self.report("护盾不足")
        else:
            enemy.attack(1)
            my_ship.attack(2, DamageType.MISSILE_LAUNCH)
            my_ship.missile -= 1
            self.report("攻击成功")

    def suggest(self):
        if my_ship.missile == 0:
            return "[资源耗竭][0]装填弹药"
        elif my_ship.shelter <= 0:
            return "[资源耗竭][2/w]回复护盾"
        else:
            return "[q]发射白夜装甲弹"


al17 = Al17(17)


class Al18(Al_general):
    def react(self):
        if dice.probability(0.6) or self.state == 1:
            my_ship.heal(2)
            self.state = 0
            self.report("成功")
        else:
            my_ship.heal(1)
            self.state = 1
            self.report("失败")

    def suggest(self):
        if self.state == 0:
            return "[2/w]回充护盾|概率回充2层"
        else:
            return "[2/w]回充护盾|回充2层"


al18 = Al18(18)

class Al19(Al_general):
    
    def react(self):
        if self.state==0:
            self.state=3
            self.report("收到")
            self.report("准备好")

    def operate_in_afternoon(self):
        if self.state>0:
            self.state-=1
            if dice.probability(0.5):
                my_ship.heal(1)
                self.report("补给护盾")
            else:
                my_ship.load(1)
                self.report("补给弹药")
            if dice.probability(0.5):
                al3.react()

    def suggest(self):
        return ["[e]呼叫浅草寺战术补给","[补给中]剩余一次","[补给中]剩余两次","[补给中]剩余三次"][self.state]

al19 = Al19(19)

class Al20(Al_general):
    def react(self):
        if self.state == 0:
            dice.probability_current+=0.6
            self.state=-5
            self.report("扫描")
        else:
            self.report("冷却中")

    def operate_in_morning(self):
        if self.state<0:
            self.state+=1
    
    def suggest(self):
        if self.state == 0:
            return f"[e]压制敌方行动|次日仍为我方航行日的概率：{dice.probability_current:.1f}"
        else:
            return f"[冷却中]剩余{-self.state}天|次日仍为我方航行日的概率：{dice.probability_current:.1f}"


al20 = Al20(20)

class Al21(Al_general):

    def heal(self):
        if self.state>2 and dice.probability(0.5):
            al21.react()
        else:
            al21.state+=1
            self.report("充注")

    def react(self):
        if self.state>0:           
            my_ship.heal(int(self.state*1.5))            
            self.state=0
            self.report("主动凝固")
        else:
            self.state+=1
            self.report("无屏障")
            self.report("充注")

    def operate_in_afternoon(self):
        if my_ship.shelter<=0:
            if self.state>0:
                self.state-=1
                my_ship.shelter=1
                self.report("急救")

    def print_self_behind_shelter(self):
        if self.is_on_my_ship():
            if self.state <= 6:
                print("/-/-/-/\n"*self.state)
            else:
                print(f"/-/-/-/ x{self.state}")

    def suggest(self):
        if self.state>=3:
            return "[w]主动凝固|[2]充注液态护盾|请注意意外凝固风险"
        elif self.state>0:
            return "[w]主动凝固|[2]充注液态护盾|急救保护中"
        else:
            return "[2]充注液态护盾"


al21 = Al21(21)

class Al22(Al_general):
    def react(self):
        if self.state == 0:
            my_ship.attack(1,DamageType.ORDINARY_ATTACK)
            self.state=-3
            self.report("攻击")
        else:
            self.report("冷却中")

    def operate_in_afternoon(self):
        if self.state == -3 and enemy.shelter<=0:
            my_ship.attack(1,DamageType.ORDINARY_ATTACK)
            self.report("处决")
        if self.state == -1:
            self.report("就绪")

        if self.state<0:
            self.state+=1

    def suggest(self):
        if self.state == 0:          
            if enemy.shelter<=1:
                return "[e]处决敌方"
            else:
                return "[e]造成1伤害"
        else:
            return f"[冷却中]剩余{-self.state}天"



al22 = Al22(22)

class Al23(Al_general):

    def react(self):
        for i in range(3):
            if my_ship.missile>0:
                my_ship.load(-1)
                my_ship.attack(1,DamageType.MISSILE_LAUNCH)
                self.report("攻击成功")
            else:
                my_ship.load(1)
                self.report("导弹耗尽")
                break
    

    def suggest(self):
        if my_ship.missile>=3:
            return "[q]浮游炮全功率开火"
        else:
            return ["[无导弹]不能使用浮生|[0]上弹","[q]浮游炮开火|导弹不足 1/3|[0]上弹","[q]浮游炮开火|导弹不足 2/3|[0]上弹"][my_ship.missile]


al23 = Al23(23)

class Al24(Al_general):

    def find_the_quotient_rounded_up(self, a, b):#向上取整
        if a % b != 0:
            return (a//b)+1
        else:
            return a//b

    def react(self):
        if self.state == 0:
            enemy.missile += 5
            self.state += 5
            while self.state:
                enemy.missile -= 1
                my_ship.attack(1,DamageType.ENEMY_MISSILE_BOOM)
                self.report("攻击成功")#
                self.state-=1
                if dice.probability(0.4*(4-self.state)):
                    break
            if self.state<0:
                self.state = 0
        elif self.state != 0:
            self.report("主动入侵")#            
            al7.react()
            self.state -= 1

    def reduce_enemy_attack(self, atk):
        if self.state == 0:
            return atk
        if dice.probability(0.99):
            self.state -= self.find_the_quotient_rounded_up(atk, 2)
            atk = 0
            my_ship.missile += 1
            self.report("拦截成功")
            if self.state < 0:
                self.state = 0
        return atk

#    def print_self(self):##祖师爷
#        if self.is_on_my_ship():
#            print("奶油的工作流")
#            if self.state>0:
#                print(f"|当前-解析保护中|可入侵敌方导弹[q]|『密钥』：{self.state}")
#            else:
#                print("|当前-空闲|电子进攻就绪[q]")

    def suggest(self):
        if self.state>0:
            return f"[q]入侵敌方导弹|解析保护中|『密钥』：{self.state}"
        else:
            return "[q]电子爆破进攻|获得秘钥"


al24 = Al24(24)


class Al25(Al_general):
    def react(self):
        if self.state == 0:
            self.state=3
            self.report("启动报告")
        
    def reduce_enemy_attack(self, atk):
        if atk == 0:
            return atk
        if self.state>0:
            self.report("拦截")
            self.state-=1
            if dice.probability(0.3):
                my_ship.attack(1,DamageType.ORDINARY_ATTACK)#
                self.report("反击")
            if self.state == 0:
                self.state=-5
                self.report("冷却")
            return 0
        else:
            return atk

    def operate_in_afternoon(self):
        if self.state<0:
            self.state+=1

    def print_self(self):
        if self.state<0:
            print(self.skin_list[4])
        elif self.is_on_my_ship():
            print(self.skin_list[self.state])

    def suggest(self):
        if self.state<0:
            return f"[冷却中]剩余{-self.state}天"
        elif self.state == 0:
            return f"[w]启动贾氏无人机群"
        else:
            return f"[防御进行中]剩余{self.state}次"


al25 = Al25(25)

class Al26(Al_general):

    def react(self):
        if self.state == 0:
            self.state = 3
            self.report("启动报告")

    def operate_in_afternoon(self):
        if self.state < 0:
            self.state += 1

    def is_my_turn(self):
        if self.state == 3:
            self.state -= 1
            return 1
        return 0

    def get_controlled_operation(self, operation:str)->str:
        if self.state <= 0:
            return operation
        self.report("控制成功")
        controlled_operation = Txt.ask_plus("[眠雀]选择敌方操作",["0","1","2"])
        self.state -= 1
        if operation == controlled_operation:
            self.report("谐振成功")
            my_ship.attack(1,DamageType.ORDINARY_ATTACK)
            self.state += 1
        if self.state == 0:
            self.state = -5
        return controlled_operation


    def suggest(self):
        if self.state == 0:
            return "[e]控制敌方两次行动"
        elif self.state < 0:
            return f"[冷却中]剩余{-self.state}天"
        elif self.state > 0 and dice.current_who == 1:
            return f"[生效中]剩余{self.state}次"
        else:
            return "[支配中]输入敌方指令[0]装弹|[1]发射|[2]上盾"


al26 = Al26(26)

class Al27(Al_general):#瞳猫

    def react(self):
        if self.state < 9:
            self.state += 1
            self.report("充能")

    def operate_in_morning(self):
        if self.is_on_my_ship() and dice.current_who == 1 and self.state < 9:
            self.state += 1

    def add_atk(self, atk, type):
        """
        瞳猫只是一只小猫，他不会对你的攻击造成加成
        只是我需要写在这里方便在atk时调用罢了
        """
        if self.is_on_my_ship() and self.state > 0:
            self.state = 0
            self.report("层数清空")
        return atk

    def reduce_enemy_attack(self, atk):
        if self.is_on_my_ship() and atk > 0:
            if dice.probability(self.state*0.1-(my_ship.shelter+al14.state-1)*0.12):
                atk = 0
                self.report("喵")
        return atk

    def suggest(self):
        if self.state<9:
            return f"[e]提升层数|{self.state}层|当前闪避率>>{self.state*10-(my_ship.shelter+al14.state-1)*12}%"
        else:
            return f"[层数已满]|{self.state}层|当前闪避率>>{self.state*10-(my_ship.shelter+al14.state-1)*12}%"

al27 = Al27(27)

class Al28(Al_general):#鹘鸮

   
    def print_self_before_shelter(self):
        if self.state > 0:
            print(r"/===\鹘鸮招架中")
            print("~~~~~\n"*max(0,4-self.state))


    def react(self):
        if self.state == 0 :
            self.state = 1
            self.report("启动报告")

    def reduce_enemy_attack(self, atk):
        if self.state>0 and self.state<4:
            while atk:
                atk -= 1
                self.state += 1
                if self.state == 4:
                    break
        if self.state >= 4:
            self.state += atk
        if self.state > 0:
            print(f"[鹘鸮]当前层数：{self.state}")
        return atk

    def operate_in_afternoon(self):
        if self.state<0:
            self.state += 1
            return
        if dice.current_who == 0:
            if self.state == 1:
                my_ship.load(2)
                self.report("冷却")
                self.state = -4
            elif self.state>1:
                if my_ship.missile>1:
                    my_ship.load(-1)
                    my_ship.attack(self.state+1,DamageType.ORDINARY_ATTACK)                    
                    self.report("反击")
                    self.report("反击")
                    print(f"[鹘鸮]造成伤害：{random.randint(3,self.state+1)}")
                else:
                    my_ship.attack(self.state,DamageType.ORDINARY_ATTACK)
                    self.report("反击")
                    print(f"[鹘鸮]造成伤害：{random.randint(2,self.state)}")
                if enemy.shelter<0:
                    Txt.print_plus("[鹘鸮]勘破灭！",2)
                self.state = 0
    
    def suggest(self):
        if self.state == 0:
            return "[q]进入招架状态"
        elif self.state > 0:
            return f"[招架中]临时护盾剩余{max(0,4-self.state)}点"
        else:
            return f"[冷却中]剩余{-self.state}天"
        
al28=Al28(28)

class Al29(Al_general):#酒师

    state = []

    def initialize(self):
        self.state = []

    def react(self):
        self.state.append(
            random.choices([0,1,2,3], weights=[0,3,3,2])[0]
        )
        self.report("建立治疗塔")

    def operate_in_morning(self):
        if self.state:

            self.state = [x for x in self.state if x != 0]
                
            my_ship.heal(
                len(self.state)
            ) 
            for i in range(len(self.state)):
                self.state[i] -= 1
            
            Txt.print_plus(f"[酒师]工作中|救治{len(self.state)}次")

            self.state = [x for x in self.state if x != 0]

    def print_self(self):
        if self.is_on_my_ship():
            for i in self.state:
                print(self.skin_list[i],end=" ")
            print()

    def suggest(self):
        if not self.state:
            return "[2/w]建立治疗塔"
        else:
            return f"[2/w]建立治疗塔|工作中|预计维持{max(self.state)}天|总治疗量{sum(self.state)}层" 

al29=Al29(29)

class Al30(Al_general):

    def react(self):
        if self.state == 0:
            my_ship.attack(2, DamageType.PARTICLE_CANNON_SHOOTING)
            self.state -= 5
            self.report("正常攻击")
            # p_c_manager.boom_now()
        else:
            enemy.attack(2)
            voices.report("护盾", "湾区铃兰导致扣血")
            self.report("牺牲护盾发射")
            my_ship.attack(2, DamageType.PARTICLE_CANNON_SHOOTING)
            # p_c_manager.boom_now()

    def add_atk(self, atk: int, type: str) -> int:
        if self.state < 0 and 1 < my_ship.missile and dice.probability(0.8):
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

class Al31(Al_general):#白鲟

    def react(self):
        if self.state == 0:
            self.state = 6
            my_ship.load(1)
            self.report("启动报告")

    def reduce_enemy_attack(self, atk):
        if self.state > 0 and atk > 0:
            di_atk = min(self.state,atk)
            self.state -= di_atk
            atk -= di_atk
            self.report("保护")
            if self.state==0:
                self.state=-5
                self.report("冷却")
        return atk
            
    def operate_in_afternoon(self):
        if self.state<0:
            self.state+=1
        elif self.state>0 and dice.current_who == 1:
            self.state-=1
            self.report("护盾流失")
            if self.state == 0:
                self.state=-5
                self.report("冷却")

    def suggest(self):
        if self.state==0:
            return "[w]部署临时护盾并获得一枚弹药"
        elif self.state>0:
            return f"[保护中]剩余{self.state}层"
        else:
            return f"[冷却中]剩余{-self.state}天"

    def print_self(self):
        print(".....\n"*self.state)

al31=Al31(31)

class Al34(Al_general):#风间浦

    state = [0,0]

    def initialize(self):
        self.state = [0,0]

    def react(self):
        if self.state[0] == 0:
            self.state[0] = 8
            my_ship.attack(1,DamageType.ORDINARY_ATTACK)
            self.report("激进模式启动")

    def add_hp(self, hp):
        if not self.is_on_my_ship():
            return hp
        if self.state[0] == 0 and dice.probability(0.5):
            self.report("保守模式治疗加成")
            return hp + 1
        elif self.state[0] == 0 and my_ship.shelter == 0:
            self.report("保守模式治疗加成")
            return hp + 1
        else:
            return hp


    def operate_in_afternoon(self):
        if self.state[0] > 5:
            if my_ship.shelter <= 0:
                my_ship.shelter = 1
                self.report("激进模式保护")
        elif self.state[0] == 5 and self.state[1] != 0:
            my_ship.heal(self.state[1])
            self.state[1] = 0
            self.report("安全港就位")

        if self.state[0] > 5 and dice.current_who == 0:
            self.state[0] -= 1
        elif 0 < self.state[0] <= 5 and dice.current_who == 1:
            self.state[0] -= 1

    def reduce_enemy_attack(self, atk):#实则不然
        if self.state[0] > 5 and atk > 0:
            self.state[1] += atk
            self.inject_and_report("记录伤害",{"atk":atk})
        return atk

    def print_self(self):
        pass

    def suggest(self):
        if self.state[0] > 5:
            return f"[激进模式]剩余{self.state[0] - 5}天|{self.state[1]}伤害计入"
        elif self.state[0] == 5:
            return f"[脱离激进模式]{self.state[1]}护盾即将回充"
        elif self.state[0] > 0:
            return f"[充能中]剩余{self.state[0]}天"
        else:
            return "[w]进入激进模式|[保守模式]回盾加成中"        

al34=Al34(34)

class Al35(Al_general): # 青鹄

    voi_list={"q":["复道行空，敌盾贯通！","泡影俱散，对面完蛋！"],"w":["固若金汤，有烟无伤！","防微杜渐，护盾无限！"],"e":["",""]}

    def react(self):
        main_loops.days-=1
        if self.state<4:
            self.state+=2
            self.report("充能")
        else:
            if my_ship.missile>1:
                my_ship.attack(2,DamageType.ORDINARY_ATTACK)
                my_ship.load(-2)
                self.state=0
                self.report("攻击")
            else:
                my_ship.load(1)
                if dice.current_who==0:
                    my_ship.load(1)
                self.report("装弹")
    def operate_in_morning(self):
        if self.is_on_my_ship():
            self.state+=1
        if self.state>=4 and dice.current_who==0:
            my_ship.heal(1)
            my_ship.load(1)
            self.report("准备")

    def check_if_extra_act(self):
        
        if self.state>=4 and dice.current_who==0:
            suggestion_tree = field_printer.generate_suggestion_tree()
            suggestion_tree.topic = "额外回合操作"
            suggestion_tree.print_self()
            inp=Txt.ask_plus("""+[+Extra action+]+>>选择你的操作[q/w/e]立即响应或重置其冷却""",["q","w","e"])
            d="qwe".find(inp)
            al_temp:Al_general=my_ship.al_list[d]
            if al_temp:
                if type(al_temp.state)==int and al_temp.state<0:
                    al_temp.state=0
                    self.report_plus(inp,1)
                    Txt.print_plus(f"[{al_temp.type}] {al_temp.short_name}#{al_temp.index}冷却已重置")
                else:
                    self.report_plus(inp,0)
                    al_temp.react()
            if self.state!=0 :
                self.state-=4
    
    def report_plus(self, type, num):
        txt=self.voi_list[type][num]
        if txt=="":
            return
        if storage_manager.show_assets()["39"]<3:
            txt="[青鹄]"+txt[0:min(len(txt),4)]+"！"
            Txt.print_plus(txt)

    def suggest(self):
        if self.state<1:
            return f"[e]增加二层充能|充能层数{self.state}/4"
        elif self.state<4:
            return f"[e]增加二层充能并进入待命状态|充能层数{self.state}/4"
        elif my_ship.missile>1:
            return f"[e]攻击对方并清空充能|[待命中]获得额外回合|充能层数{self.state}/4"
        else:
            return f"[e]装弹|[待命中]获得额外回合|充能层数{self.state}/4"

al35=Al35(35)

class Al38(Al_general): # 澈

    def initialize(self):
        self.state=[0,False]

    def react(self):
        self.state[0]+=3
        self.report("获得锋镝")
        enemy.attack(1) # todo:禁用烈风
        enemy.attack(1)

    def reduce_enemy_attack(self, atk):
        """
        其实并不会reduce
        """
        if self.is_on_my_ship() and self.state[1]==False and dice.probability(0.5):
            self.state[0]+=1
            self.report("收到")
            
        return atk
    
    def operate_in_afternoon(self):
        if self.state[0]>0 and my_ship.shelter<1:
            cure = min(self.state[0],2-my_ship.shelter)
            self.state[0]-=cure
            my_ship.heal(cure)
            self.report("护盾补充")

    
    def operate_in_morning(self):
        if self.state[0]>9 and self.state[1]==False:
            self.state[1]=True
            self.report("激进模式开启")
        elif self.state[0]<5 and self.state[1]==True:
            self.state[1]=False
            self.report("激进模式关闭")

    def add_atk(self, atk, type):
        if self.state[1]==False and self.is_on_my_ship() and dice.probability(0.5):
            self.state[0]+=1
            self.report("收到")
        if self.state[1] and self.state[0]>0:
            self.state[0]-=1
            self.report("牺牲加成")
            return atk+1
        return atk

    def print_self(self):
        if self.state[0] <= 5:
            print("--X--\n"*self.state[0])
        else:
            print(f"--X-- x{self.state[0]}")

    def suggest(self):
        if self.state[1]:
            return f"[w]自伤并获得三点锋镝|[寂]伤害加成中|[锋镝]>{self.state[0]}"
        else:
            return f"[w]自伤并获得三点锋镝|[澄]敌我攻击概率获得锋镝|[锋镝]>{self.state[0]}"

al38=Al38(38)

class Al39(Al_general): # 黎明维多利亚
    """
    黎明维多利亚的state转移过程是：0 2 4 6 8 10->11 9 7 5 3 1->0
    """

    def add_num(self, num: int):
        if self.state % 2 == 1:
            return num
        if num <= 0:
            return num
        self.state += num * 2
        if self.state > 10:
            self.state = 10
        self.report("建造中")
        return num

    def operate_in_afternoon(self):
        if self.state == 10 or self.state > 11:
            self.state = 11
            self.report("准备好")
        if self.state == 1 or self.state < 0:
            self.state = 0
            self.report("下线")

    def add_atk(self, atk: int, type: str):
        if type != DamageType.MISSILE_LAUNCH:
            return atk
        if self.state % 2 == 0 or self.state <= 1:
            return atk
        atk += 1
        self.report("增伤")
        self.state -= 2
        return atk

    def react(self):
        if self.state % 2 == 0:
            my_ship.load(1)
            voices.report(my_ship.platform, "上弹")
        elif self.state in [11,9]:
            result =  my_ship.attack(1, DamageType.MISSILE_LAUNCH)
            my_ship.load(-1)
            if result > 0:
                voices.report(my_ship.platform, "发射")
        else:
            rest = (self.state-1) // 2
            launch_num = min(rest,my_ship.missile)
            if launch_num <= 0:
                self.report("导弹不足")
                return
            for _ in range(launch_num):
                my_ship.attack(1,DamageType.MISSILE_LAUNCH)
                my_ship.load(-1)
            enemy.attack(launch_num-1)
            self.state = 1

    def suggest(self):
        if self.state % 2 == 0:
            return f"[充能中]当前层数>{int(self.state/2)}/5|[0/任意方式]获得弹药以充能"
        elif self.state in [11,9]:
            return f"[保守状态]剩余层数>{int((self.state-1)/2)}/5|[1/q]发射增强导弹"
        else:
            return f"[爆发状态]剩余层数>{int((self.state-1)/2)}|[1]发射增强导弹|[q]全弹发射 扣除{int(min((self.state-1) // 2,my_ship.missile))}点护盾"

al39 = Al39(39)

class FieldPrinter:

    def print_for_fight(self, me: MyShip, opposite: EnemyShip):
        """
        打印fight模式下双方护盾和导弹，以及我方Al
        :param me:
        :param opposite:
        :return: 无
        """
        opposite.print_self_missile(entry_manager.get_rank_of("2")>=1)
        print()
        opposite.print_self_shelter()
        print("\n\n\n")
        try:
            me.al_list[1].print_self()
        except AttributeError:
            pass
        try:
            me.al_list[0].print_self_before_shelter()
        except AttributeError:
            pass
        me.print_self_shelter(entry_manager.get_rank_of("2")>=2)
        try:
            me.al_list[1].print_self_behind_shelter()
        except AttributeError:
            pass
        me.print_self_missile()
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

    def print_basic_info(self, days):
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

    def generate_suggestion_tree(self):
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
        return Txt.Tree("战斗辅助面板", suggestion_list)

    def print_key_prompt(self):
        key_prompt = "[0/space] 装弹  [1] 发射  [2] 上盾  "
        for al in my_ship.al_list:
            try:
                key_prompt += f"[{al.type}] {al.short_name}#{al.index}  "
            except AttributeError:
                key_prompt += "[NO INFO]  "
        print(key_prompt)


field_printer = FieldPrinter()


class StationTreesManager:

    def __init__(self):
        # 树构建
        self.all_tree_list: dict[str, Txt.Advanced_tree] = {}
        all_trees = json_loader.load("station_trees")
        for topic in all_trees:
            self.all_tree_list[topic] = Txt.Advanced_tree(all_trees[topic])
        # 网格大小确认
        self.column = 0
        self.row = 0
        for tree in self.all_tree_list.values():
            self.column = max(self.column, tree.col + 1)
            self.row = max(self.row, tree.row + 1)
        # 生成网格
        self.grid: list[list[None | Txt.Advanced_tree]] = [[None for _ in range(self.row)] for _ in range(self.column)]
        for tree in self.all_tree_list.values():
            self.grid[tree.col][tree.row] = tree

    def inject_all(self):
        self.all_tree_list["空间站信息"].inject({
            "weather": random.choice(
                [
                    "晴朗",
                    "大雾",
                    "恒星磁暴",
                    "微陨石暴雨",
                    "平静",
                    "error-空间站气象仪故障",
                    "恒星季风",
                    "小行星骤雨",
                    "稀疏尘埃云",
                    "稠密尘埃云"
                ]
            ),
            "height": random.randint(35997, 36003),
            "hour": time.strftime("%H"),
            "minute": time.strftime("%M")
        })
        self.all_tree_list["指挥官信息"].inject({
            "username": storage_manager.username,
            "ship_name": storage_manager.get_value_of("ship_name"),
            "isk_num": storage_manager.get_value_of("联邦信用点"),
            "cmp_num": storage_manager.get_value_of("合约纪念点")
        })
        self.all_tree_list["按键导航"].inject({})
        self.all_tree_list["终焉结信息"].inject({
            "total_al_rank": my_ship.total_al_rank,
            "ssg_tag": "[保险点未覆盖当前舰船]" \
                if storage_manager.get_value_of("保险点") < my_ship.total_al_rank \
                else ">>保险点已覆盖当前舰船<<",
            "ssg_num": storage_manager.get_value_of("保险点"),
            "q_information": my_ship.al_list[0].len_name \
                             + f"[{storage_manager.get_value_of(str(my_ship.al_list[0].index))}]" \
                if my_ship.al_list[0] \
                else "[No Info]",
            "w_information": my_ship.al_list[1].len_name \
                             + f"[{storage_manager.get_value_of(str(my_ship.al_list[1].index))}]" \
                if my_ship.al_list[1] \
                else "[No Info]",
            "e_information": my_ship.al_list[2].len_name \
                             + f"[{storage_manager.get_value_of(str(my_ship.al_list[2].index))}]" \
                if my_ship.al_list[2] \
                else "[No Info]"
        })
        self.all_tree_list["词条信息"].inject({
            "total_points": entry_manager.count_total_points()
        })
        self.all_tree_list["词条信息"].rewrite_lines(
            entry_manager.generate_entry_summary_lines()
        )
        self.all_tree_list["仓库信息"].inject({
            "material": storage_manager.total_materials_num,
            "al_num": storage_manager.total_als_num
        })

    def generate_all_line_list(self):
        all_line_list = [[] for _ in range(self.column)]
        for column_index in range(self.column):
            for tree in self.grid[column_index]:
                try:
                    all_line_list[column_index] += tree.generate_line_list()
                except AttributeError:
                    pass
        return all_line_list


station_trees_manager = StationTreesManager()

contract_manager = Contract_manager(storage_manager,list(al_manager.all_al_list.keys()))

class MainLoops:

    def __init__(self):
        self.days = 0
        self.entry_begin_day = 0
        self.entry_delta = 1

    @staticmethod
    def is_over() -> Literal[-1, 0, 1]:
        """
        判定是否有一方死亡
        :return: -1代表敌方胜利 0表示游戏继续 1表示我方胜利
        """
        if my_ship.shelter < 0:
            return -1
        if enemy.shelter < 0:
            return 1
        return 0

    @staticmethod
    def get_adjusting_shelter_and_missile() -> tuple[int,int]:
        """
        基于SBMM理念对敌方护盾和导弹进行增强
        :return: 一个元组，包含敌方护盾、导弹的修正值
        """
        total = al_manager.get_total_al_rank() // 3
        if total < 1:
            return 0,0
        shelter = random.randint(1,total)
        return shelter, total - shelter


    def initialize_before_fight(self):
        # 舰船初始化
        my_ship.initialize()
        shelter, missile = self.get_adjusting_shelter_and_missile()
        enemy.initialize(shelter,missile)
        # 骰子初始化
        dice.set_probability(0.8)
        dice.set_di(0.3)
        dice.set_additional_di(0)
        # 自动驾驶初始化
        auto_pilot.refresh()
        # 词条管理器初始化
        entry_manager.set_mode(Modes.FIGHT)
        entry_manager.clear_all_flow()
        # 确定词条烈度
        self.entry_begin_day = 20 - al_manager.get_total_al_rank()
        self.entry_delta = (40 - al_manager.get_total_al_rank()) // 4
        # 设置天数
        self.days = 1

    @staticmethod
    def get_force_advance() -> Literal[-1,0,1]:
        """
        判定是否强制使某一方行动
        :return: 1代表我方，-1代表敌方，0代表不强制
        """
        if al26.is_my_turn():
            return 1
        return 0

    def fight_mainloop(self):
        sounds_manager.switch_to_bgm("fight")
        while 1:
            # dawn
            if (rank := entry_manager.get_rank_of("11")) != 0:
                dice.set_additional_di(rank * 0.1)
            who = dice.decide_who(force_advance=self.get_force_advance())
            if self.days >= self.entry_begin_day \
            and (self.days-self.entry_begin_day) % self.entry_delta == 0:
                entry_manager.push_up()
            time.sleep(0.4)
            for al in my_ship.al_list:
                if al:
                    al.operate_in_morning()

            # morning
            field_printer.print_basic_info(self.days)
            entry_manager.print_all_flow_rank()
            field_printer.print_for_fight(my_ship, enemy)
            field_printer.generate_suggestion_tree().print_self()
            field_printer.print_key_prompt()

            # noon
            if who == 1:
                Txt.print_plus("今天由我方行动")
                my_ship.react()
            else:
                Txt.print_plus("今天由敌方行动")
                enemy.react()

            # afternoon
            for al in my_ship.al_list:
                if al:
                    al.operate_in_afternoon()
                    if who == 1:
                        al.operate_in_our_turn()

            # dusk
            if (result := self.is_over()) != 0:
                break
            self.days += 1
        sounds_manager.stop_bgm()
        if result == 1:
            Txt.print_plus("我方胜利")
            sounds_manager.switch_to_bgm("win")
            storage_manager.drop_for_fight()
            input_plus("[enter]回站")
            sounds_manager.stop_bgm()
            return
        Txt.print_plus("敌方胜利")
        if storage_manager.has_enough_ssd(my_ship.total_al_rank):
            storage_manager.cost_ssd(my_ship.total_al_rank)
            input_plus("[enter]回站")
            return
        storage_manager.destroy_al(my_ship.al_list)
        al_manager.clear_al()
        input_plus("[enter]回站")
        return

    def disaster_mainloop(self):
        sounds_manager.switch_to_bgm("fight")
        while 1:
            # dawn
            time.sleep(0.4)
            who = dice.decide_who(force_advance=self.get_force_advance())
            for al in my_ship.al_list:
                if al:
                    al.operate_in_morning()

            # morning
            field_printer.print_basic_info(self.days)
            #entry_manager.print_all_flow_rank() # TODO 写一个适当的函数展示选择的词条难度
            field_printer.print_for_fight(my_ship, enemy)
            field_printer.generate_suggestion_tree().print_self()
            field_printer.print_key_prompt()

            # noon
            if who == 1:
                Txt.print_plus("今天由我方行动")
                my_ship.react()
            else:
                Txt.print_plus("今天由敌方行动")
                enemy.react()

            # afternoon
            for al in my_ship.al_list:
                if al:
                    al.operate_in_afternoon()
                    if who == 1:
                        al.operate_in_our_turn()

            # dusk
            if entry_manager.get_rank_of("13") != 0 and self.days > 100 - 20 * entry_manager.get_rank_of("13"):
                enemy.attack(1)
                entry_manager.all_entries["13"].print_when_react()
            if entry_manager.get_rank_of("5") != 0 and my_ship.shelter <= 0:
                entry_manager.all_entries["5"].print_when_react()
                result = -1
                break
            if (result := self.is_over()) != 0:
                break
            self.days += 1
        sounds_manager.stop_bgm()
        if result == 1:
            Txt.print_plus("我方胜利")
            sounds_manager.switch_to_bgm("win")
            storage_manager.drop_for_fight()
            input_plus("[enter]回站")
            sounds_manager.stop_bgm()
            return
        Txt.print_plus("敌方胜利")
        if storage_manager.has_enough_ssd(my_ship.total_al_rank):
            storage_manager.cost_ssd(my_ship.total_al_rank)
            input_plus("[enter]回站")
            return
        storage_manager.destroy_al(my_ship.al_list)
        al_manager.clear_al()
        input_plus("[enter]回站")
        return

    def initialize_before_disaster(self):
        # 舰船初始化
        my_ship.initialize()
        shelter, missile = self.get_adjusting_shelter_and_missile()
        enemy.initialize(shelter,missile)
        # 骰子初始化
        dice.set_probability(0.8)
        dice.set_di(0.3)
        dice.set_additional_di(0)
        # 自动驾驶初始化
        auto_pilot.refresh()
        # 词条管理器初始化
        entry_manager.set_mode(Modes.DISASTER)
        entry_manager.clear_all_flow()
        # 词条触发
        if (rank := entry_manager.get_rank_of("7")) != 0:
            enemy.shelter += rank * 3
            entry_manager.all_entries["7"].print_when_react()
        if (rank := entry_manager.get_rank_of("11")) != 0:
            dice.set_additional_di(rank * 0.1)
            entry_manager.all_entries["11"].print_when_react()
        # 设置天数
        self.days = 1

    @staticmethod
    def station_mainloop():
        sounds_manager.switch_to_bgm("station")
        while 1:
            print()
            station_trees_manager.inject_all()
            Txt.n_column_print(station_trees_manager.generate_all_line_list(), 50)
            go_to = input(">>>")
            match go_to:
                case "z":
                    storage_manager.print_storage()
                case "x":
                    if storage_manager.have_all_al_on_ship(my_ship.al_list):
                        break
                    else:
                        Txt.print_plus("并非所有终焉结都有存货|你将不能离站")
                case "p3":
                    storage_manager.set_ship_name()
                case "p2":
                    al_manager.choose_al("all")
                case "q" | "w" | "e":
                    al_manager.choose_al(go_to)
                case "g1":
                    main_loops.contract_market_mainloop()
                case "a1" | "c":
                    main_loops.industry_mainloop()
                case "c1":
                    main_loops.entry_choosing_mainloop()
                case _:
                    pass
        sounds_manager.stop_bgm()

    @staticmethod
    def contract_market_mainloop():
        contract_manager.generate_all_contracts()
        while 1:
            contract_manager.print_all_contracts()
            print()
            Txt.dict_give_and_get_print(storage_manager.show_assets_except_al(), {}, {})
            inp = input("[数字] 选择合同|[r/refresh] 刷新市场|[e/exit] 退出>>>")
            if inp == "exit" or inp == "e":
                break
            elif inp == "refresh" or inp == "r":
                contract_manager.generate_all_contracts()
            elif inp.isdigit():
                try:
                    contract: Contract = contract_manager.all_contracts_list[int(inp)]
                    contract.print_self()
                    Txt.dict_give_and_get_print(
                        storage_manager.show_assets_except_al(),
                        contract.get_list,
                        contract.give_list
                    )
                    inp1 = input("check=签署并交易 [enter]=退出>>>")
                    if inp1 == "check":
                        contract.transaction()
                except IndexError:
                    print("合同不存在")

    @staticmethod
    def industry_mainloop():
        while 1:
            for al in al_manager.all_al_list.values():
                al.refresh_craftable_tag()
            assets = storage_manager.show_assets()
            for al in al_manager.all_al_list.values():
                al.print_recipe(assets)
            inp = Txt.input_plus("工业流程正常运转中·请输入要合成的装备代码·[enter]退出>>>")
            if inp == "": # 退出
                Txt.print_plus("正在退出……")
                break
            if inp not in al_manager.all_al_list: # 输入无效
                Txt.print_plus("请输入有效的装备编号")
                Txt.input_plus("")
                continue
            current_al = al_manager.all_al_list[inp]
            if not current_al.is_craftable: # 资源不足
                Txt.print_plus("仓库资源不足·合成失败")
                Txt.input_plus("")
                continue
            current_al.craft_self()
            Txt.print_plus(f"{current_al.len_name}*1 合成完成·已送至装备仓库并铭刻您的代号")
            Txt.input_plus("")

    @staticmethod
    def entry_choosing_mainloop():
        while 1:
            print()
            entry_manager.print_all_descriptions()
            entry_manager.print_chosen_as_tree()
            inp_index = Txt.input_plus("请输入要修改或加入的词条 [0]清空词条 [all]选择所有词条 [enter]退出>>>")
            print()
            match inp_index:
                case "0":
                    entry_manager.clear_all_selected()
                    Txt.print_plus("所有词条已被清空")
                    continue
                case "all":
                    entry_manager.push_all_full()
                    Txt.print_plus("所有词条已被推至最高难度·警告·高难")
                    continue
                case "":
                    break
                case _:
                    pass
            try:
                entry = entry_manager.all_entries[inp_index]
                entry.print_description()
                inp_rank = Txt.input_plus("请输入词条难度等级")
                print()
                entry.set_rank(int(inp_rank))
                if inp_rank == "0":
                    Txt.print_plus("词条已取消")
                else:
                    Txt.print_plus(f"[{entry.index}]{entry.title}{entry.RANK_STR_LIST[entry.selected_rank]} 已激活")
            except KeyError:
                Txt.print_plus("请输入有效的词条编号")
            except ValueError:
                Txt.print_plus("请输入有效的词条等级")
        storage_manager.save_entry_rank(entry_manager.get_all_rank())

    @staticmethod
    def ask_destination() -> str:
        des = Txt.ask_plus("请输入目的地|[0]基本对战|[1]战死之地",["0","1"])
        return des

main_loops = MainLoops()

def hello():
    sounds_manager.switch_to_bgm("login")
    Txt.print_plus(f"\n{__VERSION__} > 工程启动中 > \n")
    Txt.input_plus("按任意键开始游戏|输入后请回车>>>")

if __name__ == "__main__":
    hello()
    storage_manager.login()
    my_ship.load_al()
    entry_manager.set_all_rank(storage_manager.get_entry_rank())
    while 1:
        main_loops.station_mainloop()
        des = main_loops.ask_destination()
        match des:
            case "0":
                main_loops.initialize_before_fight()
                main_loops.fight_mainloop()
            case "1":
                main_loops.initialize_before_disaster()
                main_loops.disaster_mainloop()
            case _:
                pass