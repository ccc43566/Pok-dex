#!/usr/bin/env python3
import os

# 检查后端图片目录路径
backend_dir = "../backend/spider/pokemon_images"
print(f"后端图片目录: {backend_dir}")
print(f"绝对路径: {os.path.abspath(backend_dir)}")
print(f"目录存在: {os.path.exists(backend_dir)}")

if os.path.exists(backend_dir):
    files = os.listdir(backend_dir)
    print(f"文件数量: {len(files)}")

    # 检查前几个文件
    gif_files = [f for f in files if f.endswith('.gif')]
    png_files = [f for f in files if f.endswith('.png')]
    print(f"GIF文件: {len(gif_files)}")
    print(f"PNG文件: {len(png_files)}")

    # 检查几个具体的文件
    test_files = ['1_bulbasaur.gif', '25_pikachu.gif', '150_mewtwo.gif']
    for filename in test_files:
        exists = os.path.exists(os.path.join(backend_dir, filename))
        print(f"{filename}: {'存在' if exists else '不存在'}")
else:
    print("图片目录不存在！")

# 检查前端相对路径
print("\n前端相对路径检查:")
frontend_to_backend = "../backend/spider/pokemon_images"
print(f"前端到后端的相对路径: {frontend_to_backend}")
print(f"从前端目录解析: {os.path.abspath(os.path.join('frontend', frontend_to_backend))}")

# 检查main.py中的路径
print("\nmain.py中的路径配置:")
main_py_path = "backend/spider/pokemon_images"
print(f"main.py中配置的路径: {main_py_path}")
print(f"从根目录解析: {os.path.abspath(main_py_path)}")
