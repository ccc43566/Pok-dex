#!/usr/bin/env python3
import json
import os

def test_venusaur():
    """测试重新爬取Venusaur的数据"""
    print("测试重新爬取Venusaur的数据...")

    # 导入spider_all.py的函数
    import sys
    sys.path.append('.')

    # 这里我们直接模拟调用spider_all.py的逻辑
    from spider_all import get_pokemon_data
    import requests

    # 预加载JS数据
    DATA_URL = "https://play.pokemonshowdown.com/data/pokedex.js"
    response = requests.get(DATA_URL)
    if response.status_code != 200:
        print(f"无法加载数据库: {response.status_code}")
        return

    js_content = response.text

    # 获取Venusaur的数据
    print("重新爬取Venusaur的数据...")
    data = get_pokemon_data("venusaur", js_content)

    if data:
        print("爬取成功！")
        print(f"ID: {data['id']}")
        print(f"名称: {data['name']}")
        print(f"HP: {data['hp']}")
        print(f"Attack: {data['attack']}")
        print(f"Defense: {data['defense']}")
        print(f"Sp. Atk: {data['sp_atk']}")
        print(f"Sp. Def: {data['sp_def']}")
        print(f"Speed: {data['speed']}")
        print(f"Total: {data['total']}")
        print(f"Abilities: {data['abilities']}")

        # 保存数据
        filename = f"{data['id']}_venusaur.json"
        filepath = os.path.join("pokemon_data_all", filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"数据已保存到: {filepath}")

        # 验证保存的数据
        with open(filepath, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)

        print("\n验证保存的数据:")
        print(f"HP: {saved_data['hp']}")
        print(f"Attack: {saved_data['attack']}")
        print(f"Abilities: {saved_data['abilities']}")

        # 检查是否正确（venusaur的标准特性应该是Overgrow, Chlorophyll, Cacophony）
        expected_abilities = ["Overgrow", "Chlorophyll", "Cacophony"]
        actual_abilities = saved_data['abilities']

        print("\n特性检查:")
        print(f"期望特性: {expected_abilities}")
        print(f"实际特性: {actual_abilities}")

        # 检查是否包含期望的特性
        missing = [ability for ability in expected_abilities if ability not in actual_abilities]
        extra = [ability for ability in actual_abilities if ability not in expected_abilities and ability not in ["Thick Fat"]]  # Thick Fat是mega的

        if not missing and not extra:
            print("✅ 特性匹配正确！")
        else:
            print("❌ 特性不匹配：")
            if missing:
                print(f"  缺少: {missing}")
            if extra:
                print(f"  多余: {extra}")

if __name__ == "__main__":
    test_venusaur()
