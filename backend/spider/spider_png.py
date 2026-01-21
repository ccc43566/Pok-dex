import aiohttp
import asyncio
import aiofiles
import os
import re
import json
import sys
import argparse

# 设置请求头，避免被反爬
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 配置
DATA_URL = "https://play.pokemonshowdown.com/data/pokedex.js"
# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "pokemon_png_images")
MISSING_FOLDER = os.path.join(SCRIPT_DIR, "爬取图片失败的宝可梦")
MISSING_FILE = os.path.join(MISSING_FOLDER, "missing_png_images.txt")

# 创建文件夹（如果不存在）
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MISSING_FOLDER, exist_ok=True)

def extract_pokemon_data(js_content, pokemon_key):
    """从JavaScript内容中提取特定宝可梦的数据"""
    # 查找特定的宝可梦数据，使用平衡大括号匹配
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

async def get_all_pokemon_names():
    """获取所有宝可梦的名称列表"""
    print("正在获取宝可梦列表...")
    async with aiohttp.ClientSession() as session:
        async with session.get(DATA_URL) as response:
            if response.status != 200:
                print(f"无法加载数据: {response.status}")
                return []
            js_content = await response.text()

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

async def download_pokemon_png(session, pokemon_name, pokemon_id, correct_key, missing_pokemon):
    """下载单个宝可梦的静态图片"""
    # 尝试下载静态图片
    static_urls = [
        f"https://play.pokemonshowdown.com/sprites/gen5/{correct_key}.png",
        f"https://play.pokemonshowdown.com/sprites/pokemon/{correct_key}.png",
        f"https://play.pokemonshowdown.com/sprites/pokemon/{pokemon_id}.png"
    ]

    for url in static_urls:
        filename = f"{pokemon_id}_{correct_key}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as img_response:
                if img_response.status == 200:
                    content = await img_response.read()
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(content)
                    print(f"下载静态图片成功: {pokemon_name} (ID: {pokemon_id})")
                    return True
        except Exception as e:
            print(f"尝试下载图片失败 {url}: {e}")

    # 如果所有URL都失败
    missing_pokemon.append(pokemon_name)
    print(f"所有静态图片URL都失败: {pokemon_name}")
    return False

