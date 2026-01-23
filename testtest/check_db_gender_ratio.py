import sqlite3
import json

# 连接到数据库
conn = sqlite3.connect('d:\\baizhan_program\\my_pokedex\\Pok-dex\\db\\pokemon.db')
cursor = conn.cursor()

# 检查pokemon表的结构
print("=== Pokemon表结构 ===")
cursor.execute("PRAGMA table_info(pokemon)")
columns = cursor.fetchall()
for column in columns:
    print(f"{column[1]}: {column[2]}")

# 查询皮卡丘的gender_ratio字段
print("\n=== 皮卡丘数据 ===")
cursor.execute("SELECT id, name, gender_ratio FROM pokemon WHERE id = 25")
pikachu = cursor.fetchone()
print(f"ID: {pikachu[0]}")
print(f"Name: {pikachu[1]}")
print(f"Gender Ratio: {pikachu[2]}")
print(f"Gender Ratio Type: {type(pikachu[2])}")

# 查询妙蛙种子的gender_ratio字段
print("\n=== 妙蛙种子数据 ===")
cursor.execute("SELECT id, name, gender_ratio FROM pokemon WHERE id = 1")
bulbasaur = cursor.fetchone()
print(f"ID: {bulbasaur[0]}")
print(f"Name: {bulbasaur[1]}")
print(f"Gender Ratio: {bulbasaur[2]}")
print(f"Gender Ratio Type: {type(bulbasaur[2])}")

# 查询阿尔宙斯的gender_ratio字段
print("\n=== 阿尔宙斯数据 ===")
cursor.execute("SELECT id, name, gender_ratio FROM pokemon WHERE id = 493")
arceus = cursor.fetchone()
print(f"ID: {arceus[0]}")
print(f"Name: {arceus[1]}")
print(f"Gender Ratio: {arceus[2]}")
print(f"Gender Ratio Type: {type(arceus[2])}")

# 关闭数据库连接
conn.close()