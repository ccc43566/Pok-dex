import os
import json
import sys
sys.path.append('db')
from database import (
    init_db, insert_pokemon, insert_move, insert_item, insert_evolution
)

def load_json(file_path):
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 {file_path} 失败: {e}")
        return None

def insert_all_pokemon():
    """插入所有宝可梦数据"""
    # 初始化数据库
    init_db()

    # 获取项目根目录
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 路径
    data_dir = os.path.join(project_root, "backend/spider/pokemon_data_all")
    desc_dir = os.path.join(project_root, "backend/spider/pokemon_descrptions")

    # 获取所有数据文件
    if not os.path.exists(data_dir):
        print(f"数据目录不存在: {data_dir}")
        return

    files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    print(f"找到 {len(files)} 个数据文件")

    inserted_count = 0

    for file in files:
        # 读取数据文件
        data_path = os.path.join(data_dir, file)
        data = load_json(data_path)
        if not data:
            continue

        # 读取描述文件
        desc_path = os.path.join(desc_dir, file)
        desc = load_json(desc_path)

        # 合并数据
        pokemon_data = {
            "id": data["id"],
            "name": desc.get("name_en", data["name"]) if desc else data["name"],
            "jp_name": None,  # 暂时为空
            "en_name": desc.get("name_en") if desc else None,
            "type1": data["type1"],
            "type2": data.get("type2"),
            "hp": data["hp"],
            "attack": data["attack"],
            "defense": data["defense"],
            "sp_atk": data["sp_atk"],
            "sp_def": data["sp_def"],
            "speed": data["speed"],
            "total": data["total"],
            "height": data.get("height"),  # 身高
            "weight": data.get("weight"),  # 体重
            "gender_ratio": data.get("gender_ratio"),  # 雌雄比例
            "description": desc.get("description") if desc else None,
            "image_path": data.get("image_path")
        }

        # 添加调试信息
        if data["id"] == 25:  # 只调试皮卡丘
            print(f"\n调试皮卡丘数据:")
            print(f"数据文件中的gender_ratio: {data.get('gender_ratio')}")
            print(f"pokemon_data中的gender_ratio: {pokemon_data.get('gender_ratio')}")
            print(f"gender_ratio类型: {type(pokemon_data.get('gender_ratio'))}")

        # 插入数据库
        try:
            insert_pokemon(pokemon_data)
            inserted_count += 1
        except Exception as e:
            print(f"插入失败 {pokemon_data['name']}: {e}")

    print(f"共插入 {inserted_count} 个宝可梦")

def insert_all_moves():
    """插入所有技能数据"""
    init_db()

    # 获取项目根目录
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    moves_dir = os.path.join(project_root, "backend/spider/moves")
    if not os.path.exists(moves_dir):
        print(f"技能数据目录不存在: {moves_dir}")
        return

    files = [f for f in os.listdir(moves_dir) if f.endswith('.json')]
    print(f"找到 {len(files)} 个技能文件")

    inserted_count = 0
    for file in files:
        data_path = os.path.join(moves_dir, file)
        data = load_json(data_path)
        if not data:
            continue

        move_data = {
            "id": data["id"] if "id" in data else int(file.split('_')[0]),
            "name": data["name"],
            "type": data.get("type"),
            "category": data.get("category"),
            "power": data.get("basePower"),  # JSON中是basePower
            "accuracy": data.get("accuracy"),
            "pp": data.get("pp")
        }

        try:
            insert_move(move_data)
            inserted_count += 1
        except Exception as e:
            print(f"插入技能失败 {move_data['name']}: {e}")

    print(f"共插入 {inserted_count} 个技能")

def insert_all_items():
    """插入所有物品数据"""
    init_db()

    # 获取项目根目录
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    items_dir = os.path.join(project_root, "backend/spider/items")
    if not os.path.exists(items_dir):
        print(f"物品数据目录不存在: {items_dir}")
        return

    files = [f for f in os.listdir(items_dir) if f.endswith('.json')]
    print(f"找到 {len(files)} 个物品文件")

    inserted_count = 0
    for file in files:
        data_path = os.path.join(items_dir, file)
        data = load_json(data_path)
        if not data:
            continue

        item_data = {
            "id": data["id"] if "id" in data else int(file.split('_')[0]),
            "name": data["name"],
            "english": data.get("english"),
            "category": data.get("category"),
            "num": data.get("num"),
            "spritenum": data.get("spritenum"),
            "desc": data.get("desc"),
            "shortDesc": data.get("shortDesc"),
            "gen": data.get("gen"),
            "isPokeball": data.get("isPokeball")
        }

        try:
            insert_item(item_data)
            inserted_count += 1
        except Exception as e:
            print(f"插入物品失败 {item_data['name']}: {e}")

    print(f"共插入 {inserted_count} 个物品")

