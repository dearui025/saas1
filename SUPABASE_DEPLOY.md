# AI Trading Bot - Supabase部署指南

## 🚀 部署到Supabase

### 1. 创建Supabase项目

1. 访问 [Supabase官网](https://supabase.com/) 并创建账户
2. 创建新项目
3. 记录下项目URL和API密钥

### 2. 安装Supabase CLI

```bash
# macOS
brew install supabase/tap/supabase

# Windows (使用Scoop)
scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase

# 其他平台请参考官方文档
```

### 3. 链接项目

```bash
supabase link --project-ref your-project-ref
```

### 4. 设置环境变量

在Supabase项目中设置以下环境变量：
- `DEEPSEEK_API_KEY` - DeepSeek API密钥
- `BINANCE_API_KEY` - 币安API密钥
- `BINANCE_SECRET` - 币安密钥

### 5. 部署边缘函数

```bash
supabase functions deploy web-interface
```

### 6. 访问Web界面

部署完成后，您可以通过以下URL访问Web界面：
```
https://your-project-ref.supabase.co/functions/v1/web-interface
```

## ⚠️ 重要说明

1. **AI交易机器人限制**: 当前的AI交易机器人是一个需要持续运行的Python应用程序，而Supabase Edge Functions是无服务器函数，有执行时间限制。建议将AI交易机器人部署在VPS或云服务器上，仅将Web监控界面部署到Supabase。

2. **数据存储**: 如果需要在Supabase数据库中存储交易数据，您需要创建相应的表结构并修改代码以使用Supabase客户端进行数据操作。

3. **安全性**: 请确保不要在代码中硬编码API密钥，始终使用环境变量来存储敏感信息。

## 📁 项目结构

```
supabase/
├── functions/
│   ├── _shared/
│   │   └── cors.ts          # CORS配置
│   └── web-interface.ts     # Web界面边缘函数
├── config.json             # Supabase配置文件
└── README.md               # 本文件
```

## 🛠️ 进一步开发

如果您希望将完整的AI交易功能集成到Supabase中，您可能需要：

1. 创建数据库表来存储交易数据
2. 使用Supabase的数据库功能而不是本地JSON文件
3. 将AI决策逻辑分解为可触发的函数
4. 使用Supabase的定时任务功能来定期执行交易逻辑