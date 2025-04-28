import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")

df = pd.read_csv('data/data_pegawai_hr_project.csv')

## Filter tahun
tahun_tertentu = st.number_input("Pilih tahun", min_value=2000, max_value=2024, value=2023)

df['Tanggal Masuk'] = pd.to_datetime(df['Tanggal Masuk'])
df['Tahun Masuk'] = df['Tanggal Masuk'].dt.year
df['Bulan Masuk'] = df['Tanggal Masuk'].dt.month

df['Tanggal Resign'] = pd.to_datetime(df['Tanggal Resign'], errors='coerce') #coerce untuk menghindari error krna ada data 'Still Working' jadi Nat
df['Tahun Keluar'] = df['Tanggal Resign'].dt.year
df['Bulan Keluar'] = df['Tanggal Resign'].dt.month

## menampilkan pergerakan data pegawai
pergerakan = df[(df['Tahun Masuk'] == tahun_tertentu) | ((df['Tahun Keluar'] == tahun_tertentu) )]

######## LINE CHART Resign And Join #########

# Buat kolom TahunBulan
#df['TahunBulan Masuk'] = pd.to_datetime(df['Tahun Masuk'].astype(str) + '-' + df['Bulan Masuk'].astype(str) + '-01', errors='coerce')
df['TahunBulan Masuk'] = pd.to_datetime(df['Tahun Masuk'].astype(str) + '-' + df['Bulan Masuk'].astype(str) + '-01', errors='coerce')
df['TahunBulan Keluar'] = pd.to_datetime(df['Tahun Keluar'].astype(str) + '-' + df['Bulan Keluar'].astype(str) + '-01', errors='coerce')



# Filter data masuk dan keluar
df_masuk = df[df['Tahun Masuk'] == tahun_tertentu].copy()
df_keluar = df[df['Tahun Keluar'] == tahun_tertentu].copy()


# Hitung jumlah masuk dan keluar per bulan
masuk = df[df['Tahun Masuk'] == tahun_tertentu]
masuk_perbulan = masuk['Tanggal Masuk'].dt.to_period('M').value_counts().sort_index()

keluar = df[df['Tahun Keluar'] == tahun_tertentu]
keluar_perbulan = masuk['Tanggal Resign'].dt.to_period('M').value_counts().sort_index()


df_bulan = pd.DataFrame({
  'Masuk': masuk_perbulan,
  'Keluar': keluar_perbulan
}).fillna(0)


# Reset index biar bisa di plot
df_bulan = df_bulan.reset_index()
df_bulan['TahunBulan'] = df_bulan['index'].dt.to_timestamp()

col1, col2 = st.columns(2)

with col1:
  fig = px.line(df_bulan, x='TahunBulan', y=['Masuk','Keluar'], markers=True,
                title=f"Pergerakan Pegawai Masuk dan Keluar Tahun {tahun_tertentu}")

  st.plotly_chart(fig)


# ## filter data berdasarkan tahun tertentu
# df_filtered = df[(df['Tahun Masuk'] <= tahun_tertentu) & ((df['Tahun Keluar'] >= tahun_tertentu )| df['Status'] == 'Aktif')]

# # Hitung jumlah pegawai per bulan
# df_filtered['Bulan Masuk'] = pd.to_datetime(df_filtered['Tahun Masuk'].astype(str) + '-' + df_filtered['Bulan Masuk'].astype(str), format='%Y-%m')
# df_filtered['Bulan Keluar'] = pd.to_datetime(df_filtered['Tahun Keluar'].astype(str) + '-' + df_filtered['Bulan Keluar'].astype(str), format='%Y-%m')

# #hitung pegawai perbulan
# df_filtered['Pergerakan'] = df_filtered.apply(lambda x: 'Masuk' if pd.notna(x['Bulan Masuk']) else ('Keluar' if pd.notna(x['Bulan Keluar']) else 'Aktif'), axis=1)

# #gabungkan berdasarkan bulan dan hitung jumlah pegawai perbulan
# df_bulan = df_filtered.groupby(df_filtered['Bulan Masuk'].dt.to_period('M'))['Pergerakan'].value_counts().unstack().fillna()

# ## Membuat diagram baris
# fig = px.line(df_bulan, x=df_bulan.index, y=df_bulan.columns, title=f"Pergerakan Pegawai per Bulan Tahun {tahun_tertentu}")
# st.plotly_chart(fig)


## Tampilkan data pergerakan
with col2:
  st.write(f"Pergerakan Pegawai Tahun {tahun_tertentu}:")
  st.dataframe(pergerakan)