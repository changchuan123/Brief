# Zeabur 部署指南

本指南将帮助你通过 Zeabur 部署财经简报生成器，实现外网访问。

## 📋 前置要求

1. GitHub 账号
2. Zeabur 账号（免费注册：https://zeabur.com）
3. 302.ai API 密钥

---

## 🚀 部署步骤

### 步骤1: 准备 GitHub 仓库

#### 1.1 在 GitHub 创建新仓库

1. 登录 GitHub
2. 点击右上角 "+" → "New repository"
3. 填写仓库信息：
   - **Repository name**: `brief`（或你喜欢的名字）
   - **Description**: 财经时事资讯简报生成器
   - **Visibility**: Public 或 Private（都可以）
4. 点击 "Create repository"

#### 1.2 上传代码到 GitHub

在你的本地项目目录执行：

```bash
cd /Users/weixiaogang/AI/brief

# 初始化 git（如果还没有）
git init

# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/brief.git

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: 财经简报生成器"

# 推送到 GitHub
git branch -M main
git push -u origin main
```

---

### 步骤2: 在 Zeabur 部署

#### 2.1 连接 GitHub

1. 登录 [Zeabur](https://zeabur.com)
2. 点击 "New Project"
3. 选择 "Import from GitHub"
4. 授权 Zeabur 访问你的 GitHub 仓库
5. 选择你刚创建的 `brief` 仓库

#### 2.2 配置环境变量

在 Zeabur 项目设置中，添加以下环境变量：

```
UNIFUNS_API_KEY=sk-你的API密钥
GEMINI_API_KEY=sk-你的API密钥
NANO_BANANA_API_KEY=sk-你的API密钥
ALLOWED_ORIGINS=*
```

**重要**：
- 三个 API Key 可以填同一个（302.ai 的同一个密钥）
- `ALLOWED_ORIGINS` 设置为 `*` 表示允许所有域名访问（开发阶段）
- 生产环境建议设置为你的前端域名，如：`https://yourdomain.com`

#### 2.3 部署设置

Zeabur 会自动检测到 `Dockerfile`，使用以下配置：

- **Build Method**: Dockerfile
- **Port**: 自动检测（5000）
- **Start Command**: `python3 local_proxy.py`

#### 2.4 开始部署

点击 "Deploy" 按钮，Zeabur 会：
1. 从 GitHub 拉取代码
2. 构建 Docker 镜像
3. 部署服务
4. 分配一个公网域名

---

### 步骤3: 获取部署地址

部署完成后，Zeabur 会提供一个公网地址，类似：
```
https://brief-xxxxx.zeabur.app
```

**这就是你的后端 API 地址！**

---

### 步骤4: 更新前端配置

编辑 `api_new.js`，将代理地址改为 Zeabur 地址：

```javascript
'proxyEndpoints': {
    'development': 'https://brief-xxxxx.zeabur.app/proxy',
    'production': 'https://brief-xxxxx.zeabur.app/proxy'
}
```

然后重新提交到 GitHub：

```bash
git add api_new.js
git commit -m "Update proxy endpoint to Zeabur"
git push
```

---

### 步骤5: 部署前端（可选）

#### 方式一：使用 Zeabur 部署前端

1. 在 Zeabur 创建新服务
2. 选择同一个 GitHub 仓库
3. 设置 **Build Method** 为 "Static Site"
4. 设置 **Root Directory** 为 `/`（根目录）
5. Zeabur 会自动部署前端，提供另一个域名

#### 方式二：使用其他静态托管

- **Vercel**: 连接 GitHub 仓库，自动部署
- **Netlify**: 连接 GitHub 仓库，自动部署
- **GitHub Pages**: 在仓库设置中启用 Pages

---

## 🔧 常见问题

### Q1: 部署失败怎么办？

**A**: 
1. 检查 Zeabur 的构建日志
2. 确认环境变量已正确配置
3. 确认 `requirements.txt` 中的依赖正确

### Q2: API 调用失败？

**A**:
1. 检查环境变量中的 API 密钥是否正确
2. 确认 API 密钥有效且有余额
3. 查看 Zeabur 的运行时日志

### Q3: CORS 错误？

**A**:
1. 确认 `ALLOWED_ORIGINS` 环境变量包含你的前端域名
2. 或者设置为 `*`（开发阶段）

### Q4: 如何查看日志？

**A**: 
在 Zeabur 项目页面，点击服务 → "Logs" 标签页

### Q5: 如何更新代码？

**A**:
1. 在本地修改代码
2. 提交到 GitHub：`git push`
3. Zeabur 会自动检测并重新部署

---

## 📝 环境变量说明

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `UNIFUNS_API_KEY` | 302.ai Unifuns API 密钥 | `sk-xxxxx` |
| `GEMINI_API_KEY` | 302.ai Gemini API 密钥 | `sk-xxxxx` |
| `NANO_BANANA_API_KEY` | 302.ai Nano Banana API 密钥 | `sk-xxxxx` |
| `ALLOWED_ORIGINS` | CORS 白名单（多个用逗号分隔） | `*` 或 `https://yourdomain.com` |
| `PORT` | 服务端口（Zeabur 自动设置，无需手动配置） | `5000` |

---

## 🎯 完成后的访问方式

部署完成后，你可以：

1. **后端 API**: `https://brief-xxxxx.zeabur.app`
   - 健康检查: `https://brief-xxxxx.zeabur.app/`
   - 代理端点: `https://brief-xxxxx.zeabur.app/proxy`

2. **前端页面**: 如果也部署在 Zeabur，会有另一个域名
   - 或者部署到 Vercel/Netlify 等其他平台

3. **使用流程**:
   - 打开前端页面
   - 输入新闻链接
   - 生成简报
   - 所有 API 请求都会通过 Zeabur 后端处理

---

## 💡 提示

- Zeabur 免费版有使用限制，但足够个人项目使用
- 建议定期查看日志，监控 API 调用情况
- 生产环境建议设置明确的 CORS 白名单

祝你部署顺利！ 🎉

