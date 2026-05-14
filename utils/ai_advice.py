# utils/ai_advice.py
from openai import OpenAI
from config import ZHIPU_API_KEY, ZHIPU_BASE_URL, MODEL_NAME
from utils.rank_utils import get_rank_from_score
from config import ZHIPU_API_KEY, ZHIPU_BASE_URL, MODEL_NAME

client = OpenAI(
    api_key=ZHIPU_API_KEY,
    base_url=ZHIPU_BASE_URL
)

def generate_personal_advice(student_name, scores_dict, class_means_dict):
    """
    生成个性化学习建议 - 升级版
    让AI输出具体、可操作、有学科针对性的建议
    """
    # 找出薄弱科目（低于班级平均分最多的两个）
    weaknesses = []
    for subject, score in scores_dict.items():
        diff = score - class_means_dict[subject]
        if diff < 0:
            weaknesses.append((subject, diff, score, class_means_dict[subject]))
    weaknesses.sort(key=lambda x: x[1])  # 负值越小越弱
    weak_info = []
    for subj, diff, stu_score, class_avg in weaknesses[:2]:
        weak_info.append(f"{subj}: 你的分数{stu_score:.0f}，班级平均{class_avg:.0f}，差距{-diff:.0f}分")
    
    # 找出优势科目（高于班级平均分5分以上的）
    strengths = []
    for subject, score in scores_dict.items():
        diff = score - class_means_dict[subject]
        if diff > 5:
            strengths.append(f"{subject}(+{diff:.0f})")
    
    # 构造专业化提示词
    prompt = f"""你是一位经验丰富的重点高中教师，教学风格严谨、务实、富有建设性。请为学生{student_name}写一段个性化学习建议。

学生当前成绩情况：
{chr(10).join([f"- {info}" for info in weak_info]) if weak_info else '- 各科成绩均达到或接近班级平均水平'}
优势科目：{', '.join(strengths) if strengths else '无明显优势科目'}

要求：
1. 字数控制在80-120字，语气亲切但专业，不要使用“你真的很棒”等空洞夸奖。
2. 针对薄弱科目，必须给出1-2个**具体可操作的学习方法**（如：整理错题本、专项练习某类题型、背诵解题模板、每天一道计算题等）。
3. 如果存在优势科目，可以鼓励学生保持并分享方法，但重点放在薄弱提升上。
4. 避免泛泛而谈“加强基础”“多做练习”，要落点到具体动作（例如：“数学每天做3道函数分类讨论题”）。
5. 最后一句给出一个短期可实现的小目标（如“下次考试该科争取提高5分”）。

示例（仅供参考格式，不要照抄）：
“你的英语阅读失分较多，建议每天精读一篇短文并划出长难句，周末整理高频生词本。物理力学部分概念不清，可重新看课本例题并做课后前3题。下周目标：英语阅读理解少错2个。”
"""
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=300
    )
    advice = response.choices[0].message.content.strip()
    return advice


def generate_comparison_advice(student_name, pre_scores, post_scores, diff_scores, total_diff, class_avg_pre, class_avg_post):
    """
    生成两次考试对比分析建议 - 升级版
    突出进退步原因、给出针对性的调整策略
    """
    # 找出进步最大的两个科目和退步最大的两个科目
    sorted_diff = sorted(diff_scores.items(), key=lambda x: x[1], reverse=True)
    top_improve = []
    for subj, diff in sorted_diff[:2]:
        if diff > 0:
            pre = pre_scores[subj]
            post = post_scores[subj]
            top_improve.append(f"{subj}: 从{pre:.0f}分进步到{post:.0f}分 (+{diff:.0f})")
    
    top_decline = []
    for subj, diff in sorted_diff[-2:]:
        if diff < 0:
            pre = pre_scores[subj]
            post = post_scores[subj]
            top_decline.append(f"{subj}: 从{pre:.0f}分退步到{post:.0f}分 ({diff:.0f})")
    
    prompt = f"""你是一位经验丰富的重点高中教师。学生{student_name}在两次考试中总分变化{total_diff:+.0f}分。
考试信息：
- 进步科目：{'; '.join(top_improve) if top_improve else '无明显进步科目'}
- 退步科目：{'; '.join(top_decline) if top_decline else '无明显退步科目'}

请写一段针对性的学习建议（100-150字），内容需包含：
1. 简要肯定进步（如果有），但不过度表扬。
2. 分析退步可能的原因（如：知识点遗忘、题型变化、粗心、练习不足等，根据常识推测）。
3. 针对退步科目，给出2-3个具体改进措施（如：重做错题、专题突破、限时训练等）。
4. 提醒学生保持优势科目的学习方法。
5. 结尾给出一个具体可量化的目标（例如：“下次考试物理大题多拿6分”）。

要求：语言简洁、专业、有建设性，避免“继续努力”等空话。
"""
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=400
    )
    advice = response.choices[0].message.content.strip()
    return advice

