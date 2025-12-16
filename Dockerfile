FROM python:3.9-slim

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口（Zeabur 会自动分配端口，通过 PORT 环境变量获取）
EXPOSE 5000

# 启动命令
CMD ["python3", "local_proxy.py"]

