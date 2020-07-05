import base64
import os,glob
from flask import Flask, send_from_directory
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import fnmatch
from sqlalchemy import create_engine
import contextlib
from sqlalchemy import MetaData
import pyodbc
#sd


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
UPLOAD_DIRECTORY = "tmp/project/app_uploaded_files"
'''
engine = create_engine (
    'sqlite:///app.db',
    connect_args = {'check_same_thread': False}
)
meta = MetaData()

with contextlib.closing(engine.connect()) as con:
    trans = con.begin()
    for table in reversed(meta.sorted_tables):
        con.execute(table.delete())
    trans.commit()
if not os.path.exists (UPLOAD_DIRECTORY):
    os.makedirs (UPLOAD_DIRECTORY)
'''
SERVER = '172.31.82.179'
DATABASE = 'CamelotWarehouse'
DRIVER = 'SQL Server Native Client 11.0'
USERNAME = 'michal.gontarz'
PASSWORD = 'uh@s5ACX3mc=2wFF'

DATABASE_CONNECTION = f'mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}'
engine1 = create_engine(DATABASE_CONNECTION)
connection = engine1.connect()
data = pd.read_sql_query(
    'select * from Avalon..tmp_RaportDzSprz_Kampanie where [month] = convert(varchar(7), (select top 1[Day] from ['
    'CamelotWarehousePlayground].[dbo].[Params_DaysOff] d2 with(nolock) where d2.[Day] < cast(getdate() as date) and '
    'd2.[State] = \'WorkDay\' order by[Day] desc), 120) ', connection)



df4 = data


server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=external_stylesheets)

@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)


app.layout = html.Div( children = [
    html.H2("Aplikacja do analizy danych pomiarowych z monitoringu Pola Elektromagnetycznego",
            style = {
                'textAlign': 'center',}
            ),
    html.P("{CRM}".format(CRM=df4)),
    html.P(
             """Użyj przycisku poniżej aby wczytać dane do analizy z pliku .csv""",
        style = {
            'textAlign': 'center',}
    ),

    html.Div(title = 'Upload data to view here', className = 'row', id = 'upload-container', children = [
            dcc.Upload (html.Button ('Wczytaj pliki',
                                     style={'width': '30%', 'display': 'block', 'vertical-align': 'middle', 'margin': 'auto',
                                            'background-color':'#e6f0ff'}),
            id = "upload-data",
            multiple = True,
),
    html.P (
            """Przykładowe pliki do pobrania: https://www.dropbox.com/sh/j2h6jw9h6h124y4/AAAZa5M5kfNJ3L0BJ4s6IN6Ka?dl=0 """,
            style = {
                'textAlign': 'center', }
    )
            ],
    ),
        html.Div(id ='table',
                 style={'color': 'red'}),



    html.P(),
    dcc.Tabs([
        dcc.Tab(label='Widok widma', children=[
            html.Div (
                className = "row",
                children =
                html.Div (className = 'six-columns', children = [
                        dcc.RadioItems (
                                id = 'crossfilter-yaxis-type',
                                options = [{'label': i, 'value': i} for i in ['Linear', 'log']],
                                value = 'log',
                                labelStyle={"display": "inline-block"},
                        ),
                        html.Div(className = 'row', children = [
                            dcc.RadioItems(
                                id = 'func-type',
                                options = [{'label': i, 'value': i} for i in ['ALL','ACT', 'MIN', 'MAX', 'AVG', 'MAX_AVG', 'MIN_AVG']],
                                value = 'ALL',
                                labelStyle = {"display": "inline-block"},
                            ),
                        ],),
                        html.P ('Wprowadź wartość min częstotliwości w MHz', style={'width': '22%', 'float': 'left', 'display': 'inline-block'}),
                        dcc.Input (id = 'min-freq', placeholder = 'Wpisz tutaj', type = 'text', value = '',
                        style={'width': '15%', 'float': 'left', 'display': 'inline-block'}),
                        html.Div (id = 'my-div'),
                        html.P ('Wprowadź wartość max częstotliwości w MHz', style={'width': '23%', 'float': 'left', 'display': 'inline-block'}),
                        dcc.Input (id = 'max-freq', placeholder = 'Wpisz tutaj', type = 'text', value = '', style={'width': '15%', 'float': 'left', 'display': 'inline-block'}
                        ),
                        html.Div (id = 'my-div2'),
                ], style={'width': '50%', 'flush': 'right','align': 'center' ,'display': 'inline-block'}
                ),
            ),
            html.Div (children = [
                dcc.Loading (className = 'dashbio-loading', type = 'circle', children = html.Div (
                id = 'graph-div',
                children = [ dcc.Graph (
                id = 'graph',
                config = {'displayModeBar': True,'displaylogo' : False, 'scrollZoom': True, 'toImageButtonOptions': {"width": None, "height": None}},
                ),
                ]
            ),
            )],
        ),
    ]),
    dcc.Tab(label = 'Funkcje analityczne', children = [
        html.P (
            """Wybierz jedną z funkcji aby odczytać wartość skuteczną (RMS), wartość minimalną, maksymalną i średnią natężenia pola elektrycznego""",
            style = {
                'textAlign': 'center', }
        ),
        html.Div( className = 'row', children = [
                    dcc.RadioItems(
                                id = 'aggregate-func-type',
                                options = [{'label': i, 'value': i} for i in ['RMS', 'MIN', 'MAX', 'AVG']],
                                value = 'RMS',
                                labelStyle={"display": "inline-block"},
                        ),
        ],
        style={'textAlign': 'center'}),
        html.Div (children = [
                dcc.Loading (className = 'dashbio-loading', type = 'circle', children = html.Div (
                id = 'graph-div2',
                children = [ dcc.Graph (
                id = 'aggregate-graph',
                config = {'displayModeBar': True, 'displaylogo' : False, 'scrollZoom': True, 'toImageButtonOptions': {"width": None, "height": None}},
                ),
                ]
            ),
                             ),
    ]),
        ]),
]),
])

