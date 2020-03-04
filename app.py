import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from plotly.subplots import make_subplots

import pandas as pd
import numpy as np


ext_style = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__) #external_stylesheets = ext_style)

server = app.server


#Importing the DataFrames

df_locations = pd.read_csv('locations_filtered.csv')

#df_vehicles_m = pd.read_csv('vehicles_filtered.csv')

#df_factors_m = pd.read_csv('factors_filtered.csv')

#df_demographics = pd.read_csv('demographics_filtered.csv')

#df_casualties = pd.read_csv('casualties_filtered.csv')


#Create helper lists and columns

df_locations['text'] = df_locations.apply(lambda x : '<b>Crash Severity:</b> <i>{}</i><br><b>Crash Year:</b> <i>{}</i><br><b>Crash Month:</b> <i>{}</i><br><b>Crash Day of Week:</b> <i>{}</i><br><b>Crash Hour:</b><i>{}</i><br><b>Crash Suburb:</b> <i>{}</i><br><b>Crash Street:</b> <i>{}</i><br><b>Crash Nature:</b> <i>{}</i><br><b>Surface Condition:</b> <i>{}</i><br><b>Atmospheric Condition:</b> <i>{}</i><br><b>Lighting Condition:</b> <i>{}</i><br><b>Description:</b> <i>{}</i><br>'.format(x['Crash_Severity'], x['Crash_Year'], 
                                        x['Crash_Month'], x['Crash_Day_Of_Week'], x['Crash_Hour'], x['Loc_ABS_Statistical_Area_2'], x['Crash_Street'], x['Crash_Nature'], x['Crash_Road_Surface_Condition'], 
                                        x['Crash_Atmospheric_Condition'], x['Crash_Lighting_Condition'], x['Crash_DCA_Description']), axis = 1)


days_of_week = df_locations.Crash_Day_Of_Week.unique()
months = df_locations.Crash_Month.unique()
regions2 = sorted(df_locations.Loc_ABS_Statistical_Area_3.unique())
hours = sorted(df_locations.Crash_Hour.unique())
severity = sorted(df_locations.Crash_Severity.unique())
nature = sorted(df_locations.Crash_Nature.unique())


#Create Controls


#Helper Functions


