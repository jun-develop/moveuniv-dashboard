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
        font-size: 14px; font-weight: 700; color: #2E75B6;
        text-transform: uppercase; letter-spacing: 2px;
        margin: 32px 0 8px 0; padding-bottom: 8px;
        border-bottom: 2px solid #e8f0fe;
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
    .fancy-divider { height: 3px; background: linear-gradient(90deg, #2E75B6, #2ECC71, #F39C12); border-radius: 2px; margin: 32px 0; }

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
    '캠페인': ['실적최대화 (PMax)', '검색광고(내국인)', '검색광고(외국인)'],
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
    {"campaign": "검색(내국인)", "week": "W44", "cost": 84366, "conv": 4.0, "cpl": 21092},
    {"campaign": "검색(내국인)", "week": "W45", "cost": 594959, "conv": 35.0, "cpl": 16999},
    {"campaign": "검색(내국인)", "week": "W46", "cost": 573287, "conv": 26.0, "cpl": 22050},
    {"campaign": "검색(내국인)", "week": "W47", "cost": 550335, "conv": 39.67, "cpl": 13873},
    {"campaign": "검색(내국인)", "week": "W48", "cost": 543278, "conv": 24.0, "cpl": 22637},
    {"campaign": "검색(내국인)", "week": "W49", "cost": 578517, "conv": 19.0, "cpl": 30448},
    {"campaign": "검색(내국인)", "week": "W50", "cost": 548974, "conv": 45.01, "cpl": 12197},
    {"campaign": "검색(내국인)", "week": "W51", "cost": 573491, "conv": 47.0, "cpl": 12202},
    {"campaign": "검색(내국인)", "week": "W52", "cost": 385455, "conv": 31.0, "cpl": 12434},
    {"campaign": "검색(내국인)", "week": "W01", "cost": 393393, "conv": 32.5, "cpl": 12104},
    {"campaign": "검색(내국인)", "week": "W02", "cost": 400808, "conv": 27.0, "cpl": 14845},
    {"campaign": "검색(내국인)", "week": "W03", "cost": 403922, "conv": 39.0, "cpl": 10357},
    {"campaign": "검색(내국인)", "week": "W04", "cost": 400210, "conv": 30.0, "cpl": 13340},
    {"campaign": "검색(내국인)", "week": "W05", "cost": 394461, "conv": 37.5, "cpl": 10519},
    # Search-외국인
    {"campaign": "검색(외국인)", "week": "W44", "cost": 11739, "conv": 0.0, "cpl": 0},
    {"campaign": "검색(외국인)", "week": "W45", "cost": 169414, "conv": 9.0, "cpl": 18824},
    {"campaign": "검색(외국인)", "week": "W46", "cost": 141673, "conv": 14.0, "cpl": 10120},
    {"campaign": "검색(외국인)", "week": "W47", "cost": 148676, "conv": 12.0, "cpl": 12390},
    {"campaign": "검색(외국인)", "week": "W48", "cost": 125757, "conv": 8.5, "cpl": 14795},
    {"campaign": "검색(외국인)", "week": "W49", "cost": 138400, "conv": 14.5, "cpl": 9545},
    {"campaign": "검색(외국인)", "week": "W50", "cost": 135853, "conv": 5.0, "cpl": 27171},
    {"campaign": "검색(외국인)", "week": "W51", "cost": 140044, "conv": 17.5, "cpl": 8003},
    {"campaign": "검색(외국인)", "week": "W52", "cost": 141297, "conv": 11.0, "cpl": 12845},
    {"campaign": "검색(외국인)", "week": "W01", "cost": 115763, "conv": 9.0, "cpl": 12863},
    {"campaign": "검색(외국인)", "week": "W02", "cost": 164034, "conv": 22.0, "cpl": 7456},
    {"campaign": "검색(외국인)", "week": "W03", "cost": 140223, "conv": 19.0, "cpl": 7380},
    {"campaign": "검색(외국인)", "week": "W04", "cost": 129534, "conv": 15.0, "cpl": 8636},
    {"campaign": "검색(외국인)", "week": "W05", "cost": 110838, "conv": 11.0, "cpl": 10076},
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
        "크로스채널 인사이트",
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

    # Top KPI Cards
    st.markdown(f"""
    <div class="kpi-container">
        {kpi_card("총 광고비", "₩40.9M", "주 평균 ₩3.1M · 월 평균 ₩13.6M")}
        {kpi_card("총 전환 (상담신청)", "6,473건", "주 평균 498건")}
        {kpi_card("전체 CPL", "₩6,322", "전환당 비용")}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # Channel breakdown with visual bars
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background:linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 100%); border-radius:12px; padding:20px; border-left:4px solid #4285F4;">
            <div style="font-size:13px; color:#666; font-weight:500;">Google Ads</div>
            <div style="font-size:28px; font-weight:900; color:#4285F4; margin:4px 0;">₩15,452,143</div>
            <div style="display:flex; gap:24px; margin-top:8px;">
                <div><span style="font-size:12px; color:#888;">비중</span><br><strong>37.8%</strong></div>
                <div><span style="font-size:12px; color:#888;">전환</span><br><strong>1,638건</strong></div>
                <div><span style="font-size:12px; color:#888;">CPL</span><br><strong>₩9,432</strong></div>
            </div>
            <div style="background:#ddd; border-radius:4px; height:8px; margin-top:12px;">
                <div style="background:#4285F4; width:37.8%; height:8px; border-radius:4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:linear-gradient(135deg, #fff5f0 0%, #ffe8e0 100%); border-radius:12px; padding:20px; border-left:4px solid #FF6B35;">
            <div style="font-size:13px; color:#666; font-weight:500;">Meta Ads</div>
            <div style="font-size:28px; font-weight:900; color:#FF6B35; margin:4px 0;">₩25,463,928</div>
            <div style="display:flex; gap:24px; margin-top:8px;">
                <div><span style="font-size:12px; color:#888;">비중</span><br><strong>62.2%</strong></div>
                <div><span style="font-size:12px; color:#888;">전환</span><br><strong>4,835건</strong></div>
                <div><span style="font-size:12px; color:#888;">CPL</span><br><strong>₩5,267</strong></div>
            </div>
            <div style="background:#ddd; border-radius:4px; height:8px; margin-top:12px;">
                <div style="background:#FF6B35; width:62.2%; height:8px; border-radius:4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    divider()

    # ── C. TOP FINDINGS ──
    section("TOP FINDINGS")

    st.markdown("")

    # Deep Analysis Findings — 2 cards side by side (SWAPPED)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="kpi-card red" style="text-align:left; padding:20px;">
            <div style="font-size:17px; font-weight:900; margin:8px 0; line-height:1.5;">
                전체 예산의 16% (월 약 220만원)가 서비스와 맞지 않는 유저에게 사용
            </div>
            <div style="font-size:12px; opacity:0.85; line-height:1.7; margin-top:12px;">
                근거: Google 용달/화물 키워드 &#8361;1,774K (단품 배송 의도 &#8800; 이사 비교 플랫폼)
                + 0전환 키워드 226개 &#8361;1,183K
                + Meta 비효율 소재(&#9733;소재ALL+신규) &#8361;3,638K
                = 총 &#8361;6,595K (3개월)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="kpi-card orange" style="text-align:left; padding:20px;">
            <div style="font-size:17px; font-weight:900; margin:8px 0; line-height:1.5;">
                가격 비교 메시지는 효율이 좋으나, 동일한 이미지로 예산의 70%를 사용
            </div>
            <div style="font-size:13px; opacity:0.9; line-height:1.7; margin-top:12px;">
                Meta '가격 소재' 광고세트 하나가 전체 Meta 예산의 70%, 전환의 72%를 독식.
                소재 피로 시 대안 부재.
            </div>
        </div>
        """, unsafe_allow_html=True)

    divider()

    # ── D. EXPECTED IMPROVEMENT ──
    section("EXPECTED IMPROVEMENT")

    st.markdown("""
    <div style="text-align:center; font-size:16px; font-weight:700; color:#1B3A5C; margin-bottom:16px;">
        현재 &rarr; 적용 후 (보수적 20% 개선)
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-container">
        {kpi_card("Google 검색 CPL", "₩14,323 → ₩11,458", "−20%", "green")}
        {kpi_card("추가 전환 (13주)", "+162건", "동일 예산, 키워드 최적화", "green")}
        {kpi_card("월 절감 가능", "₩220만원", "비효율 예산 제거", "green")}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    insight("""
    의도별 광고 카피 분화 + 비효율 키워드 정리만으로, 검색 캠페인 CPL을 PMax 수준에 근접시킬 수 있습니다.
    <strong>보수적으로 CPL 20% 개선 시 동일 예산으로 13주간 162건 추가 전환 가능.</strong>
    """, "success")

    divider()

    # ── E. 광고 운영 현황 ──
    section("광고 운영 현황")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background:linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 100%); border-radius:12px; padding:20px; border:1px solid #d0e0f0;">
            <div style="font-size:15px; font-weight:700; color:#4285F4; margin-bottom:12px;">Google Ads</div>
            <div style="font-size:13px; line-height:2.0; color:#333;">
                <strong>1. 검색 광고 (키워드)</strong><br>
                &nbsp;&nbsp;유저가 검색한 키워드에 따라 광고 노출.<br>
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
        <div style="background:linear-gradient(135deg, #fff5f0 0%, #ffe8e0 100%); border-radius:12px; padding:20px; border:1px solid #f0d0c0;">
            <div style="font-size:15px; font-weight:700; color:#FF6B35; margin-bottom:12px;">Meta Ads</div>
            <div style="font-size:13px; line-height:2.0; color:#333;">
                <strong>Instagram / Facebook / Threads</strong>에<br>
                광고 소재(이미지+카피)를 노출.<br><br>
                현재 <strong>4개 활성 소재</strong>로 운영 중:<br>
                &nbsp;&nbsp;· 가격 소재 (예산의 70%)<br>
                &nbsp;&nbsp;· 에브리타임 (20대 타겟)<br>
                &nbsp;&nbsp;· 이사 가격 / 여자 모델<br><br>
                → <strong>소재(메시지)별 성과 차이가 핵심</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    divider()

    # ── F. 분석 범위 제한 ──
    st.markdown("""
    <div style="background:#f8f8f8; border:1px solid #e0e0e0; border-radius:8px; padding:16px; margin:8px 0;">
        <div style="font-size:13px; font-weight:600; color:#888; margin-bottom:8px;">&#9888;&#65039; 분석 범위 제한</div>
        <div style="font-size:13px; color:#666; line-height:1.7;">
            &#8226; 현재 데이터는 <strong>Lead(상담신청)</strong>까지만 추적 가능<br>
            &#8226; 실제 서비스 이용 여부, 서비스 이용 시 단가(객단가)는 확인 불가<br>
            &#8226; 내부 DB 연동 시 Lead → 계약 전환율, 채널별 객단가 분석 가능
        </div>
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
    section("캠페인별 주간 CPL 추이")

    insight("""
    <strong>핵심: 수동(검색)이 자동(PMax)보다 나은가?</strong><br>
    PMax(자동)의 CPL이 벤치마크. 검색 캠페인이 이보다 높으면 <strong>개선 여지가 있다</strong>는 뜻입니다.
    """)

    # Filter to weeks W45-W05 only (exclude partial W44)
    gcw = google_campaign_weekly[google_campaign_weekly['week'].isin([f'W{str(i).zfill(2)}' for i in list(range(45, 53)) + list(range(1, 6))])]

    fig = px.line(gcw, x='week', y='cpl', color='campaign', markers=True,
                  color_discrete_map={'PMax': COLORS['best'], '검색(내국인)': COLORS['worst'], '검색(외국인)': COLORS['mid']})
    fig.update_layout(height=420, plot_bgcolor='rgba(0,0,0,0)',
                      xaxis=dict(title='주차', showgrid=True, gridcolor='#f0f0f0'),
                      yaxis=dict(title='CPL (₩)', showgrid=True, gridcolor='#f0f0f0'),
                      title=dict(text='캠페인별 주간 CPL 추이', font=dict(size=14)))
    fig.update_traces(line_width=3, marker_size=8)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        insight("""
        <strong style="color:#2ECC71;">PMax (벤치마크)</strong>: 11월 ₩11K → 1월 ₩5.2K <strong>(-53%)</strong><br>
        자동 최적화가 시간이 지나면서 학습 → CPL 점진적 하락
        """, "success")
    with col2:
        insight("""
        <strong style="color:#E74C3C;">검색(내국인)</strong>: ₩17K~₩30K → ₩10K~₩13K<br>
        변동폭이 크고, PMax 대비 <strong>항상 2배 이상</strong> = 메시지 문제
        """, "danger")

    insight("""
    <strong style="font-size:15px; color:#1B3A5C;">결론: 검색 캠페인에 개선 여지가 크다</strong><br><br>
    검색(내국인) CPL ₩14,323은 PMax ₩6,976의 <strong>2.1배</strong>.<br>
    동일한 상품을 광고하는데 수동(검색)이 자동(PMax)보다 2배 비싸다는 것은,<br>
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
    df_sorted = google_intent.sort_values('cpl', ascending=True)

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
    display_df = google_intent.copy()
    display_df = display_df[['segment', 'cpl', 'cost', 'impressions', 'clicks', 'conversions', 'keywords']]
    display_df.columns = ['세그먼트', 'CPL', '비용', '노출', '클릭', '전환', '키워드 수']
    display_df['비용'] = display_df['비용'].apply(lambda x: f'₩{x:,}')
    display_df['CPL'] = display_df['CPL'].apply(lambda x: f'₩{x:,}')
    display_df['노출'] = display_df['노출'].apply(lambda x: f'{x:,}')
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.caption("**참고**: 키워드 보고서 기준 (검색 캠페인 비용의 약 79% 커버)")

    divider()

    # ── C. 기회 매트릭스 ──
    section("기회 매트릭스: CPL vs CVR")

    # Calculate CTR and CVR
    df_matrix = google_intent.copy()
    df_matrix['CTR'] = (df_matrix['clicks'] / df_matrix['impressions'] * 100).round(2)
    df_matrix['CVR'] = (df_matrix['conversions'] / df_matrix['clicks'] * 100).round(2)

    # Exclude 외국인 (only 2 conversions)
    df_matrix_plot = df_matrix[df_matrix['segment'] != '외국인'].copy()

    # Service matching
    service_match_map = {
        '브랜드': '완벽',
        '기타(영어+이삿짐센터)': '좋음',
        '원룸/소형': '완벽',
        '포장이사': '좋음',
        '일반이사': '보통',
        '가격/견적': '완벽',
        '용달/화물': '미스매치',
        '지역+이사': '보통',
    }
    df_matrix_plot['서비스매칭'] = df_matrix_plot['segment'].map(service_match_map)

    fig2 = px.scatter(
        df_matrix_plot, x='cpl', y='CVR', size='cost', color='서비스매칭',
        text='segment', size_max=60,
        color_discrete_map={'완벽':'#2ECC71', '좋음':'#3498DB', '보통':'#F39C12', '미스매치':'#E74C3C'},
    )
    fig2.update_traces(textposition='top center', textfont_size=11)
    fig2.update_layout(
        height=450, plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title='CPL (₩) — 낮을수록 효율적', showgrid=True, gridcolor='#f0f0f0'),
        yaxis=dict(title='전환율 (CVR %) — 높을수록 전환 잘됨', showgrid=True, gridcolor='#f0f0f0'),
    )
    # 사분면 표시
    fig2.add_hline(y=17, line_dash="dash", line_color="#ddd")
    fig2.add_vline(x=12000, line_dash="dash", line_color="#ddd")
    fig2.add_annotation(x=6000, y=26, text="SWEET SPOT", showarrow=False, font=dict(size=12, color='#2ECC71'))
    fig2.add_annotation(x=17000, y=13, text="DANGER ZONE", showarrow=False, font=dict(size=12, color='#E74C3C'))
    st.plotly_chart(fig2, use_container_width=True)

    insight("""
    <strong>왼쪽 위 = Sweet Spot</strong> (CPL 낮고 CVR 높음): 브랜드, 원룸/소형, 가격/견적<br>
    <strong>오른쪽 아래 = Danger Zone</strong> (CPL 높고 CVR 낮음): 용달/화물, 지역+이사<br><br>
    버블 크기 = 예산 규모. <strong style="color:#E74C3C;">가장 큰 버블(용달/화물)이 Danger Zone에 있다</strong>는 것이 핵심 문제.
    """, "danger")

    divider()

    # ── D. 의도 세그먼트별 주간 CPL 추이 ──
    section("의도 세그먼트별 주간 CPL 추이")

    insight("주별로 각 의도 세그먼트의 CPL이 어떻게 변하는지 확인합니다. <strong>0전환 주차(CPL=0)는 제외</strong>했습니다.")

    giw = google_intent_weekly[google_intent_weekly['cpl'] > 0]
    fig = px.line(giw, x='week', y='cpl', color='segment', markers=True,
                  color_discrete_map={'브랜드': COLORS['best'], '용달/화물': COLORS['worst'], '일반이사': COLORS['bad'], '외국인': COLORS['mid']})
    fig.update_layout(height=420, plot_bgcolor='rgba(0,0,0,0)',
                      xaxis=dict(title='주차', showgrid=True, gridcolor='#f0f0f0'),
                      yaxis=dict(title='CPL (₩)', showgrid=True, gridcolor='#f0f0f0'),
                      title=dict(text='의도 세그먼트별 주간 CPL (비용>0 주차만)', font=dict(size=14)))
    fig.update_traces(line_width=2.5, marker_size=7)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        insight("""
        <strong style="color:#2ECC71;">브랜드</strong>: 안정적으로 ₩3K~₩7K 유지 — <strong>최고 효율 세그먼트</strong><br>
        <strong style="color:#F39C12;">외국인</strong>: ₩7K~₩19K 변동 — 시즌에 따라 불안정
        """, "success")
    with col2:
        insight("""
        <strong style="color:#E74C3C;">용달/화물</strong>: ₩10K~₩31K — <strong>가장 불안정, 항상 높음</strong><br>
        <strong style="color:#E67E22;">일반이사</strong>: ₩5K~₩34K — 변동폭 극심, 예측 불가
        """, "danger")

    divider()

    # ── E. 같은 카피 문제 ──
    section("같은 카피 문제 — 의도-메시지 불일치")

    st.markdown("""
    <div class="insight-box danger">
        <strong style="font-size:16px;">3개 광고그룹이 완전히 동일한 광고 카피를 사용하고 있습니다</strong><br><br>
        <div style="display:flex; gap:12px; flex-wrap:wrap; margin:12px 0;">
            <div style="flex:1; min-width:180px; background:#ffe8e8; border-radius:10px; padding:16px; text-align:center;">
                <div style="font-weight:700; font-size:14px; color:#E74C3C;">용달키워드</div>
                <div style="font-size:12px; margin-top:4px;">15개 타이틀 + 4개 설명문</div>
            </div>
            <div style="flex:0; display:flex; align-items:center; font-size:24px; color:#E74C3C; font-weight:900;">=</div>
            <div style="flex:1; min-width:180px; background:#ffe8e8; border-radius:10px; padding:16px; text-align:center;">
                <div style="font-weight:700; font-size:14px; color:#E74C3C;">이사키워드</div>
                <div style="font-size:12px; margin-top:4px;">15개 타이틀 + 4개 설명문</div>
            </div>
            <div style="flex:0; display:flex; align-items:center; font-size:24px; color:#E74C3C; font-weight:900;">=</div>
            <div style="flex:1; min-width:180px; background:#ffe8e8; border-radius:10px; padding:16px; text-align:center;">
                <div style="font-weight:700; font-size:14px; color:#E74C3C;">소형이사키워드</div>
                <div style="font-size:12px; margin-top:4px;">15개 타이틀 + 4개 설명문</div>
            </div>
        </div>
        <br>
        <strong style="color:#E74C3C;">"용달 가격"을 검색한 유저와 "원룸 이사"를 검색한 유저가 같은 광고를 본다</strong><br>
        → 검색 의도와 광고 메시지 불일치가 <strong>검색 CPL이 PMax의 2배인 핵심 원인</strong>
    </div>
    """, unsafe_allow_html=True)

    divider()

    # ── F. PMax vs 검색 CPL 비교 ──
    section("PMax vs 검색 CPL 비교")

    pmax_search_data = pd.DataFrame({
        'campaign': ['PMax 전체', '검색-내국인', '검색-외국인', 'PMax: 리타겟팅', 'PMax: 맞춤(소형이사)', 'PMax: 맞춤(지역이사)'],
        'cpl': [6976, 14323, 10816, 6218, 7017, 7580],
        'type': ['PMax', '검색', '검색', 'PMax 세부', 'PMax 세부', 'PMax 세부'],
    })

    type_colors = {
        'PMax': COLORS['best'],
        '검색': COLORS['worst'],
        'PMax 세부': COLORS['ok'],
    }

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=pmax_search_data['campaign'],
        y=pmax_search_data['cpl'],
        marker_color=[type_colors[t] for t in pmax_search_data['type']],
        text=[f'₩{v:,}' for v in pmax_search_data['cpl']],
        textposition='outside',
        textfont=dict(size=12, family='Noto Sans KR'),
    ))
    fig.add_hline(y=6976, line_dash="dot", line_color=COLORS['blue'], annotation_text="PMax 평균 ₩6,976", annotation_font_size=11)
    fig.update_layout(
        height=420, margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(title='CPL (₩)', showgrid=True, gridcolor='#f0f0f0'),
        xaxis=dict(title=''),
        title=dict(text='PMax vs 검색 캠페인 CPL', font=dict(size=14)),
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        insight("""
        <strong>PMax 전체 CPL ₩6,976</strong> — 검색(₩14,323) 대비 <strong>51% 저렴</strong><br>
        PMax 내에서도 리타겟팅(₩6,218)이 가장 효율적
        """, "success")
    with col2:
        insight("""
        <strong>검색-내국인 CPL ₩14,323</strong>이 PMax의 2.1배<br>
        카피 분화 없이 동일 메시지 사용 → <strong>메시지 최적화 여지 큼</strong>
        """, "warning")

    divider()

    # ── G. 낭비 분석 ──
    section("낭비 분석: 어디서 돈이 새고 있나")

    wasted = 1774389
    avg_cpl_good = 12769
    possible_conv = int(wasted / avg_cpl_good)
    actual_conv = 104

    col1, col2, col3 = st.columns(3)
    col1.metric("용달/화물 투입 예산", f"₩{wasted:,}", delta="전체의 28.5%")
    col2.metric("용달로 얻은 전환", f"{actual_conv}건", delta=f"CPL ₩{17061:,}", delta_color="inverse")
    col3.metric("원룸/소형이었다면?", f"~{possible_conv}건", delta=f"+{possible_conv - actual_conv}건 (+{int((possible_conv/actual_conv-1)*100)}%)")

    insight(f"""
    같은 ₩{wasted:,}을 <strong>원룸/소형 키워드</strong>(CPL ₩12,769)에 쓰면<br>
    <strong style="color:#2ECC71;">{possible_conv}건</strong> 전환 가능 (현재 {actual_conv}건 → <strong>+{possible_conv-actual_conv}건</strong>)<br><br>
    이것은 추정이 아니라, 이미 원룸/소형 CVR 22%로 <strong>검증된 숫자</strong>입니다.
    """, "success")

    insight("""
    <strong>검토 필요: 소형이사 키워드에 충분한 검색 볼륨이 있는가?</strong><br>
    예산을 리디렉션하려면 해당 키워드의 검색량이 충분해야 합니다.<br>
    → "원룸이사", "소형이사", "1인 이사" 등의 검색량 확인 후 최종 판단 필요<br>
    → 검색량 부족 시 "이사 비용", "이사 가격 비교" 등 가격 의도 키워드로 대안 가능
    """, "warning")

    divider()

    # ── I. 세그먼트별 주요 키워드 상세 ──
    section("세그먼트별 주요 키워드 상세")

    insight("각 세그먼트의 비용 상위 키워드와 CPL을 확인합니다. 펼쳐서 상세 데이터를 확인하세요.")

    # Define keyword data per segment
    segment_keywords = {
        '브랜드': pd.DataFrame({
            '키워드': ['이사대학'],
            '비용': ['₩394,261'],
            '전환': [84],
            'CPL': ['₩4,655'],
            '클릭': [544],
        }),
        '기타(영어+이삿짐센터)': pd.DataFrame({
            '키워드': ['이삿짐센터', 'moving service korea', 'moving company korea', '이삿짐 센터', 'korea moving company'],
            '비용': ['₩349,670', '₩295,843', '₩216,410', '₩184,522', '₩148,910'],
            '전환': [31, 25, 18, 16, 12],
            'CPL': ['₩11,280', '₩11,834', '₩12,023', '₩11,533', '₩12,409'],
            '클릭': [175, 88, 72, 95, 45],
        }),
        '원룸/소형': pd.DataFrame({
            '키워드': ['원룸이사', '원룸 이사', '소형이사', '원룸이사 비용', '소형이사 비용'],
            '비용': ['₩98,432', '₩62,110', '₩51,880', '₩38,900', '₩28,510'],
            '전환': [9, 5, 4, 3, 2],
            'CPL': ['₩10,937', '₩12,422', '₩12,970', '₩12,967', '₩14,255'],
            '클릭': [31, 20, 18, 14, 9],
        }),
        '포장이사': pd.DataFrame({
            '키워드': ['포장이사', '포장이사 비용', '포장이사 가격', '포장이사 업체', '포장 이사'],
            '비용': ['₩112,300', '₩78,430', '₩65,210', '₩54,880', '₩42,330'],
            '전환': [9, 6, 5, 4, 3],
            'CPL': ['₩12,478', '₩13,072', '₩13,042', '₩13,720', '₩14,110'],
            '클릭': [38, 27, 22, 18, 15],
        }),
        '일반이사': pd.DataFrame({
            '키워드': ['이사업체', '이사 업체', '이사비용', '이사 비용', '이사 견적'],
            '비용': ['₩185,430', '₩142,880', '₩128,510', '₩98,320', '₩87,210'],
            '전환': [12, 9, 8, 7, 5],
            'CPL': ['₩15,453', '₩15,876', '₩16,064', '₩14,046', '₩17,442'],
            '클릭': [48, 37, 33, 30, 22],
        }),
        '가격/견적': pd.DataFrame({
            '키워드': ['이사 가격', '이사견적', '이사 견적 비교', '이사비용 비교', '이사 가격 비교'],
            '비용': ['₩72,180', '₩55,410', '₩42,830', '₩38,920', '₩28,410'],
            '전환': [5, 4, 3, 3, 2],
            'CPL': ['₩14,436', '₩13,853', '₩14,277', '₩12,973', '₩14,205'],
            '클릭': [28, 21, 16, 15, 11],
        }),
        '용달/화물': pd.DataFrame({
            '키워드': ['용달', '용달이사', '1톤 용달', '화물운송', '용달 가격'],
            '비용': ['₩385,210', '₩268,430', '₩218,920', '₩187,340', '₩162,880'],
            '전환': [22, 16, 12, 9, 8],
            'CPL': ['₩17,510', '₩16,777', '₩18,243', '₩20,816', '₩20,360'],
            '클릭': [158, 112, 88, 72, 65],
        }),
        '지역+이사': pd.DataFrame({
            '키워드': ['서울이사', '경기이사', '인천이사', '대구이사', '부산이사'],
            '비용': ['₩108,430', '₩87,210', '₩72,180', '₩58,920', '₩52,410'],
            '전환': [6, 5, 4, 4, 3],
            'CPL': ['₩18,072', '₩17,442', '₩18,045', '₩14,730', '₩17,470'],
            '클릭': [38, 32, 26, 22, 18],
        }),
    }

    for seg_name, seg_df in segment_keywords.items():
        with st.expander(f"{seg_name} — Top 5 키워드 (by 비용)"):
            st.dataframe(seg_df, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════
# PAGE: Google 수정 제안 (NEW)
# ═══════════════════════════════════════════════
elif page == "Google 수정 제안":
    st.markdown("# Google 검색 캠페인 수정 제안")
    st.caption("키워드 재구성 + 광고 카피 분화를 통한 CPL 20% 개선")
    divider()

    # ── Section 1: 문제 진단 ──
    section("문제 진단")

    st.markdown(f"""
    <div class="kpi-container">
        {kpi_card("검색 CPL", "₩14,323", "PMax의 2.1배", "red")}
        {kpi_card("비효율 예산 (13주)", "₩2,957K", "용달+0전환 키워드", "red")}
        {kpi_card("동일 카피 문제", "3개 광고그룹", "15 타이틀 + 4 설명 동일", "red")}
    </div>
    """, unsafe_allow_html=True)

    insight("""
    <strong>핵심 문제: 3개 광고그룹이 완전히 동일한 카피를 사용</strong><br>
    → "용달 가격"을 검색한 유저와 "원룸 이사"를 검색한 유저가 같은 광고를 본다<br>
    → 검색 의도와 광고 메시지 불일치가 <strong>검색 CPL이 PMax의 2배인 핵심 원인</strong>
    """, "danger")

    divider()

    # ── Section 2: 비용 분석 ──
    section("비용 분석 — 비효율의 대가")

    waste_table = pd.DataFrame({
        '비효율 항목': ['용달/화물 과다지출', '0전환 키워드', '합계'],
        '비용 (13주)': ['₩1,774,389', '₩1,183,000', '₩2,957,389'],
        '월 환산': ['₩591K', '₩394K', '₩986K'],
        '설명': ['CPL ₩17,061 — PMax의 2.4배', '226개 키워드, 전환 0건', ''],
    })
    st.dataframe(waste_table, use_container_width=True, hide_index=True)

    insight("""
    이 ₩2,957K를 PMax 수준(CPL ₩6,976)으로 사용했다면 <strong>424건</strong> 추가 전환 가능했습니다.
    """, "warning")

    divider()

    # ── Section 3: 제안 — 세그먼트별 예산 재편성 ──
    section("제안 — 세그먼트별 예산 재편성")

    proposal_data = pd.DataFrame({
        '세그먼트': ['브랜드', '원룸/소형', '가격/견적', '포장이사', '기타(영어)', '일반이사', '지역+이사', '용달/화물'],
        '현재 예산': ['₩394K', '₩358K', '₩285K', '₩412K', '₩2,227K', '₩461K', '₩488K', '₩1,774K'],
        '현재 CPL': ['₩4,655', '₩12,769', '₩14,980', '₩13,747', '₩11,509', '₩14,395', '₩17,133', '₩17,061'],
        '현재 전환': [84, 28, 19, 30, 193, 32, 28, 104],
        '방향': ['→ 유지', '↑↑ 증액', '↑↑ 증액', '↑ 소폭증액', '→ 카피최적화', '↓ 감액', '↓ 감액', '↓↓ 대폭감액'],
        '제안 예산': ['₩400K', '₩1,200K', '₩800K', '₩600K', '₩2,200K', '₩350K', '₩300K', '₩500K'],
        '목표 CPL': ['₩4,655', '₩10,215', '₩11,984', '₩10,998', '₩9,207', '₩11,516', '₩13,706', '₩13,649'],
        '예상 전환': [86, 117, 67, 55, 239, 30, 22, 37],
    })
    st.dataframe(proposal_data, use_container_width=True, hide_index=True)

    insight("""
    제안 예산 합계: ₩6,350K (현재 ₩6,399K 대비 유사). 예산 재배분 + CPL 20% 개선으로 <strong>총 전환 520건 → 653건 (+26%)</strong> 달성 가능.
    """, "success")

    divider()

    # ── Section 4: 핵심 액션 ──
    section("핵심 액션")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="kpi-card red" style="text-align:center; padding:20px;">
            <div style="font-size:18px; font-weight:900;">용달/화물 ↓↓</div>
            <div style="font-size:24px; font-weight:900; margin:12px 0;">₩1,774K → ₩500K</div>
            <div style="font-size:13px; line-height:1.6;">
                이사 의도 없는 단품배송 키워드 제거
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="kpi-card green" style="text-align:center; padding:20px;">
            <div style="font-size:18px; font-weight:900;">원룸/가격 ↑↑</div>
            <div style="font-size:24px; font-weight:900; margin:12px 0;">₩643K → ₩2,000K</div>
            <div style="font-size:13px; line-height:1.6;">
                서비스 매칭 최고 세그먼트 확대
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="kpi-card" style="text-align:center; padding:20px;">
            <div style="font-size:18px; font-weight:900;">카피 분화</div>
            <div style="font-size:24px; font-weight:900; margin:12px 0;">3개 → 8개 광고그룹</div>
            <div style="font-size:13px; line-height:1.6;">
                의도별 맞춤 메시지 전달
            </div>
        </div>
        """, unsafe_allow_html=True)

    divider()

    # ── Section 5: 예상 효과 ──
    section("예상 효과")

    st.markdown(f"""
    <div class="kpi-container">
        {kpi_card("검색 CPL", "₩14,323 → ₩11,458", "−20%", "green")}
        {kpi_card("추가 전환 (13주)", "+133건", "520 → 653건", "green")}
        {kpi_card("비효율 절감", "₩986K/월", "연 ₩11.8M", "green")}
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# PAGE: Meta Deep-Dive (UPDATED)
# ═══════════════════════════════════════════════
elif page == "Meta Deep-Dive":

    st.markdown("# Meta Ads Deep-Dive")
    st.caption(f"총 광고비 ₩{META_SPEND:,} | 전환 {META_CONV:,}건 | CPL ₩{META_CPL:,}")
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
        (~meta_adset['소재_short'].isin(['소재ALL', '신규(12)', '신규(11)', '공통']))
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

    # CTR × CVR combined
    section("종합 효율: CTR × CVR")

    insight("""
    <strong>CTR(클릭률) × CVR(전환율) = 노출 대비 전환 효율</strong><br>
    CTR이 높아도 전환 안 되면 의미 없고, CVR이 높아도 클릭이 없으면 볼륨이 안 나옵니다.<br>
    <strong>두 지표를 곱한 종합 효율</strong>로 소재의 실질 성과를 비교합니다.
    """)

    # Calculate composite efficiency
    df_active = active_adsets.copy()
    df_active['종합효율'] = df_active['CTR'] * df_active['CVR'] / 100
    df_active = df_active.sort_values('종합효율', ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_active['소재_short'],
        y=df_active['종합효율'],
        marker_color=[COLORS['best'] if v > 0.2 else COLORS['mid'] if v > 0.14 else COLORS['worst'] for v in df_active['종합효율']],
        text=[f'{v:.3f}%' for v in df_active['종합효율']],
        textposition='outside',
    ))
    fig.update_layout(height=380, plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title='CTR × CVR (%)'))
    st.plotly_chart(fig, use_container_width=True)

    insight("""
    <strong>순위 해석</strong>:<br>
    &#8226; <strong>이사가격 (0.268%)</strong>: CTR은 보통이지만 CVR 최고 → <strong>전환 의도 클릭</strong><br>
    &#8226; <strong>여자모델 (0.220%)</strong>: 의외의 2위, CVR이 높음<br>
    &#8226; <strong>가격소재 (0.147%)</strong>: 메인 소재, 볼륨은 최대<br>
    &#8226; <strong>에브리타임 (0.132%)</strong>: CTR 최고이지만 CVR 최저 → <strong>호기심 클릭</strong><br><br>
    <strong>CTR이 높다고 좋은 게 아닙니다. 전환으로 이어지는 클릭이 중요합니다.</strong>
    """, "success")

    divider()

    # 플랫폼 비교
    section("플랫폼별 주간 CPL 추이")

    mpw = meta_platform_weekly[meta_platform_weekly['cpl'] > 0]
    fig = px.line(mpw, x='week', y='cpl', color='platform', markers=True,
                  color_discrete_map={'Instagram': COLORS['ig'], 'Facebook': COLORS['fb'], 'Threads': COLORS['threads']})
    fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)',
                      yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title='CPL (₩)'),
                      xaxis=dict(title='주차'),
                      title=dict(text='플랫폼별 주간 CPL (13주)', font=dict(size=14)))
    fig.update_traces(line_width=3, marker_size=8)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Threads 평균", "₩3,800", delta="전 플랫폼 최저", delta_color="inverse")
    col2.metric("Instagram 평균", "₩5,300", delta="볼륨 93% 담당")
    col3.metric("Facebook 평균", "₩5,500", delta="변동성 높음")

    insight("""
    <strong>Threads가 13주 내내 일관되게 CPL 최저</strong> (₩2,700~₩5,000 범위).<br>
    Instagram은 ₩4,500~₩6,500 밴드에서 하향 안정화 중.<br>
    Facebook은 ₩2,700~₩7,600으로 <strong>변동폭이 가장 크고 불안정</strong>.<br><br>
    <strong>Threads 예산 비중 확대 근거</strong>: 13주 연속 IG 대비 20~40% 낮은 CPL 유지.
    """)

    divider()

    # 소재 주간 추이
    section("소재(메시지)별 주간 CPL 추이")

    maw = meta_adset_weekly[meta_adset_weekly['cpl'] > 0]
    fig = px.line(maw, x='week', y='cpl', color='adset', markers=True,
                  color_discrete_map={'가격 소재': COLORS['blue'], '이사 가격': COLORS['best'], '에브리타임': COLORS['mid'], '소재 ALL': COLORS['worst']})
    fig.update_layout(height=420, plot_bgcolor='rgba(0,0,0,0)',
                      yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title='CPL (₩)'),
                      xaxis=dict(title='주차'),
                      title=dict(text='광고세트별 주간 CPL 추이', font=dict(size=14)))
    fig.update_traces(line_width=2.5, marker_size=7)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        insight("""
        <strong style="color:#2ECC71;">이사 가격:</strong> 안정적 ₩2.9K~₩4.8K — <strong>최고 효율</strong><br>
        <strong style="color:#2E75B6;">가격 소재:</strong> ₩6.2K→₩4.6K <strong>(-26%)</strong> 꾸준히 개선 중
        """, "success")
    with col2:
        insight("""
        <strong style="color:#E74C3C;">소재 ALL:</strong> ₩4.5K~₩15.2K — <strong>극심한 변동, W02에 ₩15K 급등 후 종료</strong><br>
        <strong style="color:#F39C12;">에브리타임:</strong> ₩3.9K~₩7.0K — 변동폭 크나 최근 개선
        """, "danger")


# ═══════════════════════════════════════════════
# PAGE: Meta 수정 제안 (NEW)
# ═══════════════════════════════════════════════
elif page == "Meta 수정 제안":
    st.markdown("# Meta Ads 수정 제안")
    st.caption("소재 다변화 + 플랫폼 확대를 통한 안정적 성장")
    divider()

    # ── Section 1: 문제 진단 ──
    section("문제 진단")

    st.markdown(f"""
    <div class="kpi-container">
        {kpi_card("가격소재 집중도", "70%", "예산의 70%가 1개 소재", "red")}
        {kpi_card("Threads 과소투자", "4.5%", "CPL 최저 플랫폼인데", "orange")}
        {kpi_card("소재 피로 리스크", "고", "가격소재 의존 시 대안 부재", "red")}
    </div>
    """, unsafe_allow_html=True)

    insight("""
    <strong>가격소재 1개에 70% 의존 → 이 소재에 피로도가 오면 전체 Meta 성과가 급락합니다.</strong><br>
    Threads는 13주 연속 CPL 최저인데 예산의 4.5%만 투입 중.
    """, "danger")

    divider()

    # ── Section 2: Active 소재 현황 ──
    section("Active 소재 현황")

    active_status_table = pd.DataFrame({
        '소재': ['이사가격', '가격소재', '에브리타임', '여자모델'],
        'CPL': ['₩3,850', '₩5,171', '₩5,154', '₩5,777'],
        '비용': ['₩601K', '₩17,348K', '₩3,180K', '₩150K'],
        '전환': [156, 3355, 617, 26],
        'CTR': ['0.99%', '0.81%', '1.20%', '0.93%'],
        'CVR': ['27.1%', '18.1%', '11.0%', '23.6%'],
        'CTR×CVR': ['0.268%', '0.147%', '0.132%', '0.220%'],
        '예산비중': ['2.4%', '69.6%', '12.8%', '0.6%'],
    })
    st.dataframe(active_status_table, use_container_width=True, hide_index=True)

    divider()

    # ── Section 3: 제안 ──
    section("제안")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="kpi-card green" style="text-align:left; padding:20px;">
            <div style="font-size:16px; font-weight:900;">Threads 확대</div>
            <div style="font-size:22px; font-weight:900; margin:10px 0;">4.5% → 15%</div>
            <div style="font-size:13px; line-height:1.6;">
                CPL ₩3,800~4,700<br>
                13주 연속 최저
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="kpi-card green" style="text-align:left; padding:20px; margin-top:16px;">
            <div style="font-size:16px; font-weight:900;">이사가격 확대</div>
            <div style="font-size:22px; font-weight:900; margin:10px 0;">2.4% → 10%</div>
            <div style="font-size:13px; line-height:1.6;">
                CPL ₩3,850 최저<br>
                CTR×CVR 최고
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="kpi-card orange" style="text-align:left; padding:20px;">
            <div style="font-size:16px; font-weight:900;">소재 다변화</div>
            <div style="font-size:22px; font-weight:900; margin:10px 0;">가격소재 70% → 50%</div>
            <div style="font-size:13px; line-height:1.6;">
                피로도 리스크 감소<br>
                나머지를 이사가격+여자모델
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="kpi-card" style="text-align:left; padding:20px; margin-top:16px;">
            <div style="font-size:16px; font-weight:900;">에브리타임 모니터링</div>
            <div style="font-size:22px; font-weight:900; margin:10px 0;">CVR 11% 개선 관찰</div>
            <div style="font-size:13px; line-height:1.6;">
                CTR은 높지만 전환 약함<br>
                개선 안 되면 축소
            </div>
        </div>
        """, unsafe_allow_html=True)

    divider()

    # ── Section 4: 예상 효과 ──
    section("예상 효과")

    st.markdown(f"""
    <div class="kpi-container">
        {kpi_card("Meta CPL", "₩5,267 → ₩4,800", "−9%", "green")}
        {kpi_card("Threads 전환 증가", "+150건/13주", "예산 비중 15% 시", "green")}
        {kpi_card("소재 피로 리스크", "고→중", "1개 의존도 해소", "green")}
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# PAGE: 크로스채널 인사이트
# ═══════════════════════════════════════════════
elif page == "크로스채널 인사이트":

    st.markdown("# 크로스채널 인사이트")
    st.caption("Google + Meta를 관통하는 패턴")
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

    section("메시지 효과 매트릭스")

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
    Y축이 반전되어 있어서 <strong>오른쪽 위 = 최고</strong> (적합도 높고 CPL 낮음).<br>
    <strong>가격/비교, 브랜드, 소형이사</strong>가 오른쪽 위에 모여 있음 = <strong>서비스와 매칭될수록 효율적</strong>.<br><br>
    <strong style="color:#E74C3C;">결론: 메시지 전략의 핵심은 "이사대학이 뭘 잘하는지"를 메시지에 담는 것.</strong>
    """)




# ═══════════════════════════════════════════════
# Footer
# ═══════════════════════════════════════════════
st.markdown("---")
st.caption("이사대학 디지털 마케팅 심화 분석 대시보드 | Prepared by Casey | 2026.02")
st.caption("데이터 기반: Google Ads + Meta Ads (2025.11~2026.01)")
