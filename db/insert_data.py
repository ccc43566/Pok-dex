import os
import json
import sys
sys.path.append('db')
from database import init_db, insert_pokemon

def load_json(file_path):
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 {file_path} 失败: {e}")
        return None

def insert_all_pokemon():
    """插入所有宝可梦数据"""
    # 初始化数据库
    init_db()

    # 路径
    data_dir = "backend/spider/pokemon_data_all"
    desc_dir = "backend/spider/pokemon_descrptions"

    # 获取所有数据文件
    if not os.path.exists(data_dir):
        print(f"数据目录不存在: {data_dir}")
        return

    files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    print(f"找到 {len(files)} 个数据文件")

    inserted_count = 0

    for file in files:
        # 读取数据文件
        data_path = os.path.join(data_dir, file)
        data = load_json(data_path)
        if not data:
            continue

        # 读取描述文件
        desc_path = os.path.join(desc_dir, file)
        desc = load_json(desc_path)

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
            "description": desc.get("description") if desc else None,
            "image_path": data.get("image_path")
        }

        # 插入数据库
        try:
            insert_pokemon(pokemon_data)
            inserted_count += 1
        except Exception as e:
            print(f"插入失败 {pokemon_data['name']}: {e}")

    print(f"共插入 {inserted_count} 个宝可梦")

if __name__ == "__main__":
    insert_all_pokemon()
