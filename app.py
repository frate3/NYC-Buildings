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
from bokeh.models import Div, RangeSlider, Spinner

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
named_df = named[['NAME','GROUNDELEV','BUILDING_TYPE','HEIGHTROOF','lat','lon']]
named_df['radius'] = np.sqrt(named_df['HEIGHTROOF'])

def plot(lat, lng, zoom=10, map_type='roadmap',title=''):
    gmap_options = GMapOptions(lat=lat, lng=lng, map_type=map_type, zoom=zoom)
    # p = gmap(api_key, gmap_options, title=title,width=bokeh_width, height=bokeh_height)
   
    hover = HoverTool(
        tooltips = [
            ('Name','@NAME'),
            ('Elevation','@GROUNDELEV ft'),
            ('Building Type','@BUILDING_TYPE'),
            ('Roof Height', '@HEIGHTROOF ft')
        ])

    p = gmap(api_key, gmap_options, title=title, width=bokeh_width, height=bokeh_height, tools=[hover, 'reset', 'wheel_zoom', 'pan'])
    source = ColumnDataSource(named_df)
    points = p.circle('lon', 'lat', size=5, alpha=0.5, color='red', source=source)
    return p,points


select = Select(title="Option:", value="Empire State Building", options=["Empire State Building", "Chrysler Building"])
select.js_on_change("value", CustomJS(code="""console.log('select: value=' + this.value, this.toString())"""))

wtc = named_df.sort_values('HEIGHTROOF',ascending=False).iloc[0]
p, points= plot(wtc['lat'],wtc['lon'], zoom=15)
# This final command is required to launch the plot in the browser


spinner = Spinner(
    title="Circle size",
    low=0,
    high=60,
    step=5,
    value=points.glyph.size,
    width=200,
)
spinner.js_link("value", points.glyph, "size")


layout = layout([
    [spinner],
    [p]
])

curdoc().add_root(layout)
