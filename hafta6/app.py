import streamlit as st
import numpy as np
import io

st.set_page_config(page_title="Gelişmiş Matris Analizörü", layout="wide")

st.title("📊 Esnek Matris İşlem Merkezi")
st.markdown("Artık kare matris zorunluluğu yok! Her türlü boyuttaki matrisi analiz edebilirsiniz.")

uploaded_file = st.file_uploader("Matris dosyasını (.txt) yükleyin", type=["txt"])

if uploaded_file is not None:
    try:
        # Matrisi oku
        content = uploaded_file.read().decode("utf-8")
        matris = np.loadtxt(io.StringIO(content))
        
        if len(matris.shape) == 1:
            matris = matris.reshape(1, -1)

        satir, sutun = matris.shape
        
        col_m1, col_m2 = st.columns([1, 1])
        with col_m1:
            st.subheader("Giriş Matrisi")
            st.write(f"Boyut: **{satir} x {sutun}**")
            st.dataframe(matris)

        # Raporlama için string hazırlığı
        rapor = io.StringIO()
        rapor.write(f"Matris Analiz Raporu\nBoyut: {satir}x{sutun}\n{'-'*30}\n")

        # --- İŞLEM MANTIĞI ---
        
        if satir == sutun:
            st.success("🎯 Bu bir kare matristir.")
            det = np.linalg.det(matris)
            st.metric("Determinant", f"{det:.4f}")
            rapor.write(f"Determinant: {det}\n")
            
            if not np.isclose(det, 0):
                tersi = np.linalg.inv(matris)
                with col_m2:
                    st.subheader("Matrisin Tersi ($A^{-1}$)")
                    st.dataframe(tersi)
                rapor.write(f"\nMatrisin Tersi:\n{tersi}\n")
            else:
                st.warning("Determinant 0 olduğu için standart tersi yoktur.")
        else:
            st.info(f"ℹ️ Kare matris değil ({satir}x{sutun}). Determinant hesaplanamaz, ancak Sözde Ters (Pseudo-Inverse) hesaplanıyor.")
            rapor.write("Matris kare olmadığı için determinant hesaplanmadı.\n")

        # --- SATIR TOPLAMLARI ---
        st.divider()
        st.subheader("📈 Her Satırın Toplamı")
        satir_toplamlari = np.sum(matris, axis=1)
        
        # Tabloyla göster
        sonuc_tablosu = np.column_stack((matris, satir_toplamlari))
        
        col_names = [f"Sütun {i+1}" for i in range(sutun)] + ["📊 TOPLAM"]
        sonuc_df = np.vstack((col_names, sonuc_tablosu))
        
        st.write("Matrisin her satırı ve satırın toplamı:")
        st.dataframe(sonuc_tablosu)
        
        rapor.write(f"\nHer Satırın Toplamı:\n")
        for idx, toplam in enumerate(satir_toplamlari):
            rapor.write(f"Satır {idx+1}: {toplam:.4f}\n")
        
        # --- HER DURUMDA HESAPLANAN: PSEUDO-INVERSE ---
        # (Kare matrislerde de çalışır ve normal terse çok yakındır)
        pseudo_inv = np.linalg.pinv(matris)
        
        st.divider()
        st.subheader("Sözde Ters (Moore-Penrose Pseudo-Inverse)")
        st.write("Bu ters, özellikle lineer denklem sistemlerinde en küçük kareler çözümü için kullanılır.")
        st.dataframe(pseudo_inv)
        rapor.write(f"\nSözde Ters (Pseudo-Inverse):\n{pseudo_inv}\n")

        # İndirme Butonu
        st.download_button(
            label="Analiz Sonuçlarını İndir",
            data=rapor.getvalue(),
            file_name="matris_analiz_sonuc.txt",
            mime="text/plain"
        )

    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")
else:
    st.write("---")
    st.info("Lütfen işlem yapmak için bir dosya yükleyin.")