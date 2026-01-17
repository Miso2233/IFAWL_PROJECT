from core.Module0_enums_exceptions import OSI
from core.Module1_txt import print_plus
from core.Module2_json_loader import json_loader

ALL_OCP_METADATA = json_loader.load("ocps_metadata")

class OCP_General:

    def __init__(self,index:int):
        # 元数据字段
        self.index:str = str(index)
        self.metadata = ALL_OCP_METADATA[self.index]
        self.txt_list = self.metadata["txt_list"]
        # 战场字段
        self.state = [None,0,0,0]

    def print_plot(self):
        print_plus()