def generate_class_report(class_avg_pre, class_avg_post, common_subjects, student_count, total_diff_avg):
    """生成班级整体质量分析报告"""
    # 找出进步最大的科目和退步最大的科目
    subject_diffs = {subj: class_avg_post[subj] - class_avg_pre[subj] for subj in common_subjects}
    sorted_diffs = sorted(subject_diffs.items(), key=lambda x: x[1], reverse=True)
    top_improve = sorted_diffs[0]
    top_decline = sorted_diffs[-1]
    
    prompt = f"""你是一位高中教研组长。请根据以下班级考试数据，撰写一份300-400字的班级质量分析报告，语言正式、简洁，包括整体概况、优势科目、薄弱科目、教学建议四个方面。
考试数据：
- 班级人数：{student_count}
- 前测总分平均分：{sum(class_avg_pre.values()):.1f}
- 后测总分平均分：{sum(class_avg_post.values()):.1f}
- 总分平均分变化：{total_diff_avg:+.1f}
- 进步最大科目：{top_improve[0]}（+{top_improve[1]:.1f}分）
- 退步最大科目：{top_decline[0]}（{top_decline[1]:.1f}分）

请生成报告。"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=800
    )
    return response.choices[0].message.content.strip()

def generate_trend_advice(student_name, exam_names, scores, trend_type, subject_name=None):
    """
    生成成绩趋势的AI分析建议
    :param student_name: 学生姓名
    :param exam_names: 考试名称列表（按时间顺序）
    :param scores: 对应的分数列表（总分或单科分数）
    :param trend_type: "总分趋势" 或 "单科趋势"
    :param subject_name: 如果是单科趋势，提供科目名
    """
    if len(scores) < 2:
        return "考试次数不足两次，无法分析趋势。"
    
    # 计算变化
    first_score = scores[0]
    last_score = scores[-1]
    change = last_score - first_score
    max_score = max(scores)
    min_score = min(scores)
    max_exam = exam_names[scores.index(max_score)]
    min_exam = exam_names[scores.index(min_score)]
    
    # 判断趋势（简单线性拟合）
    if change > 0:
        trend_desc = "整体呈上升趋势"
    elif change < 0:
        trend_desc = "整体呈下降趋势"
    else:
        trend_desc = "整体保持稳定"
    
    if trend_type == "总分趋势":
        prompt = f"""你是一名高中教师。学生{student_name}的历次考试总分变化如下：
考试顺序：{', '.join(exam_names)}
总分序列：{scores}
首次：{first_score:.0f}，末次：{last_score:.0f}，变化：{change:+.0f}分，最高{max_score:.0f}分（{max_exam}），最低{min_score:.0f}分（{min_exam}），{trend_desc}。

请用简短的2-3句话分析该学生的总分趋势，给出鼓励或提醒（例如：进步原因推测、是否需要重点突破某科目等）。要求语气亲切、实用，不超过80字。
"""
    else:  # 单科趋势
        prompt = f"""你是一名高中教师。学生{student_name}在《{subject_name}》科目的历次考试成绩变化如下：
考试顺序：{', '.join(exam_names)}
成绩序列：{scores}
首次：{first_score:.0f}，末次：{last_score:.0f}，变化：{change:+.0f}分，最高{max_score:.0f}分（{max_exam}），最低{min_score:.0f}分（{min_exam}），{trend_desc}。

