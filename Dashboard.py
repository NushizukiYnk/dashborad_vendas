# Importando bibliotecas
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout = 'wide')

# Criando função para formatacao de numeros
def formata_numero(valor, prefixo = ''):
    # Identifica o valor
    for unidade in ['', 'mil']:
        if valor <1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

# Adicionando um titulo
st.title('DASHBOARD DE VENDAS :shopping_trolley:')

# Criando um df e fazendo leitura do dados
url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul'] # Criando uma lista de filtragem
# Criando Filtros | Filtros por regiao
st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

# Filtro por ano
todos_anos = st.sidebar.checkbox('Dados de todo o periodo', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao':regiao.lower(), 'ano':ano}
response = requests.get(url, params = query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y') # Fazendo a transformacao da coluna Data para datatime

# Filtro para os vendedores
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]


## Tabelas
### Tabelas de receita
# Tabela receita total por estado
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

# Tabela receita mensal
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index() # Pega a frequencia de compras e agrega em uma unica informacao
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

# Tabela receita categorias
receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending = False)

### Tabelas de quantidade de vendas
vendas_categorias = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending = False))

vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].count()).reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

### Tabelas vendedores

vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count'])) 

## Graficos
# receita estado
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat': False, 'lon': False},
                                  title = 'Receita por estado')

# receita mensal
fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers = True,
                             range_y = (0,receita_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita')

# receita estado grafico de barras
fig_receita_estados = px.bar(receita_estados.head(),
                            x = 'Local da compra',
                            y = 'Preço',
                            text_auto = True,
                            title = 'Top estados (receita)')

fig_receita_estados.update_layout(yaxis_title = 'Receita')

# receita categorias
fig_receita_categorias = px.bar(receita_categorias,
                                text_auto = True,
                                title = 'Receita por categoria')

fig_receita_categorias.update_layout(yaxis_title = 'Receita')

# vendas por estado
fig_mapa_vendas = px.scatter_geo(vendas_estados, 
                     lat = 'lat', 
                     lon= 'lon', 
                     scope = 'south america', 
                     #fitbounds = 'locations', 
                     template='seaborn', 
                     size = 'Preço', 
                     hover_name ='Local da compra', 
                     hover_data = {'lat':False,'lon':False},
                     title = 'Vendas por estado',
                     )

# vendas mensais
fig_vendas_mensal = px.line(vendas_mensal, 
              x = 'Mes',
              y='Preço',
              markers = True, 
              range_y = (0,vendas_mensal.max()), 
              color = 'Ano', 
              line_dash = 'Ano',
              title = 'Quantidade de vendas mensal')

fig_vendas_mensal.update_layout(yaxis_title='Quantidade de vendas')

# top 5 vendas estado
fig_vendas_estados = px.bar(vendas_estados.head(),
                             x ='Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top 5 estados'
)

fig_vendas_estados.update_layout(yaxis_title='Quantidade de vendas')

# quantidade de vendas categoria por produto
fig_vendas_categorias = px.bar(vendas_categorias, 
                                text_auto = True,
                                title = 'Vendas por categoria')
fig_vendas_categorias.update_layout(showlegend=False, yaxis_title='Quantidade de vendas')

## Visualizacao no streamlit
# Criando abas
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:
    # Melhorando a visualizacao das metricas
    coluna1, coluna2 = st.columns(2)
    # Criando metricas
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$')) # Soma todos os valoes da coluna Preco
        st.plotly_chart(fig_mapa_receita, use_container_width = True) # Chamando o grafico fig_mapa_receita
        st.plotly_chart(fig_receita_estados, use_container_width = True)# Chamando o grafico fig_receita_estados
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True) # Chamando o grafico fig_receita_mensal
        st.plotly_chart(fig_receita_categorias, use_container_width = True) # Chamando o grafico fig_receita_categorias

with aba2:
    coluna1, coluna2 = st.columns(2)
    
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$')) # Soma todos os valoes da coluna Preco
        st.plotly_chart(fig_mapa_vendas, use_container_width = True)# Chamando o grafico fig_mapa_vendas
        st.plotly_chart(fig_vendas_estados, use_container_width = True) # Chamando o grafico fig_vendas_estados
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width = True) # Chamando o grafico fig_vendas_mensal
        st.plotly_chart(fig_vendas_categorias, use_container_width = True) # Chamando o grafico fig_vendas_categoria

with aba3:
    # Pegando da coluna a quantidade de vendedores             min, max,
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$')) # Soma todos os valoes da coluna Preco
        # Criando o grafico para a receita dos vendedores
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)
                
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        # Criando o grafico para as vendas dos vendedores
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores),
                                        x = 'count',
                                        y = vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_vendas_vendedores)

