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
    根据分数和科目类型返回省排名（位次）
    """
    if subject_type == '物理':
        df = load_physics_rank()
    else:
        df = load_history_rank()
    
    if df.empty:
        return -1
    
    if score >= df['score'].max():
        return df['cumulative'].min()
    if score <= df['score'].min():
        return df['cumulative'].max()
    
    for i in range(len(df)-1):
        high_score = df.loc[i, 'score']
        low_score = df.loc[i+1, 'score']
        high_rank = df.loc[i, 'cumulative']
        low_rank = df.loc[i+1, 'cumulative']
        if low_score <= score <= high_score:
            if high_score == low_score:
                return high_rank
            rank = high_rank + (high_score - score) / (high_score - low_score) * (low_rank - high_rank)
            return int(round(rank))
    return df['cumulative'].max()