app.layout = html.Div(
    [
        dcc.Store(id = 'agregate_data'),
        html.Div(id = 'output_clientside'),
        html.Div(
            [
                html.H1(
                    children = 'Brisbane crash incident analysis',
                ),
                html.H5(
                    children = 'A description and analysis of Brisbane crash incidents using Python, Plotly, Dash, Html and CSS.',
                ),
                html.Div([
                    html.Div([
                        html.Span('by Vitor Sousa'),
                        html.A([
                            html.Img(
                                src='https://www.spiner.com.br/wp-content/uploads/2019/02/midias-sociais-linkedin-icon.png',
                                style={
                                    'height' : '24px',
                                    'width' : '24px',
                                }
                            )
                            ], href='https://www.linkedin.com/in/vitor-sousa-a114a07b', target="_blank")
                        ]),
                    
                    html.P('Feb 20, 2020', style = {'font-size' : '12px'}),

                ], className = 'contact')
            ],
            id = 'header',
            className = 'header',
        ),

        html.Div(
            [
                html.H4('Overview'),
                html.P('This dashboard presents information on location and characteristics of crashes ocurrend in Brisbane for all reported Road Traffic Crashes occurred from 1 January 2001 to 31 December 2018, Fatal Road Traffic Crashes to 31 December 2018, Hospitalisation, Medical Treatment and Minor Injury Crashes to 31 December 2018 and Property Damage only crashes to 31 December 2010. The main purpose is to identify and analyse the main factors and trends related to these incidents.'),
                html.P('All the information used (including the datasets) were retrieved from Queensland Goverment Open Data Portal > Crash Data from Queensland roads.'),
                html.Div([html.Span('Source: ', style = {'font-style' : 'italic', 'font-size' : '12px'}), html.A('https://www.data.qld.gov.au/dataset/crash-data-from-queensland-roads', href = 'https://www.data.qld.gov.au/dataset/crash-data-from-queensland-roads', target="_blank", className = 'links')]),
                html.Div([
                    html.A('Road crash locations Dataset', href='https://www.data.qld.gov.au/dataset/crash-data-from-queensland-roads/resource/e88943c0-5968-4972-a15f-38e120d72ec0', target="_blank", className = 'links'),
                    html.A('Road Casualties Dataset', href='https://www.data.qld.gov.au/dataset/crash-data-from-queensland-roads/resource/3fc53539-d529-4c1d-85f8-6c92d9e06fc8', target="_blank", className = 'links'),
                    html.A('Driver Demographics Dataset', href='https://www.data.qld.gov.au/dataset/crash-data-from-queensland-roads/resource/dd13a889-2a48-4b91-8c64-59f824ed3d2c', target="_blank", className = 'links'),
                    html.A('Vehicles types Dataset', href='https://www.data.qld.gov.au/dataset/crash-data-from-queensland-roads/resource/f999155b-37f7-48aa-b5dd-644838130b0b', target="_blank", className = 'links'),
                    html.A('Factors in road crashes Dataset', href='https://www.data.qld.gov.au/dataset/crash-data-from-queensland-roads/resource/18ee2911-992f-40ed-b6ae-e756859786e6', target="_blank", className = 'links'),
                ])
            ]
        ),
        dcc.Loading(
            html.Div(
                [
                    
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                'Filter by indicent Year:',
                                            ),
                                            html.Div(
                                                id = 'range_year_label',
                                                className = 'year_label',
                                            ),
                                            dcc.RangeSlider(
                                                id = 'range_year',
                                                min = df_locations['Crash_Year'].min(),
                                                max = df_locations['Crash_Year'].max(),
                                                step = 1,
                                                marks = {str(year): str(year) for year in [
                                                    df_locations['Crash_Year'].min(),
                                                    df_locations['Crash_Year'].max(),
                                                ]},
                                                value = [2010, 2018],
                                                className = 'dcc_control',
                                            ),

                                        ],
                                        className = 'pretty_container four columns',
                                        id = 'filter_options',
                                    ),

                                    html.Div(
                                        [html.H6(id = 'num_acidents'), html.P('No. of Accidents Recorded')],
                                        id = 'nacidents',
                                        className = 'mini_container',
                                    ),
                                    html.Div(
                                        [html.H6(id = 'num_fatal'), html.P('No. of Fatalities Recorded')],
                                        id = 'nfatal',
                                        className = 'mini_container',
                                    ),
                                    html.Div(
                                        [html.H6(id = 'top_region'), html.P('Region with most incidents occurrencies:')],
                                        id = 'region',
                                        className = 'mini_container',
                                    ),
                                ],
                                id = 'info-container',
                                className = 'row container-display',
                            ),
                            html.Div(
                                [dcc.Graph(id = 'area_chart')],
                                id = 'countGraphcontainer',
                                className = 'pretty_container',
                            ),
                        ],
                        id = 'right-column',
                        className = 'twelve columns',
                    ),
                ],
                className = 'row flex-display',
            ),
        )
    ],
    id = 'mainContainer',
    style = {"display": "flex", "flex-direction": "column"},
)


#Sunburst Html code

'''
        html.Div(id = 'df_streets_data', style = { 'display' : 'none' }),
        dcc.Loading(
            html.Div(
                [
                    html.Div([
                        dcc.Graph(id = 'sunburst')
                    ],className="six columns"),

                    html.Div([
                        dcc.Loading(dcc.Graph(id = 'streets_bar'))
                    ],className="six columns")
                ], className="pretty_container flex-display"
            )
        ),
        '''


#Helper functions

def filter_dataframe(df, range_year):
    dff = df.loc[df['Crash_Year'].between(range_year[0], range_year[1])].copy()
    return dff

@app.callback(
    Output('range_year_label', 'children'),
    [Input('range_year', 'value')])
def update_year(year_values):
    return f'{year_values[0]} to {year_values[1]}'

@app.callback(
    [Output('num_acidents', 'children'),
    Output('num_fatal', 'children'),
    Output('top_region', 'children')],
    [Input('range_year', 'value')])
