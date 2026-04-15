import pandas as pd
import altair as alt
import streamlit as st
import os, json, base64, requests, gspread
import streamlit.components.v1 as components
from oauth2client.service_account import ServiceAccountCredentials
from config import (
                    product_column_map, thoi_gian_nhan_hang, 
                    TARGET_SALES, SCOPE, STK, TEN_CHU_TK, BIN_BANK, 
                    MEO_HTML, PROGRESS_BAR_HTML, PRINT_HTML, NOTE_HTML,
                    TIEU_DE_HTML, GIOI_THIEU_HTML, SOCIAL_HTML, SLIDER_HTML_TEMPLATE,
                    GIA_ROW_VALUE, GIA_ROW_NAME, GIA_ROW_START, GIA_ROW_END, 
                    SHEET_HANG_TON_NAME, HANG_TON_NAME_START, HANG_TON_NAME_END, HANG_TON_VALUE_START, HANG_TON_VALUE_END,
                    TIEN_BAN_HANG, MENU_TREE, MIT_500G, THAP_CAM_500G, CHUOI_SAY_ME_DUONG_500G, CHUOI_SAY_MOC_500G, KHOAI_TAY_RONG_BIEN_250G, KHOAI_TAY_MAM_250G,
                    KHOAI_MON_TRUNG_CUA_250G, NEP_CHAY_CHA_BONG_150G_X3, NEP_CHAY_CHA_BONG_150G_X5, COM_CHAY_CHA_BONG_200G, 
                    GAO_LUT_RONG_BIEN_200G, BANH_TRANG_MAM, MAT_ONG_500ML, MAT_ONG_1_LIT, MAM_1_LIT, DIEU_RANG_MUOI_200G, DIEU_RANG_MUOI_500G, DIEU_MAM_OT_500G,

                )
from util import (
                    get_gia_hang, get_secret, get_stock,
                    normalize_key, clean_money_column, convert_name
                )

SHARE_URL = get_secret("SHARE_URL")
GSP_CRED = get_secret("GSP_CRED")

st.set_page_config(
    page_title="ÔLiu F18 - Bán hàng",
    page_icon="./oliu.jpg",                
    layout="wide",
    initial_sidebar_state="expanded"
)

menu = st.sidebar.radio("📋 Menu", MENU_TREE)

creds = ServiceAccountCredentials.from_json_keyfile_dict(
            json.loads(base64.b64decode(GSP_CRED).decode("utf-8")), SCOPE
        )
client = gspread.authorize(creds)
sheet = client.open_by_url(SHARE_URL).sheet1

gia_mat_hang = get_gia_hang(sheet.get_all_values(), row_value = GIA_ROW_VALUE, row_name = GIA_ROW_NAME, row_start = GIA_ROW_START, row_end = GIA_ROW_END)

# ===== GET HANG TON WORKSHEET =====
worksheetton = client.open_by_url(SHARE_URL).worksheet(SHEET_HANG_TON_NAME)

# ===== READ HEADER & VALUE =====
headers_ton = worksheetton.get(f"{HANG_TON_NAME_START}:{HANG_TON_NAME_END}")
values_ton  = worksheetton.get(f"{HANG_TON_VALUE_START}:{HANG_TON_VALUE_END}")
stock = get_stock(headers_ton=headers_ton, values_ton=values_ton)

# ===== CHECK DISABLED =====
def is_disabled(product_name: str) -> bool:
    return stock.get(normalize_key(product_name), 0) <= 0


def custom_progress_bar(ratio):
    percent = int(min(ratio, 1.0) * 100)
    progress_bar_html = PROGRESS_BAR_HTML.format(percent=percent)
    st.markdown(progress_bar_html, unsafe_allow_html=True)


