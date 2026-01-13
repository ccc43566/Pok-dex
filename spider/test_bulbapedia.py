#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

# 设置请求头，避免被反爬
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def check_bulbapedia_structure():
    """检查Bulbapedia页面的结构"""
    url = "https://bulbapedia.bulbagarden.net/wiki/Bulbasaur_(Pok%C3%A9mon)"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        print("=== Bulbapedia页面结构分析 ===")

        # 查找所有表格
        tables = soup.find_all('table')
        print(f"总共找到 {len(tables)} 个表格")

        # 检查每个表格的内容
        for i, table in enumerate(tables[:10]):  # 只检查前10个表格
            text = table.get_text()[:200]
            print(f"\n表格 {i}:")
            print(f"  内容预览: {text}")
            print(f"  包含'Base stats': {'Base stats' in text}")
            print(f"  包含'HP': {'HP' in text}")

        # 查找所有包含数字的元素
        print("\n=== 查找数字元素 ===")
        all_td = soup.find_all('td')
        numeric_tds = []
        for td in all_td:
            text = td.get_text(strip=True)
            if text.isdigit() and len(text) <= 3:
                numeric_tds.append((text, td))

        print(f"找到 {len(numeric_tds)} 个数字单元格")
        for num, td in numeric_tds[:20]:  # 只显示前20个
            # 获取父元素的信息
            parent = td.parent if td.parent else None
            grandparent = parent.parent if parent and parent.parent else None
            print(f"  数字 {num}: 父级={parent.name if parent else 'None'}, 祖父级={grandparent.name if grandparent else 'None'}")

        # 查找Abilities部分
        print("\n=== Abilities部分 ===")
        h2_tags = soup.find_all(['h2', 'h3', 'h4'])
        for h in h2_tags:
            if 'Abilities' in h.get_text():
                print(f"找到Abilities标题: {h.get_text()}")
                # 查找后续的表格
                current = h
                for _ in range(5):  # 查找接下来的5个元素
                    current = current.find_next()
                    if current and current.name == 'table':
                        table_text = current.get_text()[:300]
                        print(f"Abilities表格内容: {table_text}")
                        break

    except Exception as e:
        print(f"检查失败: {e}")

if __name__ == "__main__":
    check_bulbapedia_structure()
