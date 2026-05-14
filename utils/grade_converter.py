# utils/grade_converter.py
import pandas as pd
import numpy as np

# 云南省等级赋分配置
# 等级 → (人数占比, (赋分下限, 赋分上限))
SCORE_LEVEL_CONFIG = {
    'A': (0.15, (86, 100)),
    'B': (0.35, (71, 85)),
    'C': (0.35, (56, 70)),
    'D': (0.13, (41, 55)),
    'E': (0.02, (30, 40)),
}

# 累加比例用于等级划分
CUMULATIVE_RATIOS = []
cum = 0
for level, (ratio, _) in SCORE_LEVEL_CONFIG.items():
    cum += ratio
    CUMULATIVE_RATIOS.append((level, cum))


def auto_detect_reelect_subjects(df):
    """
    从DataFrame的列名中自动识别再选科目（排除语数外、物理、历史、姓名等）
    返回：再选科目列表
    """
    # 定义基础科目（不参与赋分）
    basic_subjects = ['姓名', '语文', '数学', '外语', '英语', '物理', '历史']
    # 定义再选科目关键词（可扩展）
    reelect_keywords = ['化学', '地理', '思想政治', '生物学', '生物', '政治']
    
    columns = df.columns.tolist()
    detected = []
    for col in columns:
        if col in basic_subjects:
            continue
        for kw in reelect_keywords:
            if kw in col:
                detected.append(col)
                break
    # 去重并保持顺序
    detected = list(dict.fromkeys(detected))
    return detected


def get_level_by_rank(rank_percent):
    """
    根据排名百分比确定等级
    rank_percent: 排名百分比 (0~1), 越小表示排名越靠前
    """
    for level, cum_ratio in CUMULATIVE_RATIOS:
        if rank_percent <= cum_ratio:
            return level
    return 'E'


def get_level_boundaries(df, subject):
    """
    根据年级/联考数据，计算每个等级的原始分区间
    返回：{等级: (最低分, 最高分)}
    """
    if subject not in df.columns:
        return {}
    
    scores = df[subject].dropna()
    if len(scores) == 0:
        return {}
    
    sorted_scores = scores.sort_values(ascending=False).reset_index(drop=True)
    n = len(sorted_scores)
    
    boundaries = {}
    prev_end = 0
    
    for level, (ratio, _) in SCORE_LEVEL_CONFIG.items():
        end_idx = int(n * ratio)
        if end_idx > n:
            end_idx = n
        if end_idx == prev_end and end_idx < n:
            end_idx += 1  # 避免边界卡死
        
        if prev_end < n:
            level_scores = sorted_scores.iloc[prev_end:end_idx]
            if len(level_scores) > 0:
                boundaries[level] = (level_scores.min(), level_scores.max())
            else:
                boundaries[level] = (None, None)
        else:
            boundaries[level] = (None, None)
        
        prev_end = end_idx
    
    return boundaries


def convert_score(raw_score, level, boundaries):
    """
    将原始分转换为赋分
    raw_score: 原始分
    level: 等级 ('A','B','C','D','E')
    boundaries: get_level_boundaries 返回的字典
    """
    if pd.isna(raw_score):
        return np.nan
    
    y1, y2 = boundaries.get(level, (None, None))
    t1, t2 = SCORE_LEVEL_CONFIG[level][1]
    
    if y1 is None or y2 is None or y1 == y2:
        # 如果无法确定区间，返回赋分区间的中值
        return round((t1 + t2) / 2)
    
    # 等比例转换公式
    converted = t1 + (t2 - t1) * (raw_score - y1) / (y2 - y1)
    return round(converted)


