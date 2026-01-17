import requests
import os
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "item_images")

# 创建文件夹（如果不存在）
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Pokemon Showdown图片服务器URL
ITEM_SPRITE_BASE_URL = "https://play.pokemonshowdown.com/sprites/itemicons/"

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

    # 首先尝试从道具JSON数据中获取spritenum（这是最可靠的方法）
    spritenum = None
    item_data = None
    try:
        items_dir = os.path.join(SCRIPT_DIR, "items")
        # 查找对应的JSON文件
        for filename in os.listdir(items_dir):
            if filename.endswith('.json'):
                filepath_json = os.path.join(items_dir, filename)
                try:
                    with open(filepath_json, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        processed_name = data.get('english', '').lower().replace(' ', '').replace('-', '').replace("'", "")
                        if processed_name == item_name:
                            spritenum = data.get('spritenum')
                            item_data = data
                            if spritenum is not None and spritenum != 0:
                                break
                except Exception as e:
                    print(f"读取文件失败 {filename}: {e}")
                    continue
    except Exception as e:
        print(f"查找spritenum失败: {e}")

    # 如果有有效的spritenum，优先使用Pokemon Showdown
    if spritenum is not None and spritenum != 0:
        url_formats = [
            f"https://play.pokemonshowdown.com/sprites/itemicons/{spritenum}.png",
        ]
        for image_url in url_formats:
            try:
                response = requests.get(image_url, headers=headers, timeout=3)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    return f"✓ 下载成功: {item_name} (Pokemon Showdown, spritenum: {spritenum})"
            except Exception as e:
                continue

    # 如果Pokemon Showdown失败或无spritenum，尝试从wiki获取
    if item_data and 'name' in item_data:
        chinese_name = item_data['name']
        # 构造wiki道具页面URL
        item_page_url = f"https://wiki.52poke.com/wiki/{requests.utils.quote(chinese_name)}（道具）"
        try:
            page_response = requests.get(item_page_url, headers=headers, timeout=5)
            if page_response.status_code == 200:
                from bs4 import BeautifulSoup
                page_soup = BeautifulSoup(page_response.text, 'html.parser')
                # 查找Bag_道具名_Sprite.png格式的图片
                images = page_soup.find_all('img')
                for img in images:
                    src = img.get('src', '')
                    if 'Bag_' in src and '_Sprite.png' in src and 'media.52poke' in src:
                        # 构造完整URL
                        if src.startswith('//'):
                            full_url = 'https:' + src
                        elif src.startswith('/'):
                            full_url = 'https://wiki.52poke.com' + src
                        else:
                            full_url = src
                        try:
                            img_response = requests.get(full_url, headers=headers, timeout=3)
                            if img_response.status_code == 200:
                                with open(filepath, 'wb') as f:
                                    f.write(img_response.content)
                                return f"✓ 下载成功: {item_name} (Wiki)"
                        except Exception as e:
                            continue
                        break  # 只尝试第一个匹配的图片
        except Exception as e:
            pass

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
