#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading Statistics Module - Track trading history and performance
交易统计模块 - 跟踪交易历史和性能

Simplified version for single coin trading (BNB)
单币种交易的简化版本（BNB）

Author: AI Trading Bot
License: MIT
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class TradingStatistics:
    def __init__(self, stats_file='trading_stats.json', decisions_file='ai_decisions.json'):
        self.stats_file = stats_file
        self.decisions_file = decisions_file
        self.supabase: Optional[Any] = None
        self.use_supabase = False
        
        # 初始化Supabase客户端（如果环境变量存在）
        if os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_KEY'):
            try:
                from supabase import create_client
                self.supabase = create_client(
                    os.getenv('SUPABASE_URL'),
                    os.getenv('SUPABASE_KEY')
                )
                self.use_supabase = True
                print("已连接到Supabase数据库")
            except Exception as e:
                print(f"连接Supabase失败: {e}")
                self.use_supabase = False
        
        # 初始化统计数据
        self.stats = self._load_stats()
        self.decisions = self._load_decisions()
    
    def _load_stats(self) -> Dict[str, Any]:
        """加载交易统计数据"""
        if self.use_supabase and self.supabase:
            try:
                # 从Supabase获取最新统计数据
                response = self.supabase.table('trading_stats').select('*').order('last_update', desc=True).limit(1).execute()
                if response.data:
                    return response.data[0]
                else:
                    # 如果没有数据，创建初始记录
                    initial_stats = {
                        'total_trades': 0,
                        'win_trades': 0,
                        'total_pnl': 0.0,
                        'start_time': datetime.now().isoformat(),
                        'last_update': datetime.now().isoformat()
                    }
                    self.supabase.table('trading_stats').insert(initial_stats).execute()
                    return initial_stats
            except Exception as e:
                print(f"从Supabase加载统计数据失败: {e}")
                return self._load_stats_from_file()
        else:
            return self._load_stats_from_file()
    
    def _load_stats_from_file(self) -> Dict[str, Any]:
        """从本地文件加载统计数据"""
        if os.path.exists(self.stats_file):
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                'total_trades': 0,
                'win_trades': 0,
                'total_pnl': 0.0,
                'start_time': datetime.now().isoformat(),
                'last_update': datetime.now().isoformat()
            }
    
    def _load_decisions(self) -> Dict[str, List]:
        """加载AI决策数据"""
        if self.use_supabase and self.supabase:
            try:
                # 从Supabase获取最近的决策记录
                response = self.supabase.table('ai_decisions').select('*').order('decision_time', desc=True).limit(50).execute()
                return {'decisions': response.data}
            except Exception as e:
                print(f"从Supabase加载决策数据失败: {e}")
                return self._load_decisions_from_file()
        else:
            return self._load_decisions_from_file()
    
    def _load_decisions_from_file(self) -> Dict[str, List]:
        """从本地文件加载决策数据"""
        if os.path.exists(self.decisions_file):
            with open(self.decisions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {'decisions': []}
    
    def save_stats(self):
        """保存交易统计数据"""
        self.stats['last_update'] = datetime.now().isoformat()
        
        if self.use_supabase and self.supabase:
            try:
                # 更新Supabase中的统计数据
                response = self.supabase.table('trading_stats').select('id').order('last_update', desc=True).limit(1).execute()
                if response.data:
                    record_id = response.data[0]['id']
                    self.supabase.table('trading_stats').update(self.stats).eq('id', record_id).execute()
                else:
                    # 插入新记录
                    self.supabase.table('trading_stats').insert(self.stats).execute()
            except Exception as e:
                print(f"保存统计数据到Supabase失败: {e}")
                self._save_stats_to_file()
        else:
            self._save_stats_to_file()
    
    def _save_stats_to_file(self):
        """保存统计数据到本地文件"""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
    
    def save_decision(self, action: str, coin: str, confidence: str, reason: str):
        """保存AI决策"""
        decision = {
            'action': action,
            'coin': coin,
            'confidence': confidence,
            'reason': reason,
            'decision_time': datetime.now().isoformat()
        }
        
        if self.use_supabase and self.supabase:
            try:
                # 保存到Supabase
                self.supabase.table('ai_decisions').insert(decision).execute()
                # 同时更新本地缓存
                self.decisions['decisions'].insert(0, decision)
                if len(self.decisions['decisions']) > 50:
                    self.decisions['decisions'] = self.decisions['decisions'][:50]
            except Exception as e:
                print(f"保存决策到Supabase失败: {e}")
                self._save_decision_to_file(decision)
        else:
            self._save_decision_to_file(decision)
    
    def _save_decision_to_file(self, decision: Dict):
        """保存决策到本地文件"""
        self.decisions['decisions'].insert(0, decision)
        # 只保留最近50条决策
        if len(self.decisions['decisions']) > 50:
            self.decisions['decisions'] = self.decisions['decisions'][:50]
        
        with open(self.decisions_file, 'w', encoding='utf-8') as f:
            json.dump(self.decisions, f, ensure_ascii=False, indent=2)
    
    def record_trade(self, is_win: bool, pnl: float):
        """记录交易结果"""
        self.stats['total_trades'] += 1
        if is_win:
            self.stats['win_trades'] += 1
        self.stats['total_pnl'] += pnl
        self.save_stats()
    
    def get_win_rate(self) -> float:
        """计算胜率"""
        if self.stats['total_trades'] == 0:
            return 0.0
        return self.stats['win_trades'] / self.stats['total_trades']
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计数据"""
        return self.stats
    
    def get_decisions(self) -> Dict[str, List]:
        """获取决策数据"""
        # 如果使用Supabase，重新加载以获取最新数据
        if self.use_supabase:
            self.decisions = self._load_decisions()
        return self.decisions
