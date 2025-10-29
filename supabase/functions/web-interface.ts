import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
import { corsHeaders } from "../_shared/cors.ts";

// 初始化Supabase客户端
const supabase = createClient(
  Deno.env.get('SUPABASE_URL') ?? '',
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
);

// 处理CORS
function handleCors(req: Request) {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }
  return null;
}

// 格式化金额
function formatBinanceAmount(value: any) {
  if (value === '-' || value === null || value === undefined) return '-';
  const num = parseFloat(value);
  if (isNaN(num)) return '-';
  
  // 处理非常小的数值（科学计数法）
  if (Math.abs(num) < 0.000001) {
    return num.toFixed(8);
  }
  
  // 处理小数值
  if (Math.abs(num) < 0.01) {
    return num.toFixed(6);
  }
  
  // 添加千位分隔符
  return num.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

// 格式化时长
function formatDuration(startTime: string) {
  if (!startTime) return '-';
  const start = new Date(startTime);
  const now = new Date();
  const diffMs = now.getTime() - start.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
  
  if (diffDays > 0) {
    return `${diffDays}天${diffHours}小时`;
  } else if (diffHours > 0) {
    return `${diffHours}小时${diffMinutes}分钟`;
  } else {
    return `${diffMinutes}分钟`;
  }
}

// 将英文信心等级转换为中文
function translateConfidenceLevel(confidence: string) {
  const translations: Record<string, string> = {
    'HIGH': '高',
    'MEDIUM': '中',
    'LOW': '低'
  };
  return translations[confidence] || confidence;
}

// 格式化时间
function formatTime(isoString: string) {
  const date = new Date(isoString);
  return date.toLocaleString('zh-CN');
}

serve(async (_req) => {
  // 返回简单的HTML页面
  const html = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI交易机器人监控面板</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f1f5f9;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .status {
            text-align: center;
            padding: 20px;
            color: #64748b;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 AI交易机器人监控面板</h1>
            <p>基于DeepSeek AI的BNB/USDT合约自动交易系统</p>
        </header>
        
        <div class="card">
            <h2>系统状态</h2>
            <div class="status">
                <p>AI交易机器人正在运行中...</p>
                <p>请通过Supabase配置环境变量以连接到您的交易所账户</p>
            </div>
        </div>
        
        <div class="card">
            <h2>部署说明</h2>
            <p>1. 在Supabase项目中设置以下环境变量：</p>
            <ul>
                <li>DEEPSEEK_API_KEY - DeepSeek API密钥</li>
                <li>BINANCE_API_KEY - 币安API密钥</li>
                <li>BINANCE_SECRET - 币安密钥</li>
            </ul>
            <p>2. 部署边缘函数：</p>
            <code>supabase functions deploy web-interface</code>
        </div>
    </div>
</body>
</html>
  `;
  
  return new Response(html, {
    headers: { "Content-Type": "text/html; charset=utf-8" }
  });
});
