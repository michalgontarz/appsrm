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

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
UPLOAD_DIRECTORY = "tmp/project/app_uploaded_files"


if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)



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
            """Przykładowe pliki do pobrania: https://gofile.io/?c=IBAqzP """,
            style = {
                'textAlign': 'center', }
    )
            ],
    ),
    html.Div(
        id='table',
        style={'display': 'none'}
    ),
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
                        html.P ('Enter min value of frequency in MHz'),
                        dcc.Input (id = 'min-freq', placeholder = 'Type here', type = 'text', value = '',
                        ),
                        html.Div (id = 'my-div'),
                        html.P ('Enter max value of frequency in MHz'),
                        dcc.Input (id = 'max-freq', placeholder = 'Type here', type = 'text', value = '',
                        ),
                        html.Div (id = 'my-div2')
                ],
                ),
            style = {'width': '100%', 'display': 'flex', 'flex-direction': 'right', 'justify-content': 'center', 'align': 'center', 'justify': 'center', 'textAlign': 'center'}
            ),
            html.Div (children = [
                dcc.Loading (className = 'dashbio-loading', type = 'circle', children = html.Div (
                id = 'graph-div',
                children = [ dcc.Graph (
                id = 'graph',
                config = {'displayModeBar': True, 'scrollZoom': True, 'toImageButtonOptions': {"width": None, "height": None}},
                ),
                ]
            ),
            )],
        ),
    ]),
    dcc.Tab(label = 'Funkcje analityczne', children = [
        html.P (
            """Wybierz jedną z funkcji aby odczytać wartość skuteczną (RMS), wartość minimalną i maksymalną natężenia pola elektromagnetycznego""",
            style = {
                'textAlign': 'center', }
        ),
        html.Div( className = 'row', children = [
                    dcc.RadioItems(
                                id = 'aggregate-func-type',
                                options = [{'label': i, 'value': i} for i in ['RMS', 'MIN', 'MAX']],
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
                config = {'displayModeBar': True, 'scrollZoom': True, 'toImageButtonOptions': {"width": None, "height": None}},
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
    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip (uploaded_filenames, uploaded_file_contents):
            save_file (name, data)
    dff = file_aggregation()
    print(dff)
    recursively_remove_files(UPLOAD_DIRECTORY)
    return dff.to_json(orient= 'records')

@app.callback(
     Output("graph", "figure"),
    [
     Input('table', 'children'),
     Input('crossfilter-yaxis-type', 'value'),
     Input('min-freq', 'value'),
     Input('max-freq', 'value'),
     ]
)
def update_graph(data, yaxis_type, min_freq, max_freq):
    dff = pd.read_json(data)
    dff.set_index('Frequency Hz', inplace = True)
    print(dff)
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
            yaxis = {'title': 'Electromagnetic Field Strength [V/m]',
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
    dff = pd.read_json(data)
    dff.set_index('Frequency Hz', inplace = True)
    if agg_type == 'RMS':
        newdff = RMS(dff)
        print(newdff)
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
                    'title': 'RMS',
                },
            )
        }
    elif agg_type == 'MAX':
        newdff = MAX (dff)
        print (newdff)
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
                    'title': 'Max value of Electromagnetic Field Strength [V/m]',
                },
            )
        }
    elif agg_type == 'MIN':
        newdff = MIN (dff)
        print (newdff)
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
                    'title': 'Min value of Electromagnetic Field Strength [V/m]',
                },
            )
        }


def file_aggregation():
        filenames = glob.glob (UPLOAD_DIRECTORY + "/*.csv")
        dfObj = pd.DataFrame ([])
        for file in filenames:
            if not fnmatch.fnmatch (file, '*HEADER.csv'):
                df = pd.read_csv (file, delimiter = ';', encoding = "ISO-8859–1")
                loc_date =  df[df.iloc[:,0].str.contains('^Date', regex = True)]
                Date = loc_date.iloc[0][1]
                loc_time = df[df.iloc[:,0].str.contains('^Time', regex = True)]
                Time = loc_time.iloc[0][1]
                Dataframe = Date + " " + Time
                frec_position = df[df.iloc[:, 0].str.contains ('^Frequency', regex = True)]
                frec_position = frec_position.index.item()
                headers = df.iloc[frec_position]
                new_df = pd.DataFrame (df.values[frec_position+1:], columns = headers)
                new_df['Frequency [Hz]'] = new_df['Frequency [Hz]'].astype (float)
                new_df['Value [V/m]'] = new_df['Value [V/m]'].map (lambda p: float (p.replace (',', '.')))
                new_df['Frequency [Hz]'] = new_df['Frequency [Hz]'] * 0.000001
                new_df = new_df.rename (columns = {'Value [V/m]': Dataframe})
                dfObj = pd.concat ([dfObj, new_df], axis = 1)
        dfObj.columns.values[0] = 'Frequency Hz'
        dfObj = dfObj.set_index (['Frequency Hz'])
        if 'Frequency [Hz]' in dfObj.columns:
            dfObj = dfObj.drop (columns = 'Frequency [Hz]')
            dfObj = dfObj.reindex (sorted (dfObj.columns), axis = 1)
            dfObj['Frequency Hz'] = dfObj.index
            return dfObj
        else:
            dfObj['Frequency Hz'] = dfObj.index
            return dfObj

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

def MAX(Dataframeplot):
    dfObj = pd.DataFrame ([])
    for col in Dataframeplot.columns:
        MAX = Dataframeplot[col].max()
        data = {'Date': col, 'MAX': [MAX]}
        df = pd.DataFrame (data)
        dfObj = pd.concat ([dfObj, df], axis = 0)
    dfObj = dfObj.sort_values ('Date')
    return dfObj

def MIN(Dataframeplot):
    dfObj = pd.DataFrame ([])
    for col in Dataframeplot.columns:
        MIN = Dataframeplot[col].min()
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



if __name__ == '__main__':
    app.run_server(debug=True, port=8888)
