from sqlalchemy import create_engine
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import dash_table
import numpy as np
from dash.dependencies import Input, Output, State


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
color_set = ['#ff3fd8', '#4320ff']

engine = create_engine("mysql+mysqlconnector://root:Abcd12345!!@localhost/tsaListia?host=localhost?port=3306")
conn = engine.connect()

def generate_table(dataframe, page_size=10, nsite = ''):
    if nsite == '':
        dataframe = dataframe
    else:
        dataframe =  dataframe[dataframe['Claim Site'] == nsite]
    return dash_table.DataTable(
        id='dataTable',
        columns=[{
            "name": i,
            "id": i
        } for i in dataframe.columns],
        data=dataframe.to_dict('records'),
        page_action="native",
        page_current=0,
        page_size=page_size,
        style_table = {'overflowX': 'scroll'}
    )


tsa=pd.DataFrame(conn.execute('SELECT * FROM tsa2').fetchall(),columns=pd.read_csv('tsa_claims_dashboard_ujian.csv').columns)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1('Ujian Modul 2 Dashboard TSA'),
    html.P('Created by: Listia'),
    dcc.Tabs(children = 
        [dcc.Tab( value = 'Tab1', label = 'DataFrame Table', children = [
            html.Div([
            html.Div([
                html.P('Claim Site'),
                dcc.Dropdown(value = '',
                id = 'filter-site',
                options = [{'label' : 'All', 'value': ''},
                {'label' : 'Checkpoint', 'value': 'Checkpoint'},
                {'label' : 'Checked Baggage', 'value': 'Checked Baggage'},
                {'label' : 'Motor Vehicle', 'value': 'Motor Vehicle'},
                {'label' : 'Bus Station', 'value': 'Bus Station'},
                {'label' : 'Other', 'value': 'Other'}])
            ], className = 'col-3'),
            html.Br(),
            html.Div([
                html.P('Max Row'),
                dcc.Input(id='filter-row', type='number', value = 10)
                ], className = 'col-3'),
            html.Div(children = [
                html.Button('search', id='filter')
            ], className = 'row col-4'),
            html.Div(id = 'div_table',
            children = [generate_table(tsa, 10)])
            ]
            )]
    ),
    dcc.Tab(label = 'Bar Plot', children = [
            html.Div([
                html.Div([
                    html.P('Y1:'),
                    dcc.Dropdown(
                        id = 'y1-barplot',
                        options = [{'label': 'Claim Amount', 'value': 'Claim Amount'},
                                    {'label': 'Close Amount', 'value': 'Close Amount'}],
                        value = 'Claim Amount'
                    )], className = 'col-3'),
                html.Div([
                    html.P('Y2:'),
                    dcc.Dropdown(
                        id = 'y2-barplot',
                        options = [{'label': 'Claim Amount', 'value': 'Claim Amount'},
                                    {'label': 'Close Amount', 'value': 'Close Amount'}],
                        value = 'Close Amount'
                    )], className = 'col-3'),
                html.Div([
                    html.P('X:'),
                    dcc.Dropdown(
                        id = 'x-barplot',
                        options = [{'label': 'Claim Type', 'value': 'Claim Type'},
                                    {'label': 'Claim Site', 'value': 'Claim Site'},
                                    {'label': 'Disposition', 'value': 'Disposition'}],
                        value = 'Disposition'
                    )], className = 'col-3')],
                    className = 'row'),
                html.Div([
                dcc.Graph(
                    id = 'barplot',
                    figure = {
                        'data' : [
                            go.Bar(
                                x = tsa['Disposition'].unique(),
                                y = tsa.groupby('Disposition')['Claim Amount'].mean(),
                                opacity = 0.8,
                                name = 'Claim Amount'
                            ),
                            go.Bar(
                                x = tsa['Disposition'].unique(),
                                y = tsa.groupby('Disposition')['Close Amount'].mean(),
                                opacity = 0.8,
                                name = 'Close Amount'
                            )]
                        ,'layout': go.Layout(
                            xaxis = {'title': 'Disposition'}, yaxis = {'title': 'US$'},
                            margin = {'l': 40, 'b': 40, 't': 10, 'r': 10},
                            legend = {'x': 0, 'y': 1}, hovermode = 'closest'
                        )
                    }
                )
                ])
    ]),
    dcc.Tab(value = 'Tab3', label = 'Scatter Chart', children = [
        html.Div(children = dcc.Graph(
                id = 'graph-scatter',
                figure = {'data': [
                    go.Scatter(
                        x = tsa[tsa['Claim Type'] == i]['Claim Amount'],
                        y = tsa[tsa['Claim Type'] == i]['Close Amount'],
                        mode='markers',
                        name = '{}'.format(i)
                        ) for i in tsa['Claim Type'].unique()
                    ],
                    'layout':go.Layout(
                        xaxis= {'title': 'Claim Amount'},
                        yaxis={'title': 'Close Amount'},
                        title= 'TSA Scatter Visualization',
                        hovermode='closest'
                    )
                }
            ))]),
    dcc.Tab(value = 'Tab4', label = 'Pie Chart', children = [
        html.Div([
                html.Div([
                    dcc.Dropdown(
                        id = 'mpie',
                        options = [{'label': 'Claim Amount', 'value': 'Claim Amount'},
                                    {'label': 'Close Amount', 'value': 'Close Amount'},
                                    {'label': 'Day Differences', 'value': 'Day Differences'},
                                    {'label': 'Amount Differences', 'value': 'Amount Differences'}],
                        value = 'Claim Amount'
                    )], className = 'col-3'),
            html.Div(children = dcc.Graph(
            id = 'pie chart',
            figure = {
            'data':[
        go.Pie(labels = [i for i in tsa['Claim Type'].unique()], 
        values= [tsa[tsa['Claim Type'] == i]['Claim Amount'].mean() for i in tsa['Claim Type'].unique()]
        )],
        'layout': go.Layout(title = 'Mean Pie Chart')}
    ))
    ]),
    
])
],
    content_style = {
        'fontFamily': 'Arial',
        'borderBottom': '1px solid #d6d6d6',
        'borderLeft': '1px solid #d6d6d6',
        'borderRight': '1px solid #d6d6d6',
        'padding': '44px'
    })],
        style = {
    'maxwidth' : '1200px',
    'margin': '0 auto'
}
)



