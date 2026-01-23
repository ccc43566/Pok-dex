import requests

# 测试API是否返回变种宝可梦
def test_variant_pokemon():
    try:
        # 获取宝可梦列表，使用最大的limit值100
        response = requests.get('http://localhost:8003/api/pokemon', params={'limit': 100})
        response.raise_for_status()
        pokemon_list = response.json()
        
        print(f"总共获取到 {len(pokemon_list)} 只宝可梦")
        
        # 查找变种宝可梦
        variant_pokemon = []
        for pokemon in pokemon_list:
            if '-' in pokemon['name']:
                variant_pokemon.append(pokemon)
        
        print(f"找到 {len(variant_pokemon)} 只变种宝可梦")
        print("变种宝可梦列表:")
        for pokemon in variant_pokemon[:20]:  # 显示前20个
            print(f"  - {pokemon['name']} (#{pokemon['id']})")
        
        if len(variant_pokemon) > 20:
            print(f"  ... 还有 {len(variant_pokemon) - 20} 个变种宝可梦")
        
        return True
    except Exception as e:
        print(f"测试失败: {e}")
        return False

if __name__ == "__main__":
    test_variant_pokemon()