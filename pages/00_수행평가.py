import streamlit as st
import pandas as pd
import os # 파일 경로 처리를 위해 os 라이브러리를 가져옵니다.

# 1. 데이터를 불러오는 함수
@st.cache_data
def load_data():
    # 현재 스크립트 경로를 기반으로 루트 폴더의 CSV 파일을 찾습니다.
    current_dir = os.path.dirname(__file__) 
    # '..'를 사용하여 pages 폴더에서 루트 폴더로 이동합니다.
    file_path = os.path.join(current_dir, '..', 'altificial.csv')
    
    # 🌟 파일 경로 확인 (디버깅용, 나중에 필요 없으면 지워도 돼)
    # st.sidebar.write(f"파일 경로: {file_path}") 

    try:
        # 다양한 인코딩으로 시도하여 파일을 읽습니다.
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file_path, encoding='cp949')
            except:
                df = pd.read_csv(file_path, encoding='euc-kr')
                
    except FileNotFoundError:
        st.error(f"🚨 파일을 찾을 수 없어요! **altificial.csv** 파일이 루트 폴더에 있는지 확인해 주세요.")
        return pd.DataFrame() 

    # ⭐ 컬럼 이름 공백 제거 (KeyError 방지)
    df.columns = df.columns.str.strip()

    # 데이터 전처리
    df['구분'] = df['구분'].astype(str).str.strip()
    
    try:
        # '총점포수'를 안전하게 정수로 변환
        df['총점포수'] = pd.to_numeric(df['총점포수'], errors='coerce').fillna(0).astype(int)
    except:
        st.error("🚨 '총점포수' 컬럼에 숫자가 아닌 데이터가 있어요. 데이터를 확인해 주세요.")
        return pd.DataFrame()

    df['체명'] = df['체명'].fillna('정보없음')
    
    return df

# 2. 메인 Streamlit 앱 함수
def app():
    st.set_page_config(layout="wide")
    st.title("🌎 K-브랜드 해외 진출 현황 분석 대시보드")
    st.markdown("---")
    
    # 2. 데이터 로드
    df = load_data()

    if df.empty:
        return

    # 3. 사이드바 (필터 설정)
    with st.sidebar:
        st.header("🔍 분석 필터 설정")
        
        all_categories = df['구분'].unique().tolist()
        all_categories.insert(0, '전체')
        
        selected_category = st.selectbox(
            "어떤 브랜드 타입을 볼까?",
            options=all_categories,
            index=0
        )
        
        # '총점포수' 최소 기준 설정
        max_val = int(df['총점포수'].max())
        min_stores = st.slider(
            "최소 해외 점포수 기준은?",
            min_value=1, 
            max_value=max_val, 
            value=min(10, max_val),
            step=1
        )
        
        st.markdown("---")
        st.info("💡 **팁:** 데이터를 필터링해서 자세히 살펴보자!")

    # 4. 필터링된 데이터 준비
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
    
    # 7. 전체 데이터 테이블 표시
    st.header("📊 상세 데이터 테이블")
    display_cols = ['체명', '브랜드', '주요메뉴', '구분', '진출국가', '총점포수']
    display_df = filtered_df.filter(items=display_cols, axis=1)
    
    st.dataframe(display_df, use_container_width=True)

# 8. 앱 실행
if __name__ == '__main__':
    # Streamlit Cloud에서 멀티페이지 앱을 실행할 때는 
    # 'pages' 폴더 밖의 메인 스크립트(main.py)가 있어야 하거나, 
    # 아니면 이 파일(00_수행평가.py)을 메인 스크립트로 지정해야 합니다.
    # 만약 'pages' 폴더 구조를 사용하고 있다면, 이 파일이 잘 작동할 거예요!
    app()
