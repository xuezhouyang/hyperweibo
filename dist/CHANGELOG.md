# HyperWeibo 发布说明

## 版本 1.0.0

发布日期：2024-03-07

### 发布内容

本次发布包含以下内容：

1. **源码包**：
   - 位置：`release/v1.0.0/hyperweibo-1.0.0.tar.gz`
   - 适合开发者或希望从源码安装的用户
   - 包含完整的源代码和依赖列表

2. **可执行文件包**：
   - 位置：`release/binary/v1.0.0/weibo-1.0.0`
   - 适合普通用户，无需安装依赖即可运行
   - 支持 macOS 平台

3. **完整发布包**：
   - 位置：`release/final/hyperweibo-1.0.0-full.tar.gz`
   - 包含上述两种包的组合
   - 适合所有类型的用户

### 安装方式

#### 方式一：使用可执行文件（推荐）

1. 将可执行文件复制到系统 PATH 目录下（如 /usr/local/bin）：
   ```bash
   sudo cp weibo-1.0.0 /usr/local/bin/weibo
   ```

2. 添加执行权限：
   ```bash
   sudo chmod +x /usr/local/bin/weibo
   ```

3. 现在可以直接使用 `weibo` 命令了：
   ```bash
   weibo help    # 显示帮助信息
   weibo agree   # 查看并同意许可协议
   weibo home    # 查看关注的微博内容
   ```

#### 方式二：使用源码

1. 解压源码包：
   ```bash
   tar -xzf hyperweibo-1.0.0.tar.gz
   ```

2. 进入解压后的目录：
   ```bash
   cd hyperweibo-1.0.0
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 运行程序：
   ```bash
   ./weibo help    # 显示帮助信息
   ```

### 系统要求

- macOS 10.15+ / Linux
- 支持的浏览器：Chrome、Firefox、Edge 或 Safari

### 验证完整性

建议在安装前验证发布包的完整性：

```bash
shasum -a 256 -c hyperweibo-1.0.0-full.tar.gz.sha256
```

### 功能特性

- 查看首页微博内容
- 查看特别关注内容
- 支持自动刷新
- 支持多种浏览器获取 cookie
- 支持多种显示样式

### 许可证

本软件使用 MIT 许可证（带扩展免责声明）。详见 LICENSE 文件。 