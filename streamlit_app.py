'''
This app visualizes the height of buildings in NYC.
Streamlit guide: https://docs.streamlit.io/library/get-started/main-concepts
'''

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


### DATA PROCESSING

def parse_lat_lon(my_str):
    my_str = my_str.replace('MULTIPOLYGON ','').replace('(','').replace(')','').replace(', ','|').replace(' ',',')
    my_str = np.array([(float(i.split(',')[0]),float(i.split(',')[1])) for i in my_str.split('|')])
    return my_str.mean(axis=0)


named = pd.read_csv("named_buildings.csv", index_col=0)
lat_long = named['the_geom'].apply(parse_lat_lon)
named['lat'] = lat_long.str[1]
named['lon'] = lat_long.str[0]
named_df = named[['NAME','GROUNDELEV','BUILDING_TYPE','HEIGHTROOF','lat','lon']].sort_values(
    'HEIGHTROOF',ascending=False)
named_df['radius'] = np.sqrt(named_df['HEIGHTROOF']).fillna(0)


### SIDEBAR / FILTERING

choices = named_df.head(20)['NAME'].values.tolist()
choice = st.sidebar.selectbox('Choose a building:', options=choices)

center = {'lat': named_df.iloc[0]['lat'], 'lon': named_df.iloc[0]['lon']}
if choice:
    center = {
        'lat': named_df[named_df['NAME']==choice]['lat'].values[0],
        'lon': named_df[named_df['NAME']==choice]['lon'].values[0]
    }

zoom = st.sidebar.slider('Zoom', min_value=8, max_value=20, value=12, step=1)

min_height, max_height = named_df['HEIGHTROOF'].min(), named_df['HEIGHTROOF'].max()
heights = st.sidebar.slider(
    'Select a range of building heights:',
    min_height, max_height, (min_height, max_height))
named_df_filtered = named_df[named_df['HEIGHTROOF'].between(heights[0], heights[1])]


### MAIN APP

# https://plotly.github.io/plotly.py-docs/generated/plotly.express.scatter_mapbox.html
fig = px.scatter_mapbox(
    named_df_filtered,
    lat="lat",
    lon="lon",
    title="All Named Buildings in NYC - choice: {}".format(choice),
    hover_name="NAME",
    hover_data=["GROUNDELEV", "BUILDING_TYPE", "HEIGHTROOF"],
    size='radius',
    center=center,
    mapbox_style="carto-positron",
    zoom=zoom,
    width=800,
    height=600,
)

st.title('NYC Building Visualization Project')
st.text('Created using Streamlit + Plotly + Pandas + Numpy')
st.plotly_chart(fig)