@app.callback(
    Output(component_id = 'div_table', component_property = 'children'),
    [Input(component_id = 'filter', component_property = 'n_clicks')],
    [State(component_id = 'filter-row', component_property = 'value'),
    State(component_id = 'filter-site', component_property = 'value')])
    

def update_table(n_clicks, row, filtersite):
    children = [generate_table(tsa, row, filtersite)]
    return children

@app.callback(
    Output(component_id = 'barplot', component_property = 'figure'),
    [Input(component_id = 'x-barplot', component_property = 'value'),
    Input(component_id = 'y1-barplot', component_property = 'value'),
    Input(component_id = 'y2-barplot', component_property = 'value')]
)

def update_graph(xbarplot,y1barplot,y2barplot):
    return{
        'data' : [
                    go.Bar(
                            x = tsa[xbarplot].unique(),
                            y = tsa.groupby(xbarplot)[y1barplot].mean(),
                                opacity = 0.8,
                                name = y1barplot
                            ),
                            go.Bar(
                                x = tsa[xbarplot].unique(),
                                y = tsa.groupby(xbarplot)[y2barplot].mean(),
                                opacity = 0.8,
                                name = y2barplot
                            )]
                        ,'layout': go.Layout(
                            xaxis = {'title': xbarplot}, yaxis = {'title': 'US$'},
                            margin = {'l': 40, 'b': 40, 't': 10, 'r': 10},
                            legend = {'x': 0, 'y': 1}, hovermode = 'closest'
                        )
                    }






if __name__ == '__main__':
    app.run_server(debug=True)