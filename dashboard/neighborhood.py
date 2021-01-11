import streamlit as st
import pandas as pd
import json
import plotly.graph_objs as go
from preprocess import preprocess, preprocess_acs

INCOME = '''
https://data.census.gov/cedsci/table?g=8600000US19102,19103,19104,19106,19107,19109,19111,19112,19114,19115,19116,19118,19119,19120,19121,19122,19123,19124,19125,19126,19127,19128,19129,19130,19131,19132,19133,19134,19135,19136,19137,19138,19139,19140,19141,19142,19143,19144,19145,19146,19147,19148,19149,19150,19151,19152,19153,19154&tid=ACSST5Y2018.S1901&hidePreview=true
'''
POVERTY = '''
https://data.census.gov/cedsci/table?q=S1701&g=0400000US42_8600000US19102,19103,19104,19106,19107,19109,19111,19112,19113,19114,19115,19116,19118,19119,19120,19121,19122,19123,19124,19125,19126,19127,19128,19129,19130,19131,19132,19133,19134,19135,19136,19137,19138,19139,19140,19141,19142,19143,19144,19145,19146,19147,19148,19149,19150,19151,19152,19153,19154&tid=ACSST5Y2018.S1701&hidePreview=true
'''

def app():
    st.title('Breakdown by Neighborhood')
    st.write('This section provides an interactive breakdown of case counts and amounts of bail set and paid by Philadelphia zip code, in tandem with zip-code level median income and poverty level data from the American Community Survey (ACS).')
    st.markdown(f"""
    Source Data: [Median Income]({INCOME}), [Poverty Level]({POVERTY})
        """)
    
    col1, col2 = st.beta_columns(2)
    
    # Get bail data
    df = preprocess()
    
    # Create data assoc. w/ each metric (over all bail types) and put in dict
    case_counts = pd.DataFrame(df['zip'].value_counts().reset_index().rename(columns={'index': 'zip', 'zip': 'count'}))
    bail_amounts = df.groupby('zip').sum()[['bail_amount']].reset_index()
    bail_paid = df.groupby('zip').sum()[['bail_paid']].reset_index()
    cases_dfs = {'Case Count': case_counts, 'Bail Amount': bail_amounts, 'Bail Paid': bail_paid}
    
    # Geo data
    # Approximate Philly lat/long
    philly = (40.00, -75.16)

    # Open geojson of philly zip code borders
    zips_geo = '../Zipcodes_Poly.geojson'
    with open(zips_geo) as f:
        zips_data = json.load(f)
    
    # Interactive map for bail metrics
    # Make dropdown for bail metric
    metric = col1.selectbox('Metric', ('Case Count', 'Bail Amount', 'Bail Paid'))
    
    # Get data for the selected metric
    data = cases_dfs[metric]
    z = data[data.columns[1]]
    locations = data[data.columns[0]]

    # Set up figure object (choropleth map) with our geo data
    map_fig = go.FigureWidget(go.Choroplethmapbox(geojson=zips_data, # geojson data
                                          z=z, # what colors will rep. in map from our data
                                          locations=locations, # zip codes in our data
                                          featureidkey="properties.CODE", # key index in geojson for zip
                                         ))
    map_fig.update_layout(mapbox_style="carto-positron",
                   mapbox_zoom=8.5, mapbox_center = {"lat": philly[0], "lon": philly[1]})
    map_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=600, width=350)
    
    col1.plotly_chart(map_fig)
    
    # Interactive map for ACS metrics
    # Get ACS data
    acs_df = preprocess_acs()
    
    # Dropdown for ACS metrics
    acs_metric = col2.selectbox('Census Metric', ('Households Median Income', 'Percent Below Poverty'))
    
    # Set up figure object (choropleth map) with geo data, make sure z gets the selected metric
    acs_map_fig = go.FigureWidget(go.Choroplethmapbox(geojson=zips_data, # geojson data
                                          z=acs_df['_'.join([w.lower() for w in acs_metric.split(' ')])], # what colors will rep. in map from our data
                                          locations=acs_df['zipcode'], # zip codes in our data
                                          featureidkey="properties.CODE", # key index in geojson for zip
                                         ))
    acs_map_fig.update_layout(mapbox_style="carto-positron",
                   mapbox_zoom=8.5, mapbox_center = {"lat": philly[0], "lon": philly[1]})
    acs_map_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=600, width=350)
    
    col2.plotly_chart(acs_map_fig)
    