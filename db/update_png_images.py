import os
import sqlite3
import sys
from pathlib import Path

def update_png_images():
    """将爬取的PNG图片路径更新到数据库中，但跳过御三家（让他们显示GIF）"""
    # 数据库路径
    db_path = os.path.join(os.path.dirname(__file__), "pokemon.db")
    png_dir = os.path.join(os.path.dirname(__file__), "..", "backend", "spider", "pokemon_png_images")

    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return

    if not os.path.exists(png_dir):
        print(f"PNG图片目录不存在: {png_dir}")
        return

    # 世代御三家ID列表（这些宝可梦保持GIF，不更新image_path）
    starter_ids = {1, 4, 7, 152, 155, 158, 252, 255, 258, 387, 390, 393, 495, 498, 501, 650, 653, 656, 722, 725, 728, 810, 813, 816, 906, 909, 912}

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取所有PNG文件
    png_files = [f for f in os.listdir(png_dir) if f.endswith('.png')]
    print(f"找到 {len(png_files)} 个PNG文件")

    updated_count = 0

    for png_file in png_files:
        # 解析文件名格式: ID_name.png 或 ID_name-variant.png
        try:
            # 分离ID和名称部分
            parts = png_file.replace('.png', '').split('_', 1)
            if len(parts) != 2:
                print(f"跳过格式不正确的文件名: {png_file}")
                continue

            pokemon_id = int(parts[0])
            name_part = parts[1]

            # 跳过御三家，让他们显示GIF
            if pokemon_id in starter_ids:
                print(f"跳过御三家: ID {pokemon_id} ({png_file})")
                continue

            # 构建相对路径（相对于GIF目录）
            # 将PNG文件名改为GIF文件名
            gif_filename = png_file.replace('.png', '.gif')
            relative_path = gif_filename

            # 更新数据库
            cursor.execute("""
                UPDATE pokemon
                SET image_path = ?
                WHERE id = ?
            """, (relative_path, pokemon_id))

            if cursor.rowcount > 0:
                updated_count += 1
                print(f"更新图片路径: ID {pokemon_id} -> {png_file}")
            else:
                print(f"未找到ID为 {pokemon_id} 的宝可梦记录")

        except ValueError as e:
            print(f"解析文件名失败 {png_file}: {e}")
        except Exception as e:
            print(f"更新失败 {png_file}: {e}")

    conn.commit()
    conn.close()

    print(f"共更新 {updated_count} 条记录（跳过了御三家）")

if __name__ == "__main__":
    update_png_images()
