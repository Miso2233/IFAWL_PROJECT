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
        self.sfx_channel = pygame.mixer.Channel(1)

    def switch_to_bgm(self, filename, fade_ms=500):
        """
        切换到背景音乐
        :param filename: 文件名，带后缀
        :param fade_ms: 淡入淡出毫秒数
        :return: 无
        """
        self.stop_bgm()
        pygame.mixer.music.load(self.music_dir / filename)
        pygame.mixer.music.play(loops=-1,fade_ms=fade_ms)

    def stop_bgm(self, fade_ms=500):
        """
        停止背景音乐
        :param fade_ms: 淡入淡出毫秒数
        :return: 无
        """
        pygame.mixer.music.fadeout(fade_ms)

    def switch_to_ambient(self,filename, fade_ms=500):
        """
        在音轨上播放环境音
        :param filename: 文件名，带后缀
        :param fade_ms: 淡入淡出毫秒数
        :return: 无
        """
        sound = pygame.mixer.Sound(self.ambient_dir / filename)
        self.ambient_channel.play(sound,loops=-1,fade_ms=fade_ms)

    def play_sfx(self,filename):
        """
        在音轨上播放短音效
        :param filename: 文件名，带后缀
        :return: 无
        """
        sound = pygame.mixer.Sound(self.sfx_dir / filename)
        self.sfx_channel.play(sound)


sounds_manager = SoundsManager()