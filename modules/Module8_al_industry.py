import random

from core.Module1_txt import print_plus,Tree,adjust,n_column_print
from core.Module2_json_loader import json_loader

random.seed("IFAWL_RECIPE_V0")

ALL_MATERIALS:list[str] = list(
    json_loader.load("storage_template")["materials"].keys()
)

AL_META_DATA = json_loader.load("al_meta_data")
"""所有AL的元数据"""

AL_RANK_LIST:dict[str,int] = {}
"""
从AL的字符串序号获取其级数
"""
for key in AL_META_DATA:
    AL_RANK_LIST[key] = AL_META_DATA[key]["rank_num"]

AL_NAME_LIST:dict[str,int] = {}
"""
从AL的字符串序号获取其短名称
"""
for key in AL_META_DATA:
    AL_NAME_LIST[key] = AL_META_DATA[key]["short_name"] + f"#{key}"

AL_RECIPE_SKELETON = json_loader.load("al_recipe_skeleton")

class Tools:

    @staticmethod
    def generate_recipe(rank:int) -> dict[str,int]:
        if rank == 0:
            return {}
        out = {}
        key = str(rank*1100)
        skeleton = random.choice(AL_RECIPE_SKELETON[key])
        material_pool = ALL_MATERIALS.copy()
        random.shuffle(material_pool)
        for i in range(len(material_pool)):
            if skeleton[i]==0:
                continue
            else:
                out[material_pool[i]] = skeleton[i]
        return out

recipe_for_all_al = {}

for al_str_index in AL_META_DATA.keys():
    recipe_for_all_al[al_str_index] = Tools.generate_recipe(AL_RANK_LIST[al_str_index])