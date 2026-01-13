import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time

# 设置请求头，避免被反爬
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 配置
DATA_URL = "https://play.pokemonshowdown.com/data/pokedex.js"
# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "pokemon_data_all")
IMAGE_FOLDER = os.path.join(SCRIPT_DIR, "pokemon_images")

# 创建文件夹（如果不存在）
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

def extract_pokemon_data(js_content, pokemon_key):
    """从JavaScript内容中提取特定宝可梦的数据"""
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

    # 解析types
    types_match = re.search(r'types:\s*\[([^\]]*)\]', pokemon_str)
    if types_match:
        types_str = types_match.group(1)
        types = re.findall(r'["\']([^"\']+)["\']', types_str)
        data['types'] = types

    # 解析baseStats
    stats_match = re.search(r'baseStats:\s*{([^}]*)}', pokemon_str)
    if stats_match:
        stats_str = stats_match.group(1)
        stats = {}
        stat_matches = re.findall(r'(\w+):\s*(\d+)', stats_str)
        for stat_name, value in stat_matches:
            stat_map = {'hp': 'hp', 'atk': 'atk', 'def': 'def', 'spa': 'spa', 'spd': 'spd', 'spe': 'spe'}
            if stat_name in stat_map:
                stats[stat_map[stat_name]] = int(value)
        data['baseStats'] = stats

    # 解析abilities
    abilities_match = re.search(r'abilities:\s*{([^}]*)}', pokemon_str)
    if abilities_match:
        abilities_str = abilities_match.group(1)
        abilities = {}
        ability_matches = re.findall(r'["\'](\d+|H)["\']\s*:\s*["\']([^"\']+)["\']', abilities_str)
        for key, value in ability_matches:
            abilities[key] = value
        data['abilities'] = abilities

    # 解析heightm和weightkg
    height_match = re.search(r'heightm:\s*([\d.]+)', pokemon_str)
    if height_match:
        data['heightm'] = float(height_match.group(1))

    weight_match = re.search(r'weightkg:\s*([\d.]+)', pokemon_str)
    if weight_match:
        data['weightkg'] = float(weight_match.group(1))

    return data

def get_all_pokemon_names():
    """获取所有宝可梦的名称列表"""
    print("正在获取宝可梦列表...")
    response = requests.get(DATA_URL)
    if response.status_code != 200:
        print(f"无法加载数据: {response.status_code}")
        return []

    js_content = response.text

    # 提取所有宝可梦名称
    pokemon_names = []
    # 匹配形如: bulbasaur:{...}, 的模式，但排除内部属性
    matches = re.findall(r'(\w+):\s*{', js_content)
    for match in matches:
        # 跳过非宝可梦的条目：
        # 1. 以特殊前缀开头的
        # 2. 包含大写字母的（宝可梦名称通常都是小写）
        # 3. 已知的内部属性名
        if (not match.startswith(('battle_', 'pokemons_', 'learnsets_')) and
            match.islower() and  # 只包含小写字母
            match not in ['genderratio', 'basestats', 'abilities', 'evos', 'eggmoves', 'tutor_moves',
                         'learnset', 'eventdata', 'sp', 's', 'd', 'natdex', 'gen1', 'gen2', 'gen3',
                         'gen4', 'gen5', 'gen6', 'gen7', 'gen8', 'gen9']):
            pokemon_names.append(match)

    # 按宝可梦ID排序（通过提取num字段）
    pokemon_with_ids = []
    for name in pokemon_names:
        # 从数据中提取ID进行排序
        pokemon_data = extract_pokemon_data(js_content, name)
        if pokemon_data and 'num' in pokemon_data:
            pokemon_with_ids.append((pokemon_data['num'], name))

    # 排序并返回名称列表
    pokemon_with_ids.sort()
    sorted_names = [name for _, name in pokemon_with_ids]

    return sorted_names

