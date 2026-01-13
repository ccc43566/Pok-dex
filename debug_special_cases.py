import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def debug_special_cases():
    """调试特殊情况的宝可梦"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    async def analyze_page(pokemon_name):
        print(f"\n=== 分析 {pokemon_name} ===")

        # 处理特殊字符和形态
        base_name = pokemon_name.split('-')[0]
        # URL编码特殊字符
        base_name = base_name.replace("'", "%27")  # 单引号编码
        base_name = base_name.replace("♀", "_Female")  # 雌性符号
        base_name = base_name.replace("♂", "_Male")  # 雄性符号

        url = f"https://wiki.52poke.com/wiki/{base_name}"
        print(f"尝试URL: {url}")

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    print(f"响应状态: {response.status}")
                    if response.status != 200:
                        return

                    content = await response.read()
                    soup = BeautifulSoup(content, 'html.parser')

            content_div = soup.find('div', id='mw-content-text')
            if not content_div:
                print("未找到内容容器")
                return

            all_p_tags = content_div.find_all('p')
            print(f"找到 {len(all_p_tags)} 个 <p> 标签")

            for i, p_tag in enumerate(all_p_tags[:5]):
                p_text = p_tag.get_text(strip=True)[:150]
                print(f"  p[{i}]: '{p_text}'")

                # 检查是否通过过滤条件
                conditions = []
                conditions.append(("长度>20", len(p_text) > 20))
                conditions.append(("非'From '开头", not p_text.startswith('From ')))
                conditions.append(("非'这是一张'开头", not p_text.startswith('这是一张')))
                conditions.append(("不含'Category:'", 'Category:' not in p_text))
                conditions.append(("非括号内容", not (p_text.startswith('(') and p_text.endswith(')'))))
                conditions.append(("非导航内容", not any(skip_word in p_text.lower() for skip_word in ['see also', 'external links', 'references', 'navigation'])))

                passed = all(cond[1] for cond in conditions)
                print(f"    通过过滤: {passed}")
                for cond_name, cond_result in conditions:
                    if not cond_result:
                        print(f"    ❌ {cond_name}")

        except Exception as e:
            print(f"异常: {e}")

    # 测试有问题的宝可梦
    test_cases = [
        "Nidoran-F",
        "Nidoran-M",
        "Farfetch'd",
        "Farfetch'd-Galar"
    ]

    for pokemon in test_cases:
        await analyze_page(pokemon)
        await asyncio.sleep(1)  # 避免请求过快

if __name__ == "__main__":
    asyncio.run(debug_special_cases())
