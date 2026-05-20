import time
import random
import json
import base64
import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

from config import (
    SCOPE, MENU_TREE, 
    SHEET_HANG_TON_NAME, HANG_TON_NAME_START, HANG_TON_NAME_END,
    HANG_TON_VALUE_START, HANG_TON_VALUE_END, GIA_ROW_VALUE, 
    GIA_ROW_NAME, GIA_ROW_START, GIA_ROW_END, MEO_HTML
)
import streamlit.components.v1 as components
from util import get_secret, get_sheet_values, get_stock_data, get_stock, get_gia_hang

SHARE_URL = get_secret("SHARE_URL")
GSP_CRED = get_secret("GSP_CRED")

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="ÔLiu F18 - Bán hàng", 
    page_icon="./oliu.jpg", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- QUẢN LÝ CACHE TOÀN HỆ THỐNG ---
@st.cache_resource
def get_gspread_client(credentials_b64, scope):
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(base64.b64decode(credentials_b64).decode("utf-8")), scope
    )
    return gspread.authorize(creds)

@st.cache_resource
def get_spreadsheet_instance(_client, url):
    return _client.open_by_url(url)

# --- KHỞI TẠO ĐỐI TƯỢNG KẾT NỐI ---
client = get_gspread_client(GSP_CRED, SCOPE)
spreadsheet = get_spreadsheet_instance(client, SHARE_URL)
sheet = spreadsheet.sheet1
worksheetton = spreadsheet.worksheet(SHEET_HANG_TON_NAME)

# --- ĐỒNG BỘ DATA ĐẦU VÀO VÀO SESSION STATE ---
if "sheet_data" not in st.session_state:
    st.session_state.sheet_data = get_sheet_values(sheet)

# Tải trước danh mục giá & kho hàng để truyền xuống các View con
gia_mat_hang = get_gia_hang(st.session_state.sheet_data, row_value=GIA_ROW_VALUE, row_name=GIA_ROW_NAME, row_start=GIA_ROW_START, row_end=GIA_ROW_END)
headers_ton, values_ton = get_stock_data(worksheetton, f"{HANG_TON_NAME_START}:{HANG_TON_NAME_END}", f"{HANG_TON_VALUE_START}:{HANG_TON_VALUE_END}")
stock_data = get_stock(headers_ton=headers_ton, values_ton=values_ton)

# --- THANH DIỀU HƯỚNG SIDEBAR ---
menu = st.sidebar.radio("📋 Menu", MENU_TREE)

# Banner trang trí mặc định (Ẩn tại tab giới thiệu)
if menu != "👉 Về chúng tôi":
    components.html(MEO_HTML, height=80)

# --- BỘ ĐIỀU HƯỚNG ROUTER CHUYỂN TRANG DYNAMIC ---
if menu == "📊 Con số biết nói":
    from views.dashboard import show_dashboard
    show_dashboard(gia_mat_hang)

elif menu == "📥 Nhập đơn hàng":
    from views.order_entry import show_order_entry
    show_order_entry(sheet, stock_data)

elif menu == "📄 Tra cứu đơn hàng":
    from views.order_lookup import show_order_lookup
    show_order_lookup(gia_mat_hang)

elif menu == "🖨️ In đơn hàng":
    from views.order_print import show_order_print
    show_order_print(gia_mat_hang)

elif menu == "👉 Về chúng tôi":
    from views.about_us import show_about_us
    show_about_us()