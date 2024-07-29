# VISÃO DA EMPRESA

# Importing Libraries

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import folium
from PIL import Image
from datetime import datetime
from streamlit_folium import folium_static
from haversine import haversine

st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide')

#==========================================================================================================
            # FUNÇÕES
#==========================================================================================================
def clean_code(dados):
    
    """ Esta função tem a responsabilidade de limpar o Dataframe 
    
        Tipos de Limpeza:
        1. Remoção dos dados Nan
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5 .Limpeza da coluna de tempo (remoção do texto da variável numérica) 
        
        Input: Dataframe
        Output: Dataframe
    """

    # Substituindo valores 'NaN' por valores de notação padrão do pandas (ou numpy)
    dados.replace('NaN ', np.nan, inplace=True)

    # Convertendo a coluna Age de texto para número/int
    dados['Delivery_person_Age'] = pd.to_numeric(dados['Delivery_person_Age'], errors='coerce')
    dados.dropna(subset=['Delivery_person_Age'], inplace=True)
    dados['Delivery_person_Age'] = dados['Delivery_person_Age'].astype(int)

    # Convertendo a coluna Rate de texto para float
    dados['Delivery_person_Ratings'] = pd.to_numeric(dados['Delivery_person_Ratings'], errors='coerce')
    dados.dropna(subset=['Delivery_person_Ratings'], inplace=True)
    dados['Delivery_person_Ratings'] = dados['Delivery_person_Ratings'].astype(float)

    # Convertendo a coluna Order_Date de texto para data
    dados['Order_Date'] = pd.to_datetime(dados['Order_Date'], format='%d-%m-%Y', errors='coerce')
    dados.dropna(subset=['Order_Date'], inplace=True)

    # Convertendo a coluna Multiple_Deliveries de texto para número/int
    dados['multiple_deliveries'] = pd.to_numeric(dados['multiple_deliveries'], errors='coerce')
    dados.dropna(subset=['multiple_deliveries'], inplace=True)
    dados['multiple_deliveries'] = dados['multiple_deliveries'].astype(int)

    # Remover espaços extras nas colunas de texto
    dados['Road_traffic_density'] = dados['Road_traffic_density'].str.strip()

    # Verificando o tipo de variável em cada coluna
    #print(dados.dtypes)

    # Ver o head do Data Frame

    #st.dataframe(dados)
    return dados

def order_metric(dados):
    # Colunas que desejo trabalhar

    cols = ['ID','Order_Date']

    # Seleção das Linhas

    exerc_1 = dados.loc[:,cols].groupby('Order_Date').count().reset_index()

    # Fazer o gráfico de linhas a partir da biblioteca Plotly
    
    fig_1 =px.bar(exerc_1,x='Order_Date',y='ID')
    return fig_1

