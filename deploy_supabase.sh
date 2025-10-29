#!/bin/bash

# Supabase一键部署脚本

echo "🚀 开始部署Supabase组件..."

# 检查是否已安装Node.js
if ! command -v node &> /dev/null
then
    echo "📦 安装Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
fi

# 安装Supabase CLI
echo "📥 安装Supabase CLI..."
npm install -g supabase

# 验证安装
echo "✅ 验证Supabase CLI安装..."
supabase --version

echo "✅ Supabase CLI安装完成！"
echo ""
echo "请执行以下步骤完成部署："
echo "1. 登录Supabase: supabase login"
echo "2. 链接项目: supabase link --project-ref YOUR_PROJECT_REF"
echo "3. 部署函数: supabase functions deploy web-interface"