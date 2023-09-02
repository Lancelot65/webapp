from dash import Dash, html, dcc, Output, Input, State, callback_context
import ccxt, plotly.graph_objects as go, pandas as pd
from datetime import timedelta, datetime

indicateur = {}
df, fig = None, None
app = Dash(__name__)

app.layout = html.Div([
        html.H1('graphique', style={'text-align': 'center'}),
        html.Br(),
        html.Div(
            children=[
                dcc.Dropdown(options=list(ccxt.kraken().timeframes), multi=False, id='time', value='30m', searchable=False, clearable=False),
                dcc.RadioItems(options=[{'label': 'EUR/USD', 'value': 'EUR/USD'}, {'label': 'GBP/USD', 'value': 'GBP/USD'}], id='market', value='EUR/USD'), 
                html.Button('Create_graph', id='create_graph', n_clicks=0),
                dcc.Input(placeholder='calcul', value='', id='calcul'),
                dcc.Input(placeholder='name', value='', id='names'),
                html.Button('Valider', id='valider', n_clicks=0),
                dcc.Dropdown(options=[{'label': key, 'value': key} for key in indicateur.keys()], multi=True,\
                    id='active_ind', placeholder='selectionner indincateur', searchable=False, clearable=False),
            ]),
        dcc.Graph(id='graph'),
        dcc.Interval(
            id='interval-component',
            interval=30 * 20000,
            n_intervals=0),
])

@app.callback(
    Output('graph', 'figure'),
    Output('interval-component', 'interval'),
    Input('interval-component', 'n_intervals'),
    Input('create_graph', 'n_clicks'),
    State('time', 'value'),
    State('market', 'value'),
    State('active_ind', 'value'),
    State('interval-component', 'interval')
)
def update_graph(interval, n_clicks, timeframes, markets, liste_ind, actuel_interval):
    global indicateur, fig, df
    
    ctx = callback_context

    ex = ccxt.kraken()
    
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id != 'interval-component':
        df = ex.fetch_ohlcv(markets, timeframe=timeframes, limit=70)
        df = pd.DataFrame(df, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df.timestamp = pd.to_datetime(df.timestamp, unit='ms')

        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        close = df.close
        ouverture = df.open
        high = df.high
        low = df.low
        time = df.timestamp

        fig = go.Figure(go.Candlestick(x=time, open=ouverture, high=high, low=low, close=close))
        
        fig.update_layout(
            xaxis_title='date',
            yaxis_title='valeur',
            xaxis_rangeslider_visible=False,
            title=f"{markets} {timeframes}",
            title_x=0.5 
        )
        if liste_ind:
            for ind in liste_ind:
                fig.add_trace(go.Scatter(x=time, y=eval(indicateur[ind]), name=ind))
        time = ex.timeframes[timeframes] * 20000
        return fig, time
    else:
        print('update')
        new_data = ex.fetch_ohlcv('EUR/USD', timeframe=timeframes, limit=2)
        new_data = pd.DataFrame(new_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        new_data.timestamp = pd.to_datetime(new_data.timestamp, unit='ms')
        if new_data.timestamp.iloc[-1] == df.timestamp.iloc[-1]:
            print('already_exist')
            df = df.iloc[:-1]
            df = pd.concat([df, new_data.iloc[[-1]]])
        elif new_data.timestamp.iloc[-1] != df.timestamp.iloc[-1]:
            print('new')
            df = df.iloc[:-1]
            df = pd.concat([df, new_data])

        fig = go.Figure(go.Candlestick(x=df.timestamp, open=df.open, high=df.high, low=df.low, close=df.close))
        return fig, actuel_interval


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
    ouverture = open
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
    app.run(debug=True)