from __future__ import annotations

import random
import time
from typing import Literal

from core.Module0_enums_exceptions import DamageType, Modes, Side, ASI, IFAWL_ConnectionCancel, IFAWL_NoOcpError
from core import Module1_txt as Txt
from core.Module1_txt import input_plus, print_plus
from core.Module2_json_loader import json_loader
from modules.Module3_storage_manager import storage_manager
from modules.Module4_voices import voices
from core.Module5_dice import dice
from modules.Module6_market_manager import ContractManager, Contract, tools
from modules.Module7_auto_pilot import auto_pilot
from core.Module8_al_industry import recipe_for_all_al
from modules.Module9_entry_manager import entry_manager
from core.Module10_sound_manager import sounds_manager
from modules.Module11_damage_previewer import damage_previewer
from modules.Module12_infinity_card_manager import CardManager
from modules.Module13_plot_manager import plot_manager
from core.Module14_communication import Server, Client
from modules.Module15_ocp_manager import OcpManager

__VERSION__ = "IFAWL 1.3.0 'UNITED IN DEATH'"



# 枚举类已移至 core.Module0_enums 模块



class MyShip:

    def __init__(self):
        self.shelter = 0
        self.missile = 0
        self.al_list: list[Al_general | None] = [None, None, None]
        self.total_al_rank = 0
        self.platform = "导弹"
        self.life_for_ppve = 0

    def load_al(self):
        al_str_list = storage_manager.get_al_on_ship()
        for position in range(len(al_str_list)):
            self.al_list[position] = al_manager.all_al_list.get(al_str_list[position], None)
        self.update_total_al_rank()
        self.update_platform()

    def set_default_al(self):
        """
        将舰船的终焉结设置为免费。不存储到硬盘
        :return: 无
        """
        self.al_list = [al17, al18, al7]
        self.update_total_al_rank()
        self.update_platform()

    def update_total_al_rank(self):
        """
        更新舰船的总等级
        :return: 无
        """
        self.total_al_rank = 0
        for al in self.al_list:
            try:
                self.total_al_rank += al.rank_num
            except AttributeError:
                pass

    def update_platform(self):
        """
        更新舰船的平台
        :return: 无
        """
        if not self.al_list[0]:
            self.platform = "导弹"
            return
        self.platform = self.al_list[0].platform

    def print_self_shelter(self, blind=False):
        if blind:
            print("[No Info]")
            return
        for _ in range(self.shelter):
            print("-----")

    def generate_shelter_list(self, blind=False):
        if blind:
            return ["[No Info]"]
        return ["-----"]*self.shelter

    def print_self_missile(self, blind=False):
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

    def generate_missile_list(self, blind=False):
        if blind:
            return ["[No Info]"]
        ammunition_type = {
            "导弹": "[]",
            "粒子炮": "|| "
        }[self.platform]
        output_line = ""
        for _ in range(self.missile):
            output_line += ammunition_type
        return [output_line]

    def initialize(self):
        self.missile = 1
        self.shelter = 1

    def get_equivalent_shelter_from_als(self) -> int:
        """
        获取从终焉结带来的等效护盾
        :return: 终焉结带来的等效护盾
        """
        out = 0
        for al in self.al_list:
            try:
                out += al.get_equivalent_shelter()
            except AttributeError:
                pass
        return out

    def get_equivalent_shelter_of_ship(self) -> int:
        """
        计算全船等效护盾值
        :return: 全船等效护盾
        """
        return self.shelter + self.get_equivalent_shelter_from_als()

    def attack(self, atk: int, dmg_type: str) -> int:
        """
        根据原始伤害进行加减并对目标造成攻击
        :param atk: 原始伤害
        :param dmg_type: 伤害种类
        :return: 经过加成减弱后的atk
        """
        match dmg_type:
            case DamageType.MISSILE_LAUNCH:
                sounds_manager.play_sfx("missile_launch")
            case DamageType.PARTICLE_CANNON_SHOOTING:
                sounds_manager.play_sfx("particle_cannon_shooting")
            case _:
                pass
        for al in self.al_list:
            try:
                atk = al.add_atk(atk, dmg_type)
            except AttributeError:
                pass
        atk = entry_manager.check_and_reduce_atk(atk)
        atk = entry_manager.check_and_attack_me(atk, enemy)
        atk = ocp_manager.adjust_me_atk(atk)
        al33.check_if_move(atk)  ####
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
        hp = entry_manager.check_and_add_enemy_hp(hp, enemy)
        hp = ocp_manager.adjust_me_hp(hp)
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
        if num < 0:
            self.missile += num
            return
        for al in self.al_list:
            try:
                num = al.add_num(num)
            except AttributeError:
                pass
        num = ocp_manager.adjust_me_num(num)
        self.missile += num

    def ppve_react_extra(self,operation:str):
        if entry_manager.current_mode != Modes.PPVE or operation == "":
            return operation
        if operation[0] not in ["m","s","c"]:
            return operation
        match operation[0]:
            case "m":
                if len(operation) > 1 and operation[1].isdigit():
                    load = min(int(operation[1]),int(self.missile))
                    my_ship.load(load)
                    another_ship.load(load)
                    self.load(-load*2)
                    voices.report(self.platform,"弹药转移")
            case "s":
                    my_ship.heal(1)
                    another_ship.heal(1)
                    enemy.attack(2,self)
                    voices.report("护盾","相互治疗")
            case "c":
                if my_ship.life_for_ppve > 0:
                    enemy.attack(1-my_ship.shelter,self)
                    my_ship.shelter = 1
                if another_ship.life_for_ppve > 0:
                    enemy.attack(1-another_ship.shelter,self)
                    another_ship.shelter = 1
                voices.report("护盾","救你一命！")
        return "pass"

    def react(self):
        """
        进行回合中响应
        :return: 无
        """
        #自动驾驶
        field_info =  [self.shelter, self.missile, enemy.shelter, enemy.missile, 0]
        for al in self.al_list:
            if al is not None and type(al.state) == int:
                field_info.append(al.state)
            else:
                field_info.append(0)
        operation = auto_pilot.get_operation(field_info)

        operation = self.ppve_react_extra(operation)

        for al in self.al_list:
            try:
                operation = al.adjust_operation(operation)
            except AttributeError:
                pass
        if self.missile < 1 and operation == "1":
            operation = "0"
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
                result = self.attack(1, atk_type)
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
            case "f":
                try:
                    ocp_manager.operate_when_f(self)
                except IFAWL_NoOcpError:
                    Txt.print_plus("注意·当前没有活跃事件")
            case "pass":
                pass
            case _:
                Txt.print_plus("你跳过了这一天！")
                auto_pilot.refresh()

    def react_for_ppve(self,server=None):
        """
        进行回合中响应
        :return: 无
        """

        if not server:
            operation = input_plus("[对长机指挥官]请输入你的操作>>>")
        else:
            operation = server.ask("[对僚机指挥官]请输入你的操作>>>")

        operation = self.ppve_react_extra(operation)

        for al in self.al_list:
            try:
                operation = al.adjust_operation(operation)
            except AttributeError:
                pass
        if self.missile < 1 and operation == "1":
            operation = "0"
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
                result = self.attack(1, atk_type)
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
                auto_pilot.refresh()

my_ship = MyShip()

another_ship = MyShip()

class EnemyShip:
    def __init__(self):
        self.shelter = 0
        self.missile = 0
        self.target_ship = my_ship

    def print_self_missile(self, blind=False):
        if blind:
            print("[No Info]")
            return
        for _ in range(self.missile):
            print("[]", end="")

    def print_self_shelter(self, blind=False):
        if blind:
            print("[No Info]")
            return
        if al33.is_on_one_ship():
            al33.print_poisoned_shelter()
            return
        for _ in range(self.shelter):
            print("-----")

    def generate_self_missile(self, blind=False):
        if blind:
            return "[No Info]\n"
        result = ""
        for _ in range(self.missile):
            result += "[]"
        return result

    def generate_self_shelter(self, blind=False):
        if blind:
            return "[No Info]\n"
        result = ""
        for _ in range(self.shelter):
            result += "-----\n"
        return result

    def attack(self, atk: int,force_target:MyShip|None = None):
        """
        根据原始伤害进行加减并对目标造成攻击
        :param atk: 原始伤害
        :param force_target: 强制行动
        :return: 无
        """
        target_ship = self.target_ship
        if force_target:
            target_ship = force_target
        # 词条
        atk = entry_manager.check_and_add_atk(atk)
        atk = entry_manager.check_and_reduce_missile(atk, target_ship)
        # 事件
        atk = ocp_manager.adjust_enemy_atk(atk)
        # 终焉结
        reversed_al_list = target_ship.al_list.copy()
        reversed_al_list[1],reversed_al_list[2] = reversed_al_list[2], reversed_al_list[1]
        for al in reversed_al_list:
            try:
                atk = al.reduce_enemy_attack(atk)
            except AttributeError:
                pass
        target_ship.shelter -= atk
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
        hp = ocp_manager.adjust_enemy_hp(hp)
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
        num = ocp_manager.adjust_enemy_num(num)
        self.missile += num
        if num > 0:
            voices.report("战场播报", "敌上弹", False)

    def initialize(self, adj_shelter, adj_missile):
        self.missile = 2 + adj_missile
        self.shelter = 2 + adj_shelter
        self.target_ship = my_ship

    def ppve_react_extra(self):
        ##
        if entry_manager.current_mode == Modes.PPVE:
            target_ship_before = self.target_ship
            if main_loops.is_near_death(my_ship) and not main_loops.is_near_death(another_ship):
                self.target_ship = another_ship
            elif main_loops.is_near_death(another_ship) and not main_loops.is_near_death(my_ship):
                self.target_ship = my_ship
            else:
                self.target_ship = random.choice([my_ship,another_ship])
            if target_ship_before != self.target_ship:
                Txt.print_plus("敌方目标改变，注意警戒！")
                main_loops.server.send_str("敌方目标改变，注意警戒！")
        ##

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
        operation = al26.get_controlled_operation(operation)  # 眠雀控制
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

        self.ppve_react_extra()

enemy = EnemyShip()


class Al_manager:

    def __init__(self):
        self.al_meta_data: dict[str, dict[str, str | int]] = json_loader.load("al_meta_data")
        self.all_al_list: dict[str, Al_general] = {}
        self.al_max_rank_q = 0
        self.al_max_rank_w = 0
        self.al_max_rank_e = 0

    def choose_al(self, type_choosing: str | Literal["q", "w", "e", "all"]):
        if type_choosing == "all":
            self.choose_al("q")
            self.choose_al("w")
            self.choose_al("e")
            return
        #        for key,al in self.all_al_list.items():
        #            if al.type == type_choosing:
        #                al.print_description()
        # 打印Al的描述
        al_list = [al for al in self.all_al_list.values() if al.type == type_choosing]
        al_list.sort(key=lambda al: al.rank_num)
        for al in al_list:
            al.print_description()
        # Al的选择
        cn_type = {"q": "主武器", "w": "生存位", "e": "战术装备"}[type_choosing]
        al_position = {"q": 0, "w": 1, "e": 2}[type_choosing]
        while 1:
            inp = Txt.input_plus(
                f"\n指挥官，请输入数字选择本场战斗的{cn_type}|[-1] 不使用{cn_type}|[enter] 保留原有选择>>>")
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
                if not self.check_and_kick_e() or type_choosing == "q":
                    time.sleep(0.4)
                    break
        storage_manager.save_al_on_ship(my_ship.al_list)
        my_ship.update_platform()
        my_ship.update_total_al_rank()

    def choose_al_with_limit(self, type_choosing: str | Literal["q", "w", "e"], max_rank:int|None=None):
        """
        在空间站外进行终焉结转换，通常具有等级限制因素。不保存至硬盘
        :param type_choosing: 终焉结的type
        :param max_rank: 最大可选等级，默认取自身维护的self.al_max_rank_qwe变量
        :return: 无
        """
        if not max_rank:
            match type_choosing:
                case "q":
                    max_rank = self.al_max_rank_q
                case "w":
                    max_rank = self.al_max_rank_w
                case "e":
                    max_rank = self.al_max_rank_e
        al_list = [al for al in self.all_al_list.values() if al.type == type_choosing and al.rank_num <= max_rank]
        al_list.sort(key=lambda al: al.rank_num)
        for al in al_list:
            al.print_description(show_num_in_storage=False)
        # Al的选择
        cn_type = {"q": "主武器", "w": "生存位", "e": "战术装备"}[type_choosing]
        al_position = {"q": 0, "w": 1, "e": 2}[type_choosing]
        inp = Txt.ask_plus(f"请选择要换装的{cn_type}| [enter]保持现有装备",[al.index for al in al_list]+[""])
        if inp == "":
            return
        Txt.print_plus(f"{self.al_meta_data[inp]['short_name']}#{self.al_meta_data[inp]['index']} 已确认装备")
        my_ship.al_list[al_position] = self.all_al_list[inp]
        print()
        self.check_and_kick_e()
        my_ship.update_platform()
        my_ship.update_total_al_rank()

    def print_info_before_push_up(self,delta:int):
        trees = {}
        for al_type in ("q","w","e"):
            max_rank = 0
            match al_type:
                case "q":
                    max_rank = self.al_max_rank_q
                case "w":
                    max_rank = self.al_max_rank_w
                case "e":
                    max_rank = self.al_max_rank_e
#            print(f"[{type}] >>> 当前已有 >>> 最大等级{max_rank}级")
#            print()
            als_below = [
                f"{al.short_name}#{al.index}[{al.metadata['rank']}]" \
                for al in sorted(self.all_al_list.values(),key=lambda al:al.rank_num) \
                if al.rank_num <= max_rank and al.type == al_type
            ]
            als_delta = [
                f"{al.short_name}#{al.index}[{al.metadata['rank']}]" \
                for al in sorted(self.all_al_list.values(),key=lambda al:al.rank_num) \
                if max_rank < al.rank_num <= max_rank + delta and al.type == al_type
            ]
            als_future = [
                f"{al.short_name}#{al.index}[{al.metadata['rank']}]" \
                for al in sorted(self.all_al_list.values(),key=lambda al:al.rank_num) \
                if max_rank + delta < al.rank_num and al.type == al_type
            ]
            trees[al_type] = Txt.Tree(
                f"{al_type}系终焉结",
                ">>> 当前已有 >>>",
                als_below,
                ">>> 即将解锁 >>>",
                als_delta,
                ">>> 未来可解锁 >>>",
                als_future
            )
        Txt.n_column_print(
            [tree.generate_line_list() for tree in trees.values()],
            di_list=[30,30]
        )

    def push_up_limit(self,type_choosing: str | Literal["q", "w", "e"],delta:int):
        """
        将站外终焉结升级限制上推
        :param type_choosing: 终焉结类型
        :param delta: 上推等级
        :return: 无
        """
        match type_choosing:
            case "q":
                self.al_max_rank_q += delta
            case "w":
                self.al_max_rank_w += delta
            case "e":
                self.al_max_rank_e += delta

    @staticmethod
    def clear_al():
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
    def get_total_al_rank(ship:MyShip) -> int:
        """
        计算我方舰船上终焉结的总等级
        :return: 总等级
        """
        out = 0
        for al in ship.al_list:
            try:
                out += al.rank_num
            except AttributeError:
                pass
        return out

    @staticmethod
    def check_and_kick_e() -> bool:
        """
        检查主武器和战术区终焉结是否匹配，若不匹配则踢出e区终焉结
        :return: 是否踢出e区终焉结
        """
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

    def initialize_all_al(self):
        """
        调用所有终焉结的初始化函数
        :return: 无
        """
        for al in self.all_al_list.values():
            al.initialize()

