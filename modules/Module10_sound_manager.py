import pygame
import threading
import time
from pathlib import Path

# 初始化
pygame.init()
pygame.mixer.init()

class SoundsManager:

    def __init__(self):
        self.sound_dir = Path(__file__).parent.parent / "resources" / "sounds"

    def play_async(self,filename):
        """异步播放音效"""

        def play():
            pygame.mixer.Sound(self.sound_dir/filename).play()

        threading.Thread(target=play, daemon=True).start()


sounds_manager = SoundsManager()