def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


@app.callback(
    Output("table", "children"),
    [Input("upload-data", "filename"), Input("upload-data", "contents")],
)
def save_files(uploaded_filenames, uploaded_file_contents):
    try:
        if uploaded_filenames is not None and uploaded_file_contents is not None:
            for name, data in zip(uploaded_filenames, uploaded_file_contents):
                save_file(name, data)
        dff =  file_aggregation()
        recursively_remove_files(UPLOAD_DIRECTORY)
        return dff.to_sql('dataframe', engine, if_exists = 'replace', index = False)
    except Exception as e:
        return html.Div([
            html.Div('Wystąpił błąd w odczycie pliku/plików .csv, sprawdź pliki.')
                         ])

@app.callback(
     Output("graph", "figure"),
    [
     Input('table', 'children'),
     Input('crossfilter-yaxis-type', 'value'),
     Input('min-freq', 'value'),
     Input('max-freq', 'value'),
     Input('func-type', 'value')
     ]
)
def update_graph(data, yaxis_type, min_freq, max_freq, func_type):
    dff = pd.read_sql_table('dataframe', con = engine)
    dff.set_index('Frequency Hz', inplace = True)
    if func_type == 'AVG': dff = dff.filter(regex = 'AVG')
    if func_type == 'ACT': dff = dff.filter(regex = 'ACT')
    if func_type == 'MIN': dff = dff.filter(regex = 'MIN')
    if func_type == 'MAX': dff = dff.filter(regex = 'MAX')
    if func_type == 'MAX_AVG': dff = dff.filter(regex = 'MAX_AVG')
    if func_type == 'MIN_AVG': dff = dff.filter(regex = 'MIN_AVG')

    traces = []
    for col in dff.columns:
        d = dict (x = dff.index , y = dff[col].values, mode = 'lines', name = col,
                  hovertemplate = "</br>Frequency: %{x} </br>Value [V/m] %{y}"
                  )
        traces.append (d)
    return {
        'data': traces,
        'layout': dict (
            xaxis = {'title': 'Frequency [MHz]',
                     'range': [min_freq, max_freq],
                     'autorange': 'true',
                     'animate': False
                     },
            yaxis = {'title': 'E-Field Strength [V/m]',
                     'type': 'log' if yaxis_type == 'log' else 'Linear',
                     'autorange': 'true',
                     'animate': False
                     },
        )
    }
