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
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# Data
# ═══════════════════════════════════════════════

# 채널 종합
TOTAL_SPEND = 41_220_286
TOTAL_CONV = 6_452
TOTAL_CPL = 6_389
GOOGLE_SPEND = 16_300_122
GOOGLE_CONV = 1_758
GOOGLE_CPL = 9_273
META_SPEND = 24_920_164
META_CONV = 4_694
META_CPL = 5_309

# Google 키워드 의도별
google_intent = pd.DataFrame({
    '검색 의도': ['브랜드\n("이사대학")', '원룸/소형이사', '외국인(영어)', '포장이사', '가격/견적', '일반 이사', '지역+이사', '용달/화물'],
    '의도_short': ['브랜드', '원룸/소형', '외국인', '포장이사', '가격/견적', '일반이사', '지역+이사', '용달/화물'],
    '비용': [420424, 214547, 1889192, 443625, 285220, 1029073, 449963, 2626506],
    '전환': [89, 20, 171, 35, 22, 63, 29, 140],
    'CPL': [4741, 10727, 11048, 12675, 13266, 16334, 15788, 18761],
    'CTR': [53.4, 3.1, 10.7, 3.0, 3.8, 3.5, 5.9, 4.7],
    'CVR': [15.4, 27.4, 17.8, 21.3, 19.0, 13.9, 17.8, 12.6],
    '예산비중': [5.7, 2.9, 25.7, 6.0, 3.9, 14.0, 6.1, 35.7],
    '효율': ['BEST', 'CVR최고', '볼륨OK', '보통', '보통', '비효율', '비효율', 'WORST'],
    '서비스매칭': ['완벽', '완벽', '좋음', '좋음', '완벽', '보통', '보통', '미스매치'],
})

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
        "Meta Deep-Dive",
        "크로스채널 인사이트",
        "가설 & 원인 분석",
        "예산 시뮬레이터",
        "테스트 로드맵",
    ], index=0, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**분석 기간**")
    st.caption("2025.11 ~ 2026.01 (3개월)")
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

    st.markdown("# 이사대학 마케팅 심화 분석")
    st.markdown("##### 3개월(2025.11~2026.01) Google Ads + Meta Ads 통합 분석")
    divider()

    # KPI Row
    st.markdown(f"""
    <div class="kpi-container">
        {kpi_card("총 광고비 (3개월)", "₩41,220,286")}
        {kpi_card("총 전환 (상담신청)", "6,452건")}
        {kpi_card("평균 CPL", "₩6,389")}
        {kpi_card("Meta CPL 추세 (1월)", "₩4,664", "↓ 25% vs 11월", "green")}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # 핵심 발견 #1
    section("ONE-LINE FINDING")
    insight("""
    <strong style="font-size:18px; color:#1B3A5C;">
    현재 광고의 핵심 문제는 '채널 선택'이 아니라, 메시지와 유저 의도의 매칭입니다.
    </strong><br><br>
    Google과 Meta 전 채널에서 <strong style="color:#2ECC71;">"가격 비교"</strong> 메시지가 일관되게 최고 효율을 보입니다.
    반면, 예산의 35%가 서비스와 맞지 않는 유저에게 쓰이고 있습니다.
    """, "success")

    divider()

    # 채널 비교
    section("CHANNEL OVERVIEW")
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=['Google Ads', 'Meta Ads'], y=[GOOGLE_SPEND, META_SPEND], marker_color=[COLORS['google'], COLORS['meta']], text=[f'₩{GOOGLE_SPEND:,.0f}', f'₩{META_SPEND:,.0f}'], textposition='inside', textfont=dict(color='white', size=14)))
        fig.update_layout(height=300, margin=dict(l=20,r=20,t=40,b=20), title=dict(text='광고비', font=dict(size=14)), yaxis_title='', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#f0f0f0'))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=['Google Ads', 'Meta Ads'], y=[GOOGLE_CPL, META_CPL], marker_color=[COLORS['google'], COLORS['meta']], text=[f'₩{GOOGLE_CPL:,}', f'₩{META_CPL:,}'], textposition='inside', textfont=dict(color='white', size=16, family='Noto Sans KR')))
        fig.add_hline(y=TOTAL_CPL, line_dash="dot", line_color="#999", annotation_text=f"평균 ₩{TOTAL_CPL:,}", annotation_font_size=11)
        fig.update_layout(height=300, margin=dict(l=20,r=20,t=40,b=20), title=dict(text='CPL (전환당 비용)', font=dict(size=14)), yaxis_title='', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#f0f0f0'))
        st.plotly_chart(fig, use_container_width=True)

    insight(f"""
    Meta가 CPL 기준 <strong>43% 저렴</strong> (₩5,309 vs ₩9,273).<br>
    단, 이것은 <strong>리드 획득 비용</strong>일 뿐 — 리드 품질(상담→계약 전환율)은 아직 미검증.<br>
    Google 리드의 계약율이 Meta보다 2배 높다면, 실제로는 Google이 나을 수 있습니다.
    """, "warning")

    divider()

    # 3대 핵심 발견
    section("TOP 3 FINDINGS")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="kpi-card red" style="text-align:left; padding:20px;">
            <div class="kpi-label">FINDING #1 — 낭비</div>
            <div style="font-size:22px; font-weight:900; margin:8px 0;">₩2,626,506</div>
            <div style="font-size:13px; opacity:0.9; line-height:1.6;">
                Google 예산의 35.7%가 '용달/화물' 키워드에 투입<br>
                CPL ₩18,761 — 전체 최악<br>
                <strong>유저 의도와 서비스 미스매치</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card green" style="text-align:left; padding:20px;">
            <div class="kpi-label">FINDING #2 — 기회</div>
            <div style="font-size:22px; font-weight:900; margin:8px 0;">CVR 27.4%</div>
            <div style="font-size:13px; opacity:0.9; line-height:1.6;">
                '원룸/소형이사' 전환율 최고<br>
                그런데 예산 비중 겨우 2.9%<br>
                <strong>가장 잘 맞는 유저에게 예산이 너무 적음</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card" style="text-align:left; padding:20px;">
            <div class="kpi-label">FINDING #3 — 패턴</div>
            <div style="font-size:22px; font-weight:900; margin:8px 0;">"가격 비교"</div>
            <div style="font-size:13px; opacity:0.9; line-height:1.6;">
                전 채널에서 가격 관련 메시지가 최고 효율<br>
                Google 가격 CPL ₩5,767 / Meta ₩3,850<br>
                <strong>핵심 소구 포인트 = "가격 비교"</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# PAGE: Google Deep-Dive
# ═══════════════════════════════════════════════
elif page == "Google Deep-Dive":

    st.markdown("# Google Ads Deep-Dive")
    st.caption(f"총 광고비 ₩{GOOGLE_SPEND:,} | 전환 {GOOGLE_CONV:,}건 | CPL ₩{GOOGLE_CPL:,}")
    divider()

    # 의도별 분석
    section("유저 검색 의도별 세그먼트 분석")

    insight("""
    <strong>왜 '의도별'로 봐야 하는가?</strong><br>
    같은 Google 검색이라도 "이사대학" 검색과 "용달 가격" 검색은 전혀 다른 유저입니다.<br>
    유저의 <strong>검색 의도(intent)</strong>가 이사대학 서비스와 얼마나 매칭되는지가 전환의 핵심입니다.
    """)

    # CPL Bar + Service Match
    df = google_intent.sort_values('CPL')
    colors = [EFF_COLORS.get(e, '#999') for e in df['효율']]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['의도_short'], y=df['CPL'], marker_color=colors,
        text=[f'₩{v:,}' for v in df['CPL']], textposition='outside',
        textfont=dict(size=13, family='Noto Sans KR'),
    ))
    fig.add_hline(y=GOOGLE_CPL, line_dash="dot", line_color="#ccc", annotation_text=f"Google 평균 ₩{GOOGLE_CPL:,}")
    fig.update_layout(height=380, margin=dict(l=20,r=20,t=20,b=20), plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title='CPL (₩)'), xaxis_title='')
    st.plotly_chart(fig, use_container_width=True)

    # Opportunity Matrix
    section("기회 매트릭스: CPL vs 전환율")

    fig2 = px.scatter(
        google_intent, x='CPL', y='CVR', size='비용', color='서비스매칭',
        text='의도_short', size_max=60,
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
    <strong>왼쪽 위 = Sweet Spot</strong> (CPL 낮고 CVR 높음): 브랜드, 원룸/소형이사<br>
    <strong>오른쪽 아래 = Danger Zone</strong> (CPL 높고 CVR 낮음): 용달/화물, 일반 이사<br><br>
    버블 크기 = 예산 규모. <strong style="color:#E74C3C;">가장 큰 버블(용달/화물)이 Danger Zone에 있다</strong>는 것이 핵심 문제.
    """, "danger")

    divider()

    # 낭비 분석
    section("낭비 분석: 어디서 돈이 새고 있나")

    wasted = 2_626_506
    possible_conv = int(wasted / 6411)  # 소형이사 CPL 기준
    actual_conv = 140

    col1, col2, col3 = st.columns(3)
    col1.metric("용달/화물 투입 예산", f"₩{wasted:,}", delta="전체의 35.7%")
    col2.metric("용달로 얻은 전환", f"{actual_conv}건", delta=f"CPL ₩{18761:,}", delta_color="inverse")
    col3.metric("소형이사였다면?", f"~{possible_conv}건", delta=f"+{possible_conv - actual_conv}건 (+{(possible_conv/actual_conv-1)*100:.0f}%)")

    insight(f"""
    같은 ₩{wasted:,}을 <strong>소형이사 키워드</strong>(CPL ₩6,411)에 쓰면<br>
    <strong style="color:#2ECC71;">{possible_conv}건</strong> 전환 가능 (현재 {actual_conv}건 → <strong>+{possible_conv-actual_conv}건</strong>)<br><br>
    이것은 추정이 아니라, 이미 소형이사 CVR 27.4%로 <strong>검증된 숫자</strong>입니다.
    """, "success")

    divider()

    # 캠페인 & PMax
    section("캠페인 구조")

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(go.Bar(
            x=google_campaign['캠페인'], y=google_campaign['CPL'],
            marker_color=[COLORS['best'], COLORS['worst'], COLORS['mid']],
            text=[f'₩{v:,}' for v in google_campaign['CPL']], textposition='auto',
        ))
        fig.update_layout(height=320, title='캠페인별 CPL', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#f0f0f0'))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure(go.Bar(
            x=pmax_asset['에셋그룹'], y=pmax_asset['CPL'],
            marker_color=[COLORS['blue'], COLORS['best'], COLORS['mid']],
            text=[f'₩{v:,}' for v in pmax_asset['CPL']], textposition='auto',
        ))
        fig.update_layout(height=320, title='PMax 에셋그룹별 CPL', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#f0f0f0'))
        st.plotly_chart(fig, use_container_width=True)

    insight("""
    PMax CPL ₩6,880은 검색(₩14,323) 대비 절반이지만, <strong>리드 품질은 미검증</strong>.<br>
    PMax는 구글 AI가 자동 최적화하는 캠페인 — CPA는 낮지만 <strong>상담→계약 전환율이 검색 대비 낮을 수 있음</strong>.<br>
    이건 CRM 데이터 연동 후에야 확인 가능합니다 (Phase 3).
    """, "warning")


# ═══════════════════════════════════════════════
# PAGE: Meta Deep-Dive
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

    # 메인 차트
    df_meta = meta_adset[meta_adset['예산비중'] >= 0.5].sort_values('CPL')
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

    # CTR vs CVR
    section("CTR vs CVR: 관심과 전환의 괴리")

    df_sig = meta_adset[meta_adset['예산비중'] >= 0.5]
    fig = px.scatter(df_sig, x='CTR', y='CVR', size='비용', color='소재_short', text='소재_short', size_max=55,
                     color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_traces(textposition='top center', textfont_size=11)
    fig.update_layout(height=420, plot_bgcolor='rgba(0,0,0,0)',
                      xaxis=dict(title='CTR (%) — 광고 클릭률', showgrid=True, gridcolor='#f0f0f0'),
                      yaxis=dict(title='CVR (%) — 전환율', showgrid=True, gridcolor='#f0f0f0'))
    st.plotly_chart(fig, use_container_width=True)

    insight("""
    <strong style="color:#E74C3C;">"에브리타임"</strong>: CTR 1.20% (최고) but CVR 11.0% (최저) = <strong>호기심 클릭</strong><br>
    <strong style="color:#2ECC71;">"이사 가격"</strong>: CTR 0.99% (보통) but CVR 27.1% (최고) = <strong>전환 의도 클릭</strong><br><br>
    CTR이 높다고 좋은 게 아닙니다. <strong>전환으로 이어지는 클릭</strong>이 중요합니다.<br>
    "이사 가격" 소재는 관심 없는 사람은 안 클릭하지만, 클릭하는 사람은 진짜 이사 견적이 필요한 사람.
    """, "success")

    divider()

    # 플랫폼 비교
    section("플랫폼별 CPL 추이")

    fig = px.line(meta_plat_month, x='월', y='CPL', color='플랫폼', markers=True,
                  color_discrete_map={'Instagram': COLORS['ig'], 'Facebook': COLORS['fb'], 'Threads': COLORS['threads']})
    fig.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title='CPL (₩)'))
    fig.update_traces(line_width=3, marker_size=10)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("🏆 Threads", "₩3,937 (1월)", delta="모든 소재에서 CPL 최저", delta_color="inverse")
    col2.metric("📸 Instagram", "₩4,853 (1월)", delta="볼륨 90%+ 담당")
    col3.metric("📘 Facebook", "₩5,766 (1월)", delta="변동성 큼, 볼륨 소")

    insight("""
    <strong>Threads가 일관되게 CPL 최저</strong> — 가격소재 기준 IG 대비 25% 저렴.<br>
    현재 예산 비중 ~5%로 과소 투입. <strong>15%까지 확대해도 CPL 유지되는지 테스트 가치 있음.</strong><br><br>
    Threads는 아직 광고주가 적어 경쟁이 낮고, 유저가 텍스트 기반이라 광고 수용도가 높을 수 있습니다.
    """)

    divider()

    # 소재 월별 추이
    section("소재별 월별 CPL 추이 — 누가 개선되고 누가 악화되나")

    fig = px.line(meta_creative_month, x='월', y='CPL', color='소재', markers=True)
    fig.update_layout(height=380, plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title='CPL (₩)'))
    fig.update_traces(line_width=3, marker_size=10)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        insight("""
        <strong style="color:#2ECC71;">개선 중 (건드리지 말 것)</strong><br>
        "가격 소재": ₩5,729→₩4,527 <strong>(-21%)</strong><br>
        "여자 모델": ₩6,585→₩3,174 <strong>(-52%)</strong>
        """, "success")
    with col2:
        insight("""
        <strong style="color:#E74C3C;">문제 있음 (조치 필요)</strong><br>
        "소재 ALL": ₩10,060→₩4,830→₩12,867 <strong>(불안정)</strong><br>
        "에브리타임": ₩5,091→₩5,334 <strong>(개선 없음)</strong>
        """, "danger")


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
# PAGE: 가설 & 원인 분석
# ═══════════════════════════════════════════════
elif page == "가설 & 원인 분석":

    st.markdown("# 가설 & 원인 분석")
    st.caption("비효율 세그먼트가 왜 안 되는지 — 가설 기반 접근")
    divider()

    tab_g, tab_m = st.tabs(["🔍 Google 가설 (H1~H5)", "📱 Meta 가설 (H6~H9)"])

    with tab_g:
        section("Google 검색 비효율 가설")

        with st.expander("🔴 H1: 용달/화물 의도 미스매치 — 가장 유력", expanded=True):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("""
                **현상**: 예산 35.7%(₩2,626,506), CPL ₩18,761 (최악), CVR 12.6% (최저)

                **가설**: "용달"을 검색하는 유저는 이사가 아니라 **물건 운송**(냉장고, 가구 등)이 목적.
                이사대학은 **이사 견적 비교** 서비스 → 니즈가 근본적으로 다름.

                **근거**:
                - 용달 키워드 102개 중 이사 관련은 일부 ("이사용달", "원룸용달")
                - 나머지는 "화물운송", "용달가격", "1톤트럭" 등 운송 관련
                - 클릭은 하지만 (CTR 4.7%) 견적 폼에서 이탈 (CVR 12.6%)
                """)
            with col2:
                fig = go.Figure(go.Pie(values=[35.7, 64.3], labels=['용달/화물', '나머지'], marker_colors=[COLORS['worst'], '#e8e8e8'], hole=0.6))
                fig.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), showlegend=False, annotations=[dict(text='35.7%', x=0.5, y=0.5, font_size=20, showarrow=False)])
                st.plotly_chart(fig, use_container_width=True)

        with st.expander("🔴 H2: 용달 랜딩페이지 미스매치"):
            st.markdown("""
            "용달" 검색 → 이사 견적 페이지 도착 → **단순 운송 서비스 정보 없음** → 이탈

            용달 유저가 기대하는 것: "1톤 트럭으로 냉장고 옮기는 데 얼마?"
            이사대학이 보여주는 것: "이사 견적 비교해보세요"
            → **기대와 현실 불일치 = 즉시 이탈**
            """)

        with st.expander("🟠 H3: 키워드 확장 과잉"):
            st.markdown("""
            광고그룹 "용달키워드"에 **102개** 키워드가 몰려있음 (권장: 10~20개).
            → 관련 없는 검색어에도 노출되어 무효 클릭 증가.
            → 정밀 관리 불가능한 수준.
            """)

        with st.expander("🟠 H4: 일반 이사 키워드 경쟁 과열"):
            st.markdown("""
            "이사업체", "이삿짐센터" 등은 **한진, 현대 등 대형 업체**와 입찰 경쟁.
            → CPC(클릭당 비용) 높은데 이사대학 인지도는 낮아 전환율↓.
            → CPL ₩16,334 — 브랜드 키워드(₩4,741) 대비 **3.4배** 높음.
            """)

        with st.expander("🟠 H5: 지역 키워드 정밀도 부족"):
            st.markdown("""
            | 지역 | CPL | 전환 |
            |------|-----|------|
            | 대구 | ₩7,062 | 6건 |
            | 서울 | ₩10,992 | 6건 |
            | 경남 | ₩58,198 | 1건 |
            | 제주 | ₩18,047 | 2건 |

            서비스 커버리지 없는 지역에도 광고 노출 → **전환되어도 계약 불가 = 순 낭비**
            """)

    with tab_m:
        section("Meta 비효율 가설")

        with st.expander("🔴 H6: 에브리타임 — 호기심 클릭 > 전환 의도", expanded=True):
            st.markdown("""
            **현상**: CTR 1.20% (최고) but CVR 11.0% (최저급)

            **가설**: 에타(에브리타임)는 20대 대학생 커뮤니티.
            이사 안 해도 "싸다" 보면 일단 클릭 → 실제 이사 계획 없으면 전환 안 됨.

            **"관심은 많은데 안 사"** 패턴 — CTR↑ CVR↓의 전형.
            """)

        with st.expander("🔴 H7: 에브리타임 — 20대 퍼널 이탈"):
            st.markdown("""
            견적 폼이 20대 UX에 안 맞거나, 부모님 동의 필요한 단계에서 이탈.
            → 다른 소재는 CTR↓ CVR↑ 패턴인데 에타만 CTR↑ CVR↓
            → 20대 특화 랜딩페이지 필요 가능성.
            """)

        with st.expander("🟠 H8: 소재 ALL — 유사타겟 풀 소진"):
            st.markdown("""
            **월별 CPL**: ₩10,060 → ₩4,830 → ₩12,867 (불안정)

            유사타겟 = 전환 유저와 "비슷한" 유저를 Meta AI가 찾아줌.
            → 처음엔 유사도 높은 유저부터 노출 → 점점 먼 유저로 확장.
            → 12월에 "달콤한 구간"을 거친 후 1월에 풀 소진.
            """)

        with st.expander("🟠 H9: 소재 ALL — 시즌 × 타겟 품질"):
            st.markdown("""
            12월(이사 비수기) → 이사 의도 있는 유저**만** 반응 → CPL↓
            1월(이사 시즌 시작) → 넓은 유저 유입 → 탐색형 유저가 희석 → CPL↑

            계절적 수요 패턴과 타겟 품질이 동시에 작용.
            """)


