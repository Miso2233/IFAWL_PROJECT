from __future__ import annotations

from typing import Literal

from core.Module1_txt import print_plus, n_column_print, input_plus, Tree

import random
import time

# 所有产物和原材料字典
ALL_MATERIALS = {
    "凡晶石原矿": 0,
    "灼烧岩原矿": 0,
    "长流石原矿": 0,
    "冰晶砂原矿": 0,
    "精炼凡晶石": 0,
    "精炼灼烧岩": 0,
    "精炼长流石": 0,
    "凡晶石粉末": 0,
    "灼烧岩粉末": 0,
    "长流石粉末": 0,
    "冰晶砂粉末": 0,
    "研磨凡晶石粉末": 0,
    "研磨灼烧岩粉末": 0,
    "烧结凡晶石": 0,
    "二次烧结凡晶石": 0,
    "烧结灼烧岩": 0,
    "终焉结原件I": 0,
    "终焉结原件II": 0,
    "终焉结原件III": 0
}


class Recipe:
    def __init__(self, name:str, inputs:dict[str,int|float], outputs:dict[str,int|float]):
        self.name = name
        self.inputs = inputs
        self.outputs = outputs

class Machine: # TODO 自动推导配方

    def __init__(self, index):
        self.machine_type = ""
        self.id = index
        self.recipes = []

        self.input_machines:list[Machine] = []
        self.output_machines:list[Machine] = []
        self.current_recipe:Recipe|None = None
        self.current_effectiveness:float = 0
        self.depth = 0

    def __eq__(self, other):
        return self.machine_type == other.machine_type and self.id == other.id

    def add_input_machine(self, machine:Machine):
        """
        为机器添加输入
        自动更新机器工作效率
        :param machine: 目标机器
        :return: 无
        """
        self.input_machines.append(machine)
        self.update_effectiveness()
        self.update_depth()

    def remove_input_machine(self, machine:Machine):
        """
        为机器移除输入
        自动更新机器工作效率
        :param machine: 目标机器
        :return: 无
        """
        self.input_machines.remove(machine)
        self.update_effectiveness()
        self.update_depth()

    def switch_output_machine(self, machine:Machine):
        self.output_machines.clear()
        self.output_machines.append(machine)

    def clear_output_machine(self):
        self.output_machines.clear()

    def set_recipe(self, recipe_index:int):
        """
        设置配方|代码非法则抛出IndexError
        :param recipe_index: 配方代码
        :return:
        """
        self.current_recipe = self.recipes[recipe_index]
        self.update_effectiveness()

    def print_info(self):
        print(f"机器: {self.machine_type}#{self.id}")
        print(f"当前配方: {self.current_recipe.name if self.current_recipe else '无'}")
        if self.current_recipe:
            print(f"预期输入: {self.current_recipe.inputs}")
        else:
            print(f"预期输入: 无")
        print(f"当前输入从: {[f'{machine.machine_type}#{machine.id}' for machine in self.input_machines]}")
        if self.input_machines:
            input_dict = {}
            for machine in self.input_machines:
                effectiveness = machine.current_effectiveness
                for item, amount in machine.current_recipe.outputs.items():
                    if item in input_dict:
                        input_dict[item] += amount * effectiveness
                    else:
                        input_dict[item] = amount * effectiveness
            print(f"当前输入: {input_dict}")
        print(f"当前输出到: {[f'{machine.machine_type}#{machine.id}' for machine in self.output_machines]}")
        print(f"当前主工作效率{self.current_effectiveness}")
        print(f"当前深度{self.depth}")
        print()

    def generate_info(self) -> list[str]:
        # 当前配方
        info = [
            f"=========================",
            f"{self.machine_type}#{self.id}",
            f"当前配方: {self.current_recipe.name if self.current_recipe else '无'}"
        ]
        # 预期输入
        if self.current_recipe:
            info.append("预期输入: {")
            for k, v in self.current_recipe.inputs.items():
                info.append(f"  {k}: {v},")
            info.append("}")
        else:
            info.append(f"预期输入: 无")
        # 当前输入
        if self.input_machines:
            info.append("当前输入从: [")
            for machine in self.input_machines:
                info.append(f"  {machine.machine_type}#{machine.id},")
            info.append("]")
        else:
            info.append("当前输入从: [无]")
        if self.input_machines:
            input_dict = {}
            for machine in self.input_machines: # 累加各输入机器
                effectiveness = machine.current_effectiveness
                if not machine.current_recipe:
                    continue
                for item, amount in machine.current_recipe.outputs.items():
                    if item in input_dict:
                        input_dict[item] += amount * effectiveness
                    else:
                        input_dict[item] = amount * effectiveness
            info.append("当前输入: {")
            for k, v in input_dict.items():
                info.append(f"  {k}: {v},")
            info.append("}")
        else:
            info.append("当前输入: [无]")
        # 当前输出
        if self.output_machines:
            info.append(f"当前输出到>{self.output_machines[0].machine_type}#{self.output_machines[0].id}")
        else:
            info.append("当前输出到>[无]")
        # 当前工作效率
        info.append(f"当前工作效率{self.current_effectiveness}")
        info.append(f"=========================")
        return info

    def show_recipe(self):
        print(f"{self.machine_type}#{self.id}的配方>>")
        for recipe_index in range(len(self.recipes)):
            print(f"[{recipe_index}]>>>{self.recipes[recipe_index].name}")
            print(f"  输入: {self.recipes[recipe_index].inputs}")
            print(f"  输出: {self.recipes[recipe_index].outputs}")



    def calculate_effectiveness(self) -> float:
        """
        计算该机器的有效生产效率
        遍历每一个原材料，找到不满足要求的比例最小者
        该生产效率将决定物资消耗速率和
        :return: 0到1的浮点数，代表生产效率
        """
        if not self.current_recipe:
            return 0
        input_items = {}
        for machine in self.input_machines:
            if not machine.current_recipe:
                continue
            for item, amount in machine.current_recipe.outputs.items():
                if item in input_items:
                    input_items[item] += amount * machine.calculate_effectiveness()
                else:
                    input_items[item] = amount * machine.calculate_effectiveness()
        min_effectiveness = 1
        for item, required_amount in self.current_recipe.inputs.items():
            provided_amount = input_items.get(item, 0)
            item_effectiveness = provided_amount / required_amount
            if item_effectiveness < min_effectiveness:
                min_effectiveness = item_effectiveness
        return min_effectiveness

    def update_effectiveness(self):
        """
        维护式更新current_effectiveness
        :return: 无
        """
        self.current_effectiveness = self.calculate_effectiveness()

    def calculate_depth(self) -> int:
        """
        计算该机器的深度
        :return: 深度，以矿机为0 | 无输入机器深度为0
        """
        if not self.input_machines:
            return 0
        return max(machine.calculate_depth() for machine in self.input_machines) + 1

    def update_depth(self):
        """
        维护式更新depth，并递归更新所有下游机器的depth
        :return: 无
        """
        self.depth = self.calculate_depth()
        # 递归更新所有下游机器的depth
        if self.output_machines:
            for output_machine in self.output_machines:
                output_machine.update_depth()

