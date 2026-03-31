import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Öğretmen Paneli", layout="wide", initial_sidebar_state="collapsed")

# --- YARDIMCI FONKSİYONLAR ---
def turkce_tarih_formatla(tarih_str):
    gunler_tr = {
        'Monday': 'Pazartesi', 'Tuesday': 'Salı', 'Wednesday': 'Çarşamba',
        'Thursday': 'Perşembe', 'Friday': 'Cuma', 'Saturday': 'Cumartesi', 'Sunday': 'Pazar'
    }
    try:
        tarih_obj = datetime.strptime(tarih_str, '%Y-%m-%d')
        ing_gun = tarih_obj.strftime('%A')
        return tarih_obj.strftime(f'%d.%m.%Y {gunler_tr.get(ing_gun, ing_gun)}')
    except: return tarih_str

# --- KOYU TEMA VE ÖZEL CSS ---
st.markdown("""
    <meta name="color-scheme" content="dark only">
    <style>
        html, body, [data-testid="stAppViewContainer"] { background-color: #0E1117 !important; }
        h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, div { color: #FFFFFF !important; }
        
        .day-header {
            background-color: #1f77b4;
            color: white;
            padding: 10px 15px;
            border-radius: 8px;
            font-weight: bold;
            margin: 20px 0 10px 0;
        }

        input {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }

        .stButton>button {
            border-radius: 6px !important;
            font-weight: bold !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }

        /* X Silme Butonu Kırmızı Stil */
        button[key*="del_"] {
            color: #ff4b4b !important;
            border-color: #ff4b4b !important;
            padding: 0px !important;
        }

        header, [data-testid="stToolbar"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

if st.button("⬅️ Ana Menüye Dön"): st.switch_page("app.py")

if 'ogretmen_giris_yapildi' not in st.session_state:
    st.session_state.ogretmen_giris_yapildi = False

if not st.session_state.ogretmen_giris_yapildi:
    with st.container(border=True):
        st.subheader("🔐 Öğretmen Girişi")
        u = st.text_input("Kullanıcı Adı")
        p = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap", use_container_width=True):
            conn = sqlite3.connect('okul_sistemi_final.db')
            user = conn.execute("SELECT id, ad_soyad FROM ogretmenler WHERE kullanici_adi=? AND sifre=?", (u, p)).fetchone()
            conn.close()
            if user:
                st.session_state.ogretmen_giris_yapildi = True
                st.session_state.ogretmen_id = user[0]
                st.session_state.ogretmen_ad = user[1]
                st.rerun()
            else: st.error("Hatalı Giriş!")
else:
    t1, t2, t3, t4 = st.tabs(["📅 Planla", "⚡ Takvim Yönetimi", "📋 Liste", "🗑️ Gün Sil"])
    conn = sqlite3.connect('okul_sistemi_final.db')

    # --- TAB 1: PLANLAMA ---
    with t1:
        with st.container(border=True):
            st.write("### 🕒 Otomatik Program Oluştur")
            c1, c2, c3, c4 = st.columns(4)
            t_sec = c1.date_input("Tarih", min_value=datetime.today())
            b_s = c2.time_input("Başla", value=datetime.strptime("09:00", "%H:%M").time())
            s_s = c3.time_input("Bitir", value=datetime.strptime("16:00", "%H:%M").time())
            aralik = c4.selectbox("Aralık", [15, 20, 30, 45, 60], index=2)
            
            if st.button(f"{aralik} Dakikalık Slotları Kaydet", use_container_width=True):
                curr = datetime.combine(t_sec, b_s)
                while curr < datetime.combine(t_sec, s_s):
                    conn.execute("INSERT INTO randevular (ogretmen_id, tarih, saat, durum) VALUES (?,?,?, 'Bos')", 
                                 (st.session_state.ogretmen_id, t_sec.strftime('%Y-%m-%d'), curr.strftime('%H:%M')))
                    curr += timedelta(minutes=aralik)
                conn.commit(); st.success("Slotlar eklendi!"); st.rerun()

    # --- TAB 2: TAKVİM YÖNETİMİ (İSİMLER BUTON ÜZERİNDE) ---
    with t2:
        query = """
            SELECT r.id, r.tarih, r.saat, r.durum, r.veli_tc, o.ad_soyad 
            FROM randevular r 
            LEFT JOIN ogrenciler o ON r.veli_tc = o.tc_no 
            WHERE r.ogretmen_id=? ORDER BY r.tarih, r.saat
        """
        veriler = conn.execute(query, (st.session_state.ogretmen_id,)).fetchall()
        gunler = sorted(list(set([v[1] for v in veriler])))

        for gun in gunler:
            st.markdown(f'<div class="day-header">🗓️ {turkce_tarih_formatla(gun)}</div>', unsafe_allow_html=True)
            with st.container(border=True):
                gunun_verileri = [v for v in veriler if v[1] == gun]
                cols = st.columns(2) # İsimler sığsın diye sütun sayısını 2'ye düşürdüm
                
                for i, (rid, r_tarih, r_saat, r_durum, r_veli_tc, r_ogrenci) in enumerate(gunun_verileri):
                    with cols[i % 2]:
                        sub_c1, sub_c2 = st.columns([5, 1])
                        
                        # Buton Yazısı Belirleme
                        if r_durum == "Bos":
                            label = f"🟢 {r_saat} (Boş)"
                        elif r_veli_tc == "KAPALI":
                            label = f"🚫 {r_saat} (Kapalı)"
                        else:
                            # İSİM BURADA GÖRÜNECEK:
                            isim_kisa = r_ogrenci[:15] + ".." if r_ogrenci and len(r_ogrenci) > 15 else r_ogrenci
                            label = f"👤 {r_saat} | {isim_kisa}"
                        
                        # Ana Buton
                        if sub_c1.button(label, key=f"btn_{rid}", use_container_width=True):
                            yeni_durum = "Dolu" if r_durum == "Bos" else "Bos"
                            yeni_veli = "KAPALI" if r_durum == "Bos" else None
                            conn.execute("UPDATE randevular SET durum=?, veli_tc=? WHERE id=?", (yeni_durum, yeni_veli, rid))
                            conn.commit(); st.rerun()
                        
                        # X Butonu
                        if sub_c2.button("✖", key=f"del_{rid}", use_container_width=True):
                            conn.execute("DELETE FROM randevular WHERE id=?", (rid,))
                            conn.commit(); st.rerun()

    # --- TAB 3: LİSTE ---
    with t3:
        list_data = [v for v in veriler if v[4] and v[4] != 'KAPALI']
        if list_data:
            df = pd.DataFrame(list_data, columns=["ID", "Tarih", "Saat", "Durum", "TC", "Öğrenci"])
            df["Tarih"] = df["Tarih"].apply(turkce_tarih_formatla)
            st.table(df[["Tarih", "Saat", "Öğrenci"]])
        else: st.info("Randevu yok.")

    # --- TAB 4: GÜN SİLME ---
    with t4:
        if gunler:
            secilen = st.selectbox("Silinecek Günü Seç", gunler, format_func=turkce_tarih_formatla)
            if st.button("⚠️ SEÇİLİ GÜNÜ KOMPLE SİL", use_container_width=True):
                conn.execute("DELETE FROM randevular WHERE ogretmen_id=? AND tarih=?", (st.session_state.ogretmen_id, secilen))
                conn.commit(); st.rerun()

    conn.close()