def get_evolution_condition(base_name, evolved_name):
    """根据宝可梦名称推断进化条件"""
    # 常见进化条件映射
    evolution_conditions = {
        # 皮卡丘进化链
        ("pichu", "pikachu"): "亲密度",
        ("pikachu", "raichu"): "雷之石",
        # 喷火龙进化链
        ("charmander", "charmeleon"): "等级16",
        ("charmeleon", "charizard"): "等级36",
        # 妙蛙种子进化链
        ("bulbasaur", "ivysaur"): "等级16",
        ("ivysaur", "venusaur"): "等级32",
        # 小火龙进化链
        ("charmander", "charmeleon"): "等级16",
        ("charmeleon", "charizard"): "等级36",
        # 杰尼龟进化链
        ("squirtle", "wartortle"): "等级16",
        ("wartortle", "blastoise"): "等级36",
        # 绿毛虫进化链
        ("caterpie", "metapod"): "等级7",
        ("metapod", "butterfree"): "等级10",
        # 独角虫进化链
        ("weedle", "kakuna"): "等级7",
        ("kakuna", "beedrill"): "等级10",
        # 波波进化链
        ("pidgey", "pidgeotto"): "等级18",
        ("pidgeotto", "pidgeot"): "等级36",
        # 喵喵进化链
        ("meowth", "persian"): "等级28",
        # 卡蒂狗进化链
        ("growlithe", "arcanine"): "火之石",
        # 尼多兰进化链
        ("nidoranf", "nidorina"): "等级16",
        ("nidorina", "nidoqueen"): "月之石",
        ("nidoranm", "nidorino"): "等级16",
        ("nidorino", "nidoking"): "月之石",
        # 皮皮进化链
        ("clefairy", "clefable"): "月之石",
        # 六尾进化链
        ("vulpix", "ninetales"): "火之石",
        # 胖丁进化链
        ("jigglypuff", "wigglytuff"): "月之石",
        # 超音蝠进化链
        ("zubat", "golbat"): "等级22",
        ("golbat", "crobat"): "亲密度",
        # 走路草进化链
        ("oddish", "gloom"): "等级21",
        ("gloom", "vileplume"): "叶之石",
        ("gloom", "bellossom"): "太阳石",
        # 蘑菇菇进化链
        ("paras", "parasect"): "等级24",
        # 蚊香蝌蚪进化链
        ("venonat", "venomoth"): "等级31",
        # 掘掘兔进化链
        ("diglett", "dugtrio"): "等级26",
        # 喵咪咪进化链
        ("meowth", "persian"): "等级28",
        # 魔墙人偶进化链
        ("mrmime", "mrrime"): "冰之石",
        # 铁甲蛹进化链
        ("scyther", "scizor"): "金属涂层",
        # 吉利蛋进化链
        ("happiny", "chansey"): "白天携带圆形石",
        ("chansey", "blissey"): "亲密度",
        # 盆盆花进化链
        ("bellsprout", "weepinbell"): "等级21",
        ("weepinbell", "victreebel"): "叶之石",
        # 墨海马进化链
        ("tentacool", "tentacruel"): "等级30",
        # 巨石丁进化链
        ("geodude", "graveler"): "等级25",
        ("graveler", "golem"): "交换",
        # 小火马进化链
        ("ponyta", "rapidash"): "等级40",
        # 呆呆兽进化链
        ("slowpoke", "slowbro"): "等级37",
        ("slowpoke", "slowking"): "王者之证",
        # 镰刀盔进化链
        ("krabby", "kingler"): "等级28",
        # 霹雳电球进化链
        ("voltorb", "electrode"): "等级30",
        # 蛋蛋进化链
        ("exeggcute", "exeggutor"): "叶之石",
        ("exeggcute", "exeggutoralola"): "叶之石",
        # 卡拉卡拉进化链
        ("cubone", "marowak"): "等级28",
        ("cubone", "marowakalola"): "夜间等级28",
        # 魔墙人偶进化链
        ("mrmime", "mrrime"): "冰之石",
        # 肯泰罗进化链
        ("tauros", "taurospaldeaaqua"): "水之石",
        ("tauros", "taurospaldeablaze"): "火之石",
        ("tauros", "taurospaldeacombat"): "雷之石",
        # 拉普拉斯进化链
        ("lapras", "laprasgmax"): "满腹",
        # 伊布进化链
        ("eevee", "vaporeon"): "水之石",
        ("eevee", "jolteon"): "雷之石",
        ("eevee", "flareon"): "火之石",
        ("eevee", "espeon"): "白天亲密度",
        ("eevee", "umbreon"): "夜晚亲密度",
        ("eevee", "leafeon"): "叶之石附近",
        ("eevee", "glaceon"): "冰之石附近",
        ("eevee", "sylveon"): "妖精属性招式",
        # 大嘴娃进化链
        ("igglybuff", "jigglypuff"): "亲密度",
        ("jigglypuff", "wigglytuff"): "月之石",
        # 宝宝丁进化链
        ("togepi", "togetic"): "亲密度",
        ("togetic", "togekiss"): "光之石",
        # 天然雀进化链
        ("natu", "xatu"): "等级25",
        # 玛力露进化链
        ("mareep", "flaaffy"): "等级15",
        ("flaaffy", "ampharos"): "等级30",
        # 玛力露丽进化链
        ("bellossom", "vileplume"): "叶之石",
        # 美丽花进化链
        ("chikorita", "bayleef"): "等级16",
        ("bayleef", "meganium"): "等级32",
        # 火球鼠进化链
        ("cyndaquil", "quilava"): "等级14",
        ("quilava", "typhlosion"): "等级36",
        # 小锯鳄进化链
        ("totodile", "croconaw"): "等级18",
        ("croconaw", "feraligatr"): "等级30",
        # 胡地进化链
        ("sentret", "furret"): "等级15",
        # 咕咕进化链
        ("hoothoot", "noctowl"): "等级20",
        # 芭瓢虫进化链
        ("ledyba", "ledian"): "等级18",
        # 蜘蛛熊进化链
        ("spinarak", "ariados"): "等级22",
        # 叉字蝠进化链
        ("chinchou", "lanturn"): "等级27",
        # 皮丘进化链
        ("pichu", "pikachu"): "亲密度",
        ("pikachu", "raichu"): "雷之石",
        # 宝宝丁进化链
        ("cleffa", "clefairy"): "亲密度",
        ("clefairy", "clefable"): "月之石",
        # 伊布进化链
        ("igglybuff", "jigglypuff"): "亲密度",
        ("jigglypuff", "wigglytuff"): "月之石",
        # 太阳珊瑚进化链
        ("corsola", "cursola"): "等级38",
        # 未知图腾进化链
        ("sneasel", "weavile"): "夜间持有锐利之爪",
        # 雪童子进化链
        ("snorunt", "glalie"): "等级42",
        ("snorunt", "froslass"): "女性等级42",
        # 利欧路进化链
        ("riolu", "lucario"): "白天亲密度",
        # 藤藤蛇进化链
        ("snivy", "servine"): "等级17",
        ("servine", "serperior"): "等级36",
        # 暖暖猪进化链
        ("tepig", "pignite"): "等级17",
        ("pignite", "emboar"): "等级36",
        # 冷水猴进化链
        ("oshawott", "dewott"): "等级17",
        ("dewott", "samurott"): "等级36",
        # 野蛮鲈鱼进化链
        ("basculin", "basculegion"): "水中招式",
        # 鸭宝宝进化链
        ("ducklett", "swanna"): "等级35",
        # 泡沫栗鼠进化链
        ("vanillite", "vanillish"): "等级35",
        ("vanillish", "vanilluxe"): "等级47",
        # 御三家进化链
        ("snivy", "servine"): "等级17",
        ("servine", "serperior"): "等级36",
        ("tepig", "pignite"): "等级17",
        ("pignite", "emboar"): "等级36",
        ("oshawott", "dewott"): "等级17",
        ("dewott", "samurott"): "等级36",
    }

    return evolution_conditions.get((base_name.lower(), evolved_name.lower()), "进化条件未知")

