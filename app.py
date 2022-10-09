from dash import Dash, html, dcc, Output, Input
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
import json
from copy import copy

with open('geojson-counties-fips.json', 'r') as file:
  counties = json.load(file)

df = pd.read_csv('county-gdp.csv', skiprows=4, dtype={'GeoFips':str}, na_values='(NA)')
df['log10_gdp_2020'] = np.log10(df['2020'])

state_fips = pd.read_csv('state-fips.csv', dtype={'FIPS':str}).set_index('State')

fig = px.choropleth(df, geojson=counties, locations='GeoFips', scope='usa',
  color='log10_gdp_2020', color_continuous_scale='viridis')
fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})

app = Dash(__name__)

app.layout = html.Div([
  html.H1('GDP of U.S. counties'),
  html.P('Select a state:'),
  dcc.Dropdown(options=state_fips.index, id='state-dropdown'),
  dcc.Graph(figure=fig, id='gdp-map')
])

@app.callback(
  Output('gdp-map', 'figure'),
  Input('state-dropdown', 'value'),
)
def update_map(state_name):
  if state_name is None:
    return fig
  target_state = state_fips.at[state_name, 'FIPS']

  state_counties = copy(counties)
  state_counties['features'] = [f for f in state_counties['features'] if f['properties']['STATE'] == target_state]
  state_fig = px.choropleth(df, geojson=state_counties, locations='GeoFips', scope='usa',
    color='log10_gdp_2020', color_continuous_scale='viridis')
  state_fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
  return state_fig

app.run_server()
