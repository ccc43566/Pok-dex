import requests

# 测试获取宝可梦详情（包含变种形态）
def test_pokemon_variants():
    # 测试皮卡丘（ID: 25），它应该有多个变种形态
    pokemon_id = 25
    url = f"http://localhost:8003/api/pokemon/{pokemon_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        
        pokemon_data = response.json()
        print(f"宝可梦名称: {pokemon_data['name']} (#{pokemon_data['id']})")
        print(f"基础形态属性: {pokemon_data['type1']} / {pokemon_data.get('type2', '无')}")
        
        # 检查是否包含变种形态
        if 'variants' in pokemon_data:
            variants = pokemon_data['variants']
            print(f"\n找到 {len(variants)} 个变种形态:")
            for i, variant in enumerate(variants):
                print(f"  {i+1}. {variant['name']}")
                print(f"     属性: {variant['type1']} / {variant.get('type2', '无')}")
                print(f"     种族值总和: {variant.get('total', 0)}")
        else:
            print("\n未找到变种形态数据")
            
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    print("测试宝可梦详情接口（包含变种形态）\n")
    test_pokemon_variants()