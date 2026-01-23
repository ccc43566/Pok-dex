import json
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
import sys

# 添加db目录到路径并导入
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'db')
sys.path.insert(0, db_path)

try:
    from database import (
        get_all_pokemon, get_pokemon_by_id, init_db,
        get_all_items, get_all_moves, get_evolutions
    )
    print("数据库模块导入成功")
except ImportError as e:
    print(f"数据库模块导入失败: {e}")
    # 尝试备用导入方式
    try:
        import database
        get_all_pokemon = database.get_all_pokemon
        get_pokemon_by_id = database.get_pokemon_by_id
        init_db = database.init_db
        get_all_items = database.get_all_items
        get_all_moves = database.get_all_moves
        get_evolutions = database.get_evolutions
        print("备用导入方式成功")
    except ImportError as e2:
        print(f"备用导入也失败: {e2}")
        raise

app = FastAPI(title="宝可梦图鉴 API", description="提供宝可梦数据的REST API")

# 允许前端跨域请求（开发时必需）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],  # Vue, React, 开发时允许所有
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic模型
class Pokemon(BaseModel):
    id: int
    name: str
    jp_name: Optional[str] = None
    en_name: Optional[str] = None
    type1: str
    type2: Optional[str] = None
    hp: Optional[int] = None
    attack: Optional[int] = None
    defense: Optional[int] = None
    sp_atk: Optional[int] = None
    sp_def: Optional[int] = None
    speed: Optional[int] = None
    total: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    gender_ratio: Optional[dict] = None
    description: Optional[str] = None
    image_path: Optional[str] = None
    variants: Optional[List['Pokemon']] = []

# 更新forward references
Pokemon.model_rebuild()

# 初始化数据库
init_db()

@app.get("/api/pokemon", response_model=List[Pokemon])
async def get_pokemon(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回的记录数"),
    type_filter: Optional[str] = Query(None, description="按属性过滤"),
    search: Optional[str] = Query(None, description="搜索宝可梦名称"),
    generation: Optional[int] = Query(None, description="按世代过滤")
):
    """
    获取宝可梦列表

    - **skip**: 跳过的记录数（分页用）
    - **limit**: 返回的记录数（最大100）
    - **type_filter**: 按属性过滤（如 "Fire"）
    - **search**: 搜索宝可梦名称
    - **generation**: 按世代过滤（1-9）
    """
    all_pokemon = get_all_pokemon()

    # 世代过滤
    if generation:
        # 世代与编号范围的映射
        gen_ranges = {
            1: (1, 151),
            2: (152, 251),
            3: (252, 386),
            4: (387, 493),
            5: (494, 649),
            6: (650, 721),
            7: (722, 809),
            8: (810, 905),
            9: (906, 1025)
        }
        
        if generation in gen_ranges:
            start, end = gen_ranges[generation]
            all_pokemon = [
                p for p in all_pokemon
                if start <= p['id'] <= end
            ]

    # 搜索过滤
    if search:
        search_lower = search.lower()
        # 检查是否为数字，用于按序号搜索
        if search.isdigit():
            search_id = int(search)
            all_pokemon = [
                p for p in all_pokemon
                if p['id'] == search_id or
                   search_lower in p['name'].lower() or
                   (p.get('en_name') and search_lower in p['en_name'].lower()) or
                   (p.get('jp_name') and search_lower in p['jp_name'].lower())
            ]
        else:
            all_pokemon = [
                p for p in all_pokemon
                if search_lower in p['name'].lower() or
                   (p.get('en_name') and search_lower in p['en_name'].lower()) or
                   (p.get('jp_name') and search_lower in p['jp_name'].lower())
            ]

    # 属性过滤
    if type_filter:
        type_filter_lower = type_filter.lower()
        all_pokemon = [
            p for p in all_pokemon
            if type_filter_lower in p['type1'].lower() or
               (p.get('type2') and type_filter_lower in p['type2'].lower())
        ]

    # 分页
    total = len(all_pokemon)
    pokemon_list = all_pokemon[skip:skip + limit]

    return pokemon_list

