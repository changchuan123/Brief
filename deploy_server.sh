#!/bin/bash
# 服务器部署脚本 - 在服务器上执行

echo "=================================="
echo "财经简报生成器 - 服务器部署"
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装"
    exit 1
fi

# 进入项目目录
cd /opt/brief || {
    echo "错误: 项目目录不存在，请先上传项目文件到 /opt/brief"
    exit 1
}

# 检查是否安装了依赖
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖包..."
pip install -r requirements.txt --quiet

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "错误: 未找到 .env 文件"
    echo "请创建 .env 文件并配置API密钥"
    exit 1
fi

# 加载环境变量
export $(cat .env | grep -v '^#' | xargs)

# 停止旧进程（如果存在）
echo "停止旧进程..."
pkill -f "local_proxy.py" || true
sleep 2

# 启动服务器（固定端口16001）
echo "启动代理服务器（端口16001）..."
PORT=16001 nohup python3 local_proxy.py > brief.log 2>&1 &

# 等待服务启动
sleep 3

# 检查服务是否启动成功
if curl -s http://127.0.0.1:16001/ > /dev/null; then
    echo ""
    echo "=================================="
    echo "✅ 部署成功！"
    echo "=================================="
    echo "服务地址: http://212.64.57.87:16001"
    echo "健康检查: http://212.64.57.87:16001/"
    echo "代理端点: http://212.64.57.87:16001/proxy"
    echo ""
    echo "查看日志: tail -f /opt/brief/brief.log"
    echo "停止服务: pkill -f local_proxy.py"
    echo "=================================="
else
    echo "❌ 服务启动失败，请检查日志: cat /opt/brief/brief.log"
    exit 1
fi