def show_dashboard():
    st.title("📊 Số gì ra, mấy gì ra...")

    # Đọc dữ liệu từ Google Sheet (hoặc cache lại để không load nhiều)
    data = sheet.get_all_values()
    df = pd.DataFrame(data[GIA_ROW_NAME+1:], columns=data[GIA_ROW_NAME])
    df.columns = df.columns.str.replace('\n', '', regex=True)

    df[TIEN_BAN_HANG] = clean_money_column(df[TIEN_BAN_HANG])
    df["TÊN TNV BÁN"] = df["TÊN TNV BÁN"].fillna("Chưa xác định")

    ### 🥇 1. Top TNV bán hàng
    with st.container():
        st.markdown("### 🎯 Tổng doanh số và mục tiêu")
        total_sales = df[TIEN_BAN_HANG].sum()
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
                st.success("🎉 Về bờ rồi! 🚀")
            elif ratio >= 0.5:
                st.warning("📈 Đứng ở dưới sale mạnh lên 🔥")
            else:
                st.info("⚠️ Flop quá 😭")

        with col2:
            custom_progress_bar(ratio)

  
    st.markdown("---")

    ### 🏆 VÙNG 2: Top TNV bán hàng

    with st.container():
        st.markdown("### 🏆 Đại lộ danh vọng")

        top_tnv = (
            df.groupby("TÊN TNV BÁN")[TIEN_BAN_HANG]
            .sum().reset_index()
            .rename(columns={TIEN_BAN_HANG: "TIỀN BÁN HÀNG"})
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
        product_columns = df.columns[GIA_ROW_START:GIA_ROW_END]
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
            st.warning("⚠️ Chưa có đồng nào.")


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
        data_qr = res.json()
        qr_url = data_qr['data']['qrDataURL']
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
                mat_ong_500ml = st.number_input("🍯 Mật ong 500ml", min_value=0, step=1, disabled=is_disabled("MẬT ONG 500ML"))
                dieu_muoi_200g = st.number_input("🥜 Điều muối 200g", min_value=0, step=1, disabled=is_disabled("ĐIỀU RANG MUỐI 200G"))
                dieu_mam_ot_500g = st.number_input("🌶️ Điều mắm ớt 500g", min_value=0, step=1, disabled=is_disabled("ĐIỀU MẮM ỚT 500G"))
            with col2:
                mat_ong_1l = st.number_input("🍯 Mật ong 1 lít", min_value=0, step=1, disabled=is_disabled("MẬT ONG 1 LÍT"))
                dieu_muoi_500g = st.number_input("🥜 Điều muối 500g", min_value=0, step=1, disabled=is_disabled("ĐIỀU RANG MUỐI 500G"))
                mam_1l = st.number_input("🥫 Mắm 1 lít", min_value=0, step=1, disabled=is_disabled("MẮM 1 LÍT"))

        # ==== PHẦN 3: Snack - Mít, Chuối, Khoai, Gạo ====
        with st.expander("🍱 Rau củ quả - trái cây sấy", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                mit_500g = st.number_input("🥭 Mít sấy 500g", min_value=0, step=1, disabled=is_disabled("MÍT 500G"))
                thap_cam_500g = st.number_input("🍱 Thập cẩm 500g", min_value=0, step=1, disabled=is_disabled("THẬP CẨM 500G"))
                chuoi_me_duong_500g = st.number_input("🍌 Chuối sấy mè đường 500g", min_value=0, step=1)
                chuoi_500g = st.number_input("🍌 Chuối sấy mộc 500g", min_value=0, step=1, disabled=is_disabled("CHUỐI SẤY MỘC 500G"))
            with col2:
                ktrb_250g = st.number_input("🥔 Khoai tây rong biển 250g", min_value=0, step=1, disabled=is_disabled("KHOAI TÂY RONG BIỂN 250G"))
                ktmam_250g = st.number_input("🥔 Khoai tây mắm 250g", min_value=0, step=1, disabled=is_disabled("KHOAI TÂY MẮM 250G"))
                km_trung_cua_250g = st.number_input("🍠 Khoai môn trứng cua 250g", min_value=0, step=1, disabled=is_disabled("KHOAI MÔN TRỨNG CUA 250G"))

        with st.expander("🍚 Cơm cháy, Bánh tráng mắm", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                nep_chay_3 = st.number_input("🍙 Nếp cháy chà bông x3", min_value=0, step=1, disabled=is_disabled("NẾP CHÁY CHÀ BÔNG 150G"))
                com_chay_200g = st.number_input("🍚 Cơm cháy chà bông 200g", min_value=0, step=1, disabled=is_disabled("CƠM CHÁY CHÀ BÔNG 200G"))
                banh_trang_mam = st.number_input("🥖 Bánh tráng mắm", min_value=0, step=1, disabled=is_disabled("BÁNH TRÁNG MẮM"))
            with col2:
                nep_chay_5 = st.number_input("🍙 Nếp cháy chà bông x5", min_value=0, step=1, disabled=is_disabled("NẾP CHÁY CHÀ BÔNG 150G"))
                gao_lut_rb_200g = st.number_input("🌾 Gạo lứt rong biển 200g", min_value=0, step=1, disabled=is_disabled("GẠO LỨT RONG BIỂN 200G"))
            
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
                for col_idx in range(1, 39):
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
                df = pd.DataFrame(data[GIA_ROW_NAME+1:], columns=data[GIA_ROW_NAME])
                df.columns = df.columns.str.replace('\n', '', regex=True)
                df = df.loc[:, ~df.columns.duplicated()]
                df_filtered = df[df["STT"] == str(stt_don_hang_moi)]
                row_data = df_filtered.iloc[0].to_dict()
                filtered_data = {k: v for k, v in row_data.items() if str(v).strip() not in ["", "None", "nan"]}
                amount = int(filtered_data['TỔNG TIỀNCẦN TRẢ(1)+(2)'].replace('.', ''))
                ten_tnv_ban = convert_name(filtered_data['TÊN TNV BÁN'])
                ndck = f"BANHANGF18 DON{str(stt_don_hang_moi)} {ten_tnv_ban}"

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
                    data_qr = res.json()
                    qr_url = data_qr['data']['qrDataURL']
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
                    MIT_500G: mit_500g,
                    THAP_CAM_500G: thap_cam_500g,
                    CHUOI_SAY_ME_DUONG_500G: chuoi_me_duong_500g,
                    CHUOI_SAY_MOC_500G: chuoi_500g,
                    KHOAI_TAY_RONG_BIEN_250G: ktrb_250g,
                    KHOAI_TAY_MAM_250G: ktmam_250g,
                    KHOAI_MON_TRUNG_CUA_250G: km_trung_cua_250g,
                    NEP_CHAY_CHA_BONG_150G_X3: nep_chay_3,
                    NEP_CHAY_CHA_BONG_150G_X5: nep_chay_5,
                    COM_CHAY_CHA_BONG_200G: com_chay_200g,
                    GAO_LUT_RONG_BIEN_200G: gao_lut_rb_200g,
                    BANH_TRANG_MAM: banh_trang_mam,
                    MAT_ONG_500ML: mat_ong_500ml,
                    MAT_ONG_1_LIT: mat_ong_1l,
                    MAM_1_LIT: mam_1l,
                    DIEU_RANG_MUOI_200G: dieu_muoi_200g,
                    DIEU_RANG_MUOI_500G: dieu_muoi_500g,
                    DIEU_MAM_OT_500G: dieu_mam_ot_500g
                }

            # 👉 Lọc các mặt hàng có số lượng > 0
            mat_hang_co_mua = {k: v for k, v in mat_hang.items() if v > 0}

            row = [""] * 38

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


elif menu == "📄 Tra cứu đơn hàng":
    components.html(MEO_HTML, height=80)
    st.title("📄 Xem đơn hàng của bạn")
    data = sheet.get_all_values()
    df = pd.DataFrame(data[GIA_ROW_NAME+1:], columns=data[GIA_ROW_NAME])
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
                    ndck = f"BANHANGF18 DON{str(stt_input)} {ten_tnv_ban}"
                    show_qr_thanh_toan(amount, ndck)
                
                df_khach_hang = pd.DataFrame(list(thong_tin_dat_hang.items()), columns=["Thông tin", "Giá trị"])
                df_khach_hang.loc[df_khach_hang["Thông tin"] == "CHI TIẾT ĐƠN (VUI LÒNG ĐIỀN CHÍNH XÁC VỚI Ô CỘT SỐ LƯỢNG BÊN PHẢI)", "Thông tin"] = "CHI TIẾT ĐƠN"
                df_khach_hang.loc[df_khach_hang["Thông tin"] == "TỔNG TIỀNCẦN TRẢ(1)+(2)", "Thông tin"] = "TỔNG TIỀN CẦN TRẢ"
                df_khach_hang.loc[df_khach_hang["Thông tin"] == TIEN_BAN_HANG, "Thông tin"] = "TIỀN HÀNG"
                df_khach_hang.loc[df_khach_hang["Thông tin"] == "Đã thanh toán", "Thông tin"] = "ĐÃ THANH TOÁN"
                df_khach_hang.loc[df_khach_hang["Thông tin"] == "ĐÃ GIAO TNV(TNV điền hoặc người giao điền)", "Thông tin"] = "ĐÃ GIAO TNV"
                
                df_khach_hang.loc[df_khach_hang["Thông tin"] == "TỔNG TIỀN CẦN TRẢ", "Giá trị"] = df_khach_hang.loc[
                                                                                                df_khach_hang["Thông tin"] == "TỔNG TIỀN CẦN TRẢ", "Giá trị"
                                                                                            ].map(lambda x: f"{int(x):,}".replace(",", "."))
                df_khach_hang.loc[df_khach_hang["Thông tin"] == "TIỀN HÀNG", "Giá trị"] = df_khach_hang.loc[
                                                                                df_khach_hang["Thông tin"] == "TIỀN HÀNG", "Giá trị"
                                                                            ].map(lambda x: f"{int(x):,}".replace(",", "."))

                df_mon_hang = pd.DataFrame(list(mon_hang_da_mua.items()), columns=["Sản phẩm", "Số lượng"])
                
                df_khach_hang_in = df_khach_hang[df_khach_hang["Thông tin"] != "Đã thanh toán"]
                df_khach_hang_in = df_khach_hang_in[df_khach_hang_in["Thông tin"] != "ĐÃ SOẠN ĐƠN"]
                df_khach_hang_in = df_khach_hang_in[df_khach_hang_in["Thông tin"] != "ĐÃ GIAO TNV(TNV điền hoặc người giao điền)"]
                
                with col2:
                    html_code = PRINT_HTML.format(
                        customer_table=df_khach_hang_in.to_html(index=False, border=1),
                        order_table=df_mon_hang.to_html(index=False, border=1)
                    )
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

    st.markdown(NOTE_HTML,
                unsafe_allow_html=True
            )
    embed_url = SHARE_URL.replace("/edit", "/preview")
    components.iframe(embed_url, height=600, scrolling=True)


elif menu == "📊 Con số biết nói":
    components.html(MEO_HTML, height=80)
    show_dashboard()


elif menu == "👉 Về chúng tôi":
    st.markdown(TIEU_DE_HTML, unsafe_allow_html=True)


    # --- ABOUT US ---
    st.markdown("<div class='section-title'>📝 Ô Liu là...</div>", unsafe_allow_html=True)
    st.markdown(GIOI_THIEU_HTML, unsafe_allow_html=True)

    # --- MISSION & ACTIVITIES ---
    st.markdown("<div class='section-title'>🎯 Hành trình lan tỏa</div>", unsafe_allow_html=True)
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
    st.markdown("<div class='section-title'>📸 Khoảnh khắc ý nghĩa cùng Ô Liu</div>", unsafe_allow_html=True)

    image_dir = "static"
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    image_files.sort()

    def img_to_base64(path):
        with open(path, "rb") as f:
            data_img = base64.b64encode(f.read()).decode()
        ext = os.path.splitext(path)[1].lower().replace('.', '')
        return f"data:image/{ext};base64,{data_img}"

    images = [img_to_base64(os.path.join(image_dir, f)) for f in image_files]
    images_html = ''.join([f'<img src="{img}">' for img in images])
    slider_html = SLIDER_HTML_TEMPLATE.format(images_html=images_html)
    st.markdown(slider_html, unsafe_allow_html=True)

    # --- CONTACT / SOCIAL ---
    st.markdown("<div class='section-title'>📬 Kết nối cùng chúng mình</div>", unsafe_allow_html=True)
    st.markdown(SOCIAL_HTML, unsafe_allow_html=True)