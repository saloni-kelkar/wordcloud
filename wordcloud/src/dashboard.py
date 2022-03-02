import pandas as pd
import pyproj
import dash
import dash_bootstrap_components as dbc
import matplotlib.pyplot as plt #if using matplotlib
import plotly.express as px #if using plotly
import plotly.graph_objs as go
import geopandas as gpd
from dash import Dash, dcc, html, Input, Output
from datetime import datetime
from plotly.offline import iplot, init_notebook_mode
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# -- Import and clean data (importing csv into pandas)
# df = pd.read_csv("intro_bees.csv")
fp = "../data/shape/StHimark.shp"
df = pd.read_csv("../data/YInt_cat.csv")
map_df = gpd.read_file(fp)
map_df.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
map_df.columns=['id', 'location', 'geometry']


##word cloud
cat_df = pd.read_csv("../data/YInt_cat.csv")
cat_df['time'] = pd.to_datetime(cat_df['time'])


def get_wordcloud(start: datetime = datetime(2020, 4, 6), end: datetime = datetime(2020, 4, 11), category: str = None):
    tf_df = cat_df.loc[(cat_df.time >= start) & (cat_df.time <= end)]  # tf for time-filtered

    if category is not None:
        if category == 'resource':
            messages = " ".join(tf_df.loc[tf_df.cat_type == ['resource']].message.tolist())
        elif category == 'event':
            messages = " ".join(tf_df.loc[tf_df.cat_type == ['event']].message.tolist())
        else:
            raise

    else:
        messages = " ".join(tf_df.message.tolist())

    return messages.replace("re:", "")


# ------------------------------------------------------------------------------
# App layout



