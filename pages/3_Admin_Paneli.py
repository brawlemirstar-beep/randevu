import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Sistem Yönetimi", layout="wide", initial_sidebar_state="collapsed")

# --- SINIF LİSTESİ (1-A'dan 4-D'ye) ---
SINIFLAR = []
for i in range(1, 5):
    for sube in ['A', 'B', 'C', 'D']:
        SINIFLAR.append(f"{i}-{sube}")

# --- CSS TASARIM (KOYU TEMA VE KUTU STİLLERİ) ---
st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"] { background-color: #0E1117 !important; }
        h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, div { color: #FFFFFF !important; }
        .stButton>button {
            background-color: #262730 !important;
            color: #FFFFFF !important;
            border: 1px solid #4A4A4A !important;
            width: 100% !important;
            border-radius: 8px !important;
            font-weight: bold !important;
        }
        .stButton>button:hover { border-color: #1f77b4 !important; color: #1f77b4 !important; }
        input { background-color: #FFFFFF !important; color: #000000 !important; }
        header, [data-testid="stToolbar"] { display: none !important; }
        [data-testid="stMetricValue"] { color: #28a745 !important; }
    </style>
""", unsafe_allow_html=True)

if st.button("⬅️ Ana Menüye Dön"): st.switch_page("app.py")

# --- OTURUM KONTROLÜ ---
if 'admin_giris_yapildi' not in st.session_state:
    st.session_state.admin_giris_yapildi = False

if not st.session_state.admin_giris_yapildi:
    with st.container(border=True):
        st.subheader("🔑 Admin Girişi")
        a_u = st.text_input("Kullanıcı Adı")
        a_p = st.text_input("Şifre", type="password")
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            conn = sqlite3.connect('okul_sistemi_final.db')
            # Tablo yoksa hata vermemesi için kontrol (ilk kurulum)
            conn.execute("CREATE TABLE IF NOT EXISTS sistem_adminleri (id INTEGER PRIMARY KEY AUTOINCREMENT, k_adi TEXT, sifre TEXT)")
            res = conn.execute("SELECT * FROM sistem_adminleri WHERE k_adi=? AND sifre=?", (a_u, a_p)).fetchone()
            conn.close()
            if res:
                st.session_state.admin_giris_yapildi = True
                st.rerun()
            else: st.error("Hatalı admin bilgileri!")

else:
    col_h, col_c = st.columns([5,1])
    col_h.success("🔓 Yönetim Yetkisi Aktif")
    if col_c.button("🚪 Güvenli Çıkış"):
        st.session_state.admin_giris_yapildi = False
        st.rerun()

    t1, t2, t3 = st.tabs(["👨‍🏫 Öğretmen Yönetimi", "👶 Öğrenci Yönetimi", "🛡️ Admin Ayarları"])
    conn = sqlite3.connect('okul_sistemi_final.db')

    # --- 1. ÖĞRETMEN YÖNETİMİ ---
    with t1:
        st.subheader("👨‍🏫 Yeni Öğretmen Kaydı")
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns(4)
            h_ad_in = c1.text_input("Ad Soyad", placeholder="Örn: Ahmet Yılmaz")
            h_u_in = c2.text_input("Kullanıcı Adı", placeholder="ahmet123")
            h_s_in = c3.text_input("Şifre", type="default")
            h_snf_in = c4.selectbox("Sorumlu Sınıf", SINIFLAR)
            if st.button("✅ Öğretmeni Sisteme Ekle"):
                if h_ad_in and h_u_in:
                    conn.execute("INSERT INTO ogretmenler (ad_soyad, kullanici_adi, sifre, sinif) VALUES (?,?,?,?)", 
                                 (h_ad_in, h_u_in, h_s_in, h_snf_in))
                    conn.commit(); st.rerun()
                else: st.error("Lütfen tüm alanları doldurun!")
        
        st.divider()
        df_h = pd.read_sql_query("SELECT * FROM ogretmenler", conn)
        
        if not df_h.empty:
            st.subheader("✏️ Düzenle / Sil")
            h_list = df_h.apply(lambda x: f"{x['id']} - {x['ad_soyad']} ({x['sinif']})", axis=1).tolist()
            selected_h_str = st.selectbox("İşlem yapılacak öğretmen", h_list)
            selected_h_id = int(selected_h_str.split(" - ")[0])
            h_data = df_h[df_h['id'] == selected_h_id].iloc[0]

            with st.container(border=True):
                ec1, ec2, ec3, ec4 = st.columns(4)
                up_ad = ec1.text_input("Ad Soyad", value=str(h_data['ad_soyad']), key="u_h_ad")
                up_u = ec2.text_input("Kullanıcı Adı", value=str(h_data['kullanici_adi']), key="u_h_u")
                up_s = ec3.text_input("Şifre", value=str(h_data['sifre']), key="u_h_s")
                try: c_idx = SINIFLAR.index(h_data['sinif'])
                except: c_idx = 0
                up_snf = ec4.selectbox("Sınıf", SINIFLAR, index=c_idx, key="u_h_snf")
                
                b1, b2 = st.columns(2)
                if b1.button("💾 DEĞİŞİKLİKLERİ KAYDET"):
                    conn.execute("UPDATE ogretmenler SET ad_soyad=?, kullanici_adi=?, sifre=?, sinif=? WHERE id=?", 
                                 (up_ad, up_u, up_s, up_snf, selected_h_id))
                    conn.commit(); st.success("Bilgiler güncellendi!"); st.rerun()
                if b2.button("🗑️ ÖĞRETMEN KAYDINI SİL"):
                    conn.execute("DELETE FROM ogretmenler WHERE id=?", (selected_h_id,))
                    conn.commit(); st.warning("Kayıt silindi!"); st.rerun()
        
            st.write("📋 **Kayıtlı Öğretmen Listesi**")
            st.dataframe(df_h, use_container_width=True, hide_index=True)

    # --- 2. ÖĞRENCİ YÖNETİMİ ---
    with t2:
        st.subheader("👶 Yeni Öğrenci/Veli Kaydı")
        with st.container(border=True):
            o1, o2, o3, o4 = st.columns(4)
            o_tc = o1.text_input("Veli T.C. No", max_chars=11)
            o_no = o2.text_input("Öğrenci Okul No")
            o_ad = o3.text_input("Öğrenci Ad Soyad")
            o_snf = o4.selectbox("Sınıfı ", SINIFLAR)
            if st.button("➕ Öğrenciyi Kaydet"):
                if o_tc and o_ad:
                    conn.execute("INSERT INTO ogrenciler (tc_no, okul_no, ad_soyad, sinif) VALUES (?,?,?,?)", 
                                 (o_tc, o_no, o_ad, o_snf))
                    conn.commit(); st.rerun()
                else: st.error("TC ve Ad Soyad zorunludur!")

        st.divider()
        df_o = pd.read_sql_query("SELECT * FROM ogrenciler", conn)
        
        if not df_o.empty:
            st.subheader("✏️ Düzenle / Sil")
            o_list = df_o.apply(lambda x: f"{x['tc_no']} - {x['ad_soyad']}", axis=1).tolist()
            selected_o_str = st.selectbox("İşlem yapılacak öğrenci", o_list)
            selected_o_tc = selected_o_str.split(" - ")[0]
            o_data = df_o[df_o['tc_no'] == selected_o_tc].iloc[0]

            with st.container(border=True):
                oc1, oc2, oc3, oc4 = st.columns(4)
                uo_tc = oc1.text_input("Veli T.C.", value=str(o_data['tc_no']), key="u_o_tc")
                uo_no = oc2.text_input("Okul No", value=str(o_data['okul_no']), key="u_o_no")
                uo_ad = oc3.text_input("Ad Soyad", value=str(o_data['ad_soyad']), key="u_o_ad")
                try: o_idx = SINIFLAR.index(o_data['sinif'])
                except: o_idx = 0
                uo_snf = oc4.selectbox("Sınıf  ", SINIFLAR, index=o_idx, key="u_o_snf")

                ob1, ob2 = st.columns(2)
                if ob1.button("💾 GÜNCELLE"):
                    conn.execute("UPDATE ogrenciler SET tc_no=?, okul_no=?, ad_soyad=?, sinif=? WHERE tc_no=?", 
                                 (uo_tc, uo_no, uo_ad, uo_snf, selected_o_tc))
                    conn.commit(); st.success("Öğrenci güncellendi!"); st.rerun()
                if ob2.button("🗑️ ÖĞRENCİYİ SİL"):
                    conn.execute("DELETE FROM ogrenciler WHERE tc_no=?", (selected_o_tc,))
                    conn.commit(); st.warning("Öğrenci kaydı silindi!"); st.rerun()
        
            st.write("📋 **Kayıtlı Öğrenci Listesi**")
            st.dataframe(df_o, use_container_width=True, hide_index=True)

    # --- 3. ADMIN AYARLARI ---
    with t3:
        st.subheader("🛡️ Admin Yetkilendirme")
        col_left, col_right = st.columns(2)
        
        with col_left:
            with st.container(border=True):
                st.write("🆕 **Yeni Admin Ekle**")
                nu = st.text_input("Yeni Admin Kullanıcı Adı")
                np = st.text_input("Yeni Admin Şifre", type="password")
                if st.button("Admin Yetkisi Ver"):
                    if nu and np:
                        conn.execute("INSERT INTO sistem_adminleri (k_adi, sifre) VALUES (?,?)", (nu, np))
                        conn.commit(); st.success(f"{nu} artık admin."); st.rerun()
        
        with col_right:
            st.write("📋 **Mevcut Adminler**")
            df_a = pd.read_sql_query("SELECT id, k_adi FROM sistem_adminleri", conn)
            st.table(df_a)
            del_adm = st.text_input("Silinecek Admin ID")
            if st.button("❌ Admin Yetkisini Kaldır"):
                if del_adm:
                    conn.execute("DELETE FROM sistem_adminleri WHERE id=?", (del_adm,))
                    conn.commit(); st.rerun()

    conn.close()