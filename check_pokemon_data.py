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

print(f"Total Pokemon: {len(all_pokemon)}")

# 检查前10个和后10个宝可梦
print("\nFirst 10 Pokemon:")
for i, p in enumerate(all_pokemon[:10]):
    print(f"ID: {p['id']}, Name: {p['name']}, Image Path: {p.get('image_path', 'None')}")

print("\nLast 10 Pokemon:")
for i, p in enumerate(all_pokemon[-10:]):
    print(f"ID: {p['id']}, Name: {p['name']}, Image Path: {p.get('image_path', 'None')}")

# 检查图片文件是否存在
images_dir = os.path.join(current_dir, "backend/spider/pokemon_images")
print(f"\nImages directory: {images_dir}")
print(f"Images directory exists: {os.path.exists(images_dir)}")

# 检查哪些宝可梦没有image_path
print("\nPokemon without image_path:")
no_image_pokemon = [p for p in all_pokemon if not p.get('image_path')]
for p in no_image_pokemon:
    print(f"ID: {p['id']}, Name: {p['name']}")

# 检查一些具体的宝可梦图片
test_pokemon = [50, 51, 52, 100, 101, 102, 1000, 1016, 1024]  # 一些可能有问题的ID
for pid in test_pokemon:
    if pid <= len(all_pokemon):
        p = all_pokemon[pid - 1]  # 列表索引从0开始
        expected_gif = f"{p['id']}_{p['name'].lower()}.gif"
        expected_png = f"{p['id']}_{p['name'].lower()}.png"
        gif_path = os.path.join(images_dir, expected_gif)
        png_path = os.path.join(images_dir, expected_png)

        print(f"\nPokemon {p['id']} - {p['name']}:")
        print(f"  Image Path in DB: {p.get('image_path', 'None')}")
        print(f"  Expected GIF: {expected_gif} -> Exists: {os.path.exists(gif_path)}")
        print(f"  Expected PNG: {expected_png} -> Exists: {os.path.exists(png_path)}")