@app.get("/api/pokemon/{pokemon_id}")
async def get_single_pokemon(pokemon_id: int):
    """
    根据ID获取单个宝可梦信息
    """
    print(f"收到请求: GET /api/pokemon/{pokemon_id}")
    try:
        print(f"调用数据库查询: get_pokemon_by_id({pokemon_id})")
        print(f"函数类型: {type(get_pokemon_by_id)}")
        pokemon = get_pokemon_by_id(pokemon_id)
        print(f"数据库返回类型: {type(pokemon)}")
        print(f"数据库返回: {pokemon}")

        if not pokemon:
            print(f"宝可梦 {pokemon_id} 未找到")
            raise HTTPException(status_code=404, detail="宝可梦未找到")

        # 查找mega和gmax形态
        base_name = pokemon['name']
        mega_gmax_forms = find_mega_gmax_forms(pokemon_id, base_name)
        pokemon['mega_gmax_forms'] = mega_gmax_forms

        print(f"返回宝可梦数据: {pokemon.get('name', 'Unknown') if isinstance(pokemon, dict) else 'Not dict'}")
        return pokemon
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting pokemon {pokemon_id}: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

@app.get("/api/pokemon/search/{name}")
async def search_pokemon_by_name(name: str):
    """
    根据名称或序号搜索宝可梦
    """
    all_pokemon = get_all_pokemon()
    name_lower = name.lower()

    results = []
    for p in all_pokemon:
        # 检查是否为数字，用于按序号搜索
        if name.isdigit():
            search_id = int(name)
            if (p['id'] == search_id or
                name_lower in p['name'].lower() or
                (p.get('en_name') and name_lower in p['en_name'].lower()) or
                (p.get('jp_name') and name_lower in p['jp_name'].lower())):
                results.append(p)
        else:
            if (name_lower in p['name'].lower() or
                (p.get('en_name') and name_lower in p['en_name'].lower()) or
                (p.get('jp_name') and name_lower in p['jp_name'].lower())):
                results.append(p)

    if not results:
        raise HTTPException(status_code=404, detail="未找到匹配的宝可梦")

    return {"results": results, "count": len(results)}

@app.get("/api/items")
async def get_items(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回的记录数"),
    category_filter: Optional[str] = Query(None, description="按类别过滤"),
    search: Optional[str] = Query(None, description="搜索物品名称")
):
    """
    获取物品列表
    """
    all_items = get_all_items()

    # 搜索过滤
    if search:
        search_lower = search.lower()
        all_items = [
            i for i in all_items
            if search_lower in i['name'].lower() or
               (i.get('english') and search_lower in i['english'].lower())
        ]

    # 类别过滤
    if category_filter:
        category_filter_lower = category_filter.lower()
        all_items = [
            i for i in all_items
            if i.get('category') and category_filter_lower in i['category'].lower()
        ]

    # 分页
    total = len(all_items)
    items_list = all_items[skip:skip + limit]

    return {"items": items_list, "total": total, "skip": skip, "limit": limit}

@app.get("/api/moves")
async def get_moves(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回的记录数"),
    type_filter: Optional[str] = Query(None, description="按属性过滤"),
    category_filter: Optional[str] = Query(None, description="按类别过滤"),
    search: Optional[str] = Query(None, description="搜索技能名称")
):
    """
    获取技能列表
    """
    all_moves = get_all_moves()

    # 搜索过滤
    if search:
        search_lower = search.lower()
        all_moves = [
            m for m in all_moves
            if search_lower in m['name'].lower()
        ]

    # 属性过滤
    if type_filter:
        type_filter_lower = type_filter.lower()
        all_moves = [
            m for m in all_moves
            if m.get('type') and type_filter_lower in m['type'].lower()
        ]

    # 类别过滤
    if category_filter:
        category_filter_lower = category_filter.lower()
        all_moves = [
            m for m in all_moves
            if m.get('category') and category_filter_lower in m['category'].lower()
        ]

    # 分页
    total = len(all_moves)
    moves_list = all_moves[skip:skip + limit]

    return {"moves": moves_list, "total": total, "skip": skip, "limit": limit}

@app.get("/api/items/categories")
async def get_item_categories():
    """
    获取所有物品类别
    """
    all_items = get_all_items()
    categories = set()
    
    for item in all_items:
        if item.get('category'):
            categories.add(item['category'])
    
    return {"categories": sorted(list(categories))}

@app.get("/api/moves/filters")
async def get_move_filters():
    """
    获取技能过滤选项（属性和类别）
    """
    all_moves = get_all_moves()
    types = set()
    categories = set()
    
    for move in all_moves:
        if move.get('type'):
            types.add(move['type'])
        if move.get('category'):
            categories.add(move['category'])
    
    return {"types": sorted(list(types)), "categories": sorted(list(categories))}

