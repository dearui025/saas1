#!/bin/bash

# AI交易机器人VPS一键部署脚本
# 适用于Ubuntu 20.04+

echo "🚀 开始部署AI交易机器人..."

# 更新系统
echo "🔄 更新系统..."
sudo apt update && sudo apt upgrade -y

# 安装基础工具
echo "🔧 安装基础工具..."
sudo apt install -y curl wget git unzip tmux htop software-properties-common

# 安装Python 3.11
echo "🐍 安装Python 3.11..."
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils

# 验证Python安装
echo "✅ 验证Python安装..."
python3.11 --version

# 克隆项目代码
echo "📥 克隆项目代码..."
cd ~
git clone https://github.com/dearui025/saas1.git
cd saas1

# 创建虚拟环境
echo "📦 创建Python虚拟环境..."
python3.11 -m venv .venv
source .venv/bin/activate

# 升级pip
echo "⬆️ 升级pip..."
pip install --upgrade pip

# 安装项目依赖
echo "📥 安装项目依赖..."
pip install -r requirements.txt

# 创建环境配置文件
echo "⚙️ 创建环境配置文件..."
cp config/env.example .env

echo "✅ VPS部署完成！"
echo "请编辑.env文件配置您的API密钥："
echo "nano .env"
echo ""
echo "然后运行以下命令启动交易机器人："
echo "tmux new-session -d -s trading-bot"
echo "tmux send-keys -t trading-bot 'cd ~/saas1 && source .venv/bin/activate && python src/deepseekBNB.py' Enter"