import streamlit as st
import pandas as pd
import io

# 1. 데이터를 불러오는 함수 (Streamlit Cloud 환경에서는 직접 업로드된 파일을 읽습니다.)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('altificial.csv', encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv('altificial.csv', encoding='cp949')
        except:
            df = pd.read_csv('altificial.csv', encoding='euc-kr')
    except FileNotFoundError:
        st.error("🚨 'altificial.csv' 파일을 찾을 수 없어요. 파일을 Streamlit 프로젝트 폴더에 넣어주세요!")
        return pd.DataFrame() # 빈 DataFrame 반환

    # ⭐⭐ 오류 해결: 컬럼 이름의 공백을 제거합니다. ⭐⭐
    df.columns = df.columns.str.strip()

    # 데이터 전처리: '구분', '주요메뉴' 등 필요한 열의 타입을 정리합니다.
    # 이제 '주요메뉴'에 접근할 때 오류가 나지 않아요!
    df['구분'] = df['구분'].str.strip()
    df['주요메뉴'] = df['주요메뉴'].astype(str).str.strip() # 혹시 모를 NaN 값 처리를 위해 str로 변환 후 strip

    # NaN 값 처리: '체명'의 결측치는 '정보없음'으로 채워줍니다.
    df['체명'] = df['체명'].fillna('정보없음')

    return df

# 2. 메인 Streamlit 앱 함수 (이하 동일)
# ...