async def main():
    print("=" * 50)
    print("宝可梦静态图片批量爬虫")
    print("=" * 50)

    # 获取所有宝可梦名称
    all_pokemon = await get_all_pokemon_names()
    print(f"共找到 {len(all_pokemon)} 只宝可梦")

    # 预加载数据文件
    print("正在预加载宝可梦数据库...")
    async with aiohttp.ClientSession() as session:
        async with session.get(DATA_URL) as response:
            if response.status != 200:
                print(f"无法加载数据库: {response.status}")
                return
            js_content = await response.text()

    # 设置命令行参数
    parser = argparse.ArgumentParser(description='宝可梦静态图片批量爬虫')
    parser.add_argument('--start-id', type=int, default=1, help='开始爬取的宝可梦ID')
    parser.add_argument('--end-id', type=int, help='结束爬取的宝可梦ID')
    parser.add_argument('--all', action='store_true', help='爬取所有宝可梦')
    args = parser.parse_args()

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

    # 确定爬取范围
    start_id = args.start_id
    end_id = args.end_id

    if args.all:
        # 爬取所有宝可梦
        start_id = min_id
        end_id = max_id
    else:
        # 如果没有指定end_id，默认爬取到最大ID
        if not end_id:
            end_id = max_id

        # 确保范围有效
        if start_id < 1:
            start_id = 1
        if end_id < start_id:
            start_id, end_id = end_id, start_id
        if end_id > max_id:
            end_id = max_id

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

    # 构建正确的名称映射，用于图片URL
    # 已知变体后缀列表
    variant_suffixes = {
        'mega', 'gmax', 'x', 'y', 'attack', 'defense', 'speed', 'alola', 'galar', 'hisui', 'paldea',
        'sandy', 'trash', 'sunny', 'rainy', 'snowy', 'fan', 'frost', 'heat', 'mow', 'wash', 'crowned',
        'eternal', 'terastal', 'stellar', 'therian', 'incarnate', 'sky', 'black', 'white', 'resolute',
        'pirouette', 'ash', 'origin', 'land', 'speed', 'alolatotem', 'paldeaaqua', 'paldeacombat',
        'paldeablaze', 'starter', 'megaz', 'primal', 'sunshine', 'bug', 'dark', 'fire', 'dragon',
        'flying', 'electric', 'fairy', 'ice', 'grass', 'psychic', 'rock', 'poison', 'water', 'ground',
        'fighting', 'ghost', 'steel', 'bluestriped', 'whitestriped', 'galarzen', 'zen', 'bond',
        'pokeball', 'fancy', 'blade', 'small', 'large', 'super', 'neutral', 'complete', 'unbound',
        '10', 'totem', 'pompom', 'pau', 'sensu', 'dusk', 'school', 'midnight', 'busted',
        'bustedtotem', 'dawnwings', 'duskmane', 'ultra', 'originalmega', 'original', 'gorging',
        'gulping', 'lowkey', 'lowkeygmax', 'antique', 'noice', 'hangry', 'rapidstrike',
        'rapidstrikegmax', 'eternamax', 'dada', 'shadow', 'bloodmoon', 'four', 'blue', 'yellow',
        'white', 'hero', 'droopy', 'stretchy', 'curly', 'threesegment', 'roaming', 'hearthflame',
        'cornerstone', 'tealtera', 'cornerstonetera', 'hearthflametera', 'wellspring',
        'wellspringtera'
    }

    correct_names = {}
    previous_base = None
    for name in selected_pokemon:
        lower_name = name.lower()
        if previous_base and lower_name.startswith(previous_base):
            suffix = lower_name[len(previous_base):]
            # 检查suffix是否以已知变体开头，并且剩余部分也是变体或空
            converted = False
            for suffix_candidate in sorted(variant_suffixes, key=len, reverse=True):
                if suffix.startswith(suffix_candidate):
                    remaining = suffix[len(suffix_candidate):]
                    if remaining == "" or remaining in variant_suffixes:
                        formatted_suffix = f"{suffix_candidate}{remaining}"
                        correct_names[lower_name] = f"{previous_base}-{formatted_suffix}"
                        converted = True
                        break
            if not converted:
                # 不是变体，设置为基础名称
                correct_names[lower_name] = lower_name
                previous_base = lower_name
        else:
            # 基础名称
            correct_names[lower_name] = lower_name
            previous_base = lower_name

    # 如果使用任何命令行参数，直接开始下载，否则询问确认
    if len(sys.argv) > 1:
        confirm = 'y'
    else:
        confirm = input("确认开始下载静态图片? (y/n): ")
        
    if confirm.lower() != 'y':
        print("已取消")
        return

    # 开始批量下载
    print("\n开始下载静态图片...")
    successful = 0
    failed = 0
    missing_pokemon = []

    # 限制并发数为10，避免过多的并发请求
    semaphore = asyncio.Semaphore(10)

    async def process_pokemon(pokemon_name):
        nonlocal successful, failed
        async with semaphore:
            try:
                # 从预加载的数据中提取宝可梦信息
                pokemon = extract_pokemon_data(js_content, pokemon_name.lower())
                if not pokemon:
                    print(f"无法获取宝可梦数据: {pokemon_name}")
                    failed += 1
                    return

                pokemon_id = pokemon.get('num')
                if not pokemon_id:
                    print(f"无法获取宝可梦ID: {pokemon_name}")
                    failed += 1
                    return

                correct_key = correct_names.get(pokemon_name.lower(), pokemon_name.lower())

                success = await download_pokemon_png(session, pokemon_name, pokemon_id, correct_key, missing_pokemon)
                if success:
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"处理宝可梦失败 {pokemon_name}: {e}")
                failed += 1

    # 创建会话用于下载
    async with aiohttp.ClientSession(headers=headers) as session:
        # 并发处理所有宝可梦
        tasks = [process_pokemon(pokemon_name) for pokemon_name in selected_pokemon]
        await asyncio.gather(*tasks)

    print()  # 换行

    print("\n下载完成!")
    print(f"成功: {successful} 只")
    print(f"失败: {failed} 只")
    print(f"静态图片保存到: {OUTPUT_DIR}/")

    # 保存缺失图片的宝可梦列表
    if missing_pokemon:
        with open(MISSING_FILE, 'w', encoding='utf-8') as f:
            for name in missing_pokemon:
                f.write(name + '\n')
        print(f"缺失静态图片的宝可梦已保存到: {MISSING_FILE}")
    else:
        print("所有宝可梦静态图片均下载成功！")

if __name__ == "__main__":
    asyncio.run(main())
