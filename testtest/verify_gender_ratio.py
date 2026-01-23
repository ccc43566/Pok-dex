#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证数据库中gender_ratio字段是否正确存储
"""

import sqlite3
import json
import os

# 连接数据库
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db', 'pokemon.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 测试几个宝可梦的gender_ratio
pokemon_ids = [1, 25, 144, 145, 146]

print("验证数据库中gender_ratio字段存储情况：")
print("-" * 60)

for pokemon_id in pokemon_ids:
    cursor.execute('SELECT id, name, gender_ratio FROM pokemon WHERE id = ?', (pokemon_id,))
    row = cursor.fetchone()
    
    if row:
        pokemon_id, name, gender_ratio_json = row
        print(f"宝可梦: #{pokemon_id} {name}")
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
    else:
        print(f"宝可梦 #{pokemon_id} 不存在")
    
    print("-" * 60)

# 关闭连接
conn.close()

print("验证完成！")