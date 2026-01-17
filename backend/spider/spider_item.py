import requests
from bs4 import BeautifulSoup
import json
import time
import os

# 目标网址
url = "https://wiki.52poke.com/wiki/道具列表"

# 设置请求头（模拟浏览器）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

try:
    print("正在请求网页...")
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    response.encoding = 'utf-8'  # 确保正确解码中文

    print("正在解析 HTML...")
    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到所有道具表格（根据 class 定位，所有包含 hvlist 的表格）
    tables = soup.find_all('table', class_=lambda x: x and 'hvlist' in x)
    if not tables:
        raise ValueError("未找到道具表格，请检查网页结构是否变化")

    items = []
    item_count = 0

    for table in tables:
        # 从表格类中提取类别
        table_classes = table.get('class', [])
        category = "道具"  # 默认
        for cls in table_classes:
            if cls.startswith('bgd-'):
                category = cls[4:]  # 去掉'bgd-'
                break

        # 提取所有数据行（跳过表头）
        rows = table.find_all('tr')[1:]  # 第一行是表头，跳过

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:  # 确保至少有4列
                # 提取第一列的链接（如果有）
                image_link = None
                if cols[0].find('a'):
                    a_tag = cols[0].find('a')
                    if a_tag and 'href' in a_tag.attrs:
                        image_link = a_tag['href']

                item = {
                    "中文": cols[1].get_text(strip=True),
                    "日文": cols[2].get_text(strip=True),
                    "英文": cols[3].get_text(strip=True),
                    "说明": cols[4].get_text(strip=True) if len(cols) > 4 else "",
                    "category": category,
                    "image_link": image_link
                }
                items.append(item)
                item_count += 1
                print(f"[{item_count}] 已解析 [{category}]: {item['中文']}")

    # 创建items目录
    items_dir = os.path.join(os.path.dirname(__file__), 'items')
    os.makedirs(items_dir, exist_ok=True)

    # 保存每个道具为单独的JSON文件
    for i, item in enumerate(items, start=0):
        # 使用英文名作为文件名，去除空格和特殊字符
        english_name = item['英文'].lower().replace(' ', '').replace('-', '').replace("'", "").replace('é', 'e')
        filename = f"{i}_{english_name}.json"

        # 构造JSON数据，模拟现有格式
        item_data = {
            "id": i,
            "name": item['中文'],  # 使用中文作为名称
            "english": item['英文'],  # 添加英文名
            "category": item['category'],  # 使用提取的类别
            "num": i,
            "spritenum": i,  # 暂时使用i作为spritenum
            "desc": item['说明'],
            "shortDesc": item['说明'],
            "gen": 1,  # 默认世代
            "isPokeball": False  # 默认不是精灵球
        }

        filepath = os.path.join(items_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(item_data, f, ensure_ascii=False, indent=2)

        print(f"保存: {filename}")

    print(f"\n✅ 成功！共爬取 {len(items)} 个道具，已保存到 items/ 目录")

except Exception as e:
    print(f"❌ 发生错误: {e}")
    input("按回车键退出...")
