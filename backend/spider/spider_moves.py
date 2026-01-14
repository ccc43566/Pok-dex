import requests
import re
import json
import os
import time

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "moves")

# 创建文件夹（如果不存在）
os.makedirs(OUTPUT_DIR, exist_ok=True)

MOVES_URL = "https://play.pokemonshowdown.com/data/moves.js"

def get_js_content(url):
    """获取Pokemon Showdown的JS数据内容"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return None
    return response.text

def extract_move_data(js_content, move_name):
    """从JS内容中提取特定技能的数据"""
    # 清理JS内容，移除exports部分
    if js_content.startswith('exports.BattleMovedex = '):
        js_content = js_content[len('exports.BattleMovedex = '):]

    move_key = move_name.lower().replace(' ', '').replace('-', '').replace("'", "")

    # 查找特定的技能数据
    start_pattern = rf'{re.escape(move_key)}:\s*{{'
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

    move_str = js_content[start_pos:end_pos]

    # 手动解析JavaScript对象格式
    data = {}

    # 解析num
    num_match = re.search(r'num:\s*(\d+)', move_str)
    if num_match:
        data['num'] = int(num_match.group(1))

    # 解析name
    name_match = re.search(r'name:\s*["\']([^"\']+)["\']', move_str)
    if name_match:
        data['name'] = name_match.group(1)

    # 解析accuracy
    accuracy_match = re.search(r'accuracy:\s*(true|\d+)', move_str)
    if accuracy_match:
        acc_value = accuracy_match.group(1)
        data['accuracy'] = True if acc_value == 'true' else int(acc_value)

    # 解析basePower
    power_match = re.search(r'basePower:\s*(\d+)', move_str)
    if power_match:
        data['basePower'] = int(power_match.group(1))

    # 解析category
    category_match = re.search(r'category:\s*["\']([^"\']+)["\']', move_str)
    if category_match:
        data['category'] = category_match.group(1)

    # 解析type
    type_match = re.search(r'type:\s*["\']([^"\']+)["\']', move_str)
    if type_match:
        data['type'] = type_match.group(1)

    # 解析pp
    pp_match = re.search(r'pp:\s*(\d+)', move_str)
    if pp_match:
        data['pp'] = int(pp_match.group(1))

    # 解析priority
    priority_match = re.search(r'priority:\s*(\-?\d+)', move_str)
    if priority_match:
        data['priority'] = int(priority_match.group(1))

    # 解析desc
    desc_match = re.search(r'desc:\s*["\']([^"\']*)["\']', move_str)
    if desc_match:
        data['desc'] = desc_match.group(1)

    # 解析shortDesc
    short_desc_match = re.search(r'shortDesc:\s*["\']([^"\']*)["\']', move_str)
    if short_desc_match:
        data['shortDesc'] = short_desc_match.group(1)

    return data

def get_all_move_names(js_content):
    """从JS内容中获取所有技能名称"""
    # 清理JS内容
    if js_content.startswith('exports.BattleMovedex = '):
        js_content = js_content[len('exports.BattleMovedex = '):]

    # 匹配形如: "move_name":{...}, 的模式
    matches = re.findall(r'(\w+):\s*{', js_content)

    # 过滤掉非技能条目
    move_names = []
    for match in matches:
        # 跳过特殊条目
        if not match.startswith(('battle_', 'pokemons_')) and match.islower():
            move_names.append(match)

    return move_names

def save_move_data(move_name, move_data, output_dir):
    """保存单个技能的数据"""
    if not move_data or 'num' not in move_data:
        return False

    move_id = move_data['num']
    data = {
        "id": move_id,
        "name": move_name,
        **move_data
    }

    filename = f"{move_id}_{move_name}.json"
    filepath = os.path.join(output_dir, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存 {move_name} 数据失败: {e}")
        return False

def main():
    print("=" * 50)
    print("宝可梦技能数据批量爬虫")
    print("=" * 50)

    # 预加载技能数据文件
    print("正在预加载技能数据库...")
    js_content = get_js_content(MOVES_URL)
    if not js_content:
        print("无法加载技能数据库")
        return

    # 获取所有技能名称
    all_moves = get_all_move_names(js_content)
    print(f"共找到 {len(all_moves)} 个技能")

    # 显示前几个技能作为示例
    if all_moves:
        print("前10个技能:", all_moves[:10])

    # 确认开始
    confirm = input("确认开始爬取? (y/n): ")
    if confirm.lower() != 'y':
        print("已取消")
        return

    # 开始批量爬取
    print("\n开始爬取...")
    successful = 0
    failed = 0
    start_time = time.time()
    total_count = len(all_moves)

    for i, move_name in enumerate(all_moves, 1):
        try:
            move_data = extract_move_data(js_content, move_name)
            if move_data:
                if save_move_data(move_name, move_data, OUTPUT_DIR):
                    successful += 1
                    # 显示进度
                    elapsed = time.time() - start_time
                    avg_time = elapsed / i
                    remaining = (total_count - i) * avg_time
                    print(f"✓ [{i}/{total_count}] {move_name} (ID: {move_data.get('num', 'N/A')}) | 预计剩余: {remaining:.1f}秒")
                else:
                    failed += 1
                    print(f"✗ [{i}/{total_count}] 保存失败: {move_name}")
            else:
                failed += 1
                print(f"✗ [{i}/{total_count}] 解析失败: {move_name}")
        except Exception as e:
            failed += 1
            print(f"✗ [{i}/{total_count}] 错误 {move_name}: {e}")

    total_time = time.time() - start_time
    print(f"\n爬取完成! 总耗时: {total_time:.2f}秒")
    print(f"成功: {successful} 只")
    print(f"失败: {failed} 只")
    print(f"平均速度: {total_count/total_time:.1f} 只/秒")
    print(f"数据保存到: {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
