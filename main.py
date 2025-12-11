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
from modules.Module6_market_manager import Contract_manager, Contract

contract_manager = Contract_manager(storage_manager)

DMG_TYPE_LIST: dict[int, str] = {
    0: "missile_launch",  # 导弹射击
    1: "particle_cannon_shooting",  # 粒子炮射击
    2: "enemy_missile_boom",  # 敌方导弹殉爆
    3: "ordinary_attack"  # 杂项攻击
}


class MyShip:

    def __init__(self):
        self.shelter = 0
        self.missile = 0
        self.al_list: list[Al_general | None] = [None, None, None]
        self.total_al_rank = 0

    def load_al(self):
        al_str_list = storage_manager.get_al_on_ship()
        for position in range(len(al_str_list)):
            self.al_list[position] = al_manager.all_al_list.get(al_str_list[position], None)
        self.total_al_rank = al_manager.get_total_al_rank()

    def update_total_al_rank(self):
        self.total_al_rank = 0
        for al in self.al_list:
            try:
                self.total_al_rank += al.rank_num
            except AttributeError:
                pass

    def print_self(self):
        for _ in range(self.shelter):
            print("-----")
        for _ in range(self.missile):
            print("[]", end="")
        print()

    def initialize(self):
        self.missile = 1
        self.shelter = 1
        for al in al_manager.all_al_list.values():
            try:
                al.initialize()
            except AttributeError:
                pass

    def attack(self, atk: int, type: str):
        """
        根据原始伤害进行加减并对目标造成攻击
        :param atk: 原始伤害
        :param type: 伤害种类
        :return: 无
        """
        for al in self.al_list:
            try:
                atk = al.add_atk(atk, type)
            except AttributeError:
                pass
        enemy.shelter -= atk

    def heal(self, hp: int):
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
        operation = input(">>>")
        if self.missile < 1 and operation == "1":
            operation = "0"
        if self.al_list[1] == al18 and operation == "2":
            operation = "w"
        if al12.state != 0 and operation != "q":
            al12.attack()
        if al15.state != 0 and operation == "1":
            voices.report("暴雨", "常规发射器离线")
            operation = ""
        if al16.state != 0 and operation == "2":
            al16.heal()
        match operation:
            case "0" | " ":
                self.load(1)
                voices.report("导弹", "上弹")
            case "1":
                self.attack(1, DMG_TYPE_LIST[0])
                self.load(-1)
                voices.report("导弹", "发射")
            case "2":
                self.heal(1)
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
            case _:
                Txt.print_plus("你跳过了这一天！")


my_ship = MyShip()


class EnemyShip:
    def __init__(self):
        self.shelter = 0
        self.missile = 0

    def print_self(self):
        for _ in range(self.missile):
            print("[]", end="")
        print()
        for _ in range(self.shelter):
            print("-----")

    def attack(self, atk: int):
        """
        根据原始伤害进行加减并对目标造成攻击
        :param atk: 原始伤害
        :return: 无
        """
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
        else:
            voices.report("护盾", "受重击")

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
        self.missile += num
        if num > 0:
            voices.report("战场播报", "敌上弹", False)

    def initialize(self):
        self.missile = 2
        self.shelter = 2

    def react(self):
        operation = random.choice(["0", "1", "2"])
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
        self.al_meta_data: dict[str, dict[str, str | int]] = json_loader.load("al_meta_data")
        self.all_al_list: dict[str, Al_general] = {}
        # TODO 添加my_ship和enemy_ship字段并抽离所有的AL

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
                print(f"{self.al_meta_data[inp]['short_name']}#{self.al_meta_data[inp]['index']}", "已确认装备")
                my_ship.al_list[al_position] = self.all_al_list[inp]
                print("")
                time.sleep(0.4)
                break
        storage_manager.save_al_on_ship(my_ship.al_list)
        my_ship.update_total_al_rank()

    def clear_al(self):
        for index in range(len(my_ship.al_list)):
            if my_ship.al_list[index] is None:
                continue
            if my_ship.al_list[index].rank_num == 0:
                continue
            my_ship.al_list[index] = None
        storage_manager.save_al_on_ship(my_ship.al_list)
        my_ship.update_total_al_rank()

    def get_total_al_rank(self):
        out = 0
        for al in my_ship.al_list:
            try:
                out += al.rank_num
            except AttributeError:
                pass
        return out


al_manager = Al_manager()