def get_pokemon_stats_from_web(pokemon_name):
    """从Bulbapedia网页上抓取宝可梦的详细数据"""
    # 将宝可梦名称转换为URL格式
    url_name = pokemon_name.replace(' ', '_')
    url = f"https://bulbapedia.bulbagarden.net/wiki/{url_name}_(Pok%C3%A9mon)"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        stats_data = {}

        # 抓取种族值（HP, Attack, Defense, etc.）
        # 在Bulbapedia上查找包含HP, Attack等关键词的表格
        tables = soup.find_all('table')
        print(f"  找到 {len(tables)} 个表格")

        stats_table = None
        # 查找包含HP, Attack, Defense等关键词的表格
        for table in tables:
            table_text = table.get_text()
            stat_keywords = ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
            if any(keyword in table_text for keyword in stat_keywords):
                # 检查是否包含足够的统计关键词
                keyword_count = sum(1 for keyword in stat_keywords if keyword in table_text)
                if keyword_count >= 4:  # 至少包含4个统计关键词
                    stats_table = table
                    print(f"  找到包含统计数据的表格 (包含 {keyword_count} 个关键词)")
                    break

        if stats_table:
            # 解析表格中的统计数据
            rows = stats_table.find_all('tr')
            print(f"  统计表格有 {len(rows)} 行")

            # 查找包含"Level"的行（通常是种族值行）
            for row in rows:
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]

                if 'Level' in cell_texts:
                    print(f"  找到Level行: {cell_texts}")

                    # 提取数值（通常从第2列开始是数值）
                    stat_values = []
                    for i in range(1, min(len(cells), 7)):  # 最多取6个值
                        cell_text = cells[i].get_text(strip=True)
                        if cell_text.isdigit():
                            stat_values.append(int(cell_text))

                    if len(stat_values) >= 6:
                        stats_data['hp'] = stat_values[0]
                        stats_data['attack'] = stat_values[1]
                        stats_data['defense'] = stat_values[2]
                        stats_data['sp_atk'] = stat_values[3]
                        stats_data['sp_def'] = stat_values[4]
                        stats_data['speed'] = stat_values[5]
                        print(f"  成功提取种族值: {stat_values[:6]}")
                        break
        else:
            print("  未找到统计数据表格")

        # 抓取Abilities
        abilities = []

        # 方法1：查找所有包含"Ability"的链接，但过滤掉不同形态的
        ability_links = soup.find_all('a', href=lambda href: href and 'Ability' in href and 'Category:' not in href)
        print(f"  找到 {len(ability_links)} 个ability链接")
        for link in ability_links:
            ability_name = link.get_text(strip=True)
            if (ability_name and len(ability_name) > 1 and
                ability_name not in ['Ability', 'Abilities'] and
                not ability_name.startswith('Category:') and
                ability_name[0].isupper()):  # 特性名称首字母大写
                if ability_name not in abilities:
                    abilities.append(ability_name)

        print(f"  找到 {len(abilities)} 个特性: {abilities}")
        stats_data['abilities'] = abilities

        return stats_data

    except Exception as e:
        print(f"  从Bulbapedia抓取数据失败 {pokemon_name}: {e}")
        return {}

def get_pokemon_data(pokemon_name, js_content):
    """从预加载的数据中获取单个宝可梦的数据，如果JS数据不完整则从网页补充"""
    pokemon_key = pokemon_name.lower()

    # 提取JS数据作为基础数据
    pokemon = extract_pokemon_data(js_content, pokemon_key)
    if not pokemon:
        return None

    data = {}

    # 1. 获取 ID 和名字（从JS数据）
    data['id'] = pokemon.get('num')
    data['name'] = pokemon.get('name', '')

    # 2. 获取属性（type1, type2）（从JS数据）
    types = pokemon.get('types', [])
    data['type1'] = types[0] if types else None
    data['type2'] = types[1] if len(types) > 1 else None

    # 3. 获取种族值（优先使用JS数据，其次从网页抓取）
    base_stats = pokemon.get('baseStats', {})
    has_base_stats = bool(base_stats)

    data['hp'] = base_stats.get('hp', 0)
    data['attack'] = base_stats.get('atk', 0)
    data['defense'] = base_stats.get('def', 0)
    data['sp_atk'] = base_stats.get('spa', 0)
    data['sp_def'] = base_stats.get('spd', 0)
    data['speed'] = base_stats.get('spe', 0)

    # 如果JS数据中没有baseStats，从网页抓取
    if not has_base_stats:
        print(f"JS数据不完整，从网页补充 {pokemon_name} 的数据...")
        web_data = get_pokemon_stats_from_web(pokemon_name)
        if web_data.get('hp'):
            data['hp'] = web_data['hp']
            data['attack'] = web_data['attack']
            data['defense'] = web_data['defense']
            data['sp_atk'] = web_data['sp_atk']
            data['sp_def'] = web_data['sp_def']
            data['speed'] = web_data['speed']
            print(f"网页数据补充成功: HP={data['hp']}, Attack={data['attack']}")

    data['total'] = sum(data.get(stat, 0) for stat in ['hp', 'attack', 'defense', 'sp_atk', 'sp_def', 'speed'])

    # 4. 获取特性（优先使用JS数据，其次从网页抓取）
    abilities = pokemon.get('abilities', {})
    has_abilities = bool(abilities)

    data['abilities'] = [name for name in abilities.values() if name]

    # 如果JS数据中没有abilities，从网页抓取
    if not has_abilities:
        if 'web_data' not in locals():
            web_data = get_pokemon_stats_from_web(pokemon_name)
        if web_data.get('abilities'):
            data['abilities'] = web_data['abilities']
            print(f"网页数据补充特性: {data['abilities']}")

    # 5. 获取身高体重（从JS数据）
    data['height'] = pokemon.get('heightm', 0)
    data['weight'] = pokemon.get('weightkg', 0)

    # 6. 获取图片 URL（构造Pokemon Showdown的图片URL）
    if data['id']:
        sprite_url = f"https://play.pokemonshowdown.com/sprites/ani/{pokemon_key}.gif"
        data['image_url'] = sprite_url

        # 下载图片并保存
        filename = f"{data['id']}_{pokemon_key}.gif"
        filepath = os.path.join(IMAGE_FOLDER, filename)
        try:
            img_response = requests.get(sprite_url, timeout=10)
            if img_response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                data['image_path'] = filepath
        except Exception as e:
            print(f"下载图片失败 {pokemon_name}: {e}")

    return data