请用简短的2-3句话分析该学生该科目的学习趋势，给出具体的学习建议（例如：巩固基础、专项练习、保持状态等）。不超过80字。
"""
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        advice = response.choices[0].message.content.strip()
        return advice
    except Exception as e:
        return f"AI分析生成失败：{str(e)}，请检查网络或API配置。"
    
def generate_class_report(df_pre_align, df_post_align, class_avg_pre, class_avg_post, avg_diff, common_subjects, exam_names=("前测", "后测")):
    """
    生成班级整体学情智能简报
    """
    # 提取关键指标
    total_avg_change = class_avg_post.sum() - class_avg_pre.sum()
    max_improve_subj = avg_diff.idxmax()
    max_improve_val = avg_diff.max()
    max_decline_subj = avg_diff.idxmin()
    max_decline_val = avg_diff.min()
    
    # 计算优秀率假设（≥80分为优秀）
    excellent_rate_pre = (df_pre_align >= 80).mean().mean() * 100
    excellent_rate_post = (df_post_align >= 80).mean().mean() * 100
    
    prompt = f"""你是一位资深教务主任。请根据以下班级两次考试的数据，撰写一份300字以内的班级学情简报，语气专业且具有建设性。内容包括：
- 整体成绩变化（总分均分变化{total_avg_change:+.1f}分，优秀率从{excellent_rate_pre:.1f}%变为{excellent_rate_post:.1f}%）
- 优势科目（{max_improve_subj}进步{max_improve_val:.1f}分）
- 待提高科目（{max_decline_subj}退步{max_decline_val:.1f}分）
- 给老师的2条具体教学建议

数据摘要：
{df_pre_align.mean().to_string()}
→
{df_post_align.mean().to_string()}
"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=600
    )
    return response.choices[0].message.content.strip()

