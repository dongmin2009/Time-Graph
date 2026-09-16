
import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# 기본 설정
# ============================================================

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)


# ============================================================
# 제목
# ============================================================

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")

st.markdown(
    """
    영화의 일별 박스오피스 데이터를 시간의 흐름에 따라 살펴보는 그래프 도감입니다.

    원하는 영화를 선택하여 날짜별 일관객 변화를 확인할 수 있습니다.
    """
)


# ============================================================
# 데이터 불러오기
# ============================================================

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/kobis_daily.csv"
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # --------------------------------------------------------
    # 날짜 변환
    # YYYYMMDD → 실제 날짜
    # --------------------------------------------------------

    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # --------------------------------------------------------
    # 숫자형 변환
    # --------------------------------------------------------

    numeric_columns = [
        "순위",
        "영화코드",
        "일관객",
        "누적관객",
        "스크린수",
        "상영횟수"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # 날짜 → 순위 순으로 정렬
    df = df.sort_values(
        ["날짜", "순위"]
    ).reset_index(drop=True)

    return df


# ============================================================
# 데이터 로딩
# ============================================================

try:
    df = load_data()

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
    st.stop()


# ============================================================
# 데이터 기간 표시
# ============================================================

min_date = df["날짜"].min()
max_date = df["날짜"].max()

st.caption(
    f"📅 데이터 기간: {min_date.strftime('%Y-%m-%d')} ~ "
    f"{max_date.strftime('%Y-%m-%d')}  |  "
    f"총 {len(df):,}개 기록"
)


# ============================================================
# 그래프 1
# ============================================================

st.divider()

st.header("📈 그래프 1. 영화별 일관객 변화")

st.markdown(
    "영화를 하나 선택하면 날짜에 따른 일관객 변화를 확인할 수 있습니다."
)


# ------------------------------------------------------------
# 영화 선택
# ------------------------------------------------------------

movie_list = sorted(
    df["영화명"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

selected_movie = st.selectbox(
    "영화 선택",
    movie_list,
    index=0
)


# ------------------------------------------------------------
# 선택한 영화 데이터
# ------------------------------------------------------------

movie_df = df[
    df["영화명"].astype(str) == selected_movie
].copy()

movie_df = movie_df.sort_values("날짜")


# ------------------------------------------------------------
# 영화 기본 정보
# ------------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "기록된 날짜 수",
        f"{movie_df['날짜'].nunique():,}일"
    )

with col2:
    st.metric(
        "최고 일관객",
        f"{movie_df['일관객'].max():,.0f}명"
    )

with col3:
    st.metric(
        "평균 일관객",
        f"{movie_df['일관객'].mean():,.0f}명"
    )


# ------------------------------------------------------------
# 그래프 1
# ------------------------------------------------------------

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"「{selected_movie}」 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 (명)"
    }
)

fig1.update_traces(
    hovertemplate=(
        "<b>날짜</b>: %{x|%Y-%m-%d}<br>"
        "<b>관객수</b>: %{y:,.0f}명"
        "<extra></extra>"
    ),
    line=dict(width=3),
    marker=dict(size=7)
)

fig1.update_layout(
    height=550,
    hovermode="x unified",
    margin=dict(
        l=20,
        r=20,
        t=70,
        b=20
    ),
    xaxis=dict(
        title="날짜",
        tickformat="%Y-%m-%d",
        rangeslider=dict(visible=True)
    ),
    yaxis=dict(
        title="일관객 (명)",
        tickformat=","
    )
)

st.plotly_chart(
    fig1,
    width="stretch",
    config={
        "displayModeBar": True,
        "scrollZoom": False
    }
)


# ------------------------------------------------------------
# 그래프 1 설명
# ------------------------------------------------------------

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.info(
    "여기에 이 그래프로 알 수 있는 내용을 작성하세요."
)


# ============================================================
# 그래프 2
# ============================================================

st.divider()

st.header("📊 그래프 2")

st.info(
    "그래프 2가 들어갈 자리입니다."
)


# ------------------------------------------------------------
# 그래프 2 설명
# ------------------------------------------------------------

# ── 그래프 2. 흥행 대작들의 곡선 겹쳐 보기 ────────────────────
st.header("2. 흥행 대작 다섯 편의 곡선")
top5 = df.groupby("영화명")["일관객"].sum().nlargest(5).index
five = df[df["영화명"].isin(top5)].sort_values("날짜")
fig2 = px.line(five, x="날짜", y="일관객", color="영화명", markers=True)
st.plotly_chart(fig2, width="stretch")
st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")


# ── 그래프 3. 극장가 전체의 흐름과 봉우리 ─────────────────────
st.header("3. 날짜별 10위권 관객 합계")
daily = df.groupby("날짜", as_index=False)["일관객"].sum()
peak3 = daily.nlargest(3, "일관객")
fig3 = px.area(daily, x="날짜", y="일관객")
fig3.add_scatter(x=peak3["날짜"], y=peak3["일관객"], mode="markers+text",
                 text=peak3["날짜"].dt.strftime("%Y-%m-%d"), textposition="top center",
                 marker=dict(size=10, color="crimson"), name="가장 붐빈 3일")
st.plotly_chart(fig3, width="stretch")
st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")


# ── 그래프 4. 기간 전체 관객 TOP 10 ─────────────────────────
st.header("4. 이 기간 관객이 가장 많았던 열 편")
total = (df.groupby("영화명", as_index=False)
           .agg(관객합계=("일관객", "sum"), 등장일수=("날짜", "count"))
           .nlargest(10, "관객합계"))
fig4 = px.bar(total.sort_values("관객합계"), x="관객합계", y="영화명",
              orientation="h", hover_data=["등장일수"])
st.plotly_chart(fig4, width="stretch")
st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")


# ============================================================
# 그래프 5
# ============================================================

st.divider()

st.header("📊 그래프 5")

st.info(
    "그래프 5가 들어갈 자리입니다."
)


# ------------------------------------------------------------
# 그래프 5 설명
# ------------------------------------------------------------

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.info(
    "여기에 그래프 5에서 알 수 있는 내용을 작성하세요."
)

