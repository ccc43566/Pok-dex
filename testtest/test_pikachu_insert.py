#!/usr/bin/env python3
import os
import json
import sys

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 添加项目根目录到sys.path，这样可以导入db模块
sys.path.append(project_root)

from db.database import init_db, insert_pokemon

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 皮卡丘数据文件路径
data_path = os.path.join(project_root, "backend/spider/pokemon_data_all/25_pikachu.json")
desc_path = os.path.join(project_root, "backend/spider/pokemon_descrptions/25_pikachu.json")

# 加载数据文件
def load_json(file_path):
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 {file_path} 失败: {e}")
        return None

data = load_json(data_path)
desc = load_json(desc_path)

if data:
    print("=== 原始数据 ===")
    print(f"ID: {data['id']}")
    print(f"Name: {data['name']}")
    print(f"gender_ratio: {data.get('gender_ratio')}")
    print(f"gender_ratio类型: {type(data.get('gender_ratio'))}")
    
    # 合并数据
    pokemon_data = {
        "id": data["id"],
        "name": desc.get("name_en", data["name"]) if desc else data["name"],
        "jp_name": None,  # 暂时为空
        "en_name": desc.get("name_en") if desc else None,
        "type1": data["type1"],
        "type2": data.get("type2"),
        "hp": data["hp"],
        "attack": data["attack"],
        "defense": data["defense"],
        "sp_atk": data["sp_atk"],
        "sp_def": data["sp_def"],
        "speed": data["speed"],
        "total": data["total"],
        "height": data.get("height"),  # 身高
        "weight": data.get("weight"),  # 体重
        "gender_ratio": data.get("gender_ratio"),  # 雌雄比例
        "description": desc.get("description") if desc else None,
        "image_path": data.get("image_path")
    }
    
    print("\n=== 合并后的数据 ===")
    print(f"gender_ratio: {pokemon_data.get('gender_ratio')}")
    print(f"gender_ratio类型: {type(pokemon_data.get('gender_ratio'))}")
    
    # 初始化数据库
    init_db()
    
    # 插入数据库
    try:
        insert_pokemon(pokemon_data)
        print("\n=== 插入成功 ===")
        
        # 验证数据库中的数据
        from db.database import get_pokemon_by_id
        pokemon = get_pokemon_by_id(25)
        print("\n=== 数据库中的数据 ===")
        print(f"gender_ratio: {pokemon.get('gender_ratio')}")
        print(f"gender_ratio类型: {type(pokemon.get('gender_ratio'))}")
    except Exception as e:
        print(f"插入失败: {e}")
else:
    print("无法加载皮卡丘数据文件")