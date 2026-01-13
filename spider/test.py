import requests
from bs4 import BeautifulSoup

def get_pokemon_overview(pokemon_name):
    # 构造 URL（中文名）
    url = f"https://wiki.52poke.com/wiki/{pokemon_name}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 找到正文容器
        content_div = soup.find('div', id='mw-content-text')
        if not content_div:
            return None
        
                # 获取所有 <p> 标签
        all_p_tags = content_div.find_all('p')
        if len(all_p_tags) < 3:
            return "描述信息不足"
        # 提取第1个第2个和第3个 <p> 标签的文本
        first_p = all_p_tags[0].get_text(strip=True)
        second_p = all_p_tags[1].get_text(strip=True)
        third_p = all_p_tags[2].get_text(strip=True)
        overview = f"{first_p}\n{second_p}\n{third_p}"
        return overview


    except Exception as e:
        print(f"错误: {e}")
        return None

# 测试：爬取妙蛙种子的概述
overview = get_pokemon_overview("妙蛙种子")
print(overview)