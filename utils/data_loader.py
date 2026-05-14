import pandas as pd

def load_scores(uploaded_file):
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def get_class_summary(df, exclude_cols=['总分']):
    score_cols = []
    for col in df.columns[1:]:
        if pd.api.types.is_numeric_dtype(df[col]) and col not in exclude_cols:
            score_cols.append(col)
    if not score_cols:
        raise ValueError("没有找到有效的数值成绩列，请检查Excel格式。")
    summary = {}
    for col in score_cols:
        summary[col] = {
            'mean': df[col].mean(),
            'std': df[col].std(),
            'max': df[col].max(),
            'min': df[col].min()
        }
    return summary, score_cols