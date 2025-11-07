import os, json, base64, unicodedata
import pandas as pd
import altair as alt
import requests
import streamlit as st
import streamlit.components.v1 as components
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from config import (
                    gia_mat_hang, product_column_map, thoi_gian_nhan_hang, 
                    TARGET_SALES, SCOPE, STK, TEN_CHU_TK, BIN_BANK, MEO_HTML
                )

load_dotenv()

def get_secret(key):
    return st.secrets.get(key) or os.getenv(key)

SHARE_URL = get_secret("SHARE_URL")
GSP_CRED = get_secret("GSP_CRED")

json_creds = json.loads(base64.b64decode(GSP_CRED).decode("utf-8"))

st.set_page_config(
    page_title="ÔLiu F17 - Bán hàng",
    page_icon="./oliu.jpg",                
    layout="wide",
    initial_sidebar_state="expanded"
)


menu = st.sidebar.radio("📋 Menu", ["📥 Nhập đơn hàng", "📄 Xem dữ liệu", "📊 Thống kê", "👉 Về chúng tôi"])

creds = ServiceAccountCredentials.from_json_keyfile_dict(json_creds, SCOPE)
client = gspread.authorize(creds)
sheet = client.open_by_url(SHARE_URL).sheet1


def clean_money_column(series):
    return (
        series.astype(str)
        .str.replace(r"[^\d]", "", regex=True)  # Xoá ký tự không phải số
        .replace("", "0")                       # Thay thế chuỗi rỗng bằng "0"
        .astype(float)
    )

def convert_name(text: str):
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return ' '.join(text.lower().strip().split())

