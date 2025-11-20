import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(title="宝可梦图鉴 API")

# 在模块顶层加载一次宝可梦图鉴json数据
with open('pokedex.json', 'r', encoding='utf-8') as f:
    POKEDEX = json.load(f)

# 托管 images 文件夹（让 /images/xxx.webp 可访问）
if os.path.exists("images"):
    app.mount("/images", StaticFiles(directory="images"), name="images")

def search_pokemon(name_or_id):
    # 先尝试按编号找（如 "001"）
    if name_or_id.isdigit() and name_or_id in POKEDEX:
        return POKEDEX[name_or_id]
    # 再尝试按名字找（模糊匹配）
    for pokemon_id, data in POKEDEX.items():
        if name_or_id.lower() == data['name'].lower():  # 考虑宝可梦英文大小写不敏感的匹配
            return data
    return None

@app.get("/pokemon/{pokemon_id}")
def get_pokemon(pokemon_id_or_name: str):
    # 补零兼容：用户输入 "1" 自动转为 "001"
    if pokemon_id_or_name.isdigit():
        pokemon_id_or_name = pokemon_id_or_name.zfill(3)  # 1 → "001", 25 → "025"
    # 使用 search_pokemon 函数查找宝可梦
    data = search_pokemon(pokemon_id_or_name)
    if not data:
        raise HTTPException(status_code=404, detail="宝可梦未找到")
    # 构造图片 URL
    image_filename = os.path.basename(data["image"])
    data["image_url"] = f"/images/{image_filename}"
    return data


if __name__ == '__main__':
    uvicorn.run(app='main:app', host='127.0.0.1', port=8000, reload=True)

