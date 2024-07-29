# VISÃO DOS RESTAURANTES

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

st.set_page_config(page_title='Visão Restaurantes', page_icon='🏬', layout='wide')

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

def distance (dados, fig):
    if fig == False:
        cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']
        dados['Distance']=dados.loc[:,cols].apply(lambda x: haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1)
        avg_distance = np.round(dados['Distance'].mean(),2)
        return avg_distance
    else:
        cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']
        dados['Distance']=dados.loc[:,cols].apply(lambda x: haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1)                
        avg_distance = dados.loc[:,['City','Distance']].groupby('City').mean().reset_index()
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'],values=avg_distance['Distance'],pull=[0, 0.1, 0])])
        return fig


def avg_std_time_delivery (dados,festival , op):   
                """"
                Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
                Parâmetros:
                    Inputs:
                        - dados: Dataframe com os dados necessários para o cálculo
                        - op: Tipo de operação que precisa ser calculada
                            'avg_time': Calcula o tempo médio
                            'std_time': Calcula o desvio padrão do tempo
                        - festival: Condição com ou sem Festival
                            'Yes': Calcula considerando o festival
                            'No': Calcula desconsiderando o festival
                    Output:
                        - df_aux: Dataframe com 2 colunas e 1 linha
                """          
                df_aux = dados.loc[:,['Time_taken(min)','Festival']].groupby('Festival').agg({'Time_taken(min)':['mean','std']})
                df_aux.columns = ['avg_time','std_time']
                df_aux = df_aux.reset_index()
                df_aux = np.round(df_aux.loc[df_aux['Festival']==festival,op],2)
                return df_aux

def avg_std_time_graph (dados):
    df_aux = dados.loc[:,['City','Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['avg_time','std_time']
    
    df_aux = df_aux.reset_index()
    fig= go.Figure()
    fig.add_trace(go.Bar(name='Control',x=df_aux['City'],y=df_aux['avg_time'],error_y=dict(type='data',array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
    return fig

def avg_std_time_on_traffic(dados):
                df_aux=dados.loc[:,['City','Time_taken(min)','Road_traffic_density']].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean','std']})
                df_aux.columns=['avg_time','std_time']
                df_aux=df_aux.reset_index()
                fig = px.sunburst(df_aux, path=['City','Road_traffic_density'],values='avg_time',color='std_time',color_continuous_scale='RdBu',color_continuous_midpoint=np.average(df_aux['std_time']))
                return fig

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

st.header ("Marketplace - Visão Restaurantes")

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
        col_1, col_2, col_3, col_4, col_5, col_6 = st.columns(6, gap='large')
        
        with col_1:
            delivery_unique = len(dados.loc[:,"Delivery_person_ID"].unique())
            col_1.metric('Entregadores Únicos',delivery_unique)
            
        with col_2:
            avg_distance = distance (dados,fig = False)          
            col_2.metric('A distância média',avg_distance)         
            
        with col_3:
            df_aux = avg_std_time_delivery (dados,'Yes', 'avg_time')
            col_3.metric('Tempo Médio de Entregas c/ Festival', df_aux)

        with col_4:
            df_aux = avg_std_time_delivery (dados,'Yes', 'std_time')
            col_4.metric('STD de Entregas c/ Festival', df_aux)
            
            
        with col_5:
            df_aux = avg_std_time_delivery (dados,'No', 'avg_time')
            col_5.metric('Tempo Médio de Entregas s/ Festival', df_aux)
            
        with col_6:
            df_aux = avg_std_time_delivery (dados,'No', 'std_time')
            col_6.metric('STD de Entregas s/ Festival', df_aux)
        
    with st.container():
        
        col_1, col_2 = st.columns(2, gap='large')
        
        with col_1:
            st.markdown("""---""")
            st.markdown('#  Distribuição do Tempo')            
            fig = avg_std_time_graph (dados)
            st.plotly_chart(fig)    
    
        with col_2:
            st.markdown("""---""")
            st.markdown('# Distribuição da Distância')
            
            cols=['City','Time_taken(min)','Type_of_order']
            df_aux=dados.loc[:,cols].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std']})
            df_aux.columns= ['avg_time','std_time']
            df_aux=df_aux.reset_index()
            st.dataframe(df_aux)
    
    with st.container():
                
        col_1, col_2 = st.columns(2, gap='large')
        
        with col_1:
            st.markdown("""---""")
            st.markdown('# Tempo Médio de Entrega por cidade')
            fig = distance (dados,fig = True) 
            st.plotly_chart(fig) 
             
        with col_2:
            st.markdown("""---""")
            fig = avg_std_time_on_traffic(dados)
            st.plotly_chart(fig) 