# ═══════════════════════════════════════════════
# PAGE: 예산 시뮬레이터
# ═══════════════════════════════════════════════
elif page == "예산 시뮬레이터":

    st.markdown("# 예산 시뮬레이터")
    st.caption("예산 재배분 시 예상 효과를 실시간으로 확인하세요")
    divider()

    section("Google 검색 예산 재배분")

    insight("현재 Google 검색 예산 배분과 CPL을 기준으로, 예산을 재배분하면 전환이 어떻게 변하는지 시뮬레이션합니다.")

    total_search_budget = 7_358_550  # 검색 캠페인 총 예산 (키워드 비용 합)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**현재 배분**")
        st.caption(f"검색 캠페인 키워드 비용 합계: ₩{total_search_budget:,}")
        pct_yongdal = st.slider("용달/화물 비중 (%)", 0, 60, 36, key='yd')
        pct_small = st.slider("소형이사/원룸 비중 (%)", 0, 40, 3, key='sm')
        pct_price = st.slider("가격/견적 비중 (%)", 0, 30, 4, key='pr')
        pct_rest = 100 - pct_yongdal - pct_small - pct_price
        if pct_rest < 0:
            st.error("비중 합이 100%를 초과합니다!")
            pct_rest = 0
        st.caption(f"나머지 (외국인+일반+지역+포장+브랜드): {pct_rest}%")

    with col2:
        # CPL assumptions
        cpl_yongdal = 18761
        cpl_small = 6411
        cpl_price = 7900
        cpl_rest = 11500  # 가중 평균

        budget_yd = total_search_budget * pct_yongdal / 100
        budget_sm = total_search_budget * pct_small / 100
        budget_pr = total_search_budget * pct_price / 100
        budget_rest = total_search_budget * pct_rest / 100

        conv_yd = budget_yd / cpl_yongdal if cpl_yongdal > 0 else 0
        conv_sm = budget_sm / cpl_small if cpl_small > 0 else 0
        conv_pr = budget_pr / cpl_price if cpl_price > 0 else 0
        conv_rest = budget_rest / cpl_rest if cpl_rest > 0 else 0
        total_conv_sim = conv_yd + conv_sm + conv_pr + conv_rest
        total_cpl_sim = total_search_budget / total_conv_sim if total_conv_sim > 0 else 0

        # 현재 전환 (기준)
        current_conv = 569  # 검색 캠페인 키워드 전환 합계 (근사)
        conv_delta = total_conv_sim - current_conv
        conv_delta_pct = (conv_delta / current_conv * 100) if current_conv > 0 else 0

        st.markdown("**시뮬레이션 결과**")
        st.metric("예상 총 전환", f"{total_conv_sim:.0f}건", delta=f"{conv_delta:+.0f}건 ({conv_delta_pct:+.1f}%)")
        st.metric("예상 평균 CPL", f"₩{total_cpl_sim:,.0f}", delta=f"₩{total_cpl_sim - 12900:+,.0f} vs 현재", delta_color="inverse")

        # Breakdown
        sim_df = pd.DataFrame({
            '세그먼트': ['용달/화물', '소형이사/원룸', '가격/견적', '나머지'],
            '예산': [budget_yd, budget_sm, budget_pr, budget_rest],
            '예상 전환': [conv_yd, conv_sm, conv_pr, conv_rest],
            'CPL': [cpl_yongdal, cpl_small, cpl_price, cpl_rest],
        })

        fig = go.Figure()
        fig.add_trace(go.Bar(x=sim_df['세그먼트'], y=sim_df['예상 전환'], marker_color=[COLORS['worst'], COLORS['best'], COLORS['good'], COLORS['gray']],
                             text=[f'{v:.0f}건' for v in sim_df['예상 전환']], textposition='auto'))
        fig.update_layout(height=280, margin=dict(l=20,r=20,t=20,b=20), plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title='전환 (건)'))
        st.plotly_chart(fig, use_container_width=True)

    divider()

    section("추천 시나리오")

    col1, col2, col3 = st.columns(3)
    with col1:
        # Current
        st.markdown("**현재**")
        st.caption("용달 36% / 소형 3% / 가격 4%")
        st.metric("전환", "~569건")
        st.metric("CPL", "₩12,900")

    with col2:
        # Conservative
        st.markdown("**보수적 재배분**")
        st.caption("용달 20% / 소형 15% / 가격 10%")
        c_conv = total_search_budget * 0.20 / cpl_yongdal + total_search_budget * 0.15 / cpl_small + total_search_budget * 0.10 / cpl_price + total_search_budget * 0.55 / cpl_rest
        st.metric("전환", f"~{c_conv:.0f}건", delta=f"+{c_conv-569:.0f}건")
        st.metric("CPL", f"₩{total_search_budget/c_conv:,.0f}", delta=f"₩{total_search_budget/c_conv-12900:+,.0f}", delta_color="inverse")

    with col3:
        # Aggressive
        st.markdown("**공격적 재배분**")
        st.caption("용달 10% / 소형 25% / 가격 15%")
        a_conv = total_search_budget * 0.10 / cpl_yongdal + total_search_budget * 0.25 / cpl_small + total_search_budget * 0.15 / cpl_price + total_search_budget * 0.50 / cpl_rest
        st.metric("전환", f"~{a_conv:.0f}건", delta=f"+{a_conv-569:.0f}건")
        st.metric("CPL", f"₩{total_search_budget/a_conv:,.0f}", delta=f"₩{total_search_budget/a_conv-12900:+,.0f}", delta_color="inverse")

    insight(f"""
    <strong>보수적으로만 해도 +{c_conv-569:.0f}건 (+{(c_conv/569-1)*100:.0f}%)</strong>, 공격적이면 <strong>+{a_conv-569:.0f}건 (+{(a_conv/569-1)*100:.0f}%)</strong>.<br><br>
    <strong>단, 이건 CPL 기준 추정</strong>입니다. 실제로는:<br>
    1) 소형이사 볼륨을 늘리면 CPL이 소폭 상승할 수 있고<br>
    2) 용달을 줄이면 용달 CPL이 개선될 수 있습니다 (비효율 키워드 제거 효과)<br>
    → <strong>Phase 1에서 실제 테스트 후 검증 필요</strong>
    """, "warning")


