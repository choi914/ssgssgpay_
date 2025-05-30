import streamlit as st
from qr_generator import generate_qr_code
from datetime import datetime

st.set_page_config(page_title="쓱쓱페이", page_icon="💳")

# 세션 상태 초기화
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'nickname' not in st.session_state:
    st.session_state.nickname = ""
if 'point' not in st.session_state:
    st.session_state.point = 1000  # 초기 포인트 1000P 지급
if 'history' not in st.session_state:
    st.session_state.history = []
if 'total_given_today' not in st.session_state:
    st.session_state.total_given_today = 0
if 'all_records' not in st.session_state:
    st.session_state.all_records = []

# 메인 화면 분기
if not st.session_state.user_type:
    # 로그인 화면
    st.title("💳 쓱쓱페이")
    user_type = st.selectbox("당신은 누구인가요?", ["선택하세요", "사용자", "소상공인"])
    nickname = st.text_input("닉네임 또는 이름을 입력하세요")

    if st.button("로그인"):
        if user_type != "선택하세요" and nickname:
            st.session_state.user_type = user_type
            st.session_state.nickname = nickname
            st.experimental_rerun()
        else:
            st.warning("모든 정보를 입력해주세요.")

else:
    # 로그아웃 버튼 (사이드바에 배치)
    if st.sidebar.button("로그아웃"):
        st.session_state.user_type = None
        st.session_state.nickname = ""
        st.session_state.point = 1000  # 포인트 초기화
        st.session_state.history = []  # 이력 초기화
        st.session_state.total_given_today = 0  # 금일 적립 포인트 초기화
        st.session_state.all_records = []  # 전체 기록 초기화
        st.experimental_rerun()

    # 환영 메시지
    st.title("💳 쓱쓱페이")
    st.success(f"{st.session_state.nickname}님 환영합니다! ({st.session_state.user_type})")

    if st.session_state.user_type == "사용자":
        # 사용자 전용 화면
        st.header("📌 사용자 전용 화면")
        
        # 포인트 정보 표시
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="보유 포인트", value=f"{st.session_state.point:,} P")
        with col2:
            # 최근 거래 금액 계산
            recent_transactions = sum(int(log.split('P')[0]) for _, log in st.session_state.history if 'P 사용' in log)
            st.metric(label="이번 달 사용 포인트", value=f"{recent_transactions:,} P")
        
        # 포인트 관리 탭
        tab1, tab2, tab3 = st.tabs(["💰 포인트 사용", "💵 포인트 적립", "📊 거래 내역"])
        
        with tab1:
            st.subheader("포인트 사용")
            use = st.number_input("사용할 포인트", min_value=0, max_value=st.session_state.point, step=100, key="use_point")
            if st.button("포인트 사용하기"):
                if use <= st.session_state.point:
                    st.session_state.point -= use
                    st.session_state.history.append(
                        (datetime.now(), f"{use}P 사용")
                    )
                    st.success(f"{use:,}P 사용 완료!")
                else:
                    st.warning("포인트가 부족합니다.")

        with tab2:
            st.subheader("포인트 적립")
            earn = st.number_input("적립할 포인트", min_value=0, step=100, key="earn_point")
            if st.button("포인트 적립하기"):
                st.session_state.point += earn
                st.session_state.history.append(
                    (datetime.now(), f"{earn}P 적립")
                )
                st.success(f"{earn:,}P 적립 완료!")
        
        with tab3:
            st.subheader("거래 내역")
            if st.session_state.history:
                for time, log in reversed(st.session_state.history):
                    with st.container():
                        col1, col2 = st.columns([2, 3])
                        with col1:
                            st.write(f"📅 {time.strftime('%Y-%m-%d %H:%M')}")
                        with col2:
                            if "사용" in log:
                                st.write(f"🔻 {log}")
                            else:
                                st.write(f"🔺 {log}")
            else:
                st.info("아직 거래 내역이 없습니다.")
        
        # QR 스캔 섹션
        st.divider()
        st.subheader("💳 QR 결제")
        st.write("카메라로 QR 코드를 스캔하여 결제를 진행하세요.")
        if st.button("QR 스캔 시작"):
            st.info("현재 QR 코드 스캔 기능은 개발 중입니다.")

    elif st.session_state.user_type == "소상공인":
        # 소상공인 전용 화면
        st.header("🏪 소상공인 전용 화면")
        
        # 매출 및 포인트 정보
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="오늘 적립 포인트", value=f"{st.session_state.total_given_today:,} P")
        with col2:
            total_customers = len(set(record[0] for record in st.session_state.all_records))
            st.metric(label="총 고객 수", value=f"{total_customers:,} 명")
        
        # 탭 구성
        tab1, tab2, tab3 = st.tabs(["👤 포인트 적립", "📊 적립 현황", "🔲 QR 코드"])
        
        with tab1:
            st.subheader("고객 포인트 적립")
            user_name = st.text_input("고객 이름")
            amount = st.number_input("적립할 포인트", min_value=100, step=100, key="store_earn")
            
            if st.button("포인트 적립"):
                if user_name and amount:
                    now = datetime.now()
                    st.session_state.total_given_today += amount
                    st.session_state.all_records.append((user_name, amount, now))
                    st.success(f"{user_name}님에게 {amount:,}P 적립 완료!")
                else:
                    st.warning("고객 이름과 포인트를 모두 입력해주세요.")
        
        with tab2:
            st.subheader("포인트 적립 현황")
            if st.session_state.all_records:
                # 오늘 날짜 기준 필터링
                today = datetime.now().date()
                today_records = [record for record in st.session_state.all_records 
                               if record[2].date() == today]
                
                # 오늘의 통계
                st.write("📅 오늘의 통계")
                total_points = sum(record[1] for record in today_records)
                unique_customers = len(set(record[0] for record in today_records))
                st.write(f"- 총 적립 포인트: {total_points:,}P")
                st.write(f"- 방문 고객 수: {unique_customers}명")
                
                # 전체 적립 내역
                st.write("📋 전체 적립 내역")
                for user, point, time in reversed(st.session_state.all_records):
                    with st.container():
                        col1, col2, col3 = st.columns([2, 2, 1])
                        with col1:
                            st.write(f"📅 {time.strftime('%Y-%m-%d %H:%M')}")
                        with col2:
                            st.write(f"👤 {user}")
                        with col3:
                            st.write(f"💰 {point:,}P")
            else:
                st.info("아직 적립 내역이 없습니다.")
        
        with tab3:
            st.subheader("QR 코드 생성")
            qr_col1, qr_col2 = st.columns(2)
            
            with qr_col1:
                qr_amount = st.number_input("결제 금액 (원)", min_value=100, step=100)
                qr_point = int(qr_amount * 0.01)  # 1% 포인트 적립
                st.write(f"적립 예정 포인트: {qr_point:,}P")
            
            with qr_col2:
                store_name = st.text_input("가게 이름", st.session_state.nickname)
            
            if st.button("QR 코드 생성"):
                if qr_amount and store_name:
                    payment_data = f"store={store_name}&amount={qr_amount}&point={qr_point}"
                    try:
                        qr_image = generate_qr_code(payment_data)
                        st.image(f"data:image/png;base64,{qr_image}", 
                                caption=f"결제금액: {qr_amount:,}원 (적립포인트: {qr_point:,}P)")
                        st.download_button(
                            label="QR 코드 다운로드",
                            data=qr_image,
                            file_name="payment_qr.png",
                            mime="image/png"
                        )
                    except Exception as e:
                        st.error(f"QR 코드 생성 중 오류가 발생했습니다: {str(e)}")
                else:
                    st.warning("결제 금액과 가게 이름을 모두 입력해주세요.") 
