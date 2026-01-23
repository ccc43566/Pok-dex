#!/usr/bin/env python3
import re
import requests

# 原始数据源URL
DATA_URL = "https://play.pokemonshowdown.com/data/pokedex.js"

def extract_pikachu_data():
    """从原始JS文件中提取皮卡丘的数据"""
    print("正在获取原始数据...")
    response = requests.get(DATA_URL)
    if response.status_code != 200:
        print(f"无法加载数据: {response.status_code}")
        return None
    
    js_content = response.text
    
    # 查找皮卡丘的数据
    pokemon_key = "pikachu"
    start_pattern = rf'{re.escape(pokemon_key)}:\s*{{'
    start_match = re.search(start_pattern, js_content)
    
    if not start_match:
        print("未找到皮卡丘的数据")
        return None
    
    start_pos = start_match.end() - 1  # 包含开头的{
    
    # 从start_pos开始，计算大括号的平衡
    brace_count = 0
    end_pos = start_pos
    
    for i in range(start_pos, len(js_content)):
        if js_content[i] == '{':
            brace_count += 1
        elif js_content[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_pos = i + 1  # 包含结尾的}
                break
    
    if brace_count != 0:
        print("大括号匹配失败")
        return None
    
    pokemon_str = js_content[start_pos:end_pos]
    print("皮卡丘原始数据片段:")
    print(pokemon_str)
    print("\n" + "="*50 + "\n")
    
    # 提取genderRatio字段
    print("提取genderRatio字段:")
    gender_match = re.search(r'genderRatio:\s*{([^}]*)}', pokemon_str)
    if gender_match:
        print(f"找到genderRatio: {gender_match.group(0)}")
        gender_str = gender_match.group(1)
        print(f"genderRatio内容: {gender_str}")
        gender_data = {}
        gender_matches = re.findall(r'([MF]):\s*([\d.]+)', gender_str)
        print(f"解析结果: {gender_matches}")
        for gender, ratio in gender_matches:
            gender_data[gender] = float(ratio)
        print(f"最终genderRatio数据: {gender_data}")
    else:
        print("未找到genderRatio字段")
    
    return pokemon_str

if __name__ == "__main__":
    extract_pikachu_data()