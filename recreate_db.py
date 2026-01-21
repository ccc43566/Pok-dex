#!/usr/bin/env python3
"""
重新创建数据库脚本
"""

import os
import sys
import time

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'db')
sys.path.insert(0, db_path)

from pokemon_db_init import PokemonDB

def recreate_database():
    """删除并重新创建数据库"""
    db_file = "db/pokemon.db"

    # 尝试删除现有数据库文件
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"已删除现有数据库文件: {db_file}")
        except Exception as e:
            print(f"删除数据库文件失败: {e}")
            return False

    # 创建新数据库
    try:
        print("正在创建新数据库...")
        db = PokemonDB(db_file)
        db.close()
        print("数据库创建成功！")
        return True
    except Exception as e:
        print(f"创建数据库失败: {e}")
        return False

if __name__ == "__main__":
    if recreate_database():
        print("数据库重新创建完成！")
    else:
        print("数据库重新创建失败！")
