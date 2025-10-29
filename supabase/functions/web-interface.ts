// Supabase Edge Function for AI Trading Bot Web Interface
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

serve(async (_req) => {
  // 初始化Supabase客户端
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL') ?? '',
    Deno.env.get('SUPABASE_ANON_KEY') ?? ''
  );
  
  try {
    // 获取交易统计数据
    const { data: statsData, error: statsError } = await supabase
      .from('trading_stats')
      .select('*')
      .order('last_update', { ascending: false })
      .limit(1)
      .single();
    
    // 获取最新AI决策
    const { data: latestDecisionData, error: latestDecisionError } = await supabase
      .from('ai_decisions')
      .select('*')
      .order('decision_time', { ascending: false })
      .limit(1)
      .single();
    
    // 获取最近的AI决策历史
    const { data: decisionsData, error: decisionsError } = await supabase
      .from('ai_decisions')
      .select('*')
      .order('decision_time', { ascending: false })
      .limit(20);
    
    // 获取运行时信息
    const { data: runtimeData, error: runtimeError } = await supabase
      .from('runtime_info')
      .select('*')
      .order('last_update', { ascending: false })
      .limit(1)
      .single();
    
    // 获取账户信息
    const { data: accountData, error: accountError } = await supabase
      .from('account_info')
      .select('*')
      .order('last_update', { ascending: false })
      .limit(1)
      .single();
    
    // 构造响应数据
    const data = {
      stats: statsError ? null : statsData,
      latest_decision: latestDecisionError ? null : latestDecisionData,
      decisions: decisionsError ? { decisions: [] } : { decisions: decisionsData || [] },
      runtime: runtimeError ? null : runtimeData,
      account: accountError ? null : accountData
    };
    
    // 获取请求路径
    const url = new URL(_req.url);
    const path = url.pathname;
    
    // API路由处理
    if (path === '/api/status') {
      return new Response(
        JSON.stringify(data),
        { headers: { "Content-Type": "application/json" } }
      );
    } else if (path === '/api/account') {
      return new Response(
        JSON.stringify(accountData || { total: 0, available: 0, unrealized_pnl: 0 }),
        { headers: { "Content-Type": "application/json" } }
      );
    } else {
      // 返回HTML页面
      const html = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI交易机器人监控面板</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --success-color: #10b981;
            --danger-color: #ef4444;
            --warning-color: #f59e0b;
            --info-color: #3b82f6;
            --dark-color: #1e293b;
            --light-color: #f8fafc;
            --border-color: #e2e8f0;
            --card-bg: #ffffff;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f1f5f9;
            color: var(--text-primary);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: linear-gradient(135deg, var(--primary-color), #1d4ed8);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            margin: 0;
            font-size: 2rem;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: var(--card-bg);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
        }
        
        .card-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 15px;
            color: var(--dark-color);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card-title i {
            font-size: 1.5rem;
        }
        
        .stat-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid var(--border-color);
        }
        
        .stat-item:last-child {
            border-bottom: none;
        }
        
        .stat-label {
            font-weight: 500;
            color: var(--text-secondary);
        }
        
        .stat-value {
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .positive {
            color: var(--success-color);
        }
        
        .negative {
            color: var(--danger-color);
        }
        
        .neutral {
            color: var(--warning-color);
        }
        
        .binance-amount {
            font-family: 'Courier New', monospace;
        }
        
        .profit-positive {
            color: var(--success-color);
        }
        
        .profit-negative {
            color: var(--danger-color);
        }
        
        .decision-item {
            padding: 15px;
            border-left: 4px solid var(--primary-color);
            background-color: #f8fafc;
            margin-bottom: 15px;
            border-radius: 0 8px 8px 0;
        }
        
        .decision-time {
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }
        
        .decision-action {
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 10px;
        }
        
        .decision-reason {
            font-size: 0.95rem;
            line-height: 1.5;
            color: var(--text-primary);
        }
        
        .decision-list {
            max-height: 500px;
            overflow-y: auto;
            padding-right: 10px;
        }
        
        .decision-list::-webkit-scrollbar {
            width: 6px;
        }
        
        .decision-list::-webkit-scrollbar-track {
            background: #f1f5f9;
        }
        
        .decision-list::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 3px;
        }
        
        .last-updated {
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-top: 20px;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .grid {
                grid-template-columns: 1fr;
            }
            
            header {
                padding: 15px;
            }
            
            h1 {
                font-size: 1.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 AI交易机器人监控面板</h1>
            <p>基于DeepSeek AI的BNB/USDT合约自动交易系统</p>
        </header>
        
        <div class="grid">
            <!-- 财务信息 -->
            <div class="card">
                <div class="card-title">
                    <i>💰</i>
                    <span>财务信息</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">账户总额</span>
                    <span class="stat-value binance-amount" id="account_balance">-</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">可用余额</span>
                    <span class="stat-value binance-amount" id="available_balance">-</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">未实现盈亏</span>
                    <span class="stat-value binance-amount" id="unrealized_pnl">-</span>
                </div>
            </div>
            
            <!-- 运行状态 -->
            <div class="card">
                <div class="card-title">
                    <i>⚡</i>
                    <span>运行状态</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">运行状态</span>
                    <span class="stat-value positive" id="runtime_status">运行中</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">AI调用次数</span>
                    <span class="stat-value" id="invocation_count">-</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">运行时长</span>
                    <span class="stat-value" id="uptime">-</span>
                </div>
            </div>
            
            <!-- 交易统计 -->
            <div class="card">
                <div class="card-title">
                    <i>📊</i>
                    <span>交易统计</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">总交易次数</span>
                    <span class="stat-value" id="total_trades">-</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">胜率</span>
                    <span class="stat-value" id="win_rate">-</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">总盈亏</span>
                    <span class="stat-value" id="total_pnl">-</span>
                </div>
            </div>
        </div>
        
        <!-- 最新决策 -->
        <div class="card">
            <div class="card-title">
                <i>🧠</i>
                <span>最新AI决策</span>
            </div>
            <div id="latest_decision">
                <p style="text-align: center; padding: 20px; color: var(--text-secondary);">加载中...</p>
            </div>
        </div>
        
        <!-- 决策历史 -->
        <div class="card">
            <div class="card-title">
                <i>📜</i>
                <span>最近决策历史</span>
            </div>
            <div class="decision-list">
                <ul id="decision_list" style="list-style: none; padding: 0; margin: 0;">
                    <li style="text-align: center; padding: 20px; color: var(--text-secondary);">加载中...</li>
                </ul>
            </div>
        </div>
        
        <div class="last-updated">
            最后更新: <span id="last_updated">-</span>
        </div>
    </div>
    
    <script>
        // 获取决策动作的显示文本和样式
        function getActionDisplay(action) {
            const actions = {
                'BUY_OPEN': {text: '📈 开多', class: 'positive'},
                'SELL_OPEN': {text: '📉 开空', class: 'negative'},
                'CLOSE': {text: '🔒 平仓', class: 'neutral'},
                'HOLD': {text: '💤 观望', class: 'neutral'}
            };
            return actions[action] || {text: action, class: 'neutral'};
        }
        
        // 格式化金额（币安世纪金额样式）
        function formatBinanceAmount(value) {
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
        function formatDuration(startTime) {
            if (!startTime) return '-';
            const start = new Date(startTime);
            const now = new Date();
            const diffMs = now - start;
            const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
            const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
            
            if (diffDays > 0) {
                return \`\${diffDays}天\${diffHours}小时\`;
            } else if (diffHours > 0) {
                return \`\${diffHours}小时\${diffMinutes}分钟\`;
            } else {
                return \`\${diffMinutes}分钟\`;
            }
        }
        
        // 将英文信心等级转换为中文
        function translateConfidenceLevel(confidence) {
            const translations = {
                'HIGH': '高',
                'MEDIUM': '中',
                'LOW': '低'
            };
            return translations[confidence] || confidence;
        }
        
        // 格式化时间
        function formatTime(isoString) {
            const date = new Date(isoString);
            return date.toLocaleString('zh-CN');
        }
        
        // 更新财务信息
        function updateFinancialData(data) {
            if (data.account) {
                document.getElementById('account_balance').textContent = formatBinanceAmount(data.account.total_balance);
                document.getElementById('available_balance').textContent = formatBinanceAmount(data.account.available_balance);
                document.getElementById('unrealized_pnl').textContent = formatBinanceAmount(data.account.unrealized_pnl);
                
                // 根据盈亏设置颜色
                const pnlElement = document.getElementById('unrealized_pnl');
                if (data.account.unrealized_pnl > 0) {
                    pnlElement.className = 'stat-value binance-amount profit-positive';
                } else if (data.account.unrealized_pnl < 0) {
                    pnlElement.className = 'stat-value binance-amount profit-negative';
                } else {
                    pnlElement.className = 'stat-value binance-amount';
                }
            } else {
                document.getElementById('account_balance').textContent = '-';
                document.getElementById('available_balance').textContent = '-';
                document.getElementById('unrealized_pnl').textContent = '-';
            }
        }
        
        // 更新数据
        function updateData(data) {
            try {
                // 更新财务信息
                updateFinancialData(data);
                
                // 更新运行时信息
                if (data.runtime) {
                    document.getElementById('invocation_count').textContent = data.runtime.invocation_count !== undefined ? data.runtime.invocation_count : '-';
                    if (data.runtime.program_start_time) {
                        document.getElementById('uptime').textContent = formatDuration(data.runtime.program_start_time);
                    } else {
                        document.getElementById('uptime').textContent = '-';
                    }
                    document.getElementById('runtime_status').textContent = '运行中';
                    document.getElementById('runtime_status').className = 'stat-value positive';
                } else {
                    // 如果没有运行时信息，显示默认值
                    document.getElementById('invocation_count').textContent = '-';
                    document.getElementById('uptime').textContent = '-';
                    document.getElementById('runtime_status').textContent = '未知';
                    document.getElementById('runtime_status').className = 'stat-value';
                }
                
                // 更新交易统计
                if (data.stats) {
                    document.getElementById('total_trades').textContent = data.stats.total_trades !== undefined ? data.stats.total_trades : '-';
                    
                    // 计算胜率
                    if (data.stats.win_trades !== undefined && data.stats.total_trades !== undefined && data.stats.total_trades > 0) {
                        const winRate = data.stats.win_trades / data.stats.total_trades;
                        document.getElementById('win_rate').textContent = (winRate * 100).toFixed(2) + '%';
                    } else {
                        document.getElementById('win_rate').textContent = '-';
                    }
                    
                    document.getElementById('total_pnl').textContent = data.stats.total_pnl !== undefined ? formatBinanceAmount(data.stats.total_pnl) : '-';
                    
                    // 根据盈亏设置颜色
                    const pnlElement = document.getElementById('total_pnl');
                    if (data.stats.total_pnl > 0) {
                        pnlElement.className = 'stat-value profit-positive';
                    } else if (data.stats.total_pnl < 0) {
                        pnlElement.className = 'stat-value profit-negative';
                    } else {
                        pnlElement.className = 'stat-value';
                    }
                } else {
                    // 如果没有交易统计信息，显示默认值
                    document.getElementById('total_trades').textContent = '-';
                    document.getElementById('win_rate').textContent = '-';
                    document.getElementById('total_pnl').textContent = '-';
                    
                    // 重置盈亏颜色
                    const pnlElement = document.getElementById('total_pnl');
                    pnlElement.className = 'stat-value';
                }
                
                // 更新最新决策
                if (data.latest_decision) {
                    const action = getActionDisplay(data.latest_decision.action);
                    const confidence = translateConfidenceLevel(data.latest_decision.confidence);
                    document.getElementById('latest_decision').innerHTML = \`
                        <div class="decision-time"><i class="far fa-clock"></i> \${formatTime(data.latest_decision.decision_time)}</div>
                        <div class="decision-action \${action.class}">\${action.text}</div>
                        <div class="decision-reason"><i class="fas fa-comment"></i> \${data.latest_decision.reason}</div>
                        <div style="margin-top: 8px;"><i class="fas fa-shield-alt"></i> 信心: \${confidence}</div>
                    \`;
                } else {
                    document.getElementById('latest_decision').innerHTML = '<p style="text-align: center; padding: 20px; color: #777;">暂无决策数据</p>';
                }
                
                // 更新决策列表
                if (data.decisions && data.decisions.decisions) {
                    const listElement = document.getElementById('decision_list');
                    if (data.decisions.decisions.length === 0) {
                        listElement.innerHTML = '<li style="text-align: center; padding: 20px; color: #777;">暂无决策数据</li>';
                    } else {
                        let html = '';
                        // 反向遍历以显示最新的在前面
                        for (let i = data.decisions.decisions.length - 1; i >= 0; i--) {
                            const decision = data.decisions.decisions[i];
                            const action = getActionDisplay(decision.action);
                            const confidence = translateConfidenceLevel(decision.confidence);
                            
                            html += \`
                                <li class="decision-item">
                                    <div class="decision-time"><i class="far fa-clock"></i> \${formatTime(decision.decision_time)}</div>
                                    <div class="decision-action \${action.class}">\${action.text}</div>
                                    <div class="decision-reason"><i class="fas fa-comment"></i> \${decision.reason}</div>
                                    <div style="margin-top: 6px;"><i class="fas fa-shield-alt"></i> 信心: \${confidence}</div>
                                </li>
                            \`;
                        }
                        listElement.innerHTML = html;
                    }
                } else {
                    // 如果没有决策数据，显示默认消息
                    const listElement = document.getElementById('decision_list');
                    listElement.innerHTML = '<li style="text-align: center; padding: 20px; color: #777;">暂无决策数据</li>';
                }
                
                // 更新最后更新时间
                document.getElementById('last_updated').textContent = new Date().toLocaleString('zh-CN');
            } catch (error) {
                console.error('更新数据时出错:', error);
            }
        }
        
        // 定期获取数据
        function fetchData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    updateData(data);
                })
                .catch(error => {
                    console.error('获取数据失败:', error);
                });
        }
        
        // 页面加载完成后开始获取数据
        document.addEventListener('DOMContentLoaded', function() {
            fetchData();
            // 每30秒更新一次数据
            setInterval(fetchData, 30000);
        });
    </script>
</body>
</html>
      `;
      
      return new Response(html, {
        headers: { "Content-Type": "text/html; charset=utf-8" }
      });
    }
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      headers: { "Content-Type": "application/json" },
      status: 500
    });
  }
});