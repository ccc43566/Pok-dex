# database.py
import os
import json
try:
    from .pokemon_db_init import PokemonDB
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from pokemon_db_init import PokemonDB

# 使用绝对路径设置数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db/pokemon.db")

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
        # 将gender_ratio转换为JSON字符串
        gender_ratio = pokemon_data.get("gender_ratio")
        gender_ratio_json = json.dumps(gender_ratio) if gender_ratio is not None else None

        sql = """
        INSERT OR REPLACE INTO pokemon
        (id, name, jp_name, en_name, type1, type2, hp, attack, defense, sp_atk, sp_def, speed, total, height, weight, gender_ratio, description, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (
            pokemon_data["id"], pokemon_data["name"], pokemon_data.get("jp_name"),
            pokemon_data.get("en_name"), pokemon_data["type1"], pokemon_data.get("type2"),
            pokemon_data["hp"], pokemon_data["attack"], pokemon_data["defense"],
            pokemon_data["sp_atk"], pokemon_data["sp_def"], pokemon_data["speed"],
            pokemon_data["total"], pokemon_data.get("height"), pokemon_data.get("weight"),
            gender_ratio_json, pokemon_data.get("description"), pokemon_data.get("image_path")
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
    """根据ID查询宝可梦信息，包括所有变种形态"""
    if db_instance is None:
        init_db()

    try:
        cursor = db_instance.conn.cursor()
        cursor.execute("SELECT * FROM pokemon WHERE id = ?", (pokemon_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            pokemon_data = dict(zip(columns, row))
            # 将gender_ratio从JSON字符串解析为对象
            if pokemon_data.get('gender_ratio') is not None:
                try:
                    pokemon_data['gender_ratio'] = json.loads(pokemon_data['gender_ratio'])
                except:
                    pokemon_data['gender_ratio'] = {}
            else:
                pokemon_data['gender_ratio'] = {}
            
            # 从pokemon_data_all目录中读取该宝可梦的所有变种形态
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend/spider/pokemon_data_all")
            variants = []
            if os.path.exists(data_dir):
                for filename in os.listdir(data_dir):
                    if filename.endswith('.json'):
                        try:
                            # 解析文件名获取id
                            parts = filename[:-5].split('_')  # 移除.json后缀
                            if len(parts) >= 1:
                                file_id = int(parts[0])
                                if file_id == pokemon_id:
                                    # 检查是否为Mega或Gmax形态
                                    name_part = filename[len(f"{pokemon_id}_"):-5]  # 移除id_前缀和.json后缀
                                    if 'mega' in name_part.lower() or 'gmax' in name_part.lower():
                                        continue  # 跳过Mega和Gmax形态，它们应该出现在mega_gmax_forms中
                                    
                                    # 读取变种数据
                                    with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
                                        form_data = json.load(f)
                                    
                                    # 构建变种宝可梦数据
                                    variant_pokemon = {
                                        'id': pokemon_id,
                                        'name': form_data.get('name', ''),
                                        'jp_name': form_data.get('jp_name'),
                                        'en_name': form_data.get('en_name'),
                                        'type1': form_data.get('type1', 'Normal'),
                                        'type2': form_data.get('type2'),
                                        'hp': form_data.get('hp'),
                                        'attack': form_data.get('attack'),
                                        'defense': form_data.get('defense'),
                                        'sp_atk': form_data.get('sp_atk'),
                                        'sp_def': form_data.get('sp_def'),
                                        'speed': form_data.get('speed'),
                                        'total': form_data.get('total', 0),
                                        'height': form_data.get('height'),
                                        'weight': form_data.get('weight'),
                                        'gender_ratio': form_data.get('gender_ratio'),
                                        'description': form_data.get('description'),
                                        'image_path': form_data.get('image_path')
                                    }
                                    variants.append(variant_pokemon)
                        except Exception as e:
                            print(f"处理变种宝可梦数据失败 {filename}: {e}")
            
            # 将变种形态添加到宝可梦数据中
            pokemon_data['variants'] = variants
            return pokemon_data
        return None
    except Exception as e:
        print(f"查询宝可梦失败: {e}")
        return None

def get_all_pokemon():
    """获取所有宝可梦信息，包括变种形态"""
    if db_instance is None:
        init_db()

    try:
        cursor = db_instance.conn.cursor()
        cursor.execute("SELECT * FROM pokemon ORDER BY id")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        pokemon_list = []
        for row in rows:
            pokemon_data = dict(zip(columns, row))
            # 将gender_ratio从JSON字符串解析为对象
            if pokemon_data.get('gender_ratio'):
                try:
                    pokemon_data['gender_ratio'] = json.loads(pokemon_data['gender_ratio'])
                except:
                    pokemon_data['gender_ratio'] = {}
            pokemon_list.append(pokemon_data)

        # 从pokemon_data_all目录中读取变种形态的数据
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend/spider/pokemon_data_all")
        print(f"变种宝可梦数据目录: {data_dir}")
        print(f"目录是否存在: {os.path.exists(data_dir)}")
        if os.path.exists(data_dir):
            variant_count = 0
            for filename in os.listdir(data_dir):
                if filename.endswith('.json'):
                    try:
                        # 解析文件名获取id和名称
                        parts = filename[:-5].split('_')  # 移除.json后缀
                        if len(parts) >= 2:
                            pokemon_id = int(parts[0])
                            form_name = '_'.join(parts[1:])
                            
                            # 读取变种数据
                            with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
                                form_data = json.load(f)
                            
                            # 构建变种宝可梦数据
                            variant_pokemon = {
                                'id': pokemon_id,
                                'name': form_data.get('name', ''),
                                'jp_name': form_data.get('jp_name'),
                                'en_name': form_data.get('en_name'),
                                'type1': form_data.get('type1', 'Normal'),
                                'type2': form_data.get('type2'),
                                'hp': form_data.get('hp'),
                                'attack': form_data.get('attack'),
                                'defense': form_data.get('defense'),
                                'sp_atk': form_data.get('sp_atk'),
                                'sp_def': form_data.get('sp_def'),
                                'speed': form_data.get('speed'),
                                'total': form_data.get('total', 0),
                                'height': form_data.get('height'),
                                'weight': form_data.get('weight'),
                                'gender_ratio': form_data.get('gender_ratio'),
                                'description': form_data.get('description'),
                                'image_path': form_data.get('image_path')
                            }
                            
                            # 检查是否已经存在相同名称的宝可梦
                            if not any(p['name'] == variant_pokemon['name'] for p in pokemon_list):
                                pokemon_list.append(variant_pokemon)
                                variant_count += 1
                                if variant_count <= 10:  # 只显示前10个变种宝可梦
                                    print(f"添加变种宝可梦: {variant_pokemon['name']} (#{variant_pokemon['id']})")
                    except Exception as e:
                        print(f"处理变种宝可梦数据失败 {filename}: {e}")
            print(f"总共添加了 {variant_count} 个变种宝可梦")
            print(f"宝可梦总数: {len(pokemon_list)}")
        
        return pokemon_list
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

def insert_item(item_data):
    """插入物品信息"""
    if db_instance is None:
        init_db()

    try:
        cursor = db_instance.conn.cursor()
        sql = """
        INSERT OR IGNORE INTO items
        (id, name, english, category, num, spritenum, desc, shortDesc, gen, isPokeball)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (
            item_data["id"], item_data["name"], item_data.get("english"),
            item_data.get("category"), item_data.get("num"),
            item_data.get("spritenum"), item_data.get("desc"),
            item_data.get("shortDesc"), item_data.get("gen"),
            item_data.get("isPokeball")
        ))
        db_instance.conn.commit()
        print(f"成功插入物品: {item_data['name']}")
    except Exception as e:
        print(f"插入物品失败: {e}")

def get_all_items():
    """获取所有物品信息"""
    if db_instance is None:
        init_db()

    try:
        cursor = db_instance.conn.cursor()
        cursor.execute("SELECT * FROM items ORDER BY id")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"查询所有物品失败: {e}")
        return []

def close_db():
    """关闭数据库连接"""
    global db_instance
    if db_instance:
        db_instance.close()
        db_instance = None
