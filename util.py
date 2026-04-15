import os, streamlit as st, unicodedata
from dotenv import load_dotenv

load_dotenv()

def get_secret(key):
    return st.secrets.get(key) or os.getenv(key)


def get_gia_hang(data, row_value: int = 3, row_name: int = 4, row_start: int = 14, row_end: int = 34):
    gia_mat_hang = {data[row_name][i]: data[row_value][i] for i in range(row_start, row_end)}
    normalized = {}
    for k, v in gia_mat_hang.items():
        # Normalize key
        key = k.strip().replace('\n', '')

        # Normalize value
        value = int(v.replace(',', '').strip())

        normalized[key] = value
    return normalized

def extract_first_value(data):
    return [row[0] if row else None for row in data]

def normalize_key(text: str) -> str:
    return text.replace("\n", "").strip().upper()

def parse_value(val) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0
    
def get_stock(headers_ton, values_ton):
    headers = extract_first_value(headers_ton)
    values  = extract_first_value(values_ton)
    raw_ton_kho = dict(zip(headers, values))

    stock = {
        normalize_key(k): parse_value(v)
        for k, v in raw_ton_kho.items()
    }
    return stock


def clean_money_column(series):
    return (
        series.astype(str)
        .str.replace(r"[^\d]", "", regex=True)
        .replace("", "0")
        .astype(float)
    )

def convert_name(text: str):
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return ' '.join(text.lower().strip().split())