class Furnace(Machine):
    def __init__(self, index):
        super().__init__(index)
        self.machine_type = "精炼炉"
        self.recipes = [
            Recipe(
                name="精炼凡晶石",
                inputs={"凡晶石原矿": 1},
                outputs={"精炼凡晶石": 1}
            ),
            Recipe(
                name="精炼灼烧岩",
                inputs={"灼烧岩原矿": 1},
                outputs={"精炼灼烧岩": 1}
            ),
            Recipe(
                name="精炼长流石",
                inputs={"长流石原矿": 1},
                outputs={"精炼长流石": 1}
            ),
            Recipe(
                name="烧结凡晶石",
                inputs={"研磨凡晶石粉末": 1},
                outputs={"烧结凡晶石": 1}
            ),
            Recipe(
                name="二次烧结凡晶石",
                inputs={"烧结凡晶石": 1},
                outputs={"二次烧结凡晶石": 1}
            ),
            Recipe(
                name="烧结灼烧岩",
                inputs={"研磨灼烧岩粉末": 1},
                outputs={"烧结灼烧岩": 1}
            )
        ]

class Crusher(Machine):
    def __init__(self, index):
        super().__init__(index)
        self.machine_type = "粉碎机"
        self.recipes = [
            Recipe(
                name="凡晶石粉末",
                inputs={"凡晶石原矿": 1},
                outputs={"凡晶石粉末": 1}
            ),
            Recipe(
                name="冰晶砂粉末",
                inputs={"冰晶砂原矿": 1},
                outputs={"冰晶砂粉末": 3}
            ),
            Recipe(
                name="灼烧岩粉末",
                inputs={"精炼灼烧岩": 1},
                outputs={"灼烧岩粉末": 1}
            ),
            Recipe(
                name="长流石粉末",
                inputs={"精炼长流石": 1},
                outputs={"长流石粉末": 1}
            )
        ]

class Grinder(Machine):
    def __init__(self, index):
        super().__init__(index)
        self.machine_type = "研磨机"
        self.recipes = [
            Recipe(
                name="研磨凡晶石粉末",
                inputs={
                    "凡晶石粉末": 2,
                    "冰晶砂粉末": 1
                },
                outputs={
                    "研磨凡晶石粉末": 1
                }
            ),
            Recipe(
                name="研磨灼烧岩粉末",
                inputs={
                    "灼烧岩粉末": 2,
                    "冰晶砂粉末": 1
                },
                outputs={
                    "研磨灼烧岩粉末": 1
                }
            ),
        ]

