import pandas as pd
from datetime import datetime, timedelta
import time
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.grid import grid
import locale
import plotly.express as px
# Configura o locale para o Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

st.set_page_config(layout='wide')
st.title("Relatório de Performance")    

registro_df = pd.read_excel(r"COMPANHIA BARBER 2.xlsx", sheet_name='Registro')

# preco_formato_preco = locale.currency(acao_preco, grouping=True)
# compra_formato_preco = locale.currency(acao_compra_preco, grouping=True)
# venda_formato_preco = locale.currency(acao__venda_preco, grouping=True)

tipo = registro_df['Tipo']
tipo.dropna(inplace=True)
tipo.drop_duplicates(inplace=True)
tipo = tipo.values.tolist()
tipo_com_vazio = ['Selecione'] + tipo

registro_df['Data de Registro'] = pd.to_datetime(registro_df['Data de Registro'])
registro_df["Data de Pagamento"] = pd.to_datetime(registro_df['Data de Pagamento'])
registro_df['Mês - Ano'] = registro_df['Data de Registro'].dt.strftime("%B %Y").str.capitalize()
registro_df["Data"] = pd.to_datetime(registro_df["Mês - Ano"], format="%B %Y", errors='coerce')

# Ordenando os dados por data
registro_df = registro_df.sort_values(by="Data de Registro")
registro_df["Despesas Vendas Máquinas"] = registro_df["Despesas Vendas Máquinas"].fillna(0)

# Criando a coluna de Valor Ajustado (Descontando maquininha e transformando despesas em negativas)
registro_df["Valor Ajustado"] = registro_df.apply(lambda row: row["Valor Atualizado2"] - row["Despesas Vendas Máquinas"] 
                                if row["Tipo"] == "Receitas" else -row["Valor Atualizado2"], axis=1)
ajuste_fluxo = 1673.24
registro_df.at[0, 'Valor Ajustado'] += ajuste_fluxo 

# Criando a coluna de Saldo Acumulado
registro_df["Saldo Acumulado"] = registro_df["Valor Ajustado"].cumsum()

# Formatando a coluna 'Saldo Acumulado' para valores no formato brasileiro
registro_df["Saldo Formatado"] = registro_df["Saldo Acumulado"].apply(
    lambda x: locale.currency(x, grouping=True, symbol="R$ ")
)
nome_produtos = registro_df[(registro_df['Tipo'] == "Receitas") & (registro_df['Entrada/Saída'] == "Produtos")].groupby([ 'Categoria',])['Valor Unitário'].sum().reset_index()


serviços_receitas = registro_df[(registro_df['Tipo'] == "Receitas") & (registro_df['Entrada/Saída'] == "Serviços") | (registro_df['Entrada/Saída'] == "Combos")].groupby(['Mês/Ano Pag', 'Categoria', 'Mês - Ano', "Data"])['Valor Unitário'].sum().reset_index()