def generate_class_report(df_pre_align, df_post_align, class_avg_pre, class_avg_post, avg_diff, common_subjects, exam_names=("前测", "后测")):
    """
    生成班级整体学情智能简报
    """
    # 提取关键指标
    total_avg_change = class_avg_post.sum() - class_avg_pre.sum()
    max_improve_subj = avg_diff.idxmax()
    max_improve_val = avg_diff.max()
    max_decline_subj = avg_diff.idxmin()
    max_decline_val = avg_diff.min()
    
    # 计算优秀率（≥80分视为优秀）
    excellent_rate_pre = (df_pre_align >= 80).mean().mean() * 100
    excellent_rate_post = (df_post_align >= 80).mean().mean() * 100
    
    prompt = f"""你是一位资深教务主任。请根据以下班级两次考试的数据，撰写一份300字以内的班级学情简报，语气专业且具有建设性。内容包括：
- 整体成绩变化（总分均分变化{total_avg_change:+.1f}分，优秀率从{excellent_rate_pre:.1f}%变为{excellent_rate_post:.1f}%）
- 优势科目（{max_improve_subj}进步{max_improve_val:.1f}分）
- 待提高科目（{max_decline_subj}退步{max_decline_val:.1f}分）
- 给老师的2条具体教学建议

数据摘要（平均分）：
{df_pre_align.mean().to_string()}
→
{df_post_align.mean().to_string()}
"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600
        )
        advice = response.choices[0].message.content.strip()
        return advice
    except Exception as e:
        return f"AI 生成简报失败：{str(e)}"
    
def generate_college_recommendation(student_name, subjects_selected, total_score, rank_percent=None, subject_type='物理'):
    """
    基于位次(省排名)或分数的高考志愿推荐
    :param student_name: 学生姓名
    :param subjects_selected: 选科组合 {'首选': '物理'或'历史', '再选': ['化学','生物']}
    :param total_score: 赋分后总分
    :param rank_percent: 若已知排名百分比(0~1)，则优先使用（推荐），否则根据分数和subject_type估算位次
    :param subject_type: '物理' 或 '历史'，决定使用哪一套一分一段表及推荐规则
    """
    # ========== 1. 确定位次和排名百分比 ==========
    if rank_percent is not None:
        # 有真实的省排名百分比（来自年级/联考数据）
        rank_percent_used = max(0.0, min(1.0, rank_percent))
        if subject_type == '物理':
            total_students = 173282  # 物理类总人数（根据一分一段表）
        else:
            total_students = 100000  # 历史类估算人数（可后续用真实数据替换）
        rank = int(rank_percent_used * total_students)
    else:
        # 没有省排名，降级使用分数估算位次（仅后备）
        from utils.rank_utils import get_rank_from_score
        rank = get_rank_from_score(total_score, subject_type)
        if subject_type == '物理':
            total_students = 173282
        else:
            total_students = 100000
        rank_percent_used = rank / total_students if total_students > 0 else 0.5

    # ========== 2. 基于位次/分数的院校层次推荐（物理/历史区分） ==========
    if subject_type == '物理':
        # 物理类推荐规则（基于位次百分比）
        if rank_percent_used <= 0.02:       # 前2%
            level = "顶尖院校 (C9/985)"
            suggestion = "冲刺清北复交等国内顶尖高校"
        elif rank_percent_used <= 0.05:     # 2%-5%
            level = "中上游985高校"
            suggestion = "重点考虑985高校及热门211"
        elif rank_percent_used <= 0.10:     # 5%-10%
            level = "普通985/强211"
            suggestion = "可报考大多数211及部分985"
        elif rank_percent_used <= 0.20:     # 10%-20%
            level = "优质一本院校 (211/双一流)"
            suggestion = "重点关注省内外211高校及优势学科"
        elif rank_percent_used <= 0.35:     # 20%-35%
            level = "普通一本院校"
            suggestion = "可考虑省属重点大学及特色专业"
        elif rank_percent_used <= 0.50:     # 35%-50%
            level = "二本院校"
            suggestion = "可报考公办二本及热门民办"
        elif rank_percent_used <= 0.70:     # 50%-70%
            level = "民办本科/独立学院"
            suggestion = "建议关注校企合作专业，以就业为导向"
        else:
            level = "高职专科院校"
            suggestion = "可考虑高职专科院校，关注技能型专业"
    else:  # 历史类
        if rank_percent_used <= 0.01:
            level = "顶尖院校 (C9/985)"
            suggestion = "冲刺顶尖高校"
        elif rank_percent_used <= 0.03:
            level = "985/211高校"
            suggestion = "重点考虑985及211大学"
        elif rank_percent_used <= 0.08:
            level = "优质一本"
            suggestion = "可报考多数一本院校"
        elif rank_percent_used <= 0.20:
            level = "普通一本/优质二本"
            suggestion = "重点关注省属重点大学"
        elif rank_percent_used <= 0.40:
            level = "二本院校"
            suggestion = "可报考公办二本"
        elif rank_percent_used <= 0.65:
            level = "民办本科"
            suggestion = "建议关注应用型专业"
        else:
            level = "高职专科院校"
            suggestion = "可考虑高职专科"

    # ========== 3. 根据选科组合推荐专业方向 ==========
    first_subject = subjects_selected.get('首选', '')
    second_subjects = subjects_selected.get('再选', [])

    if first_subject == '物理':
        if '化学' in second_subjects and '生物' in second_subjects:
            majors = "临床医学、口腔医学、药学、生物工程、食品科学与工程"
        elif '化学' in second_subjects:
            majors = "计算机科学、电子信息、材料科学、化学工程、环境工程"
        elif '生物' in second_subjects:
            majors = "生物技术、环境科学、心理学、体育科学"
        elif '政治' in second_subjects:
            majors = "法学、公共管理、思想政治教育、公安学类"
        elif '地理' in second_subjects:
            majors = "地理科学、城乡规划、测绘工程、地质工程"
        else:
            majors = "数学、物理学、机械工程、自动化、土木工程"
    else:  # 历史组
        if '政治' in second_subjects and '地理' in second_subjects:
            majors = "汉语言文学、法学、新闻传播学、公共管理、思想政治教育"
        elif '政治' in second_subjects:
            majors = "法学、政治学、社会学、哲学、马克思主义理论"
        elif '地理' in second_subjects:
            majors = "历史学、地理科学、旅游管理、文化遗产"
        else:
            majors = "语言文学类、历史学、哲学、教育学"

    # ========== 4. 调用AI生成自然语言建议 ==========
    prompt = f"""你是一名高考志愿指导专家。学生{student_name}的赋分后总分{total_score:.0f}分，省排名约{rank}（前{rank_percent_used*100:.1f}%）。选科组合为：首选{first_subject}，再选{', '.join(second_subjects)}。

根据该选科组合和位次，请用2-3句话给出报考建议：
- 分数对应院校层次：{level}（{suggestion}）
- 该选科组合适合的专业方向：{majors}
- 提醒学生注意：报考时需查阅各校招生章程，确认选科要求是否匹配。

请以亲切、鼓励的语气回答，不超过120字。
"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        advice = response.choices[0].message.content.strip()
        return advice, level, majors
    except Exception as e:
        return f"AI志愿推荐生成失败：{str(e)}", level, majors