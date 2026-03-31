import streamlit as st
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Veli Portalı", layout="wide", initial_sidebar_state="collapsed")

# --- TARİH FORMATLAMA FONKSİYONU ---
def turkce_tarih_formatla(tarih_str):
    gunler_tr = {
        'Monday': 'Pazartesi', 'Tuesday': 'Salı', 'Wednesday': 'Çarşamba',
        'Thursday': 'Perşembe', 'Friday': 'Cuma', 'Saturday': 'Cumartesi', 'Sunday': 'Pazar'
    }
    tarih_obj = datetime.strptime(tarih_str, '%Y-%m-%d')
    ing_gun = tarih_obj.strftime('%A')
    tr_gun = gunler_tr.get(ing_gun, ing_gun)
    return tarih_obj.strftime(f'%d.%m.%Y {tr_gun}')

# --- CSS VE MOBİL TASARIM ---
st.markdown("""
    <meta name="color-scheme" content="dark only">
    <style>
        /* GENEL RENK SABİTLEME */
        .stApp { background-color: #0E1117 !important; }
        h1, h2, h3, span, label, p, .stMarkdown { color: white !important; }
        
        /* GİRİŞ KUTULARI (Telefonda görünürlük için beyaz arka plan) */
        input { 
            background-color: white !important; 
            color: black !important; 
            -webkit-text-fill-color: black !important;
        }

        .custom-header {
            background-color: #1E232D; padding: 25px; border-radius: 20px;
            border-bottom: 4px solid #28a745; text-align: center; margin-bottom: 30px;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid #30363D !important;
            border-radius: 15px !important;
            background-color: #161B22 !important;
            padding: 20px !important;
            margin-bottom: 25px !important;
        }

        .day-label {
            background-color: #1f77b4; color: white !important;
            padding: 8px 15px; border-radius: 8px; font-weight: bold;
            font-size: 1.1rem; margin-bottom: 15px; display: inline-block;
        }

        /* MOBİLDE BUTONLARI YAN YANA 3'LÜ DİZ */
        @media (max-width: 640px) {
            div[data-testid="stHorizontalBlock"] {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: wrap !important;
                gap: 5px !important;
                justify-content: flex-start !important;
            }
            div[data-testid="stHorizontalBlock"] > div {
                width: 31% !important;
                min-width: 31% !important;
                flex: 1 1 31% !important;
            }
            .stButton button {
                width: 100% !important;
                font-size: 12px !important;
                padding: 5px 2px !important;
            }
        }

        /* BUTON RENKLERİ */
        .stButton button { transition: 0.3s; font-weight: bold !important; border-radius: 8px !important; }
        
        /* Yeşil (Boş) */
        button:contains("🟢") { background-color: #0E2A1B !important; color: #2ECC71 !important; border: 1px solid #2ECC71 !important; }
        /* Mavi (Senin) */
        button:contains("🔵") { background-color: #1B263B !important; color: #3498DB !important; border: 1px solid #3498DB !important; }
        /* Kırmızı (Dolu) */
        button:contains("🔴") { background-color: #2D1B1E !important; color: #E74C3C !important; border: 1px solid #E74C3C !important; }

        [data-testid="stSidebarNav"], header { display: none !important; }
    </style>
    
    <div class="custom-header">
        <h1 style="color: white !important; margin: 0;">👩‍👦 VELİ RANDEVU SİSTEMİ</h1>
    </div>
""", unsafe_allow_html=True)

if st.button("⬅️ Ana Menüye Dön"): st.switch_page("app.py")

if 'veli_giris_yapildi' not in st.session_state:
    st.session_state.veli_giris_yapildi = False

if not st.session_state.veli_giris_yapildi:
    with st.container(border=True):
        st.subheader("🔑 Veli Girişi")
        v_tc = st.text_input("Öğrenci Okul No")
        v_no = st.text_input("Şifre")
        if st.button("Giriş Yap", use_container_width=True):
            conn = sqlite3.connect('okul_sistemi_final.db')
            ogr = conn.execute("SELECT ad_soyad, sinif FROM ogrenciler WHERE tc_no=? AND okul_no=?", (v_tc, v_no)).fetchone()
            conn.close()
            if ogr:
                st.session_state.veli_giris_yapildi = True
                st.session_state.veli_ad, st.session_state.veli_sinif, st.session_state.veli_tc = ogr[0], ogr[1], v_tc
                st.rerun()
            else: st.error("Giriş başarısız.")
else:
    st.success(f"📍 Hoş geldiniz: **{st.session_state.veli_ad}**")
    conn = sqlite3.connect('okul_sistemi_final.db')
    hoca = conn.execute("SELECT id, ad_soyad FROM ogretmenler WHERE sinif=?", (st.session_state.veli_sinif,)).fetchone()
    
    if hoca:
        h_id, h_ad = hoca
        st.info(f"Öğretmen: **{h_ad}** ({st.session_state.veli_sinif})")
        if st.button("🚪 Oturumu Kapat"):
            st.session_state.veli_giris_yapildi = False
            st.rerun()

        randevular = conn.execute("SELECT id, tarih, saat, durum, veli_tc FROM randevular WHERE ogretmen_id=? ORDER BY tarih, saat", (h_id,)).fetchall()
        mevcut_r = conn.execute("SELECT id, tarih, saat FROM randevular WHERE veli_tc=?", (st.session_state.veli_tc,)).fetchone()
        gunler = sorted(list(set([r[1] for r in randevular])))

        for gun in gunler:
            with st.container(border=True):
                tr_tarih = turkce_tarih_formatla(gun)
                st.markdown(f'<div class="day-label">🗓️ {tr_tarih}</div>', unsafe_allow_html=True)
                
                # MOBİL AYARI İÇİN: Sütun sayısını webde 6 tutuyoruz, CSS mobilde bunu yan yana dizecek.
                sub_cols = st.columns(3)
                gunun_slotlari = [r for r in randevular if r[1] == gun]
                for i, (sid, tarih, saat, durum, v_sahibi) in enumerate(gunun_slotlari):
                    with sub_cols[i % 3]:
                        if durum == "Bos":
                            if st.button(f"🟢 {saat}", key=f"v_{sid}"):
                                if mevcut_r: st.warning("Zaten bir randevunuz var!")
                                else:
                                    conn.execute("UPDATE randevular SET veli_tc=?, durum='Dolu' WHERE id=?", (st.session_state.veli_tc, sid))
                                    conn.commit(); st.rerun()
                        elif v_sahibi == st.session_state.veli_tc:
                            if st.button(f"🔵 {saat}", key=f"v_{sid}"):
                                conn.execute("UPDATE randevular SET veli_tc=NULL, durum='Bos' WHERE id=?", (sid,))
                                conn.commit(); st.rerun()
                        else: 
                            st.button(f"🔴 {saat}", key=f"v_{sid}", disabled=True)
    conn.close()