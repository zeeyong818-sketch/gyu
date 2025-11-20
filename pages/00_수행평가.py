import streamlit as st
import pandas as pd
import io

# 1. 데이터를 불러오는 함수 (Streamlit Cloud 환경에서는 직접 업로드된 파일을 읽습니다.)
@st.cache_data
def load_data():
    # 사용자가 업로드한 'altificial.csv' 파일을 직접 읽습니다.
    # Streamlit 환경에서 'altificial.csv' 파일이 접근 가능하다고 가정합니다.
    try:
        # 데이터가 CSV 형태의 문자열로 처리될 수 있으므로 io.StringIO를 사용합니다.
        # 실제 Streamlit Cloud 배포 시에는 'altificial.csv' 파일을 프로젝트 폴더에 넣어두거나
        # 파일 업로드 위젯을 사용하여 데이터를 받도록 코드를 수정해야 합니다.
        # 여기서는 파일 접근이 가능한 환경임을 가정하고 코드를 작성합니다.
        df = pd.read_csv('altificial.csv', encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv('altificial.csv', encoding='cp949')
        except:
            df = pd.read_csv('altificial.csv', encoding='euc-kr')
    except FileNotFoundError:
        st.error("🚨 'altificial.csv' 파일을 찾을 수 없어요. 파일을 Streamlit 프로젝트 폴더에 넣어주세요!")
        return pd.DataFrame() # 빈 DataFrame 반환

    # 데이터 전처리: '구분', '총점포수' 등 필요한 열의 타입을 정리합니다.
    df['구분'] = df['구분'].str.strip()
    df['주요메뉴'] = df['주요메뉴'].str.strip()
    
    # NaN 값 처리: '체명'의 결측치는 '정보없음'으로 채워줍니다.
    df['체명'] = df['체명'].fillna('정보없음')
    
    return df

# 2. 메인 Streamlit 앱 함수
def app():
    st.set_page_config(layout="wide")
    st.title("🌎 K-브랜드 해외 진출 현황 분석 대시보드")
    st.markdown("---")
    
    # 2. 데이터 불러오기
    df = load_data()
    if df.empty:
        return

    # 3. 사이드바 (사용자가 선택할 수 있는 필터) - MBTI 선택 형식 이용
    with st.sidebar:
        st.header("🔍 분석 필터 설정")
        
        # '구분' (한식/비한식)을 선택하는 위젯
        all_categories = df['구분'].unique().tolist()
        all_categories.insert(0, '전체') # '전체' 옵션 추가
        
        selected_category = st.selectbox(
            "어떤 브랜드 타입을 볼까?",
            options=all_categories, # 16개 MBTI 선택 대신, '구분' 선택
            index=0
        )
        
        # '총점포수' 최소 기준 설정
        min_stores = st.slider(
            "최소 해외 점포수 기준은?",
            min_value=1, 
            max_value=int(df['총점포수'].max()), 
            value=10, # 기본값 10개 이상
            step=1
        )
        
        st.markdown("---")
        st.info("💡 **팁:** 데이터를 필터링해서 자세히 살펴보자!")

    # 4. 필터링된 데이터 준비
    filtered_df = df.copy()
    
    if selected_category != '전체':
        filtered_df = filtered_df[filtered_df['구분'] == selected_category]
        
    filtered_df = filtered_df[filtered_df['총점포수'] >= min_stores]
    
    # 5. 핵심 통계 카드 출력
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🏆 총 브랜드 수", len(filtered_df), delta_color="off")
    
    with col2:
        st.metric("💰 총 점포 합계", f"{filtered_df['총점포수'].sum():,}개", delta_color="off")

    with col3:
        # 평균 점포수 계산 (0으로 나누는 것 방지)
        avg_stores = filtered_df['총점포수'].mean() if not filtered_df.empty else 0
        st.metric("⭐ 평균 점포수", f"{avg_stores:.1f}개", delta_color="off")

    st.markdown("---")

    # 6. 사용자 선택에 따른 분석 결과 (MBTI 진로 추천 형식 이용)
    # 선택된 '구분'에 따라 분석 결과를 제공합니다.
    st.header(f"✨ {selected_category} 브랜드 집중 분석!")
    
    if filtered_df.empty:
        st.warning(f"선택한 조건 (유형: **{selected_category}**, 점포수: **{min_stores}개 이상**)에 맞는 브랜드가 없어요! 😅 필터를 조정해 보세요.")
        return

    # **첫 번째 추천 (가장 점포수가 많은 브랜드)**
    # 2. mbti를 16개 중에서 하나 고르면 그 유형에 해당하는 진로를 2가지 추천해줘.
    top_brand = filtered_df.sort_values(by='총점포수', ascending=False).iloc[0]
    
    st.subheader(f"🥇 No.1 해외 진출 왕: **{top_brand['브랜드']}**") # 첫 번째 진로 추천
    st.markdown(f"> **총 점포수:** **{top_brand['총점포수']:,}개**")

    # 3. 각 진로에서는 어떤 학과가 적합한지 어떤 성격인 사람이 적합한지를 설명해줘.
    st.markdown(f"#### 🔎 No.1 브랜드 집중 해부! (학과/성격 설명 형식)")
    st.markdown(f"**적합한 학과:** 🍳 **외식경영학과, 식품공학과** (이 브랜드를 따라잡으려면 식품 개발과 효율적인 점포 관리가 필수!)")
    st.markdown(f"**적합한 성격:** 💪 **도전적이고 추진력이 강한 사람** (해외 진출은 쉽지 않아! 끊임없이 시장을 개척하는 열정이 필요해!)")
    
    st.markdown("---")

    # **두 번째 추천 (가장 많은 국가에 진출한 브랜드)**
    # '진출국가' 문자열에서 국가 개수를 카운트합니다.
    filtered_df['국가수'] = filtered_df['진출국가'].apply(lambda x: len(str(x).split(',')) if pd.notna(x) else 0)
    top_global_brand = filtered_df.sort_values(by='국가수', ascending=False).iloc[0]
    
    st.subheader(f"🥈 No.2 글로벌 개척자: **{top_global_brand['브랜드']}**") # 두 번째 진로 추천
    st.markdown(f"> **진출 국가:** **{top_global_brand['국가수']}개국**")

    # 3. 각 진로에서는 어떤 학과가 적합한지 어떤 성격인 사람이 적합한지를 설명해줘.
    st.markdown(f"#### 🔎 No.2 브랜드 집중 해부! (학과/성격 설명 형식)")
    st.markdown(f"**적합한 학과:** 🗺️ **국제통상학과, 외국어(중국어/영어) 계열** (다양한 나라와 계약하고 소통하려면 국제 감각이 중요!)")
    st.markdown(f"**적합한 성격:** 🤝 **개방적이고 적응력이 뛰어난 사람** (나라마다 문화가 다르니까 유연하게 대처할 수 있어야 해!)")

    st.markdown("---")
    
    # 7. 전체 데이터 테이블 표시 (자세히 보기)
    st.header("📊 상세 데이터 테이블")
    # '진출국가'를 깔끔하게 표시하기 위해 DataFrame을 복사해서 보여줍니다.
    display_df = filtered_df.drop(columns=['No', '국가수'], errors='ignore')
    
    st.dataframe(display_df, use_container_width=True)

# 8. 앱 실행
if __name__ == '__main__':
    app()
