#!/usr/bin/env python3
import sys
import os

# 添加db目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'db')
sys.path.insert(0, db_path)

print(f"Python path: {sys.path}")
print(f"Current dir: {current_dir}")
print(f"DB path: {db_path}")

try:
    from database import get_pokemon_by_id, init_db
    print("Import successful")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

# 初始化数据库
init_db()

# 测试函数类型
print(f"get_pokemon_by_id type: {type(get_pokemon_by_id)}")

# 测试调用
result = get_pokemon_by_id(1)
print(f"Result type: {type(result)}")
print(f"Result: {result}")

if result and isinstance(result, dict):
    print(f"Pokemon name: {result.get('name')}")
else:
    print("Result is not a dict or is None")
