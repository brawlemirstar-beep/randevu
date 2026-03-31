import streamlit as st
import sqlite3

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Okul Randevu Sistemi", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- KOYU TEMA VE MOBİL UYUMLU CSS ---
st.markdown("""
    <style>
        /* Arka plan ve yazı renkleri */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #0E1117 !important;
        }
        
        h1, h2, h3, h4, h5, h6, p, span, label {
            color: #FFFFFF !important;
        }

        /* Giriş butonları tasarımı */
        .stButton>button {
            background-color: #262730 !important;
            color: #FFFFFF !important;
            border: 1px solid #4A4A4A !important;
            width: 100% !important;
            height: 100px !important; /* Butonları büyük ve kolay tıklanır yap */
            border-radius: 12px !important;
            font-size: 18px !important;
            font-weight: bold !important;
            margin-bottom: 10px !important;
            transition: 0.3s;
        }

        .stButton>button:hover {
            border-color: #1f77b4 !important;
            color: #1f77b4 !important;
            transform: scale(1.02);
        }

        /* Streamlit gereksiz barları gizle */
        header, [data-testid="stToolbar"] {
            display: none !important;
        }
        
        .main-title {
            text-align: center;
            padding: 20px;
            background: linear-gradient(90deg, #1f77b4, #00d4ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 40px;
            font-weight: 800;
        }
    </style>
""", unsafe_allow_html=True)

# --- VERİTABANI BAŞLATMA ---
def init_db():
    conn = sqlite3.connect('okul_sistemi_final.db')
    c = conn.cursor()
    # Öğrenci Tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS ogrenciler 
                 (tc_no TEXT PRIMARY KEY, okul_no TEXT, ad_soyad TEXT, sinif TEXT)''')
    # Öğretmen Tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS ogretmenler 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, ad_soyad TEXT, kullanici_adi TEXT UNIQUE, sifre TEXT, sinif TEXT)''')
    # Randevu Tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS randevular 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, ogretmen_id INTEGER, tarih TEXT, saat TEXT, durum TEXT, veli_tc TEXT)''')
    # Admin Tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS sistem_adminleri 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, k_adi TEXT UNIQUE, sifre TEXT)''')
    
    # Başlangıç için örnek bir admin ekle (Eğer tablo boşsa)
    c.execute("SELECT count(*) FROM sistem_adminleri")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO sistem_adminleri (k_adi, sifre) VALUES ('admin', '1234')")
        
    conn.commit()
    conn.close()

init_db()

# --- ANA EKRAN ---
st.markdown('<p class="main-title">OKUL RANDEVU SİSTEMİ</p>', unsafe_allow_html=True)
st.write("---")
st.write("### Lütfen giriş türünü seçiniz:")

# Giriş Seçenekleri
col1, col2 = st.columns(2)

with col1:
    if st.button("👪\nVELİ GİRİŞİ", use_container_width=True):
        st.switch_page("pages/1_Veli_Giris.py")

with col2:
    if st.button("👨‍🏫\nÖĞRETMEN PANELİ", use_container_width=True):
        st.switch_page("pages/2_Ogretmen_Paneli.py")

st.write("") # Boşluk

if st.button("⚙️ SİSTEM YÖNETİMİ (ADMİN)", use_container_width=True):
    st.switch_page("pages/3_Admin_Paneli.py")

# Alt Bilgi
st.markdown("<br><br><p style='text-align: center; color: #555 !important;'>© 2026 Okul Randevu Yönetim Sistemi</p>", unsafe_allow_html=True)