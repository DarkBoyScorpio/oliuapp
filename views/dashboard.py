import streamlit as st
import pandas as pd
import altair as alt
from config import GIA_ROW_NAME, TIEN_BAN_HANG, TARGET_SALES, PROGRESS_BAR_HTML, GIA_ROW_START, GIA_ROW_END
from util import clean_money_column

def custom_progress_bar(ratio):
    percent = int(min(ratio, 1.0) * 100)
    st.markdown(PROGRESS_BAR_HTML.format(percent=percent), unsafe_allow_html=True)

def show_dashboard(gia_mat_hang):
    st.title("📊 Số gì ra, mấy gì ra...")
    data = st.session_state.sheet_data
    
    # Ép kiểu dữ liệu và làm sạch tên cột dính kí tự xuống dòng \n
    df = pd.DataFrame(data[GIA_ROW_NAME+1:], columns=data[GIA_ROW_NAME])
    df.columns = df.columns.str.replace('\n', '', regex=True)
    df[TIEN_BAN_HANG] = clean_money_column(df[TIEN_BAN_HANG])
    df["TÊN TNV BÁN"] = df["TÊN TNV BÁN"].fillna("Chưa xác định")

    # Khối 1: Tiến độ KPIs Mục tiêu doanh thu
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
            if ratio >= 1: st.success("🎉 Về bờ rồi! Xuất sắc quá Ô Liu ơi 🚀")
            elif ratio >= 0.5: st.warning("📈 Đứng ở dưới sale mạnh lên 🔥")
            else: st.info("⚠️ Flop quá cả nhà ơi 😭")
        with col2:
            custom_progress_bar(ratio)
            
    st.markdown("---")

    # Khối 2: Biểu đồ Top 10 TNV bán đỉnh nhất
    with st.container():
        st.markdown("### 🏆 Đại lộ danh vọng")
        top_tnv = df.groupby("TÊN TNV BÁN")[TIEN_BAN_HANG].sum().reset_index().sort_values(by=TIEN_BAN_HANG, ascending=False).head(10)
        
        base = alt.Chart(top_tnv).encode(
            x=alt.X(f"{TIEN_BAN_HANG}:Q", title="Doanh số (VND)"),
            y=alt.Y("TÊN TNV BÁN:N", sort="-x", title="Tên TNV")
        )
        bars = base.mark_bar().encode(
            color=alt.Color(f"{TIEN_BAN_HANG}:Q", scale=alt.Scale(scheme='greenblue'), legend=None),
            tooltip=["TÊN TNV BÁN", alt.Tooltip(TIEN_BAN_HANG, format=",.0f")]
        )
        text = base.mark_text(align='left', baseline='middle', dx=3).encode(text=alt.Text(f"{TIEN_BAN_HANG}:Q", format=",.0f"))
        st.altair_chart((bars + text).properties(height=350), use_container_width=True)

    st.markdown("---")

    # Khối 3: Thống kê chi tiết doanh thu từng mặt hàng cụ thể
    with st.container():
        st.markdown("### 💵 Doanh thu theo mặt hàng")
        product_columns = df.columns[GIA_ROW_START:GIA_ROW_END]
        product_data = df[product_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
        mat_hang_so_luong = product_data.sum().to_dict()
        
        df_doanh_thu = pd.DataFrame([
            {
                "Mặt hàng": ten.strip(),
                "Số lượng": so_luong,
                "Giá bán (VND)": gia_mat_hang.get(ten.strip(), 0),
                "Doanh thu (VND)": so_luong * gia_mat_hang.get(ten.strip(), 0)
            } for ten, so_luong in mat_hang_so_luong.items() if so_luong > 0
        ])
        
        if not df_doanh_thu.empty:
            df_doanh_thu = df_doanh_thu.sort_values(by="Doanh thu (VND)", ascending=False).reset_index(drop=True)
            st.markdown(f"#### **Tổng doanh thu các mặt hàng:** `{df_doanh_thu['Doanh thu (VND)'].sum():,.0f} VND`")
            
            col1, col2 = st.columns([2, 3])
            with col1:
                st.dataframe(df_doanh_thu.style.format({
                    "Giá bán (VND)": "{:,.0f}", "Doanh thu (VND)": "{:,.0f}", "Số lượng": "{:,.0f}"
                }), use_container_width=True)
            with col2:
                chart_revenue = alt.Chart(df_doanh_thu).mark_bar().encode(
                    x=alt.X("Doanh thu (VND):Q"), y=alt.Y("Mặt hàng:N", sort="-x"),
                    color=alt.Color("Doanh thu (VND):Q", scale=alt.Scale(scheme="greens"), legend=None),
                    tooltip=["Mặt hàng", "Số lượng", alt.Tooltip("Doanh thu (VND)", format=",.0f")]
                ).properties(height=350)
                st.altair_chart(chart_revenue, use_container_width=True)
        else:
            st.warning("⚠️ Hệ thống chưa ghi nhận số liệu sản phẩm bán ra thương mại.")