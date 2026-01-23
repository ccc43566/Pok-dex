import sys
import os

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(__file__))

# 添加db目录到路径
db_path = os.path.join(project_root, 'db')
sys.path.insert(0, db_path)

# 修改数据库路径环境变量
os.environ['DB_PATH'] = os.path.join(db_path, 'pokemon.db')

from database import init_db, insert_pokemon, get_pokemon_by_id

# 初始化数据库
init_db()

# 测试数据：空对象{}
test_data1 = {
    "id": 999,
    "name": "Test Pokemon 1",
    "type1": "Normal",
    "gender_ratio": {}  # 空对象
}

# 测试数据：有性别比例
test_data2 = {
    "id": 1000,
    "name": "Test Pokemon 2",
    "type1": "Normal",
    "gender_ratio": {"M": 0.5, "F": 0.5}  # 50% 雄性，50% 雌性
}

# 测试数据：无gender_ratio字段
test_data3 = {
    "id": 1001,
    "name": "Test Pokemon 3",
    "type1": "Normal"
}

# 插入测试数据
print("插入测试数据...")
insert_pokemon(test_data1)
insert_pokemon(test_data2)
insert_pokemon(test_data3)

# 查询测试数据
print("\n查询测试数据...")
pokemon1 = get_pokemon_by_id(999)
print(f"Test Pokemon 1 (空对象): {pokemon1.get('gender_ratio')}")

pokemon2 = get_pokemon_by_id(1000)
print(f"Test Pokemon 2 (有性别比例): {pokemon2.get('gender_ratio')}")

pokemon3 = get_pokemon_by_id(1001)
print(f"Test Pokemon 3 (无gender_ratio字段): {pokemon3.get('gender_ratio')}")