# Aplica o estilo CSS globalmente
st.markdown("""
    <style>
    /* Limita a altura total da caixa de multiselect */
    div[data-baseweb="select"] {
        max-height: 60px;
        overflow-y: auto;
    }

    /* Limita a área das opções selecionadas */
    div[data-baseweb="tag"] {
        max-height: 1.2em;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* Adiciona rolagem se necessário */
    div[role="listbox"] {
        max-height: 150px;
        overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("Filtros")
    sel_tipo = st.sidebar.selectbox("", tipo_com_vazio)



# Página Inicial
    # Receitas
receitas = registro_df[registro_df['Tipo'] == "Receitas"].groupby(['Mês/Ano Pag', 'Entrada/Saída'])['Valor Unitário'].sum().reset_index()
receitas_mes = registro_df[registro_df['Tipo'] == "Receitas"].groupby(['Tipo', 'Mês/Ano Pag', 'Data'])['Valor Unitário'].sum().reset_index()
receitas_mes = receitas_mes.sort_values("Data")
receitas_atual = receitas_mes['Valor Unitário'].iloc[-1]
receitas_atual_forma = locale.currency(receitas_atual, grouping=True)

    #Despesas
despesas = registro_df[registro_df['Tipo'] == "Despesas"].groupby(['Mês/Ano Pag', 'Entrada/Saída'])['Valor Unitário'].sum().reset_index()
despesas_mes = registro_df[registro_df['Tipo'] == "Despesas"].groupby(['Tipo', 'Mês/Ano Pag',"Data"])['Valor Unitário'].sum().reset_index()
despesas_mes = despesas_mes.sort_values("Data")
despesas_atual = despesas_mes['Valor Unitário'].iloc[-1]
despesas_atual_forma = locale.currency(despesas_atual, grouping=True)
    #  Saldo Atual
saldo_atual = receitas_atual - despesas_atual
saldo_atual_forma = locale.currency(saldo_atual, grouping=True)

# Mês 
meses_ano = registro_df['Mês - Ano']
meses_ano.dropna(inplace=True)
meses_ano.drop_duplicates(inplace=True)
meses_atual = meses_ano.iloc[-1]

mygrid = grid(1,1,1,1,  vertical_align = "top")
c = mygrid.container(border= True)
c.subheader(meses_atual, divider='orange')
colA, colB, colC, colD, colE, colF = c.columns(6, vertical_alignment="center")


colA.image(r'imagens\Dinheiro Verde.png', width=75)
#colB.metric("Receitas", receitas_atual_forma)
colB.markdown(f'<p class="metric-text">Receitas</p>', unsafe_allow_html=True)
colB.markdown(f'<p class="metric-value">{receitas_atual_forma}</p>', unsafe_allow_html=True)
# colC.markdown(f'<p class="metric-text">Compra</p>', unsafe_allow_html=True)
# colC.markdown(f'<p class="metric-value">{compra_formato_preco}</p>', unsafe_allow_html=True)
colC.image(r'Dinheiro vermelho.png', width=75)
colD.markdown(f'<p class="metric-text">Despesas</p>', unsafe_allow_html=True)
colD.markdown(f'<p class="metric-value">{despesas_atual_forma}</p>', unsafe_allow_html=True)
colE.image(r'imagens\saldo.png', width=75)
colF.markdown(f'<p class="metric-text">Saldo Atual</p>', unsafe_allow_html=True)
colF.markdown(f'<p class="metric-value">{saldo_atual_forma}</p>', unsafe_allow_html=True)


# FLUXO DE CAIXA



# st.text("Fluxo de Caixa")

# # Criar o gráfico com a coluna numérica para o eixo y
# fig = px.line(registro_df, x="Data de Registro", y="Saldo Acumulado",
#               labels={"Saldo Acumulado": "Saldo Acumulado (R$)", "Data de Registro": "Data"},
#               line_shape="linear")


# # Adicionar a linha com o valor formatado no gráfico
# fig.update_traces(
#     text=registro_df["Saldo Formatado"],  # Exibe os valores formatados como texto
#     textposition="top center",            # Posiciona os valores em cima dos pontos da linha
#     hovertemplate='%{text}'                # Quando passar o mouse, mostra os valores formatados
# )

# # Adicionar um marcador grande no último valor com a formatação correta
# ultimo_ponto = registro_df.iloc[-1]
# fig.add_scatter(x=[ultimo_ponto["Data de Registro"]], y=[ultimo_ponto["Saldo Acumulado"]],
#                 mode="markers+text", 
#                 text=[locale.currency(ultimo_ponto["Saldo Acumulado"], grouping=True, symbol="R$ ")],
#                 textposition="top center", marker=dict(size=12, color="orange", symbol="circle"),
#                 showlegend=False)

# # Formatar o eixo Y para o padrão brasileiro (milhares com ponto, decimais com vírgula)
# fig.update_layout(
#     yaxis_tickformat = "R$,.2f",  # Formato com ponto para milhar e vírgula para decimal
#     yaxis_tickprefix = "R$ ",      # Prefixo R$ no eixo Y
#     xaxis_title="",
#     yaxis_title="",
#     hovermode="x", 
#     template="plotly_dark"
# )
# fig.update_traces(line=dict(color="darkorange"), marker=dict(size=8))

# st.plotly_chart(fig)

st.divider()

Col1, Col2 = st.columns(2,vertical_alignment="center")
Col3, Col4 = st.columns(2,vertical_alignment="center")
Col5, Col6 = st.columns(2,vertical_alignment="center")


# RECEITAS E DESPESAS

Col1.text('Receitas')
Col2.text('Despesas')

#### -------------------------------> RECEITAS SERVIÇOS PRESTADOS - TIPOS


tipo_receitas = registro_df[registro_df['Tipo'] == "Receitas"].groupby(['Mês/Ano Pag', 'Entrada/Saída', 'Mês - Ano', 'Data'])['Valor Unitário'].sum().reset_index()
tipo_receitas = tipo_receitas.sort_values("Data")
tipo_receitas_atual = tipo_receitas.loc[tipo_receitas['Mês - Ano'] == meses_atual]

receitas_selecionadas = Col3.multiselect(
        "",
        options=tipo_receitas['Entrada/Saída'].unique(),
        default=tipo_receitas['Entrada/Saída'].unique()

    )

tipo_receitas_filtro = tipo_receitas[tipo_receitas['Entrada/Saída'].isin(receitas_selecionadas)]

    # Recalcular a soma total por mês
tipo_receitas_agg = tipo_receitas_filtro.groupby(['Mês - Ano', 'Data'])['Valor Unitário'].sum().reset_index()
tipo_receitas_agg = tipo_receitas_agg.sort_values("Data")
tipo_receitas_agg ['Variação (%)'] = tipo_receitas_agg ['Valor Unitário'].pct_change() * 100

fig_receitas = px.bar(tipo_receitas_filtro, x = 'Mês - Ano', y = 'Valor Unitário', color ='Entrada/Saída', text='Valor Unitário',color_discrete_sequence=px.colors.sequential.Greens_r)


# Adicionar os valores totais acima das barras
for i, row in tipo_receitas_agg.iterrows():
    valor_formatado = f"R$ {row['Valor Unitário']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")  # <br> quebra de linha # Formato R$ 1.000,00
    variacao_formatada = f"{row['Variação (%)']:.1f}%"

    fig_receitas.add_annotation(
        x=row['Mês - Ano'],  # Posiciona no mês correspondente
        y=row['Valor Unitário'],  # Altura da soma total
        text=f"{valor_formatado}<br>{variacao_formatada}", 
        showarrow=False,
        font=dict(size=12, color="white"),
        xanchor="center",
        yshift=30  # Desloca o texto para cima das barras
    )


fig_receitas.update_layout(
    yaxis_tickformat = "R$.,2f",  # Formato com ponto para milhar e vírgula para decimal
    yaxis_tickprefix = "R$ ",      # Prefixo R$ no eixo Y
    xaxis_title="",
    yaxis_title="",
    hovermode="x", 
    template="plotly_dark"
)                      

fig_receitas.update_traces(texttemplate='R$ %{text:,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."),
    textposition='inside')
                   
Col5.plotly_chart(fig_receitas)


###### --------------------------------------->  Despesas Categorias 
tipo_despesas = registro_df[registro_df['Tipo'] == "Despesas"].groupby(['Mês/Ano Pag', 'Entrada/Saída', 'Mês - Ano', 'Data'])['Valor Unitário'].sum().reset_index()
tipo_despesas = tipo_despesas.sort_values("Data")
tipo_despesas_atual = tipo_despesas.loc[tipo_despesas['Mês - Ano'] == meses_atual]

despesas_selecionadas = Col4.multiselect(
        "",
        options=tipo_despesas['Entrada/Saída'].unique(),
        default=tipo_despesas['Entrada/Saída'].unique()

    )

tipo_despesas_filtro = tipo_despesas[tipo_despesas['Entrada/Saída'].isin(despesas_selecionadas)]
tipo_despesas_filtro['Texto'] = tipo_despesas_filtro['Valor Unitário'].apply(
    lambda v: f'R$ {v:,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".") if v >= 1 else '')

    # Recalcular a soma total por mês
tipo_despesas_agg = tipo_despesas_filtro.groupby(['Mês - Ano', 'Data'])['Valor Unitário'].sum().reset_index()
tipo_despesas_agg = tipo_despesas_agg.sort_values("Data")
tipo_despesas_agg['Variação (%)'] = tipo_despesas_agg ['Valor Unitário'].pct_change() * 100

fig_despesas = px.bar(tipo_despesas_filtro, 
                      x = 'Mês - Ano', 
                      y = 'Valor Unitário', 
                      color ='Entrada/Saída',
                      text="Texto",
                      color_discrete_sequence=px.colors.sequential.Reds_r)

# Adicionar os valores totais acima das barras
for i, row in tipo_despesas_agg.iterrows():
    valor_formatado = f"R$ {row['Valor Unitário']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")  # <br> quebra de linha # Formato R$ 1.000,00
    variacao_formatada = f"{row['Variação (%)']:.1f}%"

    fig_despesas.add_annotation(
        x=row['Mês - Ano'],  # Posiciona no mês correspondente
        y=row['Valor Unitário'],  # Altura da soma total
        text=f"{valor_formatado}<br>{variacao_formatada}", 
        showarrow=False,
        font=dict(size=12, color="white"),
        xanchor="center",
        yshift=30  # Desloca o texto para cima das barras
    )

fig_despesas.update_layout(
    yaxis_tickformat = "R$.,2f",  # Formato com ponto para milhar e vírgula para decimal
    yaxis_tickprefix = "R$ ",      # Prefixo R$ no eixo Y
    xaxis_title="",
    yaxis_title="",
    hovermode="x", 
    template="plotly_dark"
)  

fig_despesas.update_traces(
    texttemplate='%{text}',
    textposition='inside')

Col6.plotly_chart(fig_despesas)


st.divider()


#### -------------------------------> SERVIÇOS PRESTADOS - TIPOS 

st.markdown("<h2 style='text-align: center;'>Serviços</h2>", unsafe_allow_html=True)

# Serviços
serviços_receitas = registro_df[(registro_df['Tipo'] == "Receitas") & (registro_df['Entrada/Saída'] == "Serviços") | (registro_df['Entrada/Saída'] == "Combos")].groupby(['Mês/Ano Pag', 'Categoria', 'Mês - Ano', "Data"])['Valor Unitário'].sum().reset_index()
serviços_receitas = serviços_receitas.sort_values("Data")

categorias_selecionadas = st.multiselect(
        "",
        options=serviços_receitas['Categoria'].unique(),
        default=serviços_receitas['Categoria'].unique()
    )

# Filtrar os dados com base nas categorias selecionadas
    # Serviços
servicos_filtro = serviços_receitas[serviços_receitas['Categoria'].isin(categorias_selecionadas)]
servicos_agg = servicos_filtro.groupby(['Mês - Ano', "Data"])['Valor Unitário'].sum().reset_index()
servicos_agg =  servicos_agg.sort_values("Data")
servicos_agg['Variação (%)'] = servicos_agg['Valor Unitário'].pct_change() * 100



# Criar coluna de texto formatado
servicos_filtro['Texto'] = servicos_filtro['Valor Unitário'].apply(
    lambda v: f'R$ {v:,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".") if v >= 1 else '')

# Criar o gráfico de barras
fig_servicos = px.bar(
    servicos_filtro,
    y='Valor Unitário',
    x='Mês - Ano',
    color='Categoria',
    text='Texto',
    color_discrete_sequence=px.colors.sequential.YlGn_r
)

# Adicionar anotações para mostrar a soma total de cada mês
for i, row in servicos_agg.iterrows():
    valor_formatado = f"R$ {row['Valor Unitário']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")  # <br> quebra de linha # Formato R$ 1.000,00
    variacao_formatada = f"{row['Variação (%)']:.1f}%"

    fig_servicos.add_annotation(
        x=row['Mês - Ano'],  # Posiciona no mês correspondente
        y=row['Valor Unitário'],  # Altura da soma total
        text=f"{valor_formatado}<br>{variacao_formatada}", 
        showarrow=False,
        font=dict(size=12, color="white"),
        xanchor="center",
        yshift=30  # Desloca o texto para cima das barras
    )


fig_servicos.update_layout(
    xaxis_tickformat = ".,2f",  # Formato com ponto para milhar e vírgula para decimal
    xaxis_title="",
    yaxis_title="",
    hovermode="x", 
    template="plotly_dark"
) 

fig_servicos.update_traces(
    texttemplate='%{text}',
    textposition='inside')

# Exibir o gráfico
st.plotly_chart(fig_servicos)

#### -------------------------------------> SERVIÇOS PRESTADOS QUANTIDADES - TIPOS 

servicos_qtd = registro_df[(registro_df['Tipo'] == "Receitas") & (registro_df['Entrada/Saída'] == "Serviços") | (registro_df['Entrada/Saída'] == "Combos")].groupby(['Mês/Ano Pag', 'Categoria', 'Mês - Ano','Data'])['Valor Unitário'].count().reset_index()
servicos_qtd = servicos_qtd.sort_values("Data")
servicos_qtd_filtro = servicos_qtd[servicos_qtd['Categoria'].isin(categorias_selecionadas)]
servicos_qtd_agg = servicos_qtd_filtro.groupby(['Mês - Ano', 'Data'])['Valor Unitário'].sum().reset_index()
servicos_qtd_agg =  servicos_qtd_agg.sort_values("Data")
servicos_qtd_agg['Variação (%)'] = servicos_qtd_agg['Valor Unitário'].pct_change() * 100
# Criar coluna de texto formatado
servicos_qtd_filtro['Texto'] = servicos_qtd_filtro['Valor Unitário']

st.markdown("<h4 style='text-align: center;'>Quantiade de Serviços Prestados</h4>", unsafe_allow_html=True)

# Criar o gráfico de barras
fig_servicos_qtd = px.bar(
    servicos_qtd_filtro,
    y='Valor Unitário',
    x='Mês - Ano',
    color='Categoria',
    text='Texto',
    color_discrete_sequence=px.colors.sequential.YlGn_r
)

# Adicionar anotações para mostrar a soma total de cada mês
for i, row in servicos_qtd_agg.iterrows():
    valor_formatado = f"{row['Valor Unitário']:,.0f}"  # <br> quebra de linha # Formato R$ 1.000,00
    variacao_formatada = f"{row['Variação (%)']:.1f}%"

    fig_servicos_qtd.add_annotation(
        x=row['Mês - Ano'],  # Posiciona no mês correspondente
        y=row['Valor Unitário'],  # Altura da soma total
        text=f"{valor_formatado}<br>{variacao_formatada}", 
        showarrow=False,
        font=dict(size=12, color="white"),
        xanchor="center",
        yshift=30  # Desloca o texto para cima das barras
    )


fig_servicos_qtd.update_layout(
    xaxis_tickformat = ".,2f",  # Formato com ponto para milhar e vírgula para decimal
    xaxis_title="",
    yaxis_title="",
    hovermode="x", 
    template="plotly_dark"
) 

fig_servicos_qtd.update_traces(
    texttemplate='%{text}',
    textposition='inside')

# Exibir o gráfico
st.plotly_chart(fig_servicos_qtd)
st.divider()


#### -------------------------------------> PRODUTOS VENDIDOS - 
st.markdown("<h2 style='text-align: center;'>Produtos Vendidos</h2>", unsafe_allow_html=True)

# Modulação e tratamento de Dados
produtos_receitas = registro_df[(registro_df['Tipo'] == "Receitas") & (registro_df['Entrada/Saída'] == "Produtos")].groupby(['Mês/Ano Pag', 'Categoria', 'Mês - Ano','Data'])['Valor Unitário'].sum().reset_index()
produtos_receitas = produtos_receitas.sort_values("Data")
produtos_selecionadas = st.multiselect(
        label="",  # espaço em branco para não aparecer título
        options=produtos_receitas['Categoria'].unique(),
        default=produtos_receitas['Categoria'].unique()
    )
produtos_filtro = produtos_receitas[produtos_receitas['Categoria'].isin(produtos_selecionadas)]
produtos_agg = produtos_filtro.groupby(['Mês - Ano', "Data"])['Valor Unitário'].sum().reset_index()
produtos_agg =  produtos_agg.sort_values("Data")
produtos_agg['Variação (%)'] = produtos_agg['Valor Unitário'].pct_change() * 100
produtos_filtro['Texto'] = produtos_filtro['Valor Unitário'].apply(
    lambda v: f'R$ {v:,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".") if v >= 1 else '')

Col7, Col8 = st.columns(2,vertical_alignment="center")

# Criar o gráfico de barras
fig_produtos = px.bar(
    produtos_filtro,
    y='Valor Unitário',
    x='Mês - Ano',
    color='Categoria',
    text='Texto',
    color_discrete_sequence=px.colors.sequential.YlGn_r
)

# Adicionar anotações para mostrar a soma total de cada mês
for i, row in produtos_agg.iterrows():
    valor_formatado = f"R$ {row['Valor Unitário']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")  # <br> quebra de linha # Formato R$ 1.000,00
    variacao_formatada = f"{row['Variação (%)']:.1f}%"

    fig_produtos.add_annotation(
        x=row['Mês - Ano'],  # Posiciona no mês correspondente
        y=row['Valor Unitário'],  # Altura da soma total
        text=f"{valor_formatado}<br>{variacao_formatada}", 
        showarrow=False,
        font=dict(size=12, color="white"),
        xanchor="center",
        yshift=30  # Desloca o texto para cima das barras
    )

fig_produtos.update_layout(
    xaxis_tickformat = ".,2f",  # Formato com ponto para milhar e vírgula para decimal
    xaxis_title="",
    yaxis_title="",
    hovermode="x", 
    template="plotly_dark"
) 
fig_produtos.update_traces(
    texttemplate='%{text}',
    textposition='inside')

Col7.plotly_chart(fig_produtos)


#### -------------------------------------> PRODUTOS VENDIDOS QUANTIDADE - 
produtos_qtd = registro_df[(registro_df['Tipo'] == "Receitas") & (registro_df['Entrada/Saída'] == "Produtos")].groupby(['Mês/Ano Pag', 'Categoria', 'Mês - Ano', 'Data'])['Valor Unitário'].count().reset_index()
produtos_qtd = produtos_qtd.sort_values("Data")
produtos_qtd_filtro = produtos_qtd[produtos_receitas['Categoria'].isin(produtos_selecionadas)]
produtos_qtd_agg = produtos_qtd_filtro.groupby(['Mês - Ano', "Data"])['Valor Unitário'].sum().reset_index()
produtos_qtd_agg =  produtos_qtd_agg.sort_values("Data")
produtos_qtd_agg['Variação (%)'] = produtos_qtd_agg['Valor Unitário'].pct_change() * 100
produtos_qtd_filtro['Texto'] = produtos_qtd_filtro['Valor Unitário']
# Criar o gráfico de barras
fig_produtos_qtd = px.bar(
    produtos_qtd_filtro,
    y='Valor Unitário',
    x='Mês - Ano',
    color='Categoria',
    text='Texto',
    color_discrete_sequence=px.colors.sequential.YlGn_r
)

# Adicionar anotações para mostrar a soma total de cada mês
for i, row in produtos_qtd_agg.iterrows():
    valor_formatado = f"{row['Valor Unitário']:,.0f}" 
    variacao_formatada = f"{row['Variação (%)']:.1f}%"

    fig_produtos_qtd.add_annotation(
        x=row['Mês - Ano'],  # Posiciona no mês correspondente
        y=row['Valor Unitário'],  # Altura da soma total
        text=f"{valor_formatado}<br>{variacao_formatada}", 
        showarrow=False,
        font=dict(size=12, color="white"),
        xanchor="center",
        yshift=30  # Desloca o texto para cima das barras
    )

fig_produtos_qtd.update_layout(
    xaxis_tickformat = ".,2f",  # Formato com ponto para milhar e vírgula para decimal
    xaxis_title="",
    yaxis_title="",
    hovermode="x", 
    template="plotly_dark"
) 

fig_produtos_qtd.update_traces(
    texttemplate='%{text}',
    textposition='inside')

Col8.plotly_chart(fig_produtos_qtd)

st.divider()


#### ----------------------------------------------> DESPESAS TIPOS - 

st.markdown("<h2 style='text-align: center;'>Despesas</h2>", unsafe_allow_html=True)
Col9, Col10 = st.columns(2,vertical_alignment="center")
Col11, Col12 = st.columns(2,vertical_alignment="center")
Col13, Col14 = st.columns(2,vertical_alignment="center")
Col15, Col16 = st.columns(2,vertical_alignment="center")


#### ------------------------------> DESPESAS FIXAS
despesas_fixas = registro_df[(registro_df['Tipo'] == "Despesas") & (registro_df['Entrada/Saída'] == "Fixas")].groupby(['Mês/Ano Pag', 'Categoria', 'Mês - Ano', "Data"])['Valor Unitário'].sum().reset_index()
despesas_fixas = despesas_fixas.sort_values("Data")

fixas_selecionadas = Col9.multiselect(
        label="Despesas Fixas",  # espaço em branco para não aparecer título
        options=despesas_fixas['Categoria'].unique(),
        default=despesas_fixas['Categoria'].unique()
    )

despesas_fixas_filtro = despesas_fixas[despesas_fixas['Categoria'].isin(fixas_selecionadas)]
despesas_fixas_agg = despesas_fixas_filtro.groupby(['Mês - Ano', "Data"])['Valor Unitário'].sum().reset_index()
despesas_fixas_agg =  despesas_fixas_agg.sort_values("Data")
despesas_fixas_agg['Variação (%)'] = despesas_fixas_agg['Valor Unitário'].pct_change() * 100
despesas_fixas_filtro['Texto'] = despesas_fixas_filtro['Valor Unitário'].apply(
    lambda v: f'R$ {v:,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".") if v >= 1 else '')



# Criar o gráfico de barras
fig_fixas = px.bar(
    despesas_fixas_filtro,
    y='Valor Unitário',
    x='Mês - Ano',
    color='Categoria',
    text='Texto',
    color_discrete_sequence=px.colors.sequential.YlOrRd_r
)

# Adicionar anotações para mostrar a soma total de cada mês
for i, row in despesas_fixas_agg.iterrows():
    valor_formatado = f"R$ {row['Valor Unitário']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")  # <br> quebra de linha # Formato R$ 1.000,00
    variacao_formatada = f"{row['Variação (%)']:.1f}%"

    fig_fixas.add_annotation(
        x=row['Mês - Ano'],  # Posiciona no mês correspondente
        y=row['Valor Unitário'],  # Altura da soma total
        text=f"{valor_formatado}<br>{variacao_formatada}", 
        showarrow=False,
        font=dict(size=12, color="white"),
        xanchor="center",
        yshift=30  # Desloca o texto para cima das barras
    )

fig_fixas.update_layout(
    xaxis_tickformat = ".,2f",  # Formato com ponto para milhar e vírgula para decimal
    xaxis_title="",
    yaxis_title="",
    hovermode="x", 
    template="plotly_dark"
) 
fig_fixas.update_traces(
    texttemplate='%{text}',
    textposition='inside')

Col11.plotly_chart(fig_fixas)


#### ------------------------------> DESPESAS VARIÁVEIS
despesas_variaveis = registro_df[(registro_df['Tipo'] == "Despesas") & (registro_df['Entrada/Saída'] == "Variáveis")].groupby(['Mês/Ano Pag', 'Categoria', 'Mês - Ano', "Data"])['Valor Unitário'].sum().reset_index()
despesas_variaveis = despesas_variaveis.sort_values("Data")

variaveis_selecionadas = Col10.multiselect(
        label="Despesas Variáveis",  # espaço em branco para não aparecer título
        options=despesas_variaveis['Categoria'].unique(),
        default=despesas_variaveis['Categoria'].unique()
    )

despesas_variaveis_filtro = despesas_variaveis[despesas_variaveis['Categoria'].isin(variaveis_selecionadas)]
despesas_variaveis_agg = despesas_variaveis_filtro.groupby(['Mês - Ano', "Data"])['Valor Unitário'].sum().reset_index()
despesas_variaveis_agg =  despesas_variaveis_agg.sort_values("Data")
despesas_variaveis_agg['Variação (%)'] = despesas_variaveis_agg['Valor Unitário'].pct_change() * 100
despesas_variaveis_filtro['Texto'] = despesas_variaveis_filtro['Valor Unitário'].apply(
    lambda v: f'R$ {v:,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".") if v >= 1 else '')



# Criar o gráfico de barras
fig_variaveis = px.bar(
    despesas_variaveis_filtro,
    y='Valor Unitário',
    x='Mês - Ano',
    color='Categoria',
    text='Texto',
    color_discrete_sequence=px.colors.sequential.YlOrRd_r
)

# Adicionar anotações para mostrar a soma total de cada mês
for i, row in despesas_variaveis_agg.iterrows():
    valor_formatado = f"R$ {row['Valor Unitário']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")  # <br> quebra de linha # Formato R$ 1.000,00
    variacao_formatada = f"{row['Variação (%)']:.1f}%"

    fig_variaveis.add_annotation(
        x=row['Mês - Ano'],  # Posiciona no mês correspondente
        y=row['Valor Unitário'],  # Altura da soma total
        text=f"{valor_formatado}<br>{variacao_formatada}", 
        showarrow=False,
        font=dict(size=12, color="white"),
        xanchor="center",
        yshift=30  # Desloca o texto para cima das barras
    )

fig_variaveis.update_layout(
    xaxis_tickformat = ".,2f",  # Formato com ponto para milhar e vírgula para decimal
    xaxis_title="",
    yaxis_title="",
    hovermode="x", 
    template="plotly_dark"
) 
fig_variaveis.update_traces(
    texttemplate='%{text}',
    textposition='inside')

Col12.plotly_chart(fig_variaveis)

#### ------------------------------> DESPESAS INVESTIMENTOS
despesas_investimentos = registro_df[(registro_df['Tipo'] == "Despesas") & (registro_df['Entrada/Saída'] == "Investimentos")].groupby(['Mês/Ano Pag', 'Categoria', 'Mês - Ano', "Data"])['Valor Unitário'].sum().reset_index()
despesas_investimentos = despesas_investimentos.sort_values("Data")

investimentos_selecionadas = Col13.multiselect(
        label="Despesas com Investimentos",  # espaço em branco para não aparecer título
        options=despesas_investimentos['Categoria'].unique(),
        default=despesas_investimentos['Categoria'].unique()
    )

despesas_investimentos_filtro = despesas_investimentos[despesas_investimentos['Categoria'].isin(investimentos_selecionadas)]
despesas_investimentos_agg = despesas_investimentos_filtro.groupby(['Mês - Ano', "Data"])['Valor Unitário'].sum().reset_index()
despesas_investimentos_agg =  despesas_investimentos_agg.sort_values("Data")
despesas_investimentos_agg['Variação (%)'] = despesas_investimentos_agg['Valor Unitário'].pct_change() * 100
despesas_investimentos_filtro['Texto'] = despesas_investimentos_filtro['Valor Unitário'].apply(
    lambda v: f'R$ {v:,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".") if v >= 1 else '')



# Criar o gráfico de barras
fig_investimentos = px.bar(
    despesas_investimentos_filtro,
    y='Valor Unitário',
    x='Mês - Ano',
    color='Categoria',
    text='Texto',
    color_discrete_sequence=px.colors.sequential.YlOrRd_r
)

# Adicionar anotações para mostrar a soma total de cada mês
for i, row in despesas_investimentos_agg.iterrows():
    valor_formatado = f"R$ {row['Valor Unitário']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")  # <br> quebra de linha # Formato R$ 1.000,00
    variacao_formatada = f"{row['Variação (%)']:.1f}%"

    fig_investimentos.add_annotation(
        x=row['Mês - Ano'],  # Posiciona no mês correspondente
        y=row['Valor Unitário'],  # Altura da soma total
        text=f"{valor_formatado}<br>{variacao_formatada}", 
        showarrow=False,
        font=dict(size=12, color="white"),
        xanchor="center",
        yshift=30  # Desloca o texto para cima das barras
    )

fig_investimentos.update_layout(
    xaxis_tickformat = ".,2f",  # Formato com ponto para milhar e vírgula para decimal
    xaxis_title="",
    yaxis_title="",
    hovermode="x", 
    template="plotly_dark"
) 
fig_investimentos.update_traces(
    texttemplate='%{text}',
    textposition='inside')

Col15.plotly_chart(fig_investimentos)


#### ------------------------------> DESPESAS Diretoria
despesas_diretoria = registro_df[(registro_df['Tipo'] == "Despesas") & (registro_df['Entrada/Saída'] == "Diretoria")].groupby(['Mês/Ano Pag', 'Categoria', 'Mês - Ano', "Data"])['Valor Unitário'].sum().reset_index()
despesas_diretoria = despesas_diretoria.sort_values("Data")

diretoria_selecionadas = Col14.multiselect(
        label="Despesas da Diretoria",  # espaço em branco para não aparecer título
        options=despesas_diretoria['Categoria'].unique(),
        default=despesas_diretoria['Categoria'].unique()
    )

despesas_diretoria_filtro = despesas_diretoria[despesas_diretoria['Categoria'].isin(diretoria_selecionadas)]
despesas_diretoria_agg = despesas_diretoria_filtro.groupby(['Mês - Ano', "Data"])['Valor Unitário'].sum().reset_index()
despesas_diretoria_agg =  despesas_diretoria_agg.sort_values("Data")
despesas_diretoria_agg['Variação (%)'] = despesas_diretoria_agg['Valor Unitário'].pct_change() * 100
despesas_diretoria_filtro['Texto'] = despesas_diretoria_filtro['Valor Unitário'].apply(
    lambda v: f'R$ {v:,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".") if v >= 1 else '')


# Criar o gráfico de barras
fig_diretoria = px.bar(
    despesas_diretoria_filtro,
    y='Valor Unitário',
    x='Mês - Ano',
    color='Categoria',
    text='Texto',
    color_discrete_sequence=px.colors.sequential.YlOrRd_r
)

# Adicionar anotações para mostrar a soma total de cada mês
for i, row in despesas_diretoria_agg.iterrows():
    valor_formatado = f"R$ {row['Valor Unitário']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")  # <br> quebra de linha # Formato R$ 1.000,00
    variacao_formatada = f"{row['Variação (%)']:.1f}%"

    fig_diretoria.add_annotation(
        x=row['Mês - Ano'],  # Posiciona no mês correspondente
        y=row['Valor Unitário'],  # Altura da soma total
        text=f"{valor_formatado}<br>{variacao_formatada}", 
        showarrow=False,
        font=dict(size=12, color="white"),
        xanchor="center",
        yshift=30  # Desloca o texto para cima das barras
    )

fig_diretoria.update_layout(
    xaxis_tickformat = ".,2f",  # Formato com ponto para milhar e vírgula para decimal
    xaxis_title="",
    yaxis_title="",
    hovermode="x", 
    template="plotly_dark"
) 
fig_diretoria.update_traces(
    texttemplate='%{text}',
    textposition='inside')

Col16.plotly_chart(fig_diretoria)

st.divider()

#### ---------------------------------------> Profissionais 
st.markdown("<h2 style='text-align: center;'>Profissionais</h2>", unsafe_allow_html=True)

profissional = registro_df[(registro_df['Tipo'] == "Receitas")].groupby(['Mês - Ano', "Data", "Profissional", "Entrada/Saída"])['Valor Unitário'].sum().reset_index()
profissional = profissional.sort_values("Data")

profissional_categoria = st.multiselect(
        label="Categoria de Receitas",  # espaço em branco para não aparecer título
        options=profissional['Entrada/Saída'].unique(),
        default=profissional['Entrada/Saída'].unique()
    )
 
profissional_filtro = profissional[profissional['Entrada/Saída'].isin(profissional_categoria)]

Col17, Col18 = st.columns(2,vertical_alignment="center")
Col19, Col20 = st.columns(2,vertical_alignment="center")
Col21, Col22 = st.columns(2,vertical_alignment="center")


#### ------------------> Gustavo
#### ----------> Faturamento

gustavo = profissional_filtro[profissional_filtro['Profissional'] == "Gustavo de Castro"].groupby(['Mês - Ano', "Data", "Profissional","Entrada/Saída"])['Valor Unitário'].sum().reset_index()
gustavo = gustavo.sort_values("Data")
gustavo_agg = gustavo.groupby(['Mês - Ano',"Profissional", "Data"])['Valor Unitário'].sum().reset_index()
gustavo_agg = gustavo_agg.sort_values("Data")
gustavo_agg['Variação (%)'] = gustavo_agg['Valor Unitário'].pct_change() * 100

fig_profissional = px.bar(gustavo, 
                      y = 'Valor Unitário', 
                      x = 'Mês - Ano', 
                      color ='Entrada/Saída',
                      text='Valor Unitário',
                      title="Gustavo - Faturamento",
                      color_discrete_sequence=px.colors.sequential.YlGn_r)


for i, row in gustavo_agg.iterrows():
    valor_formatado = f"R$ {row['Valor Unitário']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")  # <br> quebra de linha # Formato R$ 1.000,00
    variacao_formatada = f"{row['Variação (%)']:.1f}%"

    fig_profissional.add_annotation(
        x=row['Mês - Ano'],  # Posiciona no mês correspondente
        y=row['Valor Unitário'],  # Altura da soma total
        text=f"{valor_formatado}<br>{variacao_formatada}", 
        showarrow=False,
        font=dict(size=12, color="white"),
        xanchor="center",
        yshift=30  # Desloca o texto para cima das barras
    )

fig_profissional.update_layout(
    xaxis_tickformat = ".,2f",  # Formato com ponto para milhar e vírgula para decimal
    xaxis_title="",
    yaxis_title="",
    hovermode="x", 
    template="plotly_dark"
)                      
                     
Col17.plotly_chart(fig_profissional)

#### ---------------------> Gustavo
#### ----------> Quantidade

gustavo_qtd = registro_df[(registro_df['Tipo'] == "Receitas") & (registro_df['Profissional'] == "Gustavo de Castro")].groupby(['Mês - Ano', "Data", "Profissional", "Entrada/Saída"])['Valor Unitário'].count().reset_index()
gustavo_qtd = gustavo_qtd.sort_values("Data")
gustavo_qtd  = gustavo_qtd[gustavo_qtd["Entrada/Saída"].isin(profissional_categoria)]
gustavo_qtd_agg = gustavo_qtd.groupby(['Mês - Ano', "Data"])['Valor Unitário'].sum().reset_index()
gustavo_qtd_agg = gustavo_qtd_agg.sort_values("Data")
gustavo_qtd_agg['Variação (%)'] = gustavo_qtd_agg['Valor Unitário'].pct_change() * 100


fig_gustavo_qtd = px.bar(gustavo_qtd,
                      y = 'Valor Unitário', 
                      x = 'Mês - Ano', 
                      color ='Entrada/Saída',
                      text='Valor Unitário',
                      title="Gustavo - Quantidade",
                      color_discrete_sequence=px.colors.sequential.YlGn_r)


for i, row in gustavo_qtd_agg.iterrows():
    valor_formatado = f"{row['Valor Unitário']:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")  # <br> quebra de linha # Formato R$ 1.000,00
    variacao_formatada = f"{row['Variação (%)']:.1f}%"

    fig_gustavo_qtd.add_annotation(
        x=row['Mês - Ano'],  # Posiciona no mês correspondente
        y=row['Valor Unitário'],  # Altura da soma total
        text=f"{valor_formatado}<br>{variacao_formatada}", 
        showarrow=False,
        font=dict(size=12, color="white"),
        xanchor="center",
        yshift=30  # Desloca o texto para cima das barras
    )

fig_gustavo_qtd.update_layout(
    xaxis_tickformat = ".,2f",  # Formato com ponto para milhar e vírgula para decimal
    xaxis_title="",
    yaxis_title="",
    hovermode="x", 
    template="plotly_dark"
)                      
                     
Col18.plotly_chart(fig_gustavo_qtd)

#### ------------------> Christian
#### ----------> Faturamento

christian = profissional_filtro[profissional_filtro['Profissional'] == "Christian Magon"].groupby(['Mês - Ano', "Data", "Profissional","Entrada/Saída"])['Valor Unitário'].sum().reset_index()
christian = christian.sort_values("Data")
christian_agg = christian.groupby(['Mês - Ano',"Profissional", "Data"])['Valor Unitário'].sum().reset_index()
christian_agg = christian_agg.sort_values("Data")
christian_agg['Variação (%)'] = christian_agg['Valor Unitário'].pct_change() * 100

fig_christian = px.bar(christian, 
                      y = 'Valor Unitário', 
                      x = 'Mês - Ano', 
                      color ='Entrada/Saída',
                      text='Valor Unitário',
                      title="Christian - Faturamento",
                      color_discrete_sequence=px.colors.sequential.YlGn_r)


for i, row in christian_agg.iterrows():
    valor_formatado = f"R$ {row['Valor Unitário']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")  # <br> quebra de linha # Formato R$ 1.000,00
    variacao_formatada = f"{row['Variação (%)']:.1f}%"

    fig_christian.add_annotation(
        x=row['Mês - Ano'],  # Posiciona no mês correspondente
        y=row['Valor Unitário'],  # Altura da soma total
        text=f"{valor_formatado}<br>{variacao_formatada}", 
        showarrow=False,
        font=dict(size=12, color="white"),
        xanchor="center",
        yshift=30  # Desloca o texto para cima das barras
    )

fig_christian.update_layout(
    xaxis_tickformat = ".,2f",  # Formato com ponto para milhar e vírgula para decimal
    xaxis_title="",
    yaxis_title="",
    hovermode="x", 
    template="plotly_dark"
)                      
                     
Col19.plotly_chart(fig_christian)

#### ---------------------> Christian
#### ----------> Quantidade

christian_qtd = registro_df[(registro_df['Tipo'] == "Receitas") & (registro_df['Profissional'] == "Christian Magon")].groupby(['Mês - Ano', "Data", "Profissional", "Entrada/Saída"])['Valor Unitário'].count().reset_index()
christian_qtd = christian_qtd.sort_values("Data")
christian_qtd  = christian_qtd[christian_qtd["Entrada/Saída"].isin(profissional_categoria)]
christian_qtd_agg = christian_qtd.groupby(['Mês - Ano', "Data"])['Valor Unitário'].sum().reset_index()
christian_qtd_agg = christian_qtd_agg.sort_values("Data")
christian_qtd_agg['Variação (%)'] = christian_qtd_agg['Valor Unitário'].pct_change() * 100


fig_christian_qtd = px.bar(christian_qtd,
                      y = 'Valor Unitário', 
                      x = 'Mês - Ano', 
                      color ='Entrada/Saída',
                      text='Valor Unitário',
                      title="Christian - Quantidade",
                      color_discrete_sequence=px.colors.sequential.YlGn_r)


for i, row in christian_qtd_agg.iterrows():
    valor_formatado = f"{row['Valor Unitário']:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")  # <br> quebra de linha # Formato R$ 1.000,00
    variacao_formatada = f"{row['Variação (%)']:.1f}%"

    fig_christian_qtd.add_annotation(
        x=row['Mês - Ano'],  # Posiciona no mês correspondente
        y=row['Valor Unitário'],  # Altura da soma total
        text=f"{valor_formatado}<br>{variacao_formatada}", 
        showarrow=False,
        font=dict(size=12, color="white"),
        xanchor="center",
        yshift=30  # Desloca o texto para cima das barras
    )

fig_christian_qtd.update_layout(
    xaxis_tickformat = ".,2f",  # Formato com ponto para milhar e vírgula para decimal
    xaxis_title="",
    yaxis_title="",
    hovermode="x", 
    template="plotly_dark"
)                      
                     
Col20.plotly_chart(fig_christian_qtd)

#### ------------------> Christian
#### ----------> Faturamento

christian = profissional_filtro[profissional_filtro['Profissional'] == "PATRICK CARDOSO"].groupby(['Mês - Ano', "Data", "Profissional","Entrada/Saída"])['Valor Unitário'].sum().reset_index()
christian = christian.sort_values("Data")
christian_agg = christian.groupby(['Mês - Ano',"Profissional", "Data"])['Valor Unitário'].sum().reset_index()
christian_agg = christian_agg.sort_values("Data")
christian_agg['Variação (%)'] = christian_agg['Valor Unitário'].pct_change() * 100

fig_christian = px.bar(christian, 
                      y = 'Valor Unitário', 
                      x = 'Mês - Ano', 
                      color ='Entrada/Saída',
                      text='Valor Unitário',
                      title="Patrick - Faturamento",
                      color_discrete_sequence=px.colors.sequential.YlGn_r)


for i, row in christian_agg.iterrows():
    valor_formatado = f"R$ {row['Valor Unitário']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")  # <br> quebra de linha # Formato R$ 1.000,00
    variacao_formatada = f"{row['Variação (%)']:.1f}%"

    fig_christian.add_annotation(
        x=row['Mês - Ano'],  # Posiciona no mês correspondente
        y=row['Valor Unitário'],  # Altura da soma total
        text=f"{valor_formatado}<br>{variacao_formatada}", 
        showarrow=False,
        font=dict(size=12, color="white"),
        xanchor="center",
        yshift=30  # Desloca o texto para cima das barras
    )

fig_christian.update_layout(
    xaxis_tickformat = ".,2f",  # Formato com ponto para milhar e vírgula para decimal
    xaxis_title="",
    yaxis_title="",
    hovermode="x", 
    template="plotly_dark"
)                      
                     
Col21.plotly_chart(fig_christian)

#### ---------------------> Christian
#### ----------> Quantidade

patrick_qtd = registro_df[(registro_df['Tipo'] == "Receitas") & (registro_df['Profissional'] == "PATRICK CARDOSO")].groupby(['Mês - Ano', "Data", "Profissional", "Entrada/Saída"])['Valor Unitário'].count().reset_index()
patrick_qtd = patrick_qtd.sort_values("Data")
patrick_qtd  = patrick_qtd[patrick_qtd["Entrada/Saída"].isin(profissional_categoria)]
patrick_qtd_agg = patrick_qtd.groupby(['Mês - Ano', "Data"])['Valor Unitário'].sum().reset_index()
patrick_qtd_agg = patrick_qtd_agg.sort_values("Data")
patrick_qtd_agg['Variação (%)'] = patrick_qtd_agg['Valor Unitário'].pct_change() * 100


fig_patrick_qtd = px.bar(patrick_qtd,
                      y = 'Valor Unitário', 
                      x = 'Mês - Ano', 
                      color ='Entrada/Saída',
                      text='Valor Unitário',
                      title="Patrick - Quantidade",
                      color_discrete_sequence=px.colors.sequential.YlGn_r)


for i, row in patrick_qtd_agg.iterrows():
    valor_formatado = f"{row['Valor Unitário']:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")  # <br> quebra de linha # Formato R$ 1.000,00
    variacao_formatada = f"{row['Variação (%)']:.1f}%"

    fig_patrick_qtd.add_annotation(
        x=row['Mês - Ano'],  # Posiciona no mês correspondente
        y=row['Valor Unitário'],  # Altura da soma total
        text=f"{valor_formatado}<br>{variacao_formatada}", 
        showarrow=False,
        font=dict(size=12, color="white"),
        xanchor="center",
        yshift=30  # Desloca o texto para cima das barras
    )

fig_patrick_qtd.update_layout(
    xaxis_tickformat = ".,2f",  # Formato com ponto para milhar e vírgula para decimal
    xaxis_title="",
    yaxis_title="",
    hovermode="x", 
    template="plotly_dark"
)                      
                     
Col22.plotly_chart(fig_patrick_qtd)


st.divider()

#### ---------------------------------------------> Metas 
#### --------------------------------> Faturamento

st.markdown("<h1 style='text-align: center;'>Metas</h1>", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center;'>Faturamento</h2>", unsafe_allow_html=True)


receita_meta = registro_df[(registro_df['Tipo'] == "Receitas") & (registro_df['Entrada/Saída'] == "Serviços") | (registro_df['Entrada/Saída'] == "Combos") | (registro_df['Entrada/Saída'] == "Produtos") ].groupby(['Profissional', 'Mês - Ano'])['Valor Unitário'].sum().reset_index(name='Valor Financeiro')
#receita_meta = receita_meta.sort_values("Data")
receita_meta_atual = receita_meta.loc[receita_meta['Mês - Ano'] == meses_atual]
receita_meta_atual['Meta'] = [7597.98, 10159.55, 6800.60]
receita_meta_atual['Porcentagem'] = receita_meta_atual['Valor Financeiro'] / receita_meta_atual['Meta']

# 1. Ordenar os profissionais alfabeticamente
receita_meta_atual = receita_meta_atual.sort_values('Profissional')

# 2. Criar gráfico
fig_meta = px.bar(
    receita_meta_atual,
    y='Profissional',
    x='Valor Financeiro',
    orientation='h',
    color='Porcentagem',
    color_continuous_scale=[(0, '#FF4D4D'), (0.5, '#FFC900'), (1, '#2ECC71')],
    range_color=[0, 1.2],
    title='Progresso de Metas - ' + meses_atual,
    labels={'Valor Financeiro': 'Valor (R$)'}
)

# 3. Linhas de meta PERFEITAMENTE alinhadas
for i, profissional_meta in enumerate(receita_meta_atual['Profissional']):
    meta = receita_meta_atual.loc[receita_meta_atual['Profissional'] == profissional_meta, 'Meta'].values[0]
    fig_meta.add_vline(
        x=meta,
        line_dash="dot",
        line_color="red",
        line_width=2.5,
        layer='below',
        row=1, col=1
    )

# 4. Ajustes finais
fig_meta.update_traces(
    texttemplate='R$ %{x:,.2f} (%{customdata[1]:.1%})',
    textposition='auto',
    textfont_size=12,
    customdata=receita_meta_atual[['Meta', 'Porcentagem']]
)

fig_meta.update_layout(
    template="plotly_dark",
    height=400,
    yaxis={'categoryorder':'total ascending'},
    coloraxis_colorbar=dict(
        title="% da Meta",
        tickvals=[0, 0.4, 0.7, 0.9, 1.2],
        ticktext=["0%", "40%", "70%", "90%", "120%"]
    )
)

st.plotly_chart(fig_meta)

#### --------------------------------> Quantidade
st.markdown("<h2 style='text-align: center;'>Quantidade Serviços Prestados</h2>", unsafe_allow_html=True)

qtd_meta = registro_df[(registro_df['Tipo'] == "Receitas") & (registro_df['Entrada/Saída'] == "Serviços") | (registro_df['Entrada/Saída'] == "Combos")].groupby(['Profissional', 'Mês - Ano'])['Valor Unitário'].count().reset_index(name='Quantidade')
#receita_meta = receita_meta.sort_values("Data")
qtd_meta_atual = qtd_meta.loc[receita_meta['Mês - Ano'] == meses_atual]
qtd_meta_atual['Meta'] = [221, 305, 185]
qtd_meta_atual['Porcentagem'] = qtd_meta_atual['Quantidade'] / qtd_meta_atual['Meta']

# 1. Ordenar os profissionais alfabeticamente
qtd_meta_atual = qtd_meta_atual.sort_values('Profissional')

# 2. Criar gráfico
fig_meta_qtd = px.bar(
    qtd_meta_atual,
    y='Profissional',
    x='Quantidade',
    orientation='h',
    color='Porcentagem',
    color_continuous_scale=[(0, '#FF4D4D'), (0.5, '#FFC900'), (1, '#2ECC71')],
    range_color=[0, 1.2],
    title='Progresso de Metas - ' + meses_atual,
    labels={'Valor Financeiro': 'Valor (R$)'}
)

# 3. Linhas de meta PERFEITAMENTE alinhadas
for i, profissional in enumerate(qtd_meta_atual['Profissional']):
    meta = qtd_meta_atual.loc[qtd_meta_atual['Profissional'] == profissional, 'Meta'].values[0]
    fig_meta_qtd.add_vline(
        x=meta,
        line_dash="dot",
        line_color="red",
        line_width=2.5,
        layer='below',
        row=1, col=1
    )

# 4. Ajustes finais
fig_meta_qtd.update_traces(
    texttemplate='%{x:,.0f} (%{customdata[1]:.1%})',
    textposition='auto',
    textfont_size=12,
    customdata=qtd_meta_atual[['Meta', 'Porcentagem']]
)

fig_meta_qtd.update_layout(
    template="plotly_dark",
    height=400,
    yaxis={'categoryorder':'total ascending'},
    coloraxis_colorbar=dict(
        title="% da Meta",
        tickvals=[0, 0.4, 0.7, 0.9, 1.2],
        ticktext=["0%", "40%", "70%", "90%", "120%"]
    )
)

st.plotly_chart(fig_meta_qtd)