app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div([

                        html.H1("Resource Distribution", style={'text-align': 'center'}),

                        dcc.Dropdown(id="select_resource",
                                     options=[
                                         {"label": "Water", "value": "Water"},
                                         {"label": "Energy", "value": "Energy"},
                                         {"label": "Food", "value": "Food"},
                                         {"label": "Medical", "value": "Medical"},
                                         {"label": "Shelter", "value": "Shelter"},
                                         {"label": "Transportation", "value": "Transportation"}],
                                     multi=False,
                                     value="Water",
                                     style={'width': "40%"}
                                     ),


                    ]),
                    width=12,
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div([
                        dcc.Graph(id='water_map', figure={}),
                        dcc.Graph(id='energy_map', figure={}),
                        dcc.Graph(id='food_map', figure={}),
                        dcc.Graph(id='medical_map', figure={}),
                        dcc.Graph(id='shelter_map', figure={}),
                        dcc.Graph(id='transportation_map', figure={}),

                        dcc.Graph(id='word_cloud', figure={})

                    ]),
                    width=6,
                    style={"overflow": "scroll", "height": "500px"},
                ),
                dbc.Col(
                    html.Div(
                        html.H1("Trend", className="text-center"),
                        className="p-3 gradient",
                    ),
                    width=6,
                    style={"overflow": "scroll", "height": "400px"},
                    className="no-scrollbars",
                ),
            ]
        )
    ]
)
'''
app.layout = html.Div([

    html.H1("Resource Distribution", style={'text-align': 'center'}),

    dcc.Dropdown(id="select_resource",
                 options=[
                     {"label": "Water", "value": "Water"},
                     {"label": "Energy", "value": "Energy"},
                     {"label": "Food", "value": "Food"},
                     {"label": "Medical", "value": "Medical"},
                     {"label": "Shelter", "value": "Shelter"},
                     {"label": "Transportation", "value": "Transportation"}],
                 multi=False,
                 value="Water",
                 style={'width': "40%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='my_bee_map', figure={}),

    dcc.Graph(id='word_cloud', figure={})

])

'''
# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='water_map', component_property='figure'),
     Output(component_id='energy_map', component_property='figure'),
     Output(component_id='food_map', component_property='figure'),
     Output(component_id='medical_map', component_property='figure'),
     Output(component_id='shelter_map', component_property='figure'),
     Output(component_id='transportation_map', component_property='figure'),

     Output(component_id='word_cloud', component_property='figure')],
    [Input(component_id='water_map', component_property='clickData'),
     Input(component_id='energy_map', component_property='clickData'),
     Input(component_id='food_map', component_property='clickData'),
     Input(component_id='medical_map', component_property='clickData'),
     Input(component_id='shelter_map', component_property='clickData'),
     Input(component_id='transportation_map', component_property='clickData')]
)
def update_graph(water_map_input,
                 energy_map_input,
                 food_map_input,
                 medical_map_input,
                 shelter_map_input,
                 transportation_map_input ):
    ctx = dash.callback_context

    print(ctx.triggered)

    # Water choropleth
    df_cat = df[df.cat == 'Water'].groupby(['location', 'cat']).size().reset_index()
    df_cat.columns = ['location', 'cat', 'count']
    df_merged = map_df.merge(df_cat, left_on=['location'], right_on=['location'])

    water_fig = px.choropleth(df_merged, geojson=df_merged.geometry,
                        locations=df_merged.id, color="count",
                        height=300, hover_name=df_merged.location, hover_data={'id': False},
                        color_continuous_scale="Viridis")
    water_fig.update_geos(fitbounds="locations", visible=True)
    water_fig.update_layout(
    )
    water_fig.update(layout=dict(title=dict(x=0.5)))
    water_fig.update_layout(
        margin={"r": 0, "t": 30, "l": 10, "b": 10},
        coloraxis_colorbar={
            'title': 'Water'+' '*9})

    # Energy choropleth

    df_cat = df[df.cat == 'Energy'].groupby(['location', 'cat']).size().reset_index()
    df_cat.columns = ['location', 'cat', 'count']
    df_merged = map_df.merge(df_cat, left_on=['location'], right_on=['location'])
    energy_fig = px.choropleth(df_merged, geojson=df_merged.geometry,
                        locations=df_merged.id, color="count",
                        height=300, hover_name=df_merged.location, hover_data={'id': False},
                        color_continuous_scale="Viridis")
    energy_fig.update_geos(fitbounds="locations", visible=True)
    energy_fig.update_layout(
    )
    energy_fig.update(layout=dict(title=dict(x=0.5)))
    energy_fig.update_layout(
        margin={"r": 0, "t": 30, "l": 10, "b": 10},
        coloraxis_colorbar={
            'title': "Energy"})

    # Food choropleth
    df_cat = df[df.cat == 'Food'].groupby(['location', 'cat']).size().reset_index()
    df_cat.columns = ['location', 'cat', 'count']
    df_merged = map_df.merge(df_cat, left_on=['location'], right_on=['location'])

    food_fig = px.choropleth(df_merged, geojson=df_merged.geometry,
                        locations=df_merged.id, color="count",
                        height=300, hover_name=df_merged.location, hover_data={'id': False},
                        color_continuous_scale="Viridis")
    food_fig.update_geos(fitbounds="locations", visible=True)
    food_fig.update_layout(
    )
    food_fig.update(layout=dict(title=dict(x=0.5)))
    food_fig.update_layout(
        margin={"r": 0, "t": 30, "l": 10, "b": 10},
        coloraxis_colorbar={
            'title': 'Food'})

    # Medical choropleth
    df_cat = df[df.cat == 'Medical'].groupby(['location', 'cat']).size().reset_index()
    df_cat.columns = ['location', 'cat', 'count']
    df_merged = map_df.merge(df_cat, left_on=['location'], right_on=['location'])

    medical_fig = px.choropleth(df_merged, geojson=df_merged.geometry,
                        locations=df_merged.id, color="count",
                        height=300, hover_name=df_merged.location, hover_data={'id': False},
                        color_continuous_scale="Viridis")
    medical_fig.update_geos(fitbounds="locations", visible=True)
    medical_fig.update_layout(
    )
    medical_fig.update(layout=dict(title=dict(x=0.5)))
    medical_fig.update_layout(
        margin={"r": 0, "t": 30, "l": 10, "b": 10},
        coloraxis_colorbar={
            'title': 'Medical'})

    # Shelter choropleth
    df_cat = df[df.cat == 'Shelter'].groupby(['location', 'cat']).size().reset_index()
    df_cat.columns = ['location', 'cat', 'count']
    df_merged = map_df.merge(df_cat, left_on=['location'], right_on=['location'])

    shelter_fig = px.choropleth(df_merged, geojson=df_merged.geometry,
                        locations=df_merged.id, color="count",
                        height=300, hover_name=df_merged.location, hover_data={'id': False},
                        color_continuous_scale="Viridis")
    shelter_fig.update_geos(fitbounds="locations", visible=True)
    shelter_fig.update_layout(
    )
    shelter_fig.update(layout=dict(title=dict(x=0.5)))
    shelter_fig.update_layout(
        margin={"r": 0, "t": 30, "l": 10, "b": 10},
        coloraxis_colorbar={
            'title': 'Shelter'})

    # Transportation choropleth
    df_cat = df[df.cat == 'Transportation'].groupby(['location', 'cat']).size().reset_index()
    df_cat.columns = ['location', 'cat', 'count']
    df_merged = map_df.merge(df_cat, left_on=['location'], right_on=['location'])

    transportation_fig = px.choropleth(df_merged, geojson=df_merged.geometry,
                        locations=df_merged.id, color="count",
                        height=300, hover_name=df_merged.location, hover_data={'id': False},
                        color_continuous_scale="Viridis")
    transportation_fig.update_geos(fitbounds="locations", visible=True)
    transportation_fig.update_layout(
    )
    transportation_fig.update(layout=dict(title=dict(x=0.5)))
    transportation_fig.update_layout(
        margin={"r": 0, "t": 30, "l": 10, "b": 10},
        coloraxis_colorbar={
            'title': 'Transportation'})
    ##Word cloud
    msgs = get_wordcloud()
    wordcloud = WordCloud(background_color='white').generate(msgs)

    ### Data processing for plotly graph objects ###
    word_list = []
    freq_list = []
    fontsize_list = []
    position_list = []
    orientation_list = []
    color_list = []
    x_pos = []
    y_pos = []

    for (word, freq), fontsize, (x, y), orientation, color in wordcloud.layout_:
        word_list.append(word)
        freq_list.append(freq)
        fontsize_list.append(fontsize)
        x_pos.append(x)
        y_pos.append(y)
        orientation_list.append(orientation)
        color_list.append(color)

    lower, upper = 10, 30
    freq_list = [((x - min(freq_list)) / (max(freq_list) - min(freq_list))) * (upper - lower) + lower for x in
                 freq_list]

    ### Create Plotly graph Object ###
    data = go.Scatter(x=x_pos,
                      y=y_pos,
                      mode='text',
                      text=word_list,
                      marker={'opacity': 0.3},
                      textfont={'size': freq_list,
                                'color': color_list},
                      hoverinfo='text',
                      hovertext=['{0} show msgs containing words here'.format(w) for w in word_list]
                      )

    layout = go.Layout({'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                        'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False}})

    fig1 = go.Figure(data=[data], layout=layout)


    return  water_fig,energy_fig,food_fig,medical_fig,shelter_fig,transportation_fig, fig1


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)