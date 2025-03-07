#!/bin/bash

# 版本号
VERSION="1.0.0"
RELEASE_DIR="release/binary/v${VERSION}"
BINARY_NAME="weibo-${VERSION}"
TMP_DIR=$(mktemp -d)
WORKSPACE_DIR=$(pwd)

echo "开始打包 HyperWeibo ${VERSION} 可执行文件..."
echo "临时目录: ${TMP_DIR}"
echo "发布目录: ${RELEASE_DIR}"

# 清理并创建发布目录
rm -rf "${RELEASE_DIR}"
mkdir -p "${RELEASE_DIR}"

# 复制核心文件到临时目录
echo "复制源文件..."
cp hyperweibo.py "${TMP_DIR}/"
cp -r hyperweibo "${TMP_DIR}/"
mkdir -p "${TMP_DIR}/hyperweibo/utils"
touch "${TMP_DIR}/hyperweibo/__init__.py"
touch "${TMP_DIR}/hyperweibo/utils/__init__.py"

# 创建虚拟环境并安装依赖
echo "创建虚拟环境..."
python3 -m venv "${TMP_DIR}/venv"
source "${TMP_DIR}/venv/bin/activate"

# 使用阿里云镜像安装依赖
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 安装项目依赖
echo "安装项目依赖..."
pip install requests>=2.28.1 \
    browser-cookie3>=0.19.1 \
    pycookiecheat>=0.8.0 \
    beautifulsoup4>=4.11.1 \
    rich>=13.3.5 \
    lxml>=4.9.2

# 安装 PyInstaller
echo "安装 PyInstaller..."
pip install pyinstaller

# 设置 PYTHONPATH
export PYTHONPATH="${TMP_DIR}:${PYTHONPATH}"

# 创建一个简单的 Style 类
echo "创建 Style 类..."
cat > "${TMP_DIR}/hyperweibo/utils/style.py" << EOL
class Style:
    def __init__(self, simple=False, lang='auto', style='weibo'):
        self.simple = simple
        self.lang = lang
        self.style = style
EOL

# 修改 hyperweibo.py 文件以适应打包环境
echo "修改 hyperweibo.py 文件..."
cat > "${TMP_DIR}/hyperweibo.py" << EOL
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse

# 添加当前目录到模块搜索路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if hasattr(sys, '_MEIPASS'):
    # PyInstaller 创建临时文件夹 _MEIPASS
    bundle_dir = sys._MEIPASS
    sys.path.insert(0, bundle_dir)
else:
    sys.path.insert(0, current_dir)

try:
    from hyperweibo.api.weibo_api import WeiboAPI
    from hyperweibo.utils.style import Style
except ImportError as e:
    print(f"导入错误: {e}")
    print("尝试其他导入路径...")
    
    try:
        sys.path.insert(0, os.path.join(current_dir, 'hyperweibo'))
        from api.weibo_api import WeiboAPI
        from utils.style import Style
    except ImportError as e:
        print(f"导入错误: {e}")
        print("尝试直接导入...")
        
        try:
            from hyperweibo.api.weibo_api import WeiboAPI
            from hyperweibo.utils.style import Style
        except ImportError as e:
            print(f"导入错误: {e}")
            print("无法导入必要的模块，程序将退出。")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='HyperWeibo - 一个更好的微博命令行工具')
    parser.add_argument('command', choices=['home', 'special', 'agree', 'help'],
                      help='要执行的命令: home (首页), special (特别关注), agree (同意协议), help (显示帮助)')
    parser.add_argument('-b', '--browser', choices=['chrome', 'firefox', 'edge', 'safari'],
                      default='chrome', help='从哪个浏览器获取 cookie (默认: chrome)')
    parser.add_argument('-s', '--simple', action='store_true',
                      help='使用简单输出模式')
    parser.add_argument('-r', '--refresh', type=int, default=300,
                      help='自动刷新间隔（秒），0 表示不自动刷新 (默认: 300)')
    parser.add_argument('-m', '--mock', action='store_true',
                      help='使用模拟数据进行测试')
    parser.add_argument('-c', '--cookie', type=str,
                      help='直接使用提供的 cookie 字符串')
    parser.add_argument('-p', '--page', type=int, default=1,
                      help='要显示的页码 (默认: 1)')
    parser.add_argument('-g', '--group', type=str,
                      help='要显示的分组名称')
    parser.add_argument('-l', '--lang', choices=['en', 'zh', 'auto'],
                      default='auto', help='显示语言 (默认: auto)')
    parser.add_argument('-y', '--style', choices=['weibo', 'maven'],
                      default='weibo', help='显示样式 (默认: weibo)')

    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help', 'help']:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    # 创建 API 实例
    api = WeiboAPI(
        browser=args.browser,
        cookie=args.cookie,
        mock=args.mock
    )

    # 设置显示样式
    style = Style(
        simple=args.simple,
        lang=args.lang,
        style=args.style
    )

    # 执行命令
    if args.command == 'home':
        api.get_home_timeline(
            page=args.page,
            group=args.group,
            refresh=args.refresh,
            style=style
        )
    elif args.command == 'special':
        api.get_special_focus(
            page=args.page,
            refresh=args.refresh,
            style=style
        )
    elif args.command == 'agree':
        api.show_license_agreement()

if __name__ == '__main__':
    main()
EOL

# 运行 PyInstaller
echo "运行 PyInstaller..."
cd "${TMP_DIR}"
pyinstaller --onefile hyperweibo.py --name "${BINARY_NAME}" --add-data "hyperweibo:hyperweibo"

# 检查是否成功生成可执行文件
if [ ! -f "dist/${BINARY_NAME}" ]; then
    echo "错误：PyInstaller 打包失败，未生成可执行文件"
    exit 1
fi

# 复制生成的文件到发布目录
echo "复制文件到发布目录..."
cd "${WORKSPACE_DIR}"
cp "${TMP_DIR}/dist/${BINARY_NAME}" "${RELEASE_DIR}/"
chmod +x "${RELEASE_DIR}/${BINARY_NAME}"

# 创建安装说明文件
echo "创建安装说明文件..."
cat > "${RELEASE_DIR}/INSTALL.md" << EOL
# HyperWeibo 可执行文件安装说明

## 快速开始

1. 将可执行文件复制到系统 PATH 目录下（如 /usr/local/bin）：
   \`\`\`bash
   sudo cp ${BINARY_NAME} /usr/local/bin/weibo
   \`\`\`

2. 添加执行权限：
   \`\`\`bash
   sudo chmod +x /usr/local/bin/weibo
   \`\`\`

3. 现在可以直接使用 \`weibo\` 命令了：
   \`\`\`bash
   weibo help    # 显示帮助信息
   weibo agree   # 查看并同意许可协议
   weibo home    # 查看关注的微博内容
   \`\`\`

## 系统要求

- macOS 10.15+ / Linux
- 支持的浏览器：Chrome、Firefox、Edge 或 Safari

## 常见问题

如果遇到权限问题，请确保可执行文件具有执行权限：

\`\`\`bash
chmod +x ${BINARY_NAME}
\`\`\`

如果遇到导入模块错误，请尝试使用源码版本安装。
EOL

# 创建 SHA256 校验和
echo "创建 SHA256 校验和..."
cd "${RELEASE_DIR}"
shasum -a 256 "${BINARY_NAME}" > "${BINARY_NAME}.sha256"

echo "发布包已生成在 ${RELEASE_DIR} 目录下"
echo "文件列表："
ls -l

# 清理临时目录
rm -rf "${TMP_DIR}" 