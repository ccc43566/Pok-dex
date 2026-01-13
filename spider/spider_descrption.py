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
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "pokemon_descrptions")

# 创建文件夹（如果不存在）
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

def get_pokemon_data(pokemon_name, js_content):
    """从预加载的数据中获取单个宝可梦的数据"""
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
    desc = get_pokemon_description_from_52poke(data['name_en'])
    data['description'] = desc if desc else "未找到描述"

    return data

def main():
    print("=" * 50)
    print("宝可梦描述数据批量爬虫")
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

        time.sleep(0.2)  # 避免请求过快

    print()  # 换行

    print("\n爬取完成!")
    print(f"成功: {successful} 只")
    print(f"失败: {failed} 只")
    print(f"数据保存到: {OUTPUT_DIR}/")

def test():
    """测试函数，自动爬取前3只宝可梦"""
    print("测试模式：爬取前3只宝可梦")
    print("正在获取宝可梦列表...")
    all_pokemon = get_all_pokemon_names()
    print(f"共找到 {len(all_pokemon)} 只宝可梦")

    # 预加载数据文件
    print("正在预加载宝可梦数据库...")
    response = requests.get(DATA_URL)
    if response.status_code != 200:
        print(f"无法加载数据库: {response.status_code}")
        return
    js_content = response.text

    # 测试前3只宝可梦
    test_pokemon = all_pokemon[:3]  # bulbasaur, ivysaur, venusaur

    print("开始测试爬取...")
    for pokemon_name in test_pokemon:
        data = get_pokemon_data(pokemon_name, js_content)
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
        test()
    else:
        main()
