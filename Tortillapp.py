import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import json
import numpy as np


########################################   Data Cleaning   ##########################################################################

# Archivos de datos
#data_path = "tortilla_prices.csv"
#geojson_path = "mexicoHigh.json"
# Cargar datos de precios
tortilla = pd.read_csv("tortilla_prices.csv", names=['State', 'City', 'year', 'Month', 'Day', 'Store type', 'Price per kilogram'], header=1)
tortilla = tortilla.dropna()

# Cargar datos del mapa
gdf = gpd.read_file("mexicoHigh.json")
gdf = gdf.sort_values(by='name', ascending=True)

# Crear DataFrame `tortilla_state` agregando datos por estado y año
tortilla_state = tortilla.groupby(['year', 'State']).agg({'Price per kilogram': ['max', 'mean', 'min']})
tortilla_state.reset_index(inplace=True)
tortilla_state.columns = tortilla_state.columns.droplevel(0)
tortilla_state.columns = ['year', 'state', 'max', 'mean', 'min']

# ordenar los estados para que coincida con el mapa 

gdf_states = gdf['name'].values  

repeated_states = np.tile(gdf_states, int(np.ceil(len(tortilla_state) / len(gdf_states))))[:len(tortilla_state)]


tortilla_state['state'] = repeated_states

print(tortilla_state['state'])



# Configurar sidebar para selección de año y tipo de valor
st.title("Precio de las Tortillas en México del 2007 al 2024")
selected_year = st.sidebar.selectbox("Seleccione el Año", tortilla_state['year'].unique())
selected_value = st.sidebar.radio("precio maximo, promedio o minimo", ["max", "mean", "min"])

# Filtrar `tortilla_state` por el año seleccionado
filtered_data = tortilla_state[tortilla_state['year'] == selected_year]

# Asegurarse de que los nombres de estados coincidan entre `gdf` y `tortilla_state`
gdf = gdf.set_index('name')
filtered_data = filtered_data.set_index('state')
merged_data = gdf.join(filtered_data)
geojson = json.loads(merged_data.to_json())

# Crear el mapa coroplético usando la columna seleccionada
fig = px.choropleth(
    merged_data,
    geojson=geojson,
    locations=merged_data.index,  
    color=selected_value,         
    hover_name=merged_data.index,
    color_continuous_scale='Reds'
)

# Configurar apariencia del mapa
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(
    title=f"Mapa Interactivo de México - {selected_value.capitalize()} Precio ({selected_year})",
    width=500,
    height=900,
    legend=dict(
        orientation="h",  
        x=0.5,            
        y=-0.1,           
        xanchor="center", 
        yanchor="top" ),
    template="simple_white"

)


# Crear gráfico de barras dinámico
fig_bar = px.bar(
    filtered_data.reset_index(),
    x=selected_value,   #cambio aqui 
    y="state",  
    color=selected_value,  
    title=f"Precio de la Tortilla por Estado ({selected_year}) - {selected_value.capitalize()}",
    color_continuous_scale="Reds",
    text_auto=True
)

fig_bar.update_layout(
    template="plotly_dark",
    xaxis_title="Estado",
    yaxis_title=f"Precio ({selected_value.capitalize()})",
    showlegend=False,
    width=400,
    height=700
)


col1, col2 = st.columns([0.7, 0.3])

with col1: 
    st.plotly_chart(fig)

with col2: 
    st.plotly_chart(fig_bar)

#######################    serie de tiempo ################################


tortillas_price = tortilla.groupby(['year']).agg({'Price per kilogram': ['max', 'mean', 'min']})

tortillas_price.reset_index(inplace=True)

df_wide = tortillas_price.pivot_table(index='year', values='Price per kilogram')


######################## grafica de la serie de tiempo #############################################

import plotly.graph_objects as go

fig3 = go.Figure()

min_trace = go.Scatter(
    x=df_wide.index,
    y=df_wide['mean'],
    name='average price',
    line=dict(color='black', width=2)
)

max_trace = go.Scatter(
    x=df_wide.index,
    y=df_wide['max'],
    name='Maximum Price',
    line=dict(color='firebrick', width=2, dash='dash')
)


fill_area = go.Scatter(
    x=df_wide.index,  
    y=df_wide['min'],  
    fill='tonexty',  
    fillcolor='rgba(245, 158, 158, 0.3)',  
    showlegend=False,
    name='min price',
    line=dict(color='firebrick')  
)


fig3.add_trace(min_trace)
fig3.add_trace(max_trace)
fig3.add_trace(fill_area)  


fig3.update_layout(
    title=dict(text='precio de la tortilla minimos y maximos historicos'),
    xaxis=dict(title=dict(text='Year')),
    yaxis=dict(title=dict(text='Price per Kilogram'))
)
fig3.update_layout(template='plotly_dark',
                   width=1000,                # Ancho 
                   height=400)


################################# serie de tiempo grafica  ########################################
st.plotly_chart(fig3)

