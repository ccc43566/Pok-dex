# database.py
import os
try:
    from .pokemon_db_init import PokemonDB
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from pokemon_db_init import PokemonDB

DB_PATH = "db/pokemon.db"

# 创建数据库实例
db_instance = None

def init_db():
    """初始化数据库，从pokemon_db_init.py引用"""
    global db_instance
    if db_instance is None:
        # 创建PokemonDB实例，自动初始化所有表
        db_instance = PokemonDB(DB_PATH)
        print("数据库初始化完成！")
    else:
        print("数据库已初始化。")

def insert_pokemon(pokemon_data):
    """插入宝可梦信息，引用pokemon_db_init.py中的方法"""
    if db_instance is None:
        init_db()

    # 使用PokemonDB实例的数据库连接
    try:
        cursor = db_instance.conn.cursor()
        sql = """
        INSERT OR IGNORE INTO pokemon
        (id, name, jp_name, en_name, type1, type2, hp, attack, defense, sp_atk, sp_def, speed, total, description, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (
            pokemon_data["id"], pokemon_data["name"], pokemon_data.get("jp_name"),
            pokemon_data.get("en_name"), pokemon_data["type1"], pokemon_data.get("type2"),
            pokemon_data["hp"], pokemon_data["attack"], pokemon_data["defense"],
            pokemon_data["sp_atk"], pokemon_data["sp_def"], pokemon_data["speed"],
            pokemon_data["total"], pokemon_data.get("description"), pokemon_data.get("image_path")
        ))
        db_instance.conn.commit()
        print(f"成功插入宝可梦: {pokemon_data['name']}")
    except Exception as e:
        print(f"插入宝可梦失败: {e}")

def insert_move(move_data):
    """插入技能信息"""
    if db_instance is None:
        init_db()

    try:
        cursor = db_instance.conn.cursor()
        sql = """
        INSERT OR IGNORE INTO moves
        (id, name, type, category, power, accuracy, pp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (
            move_data["id"], move_data["name"], move_data.get("type"),
            move_data.get("category"), move_data.get("power"),
            move_data.get("accuracy"), move_data.get("pp")
        ))
        db_instance.conn.commit()
        print(f"成功插入技能: {move_data['name']}")
    except Exception as e:
        print(f"插入技能失败: {e}")

def insert_pokemon_move(pokemon_id, move_id, level_learned):
    """插入宝可梦-技能关联"""
    if db_instance is None:
        init_db()

    try:
        cursor = db_instance.conn.cursor()
        sql = """
        INSERT OR IGNORE INTO pokemon_moves
        (pokemon_id, move_id, level_learned)
        VALUES (?, ?, ?)
        """
        cursor.execute(sql, (pokemon_id, move_id, level_learned))
        db_instance.conn.commit()
        print(f"成功关联宝可梦 {pokemon_id} 和技能 {move_id}")
    except Exception as e:
        print(f"关联宝可梦和技能失败: {e}")

def insert_evolution(base_pokemon_id, evolved_pokemon_id, condition):
    """插入进化信息"""
    if db_instance is None:
        init_db()

    try:
        cursor = db_instance.conn.cursor()
        sql = """
        INSERT OR IGNORE INTO evolutions
        (base_pokemon_id, evolved_pokemon_id, condition)
        VALUES (?, ?, ?)
        """
        cursor.execute(sql, (base_pokemon_id, evolved_pokemon_id, condition))
        db_instance.conn.commit()
        print(f"成功插入进化: {base_pokemon_id} -> {evolved_pokemon_id}")
    except Exception as e:
        print(f"插入进化失败: {e}")

def get_pokemon_by_id(pokemon_id):
    """根据ID查询宝可梦信息"""
    if db_instance is None:
        init_db()

    try:
        cursor = db_instance.conn.cursor()
        cursor.execute("SELECT * FROM pokemon WHERE id = ?", (pokemon_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
    except Exception as e:
        print(f"查询宝可梦失败: {e}")
        return None

def get_all_pokemon():
    """获取所有宝可梦信息"""
    if db_instance is None:
        init_db()

    try:
        cursor = db_instance.conn.cursor()
        cursor.execute("SELECT * FROM pokemon ORDER BY id")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"查询所有宝可梦失败: {e}")
        return []

def get_pokemon_moves(pokemon_id):
    """获取宝可梦的技能列表"""
    if db_instance is None:
        init_db()

    try:
        cursor = db_instance.conn.cursor()
        sql = """
        SELECT m.*, pm.level_learned
        FROM moves m
        JOIN pokemon_moves pm ON m.id = pm.move_id
        WHERE pm.pokemon_id = ?
        ORDER BY pm.level_learned
        """
        cursor.execute(sql, (pokemon_id,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"查询宝可梦技能失败: {e}")
        return []

def get_move_by_id(move_id):
    """根据ID查询技能信息"""
    if db_instance is None:
        init_db()

    try:
        cursor = db_instance.conn.cursor()
        cursor.execute("SELECT * FROM moves WHERE id = ?", (move_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
    except Exception as e:
        print(f"查询技能失败: {e}")
        return None

def get_all_moves():
    """获取所有技能信息"""
    if db_instance is None:
        init_db()

    try:
        cursor = db_instance.conn.cursor()
        cursor.execute("SELECT * FROM moves ORDER BY id")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"查询所有技能失败: {e}")
        return []

def get_evolutions(pokemon_id):
    """获取宝可梦的进化信息"""
    if db_instance is None:
        init_db()

    try:
        cursor = db_instance.conn.cursor()
        sql = """
        SELECT p.name as evolved_name, e.condition
        FROM evolutions e
        JOIN pokemon p ON e.evolved_pokemon_id = p.id
        WHERE e.base_pokemon_id = ?
        """
        cursor.execute(sql, (pokemon_id,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"查询进化信息失败: {e}")
        return []

def close_db():
    """关闭数据库连接"""
    global db_instance
    if db_instance:
        db_instance.close()
        db_instance = None