def main():
    print("=" * 50)
    print("宝可梦数据批量爬虫")
    print("=" * 50)

    # 获取所有宝可梦名称
    all_pokemon = get_all_pokemon_names()
    print(f"共找到 {len(all_pokemon)} 只宝可梦")

    # 预加载数据文件
    print("正在预加载宝可梦数据库...")
    response = requests.get(DATA_URL)
    if response.status_code != 200:
        print(f"无法加载数据库: {response.status_code}")
        return
    js_content = response.text

    # 用户选择范围（按宝可梦ID编号）
    print("\n请选择爬取范围 (按宝可梦全国图鉴编号):")
    print(f"数据库中共有 {len(all_pokemon)} 只宝可梦")

    # 找出可用的ID范围
    pokemon_ids = []
    for name in all_pokemon:
        # 快速提取ID
        pattern = rf'{re.escape(name)}:\s*{{[^}}]*?num:\s*(\d+)'
        match = re.search(pattern, js_content)
        if match:
            pokemon_ids.append(int(match.group(1)))

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
        # 提取该宝可梦的ID
        pattern = rf'{re.escape(name)}:\s*{{[^}}]*?num:\s*(\d+)'
        match = re.search(pattern, js_content)
        if match:
            pokemon_id = int(match.group(1))
            if start_id <= pokemon_id <= end_id:
                selected_pokemon.append(name)

    print(f"\n将爬取ID从 {start_id} 到 {end_id} 的宝可梦，共 {len(selected_pokemon)} 只")
    if selected_pokemon:
        print(f"范围: {selected_pokemon[0]} (ID: {start_id}) 到 {selected_pokemon[-1]} (ID: {end_id})")

    # 确认开始
    confirm = input("确认开始爬取? (y/n): ")
    if confirm.lower() != 'y':
        print("已取消")
        return

    # 开始批量爬取
    print("\n开始爬取...")
    successful = 0
    failed = 0

    for i, pokemon_name in enumerate(selected_pokemon, 1):
        try:
            data = get_pokemon_data(pokemon_name, js_content)
            if data:
                # 保存单个宝可梦数据
                filename = f"{data['id']}_{pokemon_name}.json"
                filepath = os.path.join(OUTPUT_DIR, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                successful += 1
            else:
                failed += 1

        except Exception as e:
            print(f"爬取失败 {pokemon_name}: {e}")
            failed += 1

        # 显示进度
        progress = (i / len(selected_pokemon)) * 100
        print(f"\r进度: {i}/{len(selected_pokemon)} ({progress:.1f}%) - 成功:{successful} 失败:{failed}", end="", flush=True)

        time.sleep(0.1)  # 避免请求过快

    print()  # 换行

    print("\n爬取完成!")
    print(f"成功: {successful} 只")
    print(f"失败: {failed} 只")
    print(f"数据保存到: {OUTPUT_DIR}/")
    print(f"图片保存到: {IMAGE_FOLDER}/")

if __name__ == "__main__":
    main()