class EquipmentMachine(Machine):
    def __init__(self, index):
        super().__init__(index)
        self.machine_type = "设备原件机"
        self.recipes = [
            Recipe(
                name="终焉结原件I",
                inputs={
                    "精炼凡晶石": 1,
                    "精炼灼烧岩": 1,
                },
                outputs={
                    "终焉结原件I": 0.2
                }
            ),
            Recipe(
                name="终焉结原件II",
                inputs={
                    "精炼凡晶石": 2,
                    "精炼长流石": 2,
                },
                outputs={
                    "终焉结原件II": 0.2
                }
            ),
            Recipe(
                name="终焉结原件III",
                inputs={
                    "二次烧结凡晶石": 2,
                    "烧结灼烧岩": 2,
                },
                outputs={
                    "终焉结原件III": 0.2
                }
            )
        ]

class MiningMachine(Machine):

    def __init__(self, index):
        super().__init__(index)
        self.machine_type = "矿机"
        self.recipes = [
            Recipe(
                name="凡晶石原矿",
                inputs={},
                outputs={
                    "凡晶石原矿": 1
                }
            ),
            Recipe(
                name="灼烧岩原矿",
                inputs={},
                outputs={
                    "灼烧岩原矿": 1
                }
            ),
            Recipe(
                name="长流石原矿",
                inputs={},
                outputs={
                    "长流石原矿": 1
                }
            ),
            Recipe(
                name="冰晶砂原矿",
                inputs={},
                outputs={
                    "冰晶砂原矿": 1
                }
            )
        ]
        self.depth = 0
        self.effectiveness = 1.0

    def calculate_effectiveness(self) -> float:
        return 1.0

    def calculate_depth(self) -> int:
        return 0

    def generate_info(self) -> list[str]:
        # 当前配方
        info = [
            f"=========================",
            f"{self.machine_type}#{self.id}",
            f"当前产出: {self.current_recipe.name if self.current_recipe else '无'}"
        ]
        # 当前输出
        if self.output_machines:
            info.append(f"当前输出到>{self.output_machines[0].machine_type}#{self.output_machines[0].id}")
        else:
            info.append("当前输出到>[无]")
        # 当前工作效率
        info.append(f"当前工作效率{self.current_effectiveness}")
        info.append(f"=========================")
        return info

