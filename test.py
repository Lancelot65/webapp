from twelvedata import TDClient
import json
with open('cle.json', 'r') as f:
    cle = json.load(f)['cle']

td = TDClient(apikey=cle)


ts = td.time_series(
    symbol="EUR/USD",
    interval="1h",
    outputsize=1,
)

df = ts.as_pandas()