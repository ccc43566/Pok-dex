import requests
import os
import time
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "item_images")

# 创建文件夹（如果不存在）
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Pokemon Showdown图片服务器URL
ITEM_SPRITE_BASE_URL = "https://play.pokemonshowdown.com/sprites/itemicons/"

# Pokemon Showdown道具数据URL
ITEMS_DATA_URL = "https://play.pokemonshowdown.com/data/items.js"

def extract_item_data(js_content, item_key):
    """从JavaScript内容中提取特定道具的数据"""
    # 查找特定的道具数据，使用平衡大括号匹配
    start_pattern = rf'{re.escape(item_key)}:\s*{{'
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

    item_str = js_content[start_pos:end_pos]

    # 手动解析JavaScript对象格式
    data = {}

    # 解析spritenum
    spritenum_match = re.search(r'spritenum:\s*(\d+)', item_str)
    if spritenum_match:
        data['spritenum'] = int(spritenum_match.group(1))

    return data

# 全局变量缓存items.js数据
_items_js_content = None

def get_items_js_content():
    """获取并缓存Pokemon Showdown的items.js内容"""
    global _items_js_content
    if _items_js_content is None:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(ITEMS_DATA_URL, headers=headers, timeout=30)
            response.raise_for_status()
            _items_js_content = response.text
            print("成功加载Pokemon Showdown道具数据库")
        except Exception as e:
            print(f"加载道具数据库失败: {e}")
            return None
    return _items_js_content

def get_item_spritenum_from_ps(item_name):
    """从Pokemon Showdown获取道具的spritenum"""
    js_content = get_items_js_content()
    if js_content:
        # 查找道具的spritenum
        item_data = extract_item_data(js_content, item_name)
        if item_data and 'spritenum' in item_data:
            return item_data['spritenum']
    return None

def get_item_names_from_json():
    """从已有的JSON文件中获取所有道具名称"""
    items_dir = os.path.join(SCRIPT_DIR, "items")
    item_names = []

    if not os.path.exists(items_dir):
        print(f"道具数据目录不存在: {items_dir}")
        return []

    for filename in os.listdir(items_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(items_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    item_name = data.get('english', '').lower().replace(' ', '').replace('-', '').replace("'", "")
                    if item_name:
                        item_names.append(item_name)
            except Exception as e:
                print(f"读取文件失败 {filename}: {e}")

    return item_names

def download_item_image(item_name):
    """下载单个道具图片"""
    # 尝试多种URL格式
    image_filename = f"{item_name}.png"
    filepath = os.path.join(OUTPUT_DIR, image_filename)

    # 检查文件是否已存在
    if os.path.exists(filepath):
        return f"✓ 已存在: {item_name}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # 从Pokemon Showdown获取正确的spritenum
    spritenum = get_item_spritenum_from_ps(item_name)

    # 使用Pokemon Showdown下载图片
    if spritenum is not None:
        url_formats = [
            f"https://play.pokemonshowdown.com/sprites/itemicons/{spritenum}.png",
        ]
        for image_url in url_formats:
            try:
                response = requests.get(image_url, headers=headers, timeout=3)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    return f"✓ 下载成功: {item_name} (spritenum: {spritenum})"
            except Exception as e:
                continue

    return f"✗ 下载失败 {item_name}"

def main():
    print("=" * 50)
    print("宝可梦道具图片批量下载器")
    print("=" * 50)

    # 获取所有道具名称
    print("正在获取道具列表...")
    all_items = get_item_names_from_json()
    print(f"共找到 {len(all_items)} 个道具")

    if not all_items:
        print("没有找到道具数据，请先运行 spider_item.py 生成道具数据")
        return

    # 显示前几个道具作为示例
    if all_items:
        print("前10个道具:", all_items[:10])

    # 自动开始下载
    print("自动开始下载图片...")

    # 开始批量下载
    print("\n开始下载...")
    successful = 0
    failed = 0
    start_time = time.time()
    total_count = len(all_items)

    # 使用线程池进行并发下载
    max_workers = min(20, len(all_items))  # 最多20个并发线程

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有下载任务
        future_to_item = {executor.submit(download_item_image, item_name): item_name for item_name in all_items}

        # 处理完成的任务
        for future in as_completed(future_to_item):
            item_name = future_to_item[future]
            try:
                result = future.result()
                if "✓" in result:
                    successful += 1
                    if "已存在" in result:
                        print(f"{result}")
                    else:
                        print(f"{result} ({successful}/{total_count})")
                else:
                    failed += 1
                    print(f"{result}")

            except Exception as e:
                failed += 1
                print(f"✗ 错误 {item_name}: {e}")

    total_time = time.time() - start_time
    print(f"\n下载完成! 总耗时: {total_time:.2f}秒")
    print(f"成功: {successful} 张")
    print(f"失败: {failed} 张")
    print(f"平均速度: {total_count/total_time:.1f} 张/秒")
    print(f"图片保存到: {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
