import datetime
import dash
from dash.dependencies import Input, Output, State
from dash_core_components.Interval import Interval
import dash_html_components as html
import dash_core_components as dcc
from numpy.lib.shape_base import tile
import plotly.graph_objects as go
from pandas import DataFrame
# from libs.calculation import Calculation
from libs.calculationfft import Calculation
from dash.exceptions import PreventUpdate

from libs.pubsub import get_ps_1

r = get_ps_1()

app = dash.Dash(__name__)


channel = 'CALC-NIFTY 50-LTF'


def getgraph():
    data = r.get(channel)
    # print(data)
    if(data):
        calc: Calculation = data['calc']['LTF']
        n = 250
        ohlcs = calc.ohlcs
        ohlcs = calc.ohlcs[-n:]
        # import pdb; pdb.set_trace()
        sups = calc.shistory[-n:]
        ress = calc.rhistory[-n:]
        psup = calc.psup
        pres = calc.pres
        yt = calc.yt
        fig = go.Figure()
        if(not ohlcs is None):
            fig.add_trace(go.Candlestick(
                x=ohlcs.index, open=ohlcs['Open'], high=ohlcs['High'], low=ohlcs['Low'], close=ohlcs['Close'], name='ohlc'))
            fig.add_trace(go.Scatter(
                x=yt[0], y=yt[1], name='yt'))
        if(sups):
            # print(psup(0)==sups[-1][1]['value'])
            # print(psup(0),sups[-1][1]['value'])
            fig.add_trace(go.Scatter(x=[x[0] for x in sups], y=[x[1]['value']
                                                                for x in sups], name='support', mode='lines'))
        if(ress):
            fig.add_trace(go.Scatter(x=[x[0] for x in ress], y=[x[1]['value']
                                                                for x in ress], name='resistance', mode='lines'))
        if(psup):
            fig.add_trace(go.Scatter(x=ohlcs.index[:-1], y=psup(range(-(len(ohlcs)),-1)), name='psup',
                         line = dict(color='royalblue', width=2, dash='dash')))
        if(pres):
            fig.add_trace(go.Scatter(x=ohlcs.index[:-1], y=pres(range(-(len(ohlcs)),-1)), name='pres',
                         line = dict(color='firebrick', width=2, dash='dash')))
        if(calc.maximas):
            fig.add_trace(go.Scatter(x=[x[0] for x in calc.maximas],
                                     y=[x[1] for x in calc.maximas], mode='markers', marker=dict(size=12, color='#af0000'), name='maximas'))

        if(calc.minimas):
            fig.add_trace(go.Scatter(x=[x[0] for x in calc.minimas],
                                     y=[x[1] for x in calc.minimas], mode='markers', marker=dict(size=12, color='#00af00'), name='minimas'))
        # if(calc.maxima):
        #     fig.add_trace(go.Scatter(x=[calc.maxima[0]],
        #                              y=[calc.maxima[1]], mode='markers', marker=dict(size=8, color='#0000ff'), name='maxima'))
        # if(calc.minima):
        #     fig.add_trace(go.Scatter(x=[calc.minima[0]],
        #                              y=[calc.minima[1]], mode='markers', marker=dict(size=8, color='#00ff00'), name='minima'))
        if(calc.maxima and calc.minima):
            fig.add_shape(type='line', x0=calc.maxima[0], y0=calc.maxima[1], x1=calc.minima[0], y1=calc.minima[1], name='fib retr')

        if(calc.retracement_levels):
            for level in calc.retracement_levels:
                # for level in [1,2,3]:
                # x = [ohlcs.index[-10:]]
                # y = [level]*10
                # print(x,y)
                # fig.add_trace(go.Scatter(x=x, y=y, mode="lines", marker=dict(color="#000000")))
                # fig.add_hline(level, exclude_empty_subplots=True)
                ''
                # fig.add_shape(
                #     type='line', x0=min(calc.maxima[0], calc.minima[0]), y0=level, x1=ohlcs.index[-1], y1=level, )
        return fig


app.layout = html.Div(children=[
    dcc.Interval(id='refresher', interval=5*1000, disabled=False),
    html.Div(dcc.Graph(id='graph1'), className='w-2/3'),
    html.Button('Pause', id='btn_pause',
                className='p-2 border-2 border-solid border-blue-600')
])


@app.callback(Output('refresher', 'disabled'), Input('btn_pause', 'n_clicks'), State('refresher', 'disabled'))
def pause(n_clicks, isDisabled):
    if(n_clicks is None):
        return False
    return not isDisabled


@app.callback(Output('btn_pause', 'children'), Input('refresher', 'disabled'))
def updatebtn(isDisabled):
    if(isDisabled):
        return 'Paused'
    return 'Pause'


@app.callback(Output('graph1', 'figure'), Input(component_id='refresher', component_property='n_intervals'))
def updategraph1(ninterval):
    fig = getgraph()
    # fig.update_layout(title=dict(text=channel),
    #                   xaxis=dict(rangeslider=dict(visible=False)))
    if(fig):
        fig.update_layout(title_text=channel,
                        xaxis_rangeslider_visible=False)
        return fig
    else:
        raise PreventUpdate


if(__name__ == '__main__'):
    print('running...')
    app.run_server(debug=True, port='8051')


'''
import plotly.graph_objects as go
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')

fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                open=df['AAPL.Open'], high=df['AAPL.High'],
                low=df['AAPL.Low'], close=df['AAPL.Close'])
                     ])

fig.update_layout(xaxis_rangeslider_visible=False)
fig.show()

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

import pandas as pd
from datetime import datetime

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Checklist(
        id='toggle-rangeslider',
        options=[{'label': 'Include Rangeslider', 
                  'value': 'slider'}],
        value=['slider']
    ),
    dcc.Graph(id="graph"),
])

@app.callback(
    Output("graph", "figure"), 
    [Input("toggle-rangeslider", "value")])
def display_candlestick(value):
    fig = go.Figure(go.Candlestick(
        x=df['Date'],
        open=df['AAPL.Open'],
        high=df['AAPL.High'],
        low=df['AAPL.Low'],
        close=df['AAPL.Close']
    ))

    fig.update_layout(
        xaxis_rangeslider_visible='slider' in value
    )

    return fig

app.run_server(debug=True)
DOWNLOAD
Include Rangeslider

import plotly.graph_objects as go
import pandas as pd


df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')

fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                open=df['AAPL.Open'], high=df['AAPL.High'],
                low=df['AAPL.Low'], close=df['AAPL.Close'])
                      ])

fig.update_layout(
    title='The Great Recession',
    yaxis_title='AAPL Stock',
    shapes = [dict(
        x0='2016-12-09', x1='2016-12-09', y0=0, y1=1, xref='x', yref='paper',
        line_width=2)],
    annotations=[dict(
        x='2016-12-09', y=0.05, xref='x', yref='paper',
        showarrow=False, xanchor='left', text='Increase Period Begins')]
)

fig.show()
'''
