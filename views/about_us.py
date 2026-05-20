import streamlit as st
import os
import base64
from config import TIEU_DE_HTML, GIOI_THIEU_HTML, SLIDER_HTML_TEMPLATE, SOCIAL_HTML

def img_to_base64(path):
    if not os.path.exists(path): 
        return ""
    with open(path, "rb") as f:
        ext = os.path.splitext(path)[1].lower().replace('.','')
        return f"data:image/{ext};base64,{base64.b64encode(f.read()).decode()}"

def show_about_us():
    st.markdown(TIEU_DE_HTML, unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📝 Ô Liu là...</div>", unsafe_allow_html=True)
    st.markdown(GIOI_THIEU_HTML, unsafe_allow_html=True)
    
    st.markdown("<div class='section-title'>🎯 Hành trình lan tỏa</div>", unsafe_allow_html=True)
    c = st.columns(3)
    with c[0]:
        st.markdown("#### 🎮 Tổ chức ngày hội trò chơi")
        st.image("image/hoichobe.jpg", use_container_width=True)
    with c[1]:
        st.markdown("#### 🎁 Trao quà & học bổng")
        st.image("image/hocbong.jpg", use_container_width=True)
    with c[2]:
        st.markdown("#### 💝 Thăm hỏi hộ khó khăn")
        st.image("image/thamhoi.jpg", use_container_width=True)

    st.markdown("<div class='section-title'>📸 Khoảnh khắc ý nghĩa cùng Ô Liu</div>", unsafe_allow_html=True)
    static_dir = "static"
    if os.path.exists(static_dir):
        images_found = [os.path.join(static_dir, f) for f in os.listdir(static_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        images_found.sort()
        if images_found:
            html_imgs = "".join([f'<img src="{img_to_base64(p)}">' for p in images_found])
            st.markdown(SLIDER_HTML_TEMPLATE.format(images_html=html_imgs), unsafe_allow_html=True)

    st.markdown("<div class='section-title'>📬 Kết nối cùng chúng mình</div>", unsafe_allow_html=True)
    st.markdown(SOCIAL_HTML, unsafe_allow_html=True)