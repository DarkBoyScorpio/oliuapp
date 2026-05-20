import gspread
import streamlit as st
import pandas as pd
import requests
import math
from config import (
    thoi_gian_nhan_hang, STK, TEN_CHU_TK, BIN_BANK, product_column_map, GIA_ROW_NAME,
    MIT_500G, THAP_CAM_500G, CHUOI_SAY_ME_DUONG_500G, CHUOI_SAY_MOC_500G,
    KHOAI_TAY_RONG_BIEN_250G, KHOAI_TAY_MAM_250G, KHOAI_MON_TRUNG_CUA_250G,
    NEP_CHAY_CHA_BONG_150G_X3, NEP_CHAY_CHA_BONG_150G_X5, COM_CHAY_CHA_BONG_200G,
    GAO_LUT_RONG_BIEN_200G, BANH_TRANG_MAM, MAT_ONG_500ML, MAT_ONG_1_LIT,
    MAM_1_LIT, DIEU_RANG_MUOI_200G, DIEU_RANG_MUOI_500G, DIEU_MAM_OT_500G
)
from util import normalize_key, convert_name, get_sheet_values

def generate_vietqr_html(amount, code_label):
    res = requests.post("https://api.vietqr.io/v2/generate", json={
        "accountNo": STK, "accountName": TEN_CHU_TK, "acqId": BIN_BANK,
        "amount": amount, "addInfo": code_label, "template": "compact2"
    })
    qr_url = res.json().get('data', {}).get('qrDataURL', '')
    return f"""
    <div style='text-align:center;'>
        <img src="{qr_url}" style="max-width:50%; height:auto; border-radius:10px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);" />
        <p style='margin-top:8px;'><em>📱 Mở App ngân hàng bất kỳ để quét mã chuyển khoản</em></p>
    </div>
    """