al_manager = Al_manager()


class Al_general:
    # Apocalypse-Linked 终焉结

    def __init__(self, index: int):
        # metadata 字段
        self.index: str = str(index)
        self.short_name: str = al_manager.al_meta_data[self.index]["short_name"]
        self.len_name: str = al_manager.al_meta_data[self.index]["len_name"]
        self.type: str = al_manager.al_meta_data[self.index]["type"]
        self.rank_num: int = al_manager.al_meta_data[self.index]["rank_num"]
        self.skin_list: list[str] = al_manager.al_meta_data[self.index].get("skin_list", [])
        self.platform: str = al_manager.al_meta_data[self.index]["platform"]
        self.metadata: dict[str, str | int] = al_manager.al_meta_data[self.index]
        self.ship:MyShip = my_ship

        # industry字段
        self.recipe = recipe_for_all_al[self.index]
        self.recipe["联邦信用点"] = 1100 * self.rank_num
        self.is_craftable = False

        # 签名
        al_manager.all_al_list[self.index] = self

        # operation 字段
        self.state = [None,0,0,0,0]

    def report(self, theme: str):
        """
        Al所包装的说话函数，省去了说话者名字
        :param theme: 主题
        :return: 无
        """
        if entry_manager.current_mode == Modes.PPVE:
            voices.report(self.short_name, theme)
            return
        voices.report(self.short_name, theme)

    def inject_and_report(self, theme: str, data_injected: dict[str, str | int]):
        """
        Al所包装的注入数据说话函数，省去了说话者名字
        :param theme: 主题
        :param data_injected: 需注入的键值对
        :return: 无
        """
        voices.inject_and_report(self.short_name, theme, data_injected)

    def print_description(self,show_num_in_storage=True):
        """
        打印Al的描述，用于装备选择界面
        :return: 无
        """
        tag0: str = self.metadata["origin"]
        tag1: str = self.platform
        num_in_storage = f"{storage_manager.get_value_of(str(self.index))}在仓库"\
            if show_num_in_storage else ""

        print(
            Txt.adjust(f"[{self.index}] {tag0}{self.len_name}", 60),
            Txt.adjust(f"[{tag1}平台] [{self.metadata['rank']}]", 20),
            num_in_storage
        )
        print(f">>>>\"{self.metadata['short_name_en']}\"")
        print(self.metadata["description_txt"])
        # [30] 岩河军工“湾区铃兰”饱和式蜂巢突击粒子炮      [粒子炮平台] [VIII] 1在仓库 >>[可以离站使用]<<
        print()

    def is_on_one_ship(self) -> bool:
        """
        判断自己是否在任意一艘我方舰船上
        :return: 是否在任意一艘我方舰船上
        """
        return self in self.ship.al_list

    def add_atk(self, atk: int, dmg_type: str):
        """
        为atk提供加成
        :param atk: 加成前atk
        :param dmg_type: 伤害种类，各Al决定是否加成
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
        self.state = [None, 0, 0, 0, 0]

    def react(self):
        pass

    def get_equivalent_shelter(self):
        return 0

    def print_self(self):
        pass

    def generate_line_list(self) -> list[str]:
        print_list = []
        return print_list

    def print_self_behind_shelter(self,return_list = False):
        print_list = []
        if self.type == "none":
            if return_list:
                print_list = self.generate_line_list()
            else:
                self.print_self()
        return print_list

    def print_self_before_shelter(self,return_list = False) -> list[str]:
        print_list = []
        if self.type == "w":
            if return_list:
                print_list = self.generate_line_list()
            else:
                self.print_self()
        return print_list

    def print_self_behind_missile(self,return_list = False) -> list[str]:
        print_list = []
        if self.type in ["q","e"]:
            if return_list:
                print_list = self.generate_line_list()
            else:
                self.print_self()
        return print_list

    def suggest(self) -> str | None:
        return None

    def operate_in_our_turn(self):
        pass

    def adjust_operation(self, raw: str) -> str:
        return raw

    def refresh_craftable_tag(self):
        """
        刷新自己能否被合成
        :return: 无
        """
        self.is_craftable = tools.is_affordable(self.recipe, storage_manager.show_assets())

    def print_recipe(self, assets: dict[str, int]):
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
        line1 += Txt.adjust(str1, 45)
        # 可合成性
        if self.is_craftable:
            craftable_tag = "[可合成●]"
        else:
            craftable_tag = "[不可合成]"
        line1 += Txt.adjust(craftable_tag, 12)
        # 本终焉结存货
        line1 += f"现有 {assets[str(self.index)]} 在仓库"
        print(line1)
        # 物品存货
        line2 = ""
        for item, require in self.recipe.items():
            inventory = assets[item]
            note = "[▲]" if require > inventory else ""
            str0 = f"|-{item}x{require}/{inventory}{note}"
            line2 += Txt.adjust(str0, 22)
        print(line2)
        print()

    def craft_self(self):
        """
        制造自己
        :return: 无
        """
        storage_manager.transaction(self.recipe, {str(self.index): 1})


class Al3(Al_general):  # 风行者

    def react(self):
        if dice.probability(0.3 * enemy.shelter):
            self.ship.attack(1, DamageType.ORDINARY_ATTACK)
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


class Al4(Al_general):  # 咆哮

    def react(self):
#        if self.state < 2:
#            self.state += 2
#            self.report("收到")
#            if self.state == 2:
#                self.report("准备好")
        if self.state[ASI.WORKING] > 0:
            return
        if self.state[ASI.BUILDING] == 0:
            self.state[ASI.BUILDING] = 2
            self.report("准备好")

    def operate_in_afternoon(self):
#        if self.state >= 2:
#            self.state += 1
#            if self.state == 4:
#                self.state = 0
#            if dice.probability(0.7):
#                self.ship.attack(1, "missile_launch")
#                self.report("命中")
#            else:
#                self.report("未命中")
#                self.ship.load(1)
#                self.report("回流")
        if self.state[ASI.BUILDING] == 2:
            self.state[ASI.BUILDING] = 0
            self.state[ASI.WORKING] = 2

        if self.state[ASI.WORKING] > 0:
            self.state[ASI.WORKING] -= 1
            if dice.probability(0.7):
                self.ship.attack(1, "missile_launch")
                self.report("命中")
            else:
                self.report("未命中")
                self.ship.load(1)
                self.report("回流")

    def suggest(self) -> str | None:
        if self.state[ASI.BUILDING] == 0 and self.state[ASI.WORKING] == 0:
            return "[q]部署发射台"
        elif self.state[ASI.WORKING] > 0:
            return "[自动攻击中]回流系统正在生效"
        else:
            return None


al4 = Al4(4)


class Al5(Al_general):  # 水银

    def react(self):
        if self.state[ASI.BUILDING] == 0:
            self.state[ASI.BUILDING] += 1
            self.report("收到")
        elif self.state[ASI.BUILDING] == 1:
            self.state[ASI.BUILDING] += 1
            self.report("准备好")
        else:
            self.state[ASI.BUILDING] = 0
            if random.randint(0, 9) > -1:
                self.ship.attack(2, DamageType.MISSILE_LAUNCH)
                self.report("命中")
            else:
                self.report("未命中")

    def add_num(self, num) -> int:
        if self.state[ASI.BUILDING] == 2 and dice.probability(0.5):
            self.report("协助上弹")
            return num + 1
        else:
            return num

    def suggest(self):
        return \
            ["[q]建立汞弹推进器 1/2",
             "[q]加注液态汞 2/2",
             "[q]发射汞弹|[0/space]上弹效率加成中"][self.state[ASI.BUILDING]]


al5 = Al5(5)


class Al6(Al_general):  # 白金
    def react(self):
        if self.state[ASI.BUILDING] == 0:
            if self.ship.shelter > 0:
                self.state[ASI.BUILDING] = 1
                self.report("收到")
            else:
                self.state[ASI.BUILDING] = 2
                self.report("生之帝国")
        elif self.state[ASI.BUILDING] == 1:
            self.state[ASI.BUILDING] = 2
            self.report("准备好")

    def operate_in_afternoon(self):
        if self.state[ASI.BUILDING] == 2 and self.ship.shelter <= 0:
            self.state[ASI.BUILDING] = 0
            self.ship.heal(2)
            self.report("急救")

    def suggest(self):
        return ["[w]建立安全屋1/2", "[w]派遣维修小队2/2", "[保护中]急救已就绪"][self.state[ASI.BUILDING]]


al6 = Al6(6)


class Al7(Al_general):  # 奶油
    def react(self):
        if enemy.missile <= 0:
            return
        if dice.probability(0.7):
            self.report("骇入成功")
            enemy.missile -= 1
            if dice.probability(0.6):
                self.ship.attack(1, DamageType.ENEMY_MISSILE_BOOM)
                self.report("引爆成功")
            else:
                self.report("引爆失败")
        else:
            self.report("骇入失败")

    def suggest(self):
        if enemy.missile == 0:
            return "[休息中]对面没有导弹"
        else:
            return "[e]入侵敌方导弹让他们倒大霉"


al7 = Al7(7)


class Al8(Al_general):  # 维多利亚

    def react(self):
#        if self.state < 2:
#            self.state += 1
#            self.report("收到")
#            if self.state == 2:
#                self.state = 3
#                self.report("准备好")
#        elif self.state == 2:
#            self.state = 3
#            self.report("续杯")
        if self.state[ASI.WORKING] == 1:
            self.state[ASI.WORKING] += 1
            self.report("续杯")
            return
        if self.state[ASI.WORKING] == 2:
            return
        self.state[ASI.BUILDING] += 1
        self.report("收到")
        if self.state[ASI.BUILDING] >= 2:
            self.state[ASI.BUILDING] = 0
            self.state[ASI.WORKING] = 2
            self.report("准备好")

    def add_atk(self, atk, dmg_type):
        if dmg_type != DamageType.MISSILE_LAUNCH:
            return atk
        if self.state[ASI.WORKING] == 0:
            return atk
        if dice.probability(0.8):
            atk += 1
            self.report("成功")
        else:
            self.report("失败")
        self.state[ASI.WORKING] -= 1
        return atk

    def suggest(self):
        if self.state[ASI.WORKING] == 2:
            return "[已建立]导弹伤害加成中"
        elif self.state[ASI.WORKING] == 1:
            return "[q]续杯|导弹伤害加成中"
        elif self.state[ASI.BUILDING] == 0:
            return "[q]建造发射架基础 1/2"
        elif self.state[ASI.BUILDING] == 1:
            return "[q]建成发射架炮管 2/2"


al8 = Al8(8)


class Al9(Al_general):  # 修械师

    def react(self):
        if self.state[ASI.BUILDING] == 0:
            if self.ship.shelter <= 1:
                self.ship.heal(1)
                self.report("护盾学急救")
            self.state[ASI.BUILDING] += 1
            self.report("收到")

    def add_hp(self, hp):
        if self.state[ASI.BUILDING] == 1:
            hp += 2
            self.state[ASI.BUILDING] = 0
            self.report("急救")
        return hp

    def suggest(self):
        if self.state[ASI.BUILDING] == 0:
            if self.ship.shelter <= 1:
                return "[w]建立吊舱|护盾学急救就绪"
            else:
                return "[w]建立吊舱"
        else:
            return "[已就绪]|[2]释放护盾"


al9 = Al9(9)


class Al10(Al_general):  # 离人

    def react(self):
        if self.ship.shelter >= 2:
            self.ship.shelter -= 1
            self.ship.load(2)
            self.report("牺牲护盾")
        elif self.ship.shelter <= 1:
            if self.ship.missile != 0:
                self.ship.heal(2)
                self.ship.load(-1)
                self.report("拆解导弹")
            else:
                self.ship.heal(1)
                self.report("护盾不足")

    def suggest(self):
        if self.ship.shelter >= 2:
            return "[e]拆除护盾|获取2枚导弹"
        elif self.ship.shelter <= 1:
            if self.ship.missile != 0:
                return "[e]拆除导弹|获取2层护盾"
            else:
                return "[资源耗竭]|[2]回充护盾|[0]回充导弹"


al10 = Al10(10)


class Al11(Al_general):  # 柒

    def react(self):
        if self.state[ASI.WORKING] == 0:
            self.state[ASI.WORKING] += 2
            self.ship.heal(1)
            self.report("收到")
            self.report("归来")
        elif self.state[ASI.WORKING] == 2:
            self.state[ASI.WORKING] -= 1
            self.ship.attack(1, DamageType.ORDINARY_ATTACK)
            self.ship.heal(1)
            self.report("为了身后的苍生")

    def reduce_enemy_heal(self, hp):
        if self.state[ASI.WORKING] == 0:
            return hp
        self.state[ASI.WORKING] -= 1
        self.ship.heal(1)
        self.report("汲取成功")
        hp -= 1
        return hp

    def suggest(self):
        return ["[w]建立汲能器", "[剩余一次]敌方护盾锁定中", "[就绪]敌方护盾锁定中|[w]主动汲取敌方护盾"][self.state[ASI.WORKING]]


al11 = Al11(11)


class Al12(Al_general):  # 晴空

    def __init__(self, index):
        super().__init__(index)
        self.atk_list: list[int] = [0, 0, 1, 2, 4, 5, 7, 8]

    def adjust_operation(self, raw: str) -> str:
        if self.state[ASI.BUILDING] != 0 and raw != "q" and not (al16.is_on_one_ship() and raw in ["w", "2"]):
            self.attack()
        return raw

    def react(self):
        if self.state[ASI.BUILDING] < 7:
            self.state[ASI.BUILDING] += 1
            self.report("充能中")
        else:
            self.ship.attack(self.atk_list[self.state[ASI.BUILDING]], DamageType.PARTICLE_CANNON_SHOOTING)
            # p_c_manager.boom_now()
            self.state[ASI.BUILDING] = 0
            self.report("过热")

    def attack(self):
        if self.atk_list[self.state[ASI.BUILDING]] != 0:
            self.ship.attack(self.atk_list[self.state[ASI.BUILDING]], DamageType.PARTICLE_CANNON_SHOOTING)
            # p_c_manager.boom_now()
            self.state[ASI.BUILDING] = 0
            self.report("攻击")
        elif self.atk_list[self.state[ASI.BUILDING]] == 0:
            self.state[ASI.BUILDING] = 0
            self.report("十四行赞美诗与一首绝望的歌")
            self.ship.heal(1)

    def print_self(self):
        if self.state[ASI.BUILDING] != 0:
            print(self.skin_list[self.state[ASI.BUILDING] // 3], end="")
            print(f"[晴空]粒子炮集群伤害水准：{self.atk_list[self.state[ASI.BUILDING]]}")
            print()

    def generate_line_list(self):
        print_list = []
        if self.state[ASI.BUILDING] != 0:
            print_list.append(self.skin_list[self.state[ASI.BUILDING] // 3] + f"[晴空]粒子炮集群伤害水准：{self.atk_list[self.state[ASI.BUILDING]]}")
            print_list.append("")
        return print_list


    def suggest(self):
        if self.state[ASI.BUILDING] == 0:
            return "[q]开始充能"
        elif self.state[ASI.BUILDING] == 7:
            return f"[q/任意键]最高功率开火|{self.atk_list[self.state[ASI.BUILDING]]}伤害"
        elif self.atk_list[self.state[ASI.BUILDING]] == 0:
            return "[q]继续充能|[任意键]放弃开火并触发回盾|0伤害"
        else:
            return f"[q]继续充能|[任意键]粒子炮开火|{self.atk_list[self.state[ASI.BUILDING]]}伤害"


al12 = Al12(12)


class Al13(Al_general):  # 北极

    def react(self):
        if self.ship.missile == 0:
            self.ship.missile += 1
            self.report("导弹不足")
        elif self.ship.missile == 1:
            self.ship.missile -= 1
            self.ship.attack(1, DamageType.MISSILE_LAUNCH)
            self.report("单导弹导航")
        else:
            self.ship.missile -= 2
            self.ship.attack(2, DamageType.MISSILE_LAUNCH)
            self.report("全功率导航")

    def suggest(self):
        if self.ship.missile == 0:
            return "[无导弹]不能使用北极|[0]装弹"
        elif self.ship.missile == 1:
            return "[e]导航单颗导弹|[0]装弹"
        else:
            return "[e]全功率导航"


al13 = Al13(13)


class Al14(Al_general):  # 信风

    def react(self):
        if self.ship.shelter > 0:
            self.report("强化成功")
            self.state[ASI.LOGGING] += 3
            self.ship.shelter -= 1
        else:
            self.ship.heal(1)
            self.report("护盾不足")
        if dice.probability(0.2) and self.ship.shelter > 0:
            self.react()

    def reduce_enemy_attack(self, atk):
        minor = min(self.state[ASI.LOGGING], atk)
        if minor == self.state[ASI.LOGGING]:
            self.report("信风清空")
        self.state[ASI.LOGGING] -= minor
        atk -= minor
        return atk

    def get_equivalent_shelter(self):
        return self.state[ASI.LOGGING]

    def print_self(self):
        print(self.skin_list[self.state[ASI.LOGGING] % 3], end="")
        print("\n//\\\\//" * (self.state[ASI.LOGGING] // 3))

    def generate_line_list(self):
        print_list = [self.skin_list[self.state[ASI.LOGGING] % 3]]
        print_list += ["//\\\\//"] * (self.state[ASI.LOGGING] // 3)
        return print_list

    def suggest(self):

        if self.ship.shelter == 0:
            return "[护盾不足]不能使用信风|[2]回充护盾"
        else:
            return "[w]强化护盾"


al14 = Al14(14)


class Al15(Al_general):  # 暴雨

    def react(self):
        if self.state[ASI.LOGGING] == 0:
            self.state[ASI.LOGGING] = 2
            self.report("上线")
            self.ship.missile += 1
        else:
            self.state[ASI.LOGGING] = 0
            self.report("下线")

    def add_num(self, num) -> int:
        if self.state[ASI.LOGGING] > 0:
            self.report("弹雨滂沱")
            return num + 1
        else:
            return num

    def adjust_operation(self, raw: str) -> str:
        if self.state[ASI.LOGGING] != 0 and raw == "1":
            voices.report("暴雨", "常规发射器离线")
            return "0"
        return raw

    def operate_in_afternoon(self):
        if self.state[ASI.LOGGING] > 0:
            if self.state[ASI.LOGGING] == 1:
                if self.ship.missile > 0:
                    self.ship.missile -= 1
                    self.ship.attack(1, DamageType.MISSILE_LAUNCH)
                    self.state[ASI.LOGGING] = 2
                    self.report("攻击")
                else:
                    self.state[ASI.LOGGING] = 0
                    self.report("下线")
            else:
                self.state[ASI.LOGGING] -= 1

    def suggest(self):
        return ["[q]发射台开机|激活预备导弹", "[自动攻击中]当日发射|[q]发射台关机|[0]辅助上弹",
                "[自动攻击中]次日发射|[q]发射台关机"][self.state[ASI.LOGGING]]


al15 = Al15(15)


class Al16(Al_general):  # 情诗
    cure_list = [0, 3, 6, 8, 10]

    def adjust_operation(self, raw: str) -> str:
        if self.state[ASI.BUILDING] != 0 and raw == "2":
            self.heal()
        return raw

    def react(self):
        if self.state[ASI.BUILDING] < 4:
            self.state[ASI.BUILDING] += 1
            self.report("收到")
        else:
            self.ship.heal(self.cure_list[4] - 1)
            self.report("超载")
            self.state[ASI.BUILDING] = 0

    def heal(self):
        if self.state[ASI.BUILDING] != 0:  # 情诗
            self.ship.heal(self.cure_list[self.state[ASI.BUILDING]] - 1)
            self.report("释放")
            self.state[ASI.BUILDING] = 0

    def print_self(self):
        if self.state[ASI.BUILDING] != 0:
            print(self.skin_list[self.state[ASI.BUILDING] // 2], end="")
            print(f"[情诗]大规模护盾存量：{self.cure_list[self.state[ASI.BUILDING]]}")

    def generate_line_list(self):
        print_list = []
        if self.state != 0:
            print_list.append(self.skin_list[self.state[ASI.BUILDING] // 2] + f"[情诗]大规模护盾存量：{self.cure_list[self.state[ASI.BUILDING]]}")
        return print_list

    def suggest(self):
        if self.state[ASI.BUILDING] == 0:
            return "[w]开始充能"
        elif self.state[ASI.BUILDING] == 4:
            return f"[w/2]极限存量护盾|{self.cure_list[self.state[ASI.BUILDING]]}层"
        else:
            return f"[w]继续充能|[2]释放大规模护盾|{self.cure_list[self.state[ASI.BUILDING]]}层"


al16 = Al16(16)


class Al17(Al_general):  # 白夜

    def react(self):
        if self.ship.missile == 0:
            self.ship.missile += 1
            self.report("无导弹")
        elif self.ship.shelter <= 0:
            self.ship.heal(1)
            self.report("护盾不足")
        else:
            enemy.attack(1,self.ship)
            self.ship.attack(2, DamageType.MISSILE_LAUNCH)
            self.ship.missile -= 1
            self.report("攻击成功")

    def suggest(self):
        if self.ship.missile == 0:
            return "[资源耗竭][0]装填弹药"
        elif self.ship.shelter <= 0:
            return "[资源耗竭][2/w]回复护盾"
        else:
            return "[q]发射白夜装甲弹"


al17 = Al17(17)


class Al18(Al_general):  # 初夏

    def adjust_operation(self, raw: str) -> str:
        if self.is_on_one_ship() and raw == "2":
            return "w"
        return raw

    def react(self):
        if dice.probability(0.6) or self.state[ASI.LOGGING] == 1:
            self.ship.heal(2)
            self.state[ASI.LOGGING] = 0
            self.report("成功")
        else:
            self.ship.heal(1)
            self.state[ASI.LOGGING] = 1
            self.report("失败")

    def suggest(self):
        if self.state[ASI.LOGGING] == 0:
            return "[2/w]回充护盾|概率回充2层"
        else:
            return "[2/w]回充护盾|回充2层"


al18 = Al18(18)


class Al19(Al_general):  # 苍穹

    def react(self):
        if self.state[ASI.WORKING] == 0:
            self.state[ASI.WORKING] = 3
            self.report("收到")
            self.report("准备好")

    def operate_in_afternoon(self):
        if self.state[ASI.WORKING] > 0:
            self.state[ASI.WORKING] -= 1
            if dice.probability(0.5):
                self.ship.heal(1)
                self.report("补给护盾")
            else:
                self.ship.load(1)
                self.report("补给弹药")
            if dice.probability(0.5):
                al3.react()

    def suggest(self):
        return ["[e]呼叫浅草寺战术补给", "[补给中]剩余一次", "[补给中]剩余两次", "[补给中]剩余三次"][self.state[ASI.WORKING]]


al19 = Al19(19)


class Al20(Al_general):  # 长安
    def react(self):
        if self.state[ASI.COOLING] == 0:
            dice.probability_current += 0.6
            self.state[ASI.COOLING] = -5
            self.report("扫描")
        else:
            self.report("冷却中")

    def operate_in_morning(self):
        if self.state[ASI.COOLING] < 0:
            self.state[ASI.COOLING] += 1

    def suggest(self):
        if self.state[ASI.COOLING] == 0:
            return f"[e]压制敌方行动|次日仍为我方航行日的概率：{dice.probability_current:.1f}"
        else:
            return f"[冷却中]剩余{-self.state[ASI.COOLING]}天|次日仍为我方航行日的概率：{dice.probability_current:.1f}"


al20 = Al20(20)


class Al21(Al_general):  # 诗岸

    def heal(self):
        if self.state[ASI.LOGGING] > 2 and dice.probability(0.5):
            al21.react()
        else:
            al21.state[ASI.LOGGING] += 1
            self.report("充注")

    def adjust_operation(self, raw: str) -> str:
        if self.is_on_one_ship() and raw == "2":
            self.heal()
            return "pass"
        return raw

    def react(self):
        if self.state[ASI.LOGGING] > 0:
            self.ship.heal(int(self.state[ASI.LOGGING] * 1.5))
            self.state[ASI.LOGGING] = 0
            self.report("主动凝固")
        else:
            self.state[ASI.LOGGING] += 1
            self.report("无屏障")
            self.report("充注")

    def operate_in_afternoon(self):
        if self.ship.get_equivalent_shelter_of_ship() <= 0:
            if self.state[ASI.LOGGING] > 0:
                self.state[ASI.LOGGING] -= 1
                self.ship.shelter = 1
                self.report("急救")

    def print_self_behind_shelter(self,return_list = False):
        print_list = []
        if self.is_on_one_ship():
            if return_list:
                if self.state[ASI.LOGGING] <= 6:
                    print_list += ["/-/-/-/"]*self.state[ASI.LOGGING]
                else:
                    print_list.append(f"/-/-/-/ x{self.state[ASI.LOGGING]}")
            else:
                if self.state[ASI.LOGGING] <= 6:
                    print("/-/-/-/\n" * self.state[ASI.LOGGING])
                else:
                    print(f"/-/-/-/ x{self.state[ASI.LOGGING]}")
        return print_list

    def suggest(self):
        if self.state[ASI.LOGGING] >= 3:
            return "[w]主动凝固|[2]充注液态护盾|请注意意外凝固风险"
        elif self.state[ASI.LOGGING] > 0:
            return "[w]主动凝固|[2]充注液态护盾|急救保护中"
        else:
            return "[2]充注液态护盾"


al21 = Al21(21)


class Al22(Al_general):  # 迫害妄想
    def react(self):
        if self.state[ASI.COOLING] == 0:
            self.ship.attack(1, DamageType.ORDINARY_ATTACK)
            self.state[ASI.COOLING] = -3
            self.report("攻击")
        else:
            self.report("冷却中")

    def operate_in_afternoon(self):
        if self.state[ASI.COOLING] == -3 and enemy.shelter <= 0:
            self.ship.attack(1, DamageType.ORDINARY_ATTACK)
            self.report("处决")
        if self.state[ASI.COOLING] == -1:
            self.report("就绪")

        if self.state[ASI.COOLING] < 0:
            self.state[ASI.COOLING] += 1

    def suggest(self):
        if self.state[ASI.COOLING] == 0:
            if enemy.shelter <= 1:
                return "[e]处决敌方"
            else:
                return "[e]造成1伤害"
        else:
            return f"[冷却中]剩余{-self.state[ASI.COOLING]}天"


al22 = Al22(22)


class Al23(Al_general):  # 浮生

    def react(self):
        for i in range(3):
            if self.ship.missile > 0:
                self.ship.load(-1)
                self.ship.attack(1, DamageType.MISSILE_LAUNCH)
                self.report("攻击成功")
            else:
                self.ship.load(1)
                self.report("导弹耗尽")
                break

    def suggest(self):
        if self.ship.missile >= 3:
            return "[q]浮游炮全功率开火"
        else:
            return ["[无导弹]不能使用浮生|[0]上弹", "[q]浮游炮开火|导弹不足 1/3|[0]上弹",
                    "[q]浮游炮开火|导弹不足 2/3|[0]上弹"][self.ship.missile]


al23 = Al23(23)


class Al24(Al_general):  # 大奶油

    @staticmethod
    def find_the_quotient_rounded_up(a, b):  #向上取整
        if a % b != 0:
            return (a // b) + 1
        else:
            return a // b

    def react(self):
        if self.state[ASI.WORKING] == 0:
            enemy.missile += 5
            self.state[ASI.WORKING] = 5
            while self.state[ASI.WORKING]:
                enemy.missile -= 1
                self.ship.attack(1, DamageType.ENEMY_MISSILE_BOOM)
                self.report("攻击成功")  #
                self.state[ASI.WORKING] -= 1
                if dice.probability(0.4 * (4 - self.state[ASI.WORKING])):
                    break
            if self.state[ASI.WORKING] < 0:
                self.state[ASI.WORKING] = 0
        elif self.state[ASI.WORKING] != 0:
            self.report("主动入侵")  #
            al7.react()
            self.state[ASI.WORKING] -= 1

    def reduce_enemy_attack(self, atk):
        if self.state[ASI.WORKING] == 0:
            return atk
        if dice.probability(1):
            self.state[ASI.WORKING] -= self.find_the_quotient_rounded_up(atk, 2)
            atk = 0
            self.ship.missile += 1
            self.report("拦截成功")
            if self.state[ASI.WORKING] < 0:
                self.state[ASI.WORKING] = 0
        return atk

    #    def print_self(self):##祖师爷
    #        if self.is_on_ones_ship():
    #            print("奶油的工作流")
    #            if self.state>0:
    #                print(f"|当前-解析保护中|可入侵敌方导弹[q]|『密钥』：{self.state}")
    #            else:
    #                print("|当前-空闲|电子进攻就绪[q]")

    def suggest(self):
        if self.state[ASI.WORKING] > 0:
            return f"[q]入侵敌方导弹|解析保护中|『密钥』：{self.state[ASI.WORKING]}"
        else:
            return "[q]电子爆破进攻|获得秘钥"


al24 = Al24(24)


class Al25(Al_general):  # 阿贾克斯
    def react(self):
        if self.state[ASI.WORKING] == 0 and self.state[ASI.COOLING] == 0:
            self.state[ASI.WORKING] = 3
            self.report("启动报告")

    def reduce_enemy_attack(self, atk):
        if atk == 0:
            return atk
        if self.state[ASI.WORKING] > 0:
            self.report("拦截")
            self.state[ASI.WORKING] -= 1
            if dice.probability(0.3):
                self.ship.attack(1, DamageType.ORDINARY_ATTACK)  #
                self.report("反击")
            if self.state[ASI.WORKING] == 0:
                self.state[ASI.COOLING] = -5
                self.report("冷却")
            return 0
        else:
            return atk

    def operate_in_afternoon(self):
        if self.state[ASI.COOLING] < 0:
            self.state[ASI.COOLING] += 1

    def print_self(self):
        if self.state[ASI.COOLING] < 0:
            print(self.skin_list[4])
        elif self.is_on_one_ship():
            print(self.skin_list[self.state[ASI.WORKING]])

    def suggest(self):
        if self.state[ASI.COOLING] < 0:
            return f"[冷却中]剩余{-self.state[ASI.COOLING]}天"
        elif self.state[ASI.WORKING] == 0:
            return f"[w]启动贾氏无人机群"
        else:
            return f"[防御进行中]剩余{self.state[ASI.WORKING]}次"


al25 = Al25(25)


class Al26(Al_general):  # 眠雀

    def react(self):
        if self.state[ASI.WORKING] == 0 and self.state[ASI.COOLING] == 0:
            self.state[ASI.WORKING] = 3
            self.report("启动报告")

    def operate_in_afternoon(self):
        if self.state[ASI.COOLING] < 0:
            self.state[ASI.COOLING] += 1

    def is_my_turn(self):
        if self.state[ASI.WORKING] == 3:
            self.state[ASI.WORKING] -= 1
            return 1
        return 0

    def get_controlled_operation(self, operation: str) -> str:
        if not self.is_on_one_ship() or self.state[ASI.COOLING] < 0 or self.state[ASI.WORKING] == 0:
            return operation
        if entry_manager.current_mode == Modes.PPVE:
            enemy.target_ship = self.ship
        self.report("控制成功")

        if self.ship == another_ship:
            Txt.print_plus("正在等待僚机指挥官操作<<<")
            controlled_operation = main_loops.server.ask_plus("[眠雀]选择敌方操作", ["0", "1", "2"])
        else:
            if entry_manager.current_mode == Modes.PPVE:
                main_loops.server.send_str("正在等待长机指挥官操作<<<")
            controlled_operation = Txt.ask_plus("[眠雀]选择敌方操作", ["0", "1", "2"])

        self.state[ASI.WORKING] -= 1
        if operation == controlled_operation:
            self.report("谐振成功")
            self.ship.attack(1, DamageType.ORDINARY_ATTACK)
            self.state[ASI.WORKING] += 1
        if self.state[ASI.WORKING] == 0:
            self.state[ASI.COOLING] = -5
        return controlled_operation

    def suggest(self):
        if self.state[ASI.COOLING] == 0 and self.state[ASI.WORKING] == 0:
            return "[e]控制敌方两次行动"
        elif self.state[ASI.COOLING] < 0:
            return f"[冷却中]剩余{-self.state[ASI.COOLING]}天"
        elif self.state[ASI.WORKING] > 0 and dice.current_who == Side.PLAYER:
            return f"[生效中]剩余{self.state[ASI.WORKING]}次"
        else:
            return "[支配中]输入敌方指令[0]装弹|[1]发射|[2]上盾"


al26 = Al26(26)


class Al27(Al_general):  # 瞳猫

    def react(self):
        if self.state[ASI.BUILDING] < 9:
            self.state[ASI.BUILDING] += 1
            self.report("充能")

    def operate_in_morning(self):
        if self.is_on_one_ship() and dice.current_who == Side.PLAYER and self.state[ASI.BUILDING] < 9:
            self.state[ASI.BUILDING] += 1

    def add_atk(self, atk, dmg_type):
        """
        瞳猫只是一只小猫，他不会对你的攻击造成加成
        只是我需要写在这里方便在atk时调用罢了
        """
        if self.is_on_one_ship() and self.state[ASI.BUILDING] > 0:
            self.state[ASI.BUILDING] = 0
            self.report("层数清空")
            return int(atk*1.5)
        return atk

    def reduce_enemy_attack(self, atk):
        if self.is_on_one_ship() and atk > 0:
            if dice.probability(self.state[ASI.BUILDING] * 0.1 - (self.ship.get_equivalent_shelter_of_ship() - 1) * 0.12):
                atk = 0
                self.report("喵")
        return atk

    def suggest(self):
        if self.state[ASI.BUILDING] < 9:
            return f"[e]提升层数|{self.state[ASI.BUILDING]}层|当前闪避率>>{self.state[ASI.BUILDING] * 10 - (self.ship.get_equivalent_shelter_of_ship() - 1) * 12}%"
        else:
            return f"[层数已满]|{self.state[ASI.BUILDING]}层|当前闪避率>>{self.state[ASI.BUILDING] * 10 - (self.ship.get_equivalent_shelter_of_ship() - 1) * 12}%"


al27 = Al27(27)


class Al28(Al_general):  # 鹘鸮

    def print_self_before_shelter(self,return_list = False):
        print_list = []
        if self.state[ASI.BUILDING] > 0:
            if return_list:
                print_list.append(r"/===\鹘鸮招架中")
                print_list += ["~~~~~"]* max(0, 4 - self.state[ASI.BUILDING])
            else:
                print(r"/===\鹘鸮招架中")
                print("~~~~~\n" * max(0, 4 - self.state[ASI.BUILDING]))
        return print_list

    def react(self):
        if self.state[ASI.BUILDING] == 0:
            enemy.target_ship = self.ship
            self.state[ASI.BUILDING] = 1
            self.report("启动报告")

    def reduce_enemy_attack(self, atk):
        if 0 < self.state[ASI.BUILDING] < 4:
            while atk:
                atk -= 1
                self.state[ASI.BUILDING] += 1
                if self.state[ASI.BUILDING] == 4:
                    break
        if self.state[ASI.BUILDING] >= 4:
            self.state[ASI.BUILDING] += atk
        if self.state[ASI.BUILDING] > 0:
            print(f"[鹘鸮]当前层数：{self.state[ASI.BUILDING]}")
        return atk

    def operate_in_afternoon(self):
        if self.state[ASI.COOLING] < 0:
            self.state[ASI.COOLING] += 1
            return
        if dice.current_who == Side.ENEMY:
            if self.state[ASI.BUILDING] == 1:
                self.ship.load(2)
                self.report("冷却")
                self.state[ASI.BUILDING] = 0
                self.state[ASI.COOLING] = -4
            elif self.state[ASI.BUILDING] > 1:
                if self.ship.missile > 1:
                    self.ship.load(-1)
                    atk_num = self.state[ASI.BUILDING] + 1
                    self.state[ASI.BUILDING] = 0
                    self.ship.attack(atk_num, DamageType.ORDINARY_ATTACK)
                    self.report("反击")
                    self.report("反击")
                    print(f"[鹘鸮]造成伤害：{atk_num}")
                else:
                    atk_num = self.state[ASI.BUILDING]
                    self.state[ASI.BUILDING] = 0
                    self.ship.attack(atk_num, DamageType.ORDINARY_ATTACK)
                    self.report("反击")
                    print(f"[鹘鸮]造成伤害：{atk_num}")
                if enemy.shelter < 0:
                    Txt.print_plus("[鹘鸮]勘破灭！", 2)

    def suggest(self):
        if self.state[ASI.COOLING] == 0 and self.state[ASI.BUILDING] == 0:
            return "[q]进入招架状态"
        elif self.state[ASI.BUILDING] > 0:
            return f"[招架中]临时护盾剩余{max(0, 4 - self.state[ASI.BUILDING])}点"
        else:
            return f"[冷却中]剩余{-self.state[ASI.COOLING]}天"


al28 = Al28(28)


class Al29(Al_general):  # 酒师

    def __init__(self, index):
        super().__init__(index)
        self.state = [[], 0, 0, 0, 0]

    def initialize(self):
        self.state = [[],0,0,0,0]

    def adjust_operation(self, raw: str) -> str:
        if raw == "2" and self.is_on_one_ship():
            return "w"
        return raw

    def react(self):
        self.state[ASI.OTHER].append(
            random.choices([0, 1, 2, 3], weights=[0, 3, 3, 2])[0]
        )
        self.report("建立治疗塔")

    def operate_in_morning(self):
        if self.state[ASI.OTHER]:

            self.state[ASI.OTHER] = [x for x in self.state[ASI.OTHER] if x != 0]

            self.ship.heal(
                len(self.state[ASI.OTHER])
            )
            for i in range(len(self.state[ASI.OTHER])):
                self.state[ASI.OTHER][i] -= 1

            Txt.print_plus(f"[酒师]工作中|救治{len(self.state[ASI.OTHER])}次")

            self.state[ASI.OTHER] = [x for x in self.state[ASI.OTHER] if x != 0]

    def print_self(self):
        if self.is_on_one_ship():
            for i in self.state[ASI.OTHER]:
                print(self.skin_list[i], end=" ")
            print()

    def generate_line_list(self):
        print_list = []
        if self.is_on_one_ship():
            icon = ""
            for i in self.state[ASI.OTHER]:
                icon += self.skin_list[i]
            print_list.append(icon)
        return print_list

    def suggest(self):
        if not self.state[ASI.OTHER]:
            return "[2/w]建立治疗塔"
        else:
            return f"[2/w]建立治疗塔|工作中|预计维持{max(self.state[ASI.OTHER])}天|总治疗量{sum(self.state[ASI.OTHER])}层"


al29 = Al29(29)


class Al30(Al_general):  # 湾区铃兰

    def react(self):
        if self.state[ASI.COOLING] == 0:
            self.ship.attack(2, DamageType.PARTICLE_CANNON_SHOOTING)
            self.state[ASI.COOLING] -= 5
            self.report("正常攻击")
            # p_c_manager.boom_now()
        else:
            enemy.attack(2,self.ship)
            voices.report("护盾", "湾区铃兰导致扣血")
            self.report("牺牲护盾发射")
            self.ship.attack(2, DamageType.PARTICLE_CANNON_SHOOTING)
            # p_c_manager.boom_now()

    def add_atk(self, atk: int, dmg_type: str) -> int:
        if self.state[ASI.COOLING] < 0 and dice.probability(0.5):
            self.report("增伤")
            return atk + 1
        else:
            return atk

    def operate_in_our_turn(self):
        if self.state[ASI.COOLING] < 0:
            self.state[ASI.COOLING] += 1

    def suggest(self):
        if self.state[ASI.COOLING] == 0:
            return "[q]粒子炮倾巢发射"
        else:
            if self.ship.shelter >= 2:
                return f"[冷却中]剩余{-self.state[ASI.COOLING]}天|伤害加成中|[q]牺牲护盾强行攻击"
            else:
                return f"[冷却中]剩余{-self.state[ASI.COOLING]}天|伤害加成中"


al30 = Al30(30)


class Al31(Al_general):  # 白鲟

    def react(self):
        if self.state[ASI.WORKING] == 0 and self.state[ASI.COOLING] == 0:
            self.state[ASI.WORKING] = 6
            self.ship.load(1)
            self.report("启动报告")

    def reduce_enemy_attack(self, atk):
        if self.state[ASI.WORKING] > 0 and atk > 0:
            di_atk = min(self.state, atk)
            self.state[ASI.WORKING] -= di_atk
            atk -= di_atk
            self.report("保护")
            if self.state[ASI.WORKING] == 0:
                self.state[ASI.COOLING] = -5
                self.report("冷却")
        return atk

    def operate_in_afternoon(self):
        if self.state[ASI.COOLING] < 0:
            self.state[ASI.COOLING] += 1
            return
        if self.state[ASI.WORKING] > 0 and dice.current_who == Side.PLAYER:
            self.state[ASI.WORKING] -= 1
            self.report("护盾流失")
            if self.state[ASI.WORKING] == 0:
                self.state[ASI.COOLING] = -5
                self.report("冷却")

    def suggest(self):
        if self.state[ASI.WORKING] == 0 and self.state[ASI.COOLING] == 0:
            return "[w]部署临时护盾并获得一枚弹药"
        elif self.state[ASI.WORKING] > 0:
            return f"[保护中]剩余{self.state[ASI.WORKING]}层"
        else:
            return f"[冷却中]剩余{-self.state[ASI.COOLING]}天"

    def print_self(self):
        print(".....\n" * self.state[ASI.WORKING])

    def generate_line_list(self):
        return ["....."]*self.state[ASI.WORKING]


al31 = Al31(31)


class Al32(Al_general):  # 普罗旺斯

    def react(self):
        if self.ship.missile % 2 == 1:
            self.ship.load(-1)
            self.ship.heal(2)
            self.report("耗弹回盾")
        else:
            self.ship.load(2)
            self.report("回弹")

    def suggest(self):
        if self.ship.missile % 2 == 1:
            return "[e]消耗粒子匣回充2护盾"
        else:
            return "[e]回充2个粒子匣"


al32 = Al32(32)


class Al33(Al_general):  # 蛊

    def __init__(self, index: int):
        super().__init__(index)
        self.state = [[0, 0, 0, 0, 0], 0, 0, 0, 0]

    def initialize(self):
        self.state = [[0, 0, 0, 0, 0],0,0,0,0]

    def react(self):
        #p_c_manager.boom_now()
        if self.ship.missile > 0 and enemy.shelter >= 5:
            self.ship.load(-1)
            pre_poi_list = [60, 40, 30, 10, 10]
            num = random.randint(135, 246)
            self.inject_and_report("射线攻击", {"num": num})
        else:
            pre_poi_list = [40, 30, 30, 0, 0]
            self.report("内置核同质异能素组攻击")
        for i in range(5):  #for (int i=0; i<5; i++)
            self.state[ASI.OTHER][i] += pre_poi_list[i]
        if enemy.shelter <= 5:  #去尾
            for i in range(enemy.shelter, 5):
                self.state[ASI.OTHER][i] = 0

    def check_if_move(self, times):
        if self.is_on_one_ship:
            for i in range(times):
                self.state[ASI.OTHER] = self.state[ASI.OTHER][1:]
                self.state[ASI.OTHER].append(0)

    def operate_in_afternoon(self):
        for i in range(5):
            if self.state[ASI.OTHER][i] > 0:
                self.state[ASI.OTHER][i] += 4
        while self.state[ASI.OTHER][0] >= 100:
            enemy.shelter -= 1
            self.report("正常攻击")
            if enemy.shelter != 0:
                self.state[ASI.OTHER][1] += self.state[ASI.OTHER][0] - 100
            self.check_if_move(1)

    def print_poisoned_shelter(self):
        if enemy.shelter > 0:
            future = self.state[ASI.OTHER].copy()
            if self.ship.missile > 0 and enemy.shelter >= 5:
                pre_poi_list = [60, 40, 30, 10, 10]
            else:
                pre_poi_list = [40, 30, 30, 0, 0]
            for i in range(5):
                future[i] += pre_poi_list[i]

            for i in range(1, enemy.shelter + 1):
                p = enemy.shelter - i
                if p < 5 and al33.state[ASI.OTHER][p] != 0:
                    print(f"----->{self.state[ASI.OTHER][p]} |q]>{future[p]}")
                elif p < 5 and al33.state[ASI.OTHER][p] == 0 and future[p] != 0:
                    print(f"-----    |q]>{future[p]}")
                else:
                    print("-----")

    def print_self(self):
        pass

    def generate_line_list(self):
        return []

    def suggest(self):
        if self.ship.missile > 0 and enemy.shelter >= 5:
            pre_poi_list = [60, 40, 30, 10, 10]
            return f"[q]射线粒子炮发射|估计破损{pre_poi_list}|加成中"
        else:
            pre_poi_list = [40, 30, 30, 0, 0]
            return f"[q]射线粒子炮发射|估计破损{pre_poi_list}"


al33 = Al33(33)


class Al34(Al_general):  # 风间浦

    def react(self):
#        if self.state[0] == 0:
#            self.state[0] = 9
#            self.ship.attack(1, DamageType.ORDINARY_ATTACK)
#            self.report("激进模式启动")
        if self.state[ASI.WORKING] == 0 and self.state[ASI.COOLING] == 0:
            self.state[ASI.WORKING] = 4
            self.ship.attack(1, DamageType.ORDINARY_ATTACK)
            self.report("激进模式启动")

    def add_hp(self, hp):
#        if not self.is_on_one_ship():
#            return hp
#        if self.state[0] == 0 and dice.probability(0.5):
#            self.report("保守模式治疗加成")
#            return hp + 1
#        elif self.state[0] == 0 and self.ship.shelter == 0:
#            self.report("保守模式治疗加成")
#            return hp + 1
#        else:
#            return hp

        if not self.is_on_one_ship():
            return hp
        if self.state[ASI.WORKING] == 0 and self.state[ASI.COOLING] == 0:
            if dice.probability(0.7) or self.ship.shelter == 0:
                self.report("保守模式治疗加成")
                return hp + 1
        if self.state[ASI.COOLING] < 0:
            if dice.probability(0.5) or self.ship.shelter == 0:
                self.report("保守模式治疗加成")
                return hp + 1
        return hp

    def operate_in_afternoon(self):
#        BEGIN_COOLING = 6
#        if self.state[0] > BEGIN_COOLING:
#            if self.ship.shelter <= 0:
#                self.ship.shelter = 1
#                self.report("激进模式保护")
#        elif self.state[0] == BEGIN_COOLING and self.state[1] != 0:
#            self.ship.heal(self.state[1])
#            self.state[1] = 0
#            self.report("安全港就位")
#            self.state[0] -= 1
#
#        if self.state[0] > BEGIN_COOLING and dice.current_who == Side.ENEMY:
#            self.state[0] -= 1
#        elif 0 < self.state[0] <= BEGIN_COOLING and dice.current_who == Side.PLAYER:
#            self.state[0] -= 1
        if self.state[ASI.WORKING] > 1: # 激进模式下
             if self.ship.shelter <= 0:
                 self.ship.shelter = 1
                 self.report("激进模式保护")
        elif self.state[ASI.WORKING] == 1: # 脱离激进模式瞬间
            if self.state[ASI.BUILDING] != 0:
                self.ship.heal(self.state[ASI.BUILDING])
            self.state[ASI.WORKING] = 0
            self.state[ASI.BUILDING] = 0
            self.state[ASI.COOLING] = -6
            self.report("安全港就位")

        if self.state[ASI.WORKING] > 0 and dice.current_who == Side.ENEMY:
            self.state[ASI.WORKING] -= 1
        if self.state[ASI.COOLING] < 0 and dice.current_who == Side.PLAYER:
            self.state[ASI.COOLING] += 1

    def reduce_enemy_attack(self, atk): # 实则不然
#        if self.state[0] > 5 and atk > 0:
#            self.state[1] += atk
#            self.inject_and_report("记录伤害", {"atk": atk})
#        return atk
        if self.state[ASI.WORKING] > 0 and atk > 0:
            self.state[ASI.BUILDING] += atk
            self.inject_and_report("记录伤害", {"atk": atk})
        return atk

    def suggest(self):
        if self.state[ASI.WORKING] > 0:
            return f"[激进模式]剩余{self.state[ASI.WORKING]}天|{self.state[ASI.BUILDING]}伤害计入"
        elif self.state[ASI.WORKING] == 1:
            return f"[脱离激进模式]{self.state[ASI.BUILDING]}护盾即将回充"
        elif self.state[ASI.COOLING] < 0:
            return f"[充能中]剩余{-self.state[ASI.COOLING]}天|[2]回盾加成中"
        else:
            return "[w]进入激进模式|[保守模式]>[2]回盾加成中"


al34 = Al34(34)


class Al35(Al_general):  # 青鹄

    voi_list = {"q": ["复道行空，敌盾贯通！", "泡影俱散，对面完蛋！"], "w": ["固若金汤，有烟无伤！", "防微杜渐，护盾无限！"],
                "e": ["", ""]}

    def react(self):
        main_loops.days -= 1
        if self.state[ASI.LOGGING] < 4:
            self.state[ASI.LOGGING] += 2
            self.report("充能")
        else:
            if self.ship.missile > 1:
                self.ship.load(-2)
                self.ship.attack(2, DamageType.ORDINARY_ATTACK)
                self.state[ASI.LOGGING] = 0
                self.report("攻击")
            else:
                self.ship.load(1)
                if dice.current_who == Side.ENEMY:
                    self.ship.load(1)
                self.report("装弹")

    def operate_in_morning(self):
        if self.is_on_one_ship():
            self.state[ASI.LOGGING] += 1
        if self.state[ASI.LOGGING] >= 4 and dice.current_who == Side.ENEMY:
            self.ship.heal(1)
            self.ship.load(1)
            self.report("准备")

    def check_if_extra_act(self):

        if not self.is_on_one_ship():
            return

        if self.state[ASI.LOGGING] >= 4 and dice.current_who == Side.ENEMY:
            suggestion_tree = field_printer.generate_suggestion_tree(self.ship)
            suggestion_tree.topic = "额外回合操作"

            if self.ship == another_ship:
                main_loops.server.send_tree(suggestion_tree)
                Txt.print_plus("正在等待僚机指挥官操作<<<")
                inp = main_loops.server.ask_plus("""+[+Extra action+]+>>选择你的操作[q/w/e]立即响应或重置其冷却""", ["q", "w", "e"])
            else:
                suggestion_tree.print_self()
                if entry_manager.current_mode == Modes.PPVE:
                    main_loops.server.send_str("正在等待长机指挥官操作<<<")
                inp = Txt.ask_plus("""+[+Extra action+]+>>选择你的操作[q/w/e]立即响应或重置其冷却""", ["q", "w", "e"])

            d = "qwe".find(inp)
            al_temp: Al_general = self.ship.al_list[d]
            if al_temp:
                if al_temp.state[ASI.COOLING] < 0:
                    al_temp.initialize()
                    self.report_plus(inp, 1)
                    Txt.print_plus(f"[{al_temp.type}] {al_temp.short_name}#{al_temp.index}冷却已重置")
                else:
                    self.report_plus(inp, 0)
                    al_temp.react()
            if self.state[ASI.LOGGING] != 0:
                self.state[ASI.LOGGING] -= 4

    def report_plus(self, selected_type, num):
        txt = self.voi_list[selected_type][num]
        if txt == "":
            return
        if storage_manager.show_assets()["39"] < 3:
            txt = "[青鹄]" + txt[0:min(len(txt), 4)] + "！"
        Txt.print_plus(txt)
        if entry_manager.current_mode == Modes.PPVE:
            main_loops.server.send_str(txt)


    def suggest(self):
        if self.state[ASI.LOGGING] < 1:
            return f"[e]增加二层充能|充能层数{self.state[ASI.LOGGING]}/4"
        elif self.state[ASI.LOGGING] < 4:
            return f"[e]增加二层充能并进入待命状态|充能层数{self.state[ASI.LOGGING]}/4"
        elif self.ship.missile > 1:
            return f"[e]攻击对方并清空充能|[待命中]获得额外回合|充能层数{self.state[ASI.LOGGING]}/4"
        else:
            return f"[e]装弹|[待命中]获得额外回合|充能层数{self.state[ASI.LOGGING]}/4"


al35 = Al35(35)


class Al36(Al_general):  # 西岭

    def reduce_enemy_attack(self, atk):
        if not self.is_on_one_ship() or self.state[ASI.LOGGING] == 1:
            return atk
        if dice.probability(0.5):
            self.report("拦截成功")
            return 0
        else:
            self.report("拦截失败")
            return atk

    def react(self):
        if self.state[ASI.LOGGING] == 0:
            self.state[ASI.LOGGING] = 1
        else:
            self.state[ASI.LOGGING] = 0

    def operate_in_afternoon(self):
        if self.state[ASI.LOGGING] == 1 and dice.current_who == Side.PLAYER:
            if_auto = False
            count_shot = 40
            while count_shot > 0:
                if not if_auto:
                    inp = input(f"[西岭]机炮已就位|剩余{count_shot}梭>>>")
                    if inp == "a":
                        if_auto = True
                else:
                    print(f"[西岭]机炮已就位|剩余{count_shot}梭")
                count_shot -= 1
                if dice.probability(0.017):
                    print("[西岭]" +
                          random.choice(
                              [
                                  "攻击命中！",
                                  "护盾破碎！",
                                  "判定摧毁！"
                              ]
                          ) +
                          "------------+++[命中确认]+++------------"
                          )
                    self.ship.attack(1, DamageType.ORDINARY_ATTACK)
                else:
                    print("[西岭]攻击未命中！--------[未能命中]---------")
        time.sleep(0.4)

    def suggest(self):
        if self.state[ASI.LOGGING] == 0:
            return "[自动防空]导弹拦截中|[e]切换至饱和式弹雨扫射模式"
        else:
            return "[弹雨启动]每日攻击就位|[e]切换回自动防御模式"


al36 = Al36(36)


class Al37(Al_general): # 星尘

    def react(self):
        if self.state[ASI.COOLING] < 0:
            self.report("冷却中")
            return
        result = Txt.qte("星尘") if self.ship == my_ship else main_loops.server.send_qte("星尘")

        if result <= 2:
            damage = min(10, self.ship.missile)
            self.state[ASI.COOLING] = -7
        elif result <= 4:
            damage = min(4, self.ship.missile)
            self.state[ASI.COOLING] = -4
        else:
            print("?")
            self.report("锁定未成功")
            return
        self.report("锁定成功")
        self.ship.attack(int(damage * 1.5), DamageType.PARTICLE_CANNON_SHOOTING)
        self.ship.load(-damage)
        Txt.print_plus(
            f" 有效伤害>{damage_previewer.enemy_shelter - enemy.shelter}.0"
        )
        if self.ship == another_ship:
            main_loops.server.send_str(f" 有效伤害>{damage_previewer.enemy_shelter - enemy.shelter}.0")

    def operate_in_afternoon(self):
        if self.state[ASI.COOLING] < 0:
            self.state[ASI.COOLING] += 1
        if self.is_on_one_ship() and enemy.shelter < -1:
            self.ship.load(int((-1-enemy.shelter)*0.5))
            enemy.shelter=-1
            self.report("能量回收")

    def suggest(self):
        if self.state[ASI.COOLING] < 0:
            return f"[冷却中]剩余{-self.state[ASI.COOLING]}天"
        else:
            return "[q]启动狙击粒子炮|注意-含有qte"


al37 = Al37(37)


class Al38(Al_general):  # 澈

    def react(self):
        self.state[ASI.LOGGING] += 3
        self.report("获得锋镝")
        enemy.attack(1,self.ship)  # todo:禁用烈风
        enemy.attack(1,self.ship)

    def reduce_enemy_attack(self, atk):
        """
        其实并不会reduce
        """
        if self.is_on_one_ship() and self.state[ASI.WORKING] == 0 and dice.probability(0.5):
            self.state[ASI.LOGGING] += 1
            self.report("收到")

        return atk

    def operate_in_afternoon(self):
        if self.state[ASI.LOGGING] > 0 and self.ship.shelter < 1:
            cure = min(self.state[ASI.LOGGING], 2 - self.ship.shelter)
            self.state[ASI.LOGGING] -= cure
            self.ship.heal(cure)
            self.report("护盾补充")

    def operate_in_morning(self):
        if self.state[ASI.LOGGING] > 9 and self.state[ASI.WORKING] == 0:
            self.state[ASI.WORKING] = 1
            self.report("激进模式开启")
        elif self.state[ASI.LOGGING] < 5 and self.state[ASI.WORKING] == 1:
            self.state[ASI.WORKING] = 0
            self.report("激进模式关闭")

    def add_atk(self, atk, dmg_type):
        if self.state[ASI.WORKING] == 0 and self.is_on_one_ship() and dice.probability(0.5):
            self.state[ASI.LOGGING] += 1
            self.report("收到")
        if self.state[ASI.WORKING] == 1 and self.state[ASI.LOGGING] > 0:
            self.state[ASI.LOGGING] -= 1
            self.report("牺牲加成")
            return atk + 1
        return atk

    def print_self(self):
        if self.state[ASI.LOGGING] <= 5:
            print("--X--\n" * self.state[ASI.LOGGING])
        else:
            print(f"--X-- x{self.state[ASI.LOGGING]}")

    def generate_line_list(self):
        print_list = []
        if self.state[ASI.LOGGING] <= 5:
            print_list += ["--X--"] * self.state[ASI.LOGGING]
        else:
            print_list.append(f"--X-- x{self.state[ASI.LOGGING]}")
        return print_list

    def suggest(self):
        if self.state[ASI.WORKING] == 1:
            return f"[w]自伤并获得三点锋镝|[寂]伤害加成中|[锋镝]>{self.state[ASI.LOGGING]}"
        else:
            return f"[w]自伤并获得三点锋镝|[澄]敌我攻击概率获得锋镝|[锋镝]>{self.state[ASI.LOGGING]}"


al38 = Al38(38)


class Al39(Al_general):  # 黎明维多利亚
    """
    黎明维多利亚的state转移过程是：
    BUILDING: 0 1 2 3 4 5->0
    WORKING: 5 4 3 2 1 0->0
    """

    def adjust_operation(self, raw: str) -> str:
        if self.state[ASI.WORKING] >= 4 and raw == "q":
            return "1"
        return raw

    def add_num(self, num: int):
        if self.state[ASI.WORKING] > 0:
            return num
        if num <= 0:
            return num
        self.state[ASI.BUILDING] += num
        if self.state[ASI.BUILDING] > 5:
            self.state[ASI.BUILDING] = 5
        self.report("建造中")
        return num

    def operate_in_afternoon(self):
        if self.state[ASI.BUILDING] == 5:
            self.state[ASI.BUILDING] = 0
            self.state[ASI.WORKING] = 5
            self.report("准备好")
        if self.state[ASI.WORKING] == 1:
            self.state[ASI.WORKING] = 0
            self.report("下线")

    def add_atk(self, atk: int, dmg_type: str):
        if dmg_type != DamageType.MISSILE_LAUNCH:
            return atk
        if self.state[ASI.WORKING] <= 0:
            return atk
        atk += 1
        self.report("增伤")
        self.state[ASI.WORKING] -= 1
        return atk

    def react(self):
        if self.state[ASI.WORKING] > 0:
            # 工作状态：发射增强导弹
            if self.state[ASI.WORKING] >= 4:
                result = self.ship.attack(1, DamageType.MISSILE_LAUNCH)
                self.ship.load(-1)
                if result > 0:
                    voices.report(self.ship.platform, "发射")
            else:
                # 爆发状态：全弹发射
                launch_num = min(self.state[ASI.WORKING], self.ship.missile)
                if launch_num <= 0:
                    self.report("导弹不足")
                    return
                for _ in range(launch_num):
                    self.ship.attack(2, DamageType.MISSILE_LAUNCH)
                    self.ship.load(-1)
                self.state[ASI.WORKING] = 0
                self.report("下线")
                enemy.attack(launch_num - 1, self.ship)
        else:
            # 建造状态：上弹
            self.ship.load(1)
            voices.report(self.ship.platform, "上弹")
            

    def suggest(self):
        if self.state[ASI.WORKING] == 0:
            return f"[充能中]当前层数>{self.state[ASI.BUILDING]}/5|[0/任意方式]获得弹药以充能"
        elif self.state[ASI.WORKING] >= 4:
            return f"[保守状态]剩余层数>{self.state[ASI.WORKING]}/5|[1/q]发射增强导弹"
        else:
            return f"[爆发状态]剩余层数>{self.state[ASI.WORKING]}|[1]发射增强导弹|[q]全弹发射 扣除{int(min(self.state[ASI.WORKING], self.ship.missile))-1}点护盾"


al39 = Al39(39)


class Al40(Al_general):  # 冷水

    def get_equivalent_shelter(self):
        return self.state[ASI.LOGGING]

    def react(self):
        if self.ship.shelter < 1:
            self.report("护盾不足")
            self.ship.heal(1)
            return
        self.ship.shelter -= 1
        self.state[ASI.LOGGING] += 1
        self.report("冷水盾上线")

    def print_self_before_shelter(self,return_list = False):
        print_list = []
        if return_list:
            for _ in range(self.state[ASI.LOGGING]):
                print_list += [self.skin_list[0]]
        else:
            for _ in range(self.state[ASI.LOGGING]):
                print(self.skin_list[0])
        return print_list
    def reduce_enemy_attack(self, atk):
        while self.state[ASI.LOGGING] != 0 and atk != 0:
            if dice.probability(0.33):
                self.state[ASI.LOGGING] -= 1
                self.ship.attack(1, DamageType.ORDINARY_ATTACK)
                atk -= 1
                self.report("破碎")
            else:
                atk = 0
                self.report("承受")
        return atk

    def suggest(self):
        if self.ship.shelter == 0:
            return "[护盾不足]不能使用冷水|[2]回充护盾"
        else:
            return "[e]充入冷水"


al40 = Al40(40)

class Al41(Al_general): # 暮离
    """
    暮离的state转移过程是：
    COOLING: 0->-3->-2->-1->0
    """

    def react(self):
        if self.state[ASI.COOLING] == 0:
            if self.ship.missile > 0:
                self.ship.load(-1)
                self.ship.heal(3)
                self.report("耗弹治疗")
            else:
                self.ship.load(2)
            self.state[ASI.COOLING] = -3

    def operate_in_afternoon(self):
        if self.state[ASI.COOLING] >= -3 and self.ship.shelter <= 0:
            if self.ship.missile > 0:
                self.ship.load(-1)
            self.state[ASI.COOLING] = -6
            self.ship.shelter = 3
            self.report("急救")
        if self.state[ASI.COOLING] < 0:
            self.state[ASI.COOLING] += 1
    
    def reduce_enemy_attack(self, atk):
        if atk > 1:
            self.ship.load(atk)
            self.report("受击上弹")
        return atk
    
    def suggest(self):
        if self.state[ASI.COOLING] == 0 and self.ship.missile > 0:
            return "[w]消耗弹药回复三点护盾"
        elif self.state[ASI.COOLING] == 0 and self.ship.missile == 0:
            return "[w]回复两点弹药"
        elif -3 <= self.state[ASI.COOLING] < 0:
            return f"[急救激活中]扣除一弹药（若有）并强行把护盾抬至三点|[主动冷却中]剩余{-self.state[ASI.COOLING]}天"
        else:
            return f"[急救冷却中]剩余{-3-self.state[ASI.COOLING]}天|[主动冷却中]剩余{-self.state[ASI.COOLING]}天"

al41=Al41(41)
                

class Al42(Al_general): # 百里香

    def react(self):
#        if self.state == 0:
#            self.state = 1
#            self.report("开始")
#        elif self.state % 2 == 1:
#            self.state += 2
#            self.report("叠层")
        if self.state[ASI.WORKING] != 0:
            return
        if self.state[ASI.BUILDING] == 0:
            self.report("开始")
        self.state[ASI.BUILDING] += 1
        self.report("叠层")

    def adjust_operation(self, raw):
#        if self.state % 2 == 1 and raw != "q" :
#            self.state += 1
#            self.report("启动")
#        return raw
        if self.state[ASI.BUILDING] != 0 and raw != "q":
            self.state[ASI.WORKING] = self.state[ASI.BUILDING]
            self.state[ASI.BUILDING] = 0
            self.report("启动")
        return raw


    def operate_in_morning(self):
#        if self.state % 2 == 1 or self.state == 0:
#            return
#        if dice.current_who == Side.ENEMY:
#            self.ship.attack(1,DamageType.ORDINARY_ATTACK)
#            self.report("攻击")
#        else:
#            self.state -= 2
#            self.report("掉层")
#            if self.state == 0:
#                self.report("结束")
        if self.state[ASI.WORKING] == 0:
            return
        if dice.current_who == Side.ENEMY:
            self.ship.attack(1, DamageType.ORDINARY_ATTACK)
            self.report("攻击")
        else:
            self.state[ASI.WORKING] -= 1
            self.report("掉层")
            if self.state[ASI.WORKING] == 0:
                self.report("结束")
    
    def suggest(self):
#        if self.state == 0:
#            return "[q]粒子炮启动"
#        elif self.state % 2 == 1:
#            return f"[q]充能|当前层数>{self.state//2+1}"
#        else:
#            return f"[释放中]剩余{self.state/2}层"
        if self.state[ASI.WORKING] == 0 and self.state[ASI.BUILDING] != 0:
            return f"[q]充能|当前层数>{self.state[ASI.BUILDING]}"
        elif self.state[ASI.WORKING] != 0:
            return f"[释放中]剩余{self.state[ASI.WORKING]}层"
        else:
            return "[q]启动"

al42=Al42(42)


class FieldPrinter:

    @staticmethod
    def print_for_fight(me: MyShip, opposite: EnemyShip):
        """
        打印fight模式下双方护盾和导弹，以及我方Al
        :param me:
        :param opposite:
        :return: 无
        """
        opposite.print_self_missile(entry_manager.get_rank_of("2") >= 1)
        print()
        opposite.print_self_shelter()
        damage_previewer.print_enemy_dmg(opposite.shelter)
        print("\n\n\n")
        for al in reversed(my_ship.al_list):
            try:
                al.print_self_before_shelter()
            except AttributeError:
                pass
        damage_previewer.print_my_ship_dmg(me.shelter, mute=(my_ship.get_equivalent_shelter_from_als() != 0))
        me.print_self_shelter(entry_manager.get_rank_of("2") >= 2)
        for al in reversed(my_ship.al_list):
            try:
                al.print_self_behind_shelter()
            except AttributeError:
                pass
        me.print_self_missile()
        print()
        for al in reversed(my_ship.al_list):
            try:
                al.print_self_behind_missile()
            except AttributeError:
                pass
        print()
        damage_previewer.update(me.shelter, opposite.shelter)

    @staticmethod
    def print_for_ppve(me: MyShip, another:MyShip, opposite: EnemyShip):
        opposite.print_self_missile(entry_manager.get_rank_of("2") >= 1)
        print()
        opposite.print_self_shelter()
        damage_previewer.print_enemy_dmg(opposite.shelter)
        print("\n\n\n")

        left = []
        if me.life_for_ppve > 0:
            left.append("("+"+"*(me.life_for_ppve-main_loops.days+1)+")")
        elif me.life_for_ppve == -1:
            left.append("(-)")
        if opposite.target_ship == me:
            left.append("@")
        for al in reversed(me.al_list):
            try:
                left += al.print_self_before_shelter(return_list=True)
            except AttributeError:
                pass
        left += me.generate_shelter_list(entry_manager.get_rank_of("2") >= 2)
        for al in reversed(me.al_list):
            try:
                left += al.print_self_behind_shelter(return_list = True)
            except AttributeError:
                pass
        left += me.generate_missile_list()
        left += [""]
        for al in reversed(me.al_list):
            try:
                left += al.print_self_behind_missile(return_list= True)
            except AttributeError:
                pass
        left += [""]

        right = []
        if another.life_for_ppve > 0:
            right.append("("+"+"*(another.life_for_ppve-main_loops.days+1)+")")
        elif another.life_for_ppve == -1:
            right.append("(-)")
        if opposite.target_ship == another:
            right.append("@")
        for al in reversed(another.al_list):
            try:
                right += al.print_self_before_shelter(return_list = True)
            except AttributeError:
                pass
        right += another.generate_shelter_list(entry_manager.get_rank_of("2") >= 2)
        for al in reversed(another.al_list):
            try:
                right += al.print_self_behind_shelter(return_list = True)
            except AttributeError:
                pass
        right += another.generate_missile_list()
        right += [""]
        for al in reversed(another.al_list):
            try:
                right += al.print_self_behind_missile(return_list = True)
            except AttributeError:
                pass
        right += [""]
        Txt.n_column_print([left,right],60)
        damage_previewer.update(me.shelter, opposite.shelter)

    @staticmethod
    def generate_for_ppve(me: MyShip, another:MyShip, opposite: EnemyShip):
        out = ""
        out += opposite.generate_self_missile(entry_manager.get_rank_of("2") >= 1)
        out += "\n"
        out += opposite.generate_self_shelter()
        #damage_previewer.print_enemy_dmg(opposite.shelter) TODO
        out += "\n\n\n"

        left = []
        if me.life_for_ppve > 0:
            left.append("("+"+"*(me.life_for_ppve-main_loops.days+1)+")")
        elif me.life_for_ppve == -1:
            left.append("(-)")
        if opposite.target_ship == me:
            left.append("@")
        for al in reversed(me.al_list):
            try:
                left += al.print_self_before_shelter(return_list=True)
            except AttributeError:
                pass
        left += me.generate_shelter_list(entry_manager.get_rank_of("2") >= 2)
        for al in reversed(me.al_list):
            try:
                left += al.print_self_behind_shelter(return_list = True)
            except AttributeError:
                pass
        left += me.generate_missile_list()
        left += [""]
        for al in reversed(me.al_list):
            try:
                left += al.print_self_behind_missile(return_list= True)
            except AttributeError:
                pass
        left += [""]

        right = []
        if another.life_for_ppve > 0:
            right.append("("+"+"*(another.life_for_ppve-main_loops.days+1)+")")
        elif another.life_for_ppve == -1:
            right.append("(-)")
        if opposite.target_ship == another:
            right.append("@")
        for al in reversed(another.al_list):
            try:
                right += al.print_self_before_shelter(return_list = True)
            except AttributeError:
                pass
        right += another.generate_shelter_list(entry_manager.get_rank_of("2") >= 2)
        for al in reversed(another.al_list):
            try:
                right += al.print_self_behind_shelter(return_list = True)
            except AttributeError:
                pass
        right += another.generate_missile_list()
        right += [""]
        for al in reversed(another.al_list):
            try:
                right += al.print_self_behind_missile(return_list = True)
            except AttributeError:
                pass
        right += [""]
        out += Txt.n_column_generate([left,right],60)
        return out

    @staticmethod
    def print_basic_info(days):
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
        print()

    @staticmethod
    def generate_basic_info(days) -> str:
        """
        生成战场基本信息字符串
        :param days: 当前天数
        :return: 无
        """
        out = "~~~~~~~~~~~~~~~~~~~~~~~~\n"
        out += f"指挥官，今天是战线展开的第{days}天。\n"
        if days < 5:
            out += "当前舰船位置>>正在离港\n"
        elif days < 10:
            out += "当前舰船位置>>我方领土边缘\n"
        elif days <= 20:
            out += "当前舰船位置>>边境核心战场\n"
        elif days > 20:
            out += "当前舰船位置>>敌方腹地危险区域\n"
        out += "\n"
        return out

    @staticmethod
    def generate_suggestion_tree(ship = my_ship):
        suggestion_list = []
        for al in ship.al_list:
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

    def print_suggestion_for_ppve(self):
        Txt.n_column_print(
            [self.generate_suggestion_tree(my_ship).generate_line_list(),
             self.generate_suggestion_tree(another_ship).generate_line_list()]
        , 60)
    def generate_suggestion_for_ppve(self) -> str:
        return Txt.n_column_generate(
            [self.generate_suggestion_tree(my_ship).generate_line_list(),
             self.generate_suggestion_tree(another_ship).generate_line_list()]
        , 60)

    @staticmethod
    def ppve_help_prompt():
        prompt = "[m1~m9]转移1~9枚弹药 [s]转移一层护盾 [c]救援"
        main_loops.server.send_str(prompt)
        print(prompt)


    @staticmethod
    def print_key_prompt(ship = my_ship):
        key_prompt = "[0/space] 装弹  [1] 发射  [2] 上盾  "
        for al in ship.al_list:
            try:
                key_prompt += f"[{al.type}] {al.short_name}#{al.index}  "
            except AttributeError:
                key_prompt += "[NO INFO]  "
        if ship == another_ship:
            main_loops.server.send_str(key_prompt)
            return
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
            "max_disaster_point": storage_manager.get_value_of("max_disaster_point"),
            "max_infinity_round": storage_manager.get_value_of("max_infinity_round")
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
        self.all_tree_list["终焉结工业"].inject({
            "total_assets": storage_manager.estimate_total_assets()
        })
        self.all_tree_list["资源跟踪器"].inject({
            "short_name": storage_manager.get_value_of("tracing_al")
        })
        self.all_tree_list["资源跟踪器"].rewrite_lines(
            storage_manager.generate_gap_list()
        )

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

class MainLoops:

    def __init__(self):
        self.server = None
        self.days = 0
        self.entry_begin_day = 0
        self.entry_delta = 1
        self.infinity_round = 0

    @staticmethod
    def __is_over() -> Literal[-1, 0, 1]:
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
    def is_near_death(ship:MyShip) -> bool:
        if ship.shelter < 0:
            return True
        if entry_manager.get_rank_of("5") != 0 and ship.get_equivalent_shelter_of_ship() <= 0:
            return True
        return False


    @staticmethod
    def __get_adjusting_shelter_and_missile(ship:MyShip=my_ship) -> tuple[int, int]:
        """
        基于SBMM理念对敌方护盾和导弹进行增强
        :return: 一个元组，包含敌方护盾、导弹的修正值
        """
        total = al_manager.get_total_al_rank(ship) // 3
        if total < 1:
            return 0, 0
        shelter = random.randint(1, total)
        return shelter, total - shelter

    @staticmethod
    def __get_force_advance() -> Literal[-1, 0, 1]:
        """
        判定是否强制使某一方行动
        :return: 1代表我方，-1代表敌方，0代表不强制
        """
        if al26.is_my_turn():
            return 1
        return 0
    
    def is_over_for_ppve(self):
        if self.is_near_death(my_ship) and self.is_near_death(another_ship):
            return -1
        if enemy.shelter < 0:
            return 1
        for ship in [my_ship,another_ship]:
            ship:MyShip
            if not self.is_near_death(ship) and ship.life_for_ppve > 0:
                ship.life_for_ppve = -1
                voices.report("战场播报","被救起")
            elif self.is_near_death(ship):
                if ship.life_for_ppve == -1:
                    return -1
                elif ship.life_for_ppve == 0:
                    ship.life_for_ppve = self.days+5
                elif self.days == ship.life_for_ppve:
                        return -1
        return 0



    def initialize_before_fight(self):
        # 舰船初始化
        my_ship.initialize()
        shelter, missile = self.__get_adjusting_shelter_and_missile()
        enemy.initialize(shelter, missile)
        # 终焉结初始化
        al_manager.initialize_all_al()
        # 骰子初始化
        dice.set_probability(0.8)
        dice.set_di(0.3)
        dice.set_additional_di(0)
        # 随机事件初始化
        ocp_manager.initialize()
        # 自动驾驶初始化
        auto_pilot.refresh()
        # 护盾破碎效果初始化
        damage_previewer.initialize(my_ship.shelter, enemy.shelter)
        # 词条管理器初始化
        entry_manager.set_mode(Modes.FIGHT)
        entry_manager.clear_all_flow()
        # 确定词条烈度
        self.entry_begin_day = 20 - al_manager.get_total_al_rank(my_ship)
        self.entry_delta = (40 - al_manager.get_total_al_rank(my_ship)) // 4
        # 设置天数
        self.days = 1

    def fight_mainloop(self):
        sounds_manager.switch_to_bgm("fight")
        while 1:
            # dawn
            if (rank := entry_manager.get_rank_of("11")) != 0:
                dice.set_additional_di(rank * 0.1)
            who = dice.decide_who(force_advance=self.__get_force_advance())
            if self.days >= self.entry_begin_day \
                    and (self.days - self.entry_begin_day) % self.entry_delta == 0:
                entry_manager.push_up()
            ocp_manager.try_begin_new_ocp()
            time.sleep(0.4)

            # morning
            for al in my_ship.al_list:
                if al:
                    al.operate_in_morning()
            field_printer.print_basic_info(self.days)
            entry_manager.print_all_flow_rank()
            print_plus(ocp_manager.generate_current_ocp_prompt())
            field_printer.print_for_fight(my_ship, enemy)
            field_printer.generate_suggestion_tree().print_self()
            field_printer.print_key_prompt()

            # noon
            if who == Side.PLAYER:
                Txt.print_plus("今天由我方行动")
                ocp_manager.operate_in_my_day()
                my_ship.react()
            else:
                Txt.print_plus("今天由敌方行动")
                ocp_manager.operate_in_enemy_day()
                enemy.react()

            # afternoon
            for al in my_ship.al_list:
                if al:
                    al.operate_in_afternoon()
                    if who == Side.PLAYER:
                        al.operate_in_our_turn()

            # dusk
            ocp_manager.try_end_old_ocp()
            ocp_manager.cool_ocp()
            if (result := self.__is_over()) != 0:
                break
            self.days += 1
        sounds_manager.stop_bgm()
        if result == 1:
            print()
            Txt.print_plus("=========我方胜利=========")
            print()
            damage_previewer.show_total_dmg(my_ship.shelter, enemy.shelter)
            sounds_manager.switch_to_bgm("win")
            storage_manager.drop_for_fight()
            input_plus("[enter]回站")
            sounds_manager.stop_bgm()
            return
        print()
        Txt.print_plus("=========敌方胜利=========")
        print()
        damage_previewer.show_total_dmg(my_ship.shelter, enemy.shelter)
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
        shelter, missile = self.__get_adjusting_shelter_and_missile()
        enemy.initialize(shelter, missile)
        # 终焉结初始化
        al_manager.initialize_all_al()
        # 骰子初始化
        dice.set_probability(0.8)
        dice.set_di(0.3)
        dice.set_additional_di(0)
        # 自动驾驶初始化
        auto_pilot.refresh()
        # 护盾破碎效果初始化
        damage_previewer.initialize(my_ship.shelter, enemy.shelter)
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

    def disaster_mainloop(self):
        sounds_manager.switch_to_bgm("fight")
        while 1:
            # dawn
            time.sleep(0.4)
            who = dice.decide_who(force_advance=self.__get_force_advance())

            # morning
            for al in my_ship.al_list:
                if al:
                    al.operate_in_morning()
            field_printer.print_basic_info(self.days)
            entry_manager.print_all_selected_rank()
            field_printer.print_for_fight(my_ship, enemy)
            field_printer.generate_suggestion_tree().print_self()
            field_printer.print_key_prompt()

            # noon
            if who == Side.PLAYER:
                Txt.print_plus("今天由我方行动")
                my_ship.react()
            else:
                Txt.print_plus("今天由敌方行动")
                enemy.react()

            # afternoon
            if entry_manager.get_rank_of("13") != 0 and self.days > 100 - 20 * entry_manager.get_rank_of("13"):
                enemy.attack(1)
                entry_manager.all_entries["13"].print_when_react()
            for al in my_ship.al_list:
                if al:
                    al.operate_in_afternoon()
                    if who == Side.PLAYER:
                        al.operate_in_our_turn()

            # dusk
            if entry_manager.get_rank_of("5") != 0 and my_ship.get_equivalent_shelter_of_ship() <= 0:
                entry_manager.all_entries["5"].print_when_react()
                result = -1
                break
            if (result := self.__is_over()) != 0:
                break
            self.days += 1
        sounds_manager.stop_bgm()
        if result == 1:
            print()
            Txt.print_plus("=========我方胜利=========")
            print()
            damage_previewer.show_total_dmg(my_ship.shelter, enemy.shelter)
            sounds_manager.switch_to_bgm("win")
            times = (entry_manager.count_total_points() // 100)
            if times == 0:
                times = 1
            storage_manager.drop_for_fight(times=times)
            storage_manager.set_value_of("max_disaster_point",entry_manager.count_total_points())
            input_plus("[enter]回站")
            sounds_manager.stop_bgm()
            return
        print()
        Txt.print_plus("=========敌方胜利=========")
        print()
        damage_previewer.show_total_dmg(my_ship.shelter, enemy.shelter)
        if storage_manager.has_enough_ssd(my_ship.total_al_rank):
            storage_manager.cost_ssd(my_ship.total_al_rank)
            input_plus("[enter]回站")
            return
        storage_manager.destroy_al(my_ship.al_list)
        al_manager.clear_al()
        input_plus("[enter]回站")
        return

    def initialize_before_infinity(self):
        # 舰船初始化
        my_ship.initialize()
        my_ship.set_default_al()
        shelter, missile = self.__get_adjusting_shelter_and_missile()
        enemy.initialize(shelter, missile)
        # 终焉结初始化
        al_manager.initialize_all_al()
        al_manager.al_max_rank_q, al_manager.al_max_rank_w, al_manager.al_max_rank_e = 2,2,2
        # 骰子初始化
        dice.set_probability(0.8)
        dice.set_di(0.3)
        dice.set_additional_di(0)
        # 自动驾驶初始化
        auto_pilot.refresh()
        # 护盾破碎效果初始化
        damage_previewer.initialize(my_ship.shelter, enemy.shelter)
        # 词条管理器初始化
        entry_manager.set_mode(Modes.INFINITY)
        entry_manager.clear_all_flow()
        # 设置天数和轮数
        self.days = 1
        self.infinity_round = 1
        # 终焉结选择
        while 1:
            print()
            station_trees_manager.all_tree_list["终焉结信息"].inject({
            "total_al_rank": my_ship.total_al_rank,
            "ssg_tag": "",
            "ssg_num": "",
            "q_information": my_ship.al_list[0].len_name \
                if my_ship.al_list[0] \
                else "[No Info]",
            "w_information": my_ship.al_list[1].len_name \
                if my_ship.al_list[1] \
                else "[No Info]",
            "e_information": my_ship.al_list[2].len_name \
                if my_ship.al_list[2] \
                else "[No Info]"
            })
            station_trees_manager.all_tree_list["终焉结信息"].print_self()
            inp = input_plus("请输入您的准备操作| [q/w/e]更换终焉结| [enter]进入战斗")
            match inp:
                case "q"|"w"|"e":
                    al_manager.choose_al_with_limit(inp)
                case "":
                    break
                case _:
                    pass

    def __initialize_between_infinity(self):
        # 重设敌方舰船
        shelter, missile = self.__get_adjusting_shelter_and_missile()
        shelter += self.infinity_round
        shelter += self.infinity_round
        enemy.initialize(shelter, missile)
        # 护盾破碎效果初始化
        damage_previewer.initialize(my_ship.shelter, enemy.shelter)
        # 轮次增加
        self.infinity_round += 1
        # 词条推进
        entry_manager.push_up()
        # 协议选择
        infinity_card_manager.choose_card()
        # 终焉结选择
        while 1:
            print()
            station_trees_manager.all_tree_list["终焉结信息"].inject({
            "total_al_rank": my_ship.total_al_rank,
            "ssg_tag": "",
            "ssg_num": "",
            "q_information": my_ship.al_list[0].len_name \
                if my_ship.al_list[0] \
                else "[No Info]",
            "w_information": my_ship.al_list[1].len_name \
                if my_ship.al_list[1] \
                else "[No Info]",
            "e_information": my_ship.al_list[2].len_name \
                if my_ship.al_list[2] \
                else "[No Info]"
            })
            station_trees_manager.all_tree_list["终焉结信息"].print_self()
            inp = input_plus("请输入您的准备操作| [q/w/e]更换终焉结| [enter]进入战斗")
            match inp:
                case "q"|"w"|"e":
                    al_manager.choose_al_with_limit(inp)
                case "":
                    break
                case _:
                    pass
        Txt.print_plus(f"轮次{self.infinity_round}>>准备开始>>")

    def infinity_mainloop(self):
        while 1:
            sounds_manager.switch_to_bgm("fight")
            while 1:
                # dawn
                if (rank := entry_manager.get_rank_of("11")) != 0:
                    dice.set_additional_di(rank * 0.1)
                who = dice.decide_who(force_advance=self.__get_force_advance())
                time.sleep(0.4)

                # morning
                for al in my_ship.al_list:
                    if al:
                        al.operate_in_morning()
                field_printer.print_basic_info(self.days)
                print(f"轮数>>{self.infinity_round}\n")
                entry_manager.print_all_flow_rank()
                field_printer.print_for_fight(my_ship, enemy)
                field_printer.generate_suggestion_tree().print_self()
                field_printer.print_key_prompt()

                # noon
                if who == Side.PLAYER:
                    Txt.print_plus("今天由我方行动")
                    my_ship.react()
                else:
                    Txt.print_plus("今天由敌方行动")
                    enemy.react()

                # afternoon
                for al in my_ship.al_list:
                    if al:
                        al.operate_in_afternoon()
                        if who == Side.PLAYER:
                            al.operate_in_our_turn()

                # dusk
                if (result := self.__is_over()) != 0:
                    break
                self.days += 1
            if result == 1:
                print()
                Txt.print_plus("=========我方胜利=========")
                print()
                sounds_manager.switch_to_bgm("win")
                Txt.print_plus(f"第{self.infinity_round}轮次|获胜>>\n")
                damage_previewer.show_total_dmg(my_ship.shelter, enemy.shelter)
                #storage_manager.drop_for_fight()
                des = input_plus("[enter]下一轮次| [0]回站")
                match des:
                    case "":
                        self.__initialize_between_infinity()
                    case "0":
                        return
                    case _:
                        return
            else:
                print()
                Txt.print_plus("=========敌方胜利=========")
                print()
                damage_previewer.show_total_dmg(my_ship.shelter, enemy.shelter)
                Txt.print_plus(f"最高挑战轮次{self.infinity_round}\n")
                storage_manager.set_value_of("max_infinity_round", self.infinity_round)
                input_plus("[enter]回站")
                return

    def initialize_before_ppve_server(self):
        # 服务器建立
        self.server = Server()
        entry_manager.set_server(self.server)
        self.server.connect()
        voices.set_server(self.server)
        # 终焉结选择
        another_ship.al_list = [al15,al14,al19]
        fast_choi = False##员工通道
        inp_position = 0
        fclist = [0,0,0]
        while 1:
            station_trees_manager.all_tree_list["终焉结信息"].inject({
            "total_al_rank": another_ship.total_al_rank,
            "ssg_tag": "",
            "ssg_num": "",
            "q_information": another_ship.al_list[0].len_name \
                if another_ship.al_list[0] \
                else "[No Info]",
            "w_information": another_ship.al_list[1].len_name \
                if another_ship.al_list[1] \
                else "[No Info]",
            "e_information": another_ship.al_list[2].len_name \
                if another_ship.al_list[2] \
                else "[No Info]"
            })
            station_trees_manager.all_tree_list["终焉结信息"].print_self()
            main_loops.server.send_tree(station_trees_manager.all_tree_list["终焉结信息"])
            if fast_choi:##员工通道
                inp_position += 1
                inp = "qwen"[inp_position]
            else:
                Txt.print_plus("请等待僚机指挥官确认操作<<<")
                inp = main_loops.server.ask("僚机指挥官请输入您的准备操作| [q/w/e]更换终焉结| [enter]进入战斗")
                if "]" in inp:
                    inp = inp[inp.find("]")+1:]
            if " " in inp and len(fclist := inp.split(" ")) == 3:
                fast_choi = True
                inp_position = 0
                inp = "q"
            match inp:
                case "q"|"w"|"e":
                    al_position = {"q": 0, "w": 1, "e": 2}[inp]
                    while 1:
                        al_list = [al for al in al_manager.all_al_list.values() if al.type == inp]
                        al_list.sort(key=lambda al: al.rank_num)
                        al_num = 0
                        al_info_list = [[],[],[],[],[]]
                        for al_temp in al_list:
                            if fast_choi:##员工通道
                                break
                            al_temp:Al_general
                            al_info_list[al_num % 5].append("")
                            al_info_list[al_num % 5].append(
                                f"[{al_temp.metadata['rank']}]{al_temp.short_name}#{al_temp.index}"+
                                ("<已被装备>" if al_temp in my_ship.al_list else "")+
                                ("<平台不符>" if (
                                        not al_temp in my_ship.al_list and al_temp.type == "e" and
                                        al_temp.platform != "通用" and al_temp.platform != another_ship.al_list[0].platform
                                ) else "")
                            )
                            al_num += 1
                        main_loops.server.send_long_str(Txt.n_column_generate(al_info_list,26))
                        # Al的选择
                        cn_type = {"q": "主武器", "w": "生存位", "e": "战术装备"}[inp]
                        while 1:
                            if fast_choi:##员工通道
                                index = fclist[al_position]
                            else:
                                index = main_loops.server.ask(
                                    f"\n指挥官，请输入数字选择本场战斗的{cn_type}|[-1] 不使用{cn_type}|[enter] 保留原有选择>>>")
                            if (index not in al_manager.al_meta_data or al_manager.al_meta_data[index]["type"] != inp or
                                    al_manager.all_al_list[index] == my_ship.al_list[al_position] or
                                    (al_manager.al_meta_data[index]["type"] == "e" and
                                    al_manager.all_al_list[index].platform != "通用" and
                                    al_manager.all_al_list[index].platform != another_ship.al_list[0].platform)):
                                fast_choi = False
                                if index == "":
                                    break
                                elif index == "-1":
                                    another_ship.al_list[al_position] = None
                                    break

                                print(f"请在{cn_type}库中进行选择")
                                main_loops.server.send_str(f"请在{cn_type}库中进行选择")
                            else:
                                Txt.print_plus(
                                    f"{al_manager.al_meta_data[index]['short_name']}#{al_manager.al_meta_data[index]['index']} 已确认装备")
                                main_loops.server.send_str(
                                    f"{al_manager.al_meta_data[index]['short_name']}#{al_manager.al_meta_data[index]['index']} 已确认装备\n")

                                another_ship.al_list[al_position] = al_manager.all_al_list[index]
                                print("")
                                break
                        if another_ship.al_list[al_position] != my_ship.al_list[al_position]:
                            break
                case "":
                    break
                case "n":
                    fast_choi = False
                case _:
                    print(f"请输入正确的指令|{inp}不正确")
                    pass
        another_ship.update_platform()
        for al in another_ship.al_list:
            if al:
                al.ship = another_ship
        # 舰船初始化
        my_ship.initialize()
        my_ship.life_for_ppve = 0
        another_ship.initialize()
        another_ship.life_for_ppve = 0
        shelter_from_me, missile_from_me = self.__get_adjusting_shelter_and_missile(my_ship)
        shelter_from_another, missile_from_another = self.__get_adjusting_shelter_and_missile(another_ship)
        enemy.initialize(
            shelter_from_me+shelter_from_another,
            missile_from_me+shelter_from_another
        )
        # 终焉结初始化
        al_manager.initialize_all_al()
        # 骰子初始化
        dice.set_probability(0.8)
        dice.set_di(0.3)
        dice.set_additional_di(0)
        # 自动驾驶初始化
        auto_pilot.refresh()
        # 护盾破碎效果初始化
        damage_previewer.initialize(my_ship.shelter, enemy.shelter)
        # 词条管理器初始化
        entry_manager.set_mode(Modes.PPVE)
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
            
    def ppve_server_mainloop(self):
        sounds_manager.switch_to_bgm("fight")
        while 1:
            # dawn
            time.sleep(0.4)
            who = dice.decide_who(force_advance=self.__get_force_advance())

            # morning
            for al in my_ship.al_list+another_ship.al_list:
                if al:
                    al.operate_in_morning()

            field_printer.print_basic_info(self.days)
            self.server.send_str(field_printer.generate_basic_info(self.days))

            entry_manager.print_all_selected_rank()
            field_printer.print_for_ppve(my_ship,another_ship,enemy)
            field_printer.print_suggestion_for_ppve()
            self.server.send_long_str(entry_manager.generate_str_of_all_selected_rank()+
                field_printer.generate_for_ppve(my_ship,another_ship,enemy)+
                field_printer.generate_suggestion_for_ppve()
            )

            # noon
            if who == 1:
                Txt.print_plus("今天由我方行动")
                self.server.send_str("今天由我方行动")
                field_printer.ppve_help_prompt()
                if not self.is_near_death(my_ship):
                    field_printer.print_key_prompt(my_ship)
                    self.server.send_str("正在等待长机指挥官操作<<<")
                    my_ship.react_for_ppve()
                    self.server.send_str("长机指挥官操作完毕>>>")
                if not self.is_near_death(another_ship):
                    Txt.print_plus("正在等待僚机指挥官操作<<<")
                    field_printer.print_key_prompt(another_ship)
                    another_ship.react_for_ppve(self.server)
                    Txt.print_plus("僚机指挥官操作完毕>>>")
            else:
                Txt.print_plus("今天由敌方行动")
                self.server.send_str("今天由敌方行动")
                enemy.react()

            # afternoon
            if entry_manager.get_rank_of("13") != 0 and self.days > 100 - 20 * entry_manager.get_rank_of("13"):
                enemy.attack(1)
                entry_manager.all_entries["13"].print_when_react()
            for al in my_ship.al_list+another_ship.al_list:
                if al:
                    al.operate_in_afternoon()
                    if who == 1:
                        al.operate_in_our_turn()

            # dusk
            if (result := self.is_over_for_ppve()) != 0:
                break

            #self.server.buffer_send()
            self.days += 1
        sounds_manager.stop_bgm()
        for al in another_ship.al_list:
            if al:
                al.ship = my_ship
        print()
        Txt.print_plus("=========我方胜利=========" if result == 1 else"=========敌方胜利=========")
        print()
        self.server.send_str("\n=========我方胜利=========\n" if result == 1 else"\n=========敌方胜利=========\n")
        #damage_previewer.show_total_dmg(my_ship.shelter, enemy.shelter)
        self.server.send_exit("作战已结束")
        self.server.close()
        self.server = None
        voices.clear_server()
        entry_manager.clear_server()
        input_plus("[enter]回站")
        return

    @staticmethod
    def ppve_client_mainloop():
        print("[终焉结快捷码（enter以快捷键入）]"+(" ".join([al.index for al in my_ship.al_list if al])))
        client = Client()
        try:
            client.connect()
        except IFAWL_ConnectionCancel:
            Txt.print_plus("连接已取消")
        else:
            client.start_main_loop()
        finally:
            client.close()

    @staticmethod
    def station_mainloop():
        sounds_manager.switch_to_bgm("station")
        while 1:
            print()
            station_trees_manager.inject_all()
            Txt.n_column_print(station_trees_manager.generate_all_line_list(), [50, 70])
            go_to = input(">>>")
            match go_to:
                case "z":
                    storage_manager.print_storage()
                case "x" | "p1":
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
                case "a2":
                    main_loops.al_tracing_mainloop()
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
            inp = Txt.input_plus("工业流程正常运转中·请输入要合成的终焉结编号·[enter]退出>>>")
            if inp == "":  # 退出
                Txt.print_plus("正在退出……")
                break
            if inp not in al_manager.all_al_list:  # 输入无效
                Txt.print_plus("请输入有效的终焉结编号")
                Txt.input_plus("")
                continue
            current_al = al_manager.all_al_list[inp]
            if not current_al.is_craftable:  # 资源不足
                Txt.print_plus("仓库资源不足·合成失败")
                Txt.input_plus("")
                continue
            current_al.craft_self()
            Txt.print_plus(f"{current_al.len_name}*1 合成完成·已送至终焉结仓库并铭刻您的代号")
            Txt.input_plus("")

    @staticmethod
    def al_tracing_mainloop():
        while 1:
            for al in al_manager.all_al_list.values():
                al.refresh_craftable_tag()
            assets = storage_manager.show_assets()
            for al in al_manager.all_al_list.values():
                al.print_recipe(assets)
            inp = Txt.input_plus("工业流程正常运转中·请输入要跟踪的终焉结编号·[-1]清除跟踪·[enter]退出>>>")
            if inp == "":  # 退出
                Txt.print_plus("正在退出……")
                break
            if inp == "-1":  # 清除跟踪
                storage_manager.clear_tracing_al()
                Txt.print_plus("跟踪已清除")
                Txt.input_plus("")
                break
            if inp not in al_manager.all_al_list:  # 输入无效
                Txt.print_plus("请输入有效的终焉结编号")
                Txt.input_plus("")
                continue
            current_al = al_manager.all_al_list[inp]
            storage_manager.set_tracing_al(inp)
            Txt.print_plus(f"{current_al.len_name} 已加入终焉结工业追踪器")
            Txt.input_plus("")
            break

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
        Txt.Tree(
            "准备起锚>>离站请求已被接受",
            "[0] 基本对战",
            "[1] 战死之地",
            "[2] 无尽模式",
            "[3/4] 联合狩猎",
            "[enter] 回站"
        ).print_self()
        Txt.n_column_print(
            [Txt.Tree(
                "[0] 基本对战",
                "与游荡的星际海盗进行一对一战斗",
                "启用仓库的终焉结·若失败则损毁",
                "战斗胜利后将获得赏金和物资奖励",
            ).generate_line_list()+
            Txt.Tree(
                "[1] 战死之地",
                "依据选定的词条匹配相应的高强度悬赏目标进行战斗",
                "启用仓库的终焉结·若失败则损毁",
                "战斗胜利后将获得赏金和物资奖励",
            ).generate_line_list(),
            Txt.Tree(
                "[2] 无尽模式",
                "在模拟器中与多波次敌人进行战斗",
                "不启用仓库的终焉结",
                "战斗结束后无奖励"
            ).generate_line_list(),
             Txt.Tree(
                 "[3] 联合狩猎[长机]",
                 "在模拟器中与另一位指挥官合作打击敌方",
                 "不启用仓库的终焉结",
                 "战斗结束后无奖励"
             ).generate_line_list()+
             Txt.Tree(
                 "[4] 联合狩猎[僚机]",
                 "在模拟器中与另一位指挥官合作打击敌方",
                 "不启用仓库的终焉结",
                 "战斗结束后无奖励"
             ).generate_line_list()
             ]
        )
        des = Txt.ask_plus("请输入目的地>>>", ["0", "1", "2", "3", "4", ""])
        return des


main_loops = MainLoops()

contract_manager = ContractManager(storage_manager, list(al_manager.all_al_list.keys()))
infinity_card_manager = CardManager(my_ship,enemy,entry_manager,al_manager)
plot_manager.set_storage_manager(storage_manager)
ocp_manager = OcpManager(my_ship, enemy, another_ship, main_loops)

def hello():
    sounds_manager.switch_to_bgm("login")
    Txt.print_plus(f"\n{__VERSION__} > 工程启动中 > \n")
    Txt.input_plus("按任意键开始游戏|输入后请回车>>>")


if __name__ == "__main__":
    hello()
    # 存储管理器登录
    storage_manager.login()
    # 剧情管理器初始化
    plot_manager.load_session()
    plot_manager.set_information_map({
        "username": storage_manager.username,
        "ship_name": storage_manager.get_value_of("ship_name")
    })
    plot_manager.try_to_play_when_login()
    # 舰船读取终焉结
    my_ship.load_al()
    # 词条管理器读取词条
    entry_manager.set_all_rank(storage_manager.get_entry_rank())
    # 主循环
    while 1:
        main_loops.station_mainloop()
        current_destination = main_loops.ask_destination()
        match current_destination:
            case "0":
                main_loops.initialize_before_fight()
                main_loops.fight_mainloop()
            case "1":
                main_loops.initialize_before_disaster()
                main_loops.disaster_mainloop()
            case "2":
                main_loops.initialize_before_infinity()
                main_loops.infinity_mainloop()
                my_ship.load_al()
            case "3":
                main_loops.initialize_before_ppve_server()
                main_loops.ppve_server_mainloop()
            case "4":
                main_loops.ppve_client_mainloop()
            case _:
                pass
