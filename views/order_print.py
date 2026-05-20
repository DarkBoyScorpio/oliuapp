import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from config import GIA_ROW_NAME, PRINT_MULTI_HTML

def compile_print_jobs(dataframe, stt_list, price_catalog):
    sub_set = dataframe[pd.to_numeric(dataframe["STT"], errors="coerce").isin(stt_list)]
    if sub_set.empty:
        st.warning("Không tìm thấy dữ liệu trùng khớp để in.")
        return
    
    html_accumulation = ""
    for _, matrix_row in sub_set.iterrows():
        r_data = {k: v for k, v in matrix_row.to_dict().items() if str(v).strip() not in ["", "None", "nan"]}
        info_bucket, product_bucket = {}, {}
        
        for k, v in r_data.items():
            if k.strip() in price_catalog and float(v) > 0: 
                product_bucket[k] = v
            else: 
                info_bucket[k] = v
            
        df_customer = pd.DataFrame(list(info_bucket.items()), columns=["Mục", "Nội dung"])
        df_items = pd.DataFrame(list(product_bucket.items()), columns=["Sản phẩm", "Số lượng"])
        
        # Áp dụng chính xác logic map tên và format tiền tệ giống hệt tab Tra Cứu của bạn
        df_customer.loc[df_customer["Mục"] == "CHI TIẾT ĐƠN (VUI LÒNG ĐIỀN CHÍNH XÁC VỚI Ô CỘT SỐ LƯỢNG BÊN PHẢI)", "Mục"] = "CHI TIẾT ĐƠN"
        df_customer.loc[df_customer["Mục"] == "TỔNG TIỀNCẦN TRẢ(1)+(2)", "Mục"] = "TỔNG TIỀN CẦN TRẢ"
        df_customer.loc[df_customer["Mục"] == "TIỀN HÀNG BÁN ĐƯỢC", "Mục"] = "TIỀN HÀNG" # Đồng bộ theo TIEN_BAN_HANG
        
        # Định dạng tiền tệ có dấu chấm phân cách kiểu Việt Nam
        for target_col in ["TỔNG TIỀN CẦN TRẢ", "TIỀN HÀNG"]:
            df_customer.loc[df_customer["Mục"] == target_col, "Nội dung"] = df_customer.loc[
                df_customer["Mục"] == target_col, "Nội dung"
            ].map(lambda x: f"{int(str(x).replace('.', '').replace(',', '')):,}".replace(",", "."))

        # Lọc bỏ bớt các trường cồng kềnh khi in hóa đơn giấy bọc hàng
        df_customer = df_customer[~df_customer["Mục"].isin(["Đã thanh toán", "ĐÃ SOẠN ĐƠN", "ĐÃ GIAO TNV(TNV điền hoặc người giao điền)"])]
        
        block_html = f"""
        <div class="order" style="page-break-after: always; border-bottom: 2px dashed #000; padding-bottom: 15px; margin-bottom: 25px;">
            <h3 style="text-align:center; font-family: sans-serif;">📄 Đơn hàng STT: {r_data.get("STT")}</h3>
            {df_customer.to_html(index=False, border=1)}
            <br>
            {df_items.to_html(index=False, border=1)}
        </div>
        """
        html_accumulation += block_html

    components.html(PRINT_MULTI_HTML.format(all_orders_html=html_accumulation), height=1)

def show_order_print(gia_mat_hang):
    st.title("🖨️ In hóa đơn hàng loạt")
    df_p = pd.DataFrame(st.session_state.sheet_data[GIA_ROW_NAME+1:], columns=st.session_state.sheet_data[GIA_ROW_NAME])
    df_p.columns = df_p.columns.str.replace('\n', '', regex=True)
    df_p = df_p.loc[:, ~df_p.columns.duplicated()]

    all_ids = df_p["STT"].dropna().unique().tolist()
    unprepared_ids = pd.to_numeric(df_p[df_p["ĐÃ SOẠN ĐƠN"] == "FALSE"]["STT"], errors="coerce").dropna().astype(int).unique().tolist()

    col1, col2 = st.columns(2)
    with col1:
        with st.form("unprepared_form"):
            st.info(f"Tổng số đơn hàng chưa soạn trên hệ thống: **{len(unprepared_ids)}**")
            if st.form_submit_button("In tất cả đơn chưa soạn", type="primary"):
                compile_print_jobs(df_p, unprepared_ids, gia_mat_hang)

    with col2:
        with st.form("selective_form"):
            picked_stt = st.multiselect("🔢 Chọn thủ công STT các đơn hàng cần in:", options=all_ids)
            if st.form_submit_button("In đơn hàng"):
                compile_print_jobs(df_p, [int(x) for x in picked_stt], gia_mat_hang)