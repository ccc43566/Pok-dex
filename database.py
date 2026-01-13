# database.py
import sqlite3
import os


DB_PATH = "pokemon.db"

def init_db():
    if os.path.exists(DB_PATH):
        print("数据库已存在，跳过初始化。")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE pokemon (
            id INTEGER PRIMARY KEY,
            name_zh TEXT NOT NULL,
            name_ja TEXT NOT NULL,
            name_en TEXT NOT NULL,
            type1 TEXT NOT NULL,
            type2 TEXT,
            category TEXT,  -- 简介/分类
            hp INTEGER NOT NULL,
            attack INTEGER NOT NULL,
            defense INTEGER NOT NULL,
            sp_atk INTEGER NOT NULL,
            sp_def INTEGER NOT NULL,
            speed INTEGER NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("数据库初始化完成！")

def insert_pokemon(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO pokemon (
            id, name_zh, name_ja, name_en, type1, type2, category,
            hp, attack, defense, sp_atk, sp_def, speed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()

def insert_pokemon(self, pokemon_data):
        """
        插入单条宝可梦数据
        :param pokemon_data: 字典格式的宝可梦数据，示例：
        {
            "id": 25,
            "name": "皮卡丘",
            "jp_name": "ピカチュウ",
            "en_name": "Pikachu",
            "type1": "电",
            "type2": None,
            "hp": 35,
            "attack": 55,
            "defense": 40,
            "sp_atk": 50,
            "sp_def": 50,
            "speed": 90,
            "total": 320,
            "description": "脸颊两边有着小小的电力袋。遇到危险时就会放电。"
        }
        """
        sql = """
        INSERT OR IGNORE INTO pokemon 
        (id, name, jp_name, en_name, type1, type2, hp, attack, defense, sp_atk, sp_def, speed, total, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, (
                pokemon_data["id"], pokemon_data["name"], pokemon_data["jp_name"],
                pokemon_data["en_name"], pokemon_data["type1"], pokemon_data["type2"],
                pokemon_data["hp"], pokemon_data["attack"], pokemon_data["defense"],
                pokemon_data["sp_atk"], pokemon_data["sp_def"], pokemon_data["speed"],
                pokemon_data["total"], pokemon_data["description"]
            ))
            self.conn.commit()
            print(f"成功插入宝可梦: {pokemon_data['name']}")
        except Error as e:
            print(f"插入宝可梦失败: {e}")