@app.get("/api/pokemon/{pokemon_id}/evolutions")
async def get_pokemon_evolutions(pokemon_id: int):
    """
    获取宝可梦的完整进化信息
    """
    # 获取当前宝可梦的信息
    current_pokemon = get_pokemon_by_id(pokemon_id)
    if not current_pokemon:
        return {"evolutions": []}

    current_name = current_pokemon['name'].lower()

    # 从JSON文件中获取进化信息
    pokemon_data_file = f"backend/spider/pokemon_data_all/{pokemon_id}_{current_name}.json"
    if os.path.exists(pokemon_data_file):
        try:
            with open(pokemon_data_file, 'r', encoding='utf-8') as f:
                pokemon_data = json.load(f)

            # 构建完整的进化链
            full_evolution_chain = build_full_evolution_chain(current_name)

            return {"evolutions": full_evolution_chain}

        except Exception as e:
            print(f"读取宝可梦数据文件失败: {e}")

    # 如果没有找到文件，返回空数组
    return {"evolutions": []}

def build_full_evolution_chain(start_name):
    """
    从给定的宝可梦名称开始，构建完整的进化链
    """
    chain = []
    visited = set()

    def find_base_form(name):
        """递归查找基础形态"""
        if name in visited:
            return None
        visited.add(name)

        # 查找这个宝可梦的数据文件
        pokemon_id = find_pokemon_id_by_name(name)
        if not pokemon_id:
            return None

        data_file = f"backend/spider/pokemon_data_all/{pokemon_id}_{name.lower()}.json"
        if not os.path.exists(data_file):
            return None

        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 如果有上一形态，继续递归
            if data.get('prevo'):
                base = find_base_form(data['prevo'])
                if base:
                    return base

            # 没有上一形态了，这就是基础形态
            return name

        except Exception as e:
            print(f"读取数据文件失败 {name}: {e}")
            return None

    def build_chain_with_branches(current_name, current_chain, step_count):
        """递归构建带分支的进化链"""
        if current_name in visited or step_count >= 10:  # 防止无限循环
            return

        # 查找这个宝可梦的数据
        pokemon_id = find_pokemon_id_by_name(current_name)
        if not pokemon_id:
            return

        data_file = f"backend/spider/pokemon_data_all/{pokemon_id}_{current_name.lower()}.json"
        if not os.path.exists(data_file):
            return

        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 创建当前宝可梦的进化信息
            current_pokemon = {
                "id": pokemon_id,
                "name": current_name,
                "condition": format_evolution_condition(data) if step_count > 0 else None
            }

            # 添加到当前链
            new_chain = current_chain + [current_pokemon]

            # 如果没有更多进化形态，将当前链添加到结果中
            if not data.get('evos') or len(data['evos']) == 0:
                # 检查是否已经添加过相同的链
                chain_exists = False
                for existing_chain in chain:
                    if len(existing_chain) == len(new_chain):
                        match = True
                        for i in range(len(existing_chain)):
                            if existing_chain[i]['name'] != new_chain[i]['name']:
                                match = False
                                break
                        if match:
                            chain_exists = True
                            break
                if not chain_exists:
                    chain.append(new_chain)
                return

            # 标记当前宝可梦为已访问
            visited.add(current_name)

            # 处理每个进化形态（分支进化）
            for i, evo_name in enumerate(data['evos']):
                # 对于非第一个进化形态，创建新的分支链
                build_chain_with_branches(evo_name, new_chain, step_count + 1)

        except Exception as e:
            print(f"读取数据文件失败 {current_name}: {e}")

    # 找到基础形态
    base_form = find_base_form(start_name)
    if base_form:
        # 清空visited集合，为构建链做准备
        visited.clear()
        # 从基础形态开始构建完整链
        build_chain_with_branches(base_form, [], 0)

    return chain

def find_mega_gmax_forms(pokemon_id, base_name):
    """
    查找宝可梦的mega和gmax形态
    """
    mega_gmax_forms = []
    
    # 遍历宝可梦数据目录，查找包含mega或gmax的文件
    data_dir = "backend/spider/pokemon_data_all"
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.startswith(f"{pokemon_id}_"):
                # 提取文件名中的宝可梦名称（不含id和扩展名）
                name_part = filename[len(f"{pokemon_id}_"):-5]  # 移除id_前缀和.json后缀
                
                # 只检查mega和gmax形态
                if any(keyword in name_part.lower() for keyword in ['mega', 'gmax']):
                    # 构建完整的宝可梦名称
                    full_name = base_name
                    
                    # 处理mega和gmax形态
                    if 'megax' in name_part.lower():
                        full_name = base_name + '-Mega-X'
                    elif 'megay' in name_part.lower():
                        full_name = base_name + '-Mega-Y'
                    elif 'mega' in name_part.lower():
                        full_name = base_name + '-Mega'
                    elif 'gmax' in name_part.lower():
                        full_name = base_name + '-Gmax'
                    
                    mega_gmax_forms.append({
                        "id": pokemon_id,
                        "name": full_name,
                        "form_name": name_part
                    })
    
    return mega_gmax_forms

