import streamlit as st
import pandas as pd
import io

# 1. 데이터를 불러오는 함수 (파일 업로더 사용으로 변경)
@st.cache_data
def load_data(uploaded_file):
    # 파일이 업로드되지 않았으면 빈 DataFrame 반환
    if uploaded_file is None:
        return pd.DataFrame()
        
    try:
        # 파일을 문자열 형태로 읽고, 다양한 인코딩으로 시도합니다.
        data_string = uploaded_file.getvalue().decode('utf-8')
        
        # 파일 내용을 io.StringIO로 감싸서 Pandas가 읽을 수 있게 합니다.
        try:
            df = pd.read_csv(io.StringIO(data_string), encoding='utf-8')
        except:
            # utf-8이 실패하면 cp949로 재시도
            data_string = uploaded_file.getvalue().decode('cp949')
            df = pd.read_csv(io.StringIO(data_string), encoding='cp949')

    except Exception as e:
        st.error(f"🚨 파일을 읽는 중 오류가 발생했어요: {e}")
        return pd.DataFrame()

    # ⭐⭐ 오류 해결 핵심: 컬럼 이름의 공백을 제거합니다. ⭐⭐
    df.columns = df.columns.str.strip()
    
    # 핵심 컬럼 존재 여부 확인 (혹시 파일이 이상할 경우 대비)
    required_cols = ['구분', '총점포수', '브랜드', '진출국가']
    if not all(col in df.columns for col in required_cols):
        st.error("🚨 업로드한 파일에 필수 컬럼(구분, 총점포수, 브랜드, 진출국가)이 모두 없어요.")
        return pd.DataFrame()

    # 데이터 전처리: '구분'과 '주요메뉴'의 앞뒤 공백 제거
    df['구분'] = df['구분'].astype(str).str.strip()
    
    # '총점포수'가 숫자인지 확인하고, 혹시 문자열이 섞여있다면 에러 방지
    try:
        df['총점포수'] = pd.to_numeric(df['총점포수'], errors='coerce').fillna(0).astype(int)
    except:
        st.error("🚨 '총점포수' 컬럼에 숫자가 아닌 데이터가 있어서 분석을 계속할 수 없어요.")
        return pd.DataFrame()

    # NaN 값 처리: '체명'의 결측치는 '정보없음'으로 채워줍니다.
    df['체명'] = df['체명'].fillna('정보없음')
    
    return df

# 2. 메인 Streamlit 앱 함수
def app():
    st.set_page_config(layout="wide")
    st.title("🌎 K-브랜드 해외 진출 현황 분석 대시보드")
    st.markdown("---")
    
    # 2. 사이드바에 파일 업로더 위젯 배치
    with st.sidebar:
        st.header("1. 📂 데이터 파일 업로드")
        uploaded_file = st.file_uploader(
            "여기에 **altificial.csv** 파일을 올려주세요!", 
            type=['csv']
        )
        st.markdown("---")

        # 데이터 로드
        df = load_data(uploaded_file)

        if df.empty:
            st.warning("☝️ CSV 파일을 먼저 업로드해야 분석을 시작할 수 있어요!")
            return

        # 3. 분석 필터 설정 (데이터 로드 성공 시에만 표시)
        st.header("2. 🔍 분석 필터 설정")
        
        all_categories = df['구분'].unique().tolist()
        all_categories.insert(0, '전체')
        
        selected_category = st.selectbox(
            "어떤 브랜드 타입을 볼까?",
            options=all_categories,
            index=0
        )
        
        min_stores = st.slider(
            "최소 해외 점포수 기준은?",
            min_value=1, 
            max_value=int(df['총점포수'].max()), 
            value=10,
            step=1
        )
        
        st.markdown("---")
        st.info("💡 **팁:** 데이터를 필터링해서 자세히 살펴보자!")

    # 4. 필터링된 데이터 준비 (메인 화면)
    filtered_df = df.copy()
    
    if selected_category != '전체':
        filtered_df = filtered_df[filtered_df['구분'] == selected_category]
        
    filtered_df = filtered_df[filtered_df['총점포수'] >= min_stores]
    
    if filtered_df.empty:
        st.warning(f"선택한 조건 (유형: **{selected_category}**, 점포수: **{min_stores}개 이상**)에 맞는 브랜드가 없어요! 😅 필터를 조정해 보세요.")
        return
        
    # 5. 핵심 통계 카드 출력
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🏆 총 브랜드 수", len(filtered_df), delta_color="off")
    
    with col2:
        st.metric("💰 총 점포 합계", f"{filtered_df['총점포수'].sum():,}개", delta_color="off")

    with col3:
        avg_stores = filtered_df['총점포수'].mean()
        st.metric("⭐ 평균 점포수", f"{avg_stores:.1f}개", delta_color="off")

    st.markdown("---")

    # 6. 사용자 선택에 따른 분석 결과 (MBTI 진로 추천 형식 이용)
    st.header(f"✨ {selected_category} 브랜드 집중 분석!")
    
    # **첫 번째 추천 (가장 점포수가 많은 브랜드)**
    top_brand = filtered_df.sort_values(by='총점포수', ascending=False).iloc[0]
    
    st.subheader(f"🥇 No.1 해외 진출 왕: **{top_brand['브랜드']}**") 
    st.markdown(f"> **총 점포수:** **{top_brand['총점포수']:,}개**")

    st.markdown(f"#### 🔎 No.1 브랜드 집중 해부! (학과/성격 설명 형식)")
    st.markdown(f"**적합한 학과:** 🍳 **외식경영학과, 식품공학과** (이 브랜드를 따라잡으려면 식품 개발과 효율적인 점포 관리가 필수!)")
    st.markdown(f"**적합한 성격:** 💪 **도전적이고 추진력이 강한 사람** (해외 진출은 쉽지 않아! 끊임없이 시장을 개척하는 열정이 필요해!)")
    
    st.markdown("---")

    # **두 번째 추천 (가장 많은 국가에 진출한 브랜드)**
    filtered_df['국가수'] = filtered_df['진출국가'].apply(lambda x: len(str(x).split(',')) if pd.notna(x) else 0)
    top_global_brand = filtered_df.sort_values(by='국가수', ascending=False).iloc[0]
    
    st.subheader(f"🥈 No.2 글로벌 개척자: **{top_global_brand['브랜드']}**") 
    st.markdown(f"> **진출 국가:** **{top_global_brand['국가수']}개국**")

    st.markdown(f"#### 🔎 No.2 브랜드 집중 해부! (학과/성격 설명 형식)")
    st.markdown(f"**적합한 학과:** 🗺️ **국제통상학과, 외국어(중국어/영어) 계열** (다양한 나라와 계약하고 소통하려면 국제 감각이 중요!)")
    st.markdown(f"**적합한 성격:** 🤝 **개방적이고 적응력이 뛰어난 사람** (나라마다 문화가 다르니까 유연하게 대처할 수 있어야 해!)")

    st.markdown("---")
    
    # 7. 전체 데이터 테이블 표시 (자세히 보기)
    st.header("📊 상세 데이터 테이블")
    display_cols = ['체명', '브랜드', '주요메뉴', '구분', '진출국가', '총점포수']
    # 'No'와 '국가수' 컬럼을 제외하고 표시
    display_df = filtered_df.filter(items=display_cols, axis=1)
    
    st.dataframe(display_df, use_container_width=True)

# 8. 앱 실행
if __name__ == '__main__':
    app()
