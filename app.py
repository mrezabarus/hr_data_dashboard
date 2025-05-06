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
pergerakan_join = df[(df['Tahun Masuk'] == tahun_tertentu) ]
pergerakan_resign = df[((df['Tahun Keluar'] == tahun_tertentu) )]

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

## view perbandingan yang resign dan join
fig = px.line(df_bulan, x='TahunBulan', y=['Masuk','Keluar'], markers=True,
              title=f"Pergerakan Pegawai Masuk dan Keluar Tahun {tahun_tertentu}")

st.plotly_chart(fig)

col1, col2 = st.columns(2)

with col1:
  

  st.write(f"List Pegawai Join Tahun {tahun_tertentu}:")
  st.dataframe(pergerakan_join)

 

## Tampilkan data pergerakan
with col2:

  st.write(f"List Pegawai Resign Tahun {tahun_tertentu}:")
  st.dataframe(pergerakan_resign)
  


# Filter pegawai aktif di tahun tersebut
aktif_di_tahun = df[
    (df['Tahun Masuk'] <= tahun_tertentu) &
    (
        (df['Tahun Keluar'].isna()) |  # Belum resign
        (df['Tahun Keluar'] > tahun_tertentu)  # Resign setelah tahun tersebut
    )
]

# Hitung jumlah pegawai aktif per direktorat
jumlah_per_departemen = aktif_di_tahun.groupby('Department')['Nama Pegawai'].count().reset_index()
jumlah_per_departemen = jumlah_per_departemen.rename(columns={'Nama Pegawai': 'Jumlah Pegawai'})


st.write(f"Pegawai Aktif pada Tahun {tahun_tertentu}:")
st.dataframe(aktif_di_tahun[['Nama Pegawai', 'Tanggal Masuk', 'Tanggal Resign', 'Status', 'Department', 'Jabatan']])

fig_dept = px.bar(jumlah_per_departemen,
                  x='Department',
                  y='Jumlah Pegawai',
                  title=f"Jumlah pegawai Aktif per Departemen di Tahun {tahun_tertentu}",
                  text='Jumlah Pegawai'
                  )
fig_dept.update_layout(
  yaxis=dict(range=[0,80])
)

st.plotly_chart(fig_dept, use_container_width=True)