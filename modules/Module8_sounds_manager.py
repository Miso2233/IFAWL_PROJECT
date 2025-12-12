import os
import pygame
import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum
import json
from core.Module2_json_loader import json_loader

class SoundType(Enum): # 音效类型枚举，用来分类管理注意
    sfx = "sfx"
    music = "music"
    ui_sound = "ui_sound"
    voice = "voice"

@dataclass
class SoundInfo: # 声音可能会用到的属性
    sound: pygame.mixer.Sound
    sound_type: SoundType
    volume: float = 1.0
    loop: bool = False
    duration: float = 0 # 音效时长

class VoiceManager:
    """
    VoiceManager 的 Docstring
    声音管理器的类
    注意要使用单例单例单例
    """

    _instance = None

    def __init__(self, sounds_folder: str = "assets/sounds"):
        if not hasattr(self,'initialized'):
            # 这一步是初始化pygame的mixer（如果没有的话）
            if not pygame.mixer.get_init():
                """设置音频参数（就是上面提到的）"""
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

            self.sounds_folder = sounds_folder
            self.sounds_cache: Dict[str, SoundInfo] = {}  # 声音缓存
            self.sound_channels: Dict[str, pygame.mixer.Channel] = {}  # 音效频道
            self.music_channel: Optional[pygame.mixer.Channel] = None  # 音乐专用频道

            self.master_volume = 1.0  # 主音量 [0.0, 1.0]
            self.volume_groups = {
                SoundType.SFX: 1.0,
                SoundType.MUSIC: 0.7,  # 背景音乐通常比音效轻一点
                SoundType.UI: 1.0,
                SoundType.VOICE: 1.0
            }

            self.supported_formats = {'.wav', '.mp3', '.ogg', '.flac'}
            self.lock = threading.Lock()
            self.load_sound_config()

            self.initialized = True

    def load_sound(self, config_file: str = "sound_config.json"):
        """功能是加载音效设置"""
        config_path = os.path.join(self.sounds_folder, config_file)
        
        # 确保文件存在，这是谨慎的表现
        if not os.path.exists(config_path):
            print(f"警告：没有找到配置文件: {config_path}")
            return
        
        try:
            # 加载json
            config: dict = json_loader.load("sound_config")

            # 加载音量设置
            if "volumes" in config:
                for sound_type_str, volume in config["volumes"].items():
                    try:
                        # 将字符串转换为Soundtype枚举
                        sound_type = SoundType(sound_type_str.lower())
                        self.volume_groups[sound_type] = max(0.0, min(1.0, volume))
                    except ValueError:
                        print(f"警告：没有这个音乐文件：{sound_type_str}")
            
            # 加载音效
            if "preload" in config:
                print(f"正在从配置文件预加载 {len(config['preload'])} 种音效……") # 如果嫌多余可删，主要是这样看上去更有感觉。下面的也是这样
                for sound_file in config["preload"]:
                    self.preload_sound(sound_file)

            # 加载音效映射（你别管，pygame是这样的）
            if "sound_mapping" in config:
                self.sound_mappings = config["sound_mapping"]
                print("正在加载相关音效映射……")

            # 按场景加载音效组
            if "sound_groups" in config:
                self.sound_groups = config["sound_groups"]
                print("正在加载相关音效组……")

            # 加载默认设置
            if "defaults" in config:
                defaults = config["defaults"]
                if "master_volume" in defaults:
                    self.master_volume = max(0.0, min(1.0, defaults["master_volume"]))
                if "min_cool_down" in defaults:
                    self.min_cooldown = defaults["min_cool_down"]

            # 提示语
            print("已从配置文件成功加载各种音效")

        except ImportError:
            print("警告：没找到能打开json文件的方法")

    def preload_sound(self, sound_name: str):
        """预加载音效到缓存"""
        if sound_name not in self.sounds_cache:
            return self._load_sound_cache(sound_name)
        return True
    
    def _load_sound_cache(self, sound_name: str):
        """正式加载音效到缓存，防止卡顿"""
        file_path = self._get_sound_path(sound_name)
        if not file_path:
            print(f"没有找到{sound_name}对应的音乐文件") # 避免因为没有那首歌而放不了，但是又没显示，导致被误判为程序bug的情况
            return False
        
        try:
            sound = pygame.mixer.Sound(file_path) # 用load提取音乐文件
            sound_type = self._find_sound_type(sound_name) # 获取音效类型，根据文件路径或命名约定来做
            duration = self._get_sound_duration(sound) # 这是音效时长
            self.sounds_cache[sound_name] = SoundInfo(
                sound=sound,
                sound_type=sound_type,
                volume=1.0,
                loop=True,
                duration=duration
                )
            
            print(f"正在加载音乐：{sound_name} 用时：{duration:.2f}")
            return True
        
        except Exception as e:
            print("歌曲缓存错误：{e}")
            return False
        
    def _get_sound_path(self, sound_name: str):
        """找到路径，这玩意load没写"""
        if '.' in sound_name:
            potential_path = os.path.join(self.sounds_folder, sound_name)
            if os.path.exists(potential_path):
                return potential_path
        
        for ext in self.supported_formats: # 尝试添加文件扩展名
            potential_path = os.path.join(self.sounds_folder, f"{sound_name}{ext}")
            if os.path.exists(potential_path):
                return potential_path
        
        for root, dirs, files in os.walk(self.sounds_folder): # 双循环，查找子目录
            for file in files:
                name_without_ext = os.path.splitext(file)[0]
                if name_without_ext == sound_name:
                    return os.path.join(root, file)
        
        return None
    
    def _find_sound_type(self, sound_name: str):
        """根据文件名推断音效类型"""
        name_lower = sound_name.lower()
        
        if any(word in name_lower for word in ['music', 'bgm', 'theme']):
            return SoundType.MUSIC
        elif any(word in name_lower for word in ['ui', 'menu', 'button', 'select']):
            return SoundType.UI
        elif any(word in name_lower for word in ['voice', 'narrator', 'dialogue']):
            return SoundType.VOICE
        else:
            return SoundType.SFX
        
    def _get_sound_duration(self, sound): # sound来自Sound（）
        """"""