#!/usr/bin/env python3
import json
import os

def test_bulbasaur():
    """测试重新爬取Bulbasaur的数据"""
    print("测试重新爬取Bulbasaur的数据...")

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

    # 获取Bulbasaur的数据
    print("重新爬取Bulbasaur的数据...")

    # 先测试extract_pokemon_data
    from spider_all import extract_pokemon_data
    pokemon_data = extract_pokemon_data(js_content, "bulbasaur")
    print(f"extract_pokemon_data结果: {pokemon_data}")

    data = get_pokemon_data("bulbasaur", js_content)

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
        filename = f"{data['id']}_bulbasaur.json"
        os.makedirs("pokemon_data_all", exist_ok=True)
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

        # 检查是否正确（bulbasaur的标准种族值应该是HP: 45, Attack: 49, Defense: 49, Sp. Atk: 65, Sp. Def: 65, Speed: 45）
        expected_stats = {'hp': 45, 'attack': 49, 'defense': 49, 'sp_atk': 65, 'sp_def': 65, 'speed': 45}
        expected_abilities = ["Overgrow", "Chlorophyll"]

        print("\n数据验证:")
        stats_correct = all(saved_data.get(stat) == expected_stats[stat] for stat in expected_stats)
        abilities_correct = all(ability in saved_data['abilities'] for ability in expected_abilities)

        print(f"种族值正确: {'✅' if stats_correct else '❌'}")
        print(f"特性正确: {'✅' if abilities_correct else '❌'}")

        if stats_correct and abilities_correct:
            print("🎉 Bulbasaur数据完全正确！")
        else:
            print("❌ Bulbasaur数据有误")
            if not stats_correct:
                print(f"  期望种族值: {expected_stats}")
                print(f"  实际种族值: {{'hp': {saved_data['hp']}, 'attack': {saved_data['attack']}, 'defense': {saved_data['defense']}, 'sp_atk': {saved_data['sp_atk']}, 'sp_def': {saved_data['sp_def']}, 'speed': {saved_data['speed']}}}")
            if not abilities_correct:
                print(f"  期望特性: {expected_abilities}")
                print(f"  实际特性: {saved_data['abilities']}")

if __name__ == "__main__":
    test_bulbasaur()
