import streamlit as st
from utils import load_image
from vision_model import describe_image
from analyzer import analyze_ad

st.set_page_config(page_title="Ad Analyzer AI", layout="centered")
st.title("AI Advertising Analyzer")
st.markdown("Sube una imagen de un anuncio y la IA lo analizará.")

uploaded_file = st.file_uploader("Sube la imagen del anuncio", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Anuncio cargado", use_column_width=True)
    
    image = load_image(uploaded_file)
    label, results = describe_image(image)

    st.markdown(f"### Descripción automática:")
    st.write(f"La IA describe la imagen como: **{label}**")

    with st.spinner("Analizando con IA..."):
        analysis = analyze_ad(label, results)

    st.markdown("### Recomendación:")
    st.write(analysis)
