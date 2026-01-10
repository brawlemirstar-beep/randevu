import streamlit as st
import sqlite3

st.set_page_config(page_title="Okul Randevu Sistemi", layout="centered", initial_sidebar_state="collapsed")

# CSS: KOYU MOD VE HEADER
st.markdown("""
    <style>
        /* 1. Tüm Tarayıcılar İçin Zorunlu Arka Plan ve Yazı Rengi */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0E1117 !important;
            color: #FFFFFF !important;
        }

        /* 2. Header Alanı */
        .custom-header {
            background-color: #1E232D !important;
            padding: 25px 10px !important;
            border-radius: 15px !important;
            border-bottom: 4px solid #1f77b4 !important;
            text-align: center !important;
            margin-bottom: 30px !important;
        }
        
        /* 3. Giriş Kutuları (Input), Selectbox ve Yazılar */
        input, select, textarea, [data-baseweb="select"] {
            background-color: #262730 !important;
            color: white !important;
            -webkit-text-fill-color: white !important; /* Safari/Chrome için zorunlu */
        }

        /* Yazı etiketlerini (Label) beyaz yap */
        label, p, span, div {
            color: white !important;
        }

        /* 4. Butonları Sabitle */
        .stButton>button {
            background-color: #262730 !important;
            color: white !important;
            border: 1px solid #4A4A4A !important;
            width: 100% !important;
            border-radius: 8px !important;
            font-weight: bold !important;
        }

        .stButton>button:hover {
            border-color: #1f77b4 !important;
            color: #1f77b4 !important;
        }

        /* 5. Streamlit Gereksiz Boşluk ve Menü Gizleme */
        .block-container { padding-top: 2rem !important; }
        [data-testid="stSidebarNav"], [data-testid="collapsedControl"], header {
            display: none !important;
        }
    </style>
    
    <div class="custom-header">
        <h1 style="color: white !important; margin: 0; font-size: 2rem;">🏫 OKUL RANDEVU SİSTEMİ</h1>
    </div>
""", unsafe_allow_html=True)

# VERİTABANI KURULUM
conn = sqlite3.connect('okul_sistemi_final.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS ogrenciler (tc_no TEXT PRIMARY KEY, okul_no TEXT, ad_soyad TEXT, sinif TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS ogretmenler (id INTEGER PRIMARY KEY AUTOINCREMENT, ad_soyad TEXT, kullanici_adi TEXT UNIQUE, sifre TEXT, sinif TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS randevular (id INTEGER PRIMARY KEY AUTOINCREMENT, ogretmen_id INTEGER, tarih TEXT, saat TEXT, durum TEXT, veli_tc TEXT)')
conn.commit()
conn.close()

st.write("### Devam etmek için giriş türünü seçiniz:")
st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("👩‍👦 Veli Girişi"): st.switch_page("pages/1_Veli_Giris.py")
with col2:
    if st.button("👨‍🏫 Öğretmen Paneli"): st.switch_page("pages/2_Ogretmen_Paneli.py")
with col3:
    if st.button("⚙️ Admin Paneli"): st.switch_page("pages/3_Admin_Paneli.py")