import os
import json
from pathlib import Path


class JsonLoader:
    def __init__(self, base_dir=None):
        # 如果没有指定基础目录，则使用模块所在目录的父目录
        if base_dir is None:
            # 获取当前模块文件所在目录
            module_dir = Path(__file__).parent
            # 假设resources目录在项目根目录，即core目录的父目录下
            self.dir = module_dir.parent / "resources" / "json"
        else:
            self.dir = Path(base_dir)

    def load(self, title: str) -> dict:
        file_path = self.dir / f'{title}.json'
        if not file_path.exists():
            raise FileNotFoundError(f"JSON文件不存在: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_file_path(self, title: str) -> Path:
        """获取文件的完整路径"""
        return self.dir / f'{title}.json'


# 创建全局实例
json_loader = JsonLoader()