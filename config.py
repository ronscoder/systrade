import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_table as dt
from libs.pubsub import get_ps_2
import dash_core_components as dcc

rconfig = get_ps_2()

app = dash.Dash(__name__, prevent_initial_callbacks=True,
                assets_folder="assets", title='systrade config')


def getconfig():
    configs = rconfig.hgetall('configs')
    return [dict(configname=k, value=configs[k]) for k in configs]


def addConfig(key, value):
    rconfig.hset('configs', {key: value})


def delConfig(key):
    rconfig.r.hdel('configs', key)


app.layout = html.Div([
    html.Div(1, id='xconfigchanged', hidden=True),
    html.Div(id='dummy2', hidden=True),
    html.Div([
        html.H1('Systrade configurations', className='max-w-sm'),
        # html.Button('update', id='btn_updateConfig',
        #             className='p-4 shadow-md h-full'),
    ], className='flex justify-between items-center mt-8'),
    html.Hr(),
    html.Div(
        [dcc.Input(id='new_configkey', placeholder='config key',  className='border'),
         dcc.Input(id='new_configvalue', placeholder='config value',
                   className='border'),
         html.Button('Add', id='btn_add_config', className='border px-4 mx-2')]
    ),
    html.Div(
        dt.DataTable(
            id='tbl_config',
            columns=[dict(id='configname', name='configname', editable=False),
                     dict(id='value', name='value', editable=True)],
            row_deletable=True
        ),
        className='w-1/2 overflow-auto h-1/2 m-auto'
    ),
])


@app.callback(Output('new_configkey', 'value'),
              Input('xconfigchanged', 'children'),
              )
def clearkey(xstate):
    return ''

@app.callback(Output('new_configvalue', 'value'),
              Input('xconfigchanged', 'children')
              )
def clearvalue(xstate):
    return ''

@app.callback(Output('xconfigchanged', 'children'),
              Input('btn_add_config', 'n_clicks'),
              State('new_configkey', 'value'),
              State('new_configvalue', 'value'),
              State('xconfigchanged', 'children')
              )
def addnewConfig(add_clicks, newkey, newvalue, xstate):
    if(add_clicks):
        if(newkey and newvalue):
            addConfig(newkey, newvalue)
    return add_clicks

@app.callback(
    Output('tbl_config', 'data'),
    Input('tbl_config', 'data_previous'),
    Input('xconfigchanged', 'children'),
    State('tbl_config', 'data'),
)
def updateConfig(previous, changed, data):
    print('updating...')
    if(previous):
        deleted = [k['configname'] for k in previous if k['configname']
                   not in [x['configname'] for x in data]]
        for k in deleted:
            delConfig(k)
        configs = {r['configname']: r['value'] for r in data}
        rconfig.hset('configs', configs)
    return getconfig()


if(__name__ == '__main__'):
    app.run_server(debug=True, port=8050)
