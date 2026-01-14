import requests
import re
import json
import os
import time

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "pokemon_moves_data")

# 创建文件夹（如果不存在）
os.makedirs(OUTPUT_DIR, exist_ok=True)

LEARNSETS_URL = "https://play.pokemonshowdown.com/data/learnsets.js"
POKEDEX_URL = "https://play.pokemonshowdown.com/data/pokedex.js"

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

def extract_learnset_data(js_content, pokemon_name):
    """从JS内容中提取特定宝可梦的learnset数据"""
    pokemon_key = pokemon_name.lower()

    # 查找特定的宝可梦数据
    start_pattern = rf'{re.escape(pokemon_key)}:\s*{{'
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

    pokemon_str = js_content[start_pos:end_pos]

    # 解析learnset
    learnset_match = re.search(r'learnset:\s*{([^}]*)}', pokemon_str)
    if not learnset_match:
        return None

    learnset_str = learnset_match.group(1)

    # 解析每个技能的学习方式
    moves = {}

    # 匹配形如: skillname:["method1","method2"], 的模式
    move_matches = re.findall(r'(\w+):\s*\[([^\]]*)\]', learnset_str)

    for move_name, methods_str in move_matches:
        # 解析学习方式
        methods = re.findall(r'["\']([^"\']+)["\']', methods_str)
        moves[move_name] = methods

    return moves

def categorize_moves(moves):
    """将技能按学习方式分类"""
    level_up = []  # 升级学会
    egg_moves = []  # 蛋招式
    tm_moves = []  # 技能机器
    tutor_moves = []  # 自学招式

    for move_name, methods in moves.items():
        for method in methods:
            # 解析学习方式
            if method.endswith('E'):
                # 蛋招式
                if move_name not in egg_moves:
                    egg_moves.append(move_name)
            elif method.endswith('T'):
                # 自学招式 (Tutor)
                if move_name not in tutor_moves:
                    tutor_moves.append(move_name)
            elif 'M' in method:
                # 技能机器 (TM/HM)
                if move_name not in tm_moves:
                    tm_moves.append(move_name)
            elif re.match(r'\d+L\d+', method):
                # 升级学会 (Level up)
                if move_name not in level_up:
                    level_up.append(move_name)

    return {
        "level_up": level_up,
        "egg_moves": egg_moves,
        "tm_moves": tm_moves,
        "tutor_moves": tutor_moves
    }

def get_all_pokemon_names(pokedex_js):
    """从pokedex.js中获取所有宝可梦名称"""
    # 匹配形如: bulbasaur:{...}, 的模式，但排除内部属性
    matches = re.findall(r'(\w+):\s*{', pokedex_js)
    pokemon_names = []
    for match in matches:
        # 跳过非宝可梦的条目
        if (not match.startswith(('battle_', 'pokemons_', 'learnsets_')) and
            match.islower() and  # 只包含小写字母
            match not in ['genderratio', 'basestats', 'abilities', 'evos', 'eggmoves', 'tutor_moves',
                         'learnset', 'eventdata', 'sp', 's', 'd', 'natdex', 'gen1', 'gen2', 'gen3',
                         'gen4', 'gen5', 'gen6', 'gen7', 'gen8', 'gen9']):
            pokemon_names.append(match)

    # 按宝可梦ID排序
    pokemon_with_ids = []
    for name in pokemon_names:
        # 从数据中提取ID进行排序
        pokemon_id = extract_pokemon_id(pokedex_js, name)
        if pokemon_id:
            pokemon_with_ids.append((pokemon_id, name))

    # 排序并返回名称列表
    pokemon_with_ids.sort()
    sorted_names = [name for _, name in pokemon_with_ids]

    return sorted_names

