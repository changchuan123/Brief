# 腾讯云部署指南

本指南将帮助你完成项目在腾讯云函数计算（SCF）上的部署。

## 📋 前置要求

### 1. API密钥准备
你需要准备以下API密钥（从 https://302.ai 获取）：
- **Unifuns API Key**: 用于网页内容提取
- **Gemini API Key**: 用于AI内容分析
- **Nano Banana API Key**: 用于图片生成

### 2. 环境要求
- Python 3.7+
- 腾讯云账号
- 腾讯云函数计算（SCF）服务已开通

---

## 🏠 本地测试

本地测试步骤与通用部署指南相同，使用 `local_proxy.py` 和 `start_local.sh`。

详细步骤请参考 `DEPLOY.md` 中的"本地测试"部分。

---

## 🚀 腾讯云函数计算部署

### 方式一：通过控制台部署（推荐新手）

#### 步骤1: 准备部署包

创建部署目录：
```bash
mkdir deploy_tencent
cd deploy_tencent
```

复制函数文件：
```bash
cp ../scf_handler.py ./index.py  # 腾讯云要求入口文件名为 index.py
cp ../requirements.txt .
```

#### 步骤2: 安装依赖

```bash
# 创建虚拟环境（可选）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖到当前目录
pip install -r requirements.txt -t .
```

#### 步骤3: 打包部署文件

```bash
# 创建zip包（排除不必要的文件）
zip -r brief-scf.zip . \
    -x "*.pyc" \
    -x "__pycache__/*" \
    -x "*.dist-info/*" \
    -x "*.egg-info/*" \
    -x "*.so" \
    -x "*.pyo"
```

#### 步骤4: 创建云函数

