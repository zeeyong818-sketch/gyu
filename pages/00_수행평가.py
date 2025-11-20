import streamlit as st
import pandas as pd
# 파일 경로 처리를 위해 os 라이브러리를 가져옵니다.
import os 
import io

# 1. 데이터를 불러오는 함수 (파일 경로 수정)
@st.cache_data
def load_data():
    # 🌟🌟 핵심 수정: 파일 경로를 현재 스크립트 기준으로 루트 폴더로 지정 🌟🌟
    # 1. 현재 스크립트의 디렉토리 (예: /app/pages)
    current_dir = os.path.dirname(__file__) 
    # 2. 루트 폴더의 altificial.csv 경로 (예: /app/altificial.csv)
    file_path = os.path.join(current_dir, '..', 'altificial.csv')
    
    # st.write(f"디버깅 정보: 파일 경로: {file_path}") # 필요하다면 이 줄로 경로 확인

    try:
        # 파일 경로를 사용하여 CSV를 읽습니다. (다중 인코딩 시도)
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file_path, encoding='cp949')
            except:
                df = pd.read_csv(file_path, encoding='euc-kr')
                
    except FileNotFoundError:
        # 파일이 없을 경우 친절하게 에러 메시지를 띄웁니다.
        st.error(f"🚨 파일을 찾을 수 없어요! **altificial.csv** 파일이 루트 폴더에 있는지 확인해 주세요. 예상 경로: {file_path}")
        return pd.DataFrame() # 빈 DataFrame 반환

    # ⭐⭐ 컬럼 이름 공백 오류 방지: 컬럼 이름의 공백을 제거합니다. ⭐⭐
    df.columns = df.columns.str.strip()

    # 데이터 전처리: '구분', '주요메뉴'의 앞뒤 공백 제거 및 타입 정리
    df['구분'] = df['구분'].astype(str).str.strip()
    
    try:
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
        # 파일 로드 실패 시 여기서 앱 실행을 멈춥니다.
        return

    # 3. 사이드바 (사용자가 선택할 수 있는 필터)
    with st.sidebar:
        st.header("🔍 분석 필터 설정")
        
        # '구분' (한식/비한식)을 선택하는 위젯
        all_categories = df['구분'].unique().tolist()
        all_categories.insert(0, '전체')
        
        selected_category = st.selectbox(
            "어떤 브랜드 타입을 볼까?",
            options=all_categories,
            index=0
        )
        
        # '총점포수' 최소 기준 설정 (최대값보다 작은 값으로 설정해야 에러 없음)
        max_val = int(df['총점포수'].max()) if not df.empty else 1
        min_stores = st.slider(
            "최소 해외 점포수 기준은?",
            min_value=1, 
            max_value=max_val, 
            value=min(10, max_val), # 기본값 10, 최대값보다 크면 안 됨
            step=1
        )
        
        st.markdown("---")
        st.info("💡 **팁:** 데이터를 필터링해서 자세히 살펴보자!")

    # 4. 필터링된 데이터 준비 (메인 화면)
    filtered_df = df.copy()
    
    if selected_category != '전체':
        filtered_df = filtered_df[filtered_df['구분'] == selected_category]
        
    filtered_df = filtered_df[filtered_df['총점포수'] >= min
