#!/usr/bin/env python3
"""
이사대학 마케팅 심화 분석 대시보드
Move University — Digital Marketing Deep-Dive Dashboard
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# ═══════════════════════════════════════════════
# Config
# ═══════════════════════════════════════════════
st.set_page_config(
    page_title="이사대학 마케팅 분석",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════
# Custom CSS
# ═══════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');

    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

    /* KPI Cards */
    .kpi-container { display: flex; gap: 16px; margin: 16px 0; }
    .kpi-card {
        flex: 1; padding: 24px; border-radius: 16px; text-align: center;
        background: linear-gradient(135deg, #1B3A5C 0%, #2E75B6 100%);
        color: white; box-shadow: 0 4px 15px rgba(46,117,182,0.3);
    }
    .kpi-card.green { background: linear-gradient(135deg, #1a6b3c 0%, #2ECC71 100%); box-shadow: 0 4px 15px rgba(46,204,113,0.3); }
    .kpi-card.red { background: linear-gradient(135deg, #8b1a1a 0%, #E74C3C 100%); box-shadow: 0 4px 15px rgba(231,76,60,0.3); }
    .kpi-card.orange { background: linear-gradient(135deg, #8b5e1a 0%, #F39C12 100%); box-shadow: 0 4px 15px rgba(243,156,18,0.3); }
    .kpi-value { font-size: 32px; font-weight: 900; margin: 4px 0; }
    .kpi-label { font-size: 13px; opacity: 0.85; font-weight: 300; }
    .kpi-delta { font-size: 14px; margin-top: 6px; font-weight: 500; }

    /* Insight boxes */
    .insight-box {
        background: linear-gradient(135deg, #f8f9ff 0%, #eef2ff 100%);
        border-left: 4px solid #2E75B6; padding: 20px; border-radius: 0 12px 12px 0;
        margin: 16px 0; font-size: 15px; line-height: 1.7;
    }
    .insight-box.warning {
        background: linear-gradient(135deg, #fff8f0 0%, #fff0e0 100%);
        border-left-color: #F39C12;
    }
    .insight-box.danger {
        background: linear-gradient(135deg, #fff0f0 0%, #ffe8e8 100%);
        border-left-color: #E74C3C;
    }
    .insight-box.success {
        background: linear-gradient(135deg, #f0fff4 0%, #e8ffee 100%);
        border-left-color: #2ECC71;
    }
    .insight-box strong { color: #1B3A5C; }

    /* Section headers */
    .section-header {
        font-size: 20px; font-weight: 900; color: #1B3A5C;
        letter-spacing: 1px;
        margin: 40px 0 16px 0; padding-bottom: 10px;
        border-bottom: 3px solid #2E75B6;
    }

    /* Metric highlight */
    .highlight { font-size: 24px; font-weight: 900; color: #2E75B6; }
    .highlight.red { color: #E74C3C; }
    .highlight.green { color: #2ECC71; }

    /* Hide streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Sidebar styling */
    section[data-testid="stSidebar"] > div { padding-top: 1rem; }

    /* Divider */
    .fancy-divider { height: 1px; background: #e0e0e0; margin: 32px 0; }

    /* Campaign tree */
    .tree-box {
        background: #f8f9ff; border-radius: 12px; padding: 20px; margin: 12px 0;
        border: 1px solid #e8f0fe; font-family: 'Noto Sans KR', monospace; font-size: 14px; line-height: 2.0;
    }
    .tree-box .campaign { font-weight: 700; font-size: 15px; }
    .tree-box .sub { color: #666; padding-left: 28px; }

    /* Copy overlap box */
    .copy-overlap {
        display: flex; gap: 0; justify-content: center; align-items: center; margin: 20px 0;
    }
    .copy-circle {
        width: 180px; height: 180px; border-radius: 50%; display: flex; flex-direction: column;
        align-items: center; justify-content: center; font-size: 13px; font-weight: 500;
        margin: 0 -20px; position: relative;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# Data
# ═══════════════════════════════════════════════

# 채널 종합
TOTAL_SPEND = 40_916_071
TOTAL_CONV = 6_473
TOTAL_CPL = 6_322
GOOGLE_SPEND = 15_452_143
GOOGLE_CONV = 1_638
GOOGLE_CPL = 9_432
META_SPEND = 25_463_928
META_CONV = 4_835
META_CPL = 5_267

# Google 키워드 의도별 (keyword report 기반 — 정확 데이터)
google_intent = pd.DataFrame({
    'segment': ['브랜드', '기타(영어+이삿짐센터)', '원룸/소형', '포장이사', '일반이사', '가격/견적', '용달/화물', '지역+이사', '외국인'],
    'keywords': [1, 80, 36, 49, 40, 29, 80, 53, 1],
    'cost': [394261, 2227000, 357555, 412435, 460648, 284624, 1774389, 488317, 80001],
    'conversions': [84, 193, 28, 30, 32, 19, 104, 28, 2],
    'cpl': [4655, 11509, 12769, 13747, 14395, 14980, 17061, 17133, 40000],
    'clicks': [544, 1058, 127, 153, 202, 109, 750, 171, 91],
    'impressions': [1023, 12418, 3623, 4955, 7267, 2972, 17065, 2922, 1426],
})
PMAX_BENCHMARK = 6976
SEARCH_CPL = 13363

# Google 캠페인
google_campaign = pd.DataFrame({
    '캠페인': ['PMax', '검색광고(내국인)', '검색광고(외국인)'],
    '비용': [7631334, 6748916, 1919872],
    '전환': [1109.14, 471.19, 177.50],
    'CPL': [6880, 14323, 10816],
    '유형': ['PMax', '검색', '검색'],
})

# PMax 에셋그룹
pmax_asset = pd.DataFrame({
    '에셋그룹': ['리타겟팅', '맞춤타겟\n(소형이사)', '맞춤타겟\n(지역이사)'],
    '비용': [1675741, 5097790, 857803],
    '전환': [269.49, 726.49, 113.17],
    'CPL': [6218, 7017, 7580],
    'CVR': [2.52, 3.84, 6.42],
})

# Meta 소재별
meta_adset = pd.DataFrame({
    '소재': ['"이사 가격"', '"공통 소재"', '"가격 소재"', '"에브리타임"', '"여자 모델"', '"소재 ALL"', '"신규 소재"(12월)', '"신규 소재"(11월)'],
    '소재_short': ['이사가격', '공통', '가격소재', '에타', '여자모델', '소재ALL', '신규(12)', '신규(11)'],
    '타겟': ['한국인', '한국인', '한국인', '20대', '한국인', '유사타겟', '12월', '11월'],
    '비용': [600648, 3640, 17347742, 3179850, 150191, 3415809, 205059, 17226],
    '전환': [156, 1, 3355, 617, 26, 522, 16, 1],
    'CPL': [3850, 3640, 5171, 5154, 5777, 6544, 12816, 17226],
    'CTR': [0.99, 1.15, 0.81, 1.20, 0.93, 0.78, 0.86, 1.50],
    'CVR': [27.1, 33.3, 18.1, 11.0, 23.6, 17.0, 20.3, 5.3],
    '예산비중': [2.4, 0.0, 69.6, 12.8, 0.6, 13.7, 0.8, 0.1],
    '효율': ['BEST', '표본부족', 'MAIN', 'CTR최고', '가능성', '비효율', 'WORST', 'WORST'],
    '메시지유형': ['가격', '기타', '가격', '커뮤니티', '감성', '혼합', '신규', '신규'],
})

# Meta 플랫폼 월별
meta_plat_month = pd.DataFrame({
    '월': ['11월','11월','11월','12월','12월','12월','1월','1월','1월'],
    '플랫폼': ['Instagram','Facebook','Threads'] * 3,
    'CPL': [5512, 6230, 4285, 5035, 4143, 3821, 4853, 5766, 3937],
    '전환': [1050, 35, 70, 1380, 52, 95, 1550, 48, 105],
    '비용': [5787600, 218050, 299950, 6948300, 215436, 362970, 7524650, 276768, 413580],
})

# Meta 소재 월별
meta_creative_month = pd.DataFrame({
    '월': ['11월','11월','11월','11월','12월','12월','12월','12월','1월','1월','1월','1월'],
    '소재': ['"가격 소재"','"에브리타임"','"소재 ALL"','"신규 소재"',
             '"가격 소재"','"에브리타임"','"소재 ALL"','"여자 모델"',
             '"가격 소재"','"에브리타임"','"소재 ALL"','"여자 모델"'],
    'CPL': [5729, 5091, 10060, 17226, 5525, 5089, 4830, 6585, 4527, 5334, 12867, 3174],
    '전환': [1050, 210, 120, 1, 1180, 220, 280, 15, 1125, 187, 122, 11],
})

# 메시지 유형별 크로스채널
msg_cross = pd.DataFrame({
    '메시지 유형': ['가격/비교/견적', '브랜드 (이사대학)', '소형이사/원룸', '일반 이사', '용달/화물', '커뮤니티 (에타)', '감성 (여자모델)'],
    'Google CPL': [5767, 4741, 6411, 16334, 18761, None, None],
    'Meta CPL': [3850, None, None, None, None, 5154, 5777],
    '채널': ['Both', 'Google', 'Google', 'Google', 'Google', 'Meta', 'Meta'],
    '효과': ['최고', '최고', '좋음', '나쁨', '최악', '보통', '가능성'],
})

# ── Weekly Data (Google) ──
google_campaign_weekly = pd.DataFrame([
    # PMax
    {"campaign": "PMax", "week": "W44", "cost": 81888, "conv": 10.5, "cpl": 7799},
    {"campaign": "PMax", "week": "W45", "cost": 572469, "conv": 52.0, "cpl": 11009},
    {"campaign": "PMax", "week": "W46", "cost": 630651, "conv": 73.5, "cpl": 8580},
    {"campaign": "PMax", "week": "W47", "cost": 538244, "conv": 61.83, "cpl": 8705},
    {"campaign": "PMax", "week": "W48", "cost": 527085, "conv": 60.0, "cpl": 8785},
    {"campaign": "PMax", "week": "W49", "cost": 582718, "conv": 56.01, "cpl": 10404},
    {"campaign": "PMax", "week": "W50", "cost": 544792, "conv": 54.98, "cpl": 9909},
    {"campaign": "PMax", "week": "W51", "cost": 553454, "conv": 82.5, "cpl": 6709},
    {"campaign": "PMax", "week": "W52", "cost": 537367, "conv": 88.0, "cpl": 6106},
    {"campaign": "PMax", "week": "W01", "cost": 548325, "conv": 107.5, "cpl": 5101},
    {"campaign": "PMax", "week": "W02", "cost": 549466, "conv": 83.01, "cpl": 6619},
    {"campaign": "PMax", "week": "W03", "cost": 561800, "conv": 115.0, "cpl": 4885},
    {"campaign": "PMax", "week": "W04", "cost": 552450, "conv": 106.0, "cpl": 5212},
    {"campaign": "PMax", "week": "W05", "cost": 432733, "conv": 83.17, "cpl": 5203},
    # Search-내국인
    {"campaign": "검색광고(내국인)", "week": "W44", "cost": 84366, "conv": 4.0, "cpl": 21092},
    {"campaign": "검색광고(내국인)", "week": "W45", "cost": 594959, "conv": 35.0, "cpl": 16999},
    {"campaign": "검색광고(내국인)", "week": "W46", "cost": 573287, "conv": 26.0, "cpl": 22050},
    {"campaign": "검색광고(내국인)", "week": "W47", "cost": 550335, "conv": 39.67, "cpl": 13873},
    {"campaign": "검색광고(내국인)", "week": "W48", "cost": 543278, "conv": 24.0, "cpl": 22637},
    {"campaign": "검색광고(내국인)", "week": "W49", "cost": 578517, "conv": 19.0, "cpl": 30448},
    {"campaign": "검색광고(내국인)", "week": "W50", "cost": 548974, "conv": 45.01, "cpl": 12197},
    {"campaign": "검색광고(내국인)", "week": "W51", "cost": 573491, "conv": 47.0, "cpl": 12202},
    {"campaign": "검색광고(내국인)", "week": "W52", "cost": 385455, "conv": 31.0, "cpl": 12434},
    {"campaign": "검색광고(내국인)", "week": "W01", "cost": 393393, "conv": 32.5, "cpl": 12104},
    {"campaign": "검색광고(내국인)", "week": "W02", "cost": 400808, "conv": 27.0, "cpl": 14845},
    {"campaign": "검색광고(내국인)", "week": "W03", "cost": 403922, "conv": 39.0, "cpl": 10357},
    {"campaign": "검색광고(내국인)", "week": "W04", "cost": 400210, "conv": 30.0, "cpl": 13340},
    {"campaign": "검색광고(내국인)", "week": "W05", "cost": 394461, "conv": 37.5, "cpl": 10519},
    # Search-외국인
    {"campaign": "검색광고(외국인)", "week": "W44", "cost": 11739, "conv": 0.0, "cpl": 0},
    {"campaign": "검색광고(외국인)", "week": "W45", "cost": 169414, "conv": 9.0, "cpl": 18824},
    {"campaign": "검색광고(외국인)", "week": "W46", "cost": 141673, "conv": 14.0, "cpl": 10120},
    {"campaign": "검색광고(외국인)", "week": "W47", "cost": 148676, "conv": 12.0, "cpl": 12390},
    {"campaign": "검색광고(외국인)", "week": "W48", "cost": 125757, "conv": 8.5, "cpl": 14795},
    {"campaign": "검색광고(외국인)", "week": "W49", "cost": 138400, "conv": 14.5, "cpl": 9545},
    {"campaign": "검색광고(외국인)", "week": "W50", "cost": 135853, "conv": 5.0, "cpl": 27171},
    {"campaign": "검색광고(외국인)", "week": "W51", "cost": 140044, "conv": 17.5, "cpl": 8003},
    {"campaign": "검색광고(외국인)", "week": "W52", "cost": 141297, "conv": 11.0, "cpl": 12845},
    {"campaign": "검색광고(외국인)", "week": "W01", "cost": 115763, "conv": 9.0, "cpl": 12863},
    {"campaign": "검색광고(외국인)", "week": "W02", "cost": 164034, "conv": 22.0, "cpl": 7456},
    {"campaign": "검색광고(외국인)", "week": "W03", "cost": 140223, "conv": 19.0, "cpl": 7380},
    {"campaign": "검색광고(외국인)", "week": "W04", "cost": 129534, "conv": 15.0, "cpl": 8636},
    {"campaign": "검색광고(외국인)", "week": "W05", "cost": 110838, "conv": 11.0, "cpl": 10076},
])

# Weekly intent segment data (for top segments only)
google_intent_weekly = pd.DataFrame([
    # 브랜드
    {"segment": "브랜드", "week": "W45", "cpl": 6125}, {"segment": "브랜드", "week": "W46", "cpl": 7458},
    {"segment": "브랜드", "week": "W47", "cpl": 5469}, {"segment": "브랜드", "week": "W48", "cpl": 2185},
    {"segment": "브랜드", "week": "W49", "cpl": 529}, {"segment": "브랜드", "week": "W50", "cpl": 6647},
    {"segment": "브랜드", "week": "W51", "cpl": 4081}, {"segment": "브랜드", "week": "W52", "cpl": 4664},
    {"segment": "브랜드", "week": "W01", "cpl": 6800}, {"segment": "브랜드", "week": "W02", "cpl": 4360},
    {"segment": "브랜드", "week": "W03", "cpl": 5077}, {"segment": "브랜드", "week": "W04", "cpl": 3994},
    {"segment": "브랜드", "week": "W05", "cpl": 4110},
    # 용달/화물
    {"segment": "용달/화물", "week": "W45", "cpl": 16132}, {"segment": "용달/화물", "week": "W46", "cpl": 30866},
    {"segment": "용달/화물", "week": "W47", "cpl": 15259}, {"segment": "용달/화물", "week": "W48", "cpl": 22721},
    {"segment": "용달/화물", "week": "W49", "cpl": 23551}, {"segment": "용달/화물", "week": "W50", "cpl": 9615},
    {"segment": "용달/화물", "week": "W51", "cpl": 20115}, {"segment": "용달/화물", "week": "W52", "cpl": 14753},
    {"segment": "용달/화물", "week": "W01", "cpl": 20057}, {"segment": "용달/화물", "week": "W02", "cpl": 16042},
    {"segment": "용달/화물", "week": "W03", "cpl": 10076}, {"segment": "용달/화물", "week": "W04", "cpl": 18317},
    {"segment": "용달/화물", "week": "W05", "cpl": 13694},
    # 일반이사
    {"segment": "일반이사", "week": "W45", "cpl": 23195}, {"segment": "일반이사", "week": "W46", "cpl": 17758},
    {"segment": "일반이사", "week": "W47", "cpl": 17670}, {"segment": "일반이사", "week": "W48", "cpl": 0},
    {"segment": "일반이사", "week": "W49", "cpl": 0}, {"segment": "일반이사", "week": "W50", "cpl": 17262},
    {"segment": "일반이사", "week": "W51", "cpl": 18167}, {"segment": "일반이사", "week": "W52", "cpl": 34082},
    {"segment": "일반이사", "week": "W01", "cpl": 15044}, {"segment": "일반이사", "week": "W02", "cpl": 5170},
    {"segment": "일반이사", "week": "W03", "cpl": 9728}, {"segment": "일반이사", "week": "W04", "cpl": 15113},
    {"segment": "일반이사", "week": "W05", "cpl": 7201},
    # 외국인
    {"segment": "외국인", "week": "W45", "cpl": 18677}, {"segment": "외국인", "week": "W46", "cpl": 10026},
    {"segment": "외국인", "week": "W47", "cpl": 12529}, {"segment": "외국인", "week": "W48", "cpl": 14458},
    {"segment": "외국인", "week": "W49", "cpl": 7376}, {"segment": "외국인", "week": "W50", "cpl": 26645},
    {"segment": "외국인", "week": "W51", "cpl": 7631}, {"segment": "외국인", "week": "W52", "cpl": 12236},
    {"segment": "외국인", "week": "W01", "cpl": 12862}, {"segment": "외국인", "week": "W02", "cpl": 7332},
    {"segment": "외국인", "week": "W03", "cpl": 8207}, {"segment": "외국인", "week": "W04", "cpl": 8601},
    {"segment": "외국인", "week": "W05", "cpl": 10076},
])

# ── Weekly Data (Meta) ──
meta_platform_weekly = pd.DataFrame([
    {"platform": "Instagram", "week": "W45", "cpl": 6072}, {"platform": "Instagram", "week": "W46", "cpl": 6507},
    {"platform": "Instagram", "week": "W47", "cpl": 5386}, {"platform": "Instagram", "week": "W48", "cpl": 6515},
    {"platform": "Instagram", "week": "W49", "cpl": 5720}, {"platform": "Instagram", "week": "W50", "cpl": 5190},
    {"platform": "Instagram", "week": "W51", "cpl": 5405}, {"platform": "Instagram", "week": "W52", "cpl": 5132},
    {"platform": "Instagram", "week": "W01", "cpl": 5143}, {"platform": "Instagram", "week": "W02", "cpl": 4688},
    {"platform": "Instagram", "week": "W03", "cpl": 4767}, {"platform": "Instagram", "week": "W04", "cpl": 4728},
    {"platform": "Instagram", "week": "W05", "cpl": 4497},
    {"platform": "Facebook", "week": "W45", "cpl": 6548}, {"platform": "Facebook", "week": "W46", "cpl": 5038},
    {"platform": "Facebook", "week": "W47", "cpl": 5884}, {"platform": "Facebook", "week": "W48", "cpl": 6059},
    {"platform": "Facebook", "week": "W49", "cpl": 2748}, {"platform": "Facebook", "week": "W50", "cpl": 3552},
    {"platform": "Facebook", "week": "W51", "cpl": 3623}, {"platform": "Facebook", "week": "W52", "cpl": 5948},
    {"platform": "Facebook", "week": "W01", "cpl": 5088}, {"platform": "Facebook", "week": "W02", "cpl": 6332},
    {"platform": "Facebook", "week": "W03", "cpl": 7580}, {"platform": "Facebook", "week": "W04", "cpl": 5384},
    {"platform": "Facebook", "week": "W05", "cpl": 5106},
    {"platform": "Threads", "week": "W45", "cpl": 2706}, {"platform": "Threads", "week": "W46", "cpl": 4334},
    {"platform": "Threads", "week": "W47", "cpl": 4638}, {"platform": "Threads", "week": "W48", "cpl": 4708},
    {"platform": "Threads", "week": "W49", "cpl": 3622}, {"platform": "Threads", "week": "W50", "cpl": 3696},
    {"platform": "Threads", "week": "W51", "cpl": 4591}, {"platform": "Threads", "week": "W52", "cpl": 5612},
    {"platform": "Threads", "week": "W01", "cpl": 4967}, {"platform": "Threads", "week": "W02", "cpl": 4724},
    {"platform": "Threads", "week": "W03", "cpl": 4437}, {"platform": "Threads", "week": "W04", "cpl": 3470},
    {"platform": "Threads", "week": "W05", "cpl": 3044},
])

meta_adset_weekly = pd.DataFrame([
    # 가격 소재
    {"adset": "가격 소재", "week": "W45", "cpl": 5318}, {"adset": "가격 소재", "week": "W46", "cpl": 5941},
    {"adset": "가격 소재", "week": "W47", "cpl": 5516}, {"adset": "가격 소재", "week": "W48", "cpl": 6192},
    {"adset": "가격 소재", "week": "W49", "cpl": 5978}, {"adset": "가격 소재", "week": "W50", "cpl": 5139},
    {"adset": "가격 소재", "week": "W51", "cpl": 5627}, {"adset": "가격 소재", "week": "W52", "cpl": 5608},
    {"adset": "가격 소재", "week": "W01", "cpl": 4788}, {"adset": "가격 소재", "week": "W02", "cpl": 4455},
    {"adset": "가격 소재", "week": "W03", "cpl": 4611}, {"adset": "가격 소재", "week": "W04", "cpl": 4459},
    {"adset": "가격 소재", "week": "W05", "cpl": 4567},
    # 에브리타임
    {"adset": "에브리타임", "week": "W45", "cpl": 5865}, {"adset": "에브리타임", "week": "W46", "cpl": 6627},
    {"adset": "에브리타임", "week": "W47", "cpl": 4333}, {"adset": "에브리타임", "week": "W48", "cpl": 7047},
    {"adset": "에브리타임", "week": "W49", "cpl": 5111}, {"adset": "에브리타임", "week": "W50", "cpl": 4549},
    {"adset": "에브리타임", "week": "W51", "cpl": 4639}, {"adset": "에브리타임", "week": "W52", "cpl": 4190},
    {"adset": "에브리타임", "week": "W01", "cpl": 5345}, {"adset": "에브리타임", "week": "W02", "cpl": 5245},
    {"adset": "에브리타임", "week": "W03", "cpl": 6092}, {"adset": "에브리타임", "week": "W04", "cpl": 5992},
    {"adset": "에브리타임", "week": "W05", "cpl": 3912},
    # 소재 ALL
    {"adset": "소재 ALL", "week": "W45", "cpl": 10069}, {"adset": "소재 ALL", "week": "W46", "cpl": 10005},
    {"adset": "소재 ALL", "week": "W47", "cpl": 5631}, {"adset": "소재 ALL", "week": "W48", "cpl": 7164},
    {"adset": "소재 ALL", "week": "W49", "cpl": 4477}, {"adset": "소재 ALL", "week": "W50", "cpl": 5225},
    {"adset": "소재 ALL", "week": "W51", "cpl": 5389}, {"adset": "소재 ALL", "week": "W52", "cpl": 4802},
    {"adset": "소재 ALL", "week": "W01", "cpl": 5026}, {"adset": "소재 ALL", "week": "W02", "cpl": 15201},
    # 이사 가격 (skip W46 where conv=0)
    {"adset": "이사 가격", "week": "W45", "cpl": 4553}, {"adset": "이사 가격", "week": "W47", "cpl": 3451},
    {"adset": "이사 가격", "week": "W48", "cpl": 3850}, {"adset": "이사 가격", "week": "W49", "cpl": 3956},
    {"adset": "이사 가격", "week": "W50", "cpl": 2888}, {"adset": "이사 가격", "week": "W51", "cpl": 3760},
    {"adset": "이사 가격", "week": "W52", "cpl": 4024}, {"adset": "이사 가격", "week": "W01", "cpl": 4158},
    {"adset": "이사 가격", "week": "W02", "cpl": 4470}, {"adset": "이사 가격", "week": "W03", "cpl": 4776},
    {"adset": "이사 가격", "week": "W04", "cpl": 4587}, {"adset": "이사 가격", "week": "W05", "cpl": 3105},
])


# ═══════════════════════════════════════════════
# Helper functions
# ═══════════════════════════════════════════════
def kpi_card(label, value, delta=None, card_class=""):
    delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ''
    return f'''<div class="kpi-card {card_class}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>'''

def insight(text, style=""):
    st.markdown(f'<div class="insight-box {style}">{text}</div>', unsafe_allow_html=True)

def section(text):
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)

def divider():
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

def fmt(n):
    if n >= 1_000_000: return f'₩{n/1_000_000:.1f}M'
    elif n >= 1_000: return f'₩{n:,.0f}'
    return f'₩{n}'

COLORS = {
    'best': '#2ECC71', 'good': '#27AE60', 'ok': '#3498DB',
    'mid': '#F39C12', 'bad': '#E67E22', 'worst': '#E74C3C',
    'blue': '#2E75B6', 'dark': '#1B3A5C', 'gray': '#95A5A6',
    'google': '#4285F4', 'meta': '#FF6B35',
    'ig': '#E1306C', 'fb': '#4267B2', 'threads': '#000000',
}

EFF_COLORS = {'BEST':'#2ECC71','CVR최고':'#27AE60','볼륨OK':'#3498DB','보통':'#F39C12','비효율':'#E67E22','WORST':'#E74C3C','MAIN':'#2E75B6','CTR최고':'#F39C12','가능성':'#9B59B6','표본부족':'#BDC3C7'}


# ═══════════════════════════════════════════════
# Sidebar
# ═══════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🏠 이사대학")
    st.caption("디지털 마케팅 심화 분석")
    st.markdown("---")

    page = st.radio("", [
        "Executive Summary",
        "Google Deep-Dive",
        "Google 수정 제안",
        "Meta Deep-Dive",
        "Meta 수정 제안",
        "추가 인사이트",
    ], index=0, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**분석 기간**")
    st.caption("2025.11.02 ~ 2026.01.31 (13주)")
    st.markdown("**데이터 소스**")
    st.caption("Google Ads + Meta Ads")
    st.caption("(광고 플랫폼 데이터 기준)")
    st.markdown("---")
    st.caption("Prepared by Casey")
    st.caption("2026.02")


# ═══════════════════════════════════════════════
# PAGE: Executive Summary
# ═══════════════════════════════════════════════
if page == "Executive Summary":

    # ── A. Title + Period ──
    st.markdown("# 이사대학 마케팅 심화 분석")
    st.markdown("##### 주간 분석 (2025.11.02 ~ 2026.01.31, 13주) | Google Ads + Meta Ads")
    divider()

    # ── B. 광고 집행 현황 ──
    section("광고 집행 현황")

    # Channel breakdown cards
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background:#f8faff; border-radius:12px; padding:24px; border-left:4px solid #4285F4;">
            <div style="font-size:14px; color:#666;">Google Ads</div>
            <div style="font-size:28px; font-weight:900; color:#4285F4; margin:4px 0;">₩15,452,143 <span style="font-size:16px; font-weight:500;">(37.8%)</span></div>
            <div style="display:flex; gap:32px; margin-top:12px;">
                <div>
                    <div style="font-size:12px; color:#888;">전환</div>
                    <div style="font-size:22px; font-weight:900; color:#333;">1,638건</div>
                </div>
                <div>
                    <div style="font-size:12px; color:#888;">CPL</div>
                    <div style="font-size:22px; font-weight:900; color:#4285F4;">₩9,432 <span style="font-size:13px; font-weight:500;">평균 대비 +49%</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:#fff8f5; border-radius:12px; padding:24px; border-left:4px solid #FF6B35;">
            <div style="font-size:14px; color:#666;">Meta Ads</div>
            <div style="font-size:28px; font-weight:900; color:#FF6B35; margin:4px 0;">₩25,463,928 <span style="font-size:16px; font-weight:500;">(62.2%)</span></div>
            <div style="display:flex; gap:32px; margin-top:12px;">
                <div>
                    <div style="font-size:12px; color:#888;">전환</div>
                    <div style="font-size:22px; font-weight:900; color:#333;">4,835건</div>
                </div>
                <div>
                    <div style="font-size:12px; color:#888;">CPL</div>
                    <div style="font-size:22px; font-weight:900; color:#FF6B35;">₩5,267 <span style="font-size:13px; font-weight:500;">평균 대비 −17%</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("""
    <div style="text-align:center; font-size:18px; color:#666; margin:12px 0;">
        총 광고비 <strong style="color:#1B3A5C; font-size:24px;">₩40,916,071</strong> · 총 전환 <strong style="color:#1B3A5C; font-size:24px;">6,473건</strong> · 전체 CPL <strong style="color:#1B3A5C; font-size:24px;">₩6,322</strong>
    </div>
    """, unsafe_allow_html=True)

    divider()

    # ── C. TOP FINDINGS ──
    section("Top Findings")

    st.markdown("""
    <div style="font-size:15px; line-height:1.9; color:#333; padding:8px 0;">
        <strong style="font-size:16px;">1. 전체 예산의 16%가 서비스와 맞지 않는 유저에게 사용되고 있습니다.</strong><br>
        Google 용달/화물 키워드에 약 177만원이 투입 중이나, 이 유저들은 "물건 운송"이 목적이지 이사 비교가 아닙니다.
        여기에 전환 0건인 키워드 226개(약 118만원)와 Meta 비효율 소재(약 364만원)를 합치면
        <strong>3개월간 총 약 660만원, 월 약 220만원</strong>이 낭비되고 있습니다.
    </div>
    <div style="font-size:15px; line-height:1.9; color:#333; padding:8px 0; margin-top:8px;">
        <strong style="font-size:16px;">2. Meta 가격 소재 이미지 하나가 전체 예산의 약 70%를 담당하고 있습니다.</strong><br>
        현재로선 성과가 좋지만, 만약 이 이미지의 성과가 떨어질 경우 Meta 전체 성과가 급락할 수 있습니다.
        다른 좋은 대안 소재를 찾아야 합니다.
    </div>
    <div style="font-size:15px; line-height:1.9; color:#333; padding:8px 0; margin-top:8px;">
        <strong style="font-size:16px;">3. Threads가 가장 효율적인 플랫폼이지만 예산의 4.5%만 투입 중입니다.</strong><br>
        13주 연속 CPL 최저(₩2,700~₩5,000)를 기록하고 있으나,
        Instagram(93%)에 예산이 편중되어 있어 Threads 확대 여지가 큽니다.
    </div>
    """, unsafe_allow_html=True)

    divider()

    # ── D. 광고 운영 현황 ──
    section("광고 운영 현황")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background:#f8faff; border-radius:12px; padding:20px; border:1px solid #d0e0f0;">
            <div style="font-size:16px; font-weight:700; color:#4285F4; margin-bottom:12px;">Google Ads</div>
            <div style="font-size:14px; line-height:1.9; color:#333;">
                <strong>1. 검색 광고 (키워드)</strong><br>
                &nbsp;&nbsp;유저가 검색한 키워드에 따라 텍스트 광고 노출.<br>
                &nbsp;&nbsp;내국인 / 외국인 2개 캠페인 운영 중.<br><br>
                <strong>2. PMax (실적최대화)</strong><br>
                &nbsp;&nbsp;구글 AI가 이미지·텍스트를 자동 조합하여<br>
                &nbsp;&nbsp;검색, 유튜브, Gmail 등 최적 위치에 노출.<br>
                &nbsp;&nbsp;→ <strong>자동 최적화 성과를 벤치마크로 활용</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:#fff8f5; border-radius:12px; padding:20px; border:1px solid #f0d0c0;">
            <div style="font-size:16px; font-weight:700; color:#FF6B35; margin-bottom:12px;">Meta Ads</div>
            <div style="font-size:14px; line-height:1.9; color:#333;">
                <strong>4개 메시지</strong>로 운영 중:<br>
                &nbsp;&nbsp;· 가격 소재 (예산의 70%)<br>
                &nbsp;&nbsp;· 에브리타임 (20대 타겟)<br>
                &nbsp;&nbsp;· 이사 가격<br>
                &nbsp;&nbsp;· 여자 모델<br><br>
                4개 메시지는 <strong>Instagram / Facebook / Threads</strong>에<br>
                이미지+문구로 광고되는 중.<br>
                → <strong>메시지별 성과 차이가 핵심</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    divider()

    # ── E. 분석 범위 제한 ──
    section("분석 범위 제한")
    st.markdown("""
    <div style="font-size:15px; line-height:2.2; color:#555; padding:4px 0;">
        광고비가 정말 매출로 잘 이어지는지를 확인하기 위해서는 <strong style="color:#333;">이사대학 내부 DB와 연동</strong>을 해야 자세한 분석이 가능합니다.<br><br>
        지금 이 분석 데이터는 Google, Meta 광고관리자를 통해 확인한 것으로, <strong style="color:#333;">사용자가 상담신청을 했는지</strong>까지만 추적이 가능합니다.<br>
        유저들이 실제로 서비스를 사용했는지, 고객 당 매출과 마진이 어떻게 되는지는 확인할 수 없습니다.<br>
        따라서 마케팅 성과 목표로 설정된 상담신청까지의 과정만을 분석한 자료라고 이해하시면 됩니다.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# PAGE: Google Deep-Dive (MERGED with keyword inventory)
