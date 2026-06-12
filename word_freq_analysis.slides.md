---
# Slidev 全局配置
theme: seriph
title: 基于Streamlit的网页词频分析可视化工具
background: https://cover.sli.dev
class: text-center
highlighter: shiki
drawings:
  persist: false
transition: slide-left
mdc: true
---

# 📰 Streamlit 文章词频分析可视化工具
## 项目完整源码解析与功能演示
<div class="pt-12 opacity-80 text-sm">
Python + Streamlit + BeautifulSoup + Jieba + Pyecharts 多图表可视化系统
</div>

---

# 一、项目整体技术栈
### 核心依赖库说明
```python
# 页面框架
import streamlit as st
# 网页爬虫
import requests
from bs4 import BeautifulSoup
# 中文分词 + 词频统计
import jieba
from collections import Counter
# 表格数据
import pandas as pd
# 可视化图表（8种图表）
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Bar, Pie, Line, Funnel, Scatter, TreeMap, Radar
from pyecharts.commons.utils import JsCode
# Pyecharts嵌入Streamlit
from streamlit_echarts import st_pyecharts
# 正则清洗文本
import re