def format_evolution_condition(pokemon_data):
    """根据宝可梦数据格式化进化条件"""
    evo_type = pokemon_data.get('evo_type')
    evo_level = pokemon_data.get('evo_level')
    evo_item = pokemon_data.get('evo_item')

    # 处理不同的进化类型
    if evo_type == 'levelFriendship':
        return "亲密度"
    elif evo_type == 'useItem' and evo_item:
        # 翻译常见的进化物品
        item_translations = {
            'Thunder Stone': '雷之石',
            'Fire Stone': '火之石',
            'Water Stone': '水之石',
            'Leaf Stone': '叶之石',
            'Moon Stone': '月之石',
            'Sun Stone': '太阳石',
            'Shiny Stone': '光之石',
            'Dusk Stone': '暗之石',
            'Dawn Stone': '觉醒之石',
            'Ice Stone': '冰之石',
            'Metal Alloy': '合金块',
            'Syrupy Apple': '蜜汁苹果',
            'Unremarkable Teacup': '不起眼的茶碗',
            'Masterpiece Teacup': '杰作茶碗',
            'Galarica Wreath': '伽勒尔花冠',
            'Dragon Scale': '龙之鳞片',
            'King\'s Rock': '王者之证',
            'Deep Sea Tooth': '深海之牙',
            'Deep Sea Scale': '深海鳞片',
            'Upgrade': '金属膜',
            'Protector': '防护罩',
            'Electirizer': '电引擎',
            'Magmarizer': '熔岩引擎',
            'Dubious Disc': '可疑补丁',
            'Reaper Cloth': '怨念布',
            'Prism Scale': '美丽鳞片',
            'Whipped Dream': '泡绵奶油',
            'Sachet': '香袋',
            'Razor Claw': '锐利之爪',
            'Razor Fang': '锐利之牙',
            'Auspicious Armor': '吉利拳套',          # 朱／紫 新增
            'Malicious Armor': '凶恶拳套',          # 朱／紫 新增
            'Peat Block': '泥炭块',                # 朱／紫 DLC 新增（用于土王进化）
            'Linking Cord': '连接线绳',             # 朱／紫 新增（快速进化，如小箭雀→火箭雀）
            'Cracked Pot': '裂纹壶',               # 茶杯系列基础形态
            'Chipped Pot': '缺角壶',               # 茶杯系列中间形态（非进化道具，但相关）
        }
        item_name = item_translations.get(evo_item, evo_item)
        return f"使用{item_name}"
    elif evo_type == 'trade' and evo_item:
        return f"交换（持有{evo_item}）"
    elif evo_type == 'trade':
        return "交换"
    elif evo_type == 'levelMove':
        return "等级+学习技能"
    elif evo_type == 'levelHold' and evo_item:
        return f"等级+持有{evo_item}"
    elif evo_type == 'levelExtra':
        return "等级+额外条件"
    elif evo_type == 'other':
        return "特殊进化"
    elif evo_level:
        return f"等级{evo_level}"
    else:
        return "进化条件未知"

def find_pokemon_id_by_name(name):
    """根据宝可梦名称查找ID"""
    try:
        all_pokemon = get_all_pokemon()
        for pokemon in all_pokemon:
            if pokemon['name'].lower() == name.lower():
                return pokemon['id']
        return None
    except Exception as e:
        print(f"查找宝可梦ID失败: {e}")
        return None

def get_pokemon_name_by_id(pokemon_id):
    """根据ID获取宝可梦名称（小写）"""
    # 这里应该从数据库查询，但为了简化，我们返回一个默认名称
    return "unknown"

def get_evolution_condition_from_names(base_name, evolved_name):
    """根据名称获取进化条件"""
    # 常见进化条件映射（与insert_data.py中的相同）
    evolution_conditions = {
        # 喷火龙进化链
        ("charmander", "charmeleon"): "等级16",
        ("charmeleon", "charizard"): "等级36",
        # 妙蛙种子进化链
        ("bulbasaur", "ivysaur"): "等级16",
        ("ivysaur", "venusaur"): "等级32",
        # 杰尼龟进化链
        ("squirtle", "wartortle"): "等级16",
        ("wartortle", "blastoise"): "等级36",
        # 绿毛虫进化链
        ("caterpie", "metapod"): "等级7",
        ("metapod", "butterfree"): "等级10",
        # 其他常见进化
        ("krabby", "kingler"): "等级28",
        ("pichu", "pikachu"): "亲密度",
        ("pikachu", "raichu"): "雷之石",
    }

    return evolution_conditions.get((base_name.lower(), evolved_name.lower()), "进化条件未知")