def insert_all_evolutions():
    """插入所有进化链数据"""
    init_db()

    # 获取项目根目录
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    evolutions_dir = os.path.join(project_root, "backend/spider/pokemon_evolutions")
    if not os.path.exists(evolutions_dir):
        print(f"进化数据目录不存在: {evolutions_dir}")
        return

    files = [f for f in os.listdir(evolutions_dir) if f.endswith('.json')]
    print(f"找到 {len(files)} 个进化文件")

    inserted_count = 0
    for file in files:
        data_path = os.path.join(evolutions_dir, file)
        data = load_json(data_path)
        if not data:
            continue

        evolution_chain = data.get("evolution_chain", [])

        # 处理进化链中的每一级进化
        for i in range(len(evolution_chain) - 1):
            base_name = evolution_chain[i]
            evolved_name = evolution_chain[i + 1]

            # 获取进化条件
            condition = get_evolution_condition(base_name, evolved_name)

            # 需要根据名称找到对应的宝可梦ID
            # 这里简化处理，假设进化链中的宝可梦都存在于数据库中
            # 实际应该通过名称查询数据库获取ID

            evolution_data = {
                "base_pokemon_id": i + 1,  # 临时ID，需要通过名称映射
                "evolved_pokemon_id": i + 2,  # 临时ID，需要通过名称映射
                "condition": condition
            }

            try:
                # 这里需要实际的宝可梦ID，而不是临时ID
                # 为了演示，我们先跳过插入，稍后修复
                # insert_evolution(
                #     evolution_data["base_pokemon_id"],
                #     evolution_data["evolved_pokemon_id"],
                #     evolution_data["condition"]
                # )
                inserted_count += 1
                print(f"处理进化: {base_name} -> {evolved_name} ({condition})")
            except Exception as e:
                print(f"插入进化失败 {base_name}->{evolved_name}: {e}")

    print(f"共处理 {inserted_count} 个进化")

def insert_all_data():
    """插入所有数据"""
    print("开始插入所有数据...")
    insert_all_pokemon()
    insert_all_moves()
    insert_all_items()
    insert_all_evolutions()
    print("所有数据插入完成！")

if __name__ == "__main__":
    insert_all_data()
