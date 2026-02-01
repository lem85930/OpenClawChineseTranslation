#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 汉化版 - 功能面板注入脚本
武汉晴辰天下网络科技有限公司 | https://qingchencloud.com/

在构建后将功能面板 JS/CSS 注入到 Dashboard 构建产物中。
"""

import os
import sys
import glob
import json
import re

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
PANEL_DIR = os.path.join(ROOT_DIR, 'translations', 'panel')

# 尝试多个可能的构建目录路径
POSSIBLE_BUILD_DIRS = [
    os.path.join(ROOT_DIR, 'openclaw', 'dist', 'control-ui'),  # 标准路径
    os.path.join(ROOT_DIR, 'dist', 'control-ui'),              # 备选路径
    'openclaw/dist/control-ui',                                  # 相对路径
    'dist/control-ui',                                           # 相对路径备选
]

def find_build_dir():
    """查找构建目录"""
    # 先尝试固定路径
    for path in POSSIBLE_BUILD_DIRS:
        if os.path.exists(path):
            return path
    
    # 动态查找 control-ui 目录
    import subprocess
    try:
        result = subprocess.run(
            ['find', '.', '-name', 'control-ui', '-type', 'd'],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            paths = result.stdout.strip().split('\n')
            for path in paths:
                if 'dist' in path and os.path.isdir(path):
                    return path
    except Exception as e:
        print(f"⚠️ find 命令失败: {e}")
    
    # 尝试查找任何包含 assets 子目录的 dist 目录
    for root, dirs, files in os.walk('.'):
        if 'assets' in dirs and 'dist' in root:
            return root
    
    return None

BUILD_DIR = find_build_dir()

def read_file(path):
    """读取文件内容"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    """写入文件内容"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def inject_panel():
    """注入功能面板到构建产物"""
    global BUILD_DIR
    
    print("🦞 OpenClaw 功能面板注入")
    print("=" * 50)
    
    # 查找构建目录
    BUILD_DIR = find_build_dir()
    if BUILD_DIR is None:
        print("❌ 找不到构建目录，尝试过以下路径:")
        for path in POSSIBLE_BUILD_DIRS:
            abs_path = os.path.abspath(path)
            print(f"   - {abs_path} (存在: {os.path.exists(path)})")
        print(f"\n当前工作目录: {os.getcwd()}")
        print(f"脚本目录: {SCRIPT_DIR}")
        print(f"ROOT_DIR: {ROOT_DIR}")
        
        # 列出当前目录结构帮助调试
        print("\n📁 当前目录结构:")
        for item in os.listdir('.'):
            print(f"   {item}/") if os.path.isdir(item) else print(f"   {item}")
        
        if os.path.exists('openclaw'):
            print("\n📁 openclaw/ 目录结构:")
            for item in os.listdir('openclaw'):
                full_path = os.path.join('openclaw', item)
                print(f"   {item}/") if os.path.isdir(full_path) else print(f"   {item}")
        
        sys.exit(1)
    
    print(f"📁 构建目录: {os.path.abspath(BUILD_DIR)}")
    
    assets_dir = os.path.join(BUILD_DIR, 'assets')
    if not os.path.exists(assets_dir):
        print(f"❌ assets 目录不存在: {assets_dir}")
        sys.exit(1)
    
    # 读取面板资源
    print("\n📦 读取面板资源...")
    
    panel_js_path = os.path.join(PANEL_DIR, 'feature-panel.js')
    panel_css_path = os.path.join(PANEL_DIR, 'feature-panel.css')
    panel_data_path = os.path.join(PANEL_DIR, 'panel-data.json')
    
    if not os.path.exists(panel_js_path):
        print(f"❌ 找不到 feature-panel.js: {panel_js_path}")
        sys.exit(1)
    
    panel_js = read_file(panel_js_path)
    panel_css = read_file(panel_css_path) if os.path.exists(panel_css_path) else ''
    
    # 读取并注入面板数据
    if os.path.exists(panel_data_path):
        import json
        with open(panel_data_path, 'r', encoding='utf-8') as f:
            panel_data_obj = json.load(f)
        # 将 JSON 转换为 JS 对象字面量，确保换行符被正确转义
        panel_data_js = json.dumps(panel_data_obj, ensure_ascii=False)
        # 使用 lambda 避免 re.sub 对反斜杠的解释
        panel_js = re.sub(
            r'/\*PANEL_DATA_PLACEHOLDER\*/\{[\s\S]*?\}/\*END_PANEL_DATA\*/',
            lambda m: panel_data_js,
            panel_js
        )
        print(f"  ✅ 已注入面板数据")
    
    print(f"  ✅ feature-panel.js ({len(panel_js)} bytes)")
    print(f"  ✅ feature-panel.css ({len(panel_css)} bytes)")
    
    # 注入 CSS 到主 CSS 文件
    print("\n🎨 注入 CSS...")
    css_files = glob.glob(os.path.join(assets_dir, '*.css'))
    css_injected = False
    
    for css_file in css_files:
        content = read_file(css_file)
        # 追加 CSS 到文件末尾
        new_content = content + '\n\n/* === OpenClaw 功能面板样式 === */\n' + panel_css
        write_file(css_file, new_content)
        print(f"  ✅ CSS 已注入: {os.path.basename(css_file)}")
        css_injected = True
    
    if not css_injected:
        print("  ⚠️ 未找到 CSS 文件，将 CSS 内嵌到 JS 中")
        # 将 CSS 转换为 JS 注入
        css_inject_code = f"""
(function() {{
  var style = document.createElement('style');
  style.textContent = {json.dumps(panel_css)};
  document.head.appendChild(style);
}})();
"""
        panel_js = css_inject_code + '\n' + panel_js
    
    # 注入 JS 到主 JS 文件
    print("\n📜 注入 JS...")
    js_files = glob.glob(os.path.join(assets_dir, '*.js'))
    js_injected = False
    
    for js_file in js_files:
        filename = os.path.basename(js_file)
        # 寻找主 bundle（通常是 index-*.js）
        if 'index-' in filename or filename == 'index.js':
            content = read_file(js_file)
            # 追加 JS 到文件末尾
            new_content = content + '\n\n/* === OpenClaw 功能面板 === */\n' + panel_js
            write_file(js_file, new_content)
            print(f"  ✅ JS 已注入: {filename}")
            js_injected = True
            break
    
    if not js_injected:
        # 如果没找到 index-*.js，尝试注入到任意 JS 文件
        for js_file in js_files:
            content = read_file(js_file)
            new_content = content + '\n\n/* === OpenClaw 功能面板 === */\n' + panel_js
            write_file(js_file, new_content)
            print(f"  ✅ JS 已注入: {os.path.basename(js_file)}")
            js_injected = True
            break
    
    if not js_injected:
        print("  ❌ 未找到可注入的 JS 文件")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ 功能面板注入完成！")
    print("=" * 50)

if __name__ == '__main__':
    inject_panel()