class IndustryManager:

    def __init__(self):
        self.all_machines:dict[str,Machine] = {}

    def clear_all_machines(self):
        """
        清空所有机器
        :return: 无
        """
        self.all_machines.clear()

    def create_new_machine(self, machine_type:str) -> Machine|None:
        """
        新建一台机器并将其输入输出置空，并返回其指针
        :param machine_type: 机器种类|中文
        :return: 指向新机器的指针
        """
        if len(self.all_machines) >= 100:
            print_plus("机器数量已满")
            return None
        new_index:int = 0
        while str(new_index) in self.all_machines:
            new_index = random.randint(0,99)
        match machine_type:
            case "精炼炉":
                new_machine = Furnace(str(new_index))
            case "粉碎机":
                new_machine = Crusher(str(new_index))
            case "研磨机":
                new_machine = Grinder(str(new_index))
            case "设备原件机":
                new_machine = EquipmentMachine(str(new_index))
            case "矿机":
                new_machine = MiningMachine(str(new_index))
            case _:
                raise ValueError(f"Unknown machine type: {machine_type}")
        self.all_machines[new_machine.id] = new_machine
        return new_machine



    def delete_machine(self, index):
        if index not in self.all_machines:
            print_plus("机器不存在")
            return
        machine = self.all_machines[index]
        if machine.input_machines:
            print_plus(f"{machine.machine_type}#{index}正在接受以下机器的输出：")
            for input_machine in machine.input_machines:
                print_plus(f"  {input_machine.machine_type}#{input_machine.id}")
                input_machine.clear_output_machine()
        if machine.output_machines:
            print_plus(f"{machine.machine_type}#{index}正在向以下机器提供输出：")
            for output_machine in machine.output_machines:
                print_plus(f"  {output_machine.machine_type}#{output_machine.id}")
                output_machine.remove_input_machine(machine)
                output_machine.update_depth()
        print_plus(f"{machine.machine_type}#{index}断线完毕")
        print_plus(f"删除了机器{machine.machine_type}#{index}")
        self.all_machines.pop(index)

    def connect_machines(self, from_index:str, to_index:str):
        """
        将from向后连接到to
        自动处理from的老输出
        自动反制父辈以上成环
        :param from_index: from的号码
        :param to_index: to的号码
        :return: 无
        """
        from_machine = self.all_machines[from_index]
        to_machine = self.all_machines[to_index]
        if to_machine in from_machine.output_machines:
            print_plus(f"连接机器时错误-重复操作-{from_machine.machine_type}#{from_index}已经正在输出到{to_machine.machine_type}#{to_index}")
            return
        if from_machine == to_machine:
            print_plus(f"连接机器时错误-自成环-正在尝试将机器与自身连接")
            return
        current = to_machine
        while current:
            if current == from_machine:
                print_plus(f"连接机器时错误-成环- 起点 {from_machine.machine_type}#{from_index}正在作为 终点 {to_machine.machine_type}#{to_index}的间接输出")
                return
            current = current.output_machines[0] if current.output_machines else None
        if from_machine.output_machines: # 清除老连接
            origin_to = from_machine.output_machines[0]
            origin_to.remove_input_machine(from_machine)
            origin_to.update_depth()
        from_machine.switch_output_machine(to_machine)
        to_machine.add_input_machine(from_machine)

    def print_all_info(self):
        if not self.all_machines:
            print("=========场上无机器=========")
            return
        max_depth = max([machine.depth for machine in self.all_machines.values()])
        for current_depth in range(0,max_depth+1,5):
            columns = [[] for _ in range(5)]
            for machine in self.all_machines.values():
                try:
                    columns[machine.depth-current_depth] += machine.generate_info()
                except IndexError:
                    pass
            for i in range(5):
                if columns[i]:
                    columns[i].insert(0,f"第 {current_depth+i} 层机器")
            n_column_print(columns,30)

    @staticmethod
    def __extract_number(txt:str) -> list[str]:
        tokens = txt.split(" ")
        numbers = []
        for token in tokens:
            if token.isdigit():
                numbers.append(token)
        return numbers

    def mainloop(self):
        while 1:
            print("\n\n")
            self.print_all_info()
            Tree(
                "行星际工业指令集",
                "新建 矿机|精炼炉|粉碎机|研磨机|设备原件机",
                "删除 x",
                "连接 x y",
                "延接 精炼炉|粉碎机|研磨机|设备原件机 从 x"
                "调整 x",
                "退出"
            )
            do_what = input_plus("请输入操作>>>")
            args = self.__extract_number(do_what)
            if "删除" in do_what:
                for arg in args:
                    self.delete_machine(arg)
                    continue
            if "连接" in do_what:
                if len(args) != 2:
                    print_plus(f"参数错误-连接命令需2个参数-收到{len(args)}个")
                    continue
                try:
                    self.connect_machines(args[0],args[1])
                except KeyError as e:
                    print_plus(f"参数错误-机器{e}不存在")
                continue
            if "退出" in do_what:
                break
            if "新建" in do_what:
                new_types_cn = do_what.split(" ")[1:]
                if not new_types_cn:
                    print_plus("参数错误-新建命令需提供机器类型")
                    continue
                for machine_type_cn in new_types_cn:
                    try:
                        self.create_new_machine(machine_type_cn)
                    except ValueError:
                        print_plus(f"机器类型 {machine_type_cn} 不存在")
                continue
            if "延接" in do_what:
                if len(args) != 1:
                    print_plus(f"参数错误-延接命令需1个参数-收到{len(args)}个")
                if len(do_what.split(" ")) <= 1:
                    print_plus("参数错误-延接命令需提供机器类型")
                    continue
                new_type_cn = do_what.split(" ")[1]
                if args[0] not in self.all_machines:
                    print_plus(f"参数错误-机器{args[0]}不存在")
                    continue
                try:
                    new_machine = self.create_new_machine(new_type_cn)
                except ValueError:
                    print_plus(f"机器类型 {new_type_cn} 不存在")
                    continue
                try:
                    self.connect_machines(args[0],new_machine.id)
                except KeyError as e:
                    print_plus(f"参数错误-机器{e}不存在")
                    continue
                continue
            if "调整" in do_what:
                if len(args) != 1:
                    print_plus(f"参数错误-调整命令需1个参数-收到{len(args)}个")
                    continue
                try:
                    self.all_machines[args[0]].show_recipe()
                except KeyError as e:
                    print_plus(f"参数错误-机器{e}不存在")
                    continue
                try:
                    recipe_index = int(input_plus("请输入要调整到的新配方编号"))
                    self.all_machines[args[0]].set_recipe(recipe_index)
                except TypeError:
                    print_plus("参数错误-配方编号应为整数")
                    continue
                except IndexError:
                    print_plus(f"参数错误-不存在这一编号的配方")
                    continue

industry_manager = IndustryManager()

if __name__ == "__main__":
    industry_manager.mainloop()