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
