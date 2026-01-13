#!/usr/bin/env python3
import json
import os
import requests
from bs4 import BeautifulSoup

# 设置请求头，避免被反爬
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 配置
DATA_URL = "https://play.pokemonshowdown.com/data/pokedex.js"
# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "pokemon_descrptions")

# 创建文件夹（如果不存在）
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_pokemon_data(js_content, pokemon_key):
    """从JavaScript内容中提取特定宝可梦的数据"""
    import re
    # 查找特定的宝可梦数据
    pattern = rf'{re.escape(pokemon_key)}:\s*{{([^}}]*?)}}'
    match = re.search(pattern, js_content, re.DOTALL)

    if not match:
        return None

    pokemon_str = match.group(1)

    # 手动解析JavaScript对象格式
    data = {}

    # 解析num
    num_match = re.search(r'num:\s*(\d+)', pokemon_str)
    if num_match:
        data['num'] = int(num_match.group(1))

    # 解析name
    name_match = re.search(r'name:\s*["\']([^"\']+)["\']', pokemon_str)
    if name_match:
        data['name'] = name_match.group(1)

    return data

def get_pokemon_description_from_52poke(pokemon_name_en):
    """从52poke获取宝可梦的中文描述"""
    # 构造 URL（使用英文名）
    url = f"https://wiki.52poke.com/wiki/{pokemon_name_en}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # 找到正文容器
        content_div = soup.find('div', id='mw-content-text')
        if not content_div:
            return "未找到描述"

        # 获取所有 <p> 标签
        all_p_tags = content_div.find_all('p')
        if len(all_p_tags) < 3:
            return "描述信息不足"

        # 提取第1个第2个和第3个 <p> 标签的文本
        descriptions = []
        for i in range(min(3, len(all_p_tags))):
            p_text = all_p_tags[i].get_text(strip=True)
            if p_text and len(p_text) > 10:  # 确保有足够内容
                descriptions.append(p_text)

        overview = "\n".join(descriptions)
        return overview

    except Exception as e:
        print(f"获取描述失败 {pokemon_name_en}: {e}")
        return "未找到描述"

def test_save():
    """测试保存前3只宝可梦的数据"""
    print("测试保存前3只宝可梦的数据...")

    # 预加载数据文件
    response = requests.get(DATA_URL)
    if response.status_code != 200:
        print(f"无法加载数据库: {response.status_code}")
        return
    js_content = response.text

    # 测试前3只宝可梦
    test_pokemon = ['bulbasaur', 'ivysaur', 'venusaur']

    for pokemon_name in test_pokemon:
        pokemon = extract_pokemon_data(js_content, pokemon_name)
        if not pokemon:
            print(f"未找到宝可梦数据: {pokemon_name}")
            continue

        data = {
            'id': pokemon.get('num'),
            'name_en': pokemon.get('name', ''),
            'name': pokemon_name,
            'description': get_pokemon_description_from_52poke(pokemon.get('name', ''))
        }

        # 保存到JSON文件
        filename = f"{data['id']}_{pokemon_name}.json"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"已保存: {filename}")

if __name__ == "__main__":
    test_save()
