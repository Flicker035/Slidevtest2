import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Bar, Pie, Line, Funnel, Scatter, TreeMap, Radar
from pyecharts.commons.utils import JsCode
from streamlit_echarts import st_pyecharts
import re

# 设置页面配置
st.set_page_config(page_title="文章词频分析工具", layout="wide")

# 标题
st.title("📰 文章词频分析与可视化")

# ====== Sidebar 设置 ======
st.sidebar.header("⚙️ 控制面板")

# 用户输入 URL
url = st.sidebar.text_input("请输入文章 URL（建议中文网页）", value="https://example.com")

# 最小词频滑块
min_freq = st.sidebar.slider("最低词频阈值", min_value=1, max_value=20, value=2)

# 图表类型选择（至少7种）
chart_types = [
    "词云 (WordCloud)",
    "柱状图 (Bar)",
    "饼图 (Pie)",
    "折线图 (Line)",
    "漏斗图 (Funnel)",
    "散点图 (Scatter)",
    "矩形树图 (TreeMap)",
    "雷达图 (Radar)"
]
selected_chart = st.sidebar.selectbox("选择图表类型", chart_types)

# 是否显示前20词表格
show_table = st.sidebar.checkbox("显示词频前20表格", value=True)

# ====== 抓取与处理逻辑 ======
@st.cache_data(show_spinner="正在抓取并分析文章...")
def fetch_and_process(url, min_freq):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取正文（简单策略：去除 script/style）
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        text = re.sub(r'\s+', ' ', text).strip()

        if not text:
            return None, "无法提取有效文本内容"

        # 中文分词
        words = jieba.lcut(text)
        # 过滤：长度>1，非数字，非纯符号
        filtered_words = [
            w for w in words
            if len(w) > 1 and not w.isdigit() and re.search(r'[\u4e00-\u9fa5]', w)
        ]

        # 统计词频
        counter = Counter(filtered_words)
        # 过滤低频词
        filtered_counter = {k: v for k, v in counter.items() if v >= min_freq}
        return filtered_counter, None
    except Exception as e:
        return None, str(e)

# ====== 主逻辑 ======
if url:
    word_freq, error = fetch_and_process(url, min_freq)
    
    if error:
        st.error(f"❌ 错误：{error}")
    elif word_freq:
        # 获取前20高频词
        top20 = Counter(word_freq).most_common(20)
        df_top20 = pd.DataFrame(top20, columns=["词汇", "频率"])

        # 显示表格
        if show_table:
            st.subheader("📊 词频排名前20")
            st.dataframe(df_top20, use_container_width=True)

        # 准备数据
        words = [item[0] for item in top20]
        freqs = [item[1] for item in top20]
        word_freq_list = [(item[0], item[1]) for item in top20]

        # ====== 图表渲染 ======
        st.subheader("📈 可视化图表")

        if selected_chart == "词云 (WordCloud)":
            wc = (
                WordCloud()
                .add("", word_freq_list, word_size_range=[20, 100])
                .set_global_opts(title_opts=opts.TitleOpts(title="词云"))
            )
            st_pyecharts(wc, height="500px")

        elif selected_chart == "柱状图 (Bar)":
            bar = (
                Bar()
                .add_xaxis(words)
                .add_yaxis("频率", freqs)
                .reversal_axis()
                .set_global_opts(
                    title_opts=opts.TitleOpts(title="词频柱状图"),
                    yaxis_opts=opts.AxisOpts(name="词汇"),
                    xaxis_opts=opts.AxisOpts(name="频率")
                )
            )
            st_pyecharts(bar, height="600px")

        elif selected_chart == "饼图 (Pie)":
            pie = (
                Pie()
                .add("", word_freq_list)
                .set_global_opts(title_opts=opts.TitleOpts(title="词频饼图"))
                .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)"))
            )
            st_pyecharts(pie, height="600px")

        elif selected_chart == "折线图 (Line)":
            line = (
                Line()
                .add_xaxis(words)
                .add_yaxis("频率", freqs, is_smooth=True)
                .set_global_opts(title_opts=opts.TitleOpts(title="词频趋势"))
            )
            st_pyecharts(line, height="500px")

        elif selected_chart == "漏斗图 (Funnel)":
            funnel = (
                Funnel()
                .add("词频", word_freq_list, sort_="descending")
                .set_global_opts(title_opts=opts.TitleOpts(title="词频漏斗图"))
            )
            st_pyecharts(funnel, height="500px")

        elif selected_chart == "散点图 (Scatter)":
            scatter = (
                Scatter()
                .add_xaxis(words)
                .add_yaxis("频率", freqs)
                .set_global_opts(
                    title_opts=opts.TitleOpts(title="词频散点图"),
                    xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45))
                )
            )
            st_pyecharts(scatter, height="500px")

        elif selected_chart == "矩形树图 (TreeMap)":
            treemap_data = [{"name": w, "value": f} for w, f in word_freq_list]
            treemap = (
                TreeMap()
                .add("词频", treemap_data)
                .set_global_opts(title_opts=opts.TitleOpts(title="词频矩形树图"))
            )
            st_pyecharts(treemap, height="500px")

        elif selected_chart == "雷达图 (Radar)":
            # 雷达图最多适合10个维度，取前10
            radar_words = words[:10]
            radar_freqs = freqs[:10]
            c_max = max(radar_freqs) if radar_freqs else 1
            radar = (
                Radar()
                .add_schema(
                    schema=[opts.RadarIndicatorItem(name=w, max_=c_max) for w in radar_words]
                )
                .add("词频", [radar_freqs])
                .set_global_opts(title_opts=opts.TitleOpts(title="词频雷达图"))
            )
            st_pyecharts(radar, height="500px")

    else:
        st.info("请输入有效的 URL 开始分析。")
else:
    st.info("👈 请在左侧边栏输入文章 URL 并设置参数。")