import pandas as pd
import streamlit as st
import plotly.express as px

from deep_translator import GoogleTranslator
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

st.set_page_config(page_title="Dashboard Pegawai", layout="wide")
st.title("Dashboard Utama Pegawai")
st.markdown("Klik menu di kiri (sidebar) untuk menuju halaman lainnya, misalnya halaman **Sentimen**.")

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

# Reset index biar bisa di plot
df_bulan = df_bulan.reset_index()
df_bulan['TahunBulan'] = df_bulan['index'].dt.to_timestamp()

# Filter data berdasarkan tahun_tertentu
df_bulan_filtered = df_bulan[df_bulan['TahunBulan'].dt.year == tahun_tertentu]

## view perbandingan yang resign dan join
fig = px.line(df_bulan_filtered, x='TahunBulan', y=['Masuk','Keluar'], markers=True,
              title=f"Pergerakan Pegawai Masuk dan Keluar Tahun {tahun_tertentu}")


fig.for_each_trace(
  lambda t: t.update(line=dict(color='green')) if t.name == 'Masuk' else t.update(line=dict(color='red'))
)
# fig.for_each_trace(
#   lambda t: t.update(line=dict(color='green')) if t.name == 'Masuk' else t.update(line=dict(color='red'))
# )


col1, col2 = st.columns(2)
with col1:

  st.plotly_chart(fig)

with col2:
  fig_dept = px.bar(jumlah_per_departemen,
                    x='Department',
                    y='Jumlah Pegawai',
                    color='Department',
                    title=f"Jumlah pegawai Aktif per Departemen di Tahun {tahun_tertentu}",
                    text='Jumlah Pegawai'
                    )
  fig_dept.update_layout(
    yaxis=dict(range=[0,80])
  )

  st.plotly_chart(fig_dept, use_container_width=True)
  
col1, col2 = st.columns(2)

with col1:
  

  st.write(f"List Pegawai Join Tahun {tahun_tertentu}:")
  st.dataframe(pergerakan_join)

 

## Tampilkan data pergerakan
with col2:

  st.write(f"List Pegawai Resign Tahun {tahun_tertentu}:")
  st.dataframe(pergerakan_resign)
  


st.write(f"Pegawai Aktif pada Tahun {tahun_tertentu}:")
st.dataframe(aktif_di_tahun[['Nama Pegawai', 'Tanggal Masuk', 'Tanggal Resign', 'Status', 'Department', 'Jabatan']])


## membersihkan feedback yang hanya berisi tanda baca atau kosong
df_cleaned = df[~df['Feedback'].str.match(r'^[.,\s]*$')]

analyzer = SentimentIntensityAnalyzer()

def translate_feedback(text):
  return GoogleTranslator(source='auto', target='en').translate(text)


def get_vader_sentiment(feedback):
  english_text = translate_feedback(feedback)
  sentiment = analyzer.polarity_scores(english_text)
  if sentiment['compound'] >= 0.05:
    return 'Positif'
  elif sentiment['compound'] <= -0.05:
    return 'Negatif'
  else:
    return 'Netral'

df_cleaned['Sentimen'] = df_cleaned['Feedback'].apply(get_vader_sentiment)

sentimen_count = df_cleaned['Sentimen'].value_counts().reset_index()
sentimen_count.columns = ['Sentimen','Jumlah']

st.write("Data Sentimen Pegawai menggunakan google translate dan vader untuk menentukan sentimennya:")
st.dataframe(df_cleaned)

fig_sentiment = px.bar(sentimen_count, x='Sentimen',y='Jumlah', color='Sentimen', title="Distribusi sentiment feedback pegawai")
st.plotly_chart(fig_sentiment)