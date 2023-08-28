'''
This app visualizes the height of buildings in NYC.
Streamlit guide: https://docs.streamlit.io/library/get-started/main-concepts
streamlit run streamlit_app.py
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
    'HEIGHTROOF',ascending=True)
named_df['radius'] = np.sqrt(named_df['HEIGHTROOF']).fillna(0)
named_df['color'] = 'Other Buildings'


### SIDEBAR / FILTERING

st.sidebar.title("Filters/Zoom")

choices = named_df.sort_values('HEIGHTROOF',ascending=False).head(20)['NAME'].values.tolist()
choice = st.sidebar.selectbox('Choose a building:', options=choices)

if choice:
    building = named_df[named_df['NAME']==choice].iloc[0]
else:
    building = named_df.iloc[0]

center = {
    'lat': building['lat'],
    'lon': building['lon']
}
name = building["NAME"]

named_df.loc[named_df['NAME']==name,'color']=name

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
    color = 'color',
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
st.write('Used NYC building data to display named buildings. The circle\'s size relates to the height of the building.')
st.plotly_chart(fig)

st.title("Raw Data")
st.text("Obtained from NYC Open Data")
st.markdown("""
Link to data docs: https://github.com/CityOfNewYork/nyc-geo-metadata/blob/master/Metadata/Metadata_BuildingFootprints.md

* NAME: Building name
* CNSTRCT_YR: Year of construction
* LSTMODDATE: Last modified date
* LSTSTATYPE: Last Status type
* HEIGHTROOF: Roof top height
* FEAT_CODE: Buidling type (see link)
* GROUNDELEV: Base elevation of the buidling 
* the_geom: Polygon of the lat, lon

""")
st.write(named_df.sort_values('HEIGHTROOF',ascending=False).reset_index(drop=True))
