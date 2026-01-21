import random

from core.Module0_enums_exceptions import OSI, IFAWL_NoOcpError, DamageType
from core.Module1_txt import print_plus
from core.Module2_json_loader import json_loader
from core.Module5_dice import dice
from core.Module14_communication import Server

OCP_PROBABILITY_FOR_EACH_DAY = 0.2

ALL_OCP_METADATA = json_loader.load("ocps_metadata")

"""
OCP事件对象的生命周期如下
在被ocp_manager.try_begin_new_ocp()选中后，
    ocp_manager会调用其begin()方法，将日期计时器设置为与剧情等长
    同时，ocp_manager.current_ocp将被设置为此事件
    ocp_manager封装的六大增益会检测到当前事件并调用增益方法
    ocp_manager.operate_when_f()函数可用
事件进行的过程中，
    ocp.operate_in_my_day()会开始播放剧情
    当剧情播放完毕，ocp.end()将触发，使事件进入冷却
    若重写了OcpGeneral.operate_in_my_day()方法，请确保end()最终被调用
end()被调用后，事件的日期计时器将被设为0
    当天黄昏，ocp_manager.try_end_old_ocp()会发现current_ocp的日期计时器为0
    并清除该事件
"""

class OcpGeneral:

    def __init__(self, index: int, my_ship, enemy_ship, another_ship, main_loops):
        # 元数据字段
        self.index: str = str(index)
        self.metadata = ALL_OCP_METADATA[self.index]
        self.txt_list = self.metadata["txt_list"]
        self.min_day = self.metadata["min_day"]
        self.weight = self.metadata["weight"]
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
        基于天数、战场天数和冷却判断本事件是否处于空闲状态
        :return: 是否空闲
        """
        return self.state[OSI.DAYS_COUNTER] == 0 \
            and self.state[OSI.COOLING] == 0 \
            and self.main_loops.days >= self.min_day

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
        """
        打印并发送（如server属性不为None）文本
        :param txt: 文本
        :return:
        """
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
        if self.state[OSI.DAYS_COUNTER] <= 0: # 防御性语句 理论上不会出现这种情况 Miso 26.1.21
            return
        self.print_plot()
        self.state[OSI.DAYS_COUNTER] -= 1
        if self.state[OSI.DAYS_COUNTER] == 0:
            self.end()

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

    def end(self):
        """
        使事件结束并进入冷却
        :return: 无
        """
        self.state[OSI.COOLING] = self.metadata["cooling"]
        self.state[OSI.DAYS_COUNTER] = 0

    def print_when_end(self):
        self.print_and_send(f"[事件]{self.metadata['end_txt']}>[{self.metadata['title']}]事件结束")

class Ocp1(OcpGeneral):

    def operate_when_f(self, ship_calling):
        ship_calling.heal(2)
        self.end()

class Ocp2(OcpGeneral):

    def adjust_enemy_atk(self, atk: int) -> int:
        return atk + 1

class Ocp3(OcpGeneral):

    def operate_in_my_day(self):
        if self.state[OSI.DAYS_COUNTER] == 2:
            self.print_plot()
            self.state[OSI.DAYS_COUNTER] -= 1
            return
        if self.state[OSI.DAYS_COUNTER] == 1:
            self.print_plot()
            self.enemy_ship.attack(3)
            self.end()

class Ocp4(OcpGeneral):

    def adjust_me_hp(self, hp: int) -> int:
        return hp + 1

class Ocp5(OcpGeneral):

    def operate_in_my_day(self):
        if self.state[OSI.DAYS_COUNTER] <= 0:
            return
        self.print_plot()
        self.my_ship.attack(1,DamageType.ORDINARY_ATTACK)
        self.enemy_ship.attack(1)
        self.state[OSI.DAYS_COUNTER] -= 1
        if self.state[OSI.DAYS_COUNTER] == 0:
            self.end()

class Ocp6(OcpGeneral):

    def operate_in_my_day(self):
        if self.state[OSI.DAYS_COUNTER] <= 0:
            return
        self.print_plot()
        heal = random.randint(1,3)
        load = random.randint(1,3)
        self.print_and_send(f"我们发现了{heal}个护盾回充器和{load}组弹药")
        self.my_ship.heal(heal)
        self.my_ship.load(load)
        self.state[OSI.DAYS_COUNTER] -= 1
        if self.state[OSI.DAYS_COUNTER] == 0:
            self.end()

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

    def try_begin_new_ocp(self, probability: float = OCP_PROBABILITY_FOR_EACH_DAY):
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
        weight_list = [ocp.weight for ocp in available_list]
        new_ocp = random.choices(
            available_list,
            weights=weight_list,
            k=1
        )[0]
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
            self.current_ocp.print_when_end()
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
