import pandas as pd
import pyproj
import dash
from dash import dash_table
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

table_cols = [
    {'id': 'message', "name": "Message"},
    {'id': 'location', "name": "Location"},
    {'id': 'time', "name": "Time"}
]

# ------------------------------------------------------------------------------
# App layout



app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div([

                        html.H1("Word Cloud", style={'text-align': 'center'}),


                    ]),
                    width=12,
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div([
                        dcc.Graph(id='word_cloud', figure={})

                    ]),
                    width=6,
                    style={"overflow": "scroll", "height": "500px"},
                ),
                dbc.Container(
                    [html.Div(id='wc-tbl-txt', children='Messages'),
                    dash_table.DataTable(
                        id='wc-tbl',
                        columns=table_cols,
                        data=[],
                        page_size=10,
                        style_table={'border': 'thin lightgrey solid'},
                        style_header={'backgroundColor':'lightgrey','fontWeight':'bold'},
                        style_cell={

                        },
                        style_data={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'width': '20px',
                            'textAlign': 'left'
                        },
                    )]

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
    [Output(component_id='word_cloud', component_property='figure'),
     Output(component_id='wc-tbl', component_property='data'),
     Output(component_id='wc-tbl-txt', component_property='children')],


    [Input(component_id='word_cloud', component_property='clickData')]
)
def update_wordcloud(clickData):
    global fig1
    if clickData is not None:

        msg_word = clickData['points'][0]['text']
        table_df = cat_df.loc[cat_df['message'].str.contains(msg_word)][['message', 'location', 'time']]
        # print(table_df.to_dict('records'))
        return [fig1, table_df.to_dict('records'), "Messages " + msg_word]
        # return [fig1, {}, '']
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
                      # hoverinfo='text',
                      # hovertext=['{0} show msgs containing words here'.format(w) for w in word_list]
                      )

    layout = go.Layout({'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                        'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False}})

    fig1 = go.Figure(data=[data], layout=layout)

    return [fig1, [], 'Messages']


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)