@app.callback(
     Output("aggregate-graph", "figure"),
    [
     Input('table', 'children'),
     Input('aggregate-func-type', 'value')
    ]
)
def update_graph_aggregate(data, agg_type):
    dff = pd.read_sql_table('dataframe', con = engine)
    dff.set_index('Frequency Hz', inplace = True)
    if agg_type == 'RMS':
        newdff = RMS(dff)
        return {
            'data': [dict (
                x = newdff['Date'],
                y = newdff['RMS'],
                mode = 'markers',
                marker = dict(
                    color= 'black',
                    symbol= 'line-ew',
                    size = 20,
                    line = dict (
                        color = 'black',
                        width=1,
                    ),
                ),
            )],
            'layout': dict (
                xaxis = {
                    'title': 'Date',
                },
                yaxis = {
                    'title': 'RMS of E-Field',
                },
            )
        }
    elif agg_type == 'MAX':
        newdff = MAX (dff)
        return {
            'data': [dict (
                x = newdff['Date'],
                y = newdff['MAX'],
                mode = 'markers',
                marker = dict (
                    color = 'black',
                    symbol = 'line-ew',
                    size = 20,
                    line = dict (
                        color = 'black',
                        width = 1,
                    ),
                ),
            )],
            'layout': dict (
                xaxis = {
                    'title': 'Date',
                },
                yaxis = {
                    'title': 'Max value of E-Field Strength [V/m]',
                },
            )
        }
    elif agg_type == 'MIN':
        newdff = MIN (dff)
        return {
            'data': [dict (
                x = newdff['Date'],
                y = newdff['MIN'],
                mode = 'markers',
                marker = dict (
                    color = 'black',
                    symbol = 'line-ew',
                    size = 20,
                    line = dict (
                        color = 'black',
                        width = 1,
                    ),
                ),
            )],
            'layout': dict (
                xaxis = {
                    'title': 'Date',
                },
                yaxis = {
                    'title': 'Min value of E-Field Strength [V/m]',
                },
            )
        }
    else:
        newdff = AVG (dff)
        return {
            'data': [dict (
                x = newdff['Date'],
                y = newdff['AVG'],
                mode = 'markers',
                marker = dict (
                    color = 'black',
                    symbol = 'line-ew',
                    size = 20,
                    line = dict (
                        color = 'black',
                        width = 1,
                    ),
                ),
            )],
            'layout': dict (
                xaxis = {
                    'title': 'Date',
                },
                yaxis = {
                    'title': 'Avg value of E-Field Strength [V/m]',
                },
            )
        }


