#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gender Ratio 数据处理测试脚本
"""

import json
import os

# 添加数据库模块路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
db_path = os.path.join(project_root, 'db')
import sys
sys.path.insert(0, db_path)

from pokemon_db_init import PokemonDB

def test_gender_ratio_data():
    """测试性别比例数据处理"""
    print("开始测试性别比例数据处理...")
    
    # 创建临时数据库
    temp_db = os.path.join(current_dir, 'test_pokemon.db')
    if os.path.exists(temp_db):
        os.remove(temp_db)
    
    # 创建数据库实例
    db = PokemonDB(temp_db)
    
    # 测试数据
    test_pokemons = [
        {
            "id": 1,
            "name": "Bulbasaur",
            "type1": "Grass",
            "type2": "Poison",
            "hp": 45,
            "attack": 49,
            "defense": 49,
            "sp_atk": 65,
            "sp_def": 65,
            "speed": 45,
            "total": 318,
            "height": 0.7,
            "weight": 6.9,
            "gender_ratio": {"M": 0.875, "F": 0.125},
            "description": "测试描述",
            "image_path": "test_path"
        },
        {
            "id": 25,
            "name": "Pikachu",
            "type1": "Electric",
            "type2": None,
            "hp": 35,
            "attack": 55,
            "defense": 40,
            "sp_atk": 50,
            "sp_def": 50,
            "speed": 90,
            "total": 320,
            "height": 0.4,
            "weight": 6.0,
            "gender_ratio": {},
            "description": "测试描述",
            "image_path": "test_path"
        },
        {
            "id": 144,
            "name": "Articuno",
            "type1": "Ice",
            "type2": "Flying",
            "hp": 90,
            "attack": 85,
            "defense": 100,
            "sp_atk": 95,
            "sp_def": 125,
            "speed": 85,
            "total": 580,
            "height": 1.7,
            "weight": 55.4,
            "gender_ratio": {},
            "description": "测试描述",
            "image_path": "test_path"
        }
    ]
    
    # 插入测试数据
    for pokemon in test_pokemons:
        db.insert_pokemon(pokemon)
    
    # 查询并验证数据
    print("\n验证数据库中的性别比例数据:")
    cursor = db.conn.cursor()
    cursor.execute('SELECT id, name, gender_ratio FROM pokemon')
    rows = cursor.fetchall()
    
    for row in rows:
        pokemon_id, name, gender_ratio_json = row
        print(f"\n宝可梦: #{pokemon_id} {name}")
        print(f"存储的gender_ratio: {gender_ratio_json}")
        
        # 解析JSON
        if gender_ratio_json:
            try:
                gender_ratio = json.loads(gender_ratio_json)
                print(f"解析后的gender_ratio: {gender_ratio}")
                
                # 模拟前端逻辑
                male_ratio = gender_ratio.get('M', 0)
                female_ratio = gender_ratio.get('F', 0)
                
                if male_ratio == 0 and female_ratio == 0:
                    print("显示结果: 无性别")
                elif male_ratio == 0:
                    print("显示结果: 仅雌性")
                elif female_ratio == 0:
                    print("显示结果: 仅雄性")
                else:
                    male_percent = f"{male_ratio * 100:.1f}"
                    female_percent = f"{female_ratio * 100:.1f}"
                    print(f"显示结果: 雄性:{male_percent}% 雌性:{female_percent}%")
            except json.JSONDecodeError as e:
                print(f"解析错误: {e}")
        else:
            print("显示结果: 不显示")
    
    # 关闭连接
    db.close()
    
    # 清理临时文件
    if os.path.exists(temp_db):
        os.remove(temp_db)
    
    print("\n测试完成！")

if __name__ == "__main__":
    test_gender_ratio_data()