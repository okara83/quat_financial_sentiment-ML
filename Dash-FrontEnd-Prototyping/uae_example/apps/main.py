import os

import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output

from app import app

if 'DYNO' in os.environ:
    app_name = os.environ['DASH_APP_NAME']
else:
    app_name = 'dash-candlestickplot'

dff = pd.read_csv("data/EMIRATESNBD.csv")
dff1 = pd.read_csv("data/AIRARABIA.csv")

df = dff[2:].reset_index()
df1 = dff1[:-3].reset_index()

df['Year'] = pd.DatetimeIndex(df['Date']).year
df1['Year'] = pd.DatetimeIndex(df1['Date']).year


layout = html.Div([
    html.Div([html.H1("Technical Analysis : Moving Average and Returns ")], style={'textAlign': "center"}),
    html.Div([
        html.Div([
            html.Div([dcc.Graph(id="my-graph")], className="row", style={"margin": "auto"}),
            html.Div([html.Div(dcc.RangeSlider(id="year selection", updatemode='drag',
                                               marks={i: '{}'.format(i) for i in df.Year.unique().tolist()},
                                               min=df1.Year.min(), max=df1.Year.max(), value=[2019, 2020]),
                               className="row", style={"padding-bottom": 30,"padding-top": 30,"width":"60%","margin":"auto"}),
                      html.Span("Moving Average :Select Window Interval", className="row", style={"padding-top": 30}),
                      html.Div(dcc.Slider(id="select-range1", updatemode='drag',
                                          marks={i * 10: str(i * 10) for i in range(0, 21)},
                                          min=0, max=200, value=50), className="row", style={"padding": 10}),
                      html.Div(dcc.Slider(id="select-range2", updatemode='drag',
                                          marks={i * 10: str(i * 10) for i in range(0, 21)},
                                          min=0, max=200, value=170), className="row", style={"padding": 10})

                      ], className="row")
        ], className="six columns",style={"margin-right":0,"padding":0}),
        html.Div([
            dcc.Graph(id="plot-graph")
        ], className="six columns",style={"margin-left":0,"padding":0}),
    ], className="row")
], className="container",style={"width":"100%"}),


@app.callback(
    Output("my-graph", 'figure'),
    [Input("year selection", 'value'),
     Input("select-range1", 'value'),
     Input("select-range2", 'value')])
def update_figure(year, range1, range2):
    dff_apl = df[(df["Year"] >= year[0]) & (df["Year"] <= year[1])]

    rolling_mean1 = dff_apl['Adj Close'].rolling(window=range1).mean()
    rolling_mean2 = dff_apl['Adj Close'].rolling(window=range2).mean()

    trace1 = go.Scatter(x=dff_apl['Date'], y=dff_apl['Adj Close'],
                        mode='lines', name='AIRARABIA')
    trace_a = go.Scatter(x=dff_apl['Date'], y=rolling_mean1, mode='lines', yaxis='y', name=f'Window {range1}')
    trace_b = go.Scatter(x=dff_apl['Date'], y=rolling_mean2, mode='lines', yaxis='y', name=f'Window {range2}')

    layout1 = go.Layout({'title': 'Stock Price With Moving Average',
                         "legend": {"orientation": "h","xanchor":"right"},
                         "xaxis": {
                             "rangeselector": {
                                 "buttons": [
                                     {"count": 6, "label": "6M", "step": "month",
                                      "stepmode": "backward"},
                                     {"count": 1, "label": "1Y", "step": "year",
                                      "stepmode": "backward"},
                                     {"count": 1, "label": "YTD", "step": "year",
                                      "stepmode": "todate"},
                                     {"label": "5Y", "step": "all",
                                      "stepmode": "backward"}
                                 ]
                             }}})

    figure = {'data': [trace1],
              'layout': layout1
              }
    figure['data'].append(trace_a)
    figure['data'].append(trace_b)
    return figure


@app.callback(
    Output("plot-graph", 'figure'),
    [Input("year selection", 'value')])
def update_figure(year):

    dff_apl = df[(df["Year"] >= year[0]) & (df["Year"] <= year[1])]
    dff_sp = df1[(df1["Year"] >= year[0]) & (df1["Year"] <= year[1])]

    stocks = pd.DataFrame({"Date": dff_sp["Date"], "EMIRATESNBD": dff_apl["Adj Close"],
                           "AJMANBANK": dff_sp["Adj Close"]})
    stocks = stocks.set_index('Date')
    stock_return = stocks.apply(lambda x: x / x[0])

    trace2 = go.Scatter(x=dff_sp['Date'], y=stock_return['EMIRATESNBD'], mode='lines', name='EMIRATES NBD Group')
    trace3 = go.Scatter(x=dff_sp['Date'], y=stock_return['AJMANBANK'], mode='lines', name='AJMANBANK')

    layout2 = go.Layout({'title': 'Returns : EMIRATESNBD vs AJMANBANK ',
                         "legend": {"orientation": "h"}, })

    fig = {'data': [trace2],
           'layout': layout2
           }
    fig['data'].append(trace3)
    return fig
