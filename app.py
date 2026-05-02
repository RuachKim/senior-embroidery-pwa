import streamlit as st
from digitizer import create_embroidery_from_image

st.set_page_config(page_title="쉬운 자수 만들기", layout="centered")

# 시니어 친화적 UI를 위한 커스텀 CSS (큰 폰트, 큰 버튼)
st.markdown("""
<style>
    .big-title {
        font-size: 36px !important;
        font-weight: 800 !important;
        color: #2E4053;
    }
    .big-font {
        font-size: 24px !important;
        font-weight: 600 !important;
        margin-top: 15px;
        margin-bottom: 5px;
    }
    .stButton>button {
        width: 100%;
        height: 70px;
        font-size: 24px;
        font-weight: bold;
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        border: none;
    }
    .stDownloadButton>button {
        width: 100%;
        height: 70px;
        font-size: 24px;
        font-weight: bold;
        background-color: #008CBA;
        color: white;
        border-radius: 10px;
        border: none;
        margin-top: 20px;
    }
    div[data-testid="stFileUploader"] {
        padding: 20px;
        border: 3px dashed #4CAF50;
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">🧵 쉬운 자수 만들기</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 18px; color: #555;">어르신들도 쉽게! 그림이나 글씨를 자수 파일로 바꿔보세요.</p>', unsafe_allow_html=True)

st.markdown('<p class="big-font">1️⃣ 사진 올리기</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("스마트폰으로 찍은 그림이나 글씨 사진을 올려주세요.", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="올려주신 사진입니다", use_column_width=True)
    
    st.markdown('<p class="big-font">2️⃣ 설정하기</p>', unsafe_allow_html=True)
    
    # 캔버스 크기 커스터마이징 (사용자 피드백 반영)
    st.markdown("**원하시는 자수의 크기를 설정해주세요. (기본값: 가로 10cm, 세로 10cm)**")
    col1, col2 = st.columns(2)
    with col1:
        hoop_width = st.number_input("가로 크기 (mm)", min_value=10, max_value=300, value=100, step=10)
    with col2:
        hoop_height = st.number_input("세로 크기 (mm)", min_value=10, max_value=300, value=100, step=10)
        
    st.markdown("**어떤 브랜드의 자수기를 쓰시나요?**")
    machine_format = st.radio("자수기 종류 선택", options=["Brother (.PES)", "Tajima (.DST)", "Janome (.JEF)"])
    
    format_ext = "pes"
    if "DST" in machine_format:
        format_ext = "dst"
    elif "JEF" in machine_format:
        format_ext = "jef"
        
    # 옵션: 음성 안내 (사용자 피드백 반영: 메인이 아닌 옵션으로 처리)
    use_tts = st.checkbox("안내 음성 듣기 (옵션)")

    st.markdown('<p class="big-font">3️⃣ 만들기 및 저장하기</p>', unsafe_allow_html=True)
    
    if st.button("자수 파일 만들기!"):
        with st.spinner("자수 파일을 만들고 있습니다... 잠시만 기다려주세요."):
            try:
                emb_data = create_embroidery_from_image(
                    uploaded_file, 
                    format_ext=format_ext, 
                    width_mm=hoop_width, 
                    height_mm=hoop_height
                )
                
                st.success("🎉 완성되었습니다! 아래 파란색 버튼을 눌러 저장하세요.")
                
                st.download_button(
                    label=f"📥 {format_ext.upper()} 파일 저장하기",
                    data=emb_data,
                    file_name=f"my_embroidery.{format_ext}",
                    mime="application/octet-stream"
                )
                
                # HTML5 SpeechSynthesis API를 활용한 클라이언트 사이드 TTS 구현 (옵션)
                if use_tts:
                    tts_js = f"""
                    <script>
                        var msg = new SpeechSynthesisUtterance("자수 파일이 완성되었습니다. 아래 버튼을 눌러 저장하세요.");
                        msg.lang = 'ko-KR';
                        window.speechSynthesis.speak(msg);
                    </script>
                    """
                    st.components.v1.html(tts_js, height=0, width=0)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다. 그림의 선이 더 뚜렷해야 합니다. (상세: {e})")
