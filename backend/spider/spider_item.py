import requests
import json
import os
import re

def extract_item_data(js_content, item_key):
    """从JavaScript内容中提取特定道具的数据"""
    # 查找特定的道具数据，使用平衡大括号匹配
    start_pattern = rf'{re.escape(item_key)}:\s*{{'
    start_match = re.search(start_pattern, js_content)

    if not start_match:
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
        return None

    item_str = js_content[start_pos:end_pos]

    # 手动解析JavaScript对象格式
    data = {}

    # 解析spritenum
    spritenum_match = re.search(r'spritenum:\s*(\d+)', item_str)
    if spritenum_match:
        data['spritenum'] = int(spritenum_match.group(1))

    # 解析name
    name_match = re.search(r'name:\s*["\']([^"\']+)["\']', item_str)
    if name_match:
        data['name'] = name_match.group(1)

    # 解析desc
    desc_match = re.search(r'desc:\s*["\']([^"\']*)["\']', item_str)
    if desc_match:
        data['desc'] = desc_match.group(1)
    else:
        data['desc'] = ""

    # 解析shortDesc
    short_desc_match = re.search(r'shortDesc:\s*["\']([^"\']*)["\']', item_str)
    if short_desc_match:
        data['shortDesc'] = short_desc_match.group(1)
    else:
        data['shortDesc'] = data['desc']

    # 解析gen
    gen_match = re.search(r'gen:\s*(\d+)', item_str)
    if gen_match:
        data['gen'] = int(gen_match.group(1))
    else:
        data['gen'] = 1

    # 解析isPokeball
    if 'isPokeball' in item_str:
        data['isPokeball'] = True
    else:
        data['isPokeball'] = False

    return data

def main():
    # Pokemon Showdown道具数据URL
    ITEMS_DATA_URL = "https://play.pokemonshowdown.com/data/items.js"

    try:
        print("正在从Pokemon Showdown获取道具数据...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(ITEMS_DATA_URL, headers=headers, timeout=30)
        response.raise_for_status()
        js_content = response.text

        # 提取所有道具名称
        item_names = []
        matches = re.findall(r'(\w+):\s*{', js_content)
        for match in matches:
            if match.islower() or match in ['potion', 'superpotion', 'hyperpotion', 'maxpotion', 'fullrestore']:
                item_names.append(match)

        print(f"找到 {len(item_names)} 个道具")

        # 创建items目录
        items_dir = os.path.join(os.path.dirname(__file__), 'items')
        os.makedirs(items_dir, exist_ok=True)

        item_count = 0
        for item_name in item_names:
            item_data = extract_item_data(js_content, item_name)
            if item_data:
                # 构造JSON数据
                full_item_data = {
                    "id": item_count,
                    "name": item_data.get('name', item_name),
                    "english": item_name,
                    "category": "道具",  # 默认类别
                    "num": item_count,
                    "spritenum": item_data.get('spritenum', item_count),
                    "desc": item_data.get('desc', ''),
                    "shortDesc": item_data.get('shortDesc', ''),
                    "gen": item_data.get('gen', 1),
                    "isPokeball": item_data.get('isPokeball', False)
                }

                filename = f"{item_count}_{item_name}.json"
                filepath = os.path.join(items_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(full_item_data, f, ensure_ascii=False, indent=2)

                item_count += 1
                print(f"[{item_count}] 保存: {item_name}")

        print(f"\n✅ 成功！共获取 {item_count} 个道具，已保存到 items/ 目录")

    except Exception as e:
        print(f"❌ 发生错误: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()
