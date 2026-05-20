import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from config import GIA_ROW_NAME, PRINT_HTML, TIEN_BAN_HANG, NOTE_HTML
from views.order_entry import generate_vietqr_html
from util import convert_name, get_secret

SHARE_URL = get_secret("SHARE_URL")
GSP_CRED = get_secret("GSP_CRED")

def show_order_lookup(gia_mat_hang):
    st.title("📄 Tra cứu thông tin đơn hàng")
    df_lookup = pd.DataFrame(st.session_state.sheet_data[GIA_ROW_NAME+1:], columns=st.session_state.sheet_data[GIA_ROW_NAME])
    df_lookup.columns = df_lookup.columns.str.replace('\n', '', regex=True)
    df_lookup = df_lookup.loc[:, ~df_lookup.columns.duplicated()]

    with st.form("form_tra_cuu"):
        stt_target = st.number_input("🔢 Điền STT đơn hàng cần tra cứu:", min_value=1, step=1)
        triggered = st.form_submit_button("Tra cứu")

    @st.dialog(title="🧾 Chi tiết đơn hàng", width="large")
    def display_invoice(target_id):
        filtered = df_lookup[df_lookup["STT"] == str(target_id)]
        if filtered.empty:
            st.error("⚠️ Số thứ tự đơn hàng này không tồn tại trên hệ thống.")
            return

        row_dict = {k: v for k, v in filtered.iloc[0].to_dict().items() if str(v).strip() not in ["", "None", "nan"]}
        
        # Phân tách sản phẩm và thông tin khách hàng từ bản ghi gốc
        thong_tin_dat_hang = {}
        mon_hang_da_mua = {}

        for k, v in row_dict.items():
            if k.strip() in gia_mat_hang and float(v) > 0: 
                mon_hang_da_mua[k] = v
            else: 
                thong_tin_dat_hang[k] = v

        # --- ĐOẠN PROCESS ĐƯỢC KHÔI PHỤC VÀ ĐỒNG BỘ CHÍNH XÁC ---
        df_khach_hang = pd.DataFrame(list(thong_tin_dat_hang.items()), columns=["Thông tin", "Giá trị"])
        
        # Đổi tên hiển thị cho các tiêu đề cột dài dòng công kềnh
        df_khach_hang.loc[df_khach_hang["Thông tin"] == "CHI TIẾT ĐƠN (VUI LÒNG ĐIỀN CHÍNH XÁC VỚI Ô CỘT SỐ LƯỢNG BÊN PHẢI)", "Thông tin"] = "CHI TIẾT ĐƠN"
        df_khach_hang.loc[df_khach_hang["Thông tin"] == "TỔNG TIỀNCẦN TRẢ(1)+(2)", "Thông tin"] = "TỔNG TIỀN CẦN TRẢ"
        df_khach_hang.loc[df_khach_hang["Thông tin"] == TIEN_BAN_HANG, "Thông tin"] = "TIỀN HÀNG"
        
        # Định dạng lại tiền tệ hiển thị dạng chấm phân cách (Ví dụ: 1200000 -> 1.200.000)
        df_khach_hang.loc[df_khach_hang["Thông tin"] == "TỔNG TIỀN CẦN TRẢ", "Giá trị"] = df_khach_hang.loc[
            df_khach_hang["Thông tin"] == "TỔNG TIỀN CẦN TRẢ", "Giá trị"
        ].map(lambda x: f"{int(x.replace('.', '').replace(',', '')):,}".replace(",", "."))
        
        df_khach_hang.loc[df_khach_hang["Thông tin"] == "TIỀN HÀNG", "Giá trị"] = df_khach_hang.loc[
            df_khach_hang["Thông tin"] == "TIỀN HÀNG", "Giá trị"
        ].map(lambda x: f"{int(x.replace('.', '').replace(',', '')):,}".replace(",", "."))

        # Khởi tạo bảng danh mục món hàng mua thực tế
        df_mon_hang = pd.DataFrame(list(mon_hang_da_mua.items()), columns=["Sản phẩm", "Số lượng"])
        
        # Lọc bỏ bớt các trường thông tin nội bộ của kho khi kết xuất bản in hóa đơn
        df_khach_hang_in = df_khach_hang[df_khach_hang["Thông tin"] != "Đã thanh toán"]
        df_khach_hang_in = df_khach_hang_in[df_khach_hang_in["Thông tin"] != "ĐÃ SOẠN ĐƠN"]
        df_khach_hang_in = df_khach_hang_in[df_khach_hang_in["Thông tin"] != "ĐÃ GIAO TNV(TNV điền hoặc người giao điền)"]
        # --------------------------------------------------------

        col1, col2 = st.columns(2)
        with col1:
            create_qr = st.button("💳 Bấm vào đây để tạo mã QR thanh toán")

        if create_qr:
            # Lấy số tiền thô sạch để truyền vào API VietQR
            raw_amount_str = row_dict.get('TỔNG TIỀNCẦN TRẢ(1)+(2)', '0').replace('.', '').replace(',', '')
            try:
                amt = int(raw_amount_str)
                msg = f"BANHANGF18 DON{target_id} {convert_name(row_dict.get('TÊN TNV BÁN', 'TNV'))}"
                st.markdown(generate_vietqr_html(amt, msg), unsafe_allow_html=True)
            except ValueError:
                st.error("❌ Không thể tạo mã QR lúc này. Thử lại sau.")
        
        with col2:
            # Render nút lệnh in truyền đúng DataFrame đã lọc sạch (df_khach_hang_in) và danh sách sản phẩm (df_mon_hang)
            html_invoice = PRINT_HTML.format(
                customer_table=df_khach_hang_in.to_html(index=False, border=1), 
                order_table=df_mon_hang.to_html(index=False, border=1)
            )
            components.html(html_invoice, height=80)

        # Hiển thị cấu trúc xem nhanh trên Giao diện Streamlit cho người dùng đối soát
        st.subheader("📌 Thông tin khách hàng")
        st.table(df_khach_hang)
        st.subheader("🛒 Danh sách sản phẩm mua")
        st.table(df_mon_hang)

    if triggered:
        display_invoice(stt_target)

    st.markdown(NOTE_HTML, unsafe_allow_html=True)
    embed_url = SHARE_URL.replace("/edit", "/preview")
    components.iframe(embed_url, height=500, scrolling=True)