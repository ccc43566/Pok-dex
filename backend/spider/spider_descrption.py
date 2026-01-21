# 存在  爬取多个宝可梦，有部分缺失信息。
import aiohttp
from bs4 import BeautifulSoup
import json
import os
import re
import asyncio
import aiofiles

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
    pokemon_key_lower = pokemon_key.lower()

    # 查找特定的宝可梦数据，使用更精确的匹配
    start_pattern = rf'{re.escape(pokemon_key_lower)}:\s*{{'
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

async def get_pokemon_description_from_52poke(pokemon_name_en, session):
    """从52poke获取宝可梦的中文描述"""
    # 对单引号进行URL编码
    encoded_name = pokemon_name_en.replace("'", "%27")

    # 特殊处理包含特殊字符的宝可梦名称
    if encoded_name == "Type: Null":
        # Type: Null 在52poke上可能受到访问限制，返回默认描述
        return "Type: Null（日文︰タイプ：ヌル，英文︰Type: Null）是人工宝可梦，牠是由一位名叫札格的科学家制造出来的。Type: Null是第一世代以来第一只同时拥有一般和幽灵两种属性的宝可梦。牠的设定是为了测试RKS系统而被创造出来的实验性宝可梦。"

    # 构造URL列表：先尝试完整名称，再尝试基础名称
    base_name = encoded_name
    form_suffixes = [
        '-Alola', '-Mega', '-Galar', '-Hisui', '-Paldea', '-Gmax', '-Totem', '-Z', '-Blade', '-Shield',
        '-Pom-Pom', '-Pa', '-Sensu', '-Dusk', '-Midnight', '-School',
        '-Bug', '-Dragon', '-Dark', '-Electric', '-Fairy', '-Fire', '-Fighting', '-Flying', '-Ghost', '-Ground', '-Grass', '-Ice', '-Poison', '-Psychic', '-Water', '-Steel', '-Rock',
        '-Meteor', '-Busted', '-Low-Key', '-Antique', '-Four', '-White', '-Blue', '-Yellow', '-Hero',
        '-Curly', '-Droopy', '-Stretchy', '-Three-Segment', '-Roaming', '-Artisan', '-Masterpiece',
        '-Hoenn', '-Cosplay', '-Belle', '-Libre', '-PhD', '-Pop-Star', '-Partner', '-Rock-Star', '-Sinnoh', '-Unova', '-Starter', '-World', '-Original',
        '-Mega-X', '-Mega-Y', '-F', '-M', '-Galar', '-Paldea-Blaze', '-Paldea-Aqua', '-Paldea-Combat', '-Spiky-eared', '-Snowy', '-Sunny', '-Rainy',
        '-Primal', '-Defense', '-Attack', '-Speed', '-Sandy', '-Trash', '-Sunshine', '-Fan', '-Wash', '-Frost', '-Mow', '-Heat', '-Origin', '-Sky',
        '-White-Striped', '-Blue-Striped', '-Galar-Zen', '-Zen', '-Therian', '-Black', '-Resolute', '-Pirouette', '-Burn', '-Douse', '-Chill', '-Shock',
        '-Ash', '-Bond', '-Pokeball', '-Fancy', '-Eternal', '-F-Mega', '-M-Mega', '-Small', '-Large', '-Super', '-Neutral', '-Complete', '-10%',
        '-Unbound', '-Dusk-Mane', '-Ultra', '-Dawn-Wings', '-Original-Mega', '-Gorging', '-Gulping', '-Noice', '-Hangry', '-Crowned', '-Eternamax',
        '-Rapid-Strike', '-Rapid-Strike-Gmax', '-Dada', '-Shadow', '-Bloodmoon', '-Cornerstone', '-Cornerstone-Tera', '-Hearthflame-Tera', '-Hearthflame',
        '-Wellspring', '-Teal-Tera', '-Wellspring-Tera', '-Terastal', '-Stellar'
    ]
    # 循环去掉所有匹配的后缀
    while any(base_name.endswith(suffix) for suffix in form_suffixes):
        for suffix in form_suffixes:
            if base_name.endswith(suffix):
                base_name = base_name[:-len(suffix)]
                break

    # 特殊处理：某些宝可梦的页面名称特殊
    if base_name == "Nidoran":
        # Nidoran有雌雄之分，需要根据完整名称判断
        if "F" in pokemon_name_en:
            base_name = "Nidoran♀"
        elif "M" in pokemon_name_en:
            base_name = "Nidoran♂"

    urls = [f"https://wiki.52poke.com/wiki/{encoded_name}", f"https://wiki.52poke.com/wiki/{base_name}"]

    for url in urls:
        # 重试机制：最多重试2次
        for attempt in range(3):
            try:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        if attempt == 2:  # 最后一次重试
                            print(f"HTTP错误 {pokemon_name_en}: {response.status}")
                        await asyncio.sleep(0.3 * (attempt + 1))  # 递增延迟
                        continue

                    content = await response.read()
                    soup = BeautifulSoup(content, 'html.parser')

                # 找到正文容器
                content_div = soup.find('div', id='mw-content-text')
                if not content_div:
                    if attempt == 2:
                        print(f"未找到内容容器 {pokemon_name_en}")
                    await asyncio.sleep(0.3 * (attempt + 1))
                    continue

                # 获取所有 <p> 标签
                all_p_tags = content_div.find_all('p')

                # 过滤掉不包含宝可梦描述的段落
                valid_descriptions = []
                for p_tag in all_p_tags:
                    p_text = p_tag.get_text(strip=True)
                    # 跳过太短的段落、包含特定关键词的段落
                    if (len(p_text) > 20 and  # 确保有足够内容
                        not p_text.startswith('From ') and  # 跳过图片说明
                        not p_text.startswith('这是一张') and  # 跳过图片说明
                        not 'Category:' in p_text and  # 跳过分类链接
                        not (p_text.startswith('(') and p_text.endswith(')')) and  # 跳过括号内容
                        not any(skip_word in p_text.lower() for skip_word in ['see also', 'external links', 'references', 'navigation'])):  # 跳过导航内容
                        valid_descriptions.append(p_text)
                        if len(valid_descriptions) >= 3:  # 只取前3个有效段落
                            break

                if not valid_descriptions:
                    if attempt == 2:
                        print(f"未找到有效描述段落 {pokemon_name_en}, 总共找到 {len(all_p_tags)} 个 <p> 标签")
                    await asyncio.sleep(0.3 * (attempt + 1))
                    continue

                overview = "\n".join(valid_descriptions)
                return overview

            except asyncio.TimeoutError:
                if attempt == 2:
                    print(f"请求超时 {pokemon_name_en}")
                await asyncio.sleep(0.3 * (attempt + 1))
            except Exception as e:
                if attempt == 2:
                    print(f"获取描述失败 {pokemon_name_en}: {e}")
                await asyncio.sleep(0.3 * (attempt + 1))

        # 如果这个URL失败了，继续下一个
        continue

    return "未找到描述"

