import sqlite3

def check_db():
    conn = sqlite3.connect('pokemon.db')
    cursor = conn.cursor()

    # 检查御三家和普通宝可梦
    cursor.execute('SELECT id, image_path FROM pokemon WHERE id IN (1, 4, 7, 25, 1000) ORDER BY id')
    rows = cursor.fetchall()

    print('数据库中的图片路径:')
    for row in rows:
        pokemon_id, image_path = row
        print(f'ID {pokemon_id}: {image_path}')

    conn.close()

if __name__ == "__main__":
    check_db()