class Al_general:
    # Apocalypse-Linked 终焉结套件

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
        print(f">>>>\"{self.short_name}\"")
        print(self.metadata["description_txt"])
        # [30] 岩河军工“湾区铃兰”饱和式蜂巢突击粒子炮      [粒子炮平台] [VIII] 1在仓库 >>[可以离站使用]<<
        print()

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

    def print_self(self):
        if self.state != 0:
            try:
                print(self.skin_list[self.state])
                print()
            except IndexError:
                pass

    def suggest(self) -> str | None:
        return None

    def operate_in_our_turn(self):
        pass


class Al3(Al_general):

    def react(self):
        if dice.probability(0.3 * enemy.shelter):
            my_ship.attack(1, DMG_TYPE_LIST[3])
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
                my_ship.attack(2, DMG_TYPE_LIST[0])
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
                my_ship.attack(1, DMG_TYPE_LIST[2])
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
        if type != "missile_launch":
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
            my_ship.missile += 2
            self.report("牺牲护盾")
        elif my_ship.shelter <= 1:
            if my_ship.missile != 0:
                my_ship.heal(2)
                my_ship.missile -= 1
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
            my_ship.attack(1, DMG_TYPE_LIST[3])
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
            my_ship.attack(self.atk_list[self.state], DMG_TYPE_LIST[1])
            # p_c_manager.boom_now()
            self.state = 0
            self.report("过热")

    def attack(self):
        if self.atk_list[self.state] != 0:
            my_ship.attack(self.atk_list[self.state], DMG_TYPE_LIST[1])
            # p_c_manager.boom_now()
            self.state = 0
            self.report("攻击")
        elif self.atk_list[self.state] == 0:
            self.state = 0
            self.report("晴空粒子炮充能失效·集群阵列回收中")
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
            my_ship.attack(1, DMG_TYPE_LIST[0])
            self.report("单导弹导航")
        else:
            my_ship.missile -= 2
            my_ship.attack(2, DMG_TYPE_LIST[0])
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
                    my_ship.attack(1, DMG_TYPE_LIST[0])
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
    cure_list = [0, 4, 6, 8, 10]

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
            my_ship.attack(2, DMG_TYPE_LIST[0])
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


class Al30(Al_general):

    def react(self):
        if self.state == 0:
            my_ship.attack(2, DMG_TYPE_LIST[1])
            self.state -= 5
            self.report("正常攻击")
            # p_c_manager.boom_now()
        else:
            enemy.attack(2)
            voices.report("护盾", "湾区铃兰导致扣血")
            self.report("牺牲护盾发射")
            my_ship.attack(2, DMG_TYPE_LIST[1])
            # p_c_manager.boom_now()

    def add_atk(self, atk: int, type: str) -> int:
        if self.state < 0 < my_ship.missile and dice.probability(0.8):
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


class FieldPrinter:

    def print_for_fight(self, me: MyShip, opposite: EnemyShip):
        """
        打印fight模式下双方护盾和导弹，以及我方Al
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

    def print_suggestion(self):
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

    def print_key_prompt(self):
        key_prompt = "0/space 装弹  1 发射  2 上盾  "
        for al in my_ship.al_list:
            try:
                key_prompt += f"{al.type} {al.short_name}#{al.index}  "
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
        self.days = 0

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

    def initialize_before_fight(self):
        my_ship.initialize()
        enemy.initialize()
        self.days = 1

    def fight_mainloop(self):
        while 1:
            # dawn
            time.sleep(0.4)
            field_printer.print_basic_info(self.days)
            field_printer.print_for_fight(my_ship, enemy)
            field_printer.print_suggestion()
            field_printer.print_key_prompt()

            # morning
            for al in my_ship.al_list:
                if al:
                    al.operate_in_morning()

            # noon
            who = dice.decide_who()
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
                if result == 1:
                    Txt.print_plus("我方胜利")
                    storage_manager.drop_for_fight()
                else:
                    Txt.print_plus("敌方胜利")
                    storage_manager.destroy_al(my_ship.al_list)
                    al_manager.clear_al()
                input_plus("[enter]回站")
                return
            self.days += 1

    @staticmethod
    def station_mainloop():
        while 1:
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
                case _:
                    pass

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


main_loops = MainLoops()

if __name__ == "__main__":
    storage_manager.login()
    my_ship.load_al()
    while 1:
        main_loops.station_mainloop()

        main_loops.initialize_before_fight()
        main_loops.fight_mainloop()