def traffic_order_share (dados):

    #3. Distribuição dos Pedidos por Tipo de Tráfego

    df_aux = dados.loc[:,['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()

    df_aux['pct']=(df_aux['ID']/df_aux['ID'].sum())*100

    fig_3 = px.pie(df_aux,values='pct', names='Road_traffic_density')
    return fig_3

def traffic_order_city(dados):
    #4. Comparação do Volume de Pedidos por cidade e tipo de tráfego

    df_aux = dados.loc[:,['ID','City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()

    fig_4 = px.scatter(df_aux, x='City',y='Road_traffic_density',size='ID')
    return fig_4

def order_by_week (dados):

    # Criar a coluna de semana

    dados['week_of_year']=dados['Order_Date'].dt.strftime('%U')

    dados_aux = dados.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()

    dados_aux.head()
    
        
    # Gráficos de Barra e Linha

    #px.bar(dados_aux, x='week_of_year',y='ID')

    #px.line(dados_aux, x='week_of_year',y='ID')

    # Gráficos de Barra e Linha
    fig_2 = go.Figure()

    # Adicionar barras
    fig_2.add_trace(go.Bar(
        x=dados_aux['week_of_year'],
        y=dados_aux['ID'],
        name='Pedidos por Semana',
        marker_color='lightblue',
        opacity=0.6
    ))

    # Adicionar linha de tendência
    fig_2.add_trace(go.Scatter(
        x=dados_aux['week_of_year'],
        y=dados_aux['ID'],
        mode='lines+markers',
        name='Linha de Tendência',
        line=dict(color='red', width=2)
    ))

    # Atualizar layout
    fig_2.update_layout(
        title='Quantidade de Pedidos por Semana',
        xaxis_title='Semana do Ano',
        yaxis_title='Quantidade de Pedidos',
        barmode='overlay'
    )
    return fig_2
      
def order_share_by_week (dados):
    #5. A quantidade de pedidos por entregador por semana

    # Quantidade de pedidos por semana / Número único de Entregadores por semana
    
    dados['week_of_year']=dados['Order_Date'].dt.strftime('%U')

    dados_aux = dados.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()

    df_aux1 = dados.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()

    df_aux2 = dados.loc[:,['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()

    df_aux= pd.merge(df_aux1,df_aux2, how= 'inner')

    df_aux['order_by_deliver']=df_aux['ID']/df_aux['Delivery_person_ID']

    px.line(df_aux,x='week_of_year',y='order_by_deliver')
    

    # Gráficos de Barra e Linha
    fig_5 = go.Figure()

    # Adicionar barras
    fig_5.add_trace(go.Bar(
        x=dados_aux['week_of_year'],
        y=df_aux['order_by_deliver'],
        name='Pedidos por Entregadores Únicos',
        marker_color='lightblue',
        opacity=0.6
    ))

    # Adicionar linha de tendência
    fig_5.add_trace(go.Scatter(
        x=dados_aux['week_of_year'],
        y=df_aux['order_by_deliver'],
        mode='lines+markers',
        name='Linha de Tendência',
        line=dict(color='red', width=2)
    ))

    # Atualizar layout
    fig_5.update_layout(
        title='Quantidade de Pedidos por Entregador por Semana',
        xaxis_title='Semana do Ano',
        yaxis_title='Quantidade de Pedidos por Entregadores',
        barmode='overlay'
    )
    return fig_5

def country_maps (dados):
    #6. A localização central de cada cidade por tipo de tráfego

    df_aux = dados.loc[:,['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()

    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],location_info['Delivery_location_longitude']], popup=location_info[['City','Road_traffic_density']]).add_to(map)

    folium_static(map, width = 1024, height = 600)
    return None
#==========================================================================================================
            # INÍCIO DA ESTRUTURA LÓGICA DO CÓDIGO
#==========================================================================================================

# -----------------------------------------
# Carregar o DataFrame
# -----------------------------------------

dados = pd.read_csv('pages/train.csv')

# -----------------------------------------
# Limpeza de Dados
# -----------------------------------------

dados = clean_code (dados)


#==========================================================================================================
            #BARRA LATERAL NO STREAMLIT
#==========================================================================================================
st.header ("Marketplace - Visão Empresa")


imagem = Image.open('profile_image.jpeg')
st.sidebar.image (imagem, width = 120)

st.sidebar.markdown ('### CURY COMPANY')

st.sidebar.markdown ('## Fastest Delivery in Town')
st.sidebar.markdown ("""---""")

st.sidebar.markdown ('## Selecione uma data limite')
date_slider = st.sidebar.slider('Até qual valor?',value=datetime(2022,4,13),min_value=datetime(2022,2,11),max_value=datetime(2022,4,6),format='DD-MM-YYYY')

st.sidebar.markdown ("""---""")

traffic_options = st.sidebar.multiselect( "Quais as condições do trânsito?", ['Low','Medium','High','Jam'], default = ['Low','Medium','High','Jam'])
st.sidebar.markdown ("""---""")

st.sidebar.markdown ('### Powered by Lorenzo Quaglio')

# FILTRO DE DATA

linhas_selecionadas = dados['Order_Date'] < date_slider

dados = dados.loc[linhas_selecionadas,:]

# FILTRO DE TRÂNSITO

linhas_selecionadas = dados['Road_traffic_density'].isin(traffic_options)

dados = dados.loc[linhas_selecionadas,:]



#==========================================================================================================
            #LAYOUT NO STREAMLIT
#==========================================================================================================

tab_1, tab_2, tab_3 =  st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab_1:
    with st.container():
        # ORDER METRIC
        fig_1= order_metric(dados)
        st.markdown('# Orders by Day')
        st.plotly_chart (fig_1 , use_container_width = True)
        st.markdown ("""---""") 
    
    
    with st.container():    
        col_1, col_2 = st.columns(2)
        
        with col_1:
            fig_3 = traffic_order_share (dados)   
            st.markdown('# Traffic Order Share')
            st.plotly_chart (fig_3, use_container_width = True)
       
        
        with col_2:
            fig_4 = traffic_order_city(dados)
            st.markdown('# Traffic Order City')
            st.plotly_chart (fig_4, use_container_width = True)   

with tab_2:
    
    with st.container():
        st.markdown ("# Order by Week")
        fig_2 = order_by_week (dados)
        st.plotly_chart (fig_2, use_container_width = True)

       

    
    with st.container():
        
        st.markdown ("# Order Share by Week")
        fig_5 = order_share_by_week (dados)
        st.plotly_chart (fig_5, use_container_width = True)
    
    
with tab_3:
    st.markdown ("# Country Maps")
    country_maps(dados)

    



























