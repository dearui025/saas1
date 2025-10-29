# 完整部署指南：AI交易机器人 + Supabase监控

## 🏗️ 系统架构

```
┌─────────────────────┐    ┌─────────────────────┐
│   VPS/云服务器      │    │    Supabase         │
│                     │    │                     │
│  AI交易机器人       │◄──►│  数据库存储         │
│  (Python应用)       │    │  (交易数据)         │
│                     │    │                     │
│  持续运行交易逻辑   │    │                     │
└─────────────────────┘    └─────────────────────┘
                                    ▲
                                    │
                                    ▼
                          ┌─────────────────────┐
                          │   Web监控界面       │
                          │  (Supabase Edge     │
                          │   Functions)        │
                          │                     │
                          │  实时展示交易状态   │
                          └─────────────────────┘
```

## 1. VPS/云服务器部署AI交易机器人

### 🔧 服务器环境配置

1. **选择服务器**:
   - 推荐配置: 2核CPU, 4GB内存, 50GB存储
   - 操作系统: Ubuntu 20.04 LTS 或 CentOS 8+

2. **安装必要软件**:
   ```bash
   # 更新系统
   sudo apt update && sudo apt upgrade -y
   
   # 安装Python 3.11
   sudo apt install software-properties-common -y
   sudo add-apt-repository ppa:deadsnakes/ppa -y
   sudo apt install python3.11 python3.11-venv python3.11-dev -y
   
   # 安装Git
   sudo apt install git -y
   
   # 安装tmux (后台运行)
   sudo apt install tmux -y
   ```

3. **克隆项目代码**:
   ```bash
   git clone https://github.com/dearui025/saas1.git
   cd saas1
   ```

4. **创建虚拟环境并安装依赖**:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

5. **配置环境变量**:
   ```bash
   cp config/env.example .env
   # 编辑.env文件，填入API密钥
   nano .env
   ```

6. **后台运行交易机器人**:
   ```bash
   # 使用tmux创建会话
   tmux new-session -d -s trading-bot
   tmux send-keys -t trading-bot 'source .venv/bin/activate && cd src && python deepseekBNB.py' Enter
   ```

## 2. Supabase配置

### 🗄️ 创建数据库表结构

1. **登录Supabase控制台**
2. **进入SQL编辑器，执行以下SQL创建表**:

```sql
-- 交易统计表
CREATE TABLE trading_stats (
  id SERIAL PRIMARY KEY,
  total_trades INTEGER DEFAULT 0,
  win_trades INTEGER DEFAULT 0,
  total_pnl NUMERIC(20, 8) DEFAULT 0.0,
  start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_update TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI决策记录表
CREATE TABLE ai_decisions (
  id SERIAL PRIMARY KEY,
  action VARCHAR(20) NOT NULL,
  coin VARCHAR(10) NOT NULL,
  confidence VARCHAR(10) NOT NULL,
  reason TEXT,
  decision_time TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 运行时信息表
CREATE TABLE runtime_info (
  id SERIAL PRIMARY KEY,
  invocation_count INTEGER DEFAULT 0,
  program_start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_update TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 账户信息表
CREATE TABLE account_info (
  id SERIAL PRIMARY KEY,
  total_balance NUMERIC(20, 8) DEFAULT 0.0,
  available_balance NUMERIC(20, 8) DEFAULT 0.0,
  unrealized_pnl NUMERIC(20, 8) DEFAULT 0.0,
  last_update TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_ai_decisions_time ON ai_decisions(decision_time DESC);
CREATE INDEX idx_trading_stats_last_update ON trading_stats(last_update DESC);
```

### 🔐 配置环境变量

在Supabase项目设置中添加以下环境变量:
- `SUPABASE_URL` - 你的Supabase项目URL
- `SUPABASE_ANON_KEY` - 你的Supabase匿名密钥

## 3. 部署Supabase边缘函数

### 🚀 部署Web监控界面

```bash
# 安装Supabase CLI
npm install -g supabase

# 链接项目
supabase link --project-ref YOUR_PROJECT_REF

# 部署函数
supabase functions deploy web-interface
```

## 4. 配置VPS与Supabase通信

### 🔄 更新AI交易机器人代码

确保在VPS上的.env文件中添加Supabase配置:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_role_key
```

### 📊 数据同步

AI交易机器人将自动将数据同步到Supabase数据库:
- 交易统计数据
- AI决策记录
- 运行时信息
- 账户信息

## 5. 访问监控界面

部署完成后，通过以下URL访问监控界面:
```
https://your-project-ref.supabase.co/functions/v1/web-interface
```

## 🛠️ 维护和监控

### 🔧 VPS维护
```bash
# 查看交易机器人运行状态
tmux attach -t trading-bot

# 重启交易机器人
tmux send-keys -t trading-bot C-c
tmux send-keys -t trading-bot 'source .venv/bin/activate && cd src && python deepseekBNB.py' Enter
```

### 📈 Supabase监控
- 通过Supabase控制台查看数据库使用情况
- 监控边缘函数执行日志
- 设置数据库备份策略

## ⚠️ 安全注意事项

1. **API密钥保护**:
   - 不要在代码中硬编码密钥
   - 使用环境变量存储敏感信息
   - 定期轮换密钥

2. **网络安全性**:
   - 配置防火墙规则
   - 仅开放必要端口
   - 使用SSH密钥认证

3. **数据备份**:
   - 定期备份Supabase数据库
   - 保留本地交易日志
   - 设置自动备份策略

## 📞 支持和故障排除

如遇到问题，请检查:
1. Supabase数据库连接
2. API密钥有效性
3. 网络连接状态
4. 日志文件内容