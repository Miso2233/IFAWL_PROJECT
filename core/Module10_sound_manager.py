import os
import random

import pygame
import threading
import time
from pathlib import Path

# 初始化
pygame.init()
pygame.mixer.init()

class SoundsManager:
    """
    缩写与命名
    背景音乐 /music _bgm
    短音效 /sfx _sfx
    环境音 /ambient _ambient
    """

    def __init__(self):
        self.music_dir = Path(__file__).parent.parent / "resources" / "sounds" / "music"
        self.sfx_dir = Path(__file__).parent.parent / "resources" / "sounds" / "sfx"
        self.ambient_dir = Path(__file__).parent.parent / "resources" / "sounds" / "ambient"
        self.ambient_channel = pygame.mixer.Channel(0)

    def switch_to_bgm(self, theme, fade_ms=1000):
        """
        切换到背景音乐
        :param theme: 主题，对应music下的文件夹名称
        :param fade_ms: 淡入淡出毫秒数
        :return: 无
        """
        self.stop_bgm(fade_ms=fade_ms)
        folder = self.music_dir / theme
        contents = os.listdir(folder)
        chosen_music = random.choice(contents)
        pygame.mixer.music.load(folder / chosen_music)
        pygame.mixer.music.play(loops=-1,fade_ms=fade_ms)

    def stop_bgm(self, fade_ms=1000):
        """
        停止背景音乐
        :param fade_ms: 淡入淡出毫秒数
        :return: 无
        """
        pygame.mixer.music.fadeout(fade_ms)

    def switch_to_ambient(self,theme, fade_ms=1000):
        """
        在音轨上播放环境音
        :param theme: 主题，对应ambient下的文件夹名称
        :param fade_ms: 淡入淡出毫秒数
        :return: 无
        """
        folder = self.ambient_dir    / theme
        contents = os.listdir(folder)
        chosen_ambient = random.choice(contents)
        sound = pygame.mixer.Sound(folder / chosen_ambient)
        self.ambient_channel.play(sound,loops=-1,fade_ms=fade_ms)

    def stop_ambient(self, fade_ms=1000):
        """
        停止环境音
        :param fade_ms: 淡入淡出毫秒数
        :return: 无
        """
        self.ambient_channel.fadeout(fade_ms)

    def play_sfx(self,theme):
        """
        在音轨上播放短音效
        :param theme: 主题，对应sfx下的文件夹名称
        :return: 无
        """
        folder = self.sfx_dir / theme
        contents = os.listdir(folder)
        chosen_sfx = random.choice(contents)
        sound = pygame.mixer.Sound(folder / chosen_sfx)
        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(sound)



sounds_manager = SoundsManager()