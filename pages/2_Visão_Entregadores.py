# VISÃO DOS ENTREGADORES

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

st.set_page_config(page_title='Visão Entregadores', page_icon='🏍', layout='wide')

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
    dados.loc[:,'Road_traffic_density'] = dados.loc[:,'Road_traffic_density'].str.strip()
    dados.loc[:,'ID'] = dados.loc[:,'ID'].str.strip()
    dados.loc[:,'Type_of_order'] = dados.loc[:,'Type_of_order'].str.strip()
    dados.loc[:,'Type_of_vehicle'] = dados.loc[:,'Type_of_vehicle'].str.strip()
    dados.loc[:,'City'] = dados.loc[:,'City'].str.strip()
    dados.loc[:,'Festival'] = dados.loc[:,'Festival'].str.strip()
    
    # Limpeza da coluna de Time Taken
    dados['Time_taken(min)'] = dados['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    dados['Time_taken(min)'] = dados['Time_taken(min)'].astype(int)
    

    # Verificando o tipo de variável em cada coluna
    #print(dados.dtypes)

    # Ver o head do Data Frame

    #st.dataframe(dados)
    return dados

def top_delivers(dados,asc):

    dados_2= dados.loc[:,['Delivery_person_ID','City','Time_taken(min)']].groupby(['City','Delivery_person_ID']).mean().sort_values(['City','Time_taken(min)'], ascending = asc).reset_index()
    df_aux_1 = dados_2.loc[dados_2['City'] == 'Metropolitian',:].head(10)
    df_aux_2 = dados_2.loc[dados_2['City'] == 'Urban',:].head(10)
    df_aux_3 = dados_2.loc[dados_2['City'] == 'Semi-Urban',:].head(10)     
    
    df_2=pd.concat([df_aux_1,df_aux_2,df_aux_3]).reset_index(drop=True)
    
    return df_2


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

st.header ("Marketplace - Visão Entregadores")

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

# Verificando os valores únicos na coluna Road_traffic_density antes do filtro
#st.write(f"Valores únicos antes do filtro de trânsito: {dados['Road_traffic_density'].unique()}")


linhas_selecionadas = dados['Road_traffic_density'].isin(traffic_options)

dados = dados.loc[linhas_selecionadas,:]

# Verificando o resultado do filtro de trânsito
#st.write(f"Linhas após filtro de trânsito: {dados.shape[0]}")
#st.write(f"Valores únicos após o filtro de trânsito: {dados['Road_traffic_density'].unique()}")


#==========================================================================================================
            #LAYOUT NO STREAMLIT
#==========================================================================================================

tab_1, tab_2, tab_3 =  st.tabs(['Visão Gerencial','-','-'])


with tab_1:
    with st.container():
        st.markdown('# Overall Metrics')
        
        col_1, col_2, col_3, col_4 = st.columns(4, gap='large')
        
        with col_1:
            
            # A maior idade dos entregadores
            maior_idade = dados.loc[:,'Delivery_person_Age'].max()
            col_1.metric('Maior Idade', maior_idade)
        
        with col_2:
            
            # A menor idade dos entregadores
            menor_idade = dados.loc[:,'Delivery_person_Age'].min()
            col_2.metric('Menor Idade', menor_idade) 
        
        with col_3:
            
            # A Melhor Condição de Veículos
            melhor_cond = dados.loc[:,'Vehicle_condition'].max()
            col_3.metric('Melhor Condição', melhor_cond)              
            
        with col_4:
            
            # A Pior Condição de Veículos
            pior_cond = dados.loc[:,'Vehicle_condition'].min()
            col_4.metric('Pior Condição', pior_cond) 
    
    with st.container():
        
        st.markdown ("""---""")
        st.markdown('# Avaliações')
        
        col_1, col_2 = st.columns(2, gap='large')
        
        with col_1:
            st.subheader ("Avaliação Média por Entregador")
            df_avg_ratings_per_deliver = (dados.loc[:,['Delivery_person_Ratings','Delivery_person_ID']].groupby('Delivery_person_ID').mean().reset_index())
            st.dataframe(df_avg_ratings_per_deliver)
                    
        with col_2:
            
            st.subheader ("Avaliação Média por Trânsito")
            df_avg_std_ratings_by_traffic = dados.loc[:,['Delivery_person_Ratings','Road_traffic_density']].groupby('Road_traffic_density').agg({'Delivery_person_Ratings':['mean','std']})
            
            # Mudança do Nome das Colunas 
            df_avg_std_ratings_by_traffic.columns = ['Delivery_Mean','Delivery_Std']
            
            # Reset do Index
            df_avg_std_ratings_by_traffic = df_avg_std_ratings_by_traffic.reset_index()
            
            st.dataframe(df_avg_std_ratings_by_traffic)
            
            
            st.subheader ("Avaliação Média por Clima")
            df_avg_std_ratings_by_weather = dados.loc[:,['Delivery_person_Ratings','Weatherconditions']].groupby('Weatherconditions').agg({'Delivery_person_Ratings':['mean','std']})
            
            # Mudança do Nome das Colunas 
            df_avg_std_ratings_by_weather.columns = ['Delivery_Mean','Delivery_Std']
            
            # Reset do Index
            df_avg_std_ratings_by_weather = df_avg_std_ratings_by_weather.reset_index()
            
            st.dataframe(df_avg_std_ratings_by_weather)
            
            
    with st.container():
         
        st.markdown ("""---""")
        st.markdown('# Velocidade de Entrega')
        
        col_1, col_2 = st.columns(2, gap='large')
        
        with col_1:
            st.subheader("Top Entregadores mais Rápidos")
            df_2 = top_delivers(dados,asc=True) 
            st.dataframe(df_2)

        
        
        with col_2:
            st.subheader ("Top Entregadores mais Lentos")
            df_2 = top_delivers(dados,asc=False)  
            st.dataframe(df_2)
            
                
            
            
            