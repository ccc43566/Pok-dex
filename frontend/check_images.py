#!/usr/bin/env python3
import os
import sqlite3
import sys

# 检查图片文件是否存在
def check_images():
    # 连接数据库
    db_path = "../db/pokemon.db"
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取所有宝可梦
    cursor.execute("SELECT id, name FROM pokemon ORDER BY id")
    pokemon_list = cursor.fetchall()

    print(f"数据库中有 {len(pokemon_list)} 只宝可梦")

    # 检查图片文件夹
    images_dir = "../backend/spider/pokemon_images"
    if not os.path.exists(images_dir):
        print(f"图片文件夹不存在: {images_dir}")
        return

    image_files = os.listdir(images_dir)
    print(f"图片文件夹中有 {len(image_files)} 个文件")

    # 检查前50只宝可梦的图片
    missing_gif = []
    missing_png = []
    found_both = 0

    print("\n检查前50只宝可梦的图片文件:")
    for pokemon_id, name in pokemon_list[:50]:  # 只检查前50个
        # 尝试不同的文件名格式
        name_clean = name.lower().replace(' ', '').replace('-', '').replace('\'', '').replace('♀', 'f').replace('♂', 'm')
        gif_name = f"{pokemon_id}_{name_clean}.gif"
        png_name = f"{pokemon_id}_{name_clean}.png"

        has_gif = gif_name in image_files
        has_png = png_name in image_files

        if has_gif and has_png:
            found_both += 1
        elif has_gif:
            missing_png.append((pokemon_id, name))
        elif has_png:
            missing_gif.append((pokemon_id, name))
        else:
            # 尝试原始名称
            original_gif = f"{pokemon_id}_{name.lower()}.gif"
            original_png = f"{pokemon_id}_{name.lower()}.png"
            orig_has_gif = original_gif in image_files
            orig_has_png = original_png in image_files

            if orig_has_gif or orig_has_png:
                print(f"宝可梦 {pokemon_id} {name}: 文件名格式不同 (期望: {gif_name}, 实际: {original_gif if orig_has_gif else original_png})")
            else:
                print(f"宝可梦 {pokemon_id} {name}: 缺少所有图片文件")

    print("\n统计:")
    print(f"- 有GIF和PNG的宝可梦: {found_both}")
    print(f"- 只有GIF的宝可梦: {len(missing_png)}")
    print(f"- 只有PNG的宝可梦: {len(missing_gif)}")

    if missing_gif:
        print("\n只有PNG的宝可梦 (前10个):")
        for pokemon_id, name in missing_gif[:10]:
            print(f"  {pokemon_id}: {name}")

    # 检查加载更多时会显示的宝可梦 (51-100)
    print("\n检查51-100号宝可梦的图片:")
    for pokemon_id, name in pokemon_list[50:100]:  # 51-100 (索引50-99)
        gif_name = f"{pokemon_id}_{name.lower()}.gif"
        png_name = f"{pokemon_id}_{name.lower()}.png"

        has_gif = gif_name in image_files
        has_png = png_name in image_files

        if not has_gif and not has_png:
            print(f"  宝可梦 {pokemon_id} {name}: 缺少所有图片文件")
        elif not has_gif:
            print(f"  宝可梦 {pokemon_id} {name}: 缺少GIF文件 (只有PNG)")

    conn.close()

if __name__ == "__main__":
    check_images()