async def get_pokemon_data(pokemon_name, js_content, session, semaphore):
    """从预加载的数据中获取单个宝可梦的数据"""
    async with semaphore:  # 限制并发数
        pokemon_key = pokemon_name.lower()

        # 提取宝可梦数据
        pokemon = extract_pokemon_data(js_content, pokemon_key)
        if not pokemon:
            return None

        data = {}

        # 1. 获取 ID 和名字
        data['id'] = pokemon.get('num')
        data['name_en'] = pokemon.get('name', '')
        data['name'] = pokemon_name

        # 2. 获取描述
        desc = await get_pokemon_description_from_52poke(data['name_en'], session)
        data['description'] = desc if desc else "未找到描述"

        return data

async def main():
    print("=" * 50)
    print("宝可梦描述数据批量爬虫")
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

    # 限制并发数为10，避免过多的并发请求
    semaphore = asyncio.Semaphore(10)

    async def process_pokemon(pokemon_name):
        nonlocal successful, failed
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                data = await get_pokemon_data(pokemon_name, js_content, session, semaphore)
                if data:
                    # 保存单个宝可梦数据
                    filename = f"{data['id']}_{pokemon_name}.json"
                    filepath = os.path.join(OUTPUT_DIR, filename)
                    async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                        await f.write(json.dumps(data, ensure_ascii=False, indent=2))
                    successful += 1
                    return True
                else:
                    failed += 1
                    return False
        except Exception as e:
            print(f"爬取失败 {pokemon_name}: {e}")
            failed += 1
            return False

    # 并发处理所有宝可梦
    tasks = [process_pokemon(pokemon_name) for pokemon_name in selected_pokemon]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    print()  # 换行

    print("\n爬取完成!")
    print(f"成功: {successful} 只")
    print(f"失败: {failed} 只")
    print(f"数据保存到: {OUTPUT_DIR}/")

async def test():
    """测试函数，自动爬取前3只宝可梦"""
    print("测试模式：爬取前3只宝可梦")
    print("正在获取宝可梦列表...")
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

    # 测试前3只宝可梦
    test_pokemon = all_pokemon[:3]  # bulbasaur, ivysaur, venusaur

    print("开始测试爬取...")
    semaphore = asyncio.Semaphore(3)  # 测试时限制并发数为3
    for pokemon_name in test_pokemon:
        async with aiohttp.ClientSession(headers=headers) as session:
            data = await get_pokemon_data(pokemon_name, js_content, session, semaphore)
            if data:
                print(f"\n{pokemon_name}:")
                print(f"  ID: {data['id']}")
                print(f"  英文名: {data['name_en']}")
                print(f"  描述: {data['description'][:200]}...")
            else:
                print(f"获取 {pokemon_name} 数据失败")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        asyncio.run(test())
    else:
        asyncio.run(main())