1. 登录 [腾讯云控制台](https://console.cloud.tencent.com/)
2. 进入 **云函数 SCF** 服务
3. 选择 **函数服务** → **新建**
4. 配置函数：
   - **函数名称**: `brief-proxy`
   - **运行环境**: Python 3.9（或 Python 3.7/3.8）
   - **创建方式**: 选择"本地上传zip包"
   - **提交方法**: 上传 `brief-scf.zip`
   - **函数入口**: `index.main_handler`（重要！）
   - **执行超时时间**: 建议设置为 300 秒（5分钟）

#### 步骤5: 配置环境变量

在函数配置 → 环境变量中添加：

```
UNIFUNS_API_KEY=sk-your-unifuns-api-key
GEMINI_API_KEY=sk-your-gemini-api-key
NANO_BANANA_API_KEY=sk-your-nano-banana-api-key
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**注意**: 
- `ALLOWED_ORIGINS` 设置允许访问的域名，多个用逗号分隔
- 生产环境不要使用 `*`，应该明确指定域名

#### 步骤6: 配置API网关触发器

1. 在函数详情页，点击 **触发管理** → **创建触发器**
2. 选择 **API网关触发器**
3. 配置触发器：
   - **API服务**: 选择"新建API服务"或使用现有服务
   - **请求方法**: 勾选 GET, POST, OPTIONS
   - **发布环境**: 选择"发布"（生产环境）或"测试"（测试环境）
   - **路径**: `/` 或 `/proxy`
   - **鉴权方式**: 选择"免鉴权"（或根据需要配置）

#### 步骤7: 获取访问地址

部署完成后，在触发器详情中可以看到访问地址，类似：
```
https://service-xxxxx-xxxxx.ap-guangzhou.apigateway.myqcloud.com/release/brief-proxy
```

或者如果配置了自定义域名：
```
https://api.yourdomain.com/brief-proxy
```

### 方式二：使用 Serverless Framework（推荐）

#### 步骤1: 安装 Serverless Framework

```bash
npm install -g serverless
```

#### 步骤2: 配置腾讯云凭证

```bash
# 配置腾讯云凭证
serverless config credentials \
  --provider tencent \
  --key YOUR_SECRET_ID \
  --secret YOUR_SECRET_KEY
```

#### 步骤3: 创建 serverless.yml

在项目根目录创建 `serverless.yml`：

```yaml
service: brief-proxy

provider:
  name: tencent
  runtime: Python3.9
  region: ap-guangzhou
  memorySize: 512
  timeout: 300
  environment:
    UNIFUNS_API_KEY: ${env:UNIFUNS_API_KEY}
    GEMINI_API_KEY: ${env:GEMINI_API_KEY}
    NANO_BANANA_API_KEY: ${env:NANO_BANANA_API_KEY}
    ALLOWED_ORIGINS: ${env:ALLOWED_ORIGINS, '*'}
  apigw:
    protocols:
      - https
    cors:
      origin: '*'
      headers:
        - Content-Type
        - Authorization
      methods:
        - GET
        - POST
        - OPTIONS

functions:
  proxy:
    handler: scf_handler.main_handler
    events:
      - apigw:
          path: /
          method:
            - GET
            - POST
            - OPTIONS
```

#### 步骤4: 部署

```bash
# 设置环境变量（或使用 .env 文件）
export UNIFUNS_API_KEY=sk-your-key
export GEMINI_API_KEY=sk-your-key
export NANO_BANANA_API_KEY=sk-your-key
export ALLOWED_ORIGINS=https://yourdomain.com

# 部署
serverless deploy
```

### 方式三：使用腾讯云 CLI

#### 步骤1: 安装腾讯云 CLI

```bash
# macOS
brew install tencentcloud-cli

# 或使用 pip
pip install tencentcloud-cli
```

#### 步骤2: 配置凭证

```bash
tccli configure
# 输入 SecretId 和 SecretKey
```

#### 步骤3: 创建函数

```bash
# 创建函数
tccli scf CreateFunction \
  --FunctionName brief-proxy \
  --Runtime Python3.9 \
  --Handler index.main_handler \
  --Code '{"ZipFile":"base64编码的zip包"}' \
  --Timeout 300 \
  --MemorySize 512 \
  --Environment '{"Variables":[{"Key":"UNIFUNS_API_KEY","Value":"sk-your-key"},{"Key":"GEMINI_API_KEY","Value":"sk-your-key"},{"Key":"NANO_BANANA_API_KEY","Value":"sk-your-key"}]}'
```

---

## 🔧 更新前端配置

部署完成后，编辑 `api_new.js`，更新生产环境代理地址：

```javascript
'proxyEndpoints': {
    'development': 'http://localhost:5000/proxy',
    'production': 'https://your-api-gateway-url.com'  // 你的API网关地址
}
```

---

## 📝 常见问题

### Q1: 函数执行超时
**A**: 
- 增加函数的超时时间（最大900秒）
- 检查API调用是否正常
- 查看函数日志定位问题

### Q2: 内存不足
**A**: 
- 增加函数内存配置（建议至少512MB）
- 优化代码，减少内存占用

### Q3: CORS错误
**A**: 
1. 检查 `ALLOWED_ORIGINS` 环境变量配置
2. 确认API网关触发器已配置CORS
3. 检查前端请求的Origin头是否正确

### Q4: 函数找不到入口
**A**: 
- 确认入口文件名为 `index.py`
- 确认入口函数为 `main_handler`
- 确认函数入口配置为 `index.main_handler`

### Q5: 依赖包安装失败
**A**: 
- 检查 `requirements.txt` 中的包名是否正确
- 某些包可能需要编译，建议在本地打包时包含已编译的依赖
- 使用腾讯云提供的依赖层（Layer）功能

---

## 💰 成本优化建议

1. **合理设置内存**: 根据实际使用情况调整，不要设置过大
2. **设置并发限制**: 避免突发流量导致费用过高
3. **使用预留并发**: 如果流量稳定，可以使用预留并发降低成本
4. **监控调用量**: 定期查看函数调用统计，优化使用频率

---

## 🔒 安全建议

1. **API密钥安全**: 
   - 使用环境变量存储，不要硬编码
   - 定期轮换API密钥
   - 使用腾讯云密钥管理服务（KMS）

2. **CORS配置**: 
   - 生产环境明确指定允许的域名
   - 不要使用 `*` 通配符

3. **访问控制**: 
   - 考虑添加API密钥验证
   - 使用API网关的鉴权功能

---

## 📊 监控和日志

1. **查看函数日志**: 
   - 在腾讯云控制台 → 云函数 → 函数服务 → 日志查询

2. **设置告警**: 
   - 配置函数错误率告警
   - 配置执行时间告警

3. **性能监控**: 
   - 查看函数执行时间分布
   - 监控内存使用情况

---

## 🎯 下一步

部署完成后，你可以：
1. 配置自定义域名（在API网关中）
2. 设置CDN加速
3. 添加监控告警
4. 优化函数性能

祝你部署顺利！ 🎉