def file_aggregation():
    try:
        filenames = glob.glob (UPLOAD_DIRECTORY + "/*.csv")
        print(UPLOAD_DIRECTORY)
        dfObj = pd.DataFrame ([])
        colnames = '12345'
        for file in filenames:
            if not fnmatch.fnmatch (file, '*HEADER.csv'):
                df = pd.read_csv(file, delimiter = ';', encoding = "ISO-8859–1", header=None, names = colnames, na_values='-', sep = ',')
                df = df.fillna(0)
                result_type = df[df.iloc[:,0].str.contains('^Result', regex = True)]
                df = df.loc[:, (df != 0).any(axis = 0)]
                dfcol=len(df.columns)
                loc_date =  df[df.iloc[:,0].str.contains('^Date', regex = True)]
                Date = loc_date.iloc[0, 1]
                loc_time = df[df.iloc[:,0].str.contains('^Time', regex = True)]
                Time = loc_time.iloc[0][1]
                Dataframe = Date + " " + Time
                if dfcol == 2:
                    result_type1 = result_type.iloc[0][1]
                    frec_position = df[df.iloc[:, 0].str.contains('^Frequency', regex = True)]
                    frec_position = frec_position.index.item()
                    headers = df.iloc[frec_position]
                    new_df = pd.DataFrame(df.values[frec_position + 1:], columns = headers)
                    new_df = new_df.iloc[:, 0:dfcol]
                    new_df['Frequency [Hz]'] = new_df['Frequency [Hz]'].replace(',', '.', regex=True).astype(float)
                    new_df['Frequency [Hz]'] = new_df['Frequency [Hz]'] * 0.000001
                    new_df['Value [V/m]'] = new_df['Value [V/m]'].replace(',', '.', regex=True).astype(float)
                    new_df['Value [V/m]'] = new_df['Value [V/m]'].apply(lambda x: round(x, 7))
                    new_df = new_df.rename(columns = {'Value [V/m]': Dataframe + " " + result_type1})
                    dfObj = pd.concat([dfObj, new_df], axis = 1)
                if dfcol == 3:
                    result_type1 = result_type.iloc[0][1]
                    result_type2 = result_type.iloc[0][2]
                    frec_position = df[df.iloc[:, 0].str.contains('^Frequency', regex = True)]
                    frec_position = frec_position.index.item()
                    headers = df.iloc[frec_position]
                    new_df = pd.DataFrame(df.values[frec_position + 1:], columns = headers)
                    new_df = new_df.iloc[:, 0:dfcol]
                    new_df = df_column_uniquify(new_df)
                    new_df['Value [V/m]'] = new_df['Value [V/m]'].replace(',', '.', regex=True).astype(float)
                    new_df['Value [V/m]_1'] = new_df['Value [V/m]_1'].replace(',', '.', regex = True).astype(float)
                    new_df['Value [V/m]'] = new_df['Value [V/m]'].apply(lambda x: round(x, 7))
                    new_df['Value [V/m]_1'] = new_df['Value [V/m]_1'].apply(lambda x: round(x, 7))
                    new_df = new_df.rename(columns = {'Value [V/m]': Dataframe + " " + result_type1, 'Value [V/m]_1': Dataframe + " " + result_type2})
                    new_df['Frequency [Hz]'] = new_df['Frequency [Hz]'].replace(',', '.', regex=True).astype(float)
                    new_df['Frequency [Hz]'] = new_df['Frequency [Hz]'] * 0.000001
                    dfObj = pd.concat([dfObj, new_df], axis = 1)
                if dfcol == 4:
                    result_type1 = result_type.iloc[0][1]
                    result_type2 = result_type.iloc[0][2]
                    result_type3 = result_type.iloc[0][3]
                    frec_position = df[df.iloc[:, 0].str.contains('^Frequency', regex = True)]
                    frec_position = frec_position.index.item()
                    headers = df.iloc[frec_position]
                    new_df = pd.DataFrame(df.values[frec_position + 1:], columns = headers)
                    new_df = new_df.iloc[:, 0:dfcol]
                    new_df = df_column_uniquify(new_df)
                    new_df['Value [V/m]'] = new_df['Value [V/m]'].replace(',', '.', regex=True).astype(float)
                    new_df['Value [V/m]_1'] = new_df['Value [V/m]_1'].replace(',', '.', regex = True).astype(float)
                    new_df['Value [V/m]_2'] = new_df['Value [V/m]_2'].replace(',', '.', regex = True).astype(float)
                    new_df['Value [V/m]'] = new_df['Value [V/m]'].apply(lambda x: round(x, 7))
                    new_df['Value [V/m]_1'] = new_df['Value [V/m]_1'].apply(lambda x: round(x, 7))
                    new_df['Value [V/m]_2'] = new_df['Value [V/m]_2'].apply(lambda x: round(x, 7))
                    new_df = new_df.rename(columns = {'Value [V/m]': Dataframe + " " + result_type1, 'Value [V/m]_1': Dataframe + " " + result_type2,'Value [V/m]_2': Dataframe + " " + result_type3})
                    print(new_df)
                    new_df['Frequency [Hz]'] = new_df['Frequency [Hz]'].replace(',', '.', regex=True).astype(float)
                    new_df['Frequency [Hz]'] = new_df['Frequency [Hz]'] * 0.000001
                    dfObj = pd.concat([dfObj, new_df], axis = 1)
                if dfcol == 5:
                    result_type1 = result_type.iloc[0][1]
                    result_type2 = result_type.iloc[0][2]
                    result_type3 = result_type.iloc[0][3]
                    result_type4 = result_type.iloc[0][4]
                    frec_position = df[df.iloc[:, 0].str.contains('^Frequency', regex = True)]
                    frec_position = frec_position.index.item()
                    headers = df.iloc[frec_position]
                    new_df = pd.DataFrame(df.values[frec_position + 1:], columns = headers)
                    new_df = new_df.iloc[:, 0:dfcol]
                    new_df = df_column_uniquify(new_df)
                    new_df['Value [V/m]'] = new_df['Value [V/m]'].replace(',', '.', regex=True).astype(float)
                    new_df['Value [V/m]_1'] = new_df['Value [V/m]_1'].replace(',', '.', regex = True).astype(float)
                    new_df['Value [V/m]_2'] = new_df['Value [V/m]_2'].replace(',', '.', regex = True).astype(float)
                    new_df['Value [V/m]_3'] = new_df['Value [V/m]_3'].replace(',', '.', regex = True).astype(float)
                    new_df['Value [V/m]'] = new_df['Value [V/m]'].apply(lambda x: round(x, 8))
                    new_df['Value [V/m]_1'] = new_df['Value [V/m]_1'].apply(lambda x: round(x, 8))
                    new_df['Value [V/m]_2'] = new_df['Value [V/m]_2'].apply(lambda x: round(x, 8))
                    new_df['Value [V/m]_3'] = new_df['Value [V/m]_3'].apply(lambda x: round(x, 8))
                    new_df = new_df.rename(columns = {'Value [V/m]': Dataframe + " " + result_type1,
                                                      'Value [V/m]_1': Dataframe + " " + result_type2,
                                                      'Value [V/m]_2': Dataframe + " " + result_type3,
                                                      'Value [V/m]_3': Dataframe + " " + result_type4})
                    new_df['Frequency [Hz]'] = new_df['Frequency [Hz]'].replace(',', '.', regex=True).astype(float)
                    new_df['Frequency [Hz]'] = new_df['Frequency [Hz]'] * 0.000001
                    dfObj = pd.concat([dfObj, new_df], axis = 1)
        dfObj.columns.values[0] = 'Frequency Hz'
        dfObj = dfObj.set_index(['Frequency Hz'])
        print(dfObj)
        if 'Frequency [Hz]' in dfObj.columns:
            dfObj = dfObj.drop (columns = 'Frequency [Hz]')
            dfObj = dfObj.reindex (sorted (dfObj.columns), axis = 1)
            dfObj['Frequency Hz'] = dfObj.index
            return dfObj
        else:
            dfObj['Frequency Hz'] = dfObj.index
            return dfObj
    except Exception as e:
        print(e)


