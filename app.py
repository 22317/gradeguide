import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils.data_loader import load_scores, get_class_summary
from utils.radar_chart import draw_radar_chart, draw_comparison_radar
from utils.ai_advice import generate_personal_advice, generate_comparison_advice, generate_trend_advice
from utils.ai_advice import generate_personal_advice, generate_comparison_advice, generate_trend_advice, generate_class_report
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os


st.set_page_config(page_title="GradeGuide 学情分析系统", layout="wide", initial_sidebar_state="collapsed")



# 获取字体文件的绝对路径
font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'NotoSansCJKsc-Regular.otf')

if os.path.exists(font_path):
    # 添加字体到 matplotlib 字体管理器
    fm.fontManager.addfont(font_path)
    # 获取字体属性并设置为默认字体
    prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False
else:
    # 后备方案：使用系统可能存在的字体
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

# ========== 初始化启动状态 ==========
if "started" not in st.session_state:
    st.session_state.started = False


# ========== 启动页 ==========
if not st.session_state.started:
    st.markdown("""
    <style>
        /* 设置启动页整体背景与导航栏一致 */
        .stApp {
            background: linear-gradient(135deg, #e0f2e9 0%, #c8e6df 100%);
        }
        /* 顶部导航栏颜色融合 */
        header[data-testid="stHeader"] {
            background: linear-gradient(135deg, #e0f2e9 0%, #c8e6df 100%) !important;
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }
        header[data-testid="stHeader"] button {
            color: #2c3e50 !important;
            background-color: transparent !important;
        }
        .big-title {
            font-size: 70px;
            font-weight: bold;
            text-align: center;
            color: #4CAF50;
            margin-top: 15%;
        }
        .sub {
            text-align: center;
            font-size: 24px;
            color: #555;
            margin-bottom: 40px;
        }
        /* 按钮改为马卡龙淡黄色 */
        .stButton button {
            background-color: #FFF5CC;
            color: #5d5a3c;
            font-size: 20px;
            border-radius: 50px;
            padding: 10px 24px;
            width: 100%;
            border: none;
            font-weight: 600;
        }
        .stButton button:hover {
            background-color: #FFEAA7;
            color: #3d3a2c;
        }
    </style>
    <div class="big-title">✨ GradeGuide ✨</div>
    <div class="sub">AI驱动的智能学情分析系统</div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 开始探索", use_container_width=True):
            st.session_state.started = True
            st.rerun()
    st.stop()

# ========== 主界面代码（以下为您的原有功能） ==========
st.markdown("""
<style>
    /* 顶部导航栏颜色融合（与页面背景一致） */
    header[data-testid="stHeader"] {
        background: linear-gradient(135deg, #e0f2e9 0%, #c8e6df 100%) !important;
        border-bottom: 1px solid rgba(0,0,0,0.05);
    }
    header[data-testid="stHeader"] button {
        color: #2c3e50 !important;
        background-color: transparent !important;
    }

    /* 全局背景与字体 */
    .stApp {
        background: linear-gradient(135deg, #e0f2e9 0%, #c8e6df 100%);
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }
    
    /* 主容器：居中并限制最大宽度，精致留白 */
    .block-container {
        max-width: 1400px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        margin: 0 auto;
    }
    
    /* 标题样式 */
    h1 {
        color: #2c3e50;
        font-weight: 700;
        border-left: 8px solid #4CAF50;
        padding-left: 20px;
        margin-bottom: 0.5rem;
    }
    .stMarkdown p {
        color: #4a5568;
    }
    
    /* 卡片式布局 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(255,255,255,0.6);
        border-radius: 16px;
        padding: 8px 16px;
        backdrop-filter: blur(4px);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 20px;
        padding: 6px 20px;
        font-weight: 600;
        color: #2c3e50;
        transition: 0.2s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e2e8f0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
    
    /* 表格美化 */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        font-size: 14px;
    }
    .dataframe th {
        background-color: #f1f5f9 !important;
        font-weight: 600;
    }
    .dataframe td {
        background-color: white;
    }
    
    /* 按钮悬浮效果 */
    div.stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 40px;
        border: none;
        padding: 8px 20px;
        font-weight: 600;
        transition: 0.2s;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover {
        background-color: #388e3c;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    
    /* 指标卡片美化 */
    div[data-testid="stMetric"] {
        background-color: white;
        border-radius: 20px;
        padding: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    
    /* info 框 */
    .stAlert {
        border-radius: 16px;
        background-color: #f0f9ff;
        border-left: 6px solid #4CAF50;
    }
    
    /* 图表容器透明 */
    .stImage, .stPlotlyChart, .stPyplot {
        background: transparent;
    }
    
    /* 底部版权 */
    footer {
        visibility: visible;
        font-size: 12px;
        color: #94a3b8;
    }
    
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)


st.title("📊 GradeGuide：AI学情分析与个性化建议生成器")
st.markdown("欢迎使用！！更多功能敬请期待。")

tab1, tab2, tab3, tab4 = st.tabs(["📈 单次成绩分析", "🔄 两次考试对比分析", "📈 多次考试趋势分析", "🎯 高考赋分模拟与选科分析"])

# ==================== 选项卡1：单次分析 ====================
with tab1:
    uploaded_file = st.file_uploader("上传Excel成绩表", type=["xlsx"], key="single")
    if uploaded_file is not None:
        df = load_scores(uploaded_file)
        st.success(f"成功加载 {df.shape[0]} 名学生，{df.shape[1]-1} 个科目/知识点")
        
        with st.expander("预览成绩数据"):
            st.dataframe(df.head())
        
        class_summary, score_cols = get_class_summary(df)
        class_means = {col: class_summary[col]['mean'] for col in score_cols}
        
        st.subheader("📈 班级整体学情")
        col_left, col_right = st.columns([1, 1.5])
        with col_left:
            fig_class = draw_radar_chart(class_means, class_means, score_cols, "班级平均")
            st.pyplot(fig_class, use_container_width=True)
        with col_right:
            stats_data = []
            for col in score_cols:
                stats_data.append({
                    "科目": col,
                    "平均分": f"{df[col].mean():.1f}",
                    "最高分": f"{df[col].max():.0f}",
                    "最低分": f"{df[col].min():.0f}",
                    "标准差": f"{df[col].std():.1f}"
                })
            stats_df = pd.DataFrame(stats_data)
            st.dataframe(stats_df, use_container_width=True)
            st.caption(f"班级总人数：{df.shape[0]} 人")
        
        student_names = df.iloc[:, 0].tolist()
        selected_student = st.selectbox("选择学生查看详细分析", student_names, key="single_select")
        if selected_student:
            student_row = df[df.iloc[:, 0] == selected_student].iloc[0]
            student_scores = {col: student_row[col] for col in score_cols}
            col1, col2 = st.columns([1, 1])
            with col1:
                st.subheader(f"📌 {selected_student} 的雷达图")
                fig = draw_radar_chart(student_scores, class_means, score_cols, selected_student)
                st.pyplot(fig)
            with col2:
                st.subheader("🤖 AI 个性化建议")
                with st.spinner("AI 正在生成建议..."):
                    advice = generate_personal_advice(selected_student, student_scores, class_means)
                st.info(advice)
                st.subheader("📊 分数对比")
                comp_df = pd.DataFrame({
                    "科目": score_cols,
                    "学生分数": [student_scores[col] for col in score_cols],
                    "班级平均": [class_means[col] for col in score_cols]
                })
                st.dataframe(comp_df)
                # 总分分析
                if '总分' in df.columns:
                    student_total = student_row['总分']
                    class_total_avg = df['总分'].mean()
                else:
                    score_cols_for_total = [c for c in score_cols if c != '总分']
                    student_total = sum(student_scores[c] for c in score_cols_for_total)
                    class_total_avg = df[score_cols_for_total].sum(axis=1).mean()
                col_total1, col_total2 = st.columns(2)
                col_total1.metric("学生总分", f"{student_total:.1f}")
                col_total2.metric("班级总分平均", f"{class_total_avg:.1f}", delta=f"{student_total - class_total_avg:+.1f}")
        
        if st.button("🔽 批量生成所有学生建议并导出", key="single_export"):
            all_advice = []
            for _, row in df.iterrows():
                s_name = row.iloc[0]
                s_scores = {col: row[col] for col in score_cols}
                adv = generate_personal_advice(s_name, s_scores, class_means)
                all_advice.append({"学生": s_name, "个性化建议": adv})
            advice_df = pd.DataFrame(all_advice)
            st.download_button("下载CSV", advice_df.to_csv(index=False), "student_advice.csv")

# ==================== 选项卡2：两次考试对比分析 ====================
with tab2:
    st.markdown("请上传**前测**（第一次考试）和**后测**（第二次考试）两个Excel文件。")
    st.caption("要求：两个文件中的学生姓名和科目列必须一致（缺失的学生会自动标记）。")
    col_pre, col_post = st.columns(2)
    with col_pre:
        pre_file = st.file_uploader("上传前测成绩表", type=["xlsx"], key="pre")
    with col_post:
        post_file = st.file_uploader("上传后测成绩表", type=["xlsx"], key="post")
    if pre_file and post_file:
        df_pre = load_scores(pre_file)
        df_post = load_scores(post_file)
        name_col = df_pre.columns[0]
        pre_subjects = df_pre.columns[1:].tolist()
        post_subjects = df_post.columns[1:].tolist()
        common_subjects = list(set(pre_subjects) & set(post_subjects))
        common_subjects = [s for s in common_subjects if s != '总分']
        if not common_subjects:
            st.error("两个文件中没有相同的科目列名，无法对比。")
        else:
            st.success(f"对比科目：{', '.join(common_subjects)}")
            df_pre_align = df_pre[[name_col] + common_subjects].set_index(name_col)
            df_post_align = df_post[[name_col] + common_subjects].set_index(name_col)
            common_students = df_pre_align.index.intersection(df_post_align.index)
            if len(common_students) == 0:
                st.error("两个文件中没有相同的学生姓名，无法对比。")
            else:
                df_pre_align = df_pre_align.loc[common_students]
                df_post_align = df_post_align.loc[common_students]
                st.subheader("📊 班级整体进退步情况")
                class_avg_pre = df_pre_align.mean()
                class_avg_post = df_post_align.mean()
                avg_diff = class_avg_post - class_avg_pre
                summary_df = pd.DataFrame({
                    "前测平均": class_avg_pre,
                    "后测平均": class_avg_post,
                    "差值": avg_diff
                })
                st.dataframe(summary_df.style.format("{:.1f}"))
                
                if st.button("🤖 生成班级学情简报", key="class_report"):
                    with st.spinner("AI 正在分析班级数据并撰写简报..."):
                        report_text = generate_class_report(df_pre_align, df_post_align, class_avg_pre, class_avg_post, avg_diff, common_subjects)
                        st.info(report_text)
                        st.download_button("下载简报", report_text, "班级学情简报.txt")

                # 总分对比分析
                st.markdown("### 📊 总分变化分析")
                def get_total_scores(df, score_cols):
                    if '总分' in df.columns:
                        return df['总分']
                    else:
                        return df[score_cols].sum(axis=1)
                pre_total = get_total_scores(df_pre_align, common_subjects)
                post_total = get_total_scores(df_post_align, common_subjects)
                total_diff = post_total - pre_total
                total_avg_pre = pre_total.mean()
                total_avg_post = post_total.mean()
                total_avg_diff = total_avg_post - total_avg_pre
                col1, col2, col3 = st.columns(3)
                col1.metric("前测总分平均", f"{total_avg_pre:.1f}")
                col2.metric("后测总分平均", f"{total_avg_post:.1f}", delta=f"{total_avg_diff:+.1f}")
                col3.metric("班级总分变化范围", f"{total_diff.min():+.0f} ~ {total_diff.max():+.0f}")
                change_df_total = pd.DataFrame({
                    "学生": pre_total.index,
                    "前测总分": pre_total.values,
                    "后测总分": post_total.values,
                    "总分变化": total_diff.values
                }).sort_values("总分变化", ascending=False)
                st.markdown("**总分进步最多前5名**")
                st.dataframe(change_df_total.head(5).style.format({"前测总分": "{:.0f}", "后测总分": "{:.0f}", "总分变化": "{:+.0f}"}))
                st.markdown("**总分退步最多前5名**")
                st.dataframe(change_df_total.tail(5).sort_values("总分变化").style.format({"前测总分": "{:.0f}", "后测总分": "{:.0f}", "总分变化": "{:+.0f}"}))
                
                # 班级报告一键生成
                st.markdown("---")
                if st.button("📄 一键生成班级报告", key="gen_report"):
                    total_pre_avg = class_avg_pre.sum()
                    total_post_avg = class_avg_post.sum()
                    total_avg_diff = total_post_avg - total_pre_avg
                    max_improve_subj = avg_diff.idxmax()
                    max_improve_val = avg_diff.max()
                    max_decline_subj = avg_diff.idxmin()
                    max_decline_val = avg_diff.min()
                    pre_sum = get_total_scores(df_pre_align, common_subjects)
                    post_sum = get_total_scores(df_post_align, common_subjects)
                    total_change = post_sum - pre_sum
                    change_df = pd.DataFrame({
                        "学生": pre_sum.index,
                        "前测总分": pre_sum.values,
                        "后测总分": post_sum.values,
                        "总分变化": total_change.values
                    }).sort_values("总分变化", ascending=False)
                    top_improve_students = change_df.head(3)
                    top_decline_students = change_df.tail(3)
                    std_pre = df_pre_align.std()
                    std_post = df_post_align.std()
                    report = f"""
### 📋 班级对比分析报告

**整体成绩变化**  
- 班级总分平均分变化：{total_avg_diff:+.1f} 分（前测总分均值 {total_pre_avg:.1f} → 后测 {total_post_avg:.1f}）

**科目进退步**  
- 进步最大科目：{max_improve_subj}（+{max_improve_val:.1f} 分）
- 退步最多科目：{max_decline_subj}（{max_decline_val:.1f} 分）

**学生总分变化 TOP3**  
- 进步最多：
{top_improve_students.to_string(index=False, columns=["学生", "总分变化"], formatters={"总分变化": "{:+.0f}".format})}

- 退步最多：
{top_decline_students.to_string(index=False, columns=["学生", "总分变化"], formatters={"总分变化": "{:+.0f}".format})}

**班级分化情况（标准差）**  
- 前测分化最大学科：{std_pre.idxmax()}（标准差 {std_pre.max():.1f}）
- 后测分化最大学科：{std_post.idxmax()}（标准差 {std_post.max():.1f}）

> 报告由 GradeGuide 自动生成，可结合雷达图进行个性化辅导。
"""
                    st.markdown(report)
                    st.download_button(
                        label="⬇️ 下载报告为 Markdown 文件",
                        data=report,
                        file_name="班级报告.md",
                        mime="text/markdown"
                    )
                
                # 学生个体对比
                student_list = list(common_students)
                selected_student = st.selectbox("选择学生查看详细对比分析", student_list, key="compare_select")
                if selected_student:
                    pre_scores = df_pre_align.loc[selected_student].to_dict()
                    post_scores = df_post_align.loc[selected_student].to_dict()
                    diff_scores = {subj: post_scores[subj] - pre_scores[subj] for subj in common_subjects}
                    total_pre = sum(pre_scores.values())
                    total_post = sum(post_scores.values())
                    total_diff = total_post - total_pre
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("📈 各科成绩对比")
                        compare_table = pd.DataFrame({
                            "科目": common_subjects,
                            "前测": [pre_scores[subj] for subj in common_subjects],
                            "后测": [post_scores[subj] for subj in common_subjects],
                            "进退步": [diff_scores[subj] for subj in common_subjects]
                        })
                        st.dataframe(compare_table.style.format({"前测": "{:.0f}", "后测": "{:.0f}", "进退步": "{:+.0f}"}))
                        st.metric("总分变化", f"{total_post:.0f}", delta=f"{total_diff:+.0f}")
                    with col2:
                        st.subheader("📊 进退步雷达图")
                        fig_compare = draw_comparison_radar(pre_scores, post_scores, common_subjects, selected_student)
                        st.pyplot(fig_compare)
                    st.subheader("🤖 AI 对比分析建议")
                    with st.spinner("AI 正在分析进退步情况..."):
                        advice_compare = generate_comparison_advice(
                            selected_student, pre_scores, post_scores, diff_scores, total_diff,
                            class_avg_pre.to_dict(), class_avg_post.to_dict()
                        )
                    st.info(advice_compare)
                
                if st.button("🔽 批量生成所有学生对比建议并导出", key="compare_export"):
                    all_compare_advice = []
                    for student in common_students:
                        pre = df_pre_align.loc[student].to_dict()
                        post = df_post_align.loc[student].to_dict()
                        diff = {subj: post[subj] - pre[subj] for subj in common_subjects}
                        total_diff = sum(diff.values())
                        adv = generate_comparison_advice(
                            student, pre, post, diff, total_diff,
                            class_avg_pre.to_dict(), class_avg_post.to_dict()
                        )
                        all_compare_advice.append({"学生": student, "对比分析建议": adv})
                    advice_df = pd.DataFrame(all_compare_advice)
                    st.download_button("下载对比建议CSV", advice_df.to_csv(index=False), "comparison_advice.csv")

# ==================== 选项卡3：多次考试趋势分析 ====================
with tab3:
    st.markdown("### 上传多次考试成绩（每次考试一个Excel文件）")
    st.caption("请按照考试时间顺序依次上传文件（文件名将作为考试名称）。建议每个文件大小不超过2MB。")
    if "exam_files" not in st.session_state:
        st.session_state.exam_files = []
    uploaded_file = st.file_uploader("选择一个Excel文件", type=["xlsx"], key="trend_upload")
    col_btn1, _ = st.columns([1, 5])
    with col_btn1:
        add_clicked = st.button("➕ 添加此文件")
    if add_clicked and uploaded_file is not None:
        with st.spinner("正在读取文件..."):
            df = load_scores(uploaded_file)
            exam_name = uploaded_file.name.replace('.xlsx', '').replace('.xls', '')
            if exam_name not in [exam["name"] for exam in st.session_state.exam_files]:
                st.session_state.exam_files.append({"name": exam_name, "data": df})
                st.success(f"已添加考试：{exam_name}")
                st.rerun()
            else:
                st.warning(f"考试 '{exam_name}' 已存在，请勿重复添加。")
    if st.session_state.exam_files:
        st.subheader("已上传的考试（按时间顺序）")
        for i, exam in enumerate(st.session_state.exam_files):
            cols = st.columns([6, 1, 1])
            with cols[0]:
                st.markdown(f"<small>{i+1}. {exam['name']} ({exam['data'].shape[0]}人, {exam['data'].shape[1]-1}科)</small>", unsafe_allow_html=True)
            with cols[1]:
                if st.button("↑", key=f"trend_up_{i}", help="上移"):
                    if i > 0:
                        st.session_state.exam_files[i], st.session_state.exam_files[i-1] = st.session_state.exam_files[i-1], st.session_state.exam_files[i]
                        st.rerun()
            with cols[2]:
                if st.button("✖", key=f"trend_del_{i}", help="删除"):
                    st.session_state.exam_files.pop(i)
                    st.rerun()
        if len(st.session_state.exam_files) >= 2:
            @st.cache_data(ttl=3600)
            def get_common_info(exams):
                student_sets = [set(exam["data"].iloc[:, 0].tolist()) for exam in exams]
                common_students = sorted(list(set.intersection(*student_sets)))
                subject_sets = [set(exam["data"].columns[1:]) for exam in exams]
                common_subjects = list(set.intersection(*subject_sets))
                common_subjects = [s for s in common_subjects if s != '总分']
                exam_names = [exam["name"] for exam in exams]
                return common_students, common_subjects, exam_names
            common_students, common_subjects, exam_names = get_common_info(st.session_state.exam_files)
            if not common_students:
                st.error("不同考试中没有相同的学生，无法分析趋势。")
            elif not common_subjects and not any('总分' in exam["data"].columns for exam in st.session_state.exam_files):
                st.warning("没有共同的科目，且缺少总分列，无法分析。")
            else:
                @st.cache_data(ttl=3600)
                def build_student_scores(exams, common_students, common_subjects):
                    total_scores = {stu: [] for stu in common_students}
                    subject_scores = {stu: {subj: [] for subj in common_subjects} for stu in common_students}
                    for exam in exams:
                        data = exam["data"]
                        name_col = data.columns[0]
                        df_indexed = data.set_index(name_col)
                        for stu in common_students:
                            if stu in df_indexed.index:
                                row = df_indexed.loc[stu]
                                if '总分' in data.columns:
                                    total_scores[stu].append(row['总分'])
                                else:
                                    total_scores[stu].append(row[common_subjects].sum())
                                for subj in common_subjects:
                                    subject_scores[stu][subj].append(row[subj])
                            else:
                                total_scores[stu].append(None)
                                for subj in common_subjects:
                                    subject_scores[stu][subj].append(None)
                    return total_scores, subject_scores
                with st.spinner("正在分析历次考试数据..."):
                    total_scores, subject_scores = build_student_scores(st.session_state.exam_files, common_students, common_subjects)
                st.success("数据准备完成")
                trend_type = st.radio("分析类型", ["总分趋势", "单科趋势"], horizontal=True)
                if trend_type == "总分趋势":
                    selected_student = st.selectbox("选择学生", common_students, key="trend_total_stu")
                    if selected_student:
                        scores = total_scores[selected_student]
                        valid = [(exam_names[i], scores[i]) for i in range(len(exam_names)) if scores[i] is not None]
                        if valid:
                            names, vals = zip(*valid)
                            left, right = st.columns([1.2, 1])
                            with left:
                                fig, ax = plt.subplots(figsize=(4, 2.5))
                                ax.plot(names, vals, marker='o', linewidth=2)
                                ax.set_title(f"{selected_student} 总分变化趋势")
                                ax.set_xlabel("考试")
                                ax.set_ylabel("总分")
                                plt.xticks(rotation=45, ha='right')
                                ax.grid(True, linestyle='--', alpha=0.6)
                                st.pyplot(fig, use_container_width=True)
                            with right:
                                st.subheader("🤖 趋势解读")
                                with st.spinner("AI 分析中..."):
                                    advice = generate_trend_advice(selected_student, names, list(vals), "总分趋势")
                                st.info(advice)
                            st.markdown("---")
                            st.markdown("#### 多学生总分对比")
                            compare_students = st.multiselect("选择多个学生", common_students, default=common_students[:2])
                            if compare_students:
                                fig_multi, ax_multi = plt.subplots(figsize=(6, 3))
                                for stu in compare_students:
                                    s_vals = total_scores[stu]
                                    valid2 = [(exam_names[i], s_vals[i]) for i in range(len(exam_names)) if s_vals[i] is not None]
                                    if valid2:
                                        n2, v2 = zip(*valid2)
                                        ax_multi.plot(n2, v2, marker='o', label=stu)
                                ax_multi.legend()
                                ax_multi.set_title("总分趋势对比")
                                ax_multi.set_xlabel("考试")
                                ax_multi.set_ylabel("总分")
                                plt.xticks(rotation=45)
                                ax_multi.grid(True)
                                st.pyplot(fig_multi, use_container_width=True)
                        else:
                            st.warning("该学生在部分考试中无有效总分数据。")
                else:
                    if not common_subjects:
                        st.warning("没有共同科目，无法分析单科趋势。")
                    else:
                        selected_subject = st.selectbox("选择科目", common_subjects)
                        selected_student = st.selectbox("选择学生", common_students, key="trend_subj_stu")
                        if selected_student and selected_subject:
                            scores = subject_scores[selected_student][selected_subject]
                            valid = [(exam_names[i], scores[i]) for i in range(len(exam_names)) if scores[i] is not None]
                            if valid:
                                names, vals = zip(*valid)
                                left, right = st.columns([1.2, 1])
                                with left:
                                    fig, ax = plt.subplots(figsize=(5, 3.5))
                                    ax.plot(names, vals, marker='o', linewidth=2, color='green')
                                    ax.set_title(f"{selected_student} - {selected_subject} 成绩变化")
                                    ax.set_xlabel("考试")
                                    ax.set_ylabel("分数")
                                    plt.xticks(rotation=45, ha='right')
                                    ax.grid(True)
                                    st.pyplot(fig, use_container_width=True)
                                with right:
                                    st.subheader("🤖 趋势解读")
                                    with st.spinner("AI 分析中..."):
                                        advice = generate_trend_advice(selected_student, names, list(vals), "单科趋势", selected_subject)
                                    st.info(advice)
                                st.markdown("---")
                                st.markdown("#### 多学生单科对比")
                                compare_students = st.multiselect("选择多个学生", common_students, default=common_students[:2])
                                if compare_students:
                                    fig_multi, ax_multi = plt.subplots(figsize=(8, 4))
                                    for stu in compare_students:
                                        s_vals = subject_scores[stu][selected_subject]
                                        valid2 = [(exam_names[i], s_vals[i]) for i in range(len(exam_names)) if s_vals[i] is not None]
                                        if valid2:
                                            n2, v2 = zip(*valid2)
                                            ax_multi.plot(n2, v2, marker='o', label=stu)
                                    ax_multi.legend()
                                    ax_multi.set_title(f"{selected_subject} 成绩对比")
                                    ax_multi.set_xlabel("考试")
                                    ax_multi.set_ylabel("分数")
                                    plt.xticks(rotation=45)
                                    ax_multi.grid(True)
                                    st.pyplot(fig_multi, use_container_width=True)
                            else:
                                st.warning("该学生在此科目上没有有效成绩。")
        else:
            st.info("请至少上传2次考试成绩，以便查看趋势。")
    else:
        st.info("点击「选择一个Excel文件」并点击「添加此文件」按钮上传考试成绩。")


# ==================== 选项卡4：高考赋分模拟与选科分析 ====================
with tab4:
    st.markdown("## 🎯 高考赋分模拟与选科分析")
    st.markdown("""
    **根据云南省新高考“3+1+2”模式**，再选科目（化学、地理、思想政治、生物学）实行等级赋分。
    
    本功能需要上传两个成绩表：
    1. **班级成绩表**：班级学生的各科成绩（含语数外、物理/历史、再选科目）
    2. **年级/联考成绩表**：该次考试全体学生的成绩（用于确定各等级的原始分区间和排名）
    
    系统自动识别再选科目，一次性完成所有赋分计算，并基于**年级排名**提供AI选科分析与志愿参考。
    """)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        class_file = st.file_uploader("📁 上传班级成绩表", type=["xlsx"], key="yunnan_class")
        if class_file is not None:
            class_df = load_scores(class_file)
            st.success(f"班级数据：{class_df.shape[0]} 名学生，{class_df.shape[1]-1} 个科目")
            with st.expander("预览班级数据"):
                st.dataframe(class_df.head())
    
    with col_right:
        grade_file = st.file_uploader("📁 上传年级/联考成绩表", type=["xlsx"], key="yunnan_grade")
        if grade_file is not None:
            grade_df = load_scores(grade_file)
            st.success(f"年级数据：{grade_df.shape[0]} 名学生，{grade_df.shape[1]-1} 个科目")
            with st.expander("预览年级数据"):
                st.dataframe(grade_df.head())
    
    if class_file is not None and grade_file is not None:
        from utils.grade_converter import auto_detect_reelect_subjects, calculate_converted_grades, calculate_total_scores
        
        reelected_subjects = auto_detect_reelect_subjects(class_df)
        if not reelected_subjects:
            st.error("❌ 未能从班级表中识别出再选科目（化学、地理、思想政治、生物学）。请检查列名是否包含这些关键词。")
        else:
            st.success(f"✅ 自动识别再选科目：{', '.join(reelected_subjects)}")
            
            if st.button("🚀 开始模拟赋分", key="yunnan_calc", use_container_width=True):
                with st.spinner("正在计算赋分成绩..."):
                    result_df, detected_subjects = calculate_converted_grades(class_df, grade_df, reelected_subjects)
                    result_df = calculate_total_scores(result_df, detected_subjects)
                    
                    st.session_state.yunnan_result = result_df
                    st.session_state.yunnan_reelected = detected_subjects
                    st.session_state.yunnan_grade_df = grade_df
                
                st.success("✅ 赋分计算完成！")
                st.balloons()
    
    if st.session_state.get("yunnan_result") is not None:
        result_df = st.session_state.yunnan_result
        reelected = st.session_state.yunnan_reelected
        grade_df = st.session_state.get("yunnan_grade_df")
        
        st.subheader("📊 赋分结果预览")
        st.dataframe(result_df, use_container_width=True)
        
        # 分数变化对比
        st.subheader("📈 赋分前后平均分变化")
        change_data = []
        for subject in reelected:
            if f'{subject}_赋分' in result_df.columns:
                orig_mean = result_df[subject].mean()
                conv_mean = result_df[f'{subject}_赋分'].mean()
                change_data.append({
                    "科目": subject,
                    "原始平均分": f"{orig_mean:.1f}",
                    "赋分平均分": f"{conv_mean:.1f}",
                    "变化": f"{conv_mean - orig_mean:+.1f}"
                })
        if change_data:
            st.dataframe(pd.DataFrame(change_data), use_container_width=True)
        
        # 总分统计
        if '赋分后总分' in result_df.columns:
            st.subheader("💯 赋分后总分统计")
            total_stats = result_df['赋分后总分'].describe()
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("平均总分", f"{total_stats['mean']:.1f}")
            col2.metric("最高总分", f"{total_stats['max']:.0f}")
            col3.metric("最低总分", f"{total_stats['min']:.0f}")
            col4.metric("标准差", f"{total_stats['std']:.1f}")
        
        # 导出
        st.subheader("💾 导出结果")
        csv = result_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下载赋分成绩表 (CSV)",
            data=csv,
            file_name="高考赋分模拟成绩表.csv",
            mime="text/csv",
            key="yunnan_download"
        )
        
        # ========== AI 选科分析与志愿参考 ==========
        st.subheader("🎯 AI 选科分析与志愿参考")
        
        name_col = result_df.columns[0]
        student_names = result_df[name_col].tolist()
        selected_student_rec = st.selectbox("选择学生", student_names, key="yunnan_student_rec")
        
        if selected_student_rec:
            student_row = result_df[result_df[name_col] == selected_student_rec].iloc[0]
            total_score = student_row.get('赋分后总分', 0)
            
            # 计算年级排名（如果尚未计算）
            if grade_df is not None and 'grade_ranks' not in st.session_state:
                with st.spinner("正在计算年级排名..."):
                    from utils.grade_converter import calculate_grade_rank_for_class
                    reelected_grade = auto_detect_reelect_subjects(grade_df)
                    if reelected_grade:
                        grade_df_converted, _ = calculate_converted_grades(grade_df, grade_df, reelected_grade)
                        grade_df_converted = calculate_total_scores(grade_df_converted, reelected_grade)
                        grade_ranks = calculate_grade_rank_for_class(grade_df_converted, result_df, '赋分后总分')
                        st.session_state.grade_ranks = dict(zip(result_df[name_col].tolist(), grade_ranks))
                    else:
                        st.session_state.grade_ranks = {}
            
            grade_rank_percent = st.session_state.get('grade_ranks', {}).get(selected_student_rec, None)
            if grade_rank_percent is not None:
                rank_percent = grade_rank_percent
                rank_source = "年级/联考"
            else:
                df_rank = result_df.set_index(name_col)
                if '赋分后总分' in df_rank.columns:
                    rank = df_rank['赋分后总分'].rank(ascending=False).loc[selected_student_rec]
                    rank_percent = rank / len(df_rank)
                    rank_source = "班级"
                else:
                    rank_percent = 0.5
                    rank_source = "未知"
            
            # 自动识别选科组合
            first_subject = None
            if '物理' in result_df.columns and not pd.isna(student_row['物理']):
                first_subject = '物理'
            elif '历史' in result_df.columns and not pd.isna(student_row['历史']):
                first_subject = '历史'
            
            second_subjects = []
            for subj in reelected:
                if subj in result_df.columns and not pd.isna(student_row[subj]):
                    second_subjects.append(subj)
            
            if first_subject is None or len(second_subjects) != 2:
                st.warning(f"无法完整识别该学生的选科组合（首选：{first_subject}，再选：{second_subjects}）。请确保表格中包含物理/历史以及至少两门再选科目成绩。")
            else:
                st.info(f"**自动识别选科**：首选【{first_subject}】，再选【{', '.join(second_subjects)}】")
                st.info(f"**排名依据**：{rank_source}数据（排名百分位：{rank_percent*100:.1f}%）")
                
                if st.button("🤖 AI生成选科分析与志愿参考", key="yunnan_ai_rec_auto"):
                    from utils.ai_advice import generate_college_recommendation
                    with st.spinner("AI 正在分析数据并生成建议..."):
                        # 假设已有的 rank_percent 是从年级排名计算的
                        advice, level, majors = generate_college_recommendation(
                            selected_student_rec,
                            {'首选': first_subject, '再选': second_subjects},
                            total_score,
                            rank_percent=rank_percent,      # 注意参数名是 rank_percent
                            subject_type=first_subject
                        )
                    st.caption("📌 声明：以上分析基于云南省2025年高考一分一段表数据生成，院校层次推荐仅作参考，实际填报请结合当年招生计划和自身情况。一分一段表可替换为最新官方数据以更新分析结果。")
                    st.success(f"🎉 {selected_student_rec} 的选科分析")
                    st.info(f"**总分**：{total_score:.0f}分 | **{rank_source}排名**：前{rank_percent*100:.1f}%")
                    st.success(f"**推荐院校层次**：{level}")
                    st.info(f"**推荐专业方向**：{majors}")
                    st.markdown("---")
                    st.markdown(advice)
    
    # 规则说明折叠
    with st.expander("📖 云南新高考等级赋分规则说明"):
        st.markdown("""
        ### 赋分科目
        - **再选科目**：化学、地理、思想政治、生物学（4选2）
        - **原始分满分**：100分
        - **赋分后满分**：100分，起点30分
        
        ### 等级划分与赋分区间
        | 等级 | 人数占比 | 赋分区间 |
        |:---:|:---:|:---:|
        | A | 约 15% | 100～86 |
        | B | 约 35% | 85～71 |
        | C | 约 35% | 70～56 |
        | D | 约 13% | 55～41 |
        | E | 约 2% | 40～30 |
        
        ### 计算公式
        采用等比例转换公式：T = T₁ + (T₂ - T₁) × (Y - Y₁) / (Y₂ - Y₁)
        
        > 数据来源：云南省招生考试院发布的《云南省普通高中学业水平选择性考试科目等级赋分办法》
        """)