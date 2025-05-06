import pandas as pd
import streamlit as st
import plotly.express as px

from deep_translator import GoogleTranslator
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

st.set_page_config(page_title="Dashboard Pegawai", layout="wide")
st.title("Halaman Sentimen Pegawai")

df = pd.read_csv('data/data_pegawai_hr_project.csv')

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

st.write("Data Sentimen Pegawai menggunakan google translate dan vader untuk menentukan sentimennya berdasarkan kolom feedback:")
st.dataframe(df_cleaned)





# Kelompokkan berdasarkan Jabatan dan hitung jumlah sentimen
sentimen_per_jabatan = df_cleaned.groupby(['Jabatan', 'Sentimen']).size().unstack(fill_value=0)

sentimen_long = sentimen_per_jabatan.reset_index().melt(id_vars='Jabatan',
                                                        var_name='Sentimen',
                                                        value_name='Jumlah')

col1, col2 = st.columns(2)

with col1:

  fig_sentiment_jabatan = px.bar(sentimen_long, x='Jabatan', y='Jumlah', color="Sentimen", title="Distribusi Sentimen berdasarkan Jabatan")
  st.plotly_chart(fig_sentiment_jabatan)

with col2:
  fig_sentiment = px.bar(sentimen_count, x='Sentimen',y='Jumlah', color='Sentimen', title="Distribusi sentiment feedback pegawai")
  st.plotly_chart(fig_sentiment)