def update_cards(range_year):

    dff = filter_dataframe(df_locations, range_year)

    acidents = len(dff)

    fatal = len(dff.loc[dff['Crash_Severity'] == 'Fatal'])

    region4 = dff['Loc_ABS_Statistical_Area_4'].value_counts().index[0]
    region3 = dff.loc[dff['Loc_ABS_Statistical_Area_4'] == region4, 'Loc_ABS_Statistical_Area_3'].value_counts().index[0]
    region2 = dff.loc[dff['Loc_ABS_Statistical_Area_3'] == region3, 'Loc_ABS_Statistical_Area_2'].value_counts().index[0]
    top_region = str(region4 + ' > ' + region3 + ' > ' + region2)

    return acidents, fatal, top_region


@app.callback(
    Output('area_chart', 'figure'),
    [Input('range_year', 'value')])
def update_area_chart(range_year):

    dff = filter_dataframe(df_locations, range_year)
    
    df_area = pd.DataFrame(dff.groupby(['Crash_Year', 'Crash_Month']).Crash_Severity.value_counts())
    df_area.rename(columns = {'Crash_Severity' : 'Total'}, inplace = True)
    df_area.reset_index(inplace = True)


    months_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    
    df_area['Crash_Month'] = df_area['Crash_Month'].astype(pd.api.types.CategoricalDtype(categories=months_list, ordered=True))
    df_area['label'] = df_area.apply(lambda x: x['Crash_Month'][:3] + '/' + str(x['Crash_Year']), axis = 1)
    df_area['percentage'] = round(df_area['Total']/df_area['Total'].sum()*100, 2)
    df_area.sort_values(['Crash_Year','Crash_Month'], inplace = True)
    label_list = list(df_area['label'].unique())
    df_area['id'] = df_area.apply(lambda x: label_list.index(x['label']), axis = 1)
    df_area.reset_index(drop = True, inplace = True)

    tick_list = []
    for i in range(len(label_list)):
        if i in list(range(0,len(label_list), (len(label_list)//10))):
            tick_list.append(label_list[i])
        else:
            tick_list.append('')
    

    fig_area = go.Figure()

    colors = ['#106db2', '#4c8786', '#88a05a', '#c3ba2e', '#ffd302']

    for j, sev in enumerate(severity):
            
        fig_area.add_trace(go.Scatter(
                        mode = 'lines',
                        name = sev,
                        x = df_area.loc[df_area['Crash_Severity'] == sev, 'id'],
                        y = df_area.loc[df_area['Crash_Severity'] == sev, 'Total'],
                        marker = dict(
                                    color = colors[j]),
                        fill = 'tonexty',
                        line_shape='spline',
                        line_color= colors[j],
                        text = df_area.loc[df_area['Crash_Severity'] == sev, 'label'],
                        hovertemplate = '<i>%{text}</i><br><b>N. of incidents:</b> <i>%{y}',
                        stackgroup='one',
                        legendgroup = sev,
                        showlegend = True))


            

    fig_area.update_layout(xaxis = {
                                'titlefont' : {'size' : 10},
                                'type' : 'linear',
                                'showgrid' : False,
                                'zeroline' : True,
                                'showspikes': True,
                                'tickfont' : {'size' : 8},
                                'tickmode' : 'array',
                                'tickvals' : list(range(len(df_area['label'].unique()))),
                                'ticktext' : tick_list,
                                'tickangle' : 0,
                                'nticks' : 10,
                                'spikecolor' : 'black',
                                'spikethickness' : 1,
                                'spikedash' : 'solid',
                                'spikesnap' : 'data',
                                'spikemode' : 'toaxis+marker'},
                    
                    yaxis = {'title' : '',
                            'titlefont' : {'size' : 8},
                                'showticklabels' : False,
                            'tickfont' : {'size' : 8},
                                'showgrid' : False,},
                    
                    height = 500,
                    barmode = 'stack',
                    hoverlabel = {'font' : {'size' : 10}},
                    title = "Number of incidents per month",
                    font = {'size' : 10},
                    plot_bgcolor="#F9F9F9",
                    paper_bgcolor="#F9F9F9",
                    legend_orientation = 'h',
                    legend = dict(font = dict(size = 8),
                                x = 0,
                                y = 1.01),
                    margin=dict(l=0, r=0, b=0, t=40))
                        
    return fig_area

if __name__ == '__main__':
    app.run_server(debug = True)