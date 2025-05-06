import pandas as pd
import streamlit as st
import plotly.express as px

from deep_translator import GoogleTranslator
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

st.set_page_config(page_title="Dashboard Pegawai", layout="wide")
st.title("Halaman Prediksi Resign Pegawai")

df = pd.read_csv('data/data_pegawai_hr_project.csv')

st.dataframe(df)