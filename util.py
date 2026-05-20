# util.py
import time
import random
import re
import pandas as pd
import streamlit as st

def get_secret(key_name: str) -> str:
    try:
        return st.secrets[key_name]
    except KeyError:
        import os
        return os.environ.get(key_name, "")

def get_sheet_values(sheet_instance):
    """Đọc dữ liệu bảng tính với cơ chế bảo vệ hàng đợi 3 lần khi dính hạn ngạch mạng."""
    for attempt in range(3):
        try:
            return sheet_instance.get_all_values()
        except Exception as e:
            if "429" in str(e):
                time.sleep(5 + random.random())
            else:
                raise e
    raise Exception("❌ Lỗi Google Sheets: Quá tải hàng đợi yêu cầu (429 Too Many Requests). Vui lòng tải lại trang.")

def get_stock_data(worksheet_instance, name_range: str, value_range: str):
    headers = worksheet_instance.get(name_range)
    values = worksheet_instance.get(value_range)
    return headers, values

def get_stock(headers_ton, values_ton) -> dict:
    stock_dict = {}
    if not headers_ton or not values_ton:
        return stock_dict
    
    # Duyệt qua từng dòng một thay vì chỉ lấy phần tử [0]
    for i in range(min(len(headers_ton), len(values_ton))):
        if headers_ton[i] and values_ton[i]:
            k = headers_ton[i][0]
            v = values_ton[i][0]
            
            if k.strip():
                try:
                    # Làm sạch text và ép kiểu số lượng tồn kho
                    stock_dict[normalize_key(k)] = int(v) if str(v).strip() != "" else 0
                except ValueError:
                    print(ValueError)
                    stock_dict[normalize_key(k)] = 0
                    
    return stock_dict

def get_gia_hang(sheet_raw_data, row_value: int, row_name: int, row_start: int, row_end: int) -> dict:
    """Trích xuất tự động bảng giá bán lẻ của các mặt hàng dựa theo vị trí index dòng cấu hình."""
    price_dict = {}
    if len(sheet_raw_data) <= max(row_value, row_name):
        return price_dict
        
    names = sheet_raw_data[row_name]
    prices = sheet_raw_data[row_value]
    
    for i in range(row_start, min(row_end, len(names))):
        p_name = names[i].strip().replace('\n', '')
        p_val = prices[i].strip().replace('.', '').replace(',', '')
        if p_name:
            try:
                price_dict[p_name] = int(p_val) if p_val != "" else 0
            except ValueError:
                price_dict[p_name] = 0
    return price_dict

def normalize_key(text: str) -> str:
    if not text:
        return ""
    return " ".join(str(text).upper().strip().split())

def clean_money_column(series: pd.Series) -> pd.Series:
    """Làm sạch định dạng dấu chấm ngăn cách tiền tệ VNĐ để tính toán biểu đồ toán học."""
    clean_series = series.astype(str).str.replace('.', '', regex=False).str.replace(',', '', regex=False)
    return pd.to_numeric(clean_series, errors='coerce').fillna(0).astype(int)

def convert_name(vietnamese_str: str) -> str:
    """Hàm convert ký tự Latinh loại bỏ dấu tiếng Việt phục vụ sinh text nội dung VietQR chuẩn mã hóa."""
    if not vietnamese_str:
        return "UNKNOWN"
    
    patterns = {
        '[àáảãạăằắẳẵặâầấẩẫậ]': 'a', '[èéẻẽẹêềếểễệ]': 'e', '[ìíỉĩị]': 'i',
        '[òóỏõọôồốổỗộơờớởỡợ]': 'o', '[ùúủũụưừứửữự]': 'u', '[ỳýỷỹỵ]': 'y', '[đ]': 'd',
        '[ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬ]': 'A', '[ÈÉẺẼẸÊỀẾỂễỆ]': 'E', '[ÌÍỈĨỊ]': 'I',
        '[ÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢ]': 'O', '[ÙÚỦŨỤƯỪỨỬỮỰ]': 'U', '[ỲÝỶỸỴ]': 'Y', '[Đ]': 'D'
    }
    
    output = str(vietnamese_str)
    for regex, replacement in patterns.items():
        output = re.sub(regex, replacement, output)
        
    output = re.sub(r'[^a-zA-Z0-9\s]', '', output)
    return "".join(output.upper().strip().split())