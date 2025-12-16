# 部署指南

本指南将帮助你完成项目的本地测试和服务器部署。

## 📋 前置要求

### 1. API密钥准备
你需要准备以下API密钥（从 https://302.ai 获取）：
- **Unifuns API Key**: 用于网页内容提取
- **Gemini API Key**: 用于AI内容分析
- **Nano Banana API Key**: 用于图片生成

### 2. 环境要求
- Python 3.7+
- Node.js（可选，仅用于前端开发）
- 阿里云账号（用于服务器部署）

---

## 🏠 本地测试

### 步骤1: 配置环境变量

复制环境变量模板文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的API密钥：
```env
UNIFUNS_API_KEY=sk-your-unifuns-api-key
GEMINI_API_KEY=sk-your-gemini-api-key
NANO_BANANA_API_KEY=sk-your-nano-banana-api-key
```

### 步骤2: 启动本地代理服务器

**方式一：使用启动脚本（推荐）**
```bash
chmod +x start_local.sh
./start_local.sh
```

**方式二：手动启动**
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 设置环境变量（或使用 .env 文件）
export UNIFUNS_API_KEY=sk-your-key
export GEMINI_API_KEY=sk-your-key
export NANO_BANANA_API_KEY=sk-your-key

# 启动服务器
python3 local_proxy.py
```

### 步骤3: 修改前端配置

编辑 `api_new.js` 文件，将开发环境的代理地址改为本地地址：

找到 `ENV_CONFIG` 配置部分，修改 `proxyEndpoints`：
```javascript
'proxyEndpoints': {
    'development': 'http://localhost:5000/proxy',  // 改为本地地址
    'production': 'https://your-production-endpoint.fcapp.run'
}
```

### 步骤4: 启动前端

使用任意HTTP服务器打开 `index.html`：

**方式一：使用Python内置服务器**
```bash
python3 -m http.server 8000
```
然后访问: http://localhost:8000

**方式二：使用Node.js http-server**
```bash
npx http-server -p 8000
```

**方式三：直接在浏览器打开**
- 注意：某些浏览器可能因为CORS限制无法正常工作，建议使用HTTP服务器

### 步骤5: 测试

1. 打开浏览器访问前端页面
2. 点击"输入链接"按钮
3. 输入一个新闻链接或选择示例文章
4. 点击"生成简报"
5. 观察控制台日志，确认请求是否正常发送到本地代理

---

## 🚀 服务器部署（阿里云函数计算）

### 步骤1: 准备部署包

创建部署目录：
```bash
mkdir deploy
cd deploy
```

复制必要文件：
```bash
cp ../multi_handler.py .
cp ../requirements.txt .
```

### 步骤2: 安装依赖到本地目录

```bash
pip install -r requirements.txt -t .
```

### 步骤3: 打包部署文件

```bash
# 创建zip包（排除不必要的文件）
zip -r brief-function.zip . -x "*.pyc" "__pycache__/*" "*.dist-info/*"
```

### 步骤4: 创建阿里云函数

1. 登录阿里云控制台
2. 进入"函数计算"服务
3. 创建函数：
   - **函数名称**: `brief-proxy`
   - **运行环境**: Python 3.9
   - **函数入口**: `multi_handler.handler`
   - **请求处理程序类型**: 处理HTTP请求
   - **代码包**: 上传 `brief-function.zip`

### 步骤5: 配置环境变量

在函数配置中添加以下环境变量：

```
UNIFUNS_API_KEY=sk-your-unifuns-api-key
GEMINI_API_KEY=sk-your-gemini-api-key
NANO_BANANA_API_KEY=sk-your-nano-banana-api-key
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**注意**: 
- `ALLOWED_ORIGINS` 设置允许访问的域名，多个用逗号分隔
- 生产环境不要使用 `*`，应该明确指定域名

### 步骤6: 配置HTTP触发器

1. 在函数详情页，点击"触发器"
2. 创建HTTP触发器：
   - **触发路径**: `/` 或 `/proxy`
   - **请求方法**: GET, POST, OPTIONS
   - **认证方式**: 匿名访问（或根据需要配置）

### 步骤7: 获取函数访问地址

部署完成后，你会得到一个类似这样的访问地址：
```
https://brief-proxy-xxxxx.cn-hongkong.fcapp.run
```

### 步骤8: 更新前端配置

编辑 `api_new.js`，更新生产环境代理地址：

```javascript
'proxyEndpoints': {
    'development': 'http://localhost:5000/proxy',
    'production': 'https://brief-proxy-xxxxx.cn-hongkong.fcapp.run'  // 你的函数地址
}
```

### 步骤9: 部署前端

将前端文件部署到任意静态网站托管服务：
- GitHub Pages
- Vercel
- Netlify
- 阿里云OSS + CDN
- 你自己的服务器

---

## 🔧 常见问题

### Q1: 本地测试时出现CORS错误
**A**: 确保 `local_proxy.py` 中已启用 `CORS(app)`，并且前端访问的是 `http://localhost:5000`

### Q2: 函数计算返回500错误
**A**: 
1. 检查函数日志，查看具体错误信息
2. 确认环境变量已正确配置
3. 确认API密钥有效

### Q3: 前端无法连接到代理
**A**:
1. 检查代理地址是否正确
2. 检查网络连接
3. 查看浏览器控制台的错误信息

### Q4: API调用失败
**A**:
1. 确认API密钥有效且有足够余额
2. 检查API端点是否正确
3. 查看代理服务器的日志输出

---

## 📝 维护建议

1. **定期更新依赖**: 定期检查并更新 `requirements.txt` 中的依赖包
2. **监控日志**: 定期查看函数计算和API调用的日志
3. **成本控制**: 监控API调用量，合理设置函数计算的并发限制
4. **安全加固**: 
   - 生产环境使用明确的CORS白名单
   - 考虑添加API调用频率限制
   - 定期轮换API密钥

---

## 🎯 下一步

部署完成后，你可以：
1. 自定义前端样式和功能
2. 优化AI提示词以获得更好的效果
3. 添加更多功能，如简报历史记录、分享功能等

祝你使用愉快！ 🎉