def custom_progress_bar(ratio):
    percent = int(min(ratio, 1.0) * 100)

    st.markdown(f"""
    <div style="position: relative; background-color: #e0e0e0; height: 24px; border-radius: 12px; overflow: hidden; margin-top: 10px; margin-bottom: 10px;">
        <div style="
            width: {percent}%;
            background-color: #4B8BBE;
            height: 100%;
            transition: width 0.5s;
        "></div>
        <div style="
            position: absolute;
            top: 0;
            left: calc({percent}% - 20px);
            height: 100%;
            width: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        ">
            🚀
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_dashboard():
    st.title("📊 Xem qua KPI nào")

    # Đọc dữ liệu từ Google Sheet (hoặc cache lại để không load nhiều)
    data = sheet.get_all_values()
    df = pd.DataFrame(data[5:], columns=data[4])
    df.columns = df.columns.str.replace('\n', '', regex=True)

    df["TIỀN BÁN HÀNG (2)"] = clean_money_column(df["TIỀN BÁN HÀNG (2)"])
    df["TÊN TNV BÁN"] = df["TÊN TNV BÁN"].fillna("Chưa xác định")

    ### 🥇 1. Top TNV bán hàng
    with st.container():
        st.markdown("### 🎯 Tổng doanh số và mục tiêu")
        total_sales = df["TIỀN BÁN HÀNG (2)"].sum()
        delta = total_sales - TARGET_SALES
        ratio = total_sales / TARGET_SALES

        col1, col2 = st.columns([2, 3])

        with col1:
            st.metric(
                "💰 Doanh số hiện tại", 
                f"{total_sales:,.0f} VND / {TARGET_SALES:,.0f} VND", 
                delta=f"{delta:,.0f} VND", 
                delta_color="normal" if ratio < 1 else "inverse"
            )

            if ratio >= 1:
                st.success("🎉 Đã vượt mục tiêu! Tuyệt vời! 🚀")
            elif ratio >= 0.8:
                st.warning("⚠️ Sắp đạt mục tiêu, cố lên! 💪")
            else:
                st.info("📈 Tiếp tục phấn đấu để đạt mục tiêu nhé!")

        with col2:
            custom_progress_bar(ratio)

  
    st.markdown("---")

    ### 🏆 VÙNG 2: Top TNV bán hàng

    with st.container():
        st.markdown("### 🏆 Đại lộ danh vọng")

        top_tnv = (
            df.groupby("TÊN TNV BÁN")["TIỀN BÁN HÀNG (2)"]
            .sum().reset_index()
            .rename(columns={"TIỀN BÁN HÀNG (2)": "TIỀN BÁN HÀNG"})
            .sort_values(by="TIỀN BÁN HÀNG", ascending=False)
            .head(10)
        )

        base = alt.Chart(top_tnv).encode(
            x=alt.X("TIỀN BÁN HÀNG:Q", title="Doanh số (VND)"),
            y=alt.Y("TÊN TNV BÁN:N", sort="-x", title="TNV")
        )

        bars = base.mark_bar().encode(
            color=alt.Color("TIỀN BÁN HÀNG:Q", scale=alt.Scale(scheme='greenblue'), legend=None),
            tooltip=[
                alt.Tooltip("TÊN TNV BÁN", title="Người bán"), 
                alt.Tooltip("TIỀN BÁN HÀNG", title="Tiền bán hàng (VND)", format=",.0f")
            ]
        )

        text = base.mark_text(
            align='left',
            baseline='middle',
            dx=3  # khoảng cách với cột
        ).encode(
            text=alt.Text("TIỀN BÁN HÀNG:Q", format=",.0f")
        )

        chart = (bars + text).properties(height=400)

        st.altair_chart(chart, use_container_width=True)

    st.markdown("---")
    ### 📦 VÙNG 3: Thống kê mặt hàng
            
    with st.container():
        st.markdown("### 💵 Doanh thu theo mặt hàng")
        product_columns = df.columns[14:33]
        product_data = df[product_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
        mat_hang_so_luong = product_data.sum().to_dict()

        # 👉 Tạo dataframe doanh thu
        df_doanh_thu = pd.DataFrame([
            {
                "Mặt hàng": ten.strip(),
                "Số lượng": so_luong,
                "Giá bán (VND)": gia_mat_hang.get(ten.strip(), 0),
                "Doanh thu (VND)": so_luong * gia_mat_hang.get(ten.strip(), 0)
            }
            for ten, so_luong in mat_hang_so_luong.items()
            if so_luong > 0
        ])
        if not df_doanh_thu.empty:
            df_doanh_thu = df_doanh_thu.sort_values(by="Doanh thu (VND)", ascending=False).reset_index(drop=True)
            tong_tien = df_doanh_thu["Doanh thu (VND)"].sum()
            
            st.markdown(f" #### **Tổng doanh thu các mặt hàng:** `{tong_tien:,.0f} VND`")
            
            col1, col2 = st.columns([2, 3])
            with col1:
                st.dataframe(df_doanh_thu.reset_index(drop=True).style.format({
                            "Giá bán (VND)": lambda x: f"{x:,.0f}".replace(",", "."),
                            "Doanh thu (VND)": lambda x: f"{x:,.0f}".replace(",", "."),
                            "Số lượng": lambda x: f"{x:,.0f}".replace(",", ".")
                        }), use_container_width=True)
            with col2:
                chart_revenue = alt.Chart(df_doanh_thu).mark_bar().encode(
                    x=alt.X("Doanh thu (VND):Q", title="Doanh thu (VND)"),
                    y=alt.Y("Mặt hàng:N", sort="-x"),
                    color=alt.Color("Doanh thu (VND):Q", scale=alt.Scale(scheme="greens"), legend=None),
                    tooltip=[
                        alt.Tooltip("Mặt hàng", title="Tên sản phẩm"),
                        alt.Tooltip("Số lượng", title="Số lượng"),
                        alt.Tooltip("Giá bán (VND)", title="Giá 1 SP", format=",.0f"),
                        alt.Tooltip("Doanh thu (VND)", title="Doanh thu", format=",.0f")
                    ]
                ).properties(height=500)

                st.altair_chart(chart_revenue, use_container_width=True)
        else:
            st.warning("⚠️ Chưa có mặt hàng nào để tính doanh thu.")


### main code ###
def validate_required():
    if not ten_tnv.strip():
        return "Tên TNV bán"
    if not ten_khach.strip():
        return "Tên khách"
    if not chi_tiet_don.strip():
        return "Chi tiết đơn hàng"
    return None

def show_qr_thanh_toan(amount: int, ndck: str):
    with st.expander("", expanded=True):
        st.markdown(f"**📢 Vui lòng kiểm tra kĩ thông tin chuyển khoản trước khi chuyển tiền**")
        
        st.markdown(f"**🔢 Số tài khoản:** {STK}")
        st.markdown(f"**👤 Tên người nhận:** {TEN_CHU_TK}")
        st.markdown(f"**💰 Số tiền:** {amount:,.0f} VND")
        st.markdown(f"**📝 Nội dung:** {ndck}")
        
        res = requests.post("https://api.vietqr.io/v2/generate", json={
            "accountNo": STK,
            "accountName": TEN_CHU_TK,
            "acqId": BIN_BANK,
            "amount": amount,
            "addInfo": ndck,
            "template": "compact2"
        })
        data = res.json()
        qr_url = data['data']['qrDataURL']
        st.markdown(
            f"""
            <div style='text-align:center;'>
                <img src="{qr_url}" 
                    alt="QR Thanh toán"
                    style="max-width:60%; height:auto; border-radius:10px;" />
                <p><em>📱 Quét để chuyển khoản</em></p>
            </div>
            """,
            unsafe_allow_html=True
        )


if menu == "📥 Nhập đơn hàng":
    components.html(MEO_HTML, height=80)
    st.title("📦 Nhập đơn hàng")
    st.markdown("Vui lòng điền các thông tin bên dưới. Sau đó ấn 'Xác nhận & Gửi đơn'")
    with st.form("form_nhap_don"):
        # ==== PHẦN 1: Thông tin khách hàng ====
        with st.expander("ℹ️ Thông tin khách hàng", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                ten_tnv = st.text_input("👤 Tên TNV bán *")
                sdt = st.text_input("📞 SĐT khách")
                quan_tinh = st.text_input("🗺️ Quận/Tỉnh")
            with col2:
                ten_khach = st.text_input("👥 Tên khách *")
                dia_chi = st.text_input("🏠 Địa chỉ (nếu ship)")
                thoi_gian_nhan = st.selectbox("🕓 Thời gian nhận hàng", thoi_gian_nhan_hang)
            chi_tiet_don = st.text_area("📋 Chi tiết đơn hàng *")

        # ==== PHẦN 2: Mật ong, Mắm, Điều ====
        with st.expander("🍯 Mật ong, Mắm, Điều", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                mat_ong_500ml = st.number_input("🍯 Mật ong 500ml", min_value=0, step=1)
                dieu_muoi_200g = st.number_input("🥜 Điều muối 200g", min_value=0, step=1)
                dieu_mam_ot_500g = st.number_input("🌶️ Điều mắm ớt 500g", min_value=0, step=1)
            with col2:
                mat_ong_1l = st.number_input("🍯 Mật ong 1 lít", min_value=0, step=1)
                dieu_muoi_500g = st.number_input("🥜 Điều muối 500g", min_value=0, step=1)
                mam_1l = st.number_input("🥫 Mắm 1 lít", min_value=0, step=1)

        # ==== PHẦN 3: Snack - Mít, Chuối, Khoai, Gạo ====
        with st.expander("🍱 Rau củ quả - trái cây sấy", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                mit_500g = st.number_input("🥭 Mít sấy 500g", min_value=0, step=1)
                ktrb_250g = st.number_input("🥔 Khoai tây rong biển 250g", min_value=0, step=1)
                ktmam_250g = st.number_input("🥔 Khoai tây mắm 250g", min_value=0, step=1)
                km_trung_cua_250g = st.number_input("🍠 Khoai môn trứng cua 250g", min_value=0, step=1)
            with col2:
                thap_cam_500g = st.number_input("🍱 Thập cẩm 500g", min_value=0, step=1)
                ktrb_500g = st.number_input("🥔 Khoai tây rong biển 500g", min_value=0, step=1)
                ktmam_500g = st.number_input("🥔 Khoai tây mắm 500g", min_value=0, step=1)
                km_trung_cua_500g = st.number_input("🍠 Khoai môn trứng cua 500g", min_value=0, step=1)
                chuoi_500g = st.number_input("🍌 Chuối sấy mộc 500g", min_value=0, step=1)
        
        with st.expander("🍚 Cơm cháy, Bánh tráng mắm", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                nep_chay_3 = st.number_input("🍙 Nếp cháy chà bông x3", min_value=0, step=1)
                com_chay_200g = st.number_input("🍚 Cơm cháy chà bông 200g", min_value=0, step=1)
                banh_trang_mam = st.number_input("🥖 Bánh tráng mắm", min_value=0, step=1)
            with col2:
                nep_chay_5 = st.number_input("🍙 Nếp cháy chà bông x5", min_value=0, step=1)
                gao_lut_rb_200g = st.number_input("🌾 Gạo lứt rong biển 200g", min_value=0, step=1)
            
        submitted = st.form_submit_button("🚀 Xác nhận & Gửi đơn", type="primary")

    # Khởi tạo trạng thái nếu chưa có
    if "don_hang_moi" not in st.session_state:
        st.session_state["don_hang_moi"] = None

    @st.dialog(title="🧾 Xác nhận đơn hàng:", width="large")
    def show_data(tong_ket, mat_hang_co_mua, row):
        st.subheader("📌 Thông tin khách hàng")
        df_tong_ket = pd.DataFrame([(k, str(v)) for k, v in tong_ket.items()], columns=["Cột", "Giá trị"])
        st.table(df_tong_ket)

        st.subheader("🛒 Mặt hàng đã đặt")
        df_hang = pd.DataFrame(list(mat_hang_co_mua.items()), columns=["Mặt hàng", "Số lượng"])
        st.table(df_hang)

        # tong_ket.update(mat_hang_co_mua)

        if st.button("📩 Gửi đơn"):
            with st.spinner("⏳ Đang xử lý đơn hàng..."):
                column_values = sheet.col_values(2)
                first_empty_row = len(column_values) + 1
                stt_last_row = sheet.row_values(first_empty_row - 1)[0]
                row[0] = int(stt_last_row) + 1
                for col_idx in range(1, 42):
                    try:
                        value = row[col_idx-1]
                        if value == "":
                            continue
                        sheet.update_cell(first_empty_row, col_idx, value)
                    except IndexError as e:
                        print(f"Lỗi: {e} tại cột {col_idx}")

                stt_don_hang_moi = sheet.row_values(first_empty_row)[0]
                st.toast("✅ Đơn hàng đã ghi thành công!")
                st.toast(f"STT đơn hàng: **{stt_don_hang_moi}**")
                # Lưu trạng thái đơn hàng đã gửi
                st.session_state["don_hang_moi"] = stt_don_hang_moi

        # Nếu đã gửi đơn, hiển thị nút tạo QR
        if st.session_state["don_hang_moi"]:
            if st.button("💳 Bấm vào đây để tạo mã QR thanh toán", type="primary"):
                stt_don_hang_moi = st.session_state["don_hang_moi"]
                data = sheet.get_all_values()
                df = pd.DataFrame(data[5:], columns=data[4])
                df.columns = df.columns.str.replace('\n', '', regex=True)
                df = df.loc[:, ~df.columns.duplicated()]
                df_filtered = df[df["STT"] == str(stt_don_hang_moi)]
                row_data = df_filtered.iloc[0].to_dict()
                filtered_data = {k: v for k, v in row_data.items() if str(v).strip() not in ["", "None", "nan"]}
                amount = int(filtered_data['TỔNG TIỀNCẦN TRẢ(1)+(2)'].replace('.', ''))
                ten_tnv_ban = convert_name(filtered_data['TÊN TNV BÁN'])
                ndck = f"Oliu {str(stt_don_hang_moi)} {ten_tnv_ban}"

                with st.expander("QR Thanh toán", expanded=True):
                    st.markdown(f"**📢 Vui lòng kiểm tra kĩ thông tin chuyển khoản trước khi chuyển tiền**")
                    st.markdown(f"**🔢 Số tài khoản:** {STK}")
                    st.markdown(f"**👤 Tên người nhận:** {TEN_CHU_TK}")
                    st.markdown(f"**💰 Số tiền:** {amount:,.0f} VND")
                    st.markdown(f"**📝 Nội dung:** {ndck}")

                    res = requests.post("https://api.vietqr.io/v2/generate", json={
                        "accountNo": STK,
                        "accountName": TEN_CHU_TK,
                        "acqId": BIN_BANK,
                        "amount": amount,
                        "addInfo": ndck,
                        "template": "compact2"
                    })
                    data = res.json()
                    qr_url = data['data']['qrDataURL']
                    st.markdown(
                        f"""
                        <div style='text-align:center;'>
                            <img src="{qr_url}" 
                                alt="QR Thanh toán"
                                style="max-width:60%; height:auto; border-radius:10px;" />
                            <p><em>📱 Quét để chuyển khoản</em></p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.session_state["don_hang_moi"] = None


    if submitted:
        missing_field = validate_required()
        if missing_field:
            st.warning(f"⚠️ Vui lòng nhập thông tin bắt buộc: **{missing_field}**")
        else:
            tong_ket = {
                "Tên TNV bán": ten_tnv,
                "Tên khách": ten_khach,
                "SĐT khách": sdt,
                "Địa chỉ": dia_chi,
                "Quận/Tỉnh": quan_tinh,
                "Thời gian nhận hàng": str(thoi_gian_nhan),
                "Chi tiết đơn": chi_tiet_don
            }

            # 📦 Mặt hàng (chỉ hiện nếu > 0)
            mat_hang = {
                "Mít 500g": mit_500g,
                "Thập cẩm 500g": thap_cam_500g,
                "Chuối mộc 500g": chuoi_500g,           
                "Khoai tây rong biển 250g": ktrb_250g,
                "Khoai tây rong biển 500g": ktrb_500g,
                "Khoai tây mắm 250g": ktmam_250g,
                "Khoai tây mắm 500g": ktmam_500g,
                "Khoai môn trứng cua 250g": km_trung_cua_250g,
                "Khoai môn trứng cua 500g": km_trung_cua_500g,
                "Nếp cháy chà bông x3": nep_chay_3,
                "Nếp cháy chà bông x5": nep_chay_5,
                "Cơm cháy chà bông 200g": com_chay_200g,
                "Gạo lứt rong biển 200g": gao_lut_rb_200g,
                "Bánh tráng mắm": banh_trang_mam,
                "Mật ong 500ml": mat_ong_500ml,
                "Mật ong 1 lít": mat_ong_1l,
                "Mắm 1 lít": mam_1l,
                "Điều rang muối 200g": dieu_muoi_200g,
                "Điều rang muối 500g": dieu_muoi_500g,
                "Điều mắm ớt 500g": dieu_mam_ot_500g
            }

            # 👉 Lọc các mặt hàng có số lượng > 0
            mat_hang_co_mua = {k: v for k, v in mat_hang.items() if v > 0}

            row = [""] * 40

            # Gán các thông tin khách hàng
            row[1] = ten_tnv
            row[2] = ten_khach
            row[3] = chi_tiet_don
            row[4] = sdt
            row[5] = dia_chi
            row[6] = quan_tinh
            row[7] = str(thoi_gian_nhan)

            # Gán các mặt hàng có mua vào đúng cột
            for name, quantity in mat_hang_co_mua.items():
                col_idx = product_column_map[name]
                row[col_idx - 1] = quantity  # -1 vì Python index bắt đầu từ 0

            show_data(tong_ket, mat_hang_co_mua, row)


elif menu == "📄 Xem dữ liệu":
    components.html(MEO_HTML, height=80)
    st.title("📄 Dữ liệu đơn hàng")
    data = sheet.get_all_values()
    df = pd.DataFrame(data[5:], columns=data[4])
    df.columns = df.columns.str.replace('\n', '', regex=True)
    df = df.loc[:, ~df.columns.duplicated()]

    # --- Giao diện nhập STT ---
    with st.form("form_stt"):
        stt_input = st.number_input("🔢 Nhập STT đơn hàng để tra cứu hoặc tạo mã QR thanh toán:", min_value=1, step=1)
        submitted = st.form_submit_button("Enter")

    # --- Nếu nhấn Enter ---
    if submitted:
        # Tìm dòng theo STT
        df_filtered = df[df["STT"] == str(stt_input)]

        if df_filtered.empty:
            st.warning("⚠️ Không tìm thấy đơn hàng với STT đã nhập.")
        else:
            # Chuyển đổi dòng thành dict
            row_data = df_filtered.iloc[0].to_dict()

            # Hiển thị dialog
            @st.dialog(title="🧾 Thông tin đơn hàng", width="large")
            def show_data():
                filtered_data = {k: v for k, v in row_data.items() if str(v).strip() not in ["", "None", "nan"]}

                thong_tin_dat_hang = {}
                mon_hang_da_mua = {}
                for k, v in filtered_data.items():
                    if k.strip() in list(gia_mat_hang.keys()) and float(v) > 0:
                        mon_hang_da_mua[k] = v
                    elif k not in list(gia_mat_hang.keys()):
                        thong_tin_dat_hang[k] = v

                # --- 3. Hiển thị bảng thông tin ---
                col1, col2 = st.columns([1, 1])
                with col1:
                    create_qr = st.button("💳 Bấm vào đây để tạo mã QR thanh toán")
                
                if create_qr:
                    amount = int(filtered_data['TỔNG TIỀNCẦN TRẢ(1)+(2)'].replace('.', ''))
                    ten_tnv_ban = convert_name(filtered_data['TÊN TNV BÁN'])
                    ndck = f"Oliu {str(stt_input)} {ten_tnv_ban}"
                    show_qr_thanh_toan(amount, ndck)
                
                df_khach_hang = pd.DataFrame(list(thong_tin_dat_hang.items()), columns=["Thông tin", "Giá trị"])
                df_mon_hang = pd.DataFrame(list(mon_hang_da_mua.items()), columns=["Sản phẩm", "Số lượng"])
                
                df_khach_hang_in = df_khach_hang[df_khach_hang["Thông tin"] != "Đã thanh toán"]
                df_khach_hang_in = df_khach_hang_in[df_khach_hang_in["Thông tin"] != "ĐÃ SOẠN ĐƠN"]
                df_khach_hang_in = df_khach_hang_in[df_khach_hang_in["Thông tin"] != "ĐÃ GIAO TNV(TNV điền hoặc người giao điền)"]

                df_khach_hang_in.loc[df_khach_hang_in["Thông tin"] == "CHI TIẾT ĐƠN (VUI LÒNG ĐIỀN CHÍNH XÁC VỚI Ô CỘT SỐ LƯỢNG BÊN PHẢI)", "Thông tin"] = "CHI TIẾT ĐƠN"
                df_khach_hang_in.loc[df_khach_hang_in["Thông tin"] == "TỔNG TIỀNCẦN TRẢ(1)+(2)", "Thông tin"] = "TỔNG TIỀN CẦN TRẢ"
                df_khach_hang_in.loc[df_khach_hang_in["Thông tin"] == "TIỀN BÁN HÀNG (2)", "Thông tin"] = "TIỀN HÀNG"

                with col2:
                    html_code = f"""

                        <div id="print-area" style="display:none;">
                            <h3>📌 Thông tin khách hàng</h3>
                            {df_khach_hang_in.to_html(index=False, border=1)}

                            <h3>🛒 Mặt hàng đã đặt</h3>
                            {df_mon_hang.to_html(index=False, border=1)}
                        </div>

                        <button id="printBtn" style="
                            background-color:#000000; 
                            color:white; 
                            padding:0.4rem 0.9rem; 
                            border:none; 
                            border-radius:0.5rem; 
                            cursor:pointer; 
                            margin-top:-6px; 
                            vertical-align:middle;
                            font-family: 'Source Sans Pro', sans-serif; 
                            font-size:1rem; 
                            font-weight:400;
                            line-height:1.5;
                        ">
                            🖨️ In đơn hàng
                        </button>

                        <script>
                        document.getElementById("printBtn").addEventListener("click", function() {{
                            const printArea = document.getElementById("print-area");
                            if (!printArea) {{
                                alert("Không tìm thấy nội dung để in!");
                                return;
                            }}
                            const printWindow = window.open('', '', 'width=800,height=600');
                            printWindow.document.write('<html><head><title>In đơn hàng</title>');
                            printWindow.document.write('<style>');
                            printWindow.document.write('body{{font-family:Arial;padding:20px;}}');
                            printWindow.document.write('table{{border-collapse:collapse;width:100%;margin-top:10px;}}');
                            printWindow.document.write('th,td{{border:1px solid #ccc;padding:8px;text-align:left;}}');
                            printWindow.document.write('</style></head><body>');
                            printWindow.document.write(printArea.innerHTML);
                            printWindow.document.write('</body></html>');
                            printWindow.document.close();
                            printWindow.focus();
                            printWindow.print();
                        }});
                        </script>
                        """

                    components.html(html_code, height=80)
                
                # --- 4. Hiển thị bảng mặt hàng ---
                st.subheader("📌 Thông tin khách hàng")
                st.table(df_khach_hang)
                if mon_hang_da_mua:
                    st.subheader("🛒 Mặt hàng đã đặt")
                    st.table(df_mon_hang)
                else:
                    st.info("Khách hàng chưa đặt mặt hàng nào.")

            show_data()
    st.markdown(
                """
                <div style="text-align: center; font-size: 13px; color: gray;">
                    Sheet đang hiển thị chỉ có quyền xem, không thể chỉnh sửa
                </div>
                """,
                unsafe_allow_html=True
            )
    embed_url = SHARE_URL.replace("/edit", "/preview")
    components.iframe(embed_url, height=600, scrolling=True)

elif menu == "📊 Thống kê":
    components.html(MEO_HTML, height=80)
    show_dashboard()


elif menu == "👉 Về chúng tôi":
    st.markdown("""
    <style>
    .hero-title {
        text-align: left;
        color: #1E3A8A;
        font-size: 3em;
        font-weight: bold;
        font-family: 'Montserrat', sans-serif;
    }
    .section-title {
        font-size: 2em;
        font-weight: 700;
        margin: 40px 0 20px;
        color: #002B5B;
    }
    </style>

    <div class="hero-title">
        <h1>Đội tình nguyện ÔLiu</h1>
    </div>
    """, unsafe_allow_html=True)


    # --- ABOUT US ---
    st.markdown("<div class='section-title'>📝 Giới thiệu</div>", unsafe_allow_html=True)
    st.markdown("""
    <style>
    .about-container {
        max-width: 1000px;
        margin: 0;
        padding: 20px 25px;
        border-radius: 16px;
        background: #E6F0FF; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        box-sizing: border-box;
    }

    .about-text {
        text-align: justify;
        line-height: 1.6;
        color: #002B5B;
        font-size: 1.05rem;
        word-wrap: break-word;
    }

    .about-text p {
        margin-bottom: 16px;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .about-container {
            padding: 15px 15px;
        }
        .about-text {
            font-size: 0.98rem;
            line-height: 1.5;
        }
    }
    </style>

    <div class="about-container">
    <div class="about-text">
    <p><b>[Ô liu - Olympia In U]</b></p>
    <p>Mọi người đều biết đến “Đường lên đỉnh Olympia” (DLDO) là một chương trình truyền hình dành cho tất cả các bạn học sinh phổ thông trên toàn quốc, nơi thể hiện kiến thức, bản lĩnh của các nhà leo núi qua từng câu hỏi. Không chỉ thế, Olympia còn là một ngã rẽ, là cánh cửa mở ra nhiều cơ hội mới, những mối quan hệ mới cho các bạn thí sinh. Hãy để Ô liu kể bạn nghe câu chuyện của một Olympian - cách mà chúng tôi gọi các bạn tham gia DLDO.</p>
    <p>Kết thúc những trận đấu gay cấn, các bạn rời trường quay trong những cung bậc cảm xúc khác nhau, rồi bạn chợt nhận ra mình đã là một thành viên trong một đại gia đình có tên Olympians - cộng đồng các thí sinh tham gia chương trình DLDO. Olympians luôn cố gắng sẻ chia, góp sức cùng nhau tạo ra những giá trị tốt đẹp cho cuộc sống. Chúng ta gắn kết qua những ngày vui thỏa sức cùng Ono, qua những màn trình diễn ở Olym Acoustic.</p>
    <p>Với mục đích duy trì và phát triển các giá trị tốt đẹp, tinh thần lan tỏa của "nhóm máu O", đội tình nguyện Ô liu được thành lập cùng fanpage để các bạn Olympians và mọi người nói riêng có thể theo dõi, đồng hành cũng như chung tay giúp đỡ những hoàn cảnh khó khăn, góp sức trẻ tạo nên giá trị tử tế.</p>
    <p>Ô liu rất mong nhận được sự quan tâm của các bạn gần xa, nhất là những bạn không phải Olympian. Chúng ta hãy cùng nhau tạo ra giá trị khác biệt. Khi bạn cho đi, bạn chắc chắn sẽ nhận lại nhiều hơn những gì bạn đang có.</p>
    </div>
    </div>
    """, unsafe_allow_html=True)

    # --- MISSION & ACTIVITIES ---
    st.markdown("<div class='section-title'>🎯 Hoạt động của Ô Liu</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    with cols[0]:
        st.markdown("#### 🎮 Tổ chức ngày hội trò chơi")
        st.image("image/hoichobe.jpg", use_container_width =True)
    with cols[1]:
        st.markdown("#### 🎁 Trao quà và học bổng cho các em học sinh")
        st.image("image/hocbong.jpg", use_container_width =True)
    with cols[2]:
        st.markdown("#### 💝 Thăm hỏi, tặng quà hộ gia đình khó khăn")
        st.image("image/thamhoi.jpg", use_container_width =True)


    # --- GALLERY ---
    st.markdown("<div class='section-title'>📸 Một số hình ảnh của Ô Liu</div>", unsafe_allow_html=True)

    image_dir = "static"
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    image_files.sort()

    def img_to_base64(path):
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        ext = os.path.splitext(path)[1].lower().replace('.', '')
        return f"data:image/{ext};base64,{data}"

    images = [img_to_base64(os.path.join(image_dir, f)) for f in image_files]

    slider_html = f"""
    <style>
    .wrapper {{
    width: 100%;
    overflow: hidden;
    background: linear-gradient(to right, var(--background-color), var(--secondary-background-color));
    padding: 30px 0;
    border-radius: 20px;
    box-shadow: inset 0 0 8px rgba(0,0,0,0.05);
    position: relative;
    }}

    .track {{
    display: flex;
    width: max-content;
    animation: moveRight 40s linear infinite;
    }}

    @keyframes moveRight {{
    0%   {{ transform: translateX(-50%); }}
    100% {{ transform: translateX(0%); }}
    }}

    .track img {{
    height: 230px;
    width: auto;
    margin-right: 20px;
    border-radius: 16px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.15);
    transition: transform 0.4s ease;
    flex-shrink: 0;
    background-color: var(--secondary-background-color);
    }}

    .track img:hover {{
    transform: scale(1.05);
    }}
    </style>

    <div class="wrapper">
    <div class="track">
        {''.join([f'<img src="{img}">' for img in images])}
        {''.join([f'<img src="{img}">' for img in images])}
    </div>
    </div>
    """
    st.markdown(slider_html, unsafe_allow_html=True)


    # --- CONTACT / SOCIAL ---
    st.markdown("<div class='section-title'>📬 Thông tin liên hệ</div>", unsafe_allow_html=True)
    st.markdown("""
    <style>
    .contact-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 40px 25px;
        border-radius: 20px;
        background: linear-gradient(135deg, #E6F0FF, #FFFFFF);
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        box-sizing: border-box;
        text-align: center;
    }
    .contact-text {
        font-size: 1.1rem;
        line-height: 1.8;
        color: #002B5B;
        margin-bottom: 30px;
    }
    .social-icons {
        display: flex;
        justify-content: center;
        gap: 25px;
        flex-wrap: wrap;
    }
    .social-card {
        background: #fff;
        border-radius: 16px;
        padding: 15px;
        width: 70px;
        height: 70px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .social-card:hover {
        transform: translateY(-5px) scale(1.1);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    .social-card svg {
        width: 32px;
        height: 32px;
        fill: #002B5B; /* màu chủ đạo */
        transition: fill 0.3s ease;
    }
    .social-card:hover svg {
        fill: #FF8C42; /* màu hover nổi bật */
    }
    </style>

    <div class="contact-container">
        <div class="contact-text">
            <b>Email:</b> tinhnguyenoliu@gmail.com<br>
            <b>Trưởng BTC - Nhật Trình:</b> 0388534146<br>
            <b>Phụ trách gây quỹ - Thảo Trang:</b> 0901367931<br>
            <b><br>
            <div class="social-icons">
                <a href="https://www.facebook.com/oliufanpage" target="_blank" class="social-card"><img src="https://cdn-icons-png.flaticon.com/512/733/733547.png"></a>
                <a href="https://www.tiktok.com/@tinhnguyenoliu" target="_blank" class="social-card"><img src="https://cdn-icons-png.flaticon.com/512/3046/3046122.png"></a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
