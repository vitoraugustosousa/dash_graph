import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import plotly.graph_objs as go

ext_style = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets = ext_style)

df = pd.read_csv('/Users/vitorsousa/Desktop/Project/Datasets/locations_capado.csv')

available_months = df.Crash_Month.unique()

crash_type = df.iloc[:, -12:].columns.tolist()

days_of_week = df.Crash_Day_Of_Week.unique()

app.layout = html.Div(children = [
    html.H1(children = 'Grafico de cuh eh rola'),
    html.Div(children = 'DSaulo Cabecao'),
    
    
    html.Div([
        html.Label('Select the type of Crash'),
        dcc.Dropdown(
            id = 'crash_dropdown',
            options = [{'label' : i, 'value' : i} for i in crash_type],
            value = 'Count_Casualty_Fatality',
        )
    

    ]),
    
    html.Div([
        html.Label('Select the months'),
        dcc.Dropdown(
            id = 'months_dropdown',
            options = [{'label' : i, 'value' : i} for i in available_months],
            value = ['January', 'June'],
            multi = True
            )
    ]),
    
    html.Div([
        dcc.Graph(
        id = 'grafico',
        )  
        
    ]),
    
    html.Div(
        dcc.Slider(
            id = 'year_slider',
            min = df['Crash_Year'].min(),
            max = df['Crash_Year'].max(),
            value = df['Crash_Year'].max(),
            marks = {str(year) : str(year) for year in df['Crash_Year'].unique()})
        )  
])


@app.callback(
    dash.dependencies.Output('grafico', 'figure'),
    [dash.dependencies.Input('crash_dropdown', 'value'),
    dash.dependencies.Input('months_dropdown', 'value'),
    dash.dependencies.Input('year_slider', 'value')])
def update_graph(yaxis_option, months, year_value):
    
    dff = df[df['Crash_Year'] == year_value]
    dff2 = dff[dff['Crash_Month'].isin(months)]
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    yvalues = dff2.groupby('Crash_Day_Of_Week')[yaxis_option].sum()
    dfYvalues = pd.DataFrame(yvalues)
    dfYvalues.reset_index(inplace = True)
    dfYvalues['Crash_Day_Of_Week'] = dfYvalues['Crash_Day_Of_Week'].astype('category', 
                                                                           categories=days, ordered=True)
    dfYvalues.sort_values('Crash_Day_Of_Week', inplace = True)
        
    return {
        'data' : [go.Bar(
            x = dfYvalues['Crash_Day_Of_Week'],
            y = dfYvalues[yaxis_option]
        )],
        
        'layout' : go.Layout(
            xaxis = {
                'title' : 'Days of the week'
            },
            yaxis = {'title' : yaxis_option})
    }


if __name__ == '__main__':
    app.run_server(debug = True)