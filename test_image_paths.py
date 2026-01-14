#!/usr/bin/env python3
import sys
import os

# 添加db目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'db')
sys.path.insert(0, db_path)

try:
    from database import get_all_pokemon, init_db
    print("Import successful")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

# 初始化数据库
init_db()

# 获取所有宝可梦
all_pokemon = get_all_pokemon()

images_dir = os.path.join(current_dir, "backend/spider/pokemon_images")

print("Checking image path generation logic:")
print("=" * 50)

# 检查一些有问题的宝可梦
test_ids = [50, 100, 1000, 1016, 1020, 1024, 1025]
for pid in test_ids:
    if pid <= len(all_pokemon):
        p = all_pokemon[pid - 1]
        print(f"\nPokemon {p['id']}: {p['name']}")

        # 模拟前端逻辑
        if p.get('image_path'):
            # 从image_path中提取文件名
            path_parts = p['image_path'].split(os.sep)
            filename = path_parts[-1]
            frontend_path = f"/images/{filename}"
            print(f"  DB image_path: {p['image_path']}")
            print(f"  Frontend path: {frontend_path}")
        else:
            # 生成默认路径，清理名字中的特殊字符
            safe_name = p['name'].lower().replace(' ', '').replace('-', '')
            # 只保留字母和数字
            import re
            safe_name = re.sub(r'[^a-z0-9]', '', safe_name)
            frontend_path = f"/images/{p['id']}_{safe_name}.gif"
            print(f"  No DB image_path, generated: {frontend_path}")

        # 检查文件是否存在
        actual_filename = frontend_path.replace('/images/', '')
        actual_path = os.path.join(images_dir, actual_filename)
        exists = os.path.exists(actual_path)
        print(f"  File exists: {exists}")

        if not exists:
            # 尝试PNG版本
            png_path = actual_path.replace('.gif', '.png')
            png_exists = os.path.exists(png_path)
            print(f"  PNG version exists: {png_exists}")

print("\n" + "=" * 50)
print("Summary of Pokemon without image_path:")
no_image_count = sum(1 for p in all_pokemon if not p.get('image_path'))
print(f"Total Pokemon without image_path: {no_image_count}")