def calculate_converted_grades(class_df, grade_df, score_subjects=None):
    """
    计算班级学生的赋分成绩
    class_df: 班级成绩表
    grade_df: 年级/联考成绩表
    score_subjects: 需要进行赋分的科目列表（如果为 None，则自动识别）
    返回：新的 DataFrame，包含原始列 + [科目名]_赋分
    """
    if score_subjects is None:
        score_subjects = auto_detect_reelect_subjects(class_df)
    
    result_df = class_df.copy()
    
    for subject in score_subjects:
        if subject not in grade_df.columns or subject not in class_df.columns:
            print(f"警告：科目 {subject} 在年级或班级表中不存在，跳过")
            continue
        
        # 根据年级数据确定等级边界
        boundaries = get_level_boundaries(grade_df, subject)
        
        # 获取年级数据
        grade_scores = grade_df[subject].dropna()
        n_total = len(grade_scores)
        if n_total == 0:
            continue
        
        # 为每个班级分数计算赋分（基于该分数在年级中的排名位置）
        def get_converted_for_student(raw_score):
            if pd.isna(raw_score):
                return np.nan
            
            # 计算该分数在年级中的排名百分比
            higher_count = (grade_scores > raw_score).sum()
            lower_count = (grade_scores < raw_score).sum()
            equal_count = (grade_scores == raw_score).sum()
            
            if equal_count > 0:
                rank_percent = (higher_count + equal_count / 2) / n_total
            else:
                rank_percent = higher_count / n_total
            
            level = get_level_by_rank(rank_percent)
            return convert_score(raw_score, level, boundaries)
        
        result_df[f'{subject}_赋分'] = class_df[subject].apply(get_converted_for_student)
    
    return result_df, score_subjects


def calculate_total_scores(result_df, reelected_subjects):
    """
    计算赋分后的总分
    reelected_subjects: 再选科目列表（原始列名）
    """
    total_scores = []
    for idx, row in result_df.iterrows():
        total = 0
        
        # 语数外（原始分）
        for subj in ['语文', '数学', '外语', '英语']:
            if subj in result_df.columns and not pd.isna(row[subj]):
                total += row[subj]
                break  # 避免同时有外语和英语列重复加
        
        # 物理或历史（原始分，只加存在的那个）
        if '物理' in result_df.columns and not pd.isna(row['物理']):
            total += row['物理']
        elif '历史' in result_df.columns and not pd.isna(row['历史']):
            total += row['历史']
        
        # 再选科目：使用赋分后成绩
        for subj in reelected_subjects:
            col = f'{subj}_赋分'
            if col in result_df.columns and not pd.isna(row[col]):
                total += row[col]
        
        total_scores.append(total)
    
    result_df['赋分后总分'] = total_scores
    return result_df

def calculate_grade_rank_for_class(grade_df, class_df, total_score_col='赋分后总分', name_col=None):
    """
    根据年级数据，计算班级每个学生在年级中的排名百分位
    假设年级和班级的学生姓名列名称相同（默认取第一列作为姓名列）
    """
    if name_col is None:
        name_col = grade_df.columns[0]
    
    # 确保年级数据中有总分列
    if total_score_col not in grade_df.columns:
        # 如果年级数据还没有赋分后总分，需要先计算
        from utils.grade_converter import auto_detect_reelect_subjects, calculate_converted_grades, calculate_total_scores
        reelected = auto_detect_reelect_subjects(grade_df)
        if reelected:
            grade_df, _ = calculate_converted_grades(grade_df, grade_df, reelected)
            grade_df = calculate_total_scores(grade_df, reelected)
        else:
            # 如果无法自动识别，直接返回 None
            return None
    
    # 计算年级排名（使用总分列）
    grade_df_sorted = grade_df.sort_values(total_score_col, ascending=False).reset_index(drop=True)
    grade_df_sorted['grade_rank'] = grade_df_sorted.index + 1
    grade_df_sorted['grade_rank_percent'] = grade_df_sorted['grade_rank'] / len(grade_df_sorted)
    
    # 构建姓名到排名百分位的映射
    name_to_rank = dict(zip(grade_df_sorted[name_col], grade_df_sorted['grade_rank_percent']))
    
    # 为班级学生获取排名
    class_name_col = class_df.columns[0]
    ranks = []
    for student in class_df[class_name_col]:
        if student in name_to_rank:
            ranks.append(name_to_rank[student])
        else:
            ranks.append(None)  # 未匹配到
    
    return ranks