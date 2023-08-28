from dash import Dash, html, dcc, callback, Output, Input, State
import pandas as pd
import plotly.graph_objects as go
from ccxt import binance
import plotly.express as px
from datetime import datetime, date
import json

grand_df = {}
indicateur = {}
app = Dash(__name__)

app.layout = html.Div(children=[
    html.Title('visualisation data'),
    html.H1('graphique', style={'text-align': 'center'}),
    html.Div([
        html.Br(),
        dcc.RadioItems(options=[{'label': '1h', 'value': '1h'}],                                    #{'label': '1m', 'value': '1m'},
                                value='1h', id='time', style={'display': 'flex', 'margin': '1em'}),#{'label': '5m', 'value': '5m'},
        dcc.RadioItems(options=[{'label': 'BTC/USDT', 'value': 'BTC/USDT'},
                                {'label': 'EUR/USDT', 'value': 'EUR/USDT'}],
                       value='BTC/USDT', id='exchange', style={'display': 'flex', 'margin': '1em'}),
        #dcc.DatePickerRange(end_date=date(datetime.now().year, datetime.now().month, datetime.now().day)),
        dcc.Input(placeholder='calcul', value='', id='calcul', style={'display': 'flex', 'margin': '1em'}),
        dcc.Input(placeholder='name', value='', id='names', style={'display': 'flex', 'margin': '1em'}),
        html.Button('Valider', id='valider', n_clicks=0),
        dcc.Dropdown(options=[{'label': key, 'value': key} for key in indicateur.keys()], multi=True,\
            id='active_ind', placeholder='selectionner indincateur'
        ),
    ], style={'display': 'flex', 'flex-direction': 'row'}),
    html.Div([
        dcc.Loading(
                    id="loading-2",
                    children=[html.Div([html.Div(id="loading-output-2")])],
                    type="circle"),
        dcc.Graph(id='graph')
    ])
    
], style={'background-color': 'white'})

@app.callback(
    Output('graph', 'figure'),
    Input('time', 'value'),
    Input('exchange', 'value'),
    Input('active_ind', 'value'),
)
def update_graph(timeframe, exchange, liste_ind):
    global indicateur
    if exchange in grand_df and timeframe in grand_df[exchange]:
        df = grand_df[exchange][timeframe]
    else:
        binance_exchange = binance()
        df = pd.DataFrame(binance_exchange.fetch_ohlcv(exchange, timeframe, limit=100),
                          columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        if exchange not in grand_df:
            grand_df[exchange] = {}
        grand_df[exchange][timeframe] = df

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    close = df.close
    open = df.open
    high = df.high
    low = df.low
    time = df.timestamp

    fig = go.Figure(go.Candlestick(x=time, open=open, high=high, low=low, close=close))
    fig.update_layout(
        xaxis_title='date',
        yaxis_title='valeur',
        xaxis_rangeslider_visible=False
    )

    if liste_ind:
        for ind in liste_ind:
            fig.add_trace(go.Scatter(x=time, y=eval(indicateur[ind]), name=ind))
    return fig

@app.callback(
    Output('active_ind', 'options'),
    Output('calcul', 'value'),
    Output('names', 'value'),
    Input('valider', 'n_clicks'),
    State('calcul', 'value'),
    State('names', 'value'),
    State('active_ind', 'options'),
)
def add_indicator(n_clicks, calcul, name, existing_options):
    global indicateur

    df = pd.DataFrame({'close' : [], 'open' : [], 'low' : [], 'high' : [], 'volume' : []})
    close = df.close
    open = df.open
    high = df.high
    low = df.low

    if n_clicks > 0 and calcul and name:
        try:
            eval(calcul)
            indicateur[name] = calcul
            new_option = {'label': name, 'value': name}
            updated_options = existing_options + [new_option]
            return updated_options, '', ''
        except Exception as e:
            print(f"Error adding indicator '{name}': {e}")
    return existing_options, calcul, name

if __name__ == '__main__':
    app.run_server(debug=True)