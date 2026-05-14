# utils/rank_utils.py
import pandas as pd
import streamlit as st
import os

def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@st.cache_data
def load_physics_rank():
    csv_path = os.path.join(get_project_root(), 'data', 'physics_rank.csv')
    try:
        df = pd.read_csv(csv_path)
        df = df.rename(columns={'分数': 'score', '累计人数': 'cumulative'})
        df = df.sort_values('score', ascending=False).reset_index(drop=True)
        return df
    except FileNotFoundError:
        st.error(f"未找到物理类一分一段表文件: {csv_path}")
        return pd.DataFrame(columns=['score', 'cumulative'])

@st.cache_data
def load_history_rank():
    csv_path = os.path.join(get_project_root(), 'data', 'history_rank.csv')
    try:
        df = pd.read_csv(csv_path)
        df = df.rename(columns={'分数': 'score', '累计人数': 'cumulative'})
        df = df.sort_values('score', ascending=False).reset_index(drop=True)
        return df
    except FileNotFoundError:
        st.error(f"未找到历史类一分一段表文件: {csv_path}")
        return pd.DataFrame(columns=['score', 'cumulative'])

def get_rank_from_score(score, subject_type='物理'):
    """
    根据分数和科目类型返回省排名（位次），整数。
    分数高于最高分时返回最小累计人数（即最高分对应的位次）；
    分数低于最低分时返回最大累计人数（即总人数）。
    """
    if subject_type == '物理':
        df = load_physics_rank()
    else:
        df = load_history_rank()
    
    if df.empty:
        # 如果一分一段表加载失败，返回-1表示无法获取
        return -1
    
    # 确保列名正确（假设为 'score' 和 'cumulative'）
    if 'score' not in df.columns or 'cumulative' not in df.columns:
        # 如果列名是中文，尝试重命名
        if '分数' in df.columns and '累计人数' in df.columns:
            df = df.rename(columns={'分数': 'score', '累计人数': 'cumulative'})
        else:
            return -1
    
    df = df.sort_values('score', ascending=False).reset_index(drop=True)
    
    # 边界处理
    if score >= df['score'].max():
        return int(df['cumulative'].min())
    if score <= df['score'].min():
        return int(df['cumulative'].max())
    
    # 查找所在区间
    for i in range(len(df)-1):
        high_score = df.loc[i, 'score']
        low_score = df.loc[i+1, 'score']
        high_rank = df.loc[i, 'cumulative']
        low_rank = df.loc[i+1, 'cumulative']
        
        if low_score <= score <= high_score:
            if high_score == low_score:
                return int(high_rank)
            # 线性插值
            rank = high_rank + (high_score - score) / (high_score - low_score) * (low_rank - high_rank)
            return int(round(rank))
    
    # 未找到（理论上不会到这里）
    return int(df['cumulative'].max())

def get_total_students(subject_type='物理'):
    """返回该科目类别的考生总人数（基于一分一段表最后累计人数）"""
    if subject_type == '物理':
        df = load_physics_rank()
    else:
        df = load_history_rank()
    if df.empty:
        return 173282 if subject_type == '物理' else 39125  # 降级默认值
    return int(df['cumulative'].max())