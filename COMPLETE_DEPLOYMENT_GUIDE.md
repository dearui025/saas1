# 🚀 AI交易机器人完整部署指南

## 第一步：VPS服务器部署

### 1. 准备VPS服务器
- 推荐配置：2核CPU，4GB内存，50GB存储
- 操作系统：Ubuntu 20.04 LTS 或更高版本

### 2. 运行VPS部署脚本
```bash
# 下载部署脚本
wget https://raw.githubusercontent.com/dearui025/saas1/main/deploy_vps.sh

# 给脚本执行权限
chmod +x deploy_vps.sh

# 运行部署脚本
./deploy_vps.sh
```

### 3. 配置环境变量
```bash
# 编辑环境配置文件
nano ~/saas1/.env
```

在`.env`文件中填入以下信息：
```env
# DeepSeek API密钥
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 币安API密钥
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET=your_binance_secret_here

# Supabase数据库配置
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key
```

### 4. 启动交易机器人
```bash
# 进入项目目录
cd ~/saas1

# 激活虚拟环境
source .venv/bin/activate

# 后台运行交易机器人
tmux new-session -d -s trading-bot
tmux send-keys -t trading-bot 'cd ~/saas1 && source .venv/bin/activate && python src/deepseekBNB.py' Enter
```

## 第二步：Supabase配置

### 1. 创建Supabase项目
1. 访问 [Supabase官网](https://supabase.com/)
2. 注册账户或登录
3. 点击"New Project"
4. 填写项目信息并创建项目

### 2. 初始化数据库
1. 在Supabase控制台中打开SQL编辑器
2. 复制并执行 [supabase_init.sql](file://c:\Users\Administrator\Desktop\ai-trading-bot-main\supabase_init.sql) 中的内容

### 3. 配置环境变量
在Supabase项目设置中添加以下环境变量：
- `SUPABASE_URL`: 您的Supabase项目URL
- `SUPABASE_ANON_KEY`: 您的Supabase匿名密钥

### 4. 部署边缘函数
```bash
# 安装Supabase CLI（如果尚未安装）
npm install -g supabase

# 登录Supabase
supabase login

# 链接项目
supabase link --project-ref YOUR_PROJECT_REF

# 部署函数
supabase functions deploy web-interface
```

## 第三步：验证部署

### 1. 检查VPS上的交易机器人
```bash
# 查看交易机器人运行状态
tmux attach -t trading-bot
```

### 2. 检查Supabase数据库
1. 在Supabase控制台中查看表数据
2. 验证是否有新的交易记录和决策数据

### 3. 访问Web监控界面
```
https://your-project-ref.supabase.co/functions/v1/web-interface
```

## 第四步：日常维护

### 1. 更新代码
```bash
# 停止交易机器人
tmux send-keys -t trading-bot C-c

# 拉取最新代码
cd ~/saas1
git pull origin main

# 更新依赖
source .venv/bin/activate
pip install -r requirements.txt

# 重启交易机器人
tmux send-keys -t trading-bot 'cd ~/saas1 && source .venv/bin/activate && python src/deepseekBNB.py' Enter
```

### 2. 监控系统状态
```bash
# 查看系统资源使用情况
htop

# 查看交易机器人日志
tmux attach -t trading-bot
```

## 故障排除

### 常见问题及解决方案

1. **交易机器人无法启动**
   - 检查API密钥是否正确配置
   - 验证网络连接是否正常
   - 查看错误日志获取详细信息

2. **Supabase连接失败**
   - 检查环境变量配置
   - 验证Supabase项目URL和密钥
   - 确认网络防火墙设置

3. **Web界面无法访问**
   - 检查边缘函数部署状态
   - 验证Supabase环境变量
   - 查看函数执行日志

## 安全建议

1. **API密钥保护**
   - 不要在代码中硬编码密钥
   - 定期轮换API密钥
   - 限制API密钥权限

2. **服务器安全**
   - 配置防火墙规则
   - 使用SSH密钥认证
   - 定期更新系统和软件

3. **数据备份**
   - 定期备份Supabase数据库
   - 保留本地交易日志
   - 设置自动备份策略

## 联系支持

如遇到问题，请提供以下信息以便快速解决：
1. 错误日志内容
2. 系统环境信息
3. 部署步骤执行情况
4. 相关配置文件内容（隐藏敏感信息）