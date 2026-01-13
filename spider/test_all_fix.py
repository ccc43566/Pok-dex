#!/usr/bin/env python3
import json
import requests
from bs4 import BeautifulSoup
import os

# 设置请求头，避免被反爬
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

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

        # 调试：打印网页标题
        title = soup.find('title')
        print(f"网页标题: {title.get_text() if title else '未找到'}")

        # 打印网页部分内容来调试
        content = soup.find('div', id='mw-content-text')
        if content:
            print("内容区域前500字符:")
            print(content.get_text()[:500])
            print("...")

        # 抓取种族值（HP, Attack, Defense, etc.）
        # 查找所有表格
        tables = soup.find_all('table')
        print(f"找到 {len(tables)} 个表格")

        # 查找包含数字的表格行（种族值通常是数字）
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                # 检查是否是种族值行（通常有6个数字）
                numeric_cells = []
                for cell in cells:
                    text = cell.get_text(strip=True)
                    if text.isdigit() and len(text) <= 3:  # 种族值通常是1-3位数字
                        numeric_cells.append(int(text))

                if len(numeric_cells) >= 6:  # 找到了6个或更多数字
                    print(f"在表格 {i} 中找到可能的种族值: {numeric_cells[:6]}")
                    if len(numeric_cells) >= 6:
                        stats_data['hp'] = numeric_cells[0]
                        stats_data['attack'] = numeric_cells[1]
                        stats_data['defense'] = numeric_cells[2]
                        stats_data['sp_atk'] = numeric_cells[3]
                        stats_data['sp_def'] = numeric_cells[4]
                        stats_data['speed'] = numeric_cells[5]
                        print("成功提取种族值")
                        break
            if 'hp' in stats_data:
                break

        # 抓取Abilities
        abilities = []

        # 方法1：查找所有包含"Ability"的链接
        ability_links = soup.find_all('a', href=lambda href: href and 'Ability' in href and 'Category:' not in href)
        print(f"找到 {len(ability_links)} 个ability链接")
        for link in ability_links:
            ability_name = link.get_text(strip=True)
            if ability_name and len(ability_name) > 1 and ability_name not in ['Ability', 'Abilities']:
                if ability_name not in abilities:
                    abilities.append(ability_name)

        # 方法2：查找所有<span class="ability">或类似元素
        ability_spans = soup.find_all('span', class_=lambda c: c and 'ability' in c.lower())
        print(f"找到 {len(ability_spans)} 个ability span")
        for span in ability_spans:
            ability_name = span.get_text(strip=True)
            if ability_name and len(ability_name) > 1:
                if ability_name not in abilities:
                    abilities.append(ability_name)

        # 方法3：查找表格中的ability信息
        tables = soup.find_all('table')
        for table in tables:
            if 'Abilities' in table.get_text():
                links = table.find_all('a')
                for link in links:
                    href = link.get('href', '')
                    if '/wiki/' in href and 'Ability' in href:
                        ability_name = link.get_text(strip=True)
                        if ability_name and len(ability_name) > 1:
                            if ability_name not in abilities:
                                abilities.append(ability_name)

        print(f"找到 {len(abilities)} 个特性: {abilities}")
        stats_data['abilities'] = abilities

        return stats_data

    except Exception as e:
        print(f"从Bulbapedia抓取数据失败 {pokemon_name}: {e}")
        return {}

def test_fix():
    """测试修复效果，抓取Charmander和Venusaur的数据"""
    print("测试修复效果：抓取Charmander和Venusaur的数据...")

    # 测试Charmander
    print("\n=== 测试Charmander ===")
    charmander_data = get_pokemon_stats_from_web("charmander")
    print("Charmander数据:")
    print(f"  HP: {charmander_data.get('hp')}")
    print(f"  Attack: {charmander_data.get('attack')}")
    print(f"  Defense: {charmander_data.get('defense')}")
    print(f"  Sp. Atk: {charmander_data.get('sp_atk')}")
    print(f"  Sp. Def: {charmander_data.get('sp_def')}")
    print(f"  Speed: {charmander_data.get('speed')}")
    print(f"  Abilities: {charmander_data.get('abilities')}")

    # 测试Venusaur
    print("\n=== 测试Venusaur ===")
    venusaur_data = get_pokemon_stats_from_web("venusaur")
    print("Venusaur数据:")
    print(f"  HP: {venusaur_data.get('hp')}")
    print(f"  Attack: {venusaur_data.get('attack')}")
    print(f"  Defense: {venusaur_data.get('defense')}")
    print(f"  Sp. Atk: {venusaur_data.get('sp_atk')}")
    print(f"  Sp. Def: {venusaur_data.get('sp_def')}")
    print(f"  Speed: {venusaur_data.get('speed')}")
    print(f"  Abilities: {venusaur_data.get('abilities')}")



if __name__ == "__main__":
    test_fix()
