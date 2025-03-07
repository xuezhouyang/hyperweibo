#!/bin/bash

# 版本号
VERSION="1.0.0"
RELEASE_DIR="release/v${VERSION}"

# 清理并创建发布目录
rm -rf "${RELEASE_DIR}"
mkdir -p "${RELEASE_DIR}"

# 创建临时目录
TMP_DIR=$(mktemp -d)
mkdir -p "${TMP_DIR}/hyperweibo"

# 复制核心文件
cp -r hyperweibo "${TMP_DIR}/"
cp hyperweibo.py "${TMP_DIR}/hyperweibo/"
cp weibo "${TMP_DIR}/"
cp LICENSE "${TMP_DIR}/"
cp README.md "${TMP_DIR}/"
cp agree.py "${TMP_DIR}/"

# 创建虚拟环境并安装依赖
python3 -m venv "${TMP_DIR}/venv"
source "${TMP_DIR}/venv/bin/activate"
pip install -r hyperweibo/requirements.txt
deactivate

# 修改weibo脚本以使用打包的虚拟环境
sed -i '' "s|python3|./venv/bin/python3|g" "${TMP_DIR}/weibo"

# 打包文件
cd "${TMP_DIR}"
tar -czf "../hyperweibo-${VERSION}.tar.gz" *
cd -

# 移动到发布目录
mv "${TMP_DIR}/../hyperweibo-${VERSION}.tar.gz" "${RELEASE_DIR}/"

# 清理临时目录
rm -rf "${TMP_DIR}"

# 创建SHA256校验和
cd "${RELEASE_DIR}"
shasum -a 256 "hyperweibo-${VERSION}.tar.gz" > "hyperweibo-${VERSION}.tar.gz.sha256"
cd -

# 创建安装说明
cat > "${RELEASE_DIR}/INSTALL.md" << 'EOF'
# HyperWeibo 安装说明

## 快速开始

1. 下载并解压发布包：
   ```bash
   tar -xzf hyperweibo-1.0.0.tar.gz
   ```

2. 进入解压后的目录：
   ```bash
   cd hyperweibo-1.0.0
   ```

3. 运行程序：
   ```bash
   ./weibo help    # 显示帮助信息
   ./weibo agree   # 查看并同意许可协议
   ./weibo home    # 查看关注的微博内容
   ```

## 系统要求

- macOS 10.15+ / Linux
- Python 3.8+
- 支持的浏览器：Chrome、Firefox、Edge 或 Safari

## 验证完整性

建议在安装前验证发布包的完整性：

```bash
shasum -a 256 -c hyperweibo-1.0.0.tar.gz.sha256
```

## 常见问题

如果遇到权限问题，请确保weibo脚本具有执行权限：

```bash
chmod +x weibo
```

更多信息请参考README.md文件。
EOF

echo "发布包已生成在 ${RELEASE_DIR} 目录下"
echo "文件列表："
ls -l "${RELEASE_DIR}" 