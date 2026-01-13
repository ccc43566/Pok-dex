#!/usr/bin/env python3
import requests
import re

DATA_URL = "https://play.pokemonshowdown.com/data/pokedex.js"

def check_js_data():
    """检查Pokemon Showdown JS数据的内容"""
    print("正在下载Pokemon Showdown数据...")
    response = requests.get(DATA_URL)
    if response.status_code != 200:
        print(f"无法下载数据: {response.status_code}")
        return

    js_content = response.text
    print(f"数据长度: {len(js_content)} 字符")

    # 检查多个宝可梦的数据
    test_pokemon = ['bulbasaur', 'charmander', 'squirtle', 'pikachu']

    for pokemon_name in test_pokemon:
        print(f"\n{'='*20} {pokemon_name.upper()} {'='*20}")

        pattern = rf'{pokemon_name}:\s*{{([^}}]*?)}}'
        match = re.search(pattern, js_content, re.DOTALL)

        if match:
            data_str = match.group(1)
            print(f"原始数据 (前500字符): {data_str[:500]}")

            # 检查各个字段
            fields = ['baseStats', 'abilities', 'types', 'num', 'name']
            for field in fields:
                if field == 'baseStats':
                    match_field = re.search(r'baseStats:\s*{([^}]*)}', data_str)
                elif field == 'abilities':
                    match_field = re.search(r'abilities:\s*{([^}]*)}', data_str)
                elif field == 'types':
                    match_field = re.search(r'types:\s*\[([^\]]*)\]', data_str)
                elif field == 'num':
                    match_field = re.search(r'num:\s*(\d+)', data_str)
                elif field == 'name':
                    match_field = re.search(r'name:\s*["\']([^"\']+)["\']', data_str)

                if match_field:
                    print(f"✅ {field}: {match_field.group(1)}")
                else:
                    print(f"❌ {field}: 未找到")

        else:
            print(f"❌ 未找到{pokemon_name}的数据")

if __name__ == "__main__":
    check_js_data()
