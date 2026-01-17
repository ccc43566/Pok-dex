import requests
import re

def check_item_spritenum():
    """检查道具的spritenum定义"""
    url = "https://play.pokemonshowdown.com/data/items.js"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"无法获取数据: {response.status_code}")
        return

    js_content = response.text

    # 清理JS内容
    if js_content.startswith('exports.BattleItems = '):
        js_content = js_content[len('exports.BattleItems = '):]

    # 检查几个道具的spritenum
    test_items = ['mentalherb', 'metalcoat', 'metalpowder', 'electirizer', 'eviolite']

    for item_name in test_items:
        # 查找道具数据
        start_pattern = rf'{re.escape(item_name)}:\s*{{'
        start_match = re.search(start_pattern, js_content)

        if start_match:
            start_pos = start_match.end() - 1

            # 计算大括号平衡
            brace_count = 0
            end_pos = start_pos

            for i in range(start_pos, len(js_content)):
                if js_content[i] == '{':
                    brace_count += 1
                elif js_content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i + 1
                        break

            item_str = js_content[start_pos:end_pos]

            # 检查spritenum
            spritenum_match = re.search(r'spritenum:\s*(\d+)', item_str)
            if spritenum_match:
                print(f"{item_name}: spritenum = {spritenum_match.group(1)}")
            else:
                print(f"{item_name}: spritenum NOT FOUND")

            # 显示道具数据片段（前200字符）
            print(f"  数据片段: {item_str[:200]}...")
            print()
        else:
            print(f"{item_name}: NOT FOUND IN JS")
            print()

if __name__ == "__main__":
    check_item_spritenum()