# ═══════════════════════════════════════════════
# PAGE: 테스트 로드맵
# ═══════════════════════════════════════════════
elif page == "테스트 로드맵":

    st.markdown("# 테스트 로드맵")
    st.caption("3단계 실행 계획 — 가설을 검증하고 최적화 체계를 구축합니다")
    divider()

    # Visual timeline
    phase_select = st.radio("Phase 선택", ["전체 보기", "Phase 1: 즉시 실행", "Phase 2: A/B 테스트", "Phase 3: 데이터 연동"], horizontal=True)

    divider()

    if phase_select in ["전체 보기", "Phase 1: 즉시 실행"]:
        section("PHASE 1 — 즉시 실행 (1~2주)")
        st.markdown("**저위험, 고효과 액션. 지금 바로 시작 가능.**")

        actions_p1 = [
            ("1", "용달 키워드 정리", "102개 키워드 리뷰 → 이사 무관 키워드 제외", "₩1.3M+ 절감", "H1, H3"),
            ("2", "소형이사/가격 키워드 확대", "용달 감축분 → 소형이사/가격으로 이동", "+180건 전환 예상", "대안 A, D"),
            ("3", "서비스 불가 지역 OFF", "경남/제주/충북 등 확인 후 광고 중단", "낭비 예산 즉시 절감", "H5"),
            ("4", "소재ALL 예산 축소", "50% 감축 → 가격 소재로 이동", "CPL ₩6,544→₩5,171", "H8, 대안 F"),
        ]

        for num, action, detail, effect, hyp in actions_p1:
            with st.container():
                col1, col2, col3, col4 = st.columns([0.5, 3, 3, 2])
                col1.markdown(f"**{num}**")
                col2.markdown(f"**{action}**")
                col3.caption(detail)
                col4.markdown(f"🎯 {effect}")

        st.markdown("")
        insight("Phase 1만으로도 <strong>동일 예산 대비 전환수 15~20% 개선</strong>이 보수적으로 기대됩니다.", "success")

    if phase_select in ["전체 보기", "Phase 2: A/B 테스트"]:
        divider()
        section("PHASE 2 — A/B 테스트 (3~4주)")
        st.markdown("**데이터로 검증. 최적 소재/타겟/플랫폼 확정.**")

        actions_p2 = [
            ("5", "Meta 소재 A/B 테스트", '현행 "가격 소재" vs "이사 가격" vs "여자 모델"', "최적 소재 확정", "대안 F"),
            ("6", "에타 소재 변형 테스트", "현행 vs 가격 메시지 결합 버전", "CVR 11%→18%+ 목표", "대안 E"),
            ("7", "Threads 예산 확대", "5% → 15%로 확대", "CPL ₩4,114 유지 검증", "-"),
            ("8", "Google LP 변형", "용달/소형이사 전용 랜딩페이지 테스트", "CVR 개선 검증", "H2"),
        ]

        for num, action, detail, effect, hyp in actions_p2:
            with st.container():
                col1, col2, col3, col4 = st.columns([0.5, 3, 3, 2])
                col1.markdown(f"**{num}**")
                col2.markdown(f"**{action}**")
                col3.caption(detail)
                col4.markdown(f"🎯 {effect}")

    if phase_select in ["전체 보기", "Phase 3: 데이터 연동"]:
        divider()
        section("PHASE 3 — 데이터 연동 (1~2개월)")
        st.markdown("**진짜 ROI를 보려면 내부 데이터가 필요합니다.**")

        actions_p3 = [
            ("9", "CRM 데이터 연동", "광고 전환 vs 실제 상담 DB 대조", "리드 품질 검증"),
            ("10", "PMax 리드 품질 검증", "PMax vs 검색 리드의 계약율 비교", "PMax 예산 확정"),
            ("11", "채널별 ROAS 산출", "계약 금액 기반 진짜 ROI 계산", "최종 예산 배분 근거"),
            ("12", "전환 추적 감사", "대행사와 전환 태그 점검", "데이터 신뢰도 확보"),
        ]

        for num, action, detail, effect in actions_p3:
            with st.container():
                col1, col2, col3, col4 = st.columns([0.5, 3, 3, 2])
                col1.markdown(f"**{num}**")
                col2.markdown(f"**{action}**")
                col3.caption(detail)
                col4.markdown(f"🎯 {effect}")

        insight("""
        <strong>현재 분석의 한계</strong>: 지금은 광고 플랫폼 데이터(리드 획득까지)만 볼 수 있습니다.<br>
        리드→계약 전환율, 채널별 리드 품질, 실제 매출 기여도는 <strong>내부 CRM 데이터</strong>가 필요합니다.<br><br>
        Phase 3 완료 시: <strong>감이 아닌 데이터 기반 마케팅 의사결정 체계 구축</strong>
        """, "warning")

    divider()

    # Impact summary
    section("기대 효과 요약")

    st.markdown(f"""
    <div class="kpi-container">
        {kpi_card("Phase 1 (즉시)", "+15~20%", "전환수 개선 (동일 예산)", "green")}
        {kpi_card("Phase 2 (A/B)", "최적 소재 확정", "데이터 기반 검증")}
        {kpi_card("Phase 3 (연동)", "실제 ROAS", "감→데이터 전환", "orange")}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    insight("""
    이 분석과 테스트는 단순한 '광고 운영 최적화'가 아닙니다.<br>
    <strong>이사대학의 마케팅 의사결정 체계를 '감'에서 '데이터'로 전환하는 과정</strong>입니다.
    """, "success")


# ═══════════════════════════════════════════════
# Footer
# ═══════════════════════════════════════════════
st.markdown("---")
st.caption("이사대학 디지털 마케팅 심화 분석 대시보드 | Prepared by Casey | 2026.02")
st.caption("데이터 기반: Google Ads + Meta Ads (2025.11~2026.01)")
