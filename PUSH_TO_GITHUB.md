# 推送到 GitHub 的步骤

## 情况说明

当前仓库指向的是 `SiyuanJia/brief`，你没有推送权限。

## 解决方案：创建你自己的仓库

### 步骤1: 在 GitHub 创建新仓库

1. 登录 GitHub
2. 点击右上角 "+" → "New repository"
3. 填写信息：
   - **Repository name**: `brief`（或你喜欢的名字）
   - **Description**: 财经时事资讯简报生成器
   - **Visibility**: Public 或 Private
4. **不要**勾选 "Initialize with README"
5. 点击 "Create repository"

### 步骤2: 更新远程仓库地址

在你的本地项目目录执行：

```bash
cd /Users/weixiaogang/AI/brief

# 移除旧的远程仓库
git remote remove origin

# 添加你的新仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/brief.git

# 推送到你的仓库
git push -u origin main
```

### 步骤3: 在 Zeabur 部署

1. 登录 [Zeabur](https://zeabur.com)
2. 点击 "New Project"
3. 选择 "Import from GitHub"
4. 授权 Zeabur 访问 GitHub
5. 选择你刚创建的仓库
6. 配置环境变量（见下方）

---

## Zeabur 环境变量配置

在 Zeabur 项目设置中添加：

```
UNIFUNS_API_KEY=sk-your-api-key-here
GEMINI_API_KEY=sk-your-api-key-here
NANO_BANANA_API_KEY=sk-your-api-key-here
ALLOWED_ORIGINS=*
```

**注意**：请将 `sk-your-api-key-here` 替换为你的真实 API 密钥

---

## 完成后的访问

部署完成后，Zeabur 会给你一个地址，类似：
```
https://brief-xxxxx.zeabur.app
```

这就是你的后端 API 地址，可以直接外网访问！

---

## 更新前端配置

部署成功后，需要更新 `api_new.js` 中的代理地址：

```javascript
'proxyEndpoints': {
    'development': 'https://brief-xxxxx.zeabur.app/proxy',
    'production': 'https://brief-xxxxx.zeabur.app/proxy'
}
```

然后提交并推送：

```bash
git add api_new.js
git commit -m "Update proxy endpoint to Zeabur"
git push
```

