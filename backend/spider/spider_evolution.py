import requests
import re
import json
import os
import time
from bs4 import BeautifulSoup  # 保留以防万一，但现在不用
# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "pokemon_evolutions")

# 创建文件夹（如果不存在）
os.makedirs(OUTPUT_DIR, exist_ok=True)

DATA_URL = "https://play.pokemonshowdown.com/data/pokedex.js"

def get_js_content():
    """获取Pokemon Showdown的JS数据内容"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(DATA_URL, headers=headers)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return None
    return response.text

def extract_evolution_chain(js_content, pokemon_name):
    """从JS内容中提取特定宝可梦的进化链"""
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

    # 解析evos
    evos_match = re.search(r'evos:\s*\[([^\]]*)\]', pokemon_str)
    if evos_match:
        evos_str = evos_match.group(1)
        evos = re.findall(r'["\']([^"\']+)["\']', evos_str)
        return evos

    return []


def get_evolution_chain(pokemon_name, js_content=None):
    """获取宝可梦进化链"""
    if js_content is None:
        js_content = get_js_content()
        if not js_content:
            return None

    # 预构建进化关系映射，提高查找效率
    if not hasattr(get_evolution_chain, '_evo_map'):
        get_evolution_chain._evo_map = {}
        all_names = get_all_pokemon_names(js_content)
        for name in all_names:
            evos = extract_evolution_chain(js_content, name)
            if evos:
                for evo in evos:
                    evo_key = evo.lower()
                    if evo_key not in get_evolution_chain._evo_map:
                        get_evolution_chain._evo_map[evo_key] = []
                    get_evolution_chain._evo_map[evo_key].append(name)

    # 递归查找前置进化
    def find_pre_evolutions(poke_name):
        pre_evos = []
        poke_key = poke_name.lower()
        if poke_key in get_evolution_chain._evo_map:
            for pre_evo in get_evolution_chain._evo_map[poke_key]:
                pre_evos.append(pre_evo)
                # 递归查找更前面的进化
                pre_evos.extend(find_pre_evolutions(pre_evo))
        return pre_evos

    # 获取前置进化
    pre_chain = find_pre_evolutions(pokemon_name)
    pre_chain.reverse()  # 反转顺序，从最早的开始

    # 从当前宝可梦开始，递归获取所有后续进化
    def build_full_chain(poke_name):
        chain = [poke_name]
        evolutions = extract_evolution_chain(js_content, poke_name)
        if evolutions:
            for evo in evolutions:
                chain.extend(build_full_chain(evo))
        return chain

    # 合并前置 + 当前及后续
    full_chain = pre_chain + build_full_chain(pokemon_name)

    # 去重（处理分支进化）
    seen = set()
    unique_chain = []
    for poke in full_chain:
        if poke.lower() not in seen:
            seen.add(poke.lower())
            unique_chain.append(poke)

    return unique_chain

def get_all_pokemon_names(js_content):
    """从JS内容中获取所有宝可梦名称"""
    # 匹配形如: bulbasaur:{...}, 的模式，但排除内部属性
    matches = re.findall(r'(\w+):\s*{', js_content)
    pokemon_names = []
    for match in matches:
        # 跳过非宝可梦的条目
        if (not match.startswith(('battle_', 'pokemons_', 'learnsets_')) and
            match.islower() and  # 只包含小写字母
            match not in ['genderratio', 'basestats', 'abilities', 'evos', 'eggmoves', 'tutor_moves',
                         'learnset', 'eventdata', 'sp', 's', 'd', 'natdex', 'gen1', 'gen2', 'gen3',
                         'gen4', 'gen5', 'gen6', 'gen7', 'gen8', 'gen9']):
            pokemon_names.append(match)
    return pokemon_names

def extract_pokemon_id(js_content, pokemon_name):
    """从JS内容中提取宝可梦ID"""
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

    # 解析num
    num_match = re.search(r'num:\s*(\d+)', pokemon_str)
    if num_match:
        return int(num_match.group(1))

    return None

def get_all_pokemon_with_ids(js_content):
    """获取所有宝可梦名称和ID，按ID排序"""
    all_names = get_all_pokemon_names(js_content)
    pokemon_with_ids = []

    for name in all_names:
        pokemon_id = extract_pokemon_id(js_content, name)
        if pokemon_id:
            pokemon_with_ids.append((pokemon_id, name))

    # 按ID排序
    pokemon_with_ids.sort()
    return pokemon_with_ids

def save_evolution_data(pokemon_name, evolution_chain, output_dir, js_content):
    """保存单个宝可梦的进化链数据"""
    # 获取宝可梦ID用于文件名
    pokemon_id = extract_pokemon_id(js_content, pokemon_name)
    if not pokemon_id:
        print(f"无法获取 {pokemon_name} 的ID")
        return False

    data = {
        "id": pokemon_id,
        "name": pokemon_name,
        "evolution_chain": evolution_chain
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

def main():
    print("=" * 50)
    print("宝可梦进化链批量爬虫")
    print("=" * 50)

    # 预加载数据文件
    print("正在预加载宝可梦数据库...")
    js_content = get_js_content()
    if not js_content:
        print("无法加载数据库")
        return

    # 获取所有宝可梦
    all_pokemon = get_all_pokemon_with_ids(js_content)
    print(f"共找到 {len(all_pokemon)} 只宝可梦")

    # 用户选择范围（按宝可梦ID编号）
    print("\n请选择爬取范围 (按宝可梦全国图鉴编号):")
    print(f"数据库中共有 {len(all_pokemon)} 只宝可梦")

    # 找出可用的ID范围
    if all_pokemon:
        min_id = all_pokemon[0][0]
        max_id = all_pokemon[-1][0]
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
    for pokemon_id, name in all_pokemon:
        if start_id <= pokemon_id <= end_id:
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
            evolution_chain = get_evolution_chain(pokemon_name, js_content)
            if evolution_chain:
                if save_evolution_data(pokemon_name, evolution_chain, OUTPUT_DIR, js_content):
                    successful += 1
                    # 显示进度和时间估计
                    elapsed = time.time() - start_time
                    avg_time = elapsed / i
                    remaining = (total_count - i) * avg_time
                    print(f"✓ [{i}/{total_count}] {pokemon_name} (ID: {pokemon_id}): {' → '.join(evolution_chain)} | 预计剩余: {remaining:.1f}秒")
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
    main()

# 使用示例（如果直接运行该函数）
# evolution = get_evolution_chain("venusaur")
# if evolution:
#     print(" → ".join(evolution))
