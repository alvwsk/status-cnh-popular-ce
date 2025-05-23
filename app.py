import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import streamlit as st

@st.cache_data
def carregar_dados_chamados(caminho_csv):
    try:
        df = pd.read_csv(caminho_csv)
        if df.empty:
            st.warning(f"O arquivo CSV '{caminho_csv}' está vazio. Nenhum município será marcado como convocado.")
        return df
    except FileNotFoundError:
        st.error(f"Erro: O arquivo '{caminho_csv}' (com os municípios convocados) não foi encontrado. Verifique o caminho e o nome do arquivo.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Ocorreu um erro ao ler o arquivo CSV '{caminho_csv}': {e}")
        return pd.DataFrame()

@st.cache_data
def carregar_mapa_ce(url_geojson):
    try:
        gdf = gpd.read_file(url_geojson)
        return gdf
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar o GeoJSON do URL: {e}")
        return None

st.set_page_config(layout="wide")
st.title('CNH Popular 2024 no Ceará: Municípios com Convocação Iniciada')

csv_chamados = "municipios_cnh_popular_2024.csv"
geojson_url = "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-23-mun.json"

chamados_df = carregar_dados_chamados(csv_chamados)
mapa_ce_gdf = carregar_mapa_ce(geojson_url)

if mapa_ce_gdf is None:
    st.error("Não foi possível carregar os dados do mapa. A aplicação não pode continuar.")
    st.stop()

if not chamados_df.empty:
    chamados_df['nome_normalizado'] = chamados_df.iloc[:, 0].astype(str).str.lower().str.strip()
else:
    chamados_df['nome_normalizado'] = pd.Series(dtype='str')

mapa_ce_gdf['nome_normalizado'] = mapa_ce_gdf['name'].astype(str).str.lower().str.strip()
mapa_ce_gdf['ja_convocado'] = mapa_ce_gdf['nome_normalizado'].isin(chamados_df['nome_normalizado'])

cor_convocacao_iniciada = '#2ECC71'
cor_aguardando_convocacao = '#D0D3D4'
cor_borda_municipio = '#566573'
cor_texto_rotulo = '#34495E'
cor_titulo_mapa = '#2C3E50'

fig, ax = plt.subplots(1, 1, figsize=(14, 14))

mapa_ce_gdf.plot(ax=ax,
                 color=mapa_ce_gdf['ja_convocado'].map({True: cor_convocacao_iniciada, False: cor_aguardando_convocacao}),
                 edgecolor=cor_borda_municipio,
                 linewidth=0.7)

for idx, row in mapa_ce_gdf.iterrows():
    nome_municipio = row['name'].title()
    ponto_representativo = row.geometry.representative_point()
    ax.text(ponto_representativo.x,
            ponto_representativo.y,
            nome_municipio,
            fontsize=5.5,
            fontweight='normal',
            ha='center',
            va='center',
            color=cor_texto_rotulo)

patch_convocacao_iniciada = mpatches.Patch(color=cor_convocacao_iniciada, label='Convocação Iniciada')
patch_aguardando_convocacao = mpatches.Patch(color=cor_aguardando_convocacao, label='Aguardando Convocação')

ax.legend(handles=[patch_convocacao_iniciada, patch_aguardando_convocacao],
          loc='lower left',
          fontsize=10,
          title="Status da Convocação",
          title_fontsize=12,
          frameon=True,
          facecolor='white',
          edgecolor=cor_borda_municipio)

titulo_mapa = 'CNH Popular 2024 em Ceará: Status da Convocação por Município'
ax.set_title(titulo_mapa, fontsize=18, fontweight='bold', color=cor_titulo_mapa, pad=20)
ax.axis('off')

plt.tight_layout(pad=1.5)

st.pyplot(fig)

st.info("O mapa destaca em verde os municípios onde os participantes já foram convocados para iniciar o processo.")
st.caption("Fonte dos dados geográficos: GitHub @tbrugz/geodata-br. Lista de municípios convocados: arquivo local.")