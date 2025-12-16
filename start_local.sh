#!/bin/bash
# 本地测试启动脚本

echo "=================================="
echo "财经简报生成器 - 本地测试环境"
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python 3.7+"
    exit 1
fi

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
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "警告: 未找到 .env 文件"
    echo "请复制 .env.example 为 .env 并配置API密钥"
    echo ""
    read -p "是否现在创建 .env 文件? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "已创建 .env 文件，请编辑并填入你的API密钥"
        echo "然后重新运行此脚本"
        exit 0
    fi
fi

# 加载环境变量
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# 启动服务器
echo ""
echo "启动本地代理服务器..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务器"
echo "=================================="
python3 local_proxy.py

