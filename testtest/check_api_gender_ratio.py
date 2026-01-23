#!/usr/bin/env python3
import requests

# 获取皮卡丘的API响应
response = requests.get('http://localhost:8003/api/pokemon/25')

if response.status_code == 200:
    pokemon_data = response.json()
    print("=== API响应中的数据 ===")
    print(f"ID: {pokemon_data.get('id')}")
    print(f"Name: {pokemon_data.get('name')}")
    print(f"gender_ratio: {pokemon_data.get('gender_ratio')}")
    print(f"gender_ratio类型: {type(pokemon_data.get('gender_ratio'))}")
else:
    print(f"API请求失败: {response.status_code}")