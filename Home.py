#Home

# Libraries

import streamlit as st
from PIL import Image

st.set_page_config(page_title="Home", 
                   page_icon="💼")

imagem = Image.open('profile_image.jpeg')
st.sidebar.image(imagem, width=120)

st.sidebar.markdown ('### CURY COMPANY')

st.sidebar.markdown ('## Fastest Delivery in Town')
st.sidebar.markdown ("""---""")

st.write("# Curry Company Growth Dashboard")

st.markdown (" Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.")
st.markdown("""
## Como utilizar esse Growth Dashboard?
- Visão Empresa:
    - Visão Gerencial: Métricas Gerais de Comportamento.
    - Visão Tática: Indicadores Semanais de crescimento.
    - Visão Geográfica: Insights de Geolocalização.
- Visão Entregador:
    - Acompanhamento dos indicadores semanais de crescimento
- Visão Restaurante:
    - Indicadores semanais de crescimento dos restaurantes
""")

st.markdown("""
## Ask for Help 
- gmail: lorenzoquaglio@gmail.com
- LinkedIn: www.linkedin.com/in/lorenzo-quaglio-78919b180
""")

