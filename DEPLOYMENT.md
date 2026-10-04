# 后端部署清单

## 部署前本地检查

```bash
python -m unittest discover -v
docker build -t calculator-backend .
docker run --rm -p 5000:5000 calculator-backend
```

另开终端验证：

```bash
curl http://127.0.0.1:5000/api/health
curl -X POST http://127.0.0.1:5000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression":"(1+2)*3"}'
```

## Render 操作

1. 注册或登录 Render，并准备一个 GitHub 仓库。
2. 把本目录作为独立仓库根目录推送到 GitHub。
3. 创建 Web Service，选择该仓库，运行方式选择 Docker。
4. Dockerfile 使用根目录的 `Dockerfile`，健康检查填写 `/api/health`。
5. 部署完成后打开 `https://服务名.onrender.com/api/health`。
6. 将这个 HTTPS 地址加入 Android 的 `BACKEND_URLS` 第一项并重新构建 APK。

## 需要项目作者完成的事情

- 登录部署平台并确认免费实例或服务器方案。
- 创建两个独立 GitHub 仓库，分别上传 Android 和 Flask 目录。
- 将后端公网 HTTPS 地址填入 Android 代码。
- 在模拟器或真机上重新安装最终 APK，并保存演示截图。

## 数据持久化

后端支持 `CALCULATOR_DB_FILE` 环境变量。平台提供持久化磁盘时，将它设置为磁盘目录中的 `calculator.db`；没有持久化磁盘时，服务重建可能清空历史记录，但计算接口仍然可用。