def extract_pokemon_id(pokedex_js, pokemon_name):
    """从pokedex.js中提取宝可梦ID"""
    pokemon_key = pokemon_name.lower()

    # 查找特定的宝可梦数据
    start_pattern = rf'{re.escape(pokemon_key)}:\s*{{'
    start_match = re.search(start_pattern, pokedex_js)

    if not start_match:
        return None

    start_pos = start_match.end() - 1

    # 计算大括号平衡
    brace_count = 0
    end_pos = start_pos

    for i in range(start_pos, len(pokedex_js)):
        if pokedex_js[i] == '{':
            brace_count += 1
        elif pokedex_js[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_pos = i + 1
                break

    if brace_count != 0:
        return None

    pokemon_str = pokedex_js[start_pos:end_pos]

    # 解析num
    num_match = re.search(r'num:\s*(\d+)', pokemon_str)
    if num_match:
        return int(num_match.group(1))

    return None

def save_pokemon_moves_data(pokemon_name, moves_data, output_dir, pokemon_id):
    """保存单个宝可梦的技能数据"""
    if not moves_data:
        return False

    data = {
        "id": pokemon_id,
        "name": pokemon_name,
        **moves_data
    }

    filename = f"{pokemon_id}_{pokemon_name}.json"
    filepath = os.path.join(output_dir, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存 {pokemon_name} 数据失败: {e}")
        return False

def test_first_three():
    """测试前3只宝可梦"""
    print("=" * 50)
    print("宝可梦技能学习数据测试 (前3只)")
    print("=" * 50)

    # 预加载数据文件
    print("正在预加载宝可梦数据库...")
    pokedex_js = get_js_content(POKEDEX_URL)
    if not pokedex_js:
        print("无法加载宝可梦数据库")
        return

    print("正在预加载技能学习数据库...")
    learnsets_js = get_js_content(LEARNSETS_URL)
    if not learnsets_js:
        print("无法加载技能学习数据库")
        return

    # 清理JS内容，移除exports部分
    if learnsets_js.startswith('exports.BattleLearnsets = '):
        learnsets_js = learnsets_js[len('exports.BattleLearnsets = '):]

    # 获取所有宝可梦
    all_pokemon = get_all_pokemon_names(pokedex_js)
    print(f"共找到 {len(all_pokemon)} 只宝可梦")

    # 测试前3只宝可梦
    test_pokemon = all_pokemon[:3]

    print("\n开始测试爬取...")
    successful = 0
    failed = 0
    start_time = time.time()

    for i, pokemon_name in enumerate(test_pokemon, 1):
        try:
            # 获取宝可梦ID
            pokemon_id = extract_pokemon_id(pokedex_js, pokemon_name)

            # 获取原始learnset数据
            raw_moves = extract_learnset_data(learnsets_js, pokemon_name)

            if raw_moves and pokemon_id:
                # 分类技能
                categorized_moves = categorize_moves(raw_moves)

                # 保存数据
                if save_pokemon_moves_data(pokemon_name, categorized_moves, OUTPUT_DIR, pokemon_id):
                    successful += 1
                    print(f"✓ [{i}/3] {pokemon_name} (ID: {pokemon_id}) | 升级:{len(categorized_moves['level_up'])}, 蛋:{len(categorized_moves['egg_moves'])}, TM:{len(categorized_moves['tm_moves'])}, 自学:{len(categorized_moves['tutor_moves'])}")

                    # 显示前5个升级技能作为示例
                    if categorized_moves['level_up']:
                        print(f"  升级技能示例: {categorized_moves['level_up'][:5]}")
                    if categorized_moves['egg_moves']:
                        print(f"  蛋技能示例: {categorized_moves['egg_moves'][:5]}")
                    if categorized_moves['tm_moves']:
                        print(f"  TM技能示例: {categorized_moves['tm_moves'][:5]}")
                    if categorized_moves['tutor_moves']:
                        print(f"  自学技能示例: {categorized_moves['tutor_moves'][:5]}")
                else:
                    failed += 1
                    print(f"✗ [{i}/3] 保存失败: {pokemon_name}")
            else:
                failed += 1
                print(f"✗ [{i}/3] 获取失败: {pokemon_name}")
        except Exception as e:
            failed += 1
            print(f"✗ [{i}/3] 错误 {pokemon_name}: {e}")

    total_time = time.time() - start_time
    print(f"\n测试完成! 总耗时: {total_time:.2f}秒")
    print(f"成功: {successful} 只")
    print(f"失败: {failed} 只")
    print(f"数据保存到: {OUTPUT_DIR}/")

def main():
    print("=" * 50)
    print("宝可梦技能学习数据批量爬虫")
    print("=" * 50)

    # 预加载数据文件
    print("正在预加载宝可梦数据库...")
    pokedex_js = get_js_content(POKEDEX_URL)
    if not pokedex_js:
        print("无法加载宝可梦数据库")
        return

    print("正在预加载技能学习数据库...")
    learnsets_js = get_js_content(LEARNSETS_URL)
    if not learnsets_js:
        print("无法加载技能学习数据库")
        return

    # 清理JS内容，移除exports部分
    if learnsets_js.startswith('exports.BattleLearnsets = '):
        learnsets_js = learnsets_js[len('exports.BattleLearnsets = '):]

    # 获取所有宝可梦
    all_pokemon = get_all_pokemon_names(pokedex_js)
    print(f"共找到 {len(all_pokemon)} 只宝可梦")

    # 显示前几个宝可梦作为示例
    if all_pokemon:
        print("前5只宝可梦:", all_pokemon[:5])

    # 用户选择范围
    print("\n请选择爬取范围 (按宝可梦全国图鉴编号):")
    print(f"数据库中共有 {len(all_pokemon)} 只宝可梦")

    # 找出可用的ID范围
    pokemon_ids = []
    for name in all_pokemon:
        pokemon_id = extract_pokemon_id(pokedex_js, name)
        if pokemon_id:
            pokemon_ids.append(pokemon_id)

    if pokemon_ids:
        min_id = min(pokemon_ids)
        max_id = max(pokemon_ids)
        print(f"宝可梦ID范围: {min_id} - {max_id}")

    try:
        start_id = int(input("从哪个ID开始爬取 (如: 1): ") or "1")
        end_id = int(input("爬取到哪个ID结束 (如: 151): ") or "151")

        if start_id < 1:
            start_id = 1
        if end_id < start_id:
            start_id, end_id = end_id, start_id

    except ValueError:
        print("输入无效，使用默认范围 (1-151)")
        start_id = 1
        end_id = 151

    # 根据ID范围筛选宝可梦
    selected_pokemon = []
    for name in all_pokemon:
        pokemon_id = extract_pokemon_id(pokedex_js, name)
        if pokemon_id and start_id <= pokemon_id <= end_id:
            selected_pokemon.append((pokemon_id, name))

    print(f"\n将爬取ID从 {start_id} 到 {end_id} 的宝可梦，共 {len(selected_pokemon)} 只")
    if selected_pokemon:
        print(f"范围: {selected_pokemon[0][1]} (ID: {selected_pokemon[0][0]}) 到 {selected_pokemon[-1][1]} (ID: {selected_pokemon[-1][0]})")

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
    total_count = len(selected_pokemon)

    for i, (pokemon_id, pokemon_name) in enumerate(selected_pokemon, 1):
        try:
            # 获取原始learnset数据
            raw_moves = extract_learnset_data(learnsets_js, pokemon_name)

            if raw_moves:
                # 分类技能
                categorized_moves = categorize_moves(raw_moves)

                # 保存数据
                if save_pokemon_moves_data(pokemon_name, categorized_moves, OUTPUT_DIR, pokemon_id):
                    successful += 1
                    # 显示进度
                    elapsed = time.time() - start_time
                    avg_time = elapsed / i
                    remaining = (total_count - i) * avg_time
                    print(f"✓ [{i}/{total_count}] {pokemon_name} (ID: {pokemon_id}) | 升级:{len(categorized_moves['level_up'])}, 蛋:{len(categorized_moves['egg_moves'])}, TM:{len(categorized_moves['tm_moves'])}, 自学:{len(categorized_moves['tutor_moves'])} | 预计剩余: {remaining:.1f}秒")
                else:
                    failed += 1
                    print(f"✗ [{i}/{total_count}] 保存失败: {pokemon_name}")
            else:
                failed += 1
                print(f"✗ [{i}/{total_count}] 获取失败: {pokemon_name}")
        except Exception as e:
            failed += 1
            print(f"✗ [{i}/{total_count}] 错误 {pokemon_name}: {e}")

    total_time = time.time() - start_time
    print(f"\n爬取完成! 总耗时: {total_time:.2f}秒")
    print(f"成功: {successful} 只")
    print(f"失败: {failed} 只")
    print(f"平均速度: {total_count/total_time:.1f} 只/秒")
    print(f"数据保存到: {OUTPUT_DIR}/")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_first_three()
    else:
        main()
