#!/usr/bin/env python3
import os
import sqlite3

def check_filenames():
    # 连接数据库
    db_path = "../db/pokemon.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取前10只宝可梦
    cursor.execute("SELECT id, name FROM pokemon ORDER BY id LIMIT 10")
    pokemon_list = cursor.fetchall()

    # 检查图片文件夹
    images_dir = "../backend/spider/pokemon_images"
    image_files = os.listdir(images_dir)

    print("检查前10只宝可梦的文件名匹配:")
    print("=" * 50)

    for pokemon_id, name in pokemon_list:
        expected_gif = f"{pokemon_id}_{name.lower()}.gif"
        expected_png = f"{pokemon_id}_{name.lower()}.png"

        print(f"\n宝可梦 {pokemon_id}: {name}")
        print(f"  期望GIF: {expected_gif}")
        print(f"  期望PNG: {expected_png}")

        # 查找匹配的文件
        matching_files = [f for f in image_files if str(pokemon_id) in f]
        if matching_files:
            print(f"  找到的文件: {matching_files}")
        else:
            print("  未找到匹配的文件")

        # 检查是否存在
        has_gif = expected_gif in image_files
        has_png = expected_png in image_files
        print(f"  GIF存在: {has_gif}, PNG存在: {has_png}")

    conn.close()

if __name__ == "__main__":
    check_filenames()
