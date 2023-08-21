import pandas as pd
import numpy as np
from bokeh.plotting import curdoc
from bokeh.layouts import column
from bokeh.plotting import gmap
from bokeh.models import GMapOptions
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool
from bokeh.models import CustomJS, Select
from bokeh.io import show
from bokeh.layouts import layout

api_key = 'AIzaSyAVM93QZCQay8sq1vFf5KGj47PwQVt3nns'
bokeh_width, bokeh_height = 800,600

 
named = pd.read_csv("named_buildings.csv", index_col=0)

def parse_lat_lon(my_str):
    my_str = my_str.replace('MULTIPOLYGON ','').replace('(','').replace(')','').replace(', ','|').replace(' ',',')
    my_str = np.array([(float(i.split(',')[0]),float(i.split(',')[1])) for i in my_str.split('|')])
    return my_str.mean(axis=0)

lat_long = named['the_geom'].apply(parse_lat_lon)
named['lat'] = lat_long.str[1]
named['lon'] = lat_long.str[0]
named_df = named[['NAME','GROUNDELEV','FEAT_CODE','HEIGHTROOF','lat','lon']]
named_df['radius'] = np.sqrt(named_df['HEIGHTROOF'])

def plot(lat, lng, zoom=10, map_type='roadmap',title=''):
    gmap_options = GMapOptions(lat=lat, lng=lng, map_type=map_type, zoom=zoom)
    # p = gmap(api_key, gmap_options, title=title,width=bokeh_width, height=bokeh_height)
   
    hover = HoverTool(
        tooltips = [
            ('Name','@NAME'),
            ('Elevation','@GROUNDELEV ft'),
            ('Feat Code','# @FEAT_CODE'),
            ('Roof Height', '@HEIGHTROOF ft')
        ])

    p = gmap(api_key, gmap_options, title=title, width=bokeh_width, height=bokeh_height, tools=[hover, 'reset', 'wheel_zoom', 'pan'])
    source = ColumnDataSource(named_df)
    p.circle('lon', 'lat', size='radius', alpha=0.5, color='red', source=source)
    return p


select = Select(title="Option:", value="Empire State Building", options=["Empire State Building", "Chrysler Building"])
select.js_on_change("value", CustomJS(code="""console.log('select: value=' + this.value, this.toString())"""))
select.on_change()


wtc = named_df.sort_values('HEIGHTROOF',ascending=False).iloc[0]
p= plot(wtc['lat'],wtc['lon'], zoom=15)
# This final command is required to launch the plot in the browser

layout = layout([
    [select],
    [p]
])

curdoc().add_root(layout)





 
# # Read the country borders shapefile into python using Geopandas 
# shapefile = 'data/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp'
# gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]

# # Rename the columns
# gdf.columns = ['country', 'country_code', 'geometry']
 

# # Convert the GeoDataFrame to GeoJSON format so it can be read by Bokeh
# merged_json = json.loads(gdf.to_json())
# json_data = json.dumps(merged_json)
# geosource = GeoJSONDataSource(geojson=json_data)


# # Make the plot
# TOOLTIPS = [
# ('UN country', '@country')
# ]

# p = figure(title='World Map', plot_height=600 , plot_width=950, tooltips=TOOLTIPS,
# x_axis_label='Longitude', y_axis_label='Latitude')

# p.patches('xs','ys', source=geosource, fill_color='white', line_color='black',
# hover_fill_color='lightblue', hover_line_color='black')