def RMS(Dataframeplot):
        dfObj = pd.DataFrame ([])
        for col in Dataframeplot.columns:
            square = Dataframeplot[col]**2
            total = Dataframeplot[col].shape
            sum = square.sum()
            div = sum/total
            RMS = np.sqrt(div)
            RMS  = float("%0.3f"%RMS)
            data = {'Date':col, 'RMS':[RMS]}
            df = pd.DataFrame(data)
            dfObj = pd.concat ([dfObj, df], axis = 0)
        dfObj = dfObj.sort_values ('Date')
        return dfObj


def AVG(Dataframeplot):
    dfObj = pd.DataFrame ([])
    for col in Dataframeplot.columns:
        totalsum = Dataframeplot[col]
        total = Dataframeplot[col].shape
        sum = totalsum.sum ()
        AVG = sum / total
        AVG = float ("%0.3f" % AVG)
        data = {'Date': col, 'AVG': [AVG]}
        df = pd.DataFrame (data)
        dfObj = pd.concat ([dfObj, df], axis = 0)
    dfObj = dfObj.sort_values ('Date')
    return dfObj

def MAX(Dataframeplot):
    dfObj = pd.DataFrame ([])
    for col in Dataframeplot.columns:
        MAX = Dataframeplot[col].max()
        MAX = float ("%0.3f" % MAX)
        data = {'Date': col, 'MAX': [MAX]}
        df = pd.DataFrame (data)
        dfObj = pd.concat ([dfObj, df], axis = 0)
    dfObj = dfObj.sort_values ('Date')
    return dfObj

def MIN(Dataframeplot):
    dfObj = pd.DataFrame ([])
    for col in Dataframeplot.columns:
        MIN = Dataframeplot[col].min()
        MIN = float ("%0.3f" % MIN)
        data = {'Date': col, 'MIN': [MIN]}
        df = pd.DataFrame (data)
        dfObj = pd.concat ([dfObj, df], axis = 0)
    dfObj = dfObj.sort_values ('Date')
    return dfObj

def recursively_remove_files(f):
    if os.path.isfile(f):
        os.unlink(f)
    elif os.path.isdir(f):
        for fi in os.listdir(f):
            recursively_remove_files(os.path.join(f, fi))

def df_column_uniquify(df):
    df_columns = df.columns
    new_columns = []
    for item in df_columns:
        counter = 0
        newitem = item
        while newitem in new_columns:
            counter += 1
            newitem = "{}_{}".format(item, counter)
        new_columns.append(newitem)
    df.columns = new_columns
    return df

if __name__ == '__main__':
    app.run_server(debug=True, port=8888)
