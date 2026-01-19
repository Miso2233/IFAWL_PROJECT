import random

from core.Module0_enums_exceptions import OSI, IFAWL_NoOcpError
from core.Module1_txt import print_plus
from core.Module2_json_loader import json_loader
from core.Module5_dice import dice
from core.Module14_communication import Server

ALL_OCP_METADATA = json_loader.load("ocps_metadata")


class OcpGeneral:

    def __init__(self, index: int, my_ship, enemy_ship, another_ship, main_loops):
        # 元数据字段
        self.index: str = str(index)
        self.metadata = ALL_OCP_METADATA[self.index]
        self.txt_list = self.metadata["txt_list"]
        # 战场字段
        self.state = [None, 0, 0, 0]
        self.my_ship = my_ship
        self.enemy_ship = enemy_ship
        self.another_ship = another_ship
        self.main_loops = main_loops
        # 通讯字段
        self.server: Server | None = None

    def initialize(self):
        self.state = [None, 0, 0, 0]

    def set_server(self, server: Server):
        self.server = server

    def clear_server(self):
        self.server = None

    def is_available(self) -> bool:
        """
        基于天数和冷却判断本事件是否处于空闲状态
        :return: 是否空闲
        """
        return self.state[OSI.DAYS_COUNTER] == 0 and self.state[OSI.COOLING] == 0

    def is_end(self) -> bool:
        """
        基于天数判断本事件是否已经结束
        :return: 是否结束
        """
        return self.state[OSI.DAYS_COUNTER] == 0

    def cool(self):
        """
        判断是否应该冷却并进行冷却
        :return: 无
        """
        if self.state[OSI.COOLING] < 0:
            self.state[OSI.COOLING] += 1

    def print_and_send(self, txt: str):
        print_plus(txt)
        if self.server:
            self.server.send_str(txt)

    def begin(self):
        """
        使时间开始，将日期计时器设置为与剧情等长
        :return: 无
        """
        self.state[OSI.DAYS_COUNTER] = len(self.txt_list)

    def print_plot(self):
        """
        依照日期计时器进行剧情播放
        :return: 无
        """
        txt_for_today = self.txt_list[len(self.txt_list) - self.state[OSI.DAYS_COUNTER]]
        self.print_and_send(txt_for_today)

    def operate_in_my_day(self):
        if self.state[OSI.DAYS_COUNTER] > 0:
            self.print_plot()
            self.state[OSI.DAYS_COUNTER] -= 1

    def operate_when_f(self, ship_calling):
        ...

    def operate_in_enemy_day(self):
        ...

    # 六大增减益

    def adjust_enemy_atk(self, atk: int) -> int:
        return atk

    def adjust_me_atk(self, atk: int) -> int:
        return atk

    def adjust_enemy_hp(self, hp: int) -> int:
        return hp

    def adjust_me_hp(self, hp: int) -> int:
        return hp

    def adjust_enemy_num(self, num: int) -> int:
        return num

    def adjust_me_num(self, num: int) -> int:
        return num


class Ocp1(OcpGeneral):

    def operate_when_f(self, ship_calling):
        ship_calling.heal(2)
        self.state[OSI.COOLING] = -3
        self.state[OSI.DAYS_COUNTER] = 0
        self.print_and_send(f"[事件]护盾已回充，旅人正在离开舰船>[迷途旅人]事件结束")

class Ocp2(OcpGeneral):

    def adjust_enemy_atk(self, atk: int) -> int:
        if self.state[OSI.DAYS_COUNTER] > 0:
            return atk * 2
        return atk


class OcpManager:

    def __init__(self, my_ship, enemy_ship, another_ship, main_loops):
        # 战场字段
        self.my_ship = my_ship
        self.enemy_ship = enemy_ship
        self.another_ship = another_ship
        self.current_ocp: OcpGeneral | None = None
        self.main_loops = main_loops
        # 通讯字段
        self.server: Server | None = None
        # 事件字典
        self.ocp_list = {}
        for class_name, Ocp in globals().items():
            if class_name.startswith("Ocp") and class_name != "OcpGeneral" and class_name != "OcpManager":
                self.ocp_list[class_name[3:]] = Ocp(int(class_name[3:]), my_ship, enemy_ship, another_ship, main_loops)

    def initialize(self):
        for ocp in self.ocp_list.values():
            ocp.initialize()

    def set_server(self, server: Server):
        self.server = server
        for ocp in self.ocp_list.values():
            ocp.set_server(server)

    def clear_server(self):
        self.server = None
        for ocp in self.ocp_list.values():
            ocp.clear_server()

    def try_begin_new_ocp(self, probability: float = 0.9):
        """
        at dawn
        审视每个ocp的available()状态，并随机启动一个空闲的
        :param probability: 事件生成概率
        :return: 无
        """
        if self.current_ocp:
            return
        if not dice.probability(probability):
            return
        available_list = [ocp for ocp in self.ocp_list.values() if ocp.is_available()]
        if not available_list:
            return
        new_ocp = random.choice(available_list)
        self.current_ocp = new_ocp
        self.current_ocp.begin()

    def try_end_old_ocp(self):
        """
        at dusk
        审视当前ocp的end()状态，若已结束则将之清除
        :return: 无
        """
        if not self.current_ocp:
            return
        if self.current_ocp.is_end():
            self.current_ocp = None

    def cool_ocp(self):
        """
        at dusk
        对所有事件进行一次冷却
        :return: 无
        """
        for ocp in self.ocp_list.values():
            ocp.cool()

    def generate_current_ocp_prompt(self) -> str:
        """
        生成ocp提示
        :return: 若有事件，返回f"当前事件>>{self.current_ocp.metadata['title']}\n"，否则返回空闲
        """
        if self.current_ocp:
            return f"当前事件>>{self.current_ocp.metadata['title']}\n"
        else:
            return "当前事件>>[空闲]\n"

    def operate_in_my_day(self):
        if self.current_ocp:
            self.current_ocp.operate_in_my_day()

    def operate_in_enemy_day(self):
        if self.current_ocp:
            self.current_ocp.operate_in_enemy_day()

    def operate_when_f(self, ship_calling):
        if self.current_ocp:
            self.current_ocp.operate_when_f(ship_calling)
        else:
            raise IFAWL_NoOcpError

    def adjust_enemy_atk(self, atk: int) -> int:
        """调整敌方攻击力"""
        if self.current_ocp:
            return self.current_ocp.adjust_enemy_atk(atk)
        return atk

    def adjust_me_atk(self, atk: int) -> int:
        """调整我方攻击力"""
        if self.current_ocp:
            return self.current_ocp.adjust_me_atk(atk)
        return atk

    def adjust_enemy_hp(self, hp: int) -> int:
        """调整敌方治疗量"""
        if self.current_ocp:
            return self.current_ocp.adjust_enemy_hp(hp)
        return hp

    def adjust_me_hp(self, hp: int) -> int:
        """调整我方治疗量"""
        if self.current_ocp:
            return self.current_ocp.adjust_me_hp(hp)
        return hp

    def adjust_enemy_num(self, num: int) -> int:
        """调整敌方上弹量"""
        if self.current_ocp:
            return self.current_ocp.adjust_enemy_num(num)
        return num

    def adjust_me_num(self, num: int) -> int:
        """调整我方上弹量"""
        if self.current_ocp:
            return self.current_ocp.adjust_me_num(num)
        return num
