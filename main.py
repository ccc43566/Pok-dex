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
    from database import get_all_pokemon, get_pokemon_by_id, init_db
    print("数据库模块导入成功")
except ImportError as e:
    print(f"数据库模块导入失败: {e}")
    # 尝试备用导入方式
    try:
        import database
        get_all_pokemon = database.get_all_pokemon
        get_pokemon_by_id = database.get_pokemon_by_id
        init_db = database.init_db
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
    description: Optional[str] = None
    image_path: Optional[str] = None

# 初始化数据库
init_db()

@app.get("/api/pokemon", response_model=List[Pokemon])
async def get_pokemon(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回的记录数"),
    type_filter: Optional[str] = Query(None, description="按属性过滤"),
    search: Optional[str] = Query(None, description="搜索宝可梦名称")
):
    """
    获取宝可梦列表

    - **skip**: 跳过的记录数（分页用）
    - **limit**: 返回的记录数（最大100）
    - **type_filter**: 按属性过滤（如 "Fire"）
    - **search**: 搜索宝可梦名称
    """
    all_pokemon = get_all_pokemon()

    # 搜索过滤
    if search:
        search_lower = search.lower()
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
    根据名称搜索宝可梦
    """
    all_pokemon = get_all_pokemon()
    name_lower = name.lower()

    results = []
    for p in all_pokemon:
        if (name_lower in p['name'].lower() or
            (p.get('en_name') and name_lower in p['en_name'].lower()) or
            (p.get('jp_name') and name_lower in p['jp_name'].lower())):
            results.append(p)

    if not results:
        raise HTTPException(status_code=404, detail="未找到匹配的宝可梦")

    return {"results": results, "count": len(results)}

@app.get("/api/stats")
async def get_stats():
    """
    获取宝可梦统计信息
    """
    all_pokemon = get_all_pokemon()

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

    # 种族值统计
    total_stats = [p['total'] for p in all_pokemon]
    hp_stats = [p['hp'] for p in all_pokemon]
    attack_stats = [p['attack'] for p in all_pokemon]

    return {
        "total_pokemon": len(all_pokemon),
        "type_distribution": type_stats,
        "stats_summary": {
            "total_avg": sum(total_stats) / len(total_stats),
            "total_max": max(total_stats),
            "total_min": min(total_stats),
            "hp_avg": sum(hp_stats) / len(hp_stats),
            "attack_avg": sum(attack_stats) / len(attack_stats)
        }
    }

# 挂载静态文件（图片等）
# 获取正确的图片目录路径（相对于项目根目录）
project_root = os.path.dirname(os.path.abspath(__file__))
images_dir = os.path.join(project_root, "backend/spider/pokemon_images")
print(f"图片目录路径: {images_dir}")
print(f"图片目录存在: {os.path.exists(images_dir)}")

app.mount("/images", StaticFiles(directory=images_dir), name="images")

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
            "GET /api/stats": "获取统计信息",
            "GET /images/{filename}": "获取宝可梦图片"
        },
        "docs": "/docs"
    }

if __name__ == "__main__":
    print("启动宝可梦图鉴 API 服务器...")
    print("访问 http://localhost:8000 查看 API 文档")
    print("访问 http://localhost:8000/docs 查看交互式文档")
    print("访问 http://127.0.0.1:8000 查看 API 文档")
    uvicorn.run(app, host="127.0.0.1", port=8000)