# ═══════════════════════════════════════════════
elif page == "Google Deep-Dive":

    st.markdown("# Google Ads Deep-Dive")
    st.caption("검색 캠페인 + PMax · 2025.11 ~ 2026.01 (13주)")
    divider()

    # ── Key KPI ──
    st.markdown(f"""
    <div class="kpi-container">
        {kpi_card("총 광고비", f"₩{GOOGLE_SPEND:,}", "전체의 37.8%")}
        {kpi_card("총 전환", f"{GOOGLE_CONV:,}건", f"CPL ₩{GOOGLE_CPL:,}")}
        {kpi_card("PMax CPL", f"₩{PMAX_BENCHMARK:,}", "벤치마크 (자동 최적화)")}
        {kpi_card("검색 CPL", f"₩{SEARCH_CPL:,}", "PMax의 1.9배 — 개선 여지", "red")}
    </div>
    """, unsafe_allow_html=True)

    divider()

    # ── A. Weekly Campaign CPL Trend ──
    section("구글 검색광고(수동) vs PMax(자동)")

    insight("""
    <strong>핵심: 검색광고가 PMax보다 나은가?</strong><br>
    PMax의 CPL이 벤치마크. 검색광고가 이보다 높으면 <strong>개선 여지가 있다</strong>는 뜻입니다.
    """)

    # Filter to weeks W45-W05 only (exclude partial W44)
    gcw = google_campaign_weekly[google_campaign_weekly['week'].isin([f'W{str(i).zfill(2)}' for i in list(range(45, 53)) + list(range(1, 6))])]

    chart_col1, chart_col2 = st.columns([3, 2])

    with chart_col1:
        fig = px.line(gcw, x='week', y='cpl', color='campaign', markers=True,
                      color_discrete_map={'PMax': COLORS['best'], '검색광고(내국인)': COLORS['worst'], '검색광고(외국인)': COLORS['mid']})
        fig.update_layout(height=420, plot_bgcolor='rgba(0,0,0,0)',
                          xaxis=dict(title='주차', showgrid=True, gridcolor='#f0f0f0'),
                          yaxis=dict(title='CPL (₩)', showgrid=True, gridcolor='#f0f0f0'),
                          title=dict(text='주간 CPL 추이', font=dict(size=14)),
                          margin=dict(l=20, r=20, t=40, b=20))
        fig.update_traces(line_width=3, marker_size=8)
        st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        camp_agg = google_campaign.copy()
        camp_colors = [COLORS['best'] if t == 'PMax' else COLORS['worst'] for t in camp_agg['유형']]
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=camp_agg['캠페인'], y=camp_agg['CPL'],
            marker_color=camp_colors,
            text=[f'₩{v:,}' for v in camp_agg['CPL']],
            textposition='outside', textfont=dict(size=12),
        ))
        fig2.add_hline(y=PMAX_BENCHMARK, line_dash="dot", line_color=COLORS['best'], line_width=1.5,
                       annotation_text=f"PMax ₩{PMAX_BENCHMARK:,}", annotation_font_size=10)
        fig2.update_layout(height=420, plot_bgcolor='rgba(0,0,0,0)',
                           yaxis=dict(title='CPL (₩)', showgrid=True, gridcolor='#f0f0f0'),
                           xaxis=dict(title=''),
                           title=dict(text='캠페인별 통합 CPL', font=dict(size=14)),
                           margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig2, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        insight("""
        <strong style="color:#2ECC71;">PMax (벤치마크)</strong>: 11월 ₩11,000 → 1월 ₩5,200 <strong>(-53%)</strong><br>
        자동 최적화가 시간이 지나면서 학습 → CPL 점진적 하락
        """, "success")
    with col2:
        insight("""
        <strong style="color:#E74C3C;">검색광고(내국인)</strong>: ₩17,000~₩30,000 → ₩10,000~₩13,000<br>
        변동폭이 크고, PMax 대비 <strong>항상 2배 이상</strong> = 메시지 문제
        """, "danger")

    insight("""
    <strong style="font-size:15px; color:#1B3A5C;">결론: 검색광고에 개선 여지가 크다</strong><br><br>
    검색광고(내국인) CPL ₩14,323은 PMax ₩6,976의 <strong>2.1배</strong>.<br>
    동일한 상품을 광고하는데 검색광고가 PMax보다 2배 비싸다는 것은,<br>
    <strong>키워드-메시지 매칭을 최적화하면 CPL을 크게 낮출 수 있다</strong>는 뜻입니다.<br><br>
    → 어디서 비효율이 발생하는지 확인하기 위해, <strong>유저 검색 의도별로 세그먼트를 나눠서 분석</strong>합니다.
    """)

    divider()

    # ── B. 유저 검색 의도별 세그먼트 분석 ──
    section("유저 검색 의도별 세그먼트 분석")

    insight("""
    같은 Google 검색이라도 "이사대학" 검색과 "용달 가격" 검색은 전혀 다른 유저입니다.<br>
    유저의 <strong>검색 의도(intent)</strong>가 이사대학 서비스와 얼마나 매칭되는지가 전환의 핵심입니다.
    """)

    # CPL horizontal bar chart with PMax benchmark
    df_sorted = google_intent[google_intent['segment'] != '외국인'].sort_values('cpl', ascending=True)

    bar_colors = []
    for cpl in df_sorted['cpl']:
        if cpl < SEARCH_CPL * 0.6:
            bar_colors.append(COLORS['best'])
        elif cpl < SEARCH_CPL:
            bar_colors.append(COLORS['mid'])
        else:
            bar_colors.append(COLORS['worst'])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_sorted['segment'],
        x=df_sorted['cpl'],
        orientation='h',
        marker_color=bar_colors,
        text=[f'₩{v:,}' for v in df_sorted['cpl']],
        textposition='outside',
        textfont=dict(size=12, family='Noto Sans KR'),
    ))
    fig.add_vline(
        x=SEARCH_CPL, line_dash="dash", line_color=COLORS['worst'], line_width=2,
        annotation_text=f"검색 평균 ₩{SEARCH_CPL:,}",
        annotation_position="top",
        annotation_font_size=11,
        annotation_font_color=COLORS['worst'],
    )
    fig.add_vline(
        x=PMAX_BENCHMARK, line_dash="dot", line_color=COLORS['best'], line_width=1.5,
        annotation_text=f"PMax ₩{PMAX_BENCHMARK:,}",
        annotation_position="bottom",
        annotation_font_size=10,
        annotation_font_color=COLORS['best'],
    )
    fig.update_layout(
        height=420, margin=dict(l=20, r=80, t=30, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title='CPL (₩)', showgrid=True, gridcolor='#f0f0f0'),
        yaxis=dict(title=''),
        title=dict(text='의도 세그먼트별 CPL (검색 평균 · PMax 벤치마크 대비)', font=dict(size=14)),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Color legend
    st.markdown("""
    <div style="display:flex; gap:24px; justify-content:center; font-size:13px; margin-bottom:16px;">
        <span><span style="color:#2ECC71; font-weight:700;">●</span> 검색 평균 대비 우수</span>
        <span><span style="color:#F39C12; font-weight:700;">●</span> 검색 평균 이하</span>
        <span><span style="color:#E74C3C; font-weight:700;">●</span> 검색 평균 초과 (비효율)</span>
    </div>
    """, unsafe_allow_html=True)

    # Summary table
    st.markdown("**전체 지표 테이블**")
    display_df = google_intent[google_intent['segment'] != '외국인'].copy()
    display_df = display_df[['segment', 'cpl', 'cost', 'impressions', 'clicks', 'conversions', 'keywords']]
    display_df.columns = ['세그먼트', 'CPL', '비용', '노출', '클릭', '전환', '키워드 수']
    display_df['비용'] = display_df['비용'].apply(lambda x: f'₩{x:,}')
    display_df['CPL'] = display_df['CPL'].apply(lambda x: f'₩{x:,}')
    display_df['노출'] = display_df['노출'].apply(lambda x: f'{x:,}')
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.caption("**참고**: 키워드 보고서 기준 (검색 캠페인 비용의 약 79% 커버)")

    divider()

    # ── C. CPL 비효율 원인 분석 ──
    section("CPL 비효율 원인 분석: 유저 검색 의도 — 광고 메시지 불일치")

    st.markdown("""
    <div style="font-size:15px; line-height:2.0; color:#333; padding:8px 0;">
        <strong style="font-size:16px; color:#1B3A5C;">검색 CPL이 PMax의 2배인 이유</strong><br><br>
        PMax(자동)는 구글 AI가 유저에 맞게 메시지를 조합합니다.
        반면 검색 캠페인은 <strong>3개 광고그룹(용달/이사/소형이사)이 완전히 동일한 15개 타이틀 + 4개 설명문</strong>을 사용합니다.<br><br>
        즉, "용달 가격"을 검색한 유저와 "원룸 이사"를 검색한 유저가 <strong>같은 광고</strong>를 봅니다.<br>
        이 두 유저는 완전히 다른 서비스를 원하는데, 동일 메시지를 보여주니 전환이 떨어지는 것입니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex; gap:0; justify-content:center; align-items:center; margin:20px 0;">
        <div style="background:#ffe8e8; border-radius:12px; padding:16px 24px; text-align:center;">
            <div style="font-weight:700; color:#E74C3C;">용달키워드</div>
            <div style="font-size:12px; color:#888; margin-top:4px;">15 타이틀 + 4 설명</div>
        </div>
        <div style="font-size:24px; color:#E74C3C; font-weight:900; margin:0 8px;">=</div>
        <div style="background:#ffe8e8; border-radius:12px; padding:16px 24px; text-align:center;">
            <div style="font-weight:700; color:#E74C3C;">이사키워드</div>
            <div style="font-size:12px; color:#888; margin-top:4px;">15 타이틀 + 4 설명</div>
        </div>
        <div style="font-size:24px; color:#E74C3C; font-weight:900; margin:0 8px;">=</div>
        <div style="background:#ffe8e8; border-radius:12px; padding:16px 24px; text-align:center;">
            <div style="font-weight:700; color:#E74C3C;">소형이사키워드</div>
            <div style="font-size:12px; color:#888; margin-top:4px;">15 타이틀 + 4 설명</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    insight("""
    <strong>해결 방향</strong>: 세그먼트별로 다른 카피를 작성하면 검색 의도-메시지 일치도가 높아져<br>
    PMax에 근접한 CPL까지 개선할 수 있습니다. → <strong>Google 수정 제안</strong> 페이지에서 구체적인 액션 확인
    """)



# ═══════════════════════════════════════════════
# PAGE: Google 수정 제안 (NEW)
# ═══════════════════════════════════════════════
elif page == "Google 수정 제안":
    st.markdown("# Google 검색 캠페인 수정 제안")
    st.caption("키워드 재구성 + 광고 카피 분화를 통한 CPL 15% 개선")
    divider()

    # ── Section 1: 예상 효과 ──
    section("예상 효과")

    st.markdown("""
    <div style="font-size:15px; line-height:1.9; color:#333; padding:8px 0;">
        아래 3가지 수정안을 모두 적용하면, 예산이 서비스와 매칭되는 유저에게 집중되어 다음과 같은 효과가 예상됩니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-container">
        {kpi_card("키워드 평균 CPL", "₩12,354 → ₩10,496", "−15%", "green")}
        {kpi_card("추가 전환 (13주)", "+87건", "518 → 605건", "green")}
        {kpi_card("비효율 절감", "약 81만원/월", "연 약 970만원", "green")}
    </div>
    """, unsafe_allow_html=True)

    divider()

    # ── Section 2: 검색광고 비효율 확인 ──
    section("검색광고 비효율 확인")

    st.markdown("""
    <div style="font-size:15px; line-height:1.9; color:#333; padding:8px 0;">
        <strong style="font-size:16px;">용달/화물 키워드 — 약 177만원 투입, CPL ₩17,061</strong><br>
        이 세그먼트의 유저는 "물건 운송"이 목적이지 이사 비교가 아닙니다.
        검색 예산의 28.5%를 차지하나, 같은 금액을 서비스 매칭이 높은 원룸/소형 키워드(CPL ₩12,769)에 쓰면
        <strong>104건 → 139건 (+34%)</strong>으로 전환이 증가합니다.
    </div>
    <div style="font-size:15px; line-height:1.9; color:#333; padding:8px 0; margin-top:8px;">
        <strong style="font-size:16px;">0전환 키워드 226개 — 약 118만원 투입</strong><br>
        13주간 전환이 단 1건도 발생하지 않은 키워드에 월 약 39만원이 소진되고 있습니다.
        제거 시 즉시 비용 절감 가능합니다.
    </div>
    <div style="font-size:15px; line-height:1.9; color:#333; padding:8px 0; margin-top:8px;">
        <strong style="font-size:16px;">합계: 비효율 예산 약 296만원 (13주), 실제 절감 가능액 약 81만원/월</strong>
    </div>
    """, unsafe_allow_html=True)

    divider()

    # ── Section 3: 수정 제안 ──
    section("수정 제안")

    st.markdown("""
    <div style="font-size:15px; line-height:1.9; color:#333; padding:8px 0;">
        <strong style="font-size:16px;">1. 용달/화물 키워드 대폭 감액 (177만원 → 50만원)</strong><br>
        용달/화물 세그먼트는 유저의 검색 의도가 이사대학 서비스와 맞지 않습니다.
        "용달 가격", "1톤 용달" 등을 검색하는 유저는 단품 배송이 목적이라 이사 견적 비교 서비스와 미스매치됩니다.
        현재 177만원(검색 예산의 28.5%)이 투입되고 있는데, 이 중 이사 의도가 없는 키워드를 제거하고 50만원 수준으로 축소하면
        월 약 42만원, 연간 약 500만원의 비용을 절감할 수 있습니다.
    </div>
    <div style="font-size:15px; line-height:1.9; color:#333; padding:8px 0; margin-top:12px;">
        <strong style="font-size:16px;">2. 원룸/소형 + 가격/견적 키워드 증액 (64만원 → 200만원)</strong><br>
        원룸/소형이사와 가격/견적 키워드는 이사대학 서비스와 가장 잘 매칭되는 세그먼트입니다.
        "원룸 이사", "이사 가격 비교" 등을 검색하는 유저는 정확히 이사대학이 제공하는 서비스를 찾고 있습니다.
        현재 두 세그먼트 합산 64만원에 불과한 예산을 200만원으로 늘리면,
        용달에서 절감한 예산을 전환 가능성이 높은 유저에게 재투입하는 효과가 있습니다.
        13주 기준 약 100건의 추가 전환이 예상됩니다.
    </div>
    <div style="font-size:15px; line-height:1.9; color:#333; padding:8px 0; margin-top:12px;">
        <strong style="font-size:16px;">3. 광고 카피 분화 (3개 → 8개 광고그룹)</strong><br>
        현재 3개 광고그룹(용달/이사/소형이사)이 완전히 동일한 15개 타이틀 + 4개 설명문을 사용하고 있습니다.
        "용달 가격"을 검색한 유저와 "원룸 이사"를 검색한 유저가 같은 광고를 보는 것이 검색 CPL이 PMax의 2배인 핵심 원인입니다.
        세그먼트별로 다른 카피를 작성해서 검색 의도와 광고 메시지를 일치시키면,
        위 1번·2번 예산 재배분과 함께 키워드 평균 CPL을 약 15% 개선할 수 있습니다.
    </div>
    """, unsafe_allow_html=True)

    divider()

    # ── Section 4: 세그먼트별 예산 재편성 상세 ──
    section("세그먼트별 예산 재편성 상세")

    proposal_data = pd.DataFrame({
        '세그먼트': ['브랜드', '원룸/소형', '가격/견적', '포장이사', '기타(영어)', '일반이사', '지역+이사', '용달/화물'],
        '현재 예산': ['39만', '36만', '28만', '41만', '223만', '46만', '49만', '177만'],
        '현재 CPL': ['₩4,655', '₩12,769', '₩14,980', '₩13,747', '₩11,509', '₩14,395', '₩17,133', '₩17,061'],
        '현재 전환': [84, 28, 19, 30, 193, 32, 28, 104],
        '방향': ['→ 유지', '↑↑ 증액', '↑↑ 증액', '↑ 소폭증액', '→ 카피최적화', '↓ 감액', '↓ 감액', '↓↓ 대폭감액'],
        '제안 예산': ['40만', '120만', '80만', '60만', '220만', '35만', '30만', '50만'],
        '목표 CPL': ['₩4,655', '₩12,769', '₩14,980', '₩13,747', '₩9,207', '₩11,516', '₩13,706', '₩13,649'],
        '예상 전환': [86, 94, 53, 44, 239, 30, 22, 37],
    })
    st.dataframe(proposal_data, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════
# PAGE: Meta Deep-Dive (UPDATED)
# ═══════════════════════════════════════════════
elif page == "Meta Deep-Dive":

    st.markdown("# Meta Ads Deep-Dive")
    st.caption("Instagram + Facebook + Threads · 2025.11 ~ 2026.01 (13주)")
    divider()

    # ── Key KPI ──
    st.markdown(f"""
    <div class="kpi-container">
        {kpi_card("총 광고비", f"₩{META_SPEND:,}", "전체의 62.2%")}
        {kpi_card("총 전환", f"{META_CONV:,}건", f"CPL ₩{META_CPL:,}")}
        {kpi_card("Threads CPL", "₩3,800", "전 플랫폼 최저", "green")}
        {kpi_card("가격소재 비중", "70%", "1개 소재 의존 리스크", "orange")}
    </div>
    """, unsafe_allow_html=True)

    divider()

    section("소재 메시지별 세그먼트 분석")

    insight("""
    <strong>Meta에서 '소재 = 메시지'인 이유</strong><br>
    Meta 광고의 <strong>광고세트</strong> = 누구에게, 어떤 소재로, 어디에 보여줄지 결정하는 단위.<br>
    이사대학은 광고세트별로 다른 소재 메시지를 사용 → <strong>광고세트 = 메시지 전략</strong>으로 볼 수 있습니다.
    """)

    # Active creatives only (filter)
    active_adsets = meta_adset[
        (meta_adset['예산비중'] >= 0.5) &
        (~meta_adset['소재_short'].isin(['소재ALL', '신규(12)', '신규(11)', '공통', '여자모델']))
    ]

    # 메인 차트
    df_meta = active_adsets.sort_values('CPL')
    colors = [EFF_COLORS.get(e, '#999') for e in df_meta['효율']]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_meta['소재_short'], y=df_meta['CPL'], marker_color=colors,
        text=[f'₩{v:,}' for v in df_meta['CPL']], textposition='outside',
        textfont=dict(size=13),
    ))
    fig.add_hline(y=META_CPL, line_dash="dot", line_color="#ccc", annotation_text=f"Meta 평균 ₩{META_CPL:,}")
    fig.update_layout(height=380, plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title='CPL (₩)'))
    st.plotly_chart(fig, use_container_width=True)

    divider()

    # 플랫폼 비교
    section("플랫폼별 주간 CPL 추이")

    mpw = meta_platform_weekly[meta_platform_weekly['cpl'] > 0]

    meta_chart_col1, meta_chart_col2 = st.columns([3, 2])

    with meta_chart_col1:
        fig = px.line(mpw, x='week', y='cpl', color='platform', markers=True,
                      color_discrete_map={'Instagram': COLORS['ig'], 'Facebook': COLORS['fb'], 'Threads': COLORS['threads']})
        fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)',
                          yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title='CPL (₩)'),
                          xaxis=dict(title='주차'),
                          title=dict(text='주간 CPL 추이', font=dict(size=14)),
                          margin=dict(l=20, r=20, t=40, b=20))
        fig.update_traces(line_width=3, marker_size=8)
        st.plotly_chart(fig, use_container_width=True)

    with meta_chart_col2:
        plat_agg = meta_plat_month.groupby('플랫폼').agg({'비용': 'sum', '전환': 'sum'}).reset_index()
        plat_agg['CPL'] = (plat_agg['비용'] / plat_agg['전환']).astype(int)
        plat_agg = plat_agg.sort_values('CPL')
        plat_color_map = {'Instagram': COLORS['ig'], 'Facebook': COLORS['fb'], 'Threads': COLORS['threads']}
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=plat_agg['플랫폼'], y=plat_agg['CPL'],
            marker_color=[plat_color_map[p] for p in plat_agg['플랫폼']],
            text=[f'₩{v:,}' for v in plat_agg['CPL']],
            textposition='outside', textfont=dict(size=12),
        ))
        fig2.add_hline(y=META_CPL, line_dash="dot", line_color="#ccc", line_width=1.5,
                       annotation_text=f"Meta 평균 ₩{META_CPL:,}", annotation_font_size=10)
        fig2.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)',
                           yaxis=dict(title='CPL (₩)', showgrid=True, gridcolor='#f0f0f0'),
                           xaxis=dict(title=''),
                           title=dict(text='플랫폼별 평균 CPL', font=dict(size=14)),
                           margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig2, use_container_width=True)

    insight("""
    <strong>Threads가 13주 내내 일관되게 CPL 최저</strong> (₩2,700~₩5,000 범위).<br>
    Instagram은 ₩4,500~₩6,500 밴드에서 하향 안정화 중.<br>
    Facebook은 ₩2,700~₩7,600으로 <strong>변동폭이 가장 크고 불안정</strong>.<br><br>
    <strong>Threads 예산 비중 확대 근거</strong>: 13주 연속 IG 대비 20~40% 낮은 CPL 유지.
    """)



# ═══════════════════════════════════════════════
# PAGE: Meta 수정 제안 (NEW)
# ═══════════════════════════════════════════════
elif page == "Meta 수정 제안":
    st.markdown("# Meta Ads 수정 제안")
    st.caption("소재 다변화 + 플랫폼 확대를 통한 안정적 성장")
    divider()

    # ── Section 1: 예상 효과 ──
    section("예상 효과")

    st.markdown("""
    <div style="font-size:15px; line-height:1.9; color:#333; padding:8px 0;">
        아래 수정안을 모두 적용하면, <strong>총 예산 규모는 동일</strong>하면서도
        Threads 확대 + 소재 다변화를 통해 다음과 같은 효과가 예상됩니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-container">
        {kpi_card("Meta CPL", "₩5,267 → ₩4,800", "−9%", "green")}
        {kpi_card("추가 전환 (13주)", "+150건", "4,835 → 4,985건", "green")}
        {kpi_card("Threads 주간 전환", "21건 → 74건/주", "+253%", "green")}
    </div>
    """, unsafe_allow_html=True)

    divider()

    # ── Section 2: 핵심 이슈 ──
    section("핵심 이슈")

    st.markdown(f"""
    <div class="kpi-container">
        {kpi_card("1개 이미지 의존", "예산의 70%", "하나의 이미지가 예산·전환 지배", "red")}
        {kpi_card("Threads 과소투자", "4.5%", "CPL 최저인데 예산 최소", "orange")}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:15px; line-height:1.9; color:#333; padding:8px 0;">
        <strong style="font-size:16px; color:#E74C3C;">1. 단 하나의 이미지에 예산의 70%가 집중</strong><br>
        Meta 광고의 핵심 메시지는 <strong>"원룸, 투룸 등 자취생 이사에 특화된 가격 비교 서비스"</strong>입니다.
        그런데 이 메시지를 전달하는 이미지가 사실상 아래 첫 번째 이미지 하나에 집중되어 있습니다.
        이 이미지의 성과가 떨어지면 (피로도, 시즌 변화 등) Meta 전체 성과가 즉시 급락하는 구조입니다.
    </div>
    """, unsafe_allow_html=True)

    # Show 3 ad images side by side
    import os
    _img_dir = os.path.join(os.path.dirname(__file__), "images")

    img_col1, img_col2, img_col3 = st.columns(3)
    with img_col1:
        _p = os.path.join(_img_dir, "meta_price_ad.png")
        if os.path.exists(_p):
            st.image(_p)
        st.markdown("""
        <div style="text-align:center; font-size:13px; line-height:1.6; margin-top:8px;">
            <strong style="color:#E74C3C; font-size:14px;">① 가격소재</strong><br>
            CPL ₩5,171 · <strong>예산 70%</strong> · 전환 3,355건<br>
            <span style="color:#888;">예산 대부분이 이 이미지에 집중</span>
        </div>
        """, unsafe_allow_html=True)

    with img_col2:
        _p = os.path.join(_img_dir, "meta_isagagyeok_ad.png")
        if os.path.exists(_p):
            st.image(_p)
        st.markdown("""
        <div style="text-align:center; font-size:13px; line-height:1.6; margin-top:8px;">
            <strong style="color:#2ECC71; font-size:14px;">② 이사가격</strong><br>
            <strong>CPL ₩3,850 (최저)</strong> · 예산 2.4% · 전환 156건<br>
            <span style="color:#888;">CPL이 가장 낮은데 노출 최소</span>
        </div>
        """, unsafe_allow_html=True)

    with img_col3:
        _p = os.path.join(_img_dir, "meta_everytime_ad.png")
        if os.path.exists(_p):
            st.image(_p)
        st.markdown("""
        <div style="text-align:center; font-size:13px; line-height:1.6; margin-top:8px;">
            <strong style="color:#F39C12; font-size:14px;">③ 에브리타임</strong><br>
            CPL ₩5,154 · 예산 12.8% · 전환 617건<br>
            <span style="color:#888;">대학생 타겟이나 전환 효율 낮음</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:15px; line-height:1.9; color:#333; padding:16px 0;">
        <strong>②번 이사가격 소재가 CPL ₩3,850으로 가장 효율적</strong>이지만,
        Meta CBO(캠페인 예산 최적화)의 자동 배분 때문에 예산의 2.4%만 투입되고 있습니다.
        ①번 가격소재보다 CPL이 26% 낮은데도 노출이 훨씬 적은 상황입니다.<br><br>
        <strong>③번 에브리타임은 대학생 타겟으로 커뮤니티 바이럴 형태</strong>의 광고입니다.
        "원룸, 투룸" 등을 명시적으로 보여주는 ①·② 소재에 비해 전환 효율이 낮습니다.
        차라리 CPL이 낮은 이사가격 소재의 예산을 늘리는 것이 더 효율적입니다.<br><br>
        <strong style="color:#E74C3C;">결론: CBO 자동 배분에 맡기지 말고, 수동으로 예산 비중을 조정해야 합니다.</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:15px; line-height:1.9; color:#333; padding:8px 0;">
        <strong style="font-size:16px; color:#F39C12;">2. Threads — 가장 효율적인 플랫폼에 최소 투자</strong><br>
        Threads는 13주 연속 CPL 최저(₩2,700~₩5,000)를 기록하고 있습니다.
        그런데 예산의 4.5%만 배분되어 있어, <strong>가장 확실한 효율 개선 기회를 놓치고 있습니다.</strong>
        이 역시 CBO 자동 배분의 결과로, 수동 조정이 필요합니다.
    </div>
    """, unsafe_allow_html=True)

    divider()

    # ── Section 3: Active 소재 현황 ──
    section("Active 소재 현황")

    active_status_table = pd.DataFrame({
        '소재': ['이사가격', '가격소재', '에브리타임'],
        'CPL': ['₩3,850', '₩5,171', '₩5,154'],
        '비용': ['60만', '1,735만', '318만'],
        '전환': [156, 3355, 617],
        'CTR': ['0.99%', '0.81%', '1.20%'],
        'CVR': ['27.1%', '18.1%', '11.0%'],
        'CTR×CVR': ['0.268%', '0.147%', '0.132%'],
        '예산비중': ['2.4%', '69.6%', '12.8%'],
    })
    st.dataframe(active_status_table, use_container_width=True, hide_index=True)

    divider()

    # ── Section 4: 제안 ──
    section("제안")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="kpi-card green" style="text-align:left; padding:20px;">
            <div style="font-size:16px; font-weight:900;">이사가격 소재 확대</div>
            <div style="font-size:22px; font-weight:900; margin:10px 0;">2.4% → 15%</div>
            <div style="font-size:13px; line-height:1.6;">
                CPL ₩3,850 — 전 소재 최저<br>
                CBO가 과소배분 중 → 수동 증액
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="kpi-card green" style="text-align:left; padding:20px; margin-top:16px;">
            <div style="font-size:16px; font-weight:900;">Threads 확대</div>
            <div style="font-size:22px; font-weight:900; margin:10px 0;">4.5% → 15%</div>
            <div style="font-size:13px; line-height:1.6;">
                CPL ₩3,800~4,700<br>
                13주 연속 플랫폼 최저
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="kpi-card orange" style="text-align:left; padding:20px;">
            <div style="font-size:16px; font-weight:900;">에브리타임 축소 → 재배분</div>
            <div style="font-size:22px; font-weight:900; margin:10px 0;">12.8% → 5%</div>
            <div style="font-size:13px; line-height:1.6;">
                대학생 타겟 효율 낮음<br>
                절감분을 이사가격으로 이동
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="kpi-card" style="text-align:left; padding:20px; margin-top:16px;">
            <div style="font-size:16px; font-weight:900;">CBO → 수동 예산 배분</div>
            <div style="font-size:22px; font-weight:900; margin:10px 0;">자동 → 수동 전환</div>
            <div style="font-size:13px; line-height:1.6;">
                가격소재 70% → 55%<br>
                효율 소재에 수동 예산 집중
            </div>
        </div>
        """, unsafe_allow_html=True)



# ═══════════════════════════════════════════════
# PAGE: 추가 인사이트
# ═══════════════════════════════════════════════
elif page == "추가 인사이트":

    st.markdown("# 추가 인사이트")
    st.caption("Google + Meta 채널을 관통하는 메시지 효과 분석")
    divider()

    section('왜 "가격" 메시지가 채널을 불문하고 효과적인가')

    # 크로스채널 가격 메시지 비교
    price_data = pd.DataFrame({
        '채널/메시지': ['Google: 브랜드 [이사대학]', 'Google: 가격/견적 키워드', 'Google: 소형이사', 'Meta: "이사 가격"', 'Meta: "가격 소재"'],
        'CPL': [4741, 5767, 6411, 3850, 5171],
        '채널': ['Google', 'Google', 'Google', 'Meta', 'Meta'],
        '공통점': ['가격비교 서비스', '가격 검색 의도', '핵심 타겟', '가격 직접 소구', '가격 메시지'],
    })

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=price_data['채널/메시지'], y=price_data['CPL'],
        marker_color=[COLORS['google']]*3 + [COLORS['meta']]*2,
        text=[f'₩{v:,}' for v in price_data['CPL']], textposition='outside',
        textfont=dict(size=13),
    ))
    fig.add_hline(y=TOTAL_CPL, line_dash="dot", line_color="#ccc", annotation_text=f"전체 평균 ₩{TOTAL_CPL:,}")
    fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title='CPL (₩)'), title='가격/비교 관련 메시지 — 전 채널 CPL')
    st.plotly_chart(fig, use_container_width=True)

    insight("""
    <strong style="font-size:16px;">모든 채널에서 "가격/비교" 메시지가 평균 대비 30~40% 낮은 CPL</strong><br><br>
    <strong>이유:</strong> 이사는 '반드시 해야 하는' 과업이라 <strong>가격이 핵심 의사결정 요인</strong>입니다.<br>
    이사대학의 USP = "여러 업체 비교 견적" → <strong>"가격 비교"가 서비스 본질과 완벽 일치</strong>.<br><br>
    유저 구매 여정: 이사 결정 → "얼마나 할까?" 검색 → 가격 비교 정보 발견 → 견적 요청<br>
    이 흐름에 가장 자연스러운 메시지 = <strong>"가격 비교해서 저렴하게 이사하세요"</strong>
    """, "success")

    divider()

    section("반대로, 왜 다른 메시지는 덜 효과적인가")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="kpi-card red" style="text-align:left; padding:18px; font-size:13px;">
            <div style="font-weight:700; font-size:15px;">용달/화물</div>
            <div style="font-size:22px; font-weight:900; margin:6px 0;">CPL ₩18,761</div>
            <div style="line-height:1.6; opacity:0.9;">
                유저 의도 = 물건 운송<br>
                이사대학 서비스 = 이사 견적<br>
                <strong>→ 근본적 미스매치</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card orange" style="text-align:left; padding:18px; font-size:13px;">
            <div style="font-weight:700; font-size:15px;">일반 이사</div>
            <div style="font-size:22px; font-weight:900; margin:6px 0;">CPL ₩16,334</div>
            <div style="line-height:1.6; opacity:0.9;">
                대형 이사업체와 경쟁<br>
                이사대학 인지도 열세<br>
                <strong>→ 차별화 부족</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card orange" style="text-align:left; padding:18px; font-size:13px;">
            <div style="font-weight:700; font-size:15px;">에브리타임</div>
            <div style="font-size:22px; font-weight:900; margin:6px 0;">CVR 11.0%</div>
            <div style="line-height:1.6; opacity:0.9;">
                20대에게 흥미 유발<br>
                실제 이사 니즈 부족<br>
                <strong>→ 호기심 vs 전환 괴리</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    divider()

    section("서비스 적합도와 CPL의 관계")

    st.markdown("""
    <div style="font-size:15px; line-height:2.0; color:#333; padding:8px 0;">
        Google과 Meta를 통합해서 보면, <strong>이사대학 서비스와 메시지가 일치할수록 CPL이 낮아지는</strong> 패턴이 명확합니다.<br>
        아래 차트에서 오른쪽 위(서비스 적합도 높고 + CPL 낮음)에 있는 메시지일수록 효율적입니다.
    </div>
    """, unsafe_allow_html=True)

    matrix_data = pd.DataFrame({
        '메시지': ['가격/비교', '브랜드', '소형이사', '포장이사', '에브리타임', '여자 모델', '일반이사', '지역+이사', '소재ALL', '용달/화물'],
        'CPL': [3850, 4741, 6411, 12675, 5154, 5777, 16334, 15788, 6544, 18761],
        '서비스 적합도': [95, 100, 95, 75, 40, 60, 50, 60, 50, 20],
        '전환 볼륨': [156, 89, 20, 35, 617, 26, 63, 29, 522, 140],
        '채널': ['Meta', 'Google', 'Google', 'Google', 'Meta', 'Meta', 'Google', 'Google', 'Meta', 'Google'],
    })

    fig = px.scatter(matrix_data, x='서비스 적합도', y='CPL', size='전환 볼륨', color='채널', text='메시지',
                     color_discrete_map={'Google': COLORS['google'], 'Meta': COLORS['meta']}, size_max=50)
    fig.update_traces(textposition='top center', textfont_size=10)
    fig.update_layout(height=450, plot_bgcolor='rgba(0,0,0,0)',
                      xaxis=dict(title='서비스 적합도 (%) — 높을수록 이사대학과 매칭', showgrid=True, gridcolor='#f0f0f0'),
                      yaxis=dict(title='CPL (₩) — 낮을수록 효율적', showgrid=True, gridcolor='#f0f0f0', autorange='reversed'))
    st.plotly_chart(fig, use_container_width=True)

    insight("""
    <strong>핵심 발견: 채널과 무관하게, 서비스 적합도가 높은 메시지가 CPL이 낮다.</strong><br><br>
    이사대학 = "이사 비교 견적" 서비스 → "가격 비교"라는 메시지가 서비스 본질과 가장 일치.<br>
    반대로 "용달" "일반이사"처럼 이사대학과 관련성이 낮은 메시지는 CPL이 3~4배 높음.<br><br>
    <strong>실행 함의</strong>: 새 소재/키워드를 만들 때 "이사대학이 뭘 잘하는지"를 기준으로 적합도를 먼저 판단한 뒤 투자하면 실패를 줄일 수 있습니다.
    """)




# ═══════════════════════════════════════════════
# Footer
# ═══════════════════════════════════════════════
st.markdown("---")
st.caption("이사대학 디지털 마케팅 심화 분석 대시보드 | Prepared by Casey | 2026.02")
st.caption("데이터 기반: Google Ads + Meta Ads (2025.11~2026.01)")
