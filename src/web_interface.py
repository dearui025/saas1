#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Trading Bot - Web可视化界面
基于Flask的简单Web接口，用于显示交易状态和AI决策
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime
import pandas as pd
from typing import Dict, Any, Optional
from binance.client import Client

app = Flask(__name__, static_folder='static', template_folder='templates')

# 设置项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_json_data(file_path: str) -> Dict[str, Any]:
    """加载JSON数据文件"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"读取文件 {file_path} 失败: {e}")
        return {}

def load_trading_stats() -> Dict[str, Any]:
    """加载交易统计数据"""
    stats_file = os.path.join(PROJECT_ROOT, 'trading_stats.json')
    return load_json_data(stats_file)

def load_ai_decisions() -> Dict[str, Any]:
    """加载AI决策数据"""
    decisions_file = os.path.join(PROJECT_ROOT, 'ai_decisions.json')
    return load_json_data(decisions_file)

def load_runtime_info() -> Dict[str, Any]:
    """加载运行时信息"""
    runtime_file = os.path.join(PROJECT_ROOT, 'current_runtime.json')
    return load_json_data(runtime_file)

def load_env_config() -> Dict[str, str]:
    """加载.env配置文件"""
    env_file = os.path.join(PROJECT_ROOT, '.env')
    config = {}
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value
    return config

def save_env_config(config: Dict[str, str]) -> None:
    """保存配置到.env文件"""
    env_file = os.path.join(PROJECT_ROOT, '.env')
    
    # 读取现有文件内容
    existing_lines = []
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            existing_lines = f.readlines()
    
    # 更新或添加配置项
    new_lines = []
    processed_keys = set()
    
    for line in existing_lines:
        line = line.rstrip('\n\r')
        if line.strip() and not line.startswith('#') and '=' in line:
            key = line.split('=', 1)[0]
            if key in config:
                new_lines.append(f"{key}={config[key]}\n")
                processed_keys.add(key)
            else:
                new_lines.append(line + '\n')
        else:
            new_lines.append(line + '\n')
    
    # 添加新的配置项
    for key, value in config.items():
        if key not in processed_keys:
            new_lines.append(f"{key}={value}\n")
    
    # 保存文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def get_binance_account_info():
    """获取币安账户信息"""
    try:
        # 从环境变量加载API密钥
        config = load_env_config()
        api_key = config.get('BINANCE_API_KEY')
        api_secret = config.get('BINANCE_SECRET')
        
        if not api_key or not api_secret:
            print("API密钥未配置")
            return None
            
        # 初始化币安客户端
        client = Client(api_key, api_secret)
        
        # 获取账户信息
        account = client.futures_account()
        print(f"获取到账户信息: {account}")
        for asset in account['assets']:
            if asset['asset'] == 'USDT':
                total = float(asset['walletBalance'])
                available = float(asset['availableBalance'])
                unrealized_pnl = float(asset['unrealizedProfit'])
                print(f"USDT资产: 总余额={total}, 可用余额={available}, 未实现盈亏={unrealized_pnl}")
                return {
                    'total': total,
                    'available': available,
                    'unrealized_pnl': unrealized_pnl
                }
        print("未找到USDT资产")
        return None
    except Exception as e:
        print(f"获取币安账户信息失败: {e}")
        import traceback
        traceback.print_exc()
        return None

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/settings')
def settings():
    """设置页面"""
    config = load_env_config()
    return render_template('settings.html', config=config)

@app.route('/api/save_binance_keys', methods=['POST'])
def save_binance_keys():
    """API接口：保存币安API密钥"""
    try:
        data: Optional[Dict[str, str]] = request.json
        if data is None:
            return jsonify({'success': False, 'message': '无效的请求数据'})
            
        binance_api_key = data.get('binance_api_key', '')
        binance_secret = data.get('binance_secret', '')
        
        # 获取当前配置
        config = load_env_config()
        
        # 更新币安API密钥
        if binance_api_key:
            config['BINANCE_API_KEY'] = binance_api_key
        if binance_secret:
            config['BINANCE_SECRET'] = binance_secret
        
        # 保存配置
        save_env_config(config)
        
        return jsonify({'success': True, 'message': '币安API密钥保存成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'保存失败: {str(e)}'})

@app.route('/api/stats')
def api_stats():
    """API接口：获取交易统计数据"""
    stats = load_trading_stats()
    return jsonify(stats)

@app.route('/api/decisions')
def api_decisions():
    """API接口：获取AI决策数据"""
    decisions = load_ai_decisions()
    # 只返回最近的10条决策
    if 'decisions' in decisions:
        decisions['decisions'] = decisions['decisions'][-10:]
    return jsonify(decisions)

@app.route('/api/runtime')
def api_runtime():
    """API接口：获取运行时信息"""
    runtime = load_runtime_info()
    return jsonify(runtime)

@app.route('/api/account')
def api_account():
    """API接口：获取账户信息"""
    print("API请求: 获取账户信息")
    account_info = get_binance_account_info()
    print(f"账户信息: {account_info}")
    if account_info is not None:  # 修改这里，检查是否为None而不是是否为True
        print("返回真实账户信息")
        return jsonify(account_info)
    else:
        # 如果无法获取真实数据，返回模拟数据
        print("返回模拟账户信息")
        return jsonify({
            'total': 0.0,
            'available': 0.0,
            'unrealized_pnl': 0.0
        })

@app.route('/api/status')
def api_status():
    """API接口：获取综合状态信息"""
    stats = load_trading_stats()
    decisions = load_ai_decisions()
    runtime = load_runtime_info()
    
    # 获取最近的决策
    latest_decision = None
    if 'decisions' in decisions and decisions['decisions']:
        latest_decision = decisions['decisions'][-1]
    
    return jsonify({
        'stats': stats,
        'latest_decision': latest_decision,
        'decisions': decisions,
        'runtime': runtime
    })

if __name__ == '__main__':
    # 创建templates目录
    templates_dir = os.path.join(PROJECT_ROOT, 'src', 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # 创建static目录
    static_dir = os.path.join(PROJECT_ROOT, 'src', 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    # 创建主页面HTML模板
    html_template = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI交易机器人监控面板</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --success-color: #2ecc71;
            --danger-color: #e74c3c;
            --warning-color: #f39c12;
            --info-color: #1abc9c;
            --light-color: #ecf0f1;
            --dark-color: #34495e;
            --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            --hover-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: var(--card-shadow);
            text-align: center;
        }
        
        header h1 {
            font-size: 1.8rem;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        header p {
            font-size: 1rem;
            opacity: 0.9;
        }
        
        nav {
            background: white;
            padding: 12px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: var(--card-shadow);
            display: flex;
            justify-content: center;
        }
        
        nav a {
            text-decoration: none;
            color: var(--primary-color);
            padding: 10px 15px;
            border-radius: 6px;
            margin: 0 5px;
            transition: all 0.3s ease;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.9rem;
        }
        
        nav a:hover, nav a.active {
            background: var(--secondary-color);
            color: white;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: var(--card-shadow);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-3px);
            box-shadow: var(--hover-shadow);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 12px;
            border-bottom: 2px solid #eee;
        }
        
        .card-header i {
            font-size: 1.3rem;
            margin-right: 10px;
            color: var(--secondary-color);
        }
        
        .card-header h2 {
            font-size: 1.2rem;
            color: var(--primary-color);
            margin: 0;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 15px;
        }
        
        .stat-item {
            text-align: center;
            padding: 15px 10px;
            background: #f8f9fa;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .stat-item:hover {
            background: #e9ecef;
            transform: scale(1.02);
        }
        
        .stat-value {
            font-size: 1.4rem;
            font-weight: 700;
            color: var(--primary-color);
            font-family: 'Courier New', monospace;
            margin: 8px 0;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            word-break: break-all;
        }
        
        .stat-label {
            font-size: 0.8rem;
            color: #666;
            font-weight: 500;
        }
        
        .decision-list {
            list-style: none;
            padding: 0;
        }
        
        .decision-item {
            padding: 15px;
            border-bottom: 1px solid #eee;
            transition: background-color 0.3s ease;
        }
        
        .decision-item:hover {
            background-color: #f8f9fa;
        }
        
        .decision-item:last-child {
            border-bottom: none;
        }
        
        .decision-time {
            font-size: 0.75rem;
            color: #999;
            margin-bottom: 6px;
        }
        
        .decision-action {
            font-weight: 700;
            margin: 8px 0;
            font-size: 1.1rem;
        }
        
        .decision-reason {
            font-size: 0.85rem;
            color: #555;
            line-height: 1.4;
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
        
        .refresh-section {
            text-align: center;
            margin: 25px 0;
        }
        
        .refresh-btn {
            background: var(--secondary-color);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            box-shadow: var(--card-shadow);
        }
        
        .refresh-btn:hover {
            background: #2980b9;
            transform: translateY(-2px);
            box-shadow: var(--hover-shadow);
        }
        
        .last-updated {
            text-align: center;
            color: #777;
            font-size: 0.8rem;
            margin-top: 15px;
        }
        
        /* 财务信息样式 */
        .financial-card {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
        }
        
        .financial-card .card-header i {
            color: white;
        }
        
        .financial-card .card-header h2 {
            color: white;
        }
        
        .financial-card .stat-value {
            color: white;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
            font-size: 1.6rem;
        }
        
        .financial-card .stat-label {
            color: rgba(255,255,255,0.85);
        }
        
        .financial-card .stat-item {
            background: rgba(255,255,255,0.15);
        }
        
        .financial-card .stat-item:hover {
            background: rgba(255,255,255,0.25);
        }
        
        .profit-positive {
            color: var(--success-color) !important;
        }
        
        .profit-negative {
            color: var(--danger-color) !important;
        }
        
        /* 币安世纪金额特殊样式 */
        .binance-amount {
            font-size: 1.6rem;
            font-weight: 800;
            font-family: 'Courier New', monospace;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
        }
        
        /* 手机端优化 */
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            header {
                padding: 15px 10px;
            }
            
            header h1 {
                font-size: 1.5rem;
                gap: 8px;
            }
            
            header h1 i {
                font-size: 1.2rem;
            }
            
            header p {
                font-size: 0.9rem;
            }
            
            nav {
                padding: 10px 5px;
                flex-wrap: wrap;
            }
            
            nav a {
                padding: 8px 12px;
                margin: 3px;
                font-size: 0.85rem;
                gap: 5px;
            }
            
            .dashboard {
                grid-template-columns: 1fr;
                gap: 15px;
            }
            
            .card {
                padding: 15px;
            }
            
            .card-header {
                margin-bottom: 12px;
                padding-bottom: 10px;
            }
            
            .card-header h2 {
                font-size: 1.1rem;
            }
            
            .stats-grid {
                gap: 10px;
            }
            
            .stat-item {
                padding: 12px 8px;
            }
            
            .stat-value {
                font-size: 1.2rem;
            }
            
            .stat-label {
                font-size: 0.75rem;
            }
            
            .decision-item {
                padding: 12px;
            }
            
            .decision-time {
                font-size: 0.7rem;
            }
            
            .decision-action {
                font-size: 1rem;
            }
            
            .decision-reason {
                font-size: 0.8rem;
            }
            
            .refresh-btn {
                padding: 10px 20px;
                font-size: 0.9rem;
            }
            
            .binance-amount {
                font-size: 1.3rem;
            }
        }
        
        /* 小屏幕手机优化 */
        @media (max-width: 480px) {
            header h1 {
                font-size: 1.3rem;
                flex-direction: column;
                gap: 5px;
            }
            
            nav {
                flex-direction: column;
                gap: 8px;
            }
            
            nav a {
                width: 100%;
                justify-content: center;
                margin: 0;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .stat-value {
                font-size: 1.3rem;
            }
            
            .binance-amount {
                font-size: 1.4rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1><i class="fas fa-robot"></i> AI交易机器人</h1>
            <p>实时监控AI交易决策和性能</p>
        </header>
        
        <nav>
            <a href="/" class="active"><i class="fas fa-chart-line"></i> 仪表盘</a>
            <a href="/settings"><i class="fas fa-cog"></i> 设置</a>
        </nav>
        
        <div class="dashboard">
            <div class="card financial-card">
                <div class="card-header">
                    <i class="fas fa-wallet"></i>
                    <h2>账户财务信息</h2>
                </div>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-label">账户总权益</div>
                        <div class="stat-value binance-amount" id="account_balance">-</div>
                        <div class="stat-label">USDT</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">可用余额</div>
                        <div class="stat-value binance-amount" id="available_balance">-</div>
                        <div class="stat-label">USDT</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">未实现盈亏</div>
                        <div class="stat-value binance-amount" id="unrealized_pnl">-</div>
                        <div class="stat-label">USDT</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <i class="fas fa-tachometer-alt"></i>
                    <h2>运行状态</h2>
                </div>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-label">运行状态</div>
                        <div class="stat-value" id="runtime_status">-</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">AI调用次数</div>
                        <div class="stat-value" id="invocation_count">-</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">运行时长</div>
                        <div class="stat-value" id="uptime">-</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <i class="fas fa-chart-bar"></i>
                    <h2>交易统计</h2>
                </div>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-label">总交易次数</div>
                        <div class="stat-value" id="total_trades">-</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">胜率</div>
                        <div class="stat-value" id="win_rate">-</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">总盈亏</div>
                        <div class="stat-value" id="total_pnl">-</div>
                        <div class="stat-label">USDT</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <i class="fas fa-brain"></i>
                <h2>最新AI决策</h2>
            </div>
            <div id="latest_decision">
                <p style="text-align: center; padding: 20px; color: #777;">暂无决策数据</p>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <i class="fas fa-history"></i>
                <h2>最近决策历史</h2>
            </div>
            <ul class="decision-list" id="decision_list">
                <li style="text-align: center; padding: 20px; color: #777;">加载中...</li>
            </ul>
        </div>
        
        <div class="refresh-section">
            <button class="refresh-btn" onclick="refreshData()">
                <i class="fas fa-sync-alt"></i> 刷新数据
            </button>
        </div>
        
        <div class="last-updated">
            最后更新: <span id="last_updated">-</span>
        </div>
    </div>

    <script>
        // 格式化时间
        function formatTime(isoString) {
            const date = new Date(isoString);
            return date.toLocaleString('zh-CN');
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
                return `${diffDays}天${diffHours}小时`;
            } else if (diffHours > 0) {
                return `${diffHours}小时${diffMinutes}分钟`;
            } else {
                return `${diffMinutes}分钟`;
            }
        }
        
        // 格式化金额（币安世纪金额样式）
        function formatBinanceAmount(value) {
            if (value === '-' || value === null || value === undefined) return '-';
            const num = parseFloat(value);
            if (isNaN(num)) return '-';
            
            // 添加千位分隔符
            return num.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
        
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
        
        // 将英文信心等级转换为中文
        function translateConfidenceLevel(confidence) {
            const translations = {
                'HIGH': '高',
                'MEDIUM': '中',
                'LOW': '低'
            };
            return translations[confidence] || confidence;
        }
        
        // 更新财务信息
        function updateFinancialData(data) {
            fetch('/api/account')
                .then(response => response.json())
                .then(accountData => {
                    console.log("获取到账户数据:", accountData);
                    document.getElementById('account_balance').textContent = formatBinanceAmount(accountData.total);
                    document.getElementById('available_balance').textContent = formatBinanceAmount(accountData.available);
                    document.getElementById('unrealized_pnl').textContent = formatBinanceAmount(accountData.unrealized_pnl);
                    
                    // 根据盈亏设置颜色
                    const pnlElement = document.getElementById('unrealized_pnl');
                    if (accountData.unrealized_pnl > 0) {
                        pnlElement.className = 'stat-value binance-amount profit-positive';
                    } else if (accountData.unrealized_pnl < 0) {
                        pnlElement.className = 'stat-value binance-amount profit-negative';
                    } else {
                        pnlElement.className = 'stat-value binance-amount';
                    }
                })
                .catch(error => {
                    console.error('获取账户信息失败:', error);
                });
        }
        
        // 更新数据
        function updateData(data) {
            // 更新财务信息
            updateFinancialData(data);
            
            // 更新运行时信息
            if (data.runtime) {
                document.getElementById('invocation_count').textContent = data.runtime.invocation_count || '-';
                if (data.runtime.program_start_time) {
                    document.getElementById('uptime').textContent = formatDuration(data.runtime.program_start_time);
                }
                document.getElementById('runtime_status').textContent = '运行中';
                document.getElementById('runtime_status').className = 'stat-value positive';
            }
            
            // 更新交易统计
            if (data.stats) {
                document.getElementById('total_trades').textContent = data.stats.total_trades || 0;
                document.getElementById('win_rate').textContent = data.stats.win_rate ? (data.stats.win_rate * 100).toFixed(2) + '%' : '-';
                document.getElementById('total_pnl').textContent = data.stats.total_pnl ? formatBinanceAmount(data.stats.total_pnl) : '-';
                
                // 根据盈亏设置颜色
                const pnlElement = document.getElementById('total_pnl');
                if (data.stats.total_pnl > 0) {
                    pnlElement.className = 'stat-value profit-positive';
                } else if (data.stats.total_pnl < 0) {
                    pnlElement.className = 'stat-value profit-negative';
                } else {
                    pnlElement.className = 'stat-value';
                }
            }
            
            // 更新最新决策
            if (data.latest_decision) {
                const action = getActionDisplay(data.latest_decision.action);
                const confidence = translateConfidenceLevel(data.latest_decision.confidence);
                document.getElementById('latest_decision').innerHTML = `
                    <div class="decision-time"><i class="far fa-clock"></i> ${formatTime(data.latest_decision.time)}</div>
                    <div class="decision-action ${action.class}">${action.text}</div>
                    <div class="decision-reason"><i class="fas fa-comment"></i> ${data.latest_decision.reason}</div>
                    <div style="margin-top: 8px;"><i class="fas fa-shield-alt"></i> 信心: ${confidence}</div>
                `;
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
                        
                        // 处理可能的编码问题
                        let reason = decision.reason || '';
                        
                        html += `
                            <li class="decision-item">
                                <div class="decision-time"><i class="far fa-clock"></i> ${formatTime(decision.time)}</div>
                                <div class="decision-action ${action.class}">${action.text}</div>
                                <div class="decision-reason"><i class="fas fa-comment"></i> ${reason}</div>
                                <div style="margin-top: 6px;"><i class="fas fa-shield-alt"></i> 信心: ${confidence}</div>
                            </li>
                        `;
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
        }
        
        // 刷新数据
        function refreshData() {
            // 显示加载状态
            const refreshBtn = document.querySelector('.refresh-btn');
            const originalText = refreshBtn.innerHTML;
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 刷新中...';
            refreshBtn.disabled = true;
            
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    updateData(data);
                })
                .catch(error => {
                    console.error('获取数据失败:', error);
                    alert('获取数据失败，请检查服务器是否运行正常');
                })
                .finally(() => {
                    // 恢复按钮状态
                    setTimeout(() => {
                        refreshBtn.innerHTML = originalText;
                        refreshBtn.disabled = false;
                    }, 500);
                });
        }
        
        // 页面加载完成后自动获取数据
        document.addEventListener('DOMContentLoaded', function() {
            refreshData();
            // 每30秒自动刷新一次
            setInterval(refreshData, 30000);
        });
    </script>
</body>
</html>
'''
    
    # 保存主页面HTML模板
    template_path = os.path.join(templates_dir, 'index.html')
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    # 创建设置页面HTML模板（保持不变）
    settings_template = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>设置 - AI交易机器人</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --success-color: #2ecc71;
            --danger-color: #e74c3c;
            --warning-color: #f39c12;
            --info-color: #1abc9c;
            --light-color: #ecf0f1;
            --dark-color: #34495e;
            --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            --hover-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: var(--card-shadow);
            text-align: center;
        }
        
        header h1 {
            font-size: 2.2rem;
            margin-bottom: 10px;
        }
        
        header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        nav {
            background: white;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: var(--card-shadow);
            display: flex;
            justify-content: center;
        }
        
        nav a {
            text-decoration: none;
            color: var(--primary-color);
            padding: 12px 25px;
            border-radius: 8px;
            margin: 0 10px;
            transition: all 0.3s ease;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        nav a:hover, nav a.active {
            background: var(--secondary-color);
            color: white;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: var(--card-shadow);
            margin-bottom: 25px;
        }
        
        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid #eee;
        }
        
        .card-header i {
            font-size: 1.5rem;
            margin-right: 12px;
            color: var(--secondary-color);
        }
        
        .card-header h2 {
            font-size: 1.4rem;
            color: var(--primary-color);
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        .form-group input {
            width: 100%;
            padding: 14px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
            box-sizing: border-box;
        }
        
        .form-group input:focus {
            border-color: var(--secondary-color);
            outline: none;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
        }
        
        .btn {
            background: var(--secondary-color);
            color: white;
            border: none;
            padding: 14px 28px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            box-shadow: var(--card-shadow);
        }
        
        .btn:hover {
            background: #2980b9;
            transform: translateY(-2px);
            box-shadow: var(--hover-shadow);
        }
        
        .btn-success {
            background: var(--success-color);
        }
        
        .btn-success:hover {
            background: #27ae60;
        }
        
        .message {
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            display: none;
            font-weight: 500;
        }
        
        .message.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .message.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .note {
            background: #fff3cd;
            color: #856404;
            padding: 25px;
            border-radius: 12px;
            margin-top: 25px;
            border: 1px solid #ffeaa7;
        }
        
        .note h3 {
            margin-top: 0;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .note ul {
            padding-left: 20px;
        }
        
        .note li {
            margin-bottom: 10px;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            
            nav {
                flex-direction: column;
                gap: 10px;
            }
            
            nav a {
                margin: 5px 0;
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1><i class="fas fa-cog"></i> AI交易机器人设置</h1>
            <p>配置API密钥和其他参数</p>
        </header>
        
        <nav>
            <a href="/"><i class="fas fa-chart-line"></i> 仪表盘</a>
            <a href="/settings" class="active"><i class="fas fa-cog"></i> 设置</a>
        </nav>
        
        <div class="card">
            <div class="card-header">
                <i class="fas fa-key"></i>
                <h2>币安API密钥配置</h2>
            </div>
            <div id="message" class="message"></div>
            
            <form id="binanceForm">
                <div class="form-group">
                    <label for="binance_api_key"><i class="fas fa-key"></i> 币安API Key:</label>
                    <input type="password" id="binance_api_key" name="binance_api_key" value="{{ config.get('BINANCE_API_KEY', '') }}" placeholder="请输入币安API Key">
                </div>
                
                <div class="form-group">
                    <label for="binance_secret"><i class="fas fa-lock"></i> 币安Secret Key:</label>
                    <input type="password" id="binance_secret" name="binance_secret" value="{{ config.get('BINANCE_SECRET', '') }}" placeholder="请输入币安Secret Key">
                </div>
                
                <button type="submit" class="btn btn-success">
                    <i class="fas fa-save"></i> 保存配置
                </button>
            </form>
        </div>
        
        <div class="note">
            <h3><i class="fas fa-lightbulb"></i> 使用说明</h3>
            <p><strong>1. 获取币安API密钥：</strong></p>
            <ul>
                <li>登录币安账户</li>
                <li>进入API管理页面：https://www.binance.com/zh-CN/my/settings/api-management</li>
                <li>点击"创建API"</li>
                <li>设置API名称（如"AI Trading Bot"）</li>
                <li>启用"读取权限"和"现货/期货交易"权限</li>
                <li>保存并记录您的API密钥和Secret</li>
            </ul>
            <p><strong>2. 重要提醒：</strong></p>
            <ul>
                <li>保存配置后，需要重启交易机器人程序才能使新配置生效</li>
                <li>请妥善保管您的API密钥，不要泄露给他人</li>
                <li>建议为交易机器人创建独立的币安子账户以隔离风险</li>
            </ul>
        </div>
    </div>

    <script>
        document.getElementById('binanceForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const apiKey = document.getElementById('binance_api_key').value;
            const secretKey = document.getElementById('binance_secret').value;
            
            // 显示加载状态
            const submitBtn = document.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 保存中...';
            submitBtn.disabled = true;
            
            // 发送请求
            fetch('/api/save_binance_keys', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    binance_api_key: apiKey,
                    binance_secret: secretKey
                })
            })
            .then(response => response.json())
            .then(data => {
                const messageDiv = document.getElementById('message');
                if (data.success) {
                    messageDiv.className = 'message success';
                    messageDiv.innerHTML = '<i class="fas fa-check-circle"></i> ' + data.message;
                    messageDiv.style.display = 'block';
                    
                    // 3秒后隐藏消息
                    setTimeout(() => {
                        messageDiv.style.display = 'none';
                    }, 3000);
                } else {
                    messageDiv.className = 'message error';
                    messageDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> ' + data.message;
                    messageDiv.style.display = 'block';
                }
            })
            .catch(error => {
                const messageDiv = document.getElementById('message');
                messageDiv.className = 'message error';
                messageDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> 保存失败: ' + error.message;
                messageDiv.style.display = 'block';
            })
            .finally(() => {
                // 恢复按钮状态
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 500);
            });
        });
    </script>
</body>
</html>
'''
    
    # 保存设置页面HTML模板
    settings_template_path = os.path.join(templates_dir, 'settings.html')
    with open(settings_template_path, 'w', encoding='utf-8') as f:
        f.write(settings_template)
    
    print("Web界面已创建，正在启动...")
    print("请在浏览器中访问: http://localhost:5000")
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000, debug=True)