@app.get("/api/stats")
async def get_stats():
    """
    获取宝可梦统计信息
    """
    all_pokemon = get_all_pokemon()
    all_items = get_all_items()
    all_moves = get_all_moves()

    # 计算属性分布
    type_stats = {}
    for p in all_pokemon:
        t1 = p['type1']
        t2 = p.get('type2')

        if t1 not in type_stats:
            type_stats[t1] = 0
        type_stats[t1] += 1

        if t2:
            if t2 not in type_stats:
                type_stats[t2] = 0
            type_stats[t2] += 1

    # 物品类别分布
    item_category_stats = {}
    for i in all_items:
        category = i.get('category', '其他')
        if category not in item_category_stats:
            item_category_stats[category] = 0
        item_category_stats[category] += 1

    # 技能属性分布
    move_type_stats = {}
    for m in all_moves:
        move_type = m.get('type', 'Normal')
        if move_type not in move_type_stats:
            move_type_stats[move_type] = 0
        move_type_stats[move_type] += 1

    # 种族值统计
    total_stats = [p['total'] for p in all_pokemon if p.get('total')]
    hp_stats = [p['hp'] for p in all_pokemon if p.get('hp')]
    attack_stats = [p['attack'] for p in all_pokemon if p.get('attack')]

    return {
        "total_pokemon": len(all_pokemon),
        "total_items": len(all_items),
        "total_moves": len(all_moves),
        "type_distribution": type_stats,
        "item_category_distribution": item_category_stats,
        "move_type_distribution": move_type_stats,
        "stats_summary": {
            "total_avg": sum(total_stats) / len(total_stats) if total_stats else 0,
            "total_max": max(total_stats) if total_stats else 0,
            "total_min": min(total_stats) if total_stats else 0,
            "hp_avg": sum(hp_stats) / len(hp_stats) if hp_stats else 0,
            "attack_avg": sum(attack_stats) / len(attack_stats) if attack_stats else 0
        }
    }

# 挂载静态文件（图片等）
# 获取正确的图片目录路径（相对于项目根目录）
project_root = os.path.dirname(os.path.abspath(__file__))
images_dir = os.path.join(project_root, "backend/spider/pokemon_gif_images")
png_images_dir = os.path.join(project_root, "backend/spider/pokemon_png_images")
print(f"GIF图片目录路径: {images_dir}")
print(f"GIF图片目录存在: {os.path.exists(images_dir)}")
print(f"PNG图片目录路径: {png_images_dir}")
print(f"PNG图片目录存在: {os.path.exists(png_images_dir)}")

# 挂载 GIF 图片目录（用于正常展示的宝可梦）
app.mount("/images", StaticFiles(directory=images_dir), name="images")
# 挂载 PNG 图片目录（用于世代御三家）
app.mount("/png-images", StaticFiles(directory=png_images_dir), name="png_images")

@app.get("/")
async def root():
    """
    API根路径，返回欢迎信息
    """
    return {
        "message": "欢迎使用宝可梦图鉴 API",
        "version": "1.0",
        "endpoints": {
            "GET /api/pokemon": "获取宝可梦列表（支持分页、搜索、过滤）",
            "GET /api/pokemon/{id}": "获取单个宝可梦",
            "GET /api/pokemon/search/{name}": "按名称搜索宝可梦",
            "GET /api/pokemon/{id}/evolutions": "获取宝可梦进化信息",
            "GET /api/items": "获取物品列表（支持分页、搜索、过滤）",
            "GET /api/moves": "获取技能列表（支持分页、搜索、过滤）",
            "GET /api/stats": "获取统计信息",
            "GET /images/{filename}": "获取宝可梦图片"
        },
        "docs": "/docs"
    }

if __name__ == "__main__":
    print("启动宝可梦图鉴 API 服务器...")
    print("访问 http://localhost:8003 查看 API 文档")
    print("访问 http://localhost:8003/docs 查看交互式文档")
    print("访问 http://127.0.0.1:8003 查看 API 文档")
    uvicorn.run(app, host="0.0.0.0", port=8003)
