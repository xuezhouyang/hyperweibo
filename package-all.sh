#!/bin/bash

# 版本号
VERSION="1.0.0"
RELEASE_DIR="release/v${VERSION}"
BINARY_RELEASE_DIR="release/binary/v${VERSION}"
FINAL_RELEASE_DIR="release/final/v${VERSION}"

echo "开始创建最终发布包 HyperWeibo ${VERSION}..."

# 清理并创建最终发布目录
rm -rf "${FINAL_RELEASE_DIR}"
mkdir -p "${FINAL_RELEASE_DIR}"

# 检查源码包是否存在
if [ ! -d "${RELEASE_DIR}" ]; then
    echo "错误：源码包目录 ${RELEASE_DIR} 不存在，请先运行 package.sh"
    exit 1
fi

# 检查可执行文件包是否存在
if [ ! -d "${BINARY_RELEASE_DIR}" ]; then
    echo "错误：可执行文件包目录 ${BINARY_RELEASE_DIR} 不存在，请先运行 package-binary.sh"
    exit 1
fi

# 复制源码包
echo "复制源码包..."
cp -r "${RELEASE_DIR}"/* "${FINAL_RELEASE_DIR}/"

# 复制可执行文件包
echo "复制可执行文件包..."
cp -r "${BINARY_RELEASE_DIR}"/* "${FINAL_RELEASE_DIR}/"

# 创建最终的 README.md
echo "创建 README.md..."
cat > "${FINAL_RELEASE_DIR}/README.md" << EOL
# HyperWeibo ${VERSION}

HyperWeibo 是一个命令行微博客户端，支持查看首页微博和特别关注。

## 安装方式

### 方式一：使用可执行文件（推荐）

详见 [INSTALL.md](INSTALL.md) 文件。

### 方式二：使用源码

详见 [INSTALL-SOURCE.md](INSTALL-SOURCE.md) 文件。

## 使用方法

\`\`\`bash
# 显示帮助信息
weibo help

# 查看首页微博
weibo home

# 查看特别关注
weibo special

# 查看并同意许可协议
weibo agree
\`\`\`

## 系统要求

- macOS 10.15+ / Linux
- 支持的浏览器：Chrome、Firefox、Edge 或 Safari

## 许可证

本软件使用 MIT 许可证（带扩展免责声明）。详见 LICENSE 文件。
EOL

# 创建最终的压缩包
echo "创建最终压缩包..."
cd "${FINAL_RELEASE_DIR}/.."
tar -czf "hyperweibo-${VERSION}-full.tar.gz" "v${VERSION}"
cd -

# 创建 SHA256 校验和
echo "创建 SHA256 校验和..."
cd "${FINAL_RELEASE_DIR}/.."
shasum -a 256 "hyperweibo-${VERSION}-full.tar.gz" > "hyperweibo-${VERSION}-full.tar.gz.sha256"
cd -

echo "最终发布包已生成在 ${FINAL_RELEASE_DIR} 目录下"
echo "文件列表："
ls -l "${FINAL_RELEASE_DIR}"
echo ""
echo "压缩包："
ls -l "release/final/hyperweibo-${VERSION}-full.tar.gz" 