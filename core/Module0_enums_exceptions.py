"""
Module0_enums_exceptions.py - 枚举类定义模块

该模块包含项目中使用的所有枚举类，便于统一管理和使用。
"""

class DamageType:
    """伤害类型枚举"""
    MISSILE_LAUNCH = "missile_launch"  # 导弹射击
    PARTICLE_CANNON_SHOOTING = "particle_cannon_shooting"  # 粒子炮射击
    ENEMY_MISSILE_BOOM = "enemy_missile_boom"  # 敌方导弹殉爆
    ORDINARY_ATTACK = "ordinary_attack"  # 杂项攻击


class Modes:
    """游戏模式枚举"""
    FIGHT = "FIGHT"
    DISASTER = "DISASTER"
    INFINITY = "INFINITY"
    PPVE = "PPVE"



class Side:
    """阵营枚举，用于标识敌我双方"""
    PLAYER = 1  # 玩家方
    ENEMY = 0   # 敌方

class ASI:
    """Al state列表索引枚举"""
    OTHER = 0
    BUILDING = 1
    WORKING = 2
    LOGGING = 3
    COOLING = 4

class OSI:
    """OCP state列表索引枚举"""
    OTHER = 0
    DAYS_COUNTER = 1
    LOGGING = 2
    COOLING = 3

class IFAWL_ConnectionCancel(Exception):
    pass

class IFAWL_NoOcpError(Exception):
    pass