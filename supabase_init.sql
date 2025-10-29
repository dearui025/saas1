-- Supabase数据库初始化脚本

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

-- 创建索引以提高查询性能
CREATE INDEX idx_ai_decisions_time ON ai_decisions(decision_time DESC);
CREATE INDEX idx_trading_stats_last_update ON trading_stats(last_update DESC);

-- 插入初始数据
INSERT INTO trading_stats (total_trades, win_trades, total_pnl) VALUES (0, 0, 0.0);
INSERT INTO runtime_info (invocation_count, program_start_time) VALUES (0, NOW());
INSERT INTO account_info (total_balance, available_balance, unrealized_pnl) VALUES (0.0, 0.0, 0.0);