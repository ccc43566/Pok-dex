import sqlite3
from sqlite3 import Error

class PokemonDB:
    """宝可梦数据库操作类，用于初始化表和基础数据库操作"""
    
    def __init__(self, db_file="pokemon.db"):
        """
        初始化数据库连接
        :param db_file: 数据库文件路径/名称，默认是 pokemon.db
        """
        self.db_file = db_file
        self.conn = None
        # 尝试连接数据库并创建所有表
        try:
            self.conn = sqlite3.connect(db_file)
            self.conn.execute("PRAGMA foreign_keys = ON")  # 开启外键约束
            print(f"成功连接到数据库: {db_file}")
            # 创建所有表
            self.create_all_tables()
        except Error as e:
            print(f"数据库连接/创建表失败: {e}")
    
    def create_all_tables(self):
        """创建所有宝可梦相关的表"""
        # 1. 创建宝可梦主表
        create_pokemon_sql = """
        CREATE TABLE IF NOT EXISTS pokemon (
             id INTEGER PRIMARY KEY,         -- 全国图鉴编号（如 25）
            name TEXT UNIQUE NOT NULL,       -- 名称（如 "皮卡丘"）
            jp_name TEXT,                    -- 日文名（可选）
            en_name TEXT,                    -- 英文名（可选）
            type1 TEXT NOT NULL,             -- 主属性
            type2 TEXT,                      -- 副属性（可能为空）
            hp INTEGER,                     -- 种族值
            attack INTEGER,
            defense INTEGER,
            sp_atk INTEGER,
            sp_def INTEGER,
            speed INTEGER,
            total INTEGER,                   -- 种族值总和
            height REAL,                     -- 身高（米）
            weight REAL,                     -- 体重（公斤）
            gender_ratio TEXT,               -- 雌雄比例（JSON格式）
            description TEXT,                -- 图鉴描述
            image_path TEXT                  -- 图片路径
        );
        """
        
        # 2. 创建技能表
        create_moves_sql = """
        CREATE TABLE IF NOT EXISTS moves (
            id INTEGER PRIMARY KEY, -- 技能唯一标识 ID，自动递增（主键）
            name TEXT UNIQUE NOT NULL,-- 技能名称（如 "十万伏特"、"喷射火焰"），必须唯一且不能为空
            type TEXT,-- 技能属性（如 "Electric" 电系、"Fire" 火系、"Normal" 一般系等）
            category TEXT, -- 技能类别：物理（Physical）、特殊（Special）或变化（Status）
            -- 物理：受攻击/防御影响；特殊：受特攻/特防影响；变化：无伤害，如状态变化技能
            power INTEGER,-- 技能威力（Power）：造成伤害的数值，0 表示无伤害（如变化类技能）
            accuracy INTEGER, -- 命中率（Accuracy）：以百分比表示（如 100 表示 100% 命中），NULL 表示必定命中
            pp INTEGER -- PP（Power Points）：技能可使用次数，使用后消耗，可通过道具恢复
        );
        """
        
        # 3. 创建宝可梦-技能关联表
        create_pokemon_moves_sql = """
        CREATE TABLE IF NOT EXISTS pokemon_moves (
            pokemon_id INTEGER,
            move_id INTEGER,
            level_learned INTEGER,
            FOREIGN KEY(pokemon_id) REFERENCES pokemon(id),
            FOREIGN KEY(move_id) REFERENCES moves(id),
            PRIMARY KEY(pokemon_id, move_id)
        );
        """
        
        # 4. 创建进化链表
        create_evolutions_sql = """
        CREATE TABLE IF NOT EXISTS evolutions (
            base_pokemon_id INTEGER,
            evolved_pokemon_id INTEGER,
            condition TEXT,
            FOREIGN KEY(base_pokemon_id) REFERENCES pokemon(id),
            FOREIGN KEY(evolved_pokemon_id) REFERENCES pokemon(id)
        );
        """

        # 5. 创建物品表
        create_items_sql = """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            english TEXT,
            category TEXT,
            num INTEGER,
            spritenum INTEGER,
            desc TEXT,
            shortDesc TEXT,
            gen INTEGER,
            isPokeball BOOLEAN
        );
        """
        
        # 执行所有建表语句
        try:
            cursor = self.conn.cursor()
            cursor.execute(create_pokemon_sql)
            cursor.execute(create_moves_sql)
            cursor.execute(create_pokemon_moves_sql)
            cursor.execute(create_evolutions_sql)
            cursor.execute(create_items_sql)
            self.conn.commit()
            print("所有表创建成功（或已存在）")
        except Error as e:
            print(f"创建表失败: {e}")
    
    
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            print("数据库连接已关闭")

def insert_pokemon(self, pokemon_data):
        """
        插入单条宝可梦数据         ===========格式
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


if __name__ == "__main__":
    # 创建数据库实例（自动创建所有表）
    db = PokemonDB()
    db.close()
