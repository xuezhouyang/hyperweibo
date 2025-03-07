# HyperWeibo 可执行文件安装说明

## 快速开始

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

## 系统要求

- macOS 10.15+ / Linux
- 支持的浏览器：Chrome、Firefox、Edge 或 Safari

## 常见问题

如果遇到权限问题，请确保可执行文件具有执行权限：

```bash
chmod +x weibo-1.0.0
```

如果遇到导入模块错误，请尝试使用源码版本安装。