def show_order_entry(sheet, stock_data):
    st.title("📦 Nhập đơn hàng")
    
    col1, col2 = st.columns(2)
    with col1: st.markdown("Vui lòng điền các thông tin bên dưới. Sau đó ấn 'Xác nhận & Gửi đơn'")
    with col2: st.markdown('<div style="font-size:14px; text-align:right;">📍 Điểm lấy hàng: Chung Cư Bình Minh, Quận 2 — <a href="https://maps.app.goo.gl/ggeuzpja9fodBJNz9" target="_blank">Google Map</a></div>', unsafe_allow_html=True)

    def check_stock(prod): 
        return max(0, stock_data.get(normalize_key(prod), 0))

    if "don_hang_moi" not in st.session_state:
        st.session_state["don_hang_moi"] = None

    with st.form("form_nhap_don"):
        with st.expander("ℹ️ Thông tin khách hàng", expanded=True):
            c1, c2 = st.columns(2)
            ten_tnv = c1.text_input("👤 Tên TNV bán *")
            sdt = c1.text_input("📞 SĐT khách")
            quan_tinh = c1.text_input("🗺️ Quận/Tỉnh")
            ten_khach = c2.text_input("👥 Tên khách *")
            dia_chi = c2.text_input("🏠 Địa chỉ (nếu ship)")
            thoi_gian_nhan = c2.selectbox("🕓 Thời gian nhận hàng", thoi_gian_nhan_hang)
            chi_tiet_don = st.text_area("📋 Chi tiết đơn hàng*")

        with st.expander("🍯 Mật ong, Mắm, Điều", expanded=False):
            c1, c2 = st.columns(2)
            mo_500 = c1.number_input("🍯 Mật ong 500ml", min_value=0, max_value=check_stock("MẬT ONG 500ML"), step=1)
            d_200 = c1.number_input("🥜 Điều muối 200g", min_value=0, max_value=check_stock("ĐIỀU RANG MUỐI 200G"), step=1)
            d_mam = c1.number_input("🌶️ Điều mắm ớt 500g", min_value=0, max_value=check_stock("ĐIỀU MẮM ỚT 500G"), step=1)
            mo_1l = c2.number_input("🍯 Mật ong 1 lít", min_value=0, max_value=check_stock("MẬT ONG 1 LÍT"), step=1)
            d_500 = c2.number_input("🥜 Điều muối 500g", min_value=0, max_value=check_stock("ĐIỀU RANG MUỐI 500G"), step=1)
            mam = c2.number_input("🥫 Mắm 1 lít", min_value=0, max_value=check_stock("MẮM 1 LÍT"), step=1)

        with st.expander("🍱 Rau củ quả - trái cây sấy", expanded=False):
            c1, c2 = st.columns(2)
            mit = c1.number_input("🥭 Mít sấy 500g", min_value=0, max_value=check_stock("MÍT 500G"), step=1)
            tc = c1.number_input("🍱 Thập cẩm 500g", min_value=0, max_value=check_stock("THẬP CẨM 500G"), step=1)
            c_me = c1.number_input("🍌 Chuối sấy mè đường 500g", min_value=0, max_value=check_stock("CHUỐI SẤY MÈ ĐƯỜNG 500G"), step=1)
            c_moc = c1.number_input("🍌 Chuối sấy mộc 500g", min_value=0, max_value=check_stock("CHUỐI SẤY MỘC 500G"), step=1)
            kt_rb = c2.number_input("🥔 Khoai tây rong biển 250g", min_value=0, max_value=check_stock("KHOAI TÂY RONG BIỂN 250G"), step=1)
            kt_mam = c2.number_input("🥔 Khoai tây mắm 250g", min_value=0, max_value=check_stock("KHOAI TÂY MẮM 250G"), step=1)
            km_trung = c2.number_input("🍠 Khoai môn trứng cua 250g", min_value=0, max_value=check_stock("KHOAI MÔN TRỨNG CUA 250G"), step=1)

        with st.expander("🍚 Cơm cháy, Bánh tráng mắm", expanded=False):
            c1, c2 = st.columns(2)
            nc_3 = c1.number_input("🍙 Nếp cháy chà bông x3", min_value=0, max_value=math.floor(check_stock("NẾP CHÁY CHÀ BÔNG 150G")/3), step=1)
            cc_200 = c1.number_input("🍚 Cơm cháy chà bông 200g", min_value=0, max_value=check_stock("CƠM CHÁY CHÀ BÔNG 200G"), step=1)
            bt_mam = c1.number_input("🥖 Bánh tráng mắm", min_value=0, max_value=check_stock("BÁNH TRÁNG MẮM"), step=1)
            nc_5 = c2.number_input("🍙 Nếp cháy chà bông x5", min_value=0, max_value=math.floor(check_stock("NẾP CHÁY CHÀ BÔNG 150G")/5), step=1)
            gl_rb = c2.number_input("🌾 Gạo lứt rong biển 200g", min_value=0, max_value=check_stock("GẠO LỨT RONG BIỂN 200G"), step=1)

        submitted = st.form_submit_button("🚀 Xác nhận & Gửi đơn", type="primary")

    @st.dialog(title="🧾 Xác nhận đơn hàng", width="large")
    def review_dialog(summary_info, items_purchased, complete_row):
        st.subheader("📌 Thông tin khách hàng")
        st.table(pd.DataFrame(list(summary_info.items()), columns=["Mục", "Dữ liệu"]))
        st.subheader("🛒 Giỏ hàng")
        if items_purchased:
            st.table(pd.DataFrame(list(items_purchased.items()), columns=["Mặt hàng", "Số lượng"]))
        else:
            st.error("Giỏ hàng của bạn đang trống!")

        if st.button("📩 Gửi đơn", disabled=not items_purchased):
            with st.spinner("⏳ Đang ghi dữ liệu..."):
                # 1. Tìm dòng trống đầu tiên dựa vào cột B (Tên TNV bán)
                all_tnv_values = sheet.col_values(2)  
                next_row_index = len(all_tnv_values) + 1
                
                # 2. Tính toán số STT tiếp theo
                all_stt = sheet.col_values(1)[4:]  
                valid_stt = [int(x) for x in all_stt if str(x).isdigit()]
                next_stt = max(valid_stt) + 1 if valid_stt else 1
                
                # Gán STT vào vị trí đầu tiên
                complete_row[0] = next_stt
                
                # 3. Chuẩn bị danh sách các ô cần cập nhật (Bỏ qua ô trống hoặc ô công thức)
                # Kỹ thuật batch_update giúp đẩy nhiều ô lên cùng 1 lúc mà không làm mất công thức các ô còn lại
                update_data = []
                
                for col_idx, value in enumerate(complete_row, start=1):
                    # Chỉ cập nhật ô nếu giá trị không rỗng và không phải bằng 0 (đối với số lượng hàng)
                    if value != "" and value != 0:
                        # Chuyển đổi chỉ số cột số thành ký tự cột chữ (Ví dụ: 1 -> A, 2 -> B...)
                        col_letter = gspread.utils.rowcol_to_a1(1, col_idx).replace("1", "")
                        
                        update_data.append({
                            'range': f"{col_letter}{next_row_index}",
                            'values': [[value]]
                        })
                
                # 4. Gửi lệnh cập nhật hàng loạt lên Google Sheets
                if update_data:
                    sheet.batch_update(update_data, value_input_option="USER_ENTERED")
                
                st.toast(f"✅ Đơn hàng số {next_stt} đã được ghi thành công!")
                st.session_state["don_hang_moi"] = next_stt
                st.session_state.sheet_data = get_sheet_values(sheet)
                st.rerun()

    if submitted:
        if not ten_tnv.strip() or not ten_khach.strip() or not chi_tiet_don.strip():
            st.warning("⚠️ Hãy nhập đầy đủ các thông tin bắt buộc có dấu (*)")
        else:
            summary = {"Tên TNV bán": ten_tnv, "Tên khách": ten_khach, "SĐT khách": sdt, "Địa chỉ": dia_chi, "Quận/Tỉnh": quan_tinh, "Thời gian nhận hàng": str(thoi_gian_nhan), "Chi tiết đơn": chi_tiet_don}
            mapping_items = {
                MIT_500G: mit, THAP_CAM_500G: tc, CHUOI_SAY_ME_DUONG_500G: c_me, CHUOI_SAY_MOC_500G: c_moc,
                KHOAI_TAY_RONG_BIEN_250G: kt_rb, KHOAI_TAY_MAM_250G: kt_mam, KHOAI_MON_TRUNG_CUA_250G: km_trung,
                NEP_CHAY_CHA_BONG_150G_X3: nc_3, NEP_CHAY_CHA_BONG_150G_X5: nc_5, COM_CHAY_CHA_BONG_200G: cc_200,
                GAO_LUT_RONG_BIEN_200G: gl_rb, BANH_TRANG_MAM: bt_mam, MAT_ONG_500ML: mo_500, MAT_ONG_1_LIT: mo_1l,
                MAM_1_LIT: mam, DIEU_RANG_MUOI_200G: d_200, DIEU_RANG_MUOI_500G: d_500, DIEU_MAM_OT_500G: d_mam
            }
            purchased = {k: v for k, v in mapping_items.items() if v > 0}
            
            raw_row = [""] * 38
            raw_row[1], raw_row[2], raw_row[3], raw_row[4], raw_row[5], raw_row[6], raw_row[7] = ten_tnv, ten_khach, chi_tiet_don, sdt, dia_chi, quan_tinh, str(thoi_gian_nhan)
            for k, v in purchased.items():
                raw_row[product_column_map[k] - 1] = v
                
            review_dialog(summary, purchased, raw_row)

    if st.session_state["don_hang_moi"]:
        last_id = st.session_state["don_hang_moi"]
        if st.button("💳 Bấm vào đây để tạo mã QR thanh toán", type="primary"):
            df_sync = pd.DataFrame(st.session_state.sheet_data[GIA_ROW_NAME+1:], columns=st.session_state.sheet_data[GIA_ROW_NAME])
            df_sync.columns = df_sync.columns.str.replace('\n', '', regex=True)
            matched_row = df_sync[df_sync["STT"] == str(last_id)].iloc[0].to_dict()
            
            amount = int(matched_row['TỔNG TIỀNCẦN TRẢ(1)+(2)'].replace('.', ''))
            content_qr = f"BANHANGF18 DON{last_id} {convert_name(matched_row['TÊN TNV BÁN'])}"
            
            with st.expander("📢 Vui lòng kiểm tra kĩ thông tin chuyển khoản trước khi chuyển tiền", expanded=True):
                st.write(f"**Số tài khoản:** `{STK}` | **Tên người nhận:** `{TEN_CHU_TK}` | **Số tiền:** `{amount:,.0f} VND` | **Nội dung:** `{content_qr}` ")
                st.markdown(generate_vietqr_html(amount, content_qr), unsafe_allow_html=True)
            st.session_state["don_hang_moi"] = None