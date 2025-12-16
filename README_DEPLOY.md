# 快速部署指南

## 📚 部署文档索引

根据你使用的云服务提供商，选择对应的部署文档：

- **腾讯云函数计算（SCF）**: 查看 [DEPLOY_TENCENT.md](./DEPLOY_TENCENT.md)
- **阿里云函数计算（FC）**: 查看 [DEPLOY.md](./DEPLOY.md)

## 🎯 快速选择

### 如果你使用腾讯云
1. 使用 `scf_handler.py` 作为函数入口
2. 参考 `DEPLOY_TENCENT.md` 完成部署
3. 推荐使用 Serverless Framework 或控制台部署

### 如果你使用阿里云
1. 使用 `multi_handler.py` 作为函数入口
2. 参考 `DEPLOY.md` 完成部署

## 🏠 本地测试（通用）

无论使用哪个云服务，本地测试步骤都相同：

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入API密钥

# 2. 启动本地代理
./start_local.sh

# 3. 修改前端配置（api_new.js）
# 将 development 代理地址改为: http://localhost:5000/proxy

# 4. 启动前端
python3 -m http.server 8000
# 访问 http://localhost:8000
```

## 📝 文件说明

- `local_proxy.py` - 本地测试用的Flask代理服务器
- `scf_handler.py` - 腾讯云函数计算入口文件
- `multi_handler.py` - 阿里云函数计算入口文件
- `start_local.sh` - 本地测试启动脚本
- `.env.example` - 环境变量配置模板

## ⚠️ 重要提示

1. **API密钥安全**: 永远不要将API密钥提交到代码仓库
2. **CORS配置**: 生产环境务必配置明确的CORS白名单
3. **函数超时**: 建议设置至少300秒的超时时间
4. **内存配置**: 建议至少512MB内存

