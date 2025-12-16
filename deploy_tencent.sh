#!/bin/bash
# 腾讯云函数计算快速部署脚本

echo "=================================="
echo "腾讯云函数计算 - 快速部署脚本"
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3"
    exit 1
fi

# 创建部署目录
DEPLOY_DIR="deploy_tencent"
echo "创建部署目录: $DEPLOY_DIR"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

# 复制必要文件
echo "复制函数文件..."
cp scf_handler.py $DEPLOY_DIR/index.py
cp requirements.txt $DEPLOY_DIR/

# 检查是否安装依赖
read -p "是否安装Python依赖到部署包? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "安装依赖包..."
    cd $DEPLOY_DIR
    pip install -r requirements.txt -t . --upgrade
    
    # 清理不必要的文件
    echo "清理不必要的文件..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find . -type f -name "*.pyc" -delete
    find . -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null
    
    cd ..
fi

# 打包
ZIP_FILE="brief-scf-$(date +%Y%m%d-%H%M%S).zip"
echo "打包部署文件: $ZIP_FILE"
cd $DEPLOY_DIR
zip -r ../$ZIP_FILE . -q
cd ..

echo ""
echo "=================================="
echo "部署包已创建: $ZIP_FILE"
echo "=================================="
echo ""
echo "下一步操作:"
echo "1. 登录腾讯云控制台"
echo "2. 进入云函数 SCF 服务"
echo "3. 创建新函数或更新现有函数"
echo "4. 上传 $ZIP_FILE"
echo "5. 配置函数入口: index.main_handler"
echo "6. 配置环境变量（UNIFUNS_API_KEY, GEMINI_API_KEY, NANO_BANANA_API_KEY）"
echo "7. 创建API网关触发器"
echo ""
echo "详细步骤请参考: DEPLOY_TENCENT.md"
echo "=================================="

