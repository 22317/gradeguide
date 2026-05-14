import matplotlib.pyplot as plt
import numpy as np
import matplotlib

# ================= 满分映射配置 =================
SUBJECT_FULL_SCORES = {
    "语文": 150, "数学": 150, "英语": 150,
    "物理": 100, "化学": 100, "生物": 100,
    "历史": 100, "地理": 100, "政治": 100,
}
DEFAULT_FULL_SCORE = 100

# ================= 中文字体设置 =================
def set_chinese_font():
    font_names = ['Microsoft YaHei', 'SimHei', 'SimSun', 'FangSong', 'KaiTi']
    for font in font_names:
        try:
            matplotlib.rcParams['font.sans-serif'] = [font]
            matplotlib.rcParams['axes.unicode_minus'] = False
            plt.text(0.5, 0.5, '测试', fontdict={'size': 10})
            plt.close()
            return
        except:
            continue
set_chinese_font()
# ================================================

def normalize_scores(scores_dict):
    """将原始分数转换为百分比（0-100）"""
    normalized = {}
    for subject, raw_score in scores_dict.items():
        # 跳过总分（实际上在调用前已经过滤，但双重保险）
        if subject == '总分':
            continue
        full = SUBJECT_FULL_SCORES.get(subject, DEFAULT_FULL_SCORE)
        if full <= 0:
            full = 100
        percent = (raw_score / full) * 100
        normalized[subject] = max(0, min(100, percent))
    return normalized

def draw_radar_chart(student_scores, class_means, dimensions, student_name, figsize=(4,4)):
    dimensions = [d for d in dimensions if d != '总分']
    if len(dimensions) < 2:
        fig, ax = plt.subplots()
        ax.text(0.5,0.5,'科目数量不足，无法绘制雷达图', ha='center', va='center')
        return fig

    # 归一化
    student_subset = {k:v for k,v in student_scores.items() if k in dimensions}
    class_subset = {k:v for k,v in class_means.items() if k in dimensions}
    norm_student = normalize_scores(student_subset)
    norm_class = normalize_scores(class_subset)

    # 按维度顺序取值
    student_vals = [norm_student[d] for d in dimensions]
    class_vals   = [norm_class[d] for d in dimensions]

    # 计算角度并闭合
    angles = np.linspace(0, 2*np.pi, len(dimensions), endpoint=False).tolist()
    # 闭合：将第一个点添加到末尾
    angles += angles[:1]
    student_vals += student_vals[:1]
    class_vals   += class_vals[:1]

    # 绘图
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
    ax.plot(angles, student_vals, 'o-', linewidth=2, label=student_name)
    ax.fill(angles, student_vals, alpha=0.25)
    ax.plot(angles, class_vals, 'o-', linewidth=2, label='班级平均')
    ax.fill(angles, class_vals, alpha=0.1)

    # 科目标签
    wrapped = [d if len(d)<=6 else '\n'.join([d[i:i+6] for i in range(0,len(d),6)]) for d in dimensions]
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(wrapped, fontsize=10, ha='center')

    # 径向刻度：强制百分比
    ax.set_ylim(0,100)
    ax.set_yticks([20,40,60,80,100])
    ax.set_yticklabels(['20%','40%','60%','80%','100%'], fontsize=8)
    ax.grid(True)
    ax.legend(loc='upper right', bbox_to_anchor=(1.2,1.0))
    ax.set_title(f'{student_name} 学情雷达图 (百分制)', fontsize=14, pad=20)
    return fig

def draw_comparison_radar(pre_scores, post_scores, dimensions, student_name, figsize=(4,4)):
    dimensions = [d for d in dimensions if d != '总分']
    if len(dimensions) < 2:
        fig, ax = plt.subplots()
        ax.text(0.5,0.5,'科目数量不足，无法绘制雷达图', ha='center', va='center')
        return fig

    pre_subset = {k:v for k,v in pre_scores.items() if k in dimensions}
    post_subset = {k:v for k,v in post_scores.items() if k in dimensions}
    norm_pre = normalize_scores(pre_subset)
    norm_post = normalize_scores(post_subset)

    pre_vals = [norm_pre[d] for d in dimensions]
    post_vals = [norm_post[d] for d in dimensions]

    angles = np.linspace(0, 2*np.pi, len(dimensions), endpoint=False).tolist()
    angles += angles[:1]
    pre_vals += pre_vals[:1]
    post_vals += post_vals[:1]

    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
    ax.plot(angles, pre_vals, 'o-', linewidth=2, label='前测', color='gray')
    ax.fill(angles, pre_vals, alpha=0.1, color='gray')
    ax.plot(angles, post_vals, 'o-', linewidth=2, label='后测', color='blue')
    ax.fill(angles, post_vals, alpha=0.25, color='blue')

    wrapped = [d if len(d)<=6 else '\n'.join([d[i:i+6] for i in range(0,len(d),6)]) for d in dimensions]
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(wrapped, fontsize=10, ha='center')

    ax.set_ylim(0,100)
    ax.set_yticks([20,40,60,80,100])
    ax.set_yticklabels(['20%','40%','60%','80%','100%'], fontsize=8)
    ax.grid(True)
    ax.legend(loc='upper right', bbox_to_anchor=(1.2,1.0))
    ax.set_title(f'{student_name} 前后测对比 (百分制)', fontsize=14, pad=20)
    return fig