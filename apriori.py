import pandas as pd
import numpy as np
from apyori import apriori
import streamlit as st
import matplotlib.pyplot as plt

# Fungsi utama untuk menampilkan hasil
def main():
    # Menambahkan CSS untuk latar belakang
    # st.markdown(
    #     """
    #     <style>
    #     .stApp {
    #         background-image: url("data:image/jpeg;base64,%s");
    #         background-size: cover;
    #     }
    #     </style>
    #     """ % to_base64("24.png"),
    #     unsafe_allow_html=True
    # )
    
    st.title("BuyPatterns")
    
    # Sidebar untuk upload file dan kontrol parameter
    st.sidebar.header("Pengaturan")
    
    # Sidebar untuk upload file
    uploaded_file = st.sidebar.file_uploader("Unggah file Excel", type=["xlsx", "xls"])

    # Sidebar untuk input nilai support dan confidence
    min_support = st.sidebar.slider("Min Support", 0.01, 1.0, 0.05)
    min_confidence = st.sidebar.slider("Min Confidence", 0.01, 1.0, 0.5)
    
    # Sidebar untuk tombol hitung apriori
    apriori_button = st.sidebar.button('Hitung Apriori')

    # Jika file di-upload
    if uploaded_file is not None:
        # Membaca data yang diunggah
        data1 = pd.read_excel(uploaded_file)
        st.subheader("Data yang Diupload")
        st.write(data1)
        
        # Mengecek apakah ada missing values
        st.write(f"Apakah ada missing values? {data1.isnull().values.any()}")
        
        # Preprocessing data: Menghapus kolom yang tidak relevan
        data = data1.drop(['No', 'tanggal'], axis=1, errors='ignore')  # Mengabaikan jika kolom tidak ada
        st.subheader("Data Setelah Preprocessing")
        st.write(data)
        
        # Mengubah format data menjadi array
        records = []
        for i in range(data.shape[0]):
            records.append([str(data.values[i, j]).split(',') for j in range(data.shape[1])])

        trx = [[] for _ in range(len(records))]
        for i in range(len(records)):
            for j in records[i][0]:
                trx[i].append(j)

        # Jika tombol "Hitung Apriori" ditekan
        if apriori_button:
            # Menjalankan algoritma Apriori dengan parameter yang diberikan
            association_rules = apriori(trx, min_support=min_support, min_confidence=min_confidence, min_lift=1)
            
            # Mengubah hasil asosiasi menjadi list
            association_results = list(association_rules)

            # Membuat DataFrame untuk hasil asosiasi
            Result = pd.DataFrame(columns=['Rule', 'Support', 'Confidence'])

            supports = []
            confidences = []

            for item in association_results:
                pair = item[2]
                for i in pair:
                    if i[3] != 1:  # Mengecek apakah lift lebih besar dari 1
                        new_row = {
                            'Rule': str([x for x in i[0]]) + " -> " + str([x for x in i[1]]),
                            'Support': str(round(item[1] * 100, 2)) + '%',
                            'Confidence': str(round(i[2] * 100, 2)) + '%'
                        }
                        Result = pd.concat([Result, pd.DataFrame([new_row])], ignore_index=True)
                        
                        supports.append(round(item[1] * 100, 2))
                        confidences.append(round(i[2] * 100, 2))

            # Menampilkan hasil asosiasi di Streamlit
            if not Result.empty:
                st.subheader("Hasil Asosiasi Apriori")
                st.dataframe(Result)
                
                # Visualisasi grafik untuk Support dan Confidence
                st.subheader("Grafik Hasil Asosiasi")
                fig, ax = plt.subplots(figsize=(10, 6))

                index = np.arange(len(Result))
                bar_width = 0.35

                # Grafik Support
                ax.bar(index, supports, bar_width, label='Support', color='b')

                # Grafik Confidence
                ax.bar(index + bar_width, confidences, bar_width, label='Confidence', color='g')

                ax.set_xlabel('Rules')
                ax.set_ylabel('Percentage')
                ax.set_title('Support dan Confidence untuk Setiap Aturan Asosiasi')
                ax.set_xticks(index + bar_width / 2)
                ax.set_xticklabels(Result['Rule'], rotation=90)
                ax.legend()

                st.pyplot(fig)
            else:
                st.write("Tidak ada aturan asosiasi yang memenuhi kriteria.")

# Fungsi untuk mengonversi gambar ke format base64
import base64
def to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Menjalankan aplikasi
if __name__ == "__main__":
    main()
