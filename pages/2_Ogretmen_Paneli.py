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
        }

        button[key*="del_"], button[key*="edit_"] {
            padding: 0px !important;
            min-height: 35px !important;
        }
        
        button[key*="del_"] { color: #ff4b4b !important; border-color: #ff4b4b !important; }
        button[key*="edit_"] { color: #f1c40f !important; border-color: #f1c40f !important; }

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
                st.session_state.ogretmen_id = user[0]; st.session_state.ogretmen_ad = user[1]
                st.rerun()
            else: st.error("Hatalı Giriş!")
else:
    t1, t2, t3, t4 = st.tabs(["📅 Planlama", "⚡ Takvim Yönetimi", "📋 Liste", "🗑️ Gün Sil"])
    conn = sqlite3.connect('okul_sistemi_final.db')

    # --- TAB 1: AKILLI PLANLAMA (TOPLU VE TEKLİ) ---
    with t1:
        with st.container(border=True):
            st.write("### 🕒 Program Oluştur")
            m1, m2 = st.columns(2)
            plan_tipi = m1.radio("İşlem Tipi", ["Toplu Slot Oluştur", "Tekli Özel Saat Ekle"], horizontal=True)
            
            if plan_tipi == "Toplu Slot Oluştur":
                c1, c2, c3, c4 = st.columns(4)
                t_sec = c1.date_input("Tarih", min_value=datetime.today())
                b_s = c2.time_input("Başla", value=datetime.strptime("09:00", "%H:%M").time())
                s_s = c3.time_input("Bitir", value=datetime.strptime("16:00", "%H:%M").time())
                aralik = c4.selectbox("Aralık", [15, 20, 30, 45, 60], index=2)
                
                if st.button("Otomatik Slotları Kaydet", use_container_width=True):
                    curr = datetime.combine(t_sec, b_s)
                    while curr < datetime.combine(t_sec, s_s):
                        saat_str = curr.strftime('%H:%M')
                        tarih_str = t_sec.strftime('%Y-%m-%d')
                        exists = conn.execute("SELECT id FROM randevular WHERE ogretmen_id=? AND tarih=? AND saat=?", 
                                            (st.session_state.ogretmen_id, tarih_str, saat_str)).fetchone()
                        if not exists:
                            conn.execute("INSERT INTO randevular (ogretmen_id, tarih, saat, durum) VALUES (?,?,?, 'Bos')", 
                                         (st.session_state.ogretmen_id, tarih_str, saat_str))
                        curr += timedelta(minutes=aralik)
                    conn.commit(); st.success("Slotlar eklendi!"); st.rerun()
            
            else:
                c1, c2 = st.columns(2)
                t_sec = c1.date_input("Tarih Seç", min_value=datetime.today())
                mevcutlar = [r[0] for r in conn.execute("SELECT saat FROM randevular WHERE ogretmen_id=? AND tarih=?", 
                                                        (st.session_state.ogretmen_id, t_sec.strftime('%Y-%m-%d'))).fetchall()]
                saat_listesi = [f"{h:02d}:{m:02d}" for h in range(8, 20) for m in [0, 15, 30, 45] if f"{h:02d}:{m:02d}" not in mevcutlar]
                
                secilen_tek_saat = c2.selectbox("Eklenebilir Saatler", saat_listesi)
                if st.button("Tekli Saati Ekle", use_container_width=True):
                    conn.execute("INSERT INTO randevular (ogretmen_id, tarih, saat, durum) VALUES (?,?,?, 'Bos')", 
                                 (st.session_state.ogretmen_id, t_sec.strftime('%Y-%m-%d'), secilen_tek_saat))
                    conn.commit(); st.rerun()

    # --- TAB 2: TAKVİM YÖNETİMİ (GÜN İÇİ TEKLİ EKLEME DAHİL) ---
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
                # --- GÜN İÇİ AKILLI TEKLİ EKLEME ---
                with st.expander(f"➕ Bu Güne Özel Saat Ekle"):
                    # O güne ait mevcut saatleri çek
                    gunun_mevcut_saatleri = [v[2] for v in veriler if v[1] == gun]
                    # Sadece mevcut olmayan saatleri listele
                    gunun_liste = [f"{h:02d}:{m:02d}" for h in range(8, 20) for m in [0, 15, 30, 45] if f"{h:02d}:{m:02d}" not in gunun_mevcut_saatleri]
                    
                    c_ekle, c_onay = st.columns([3, 1])
                    eklenecek_saat = c_ekle.selectbox("Saat Seç", gunun_liste, key=f"sel_{gun}")
                    if c_onay.button("Ekle", key=f"add_{gun}"):
                        conn.execute("INSERT INTO randevular (ogretmen_id, tarih, saat, durum) VALUES (?,?,?, 'Bos')",
                                     (st.session_state.ogretmen_id, gun, eklenecek_saat))
                        conn.commit(); st.rerun()

                st.divider()
                
                gunun_verileri = [v for v in veriler if v[1] == gun]
                cols = st.columns(2)
                for i, (rid, r_tarih, r_saat, r_durum, r_veli_tc, r_ogrenci) in enumerate(gunun_verileri):
                    with cols[i % 2]:
                        sub_c1, sub_c2, sub_c3 = st.columns([6, 1, 1])
                        if r_durum == "Bos": label = f"🟢 {r_saat} (Boş)"
                        elif r_veli_tc == "KAPALI": label = f"🚫 {r_saat} (Kapalı)"
                        else: label = f"👤 {r_saat} | {r_ogrenci[:12] if r_ogrenci else '...'}"
                        
                        if sub_c1.button(label, key=f"btn_{rid}", use_container_width=True):
                            yeni_durum = "Dolu" if r_durum == "Bos" else "Bos"
                            yeni_veli = "KAPALI" if r_durum == "Bos" else None
                            conn.execute("UPDATE randevular SET durum=?, veli_tc=? WHERE id=?", (yeni_durum, yeni_veli, rid))
                            conn.commit(); st.rerun()
                        
                        if sub_c2.button("✏️", key=f"edit_{rid}"): st.session_state[f"edit_mode_{rid}"] = True
                        if sub_c3.button("✖", key=f"del_{rid}"):
                            conn.execute("DELETE FROM randevular WHERE id=?", (rid,))
                            conn.commit(); st.rerun()
                        
                        if st.session_state.get(f"edit_mode_{rid}", False):
                            new_val = st.text_input("Saat", value=r_saat, key=f"inp_{rid}")
                            if st.button("Kaydet", key=f"save_{rid}"):
                                conn.execute("UPDATE randevular SET saat=? WHERE id=?", (new_val, rid))
                                conn.commit(); st.session_state[f"edit_mode_{rid}"] = False; st.rerun()

    # --- TAB 3: LİSTE & TAB 4: GÜN SİLME (Stabil) ---
    with t3:
        list_data = [v for v in veriler if v[4] and v[4] != 'KAPALI']
        if list_data:
            df = pd.DataFrame(list_data, columns=["ID", "Tarih", "Saat", "Durum", "TC", "Öğrenci"])
            df["Tarih"] = df["Tarih"].apply(turkce_tarih_formatla)
            st.table(df[["Tarih", "Saat", "Öğrenci"]])
        else: st.info("Randevu bulunmuyor.")

    with t4:
        if gunler:
            secilen = st.selectbox("Silinecek Günü Seç", gunler, format_func=turkce_tarih_formatla)
            if st.button("⚠️ GÜNÜ KOMPLE SİL", use_container_width=True):
                conn.execute("DELETE FROM randevular WHERE ogretmen_id=? AND tarih=?", (st.session_state.ogretmen_id, secilen))
                conn.commit(); st.rerun()

    conn.close()