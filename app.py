import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from plotly.subplots import make_subplots

import json
import pandas as pd
import numpy as np


ext_style = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__) #external_stylesheets = ext_style)

server = app.server


#Importing the DataFrames

df_locations = pd.read_csv('locations_filtered.csv')

df_vehicles_m = pd.read_csv('vehicles_filtered.csv')

df_factors_m = pd.read_csv('factors_filtered.csv')

df_demographics = pd.read_csv('demographics_filtered.csv')

df_casualties = pd.read_csv('casualties_filtered.csv')


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

demo_labels = ['Involving Young Driver (16-24)',
         'Involving Young Provisional Driver',
         'Involving Young Overseas Licensed Driver',
         'Involving Young Unlicensed_Driver',
         'Involving Young Provisional Driver & Overseas Licensed Driver',
         'Involving Young Provisional Driver & Unlicensed Driver',
         'Involving Young Overseas Licensed Driver & Unlicensed Driver',
         'Involving Senior Driver (60 plus)',
         'Involving Senior Provisional Driver',
         'Involving Senior Overseas Licensed Driver',
         'Involving Senior Unlicensed_Driver',
         'Involving Senior Provisional Driver & Overseas Licensed Driver',
         'Involving Senior Provisional Driver & Unlicensed Driver',
         'Involving Senior Overseas Licensed Driver & Unlicensed Driver',
         'Involving Adult Driver (25-59)',
         'Involving Adult Provisional Driver',
         'Involving Adult Overseas Licensed Driver',
         'Involving Adult Unlicensed_Driver',
         'Involving Adult Provisional Driver & Overseas Licensed Driver',
         'Involving Adult Provisional Driver & Unlicensed Driver',
         'Involving Adult Overseas Licensed Driver & Unlicensed Driver',
         'Involving Adult Overseas Licensed Driver, Provisional Driver & Unlicensed Driver', 
         'Involving Young & Senior Driver',
         'Involving Young & Senior Provisional Driver',
         'Involving Young & Senior Overseas Licensed Driver',
         'Involving Young & Senior Unlicensed_Driver',
         'Involving Young & Senior Provisional Driver & Overseas Licensed Driver',
         'Involving Young & Senior Provisional Driver & Unlicensed Driver',
         'Involving Young & Senior Overseas Licensed Driver & Unlicensed Driver',  
         ]

#Create Controls

month_options = [{'label' : month, 'value' : month} for month in df_locations.Crash_Month.unique()]


#Helper Functions



styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}


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
                                                value = [2001, 2018],
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
        ),
        dcc.Loading(
            html.Div(
                [
                    html.Div(
                        [
                            html.P('Choose the severity', className = 'control_label'),
                            dcc.RadioItems(
                                id = 'severity_selector',
                                options = [
                                    {'label' : 'All', 'value' : 'all'},
                                    {'label' : 'Fatal', 'value' : 'Fatal'},
                                    {'label' : 'Hospitalisation', 'value' : 'Hospitalisation'},
                                    {'label' : 'Medical Treatment', 'value' : 'Medical treatment'},
                                    {'label' : 'Minor Injury', 'value' : 'Minor injury'},
                                ],
                                value = 'all',
                                labelStyle = {'display' : 'inline-block', 'padding' : '10px', 'font-style': 'italic', 'font-size' : '12px'},
                                className = 'dcc_control',
                            ),
                            dcc.Graph(id = 'nature_bars'),
                            dcc.Graph(id = 'donut_subplots')
                        ],
                        className = 'pretty_container eight columns',
                    ),
                    html.Div(
                        [dcc.Graph(id = 'joyplot')],
                        className = 'pretty_container four columns'
                    ),
                ],
                className="row flex-display",
            ),
        ),
        
        dcc.Loading(
            html.Div(
                [
                    dcc.Graph(
                        id = 'map',
                        className="nine columns"
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.P('Select the regions', className = 'control_label'),
                                    dcc.Dropdown(
                                        id= 'select_region2',
                                        options = [{'label' : i, 'value' : i } for i in regions2],
                                        value = ['Brisbane Inner'],
                                        multi = True)
                                ],style = {'padding' : '10px 0px'}
                            ),

                            html.Div(
                                [
                                    html.P('Select the incident hour', className = 'control_label'),
                                    dcc.Dropdown(
                                        id= 'select_hour',
                                        options = [{'label' : i, 'value' : i } for i in hours],
                                        value = [],
                                        multi = True)
                                ],style = {'padding' : '10px 0px'}
                            ),

                            html.Div(
                                [
                                    html.P('Select the severity', className = 'control_label'),
                                    dcc.Dropdown(
                                        id= 'select_sev',
                                        options = [{'label' : i, 'value' : i } for i in severity],
                                        value = [],
                                        multi = True)
                                ],style = {'padding' : '10px 0px'}
                            ),
                            
                            html.Div(
                                [
                                    html.P('Select the Crash Nature', className = 'control_label'),
                                    dcc.Dropdown(
                                        id= 'select_nature',
                                        options = [{'label' : i, 'value' : i } for i in nature],
                                        value = [],
                                        multi = True)
                                ],style = {'padding' : '10px 0px'}
                            )
                    ], className="three columns")
                ], className = 'pretty_container flex-display'
            )
        ),
        dcc.Loading(
            html.Div(
                [
                    html.Div(
                        [
                            html.P('Choose the severity', className = 'control_label'),
                            dcc.RadioItems(
                                id = 'severity_selector2',
                                options = [
                                    {'label' : 'All', 'value' : 'all'},
                                    {'label' : 'Fatal', 'value' : 'Fatal'},
                                    {'label' : 'Hospitalisation', 'value' : 'Hospitalisation'},
                                    {'label' : 'Medical Treatment', 'value' : 'Medical treatment'},
                                    {'label' : 'Minor Injury', 'value' : 'Minor injury'},
                                ],
                                value = 'all',
                                labelStyle = {'display' : 'inline-block', 'padding' : '20px', 'font-style': 'italic', 'font-size' : '12px'},
                                className = 'dcc_control',
                            ),
                            dcc.Graph(id = 'conditions_subplot')
                        ],
                        className = 'twelve columns'
                    ),
                ],
                className="pretty_container flex-display",
            )
        ),
        dcc.Loading(
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id = 'treemap')],
                        className = 'twelve columns'
                    ),
                ],
                className="pretty_container flex-display"
            )
        ),
        dcc.Loading(
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id = 'factors_bar')],
                        className = 'twelve columns',
                        style = {'flex': 1}
                    ),
                ],
                className="pretty_container flex-display",
            )
        ),
        dcc.Loading(
            html.Div(
                [
                    dcc.Graph(
                        id = 'demo_dots',
                        className = 'eight columns'
                    ),
                    html.Div(
                        [
                            dcc.Checklist(
                                id = 'demo_options',
                                options = [{'label' : i, 'value' : i} for i in demo_labels],
                                value = [],
                                labelStyle = {'font-size' : '10px', 'padding' : '3px', 'display' : 'block'},
                            )
                        ],
                        style = {'margin' : '40px 0 0 0'},
                        className = 'four columns'
                    )
                ],
                className = 'pretty_container flex-display'
            )
        ),
        dcc.Loading(
            html.Div(
                [
                    html.Div([
                        html.Div(
                            [
                                html.P('Choose the Casualty Severity', className = 'control_label'),
                                dcc.RadioItems(
                                    id = 'casualty_selector',
                                    options = [
                                        {'label' : 'All', 'value' : 'all'},
                                        {'label' : 'Fatality', 'value' : 'Fatality'},
                                        {'label' : 'Hospitalised', 'value' : 'Hospitalised'},
                                        {'label' : 'Medically treated', 'value' : 'Medically treated'},
                                        {'label' : 'Minor injury', 'value' : 'Minor injury'},
                                    ],
                                    value = 'all',
                                    labelStyle = {'display' : 'inline-block', 'padding' : '20px', 'font-style': 'italic', 'font-size' : '12px'},
                                    className = 'dcc_control',
                                ),
                            ],
                            className = 'eight columns'
                        ),
                        html.Div(
                            [
                                html.Button('Click to reset for Total values', id='reset_total', n_clicks = 0),
                            ],
                            className = 'four columns'
                        )
                    ], className="flex-display"),
                    html.Div([
                        html.Div(
                            [
                                dcc.Graph(id = 'casualties_chart')
                            ],
                            className = 'eight columns'
                        ),
                        html.Div(
                            [
                                dcc.Graph(id = 'casualties_bars'),
                            ],
                            className = 'four columns'
                        )
                    ], className="flex-display"),
                ],
                className="pretty_container",
            )
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


@app.callback(
    Output('joyplot', 'figure'),
    [Input('range_year', 'value')])
def update_joyplot(range_year):

    dff = filter_dataframe(df_locations, range_year) 

    df_bubble = pd.DataFrame(dff.groupby(['Crash_Hour', 'Crash_Day_Of_Week']).Crash_Severity.value_counts())
    df_bubble.rename(columns = {'Crash_Severity' : 'Total'}, inplace = True)
    df_bubble.reset_index(inplace = True)

    days_list = ['Sunday', 'Saturday', 'Friday', 'Thursday', 'Wednesday', 'Tuesday', 'Monday']
    
    df_bubble['Crash_Day_Of_Week'] = df_bubble['Crash_Day_Of_Week'].astype(pd.api.types.CategoricalDtype(categories=days_list, ordered=True))
    df_bubble['percentage'] = round(df_bubble['Total']/df_bubble['Total'].sum()*100, 2)
    df_bubble.sort_values(['Crash_Day_Of_Week', 'Crash_Severity'], inplace = True)


    severity = df_bubble.Crash_Severity.unique()
    days = df_bubble.Crash_Day_Of_Week.unique()

    fig = make_subplots(
        rows=7, cols=1, 
        shared_xaxes=True, 
        vertical_spacing= 0.0,

    )

    yaxes = ['yaxis1', 'yaxis2', 'yaxis3', 'yaxis4', 'yaxis5', 'yaxis6', 'yaxis7']
    xaxes = ['xaxis1', 'xaxis2', 'xaxis3', 'xaxis4', 'xaxis5', 'xaxis6', 'xaxis7']
    legend = [True, False, False, False, False, False, False]
    colors = ['#106db2', '#4c8786', '#88a05a', '#c3ba2e', '#ffd302']

    for j, sev in enumerate(severity):
        
        for i, day in enumerate(days):
            
            fig.add_trace(go.Scatter(
                            mode = 'lines',
                            name = sev,
                            x = df_bubble.loc[(df_bubble['Crash_Day_Of_Week'] == day) & (df_bubble['Crash_Severity'] == sev), 'Crash_Hour'],
                            y = df_bubble.loc[(df_bubble['Crash_Day_Of_Week'] == day) & (df_bubble['Crash_Severity'] == sev), 'Total'],
                            fill = 'tonexty',
                            line_shape='spline',
                            line_color= colors[j],
                            hovertemplate = '<i>'+day+' - %{x}</i><br><b>N. of incidents:</b> <i>%{y}',
                            #stackgroup='one',
                            legendgroup = sev,
                            showlegend = legend[i]),
                            row = i+1, col = 1)
            
            
            fig['layout'][yaxes[i]].update({'title' : day,
                                            'titlefont' : {'size' : 8},
                                            'showticklabels' : False,
                                            'showgrid' : False,
                                            'range' : [0, df_bubble['Total'].max()],
                                            })
            fig['layout'][xaxes[i]].update({'showgrid' : False,
                                            'zeroline' : True,
                                            'showspikes': True,
                                            'tickvals' : [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23],
                                            'ticktext' : ['0 am', '1 am', '2am', '3am', '4am', '5am', '6am', '7am', '8am',
                                                        '9am', '10am', '11am', '12am', '1pm', '2pm', '3pm', '4pm', '5pm',
                                                        '6pm', '7pm', '8pm', '9pm', '10pm', '11pm'],
                                            'tickfont' : {'size' : 8},
                                        'spikecolor' : 'black',
                                        'spikethickness' : 1,
                                        'spikedash' : 'solid',
                                        'spikesnap' : 'data',
                                        'spikemode' : 'toaxis+marker'})

            

    fig.update_layout(xaxis = {
                                'titlefont' : {'size' : 10},
                                'showgrid' : False},
                    height=800,
                    hoverlabel = {'font' : {'size' : 10}},
                    hovermode = 'closest',
                    title="Incidents per day of the week and hour of day",
                    font = {'size' : 10},
                    plot_bgcolor="#F9F9F9",
                    paper_bgcolor="#F9F9F9",
                    legend_orientation = 'h',
                    legend = dict(font = dict(size = 8),
                                x = 0,
                                y = 1.01),
                    margin=dict(l=0, r=0, b=0, t=40))
                        
    return fig


@app.callback(
    Output('nature_bars', 'figure'),
    [Input('severity_selector', 'value'),
    Input('range_year', 'value')])
def update_nature(sev, range_year):

    dff = filter_dataframe(df_locations, range_year)

    if sev != 'all':
        dff = dff.loc[dff['Crash_Severity'] == sev]
    else:
        sev = ['Fatal', 'Hospitalisation', 'Medical Treatment', 'Minor Injury']
        dff = dff.loc[dff['Crash_Severity'].isin(sev)]
        

    df_nature = pd.DataFrame(dff.groupby('Crash_Nature').Crash_Severity.count())
    df_nature.rename(columns = {'Crash_Severity' : 'Total'}, inplace = True)
    #df_nature.drop(labels = df_nature.columns.tolist()[1:], axis = 1, inplace = True)
    df_nature.reset_index(inplace = True)
    #df_nature['Crash_Month'] = df_area['Crash_Month'].astype(pd.api.types.CategoricalDtype(categories=months_list, ordered=True))
    #df_nature['label'] = df_area.apply(lambda x: x['Crash_Month'][:3] + '/' + str(x['Crash_Year']), axis = 1)
    #df_nature['total_cat'] = df_nature.apply(lambda x: df_nature.loc[df_nature['Crash_Nature'] == x['Crash_Nature'], 'Total'].sum(), axis = 1)
    df_nature['percentage'] = round(df_nature['Total']/df_nature['Total'].sum()*100, 2)
    df_nature.sort_values(['Total'], axis = 0, ascending = False, inplace = True)


    colors = ['#106db2', '#126eb0', '#156fae', '#1770ad', '#1a71ab', '#1c72a9', '#1e73a7', '#2174a6', '#2375a4', '#2676a2', 
          '#2877a0', '#2b789e', '#2d799d', '#2f7a9b', '#327b99', '#347c97', '#377d96', '#397f94', '#3b8092', '#3e8190', 
          '#40828e', '#43838d', '#45848b', '#488589', '#4a8687', '#4c8786', '#4f8884', '#518982', '#548a80', '#568b7e', 
          '#588c7d', '#5b8d7b', '#5d8e79', '#608f77', '#629076', '#649174', '#679272', '#699370', '#6c946e', '#6e956d', 
          '#71966b', '#739769', '#759867', '#789966', '#7a9a64', '#7d9b62', '#7f9c60', '#819d5e', '#849e5d', '#869f5b', 
          '#89a159', '#8ba257', '#8ea356', '#90a454', '#92a552', '#95a650', '#97a74e', '#9aa84d', '#9ca94b', '#9eaa49', 
          '#a1ab47', '#a3ac46', '#a6ad44', '#a8ae42', '#abaf40', '#adb03e', '#afb13d', '#b2b23b', '#b4b339', '#b7b437', 
          '#b9b536', '#bbb634', '#beb732', '#c0b830', '#c3b92e', '#c5ba2d', '#c7bb2b', '#cabc29', '#ccbd27', '#cfbe26', 
          '#d1bf24', '#d4c022', '#d6c120', '#d8c31e', '#dbc41d', '#ddc51b', '#e0c619', '#e2c717', '#e4c816', '#e7c914', 
          '#e9ca12', '#eccb10', '#eecc0e', '#f1cd0d', '#f3ce0b', '#f5cf09', '#f8d007', '#fad106', '#fdd204', '#ffd302']

    fig_nature = go.Figure()

    #sevs = df_nature['Crash_Severity'].unique()

    #for sev in sevs:
            
    fig_nature.add_trace(go.Bar(
                    
                    name = '',
                    x = df_nature['Crash_Nature'],
                    y = df_nature['Total'],
                    marker = dict(color = df_nature['Total'],
                              colorscale = colors,
                              line = dict(width = 2,
                                          color = '#002660')),
                    hovertemplate = '<i>%{x}</i><br><b>N. of incidents:</b> <i>%{y}',
                    text = [str(df_nature.iloc[i]['percentage']) + '%' for i in range(len(df_nature))],
                    textposition = 'outside',
                    textfont= {'size' : 8},
                    showlegend = True))

            

    fig_nature.update_layout(xaxis = {
                                'titlefont' : {'size' : 10},
                                'showgrid' : False,
                                'zeroline' : True,
                                'showspikes': False,
                                #'nticks' : 10,
                                'tickfont' : {'size' : 8}},
                    
                    yaxis = {'title' : '',
                            'titlefont' : {'size' : 8},
                            'showticklabels' : True,
                            'tickfont' : {'size' : 8},
                            'range' : [0, 4.54],
                            'type' : 'log',
                            'showgrid' : False,},
                    
                    height=400,
                    barmode = 'stack',
                    showlegend = False,
                    hoverlabel = {'font' : {'size' : 10}},
                    title_text="Incident nature",
                    font = {'size' : 10},
                    plot_bgcolor="#F9F9F9",
                    paper_bgcolor="#F9F9F9",
                    margin=dict(l=0, r=0, b=0, t=40))
                        
    return fig_nature


@app.callback(
    Output('donut_subplots', 'figure'),
    [Input('severity_selector', 'value'),
    Input('range_year', 'value')])
def update_donut(sev, range_year):

    dff = filter_dataframe(df_locations, range_year)

    if sev != 'all':
        dff = dff.loc[dff['Crash_Severity'] == sev].copy()
    else:
        sev = ['Fatal', 'Hospitalisation', 'Medical Treatment', 'Minor Injury']
        dff = dff.loc[dff['Crash_Severity'].isin(sev)].copy()


    df_donut = pd.DataFrame(dff.groupby('Crash_Type').Crash_Severity.count())
    df_donut.rename(columns = {'Crash_Severity' : 'Total'}, inplace = True)
    #df_donut.drop(labels = df_donut.columns.tolist()[1:], axis = 1, inplace = True)
    df_donut.reset_index(inplace = True)
    #df_nature['Crash_Month'] = df_area['Crash_Month'].astype(pd.api.types.CategoricalDtype(categories=months_list, ordered=True))
    #df_nature['label'] = df_area.apply(lambda x: x['Crash_Month'][:3] + '/' + str(x['Crash_Year']), axis = 1)
    #df_nature['total_cat'] = df_nature.apply(lambda x: df_nature.loc[df_nature['Crash_Nature'] == x['Crash_Nature'], 'Total'].sum(), axis = 1)
    df_donut['percentage'] = round(df_donut['Total']/df_donut['Total'].sum()*100, 2)
    df_donut.sort_values('Total', axis = 0, ascending = False, inplace = True)

    fig_donut = make_subplots(rows = 1, cols = 4,
                        specs = [[{'type' : 'domain'}, {'type' : 'domain'}, {'type' : 'domain'}, {'type' : 'domain'}]],
                        column_titles = ['Multi-Vehicle', 'Single Vehicle', 'Hit pedestrian', 'Other'],
                        )

    for ctype in df_donut['Crash_Type'].unique():
        
        fig_donut.add_trace(go.Pie(
                                    labels = df_donut['Crash_Type'],
                                    values = df_donut['Total'],
                                    name = ctype,
                                    opacity = 0.4,
                                    textfont = dict(color = ['#13589A' if t == 'Multi-Vehicle' else '#F9F9F9' for t in df_donut['Crash_Type'].unique()],
                                                size = 10),
                                    marker = dict(colors = ['#106db2' if t == 'Multi-Vehicle' else '#F9F9F9' for t in df_donut['Crash_Type'].unique()],
                                                line=dict(color= ['#002660' if t == 'Multi-Vehicle' else '#d7d7d7' for t in df_donut['Crash_Type'].unique()], width=2))), row = 1, col = 1)
                                                


        fig_donut.add_trace(go.Pie(
                                    labels = df_donut['Crash_Type'],
                                    values = df_donut['Total'],
                                    name = ctype,
                                    opacity = 0.4,
                                    textfont = dict(color = ['#13589A' if t == 'Single Vehicle' else '#F9F9F9' for t in df_donut['Crash_Type'].unique()],
                                                size = 10),
                                    marker = dict(colors = ['#608f77' if t == 'Single Vehicle' else '#F9F9F9' for t in df_donut['Crash_Type'].unique()],
                                                line=dict(color= ['#002660' if t == 'Single Vehicle' else '#d7d7d7' for t in df_donut['Crash_Type'].unique()], width=2))), row = 1, col = 2)


        fig_donut.add_trace(go.Pie(
                                    labels = df_donut['Crash_Type'],
                                    values = df_donut['Total'],
                                    name = ctype,
                                    opacity = 0.4,
                                    textfont = dict(color = ['#13589A' if t == 'Hit pedestrian' else '#F9F9F9' for t in df_donut['Crash_Type'].unique()],
                                                size = 10),
                                    marker = dict(colors = ['#afb13d' if t == 'Hit pedestrian' else '#F9F9F9' for t in df_donut['Crash_Type'].unique()],
                                                line=dict(color= ['#002660' if t == 'Hit pedestrian' else '#d7d7d7' for t in df_donut['Crash_Type'].unique()], width=2))), row = 1, col = 3)

        
        fig_donut.add_trace(go.Pie(
                                    labels = df_donut['Crash_Type'],
                                    values = df_donut['Total'],
                                    name = ctype,
                                    opacity = 0.4,
                                    textfont = dict(color = ['#13589A' if t == 'Other' else '#F9F9F9' for t in df_donut['Crash_Type'].unique()],
                                                size = 10),
                                    marker = dict(colors = ['#ffd302' if t == 'Other' else '#F9F9F9' for t in df_donut['Crash_Type'].unique()],
                                                line=dict(color= ['#002660' if t == 'Other' else '#d7d7d7' for t in df_donut['Crash_Type'].unique()], width=2))), row = 1, col = 4)
        
        
        
    # Use `hole` to create a donut-like pie chart
    fig_donut.update_traces(hole=.7, hoverinfo="label+percent+name", textinfo = 'none')

    #Function to extract values for donut chart
    def donut_value(df, colname, colvalue):
        try:
            return df.loc[df['Crash_Type'] == colname][colvalue].item()
        except ValueError:
            return 0

    #Add annotations in the center of the donut pies.
    fig_donut['layout']['annotations'] += (
        dict(text='<b>{}%</b><br><i>{}<br>incidents'.format(donut_value(df_donut, 'Multi-Vehicle', 'percentage'), donut_value(df_donut, 'Multi-Vehicle', 'Total')), x=0.08, y=0.5, font_size=12, showarrow=False),
        dict(text='<b>{}%</b><br><i>{}<br>incidents'.format(donut_value(df_donut, 'Single Vehicle', 'percentage'), donut_value(df_donut, 'Single Vehicle', 'Total')), x=0.37, y=0.5, font_size=12, showarrow=False),
        dict(text='<b>{}%</b><br><i>{}<br>incidents'.format(donut_value(df_donut, 'Hit pedestrian', 'percentage'), donut_value(df_donut, 'Hit pedestrian', 'Total')), x=0.63, y=0.5, font_size=12, showarrow=False),
        dict(text='<b>{}%</b><br><i>{}<br>incidents'.format(donut_value(df_donut, 'Other', 'percentage'), donut_value(df_donut, 'Other', 'Total')), x=0.91, y=0.5, font_size=12, showarrow=False)
    )

    fig_donut.update_layout(
        title_text="Incident type",
        font = {'size' : 10},
        height = 400,
        annotations=[go.layout.Annotation(
                                font = {'size' : 12})],
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        showlegend = False)
        
        
    return fig_donut


'''
#Build dataframe fo Sunburst Chart
def build_hierarchical_dataframe(df, levels, value_column):

    """
    Build a hierarchy of levels for Sunburst or Treemap charts.

    Levels are given starting from the bottom to the top of the hierarchy, 
    ie the last level corresponds to the root.
    """
    df_all_trees = pd.DataFrame(columns=['id', 'parent', 'value'])
    for i, level in enumerate(levels):
        df_tree = pd.DataFrame(columns=['id', 'parent', 'value'])
        dfg = df.groupby(levels[i:]).sum(numerical_only=True)
        dfg = dfg.reset_index()
        df_tree['id'] = dfg[level].copy()
        if i < len(levels) - 1:
            df_tree['parent'] = dfg[levels[i+1]].copy()
        else:
            df_tree['parent'] = 'Brisbane total'
        df_tree['value'] = dfg[value_column]
        df_all_trees = df_all_trees.append(df_tree, ignore_index=True)
    total = pd.Series(dict(id='Brisbane total', parent='', 
                            value=df[value_column].sum()))
    df_all_trees = df_all_trees.append(total, ignore_index=True)


    df_all_trees.sort_values('parent', na_position = 'first', inplace = True)
    df_all_trees.reset_index(drop = True, inplace = True)
    df_all_trees['labels'] = df_all_trees['id']
    df_all_trees = df_all_trees[['id', 'labels', 'parent', 'value']]
    
    return df_all_trees

#Build Sunburst Chart
@app.callback(
    [Output('sunburst', 'figure'),
    Output('df_streets_data', 'children')],
    [Input('range_year', 'value')])
def update_sunburst(range_year):

    df = filter_dataframe(df_locations, range_year)
    col_list = [col for col in df.columns.tolist() if col not in ['Loc_ABS_Statistical_Area_4', 'Loc_ABS_Statistical_Area_3', 'Loc_ABS_Statistical_Area_2', 'Crash_Street']]
    df.drop(labels = col_list, axis = 1, inplace = True)

    dff = pd.DataFrame(df.groupby(['Loc_ABS_Statistical_Area_4', 'Loc_ABS_Statistical_Area_3', 'Loc_ABS_Statistical_Area_2']).Crash_Street.value_counts())
    dff.rename(columns = {'Crash_Street' : 'Total'}, inplace = True)
    dff.reset_index(inplace = True)

    cols = ['Loc_ABS_Statistical_Area_4', 'Loc_ABS_Statistical_Area_3', 'Loc_ABS_Statistical_Area_2', 'Crash_Street']
    top5_reg1 = list(dff.groupby(cols[0]).sum(numerical_only = True).nlargest(5, 'Total').index)
    dff.loc[~dff[cols[0]].isin(top5_reg1), cols[0]] = 'Others'
    ranks = [5, 10, 20]

    for i, col in enumerate(cols):
        if i < len(cols)-1:
            k = i +1
            r = i
        else: 
            k = i
            r = 2

        for name in df[cols[k]].unique():
            if (col != cols[-1]):
                if name in df[col].unique():
                    dff.loc[dff[cols[k]] == name, cols[k]] = name + '_'

        for reg in dff[col].unique():  
            top5 = list(dff.loc[dff[col] == reg].groupby(cols[k]).sum(numerical_only = True).nlargest(ranks[r], 'Total').index)
            dff.loc[(dff[col] == reg) & ~(dff[cols[k]].isin(top5)), cols[k]] = 'Others_' + str(reg)

    levels = ['Loc_ABS_Statistical_Area_2', 'Loc_ABS_Statistical_Area_3', 'Loc_ABS_Statistical_Area_4'] # levels used for the hierarchical chart
    value_column = 'Total'

    df_all_trees = build_hierarchical_dataframe(dff, levels, value_column)

    df_all_trees['value'] = df_all_trees['value'].astype(int)
    df_all_trees['color'] = ''

    regions = df_all_trees.loc[df_all_trees['parent'] == 'Brisbane total', ['id','value']]
    regions.sort_values('value', ascending = False, inplace = True)
    regions = regions.id.tolist()

    others = list(df_all_trees.loc[~(df_all_trees['parent'].isin(df_locations['Loc_ABS_Statistical_Area_3'])) & ~(df_all_trees['parent'].isin(regions))].parent.unique())
    others.pop(0)
    others.pop(0)

    others_reg = (df_all_trees.loc[df_all_trees['parent'] == 'Others', 'id'].tolist())

    colors1 = ['#106db2', '#40818f', '#70966c', '#9faa48', '#cfbf25', '#ffd302']
    color_dic1 = dict(zip(regions, colors1))
    colors2 = ['#7da7d8', '#78b5c3', '#9ebf99', '#c2c783', '#e0d178', '#fcda75']
    color_dic2 = dict(zip(regions, colors2))
    colors3 = ['#cee4ff', '#b1ecfa', '#ceeac9', '#e4e5be', '#ece3bd', '#f2e1bc']
    color_dic3 = dict(zip(colors2, colors3))

    for i, region in enumerate(regions):
        for j, reg in enumerate(df_all_trees['id']):
            if reg == region:
                df_all_trees.loc[df_all_trees['id'] == reg, 'color'] = color_dic1.get(reg, None)

    for i, region in enumerate(regions):
        for j, reg in enumerate(df_all_trees['parent']):
            if reg == region:
                df_all_trees.loc[df_all_trees['parent'] == reg, 'color'] = color_dic2.get(reg, None)

    for j, reg in enumerate(df_all_trees['parent']):
        if (reg in df_locations.Loc_ABS_Statistical_Area_3.unique()) & ~(reg in others_reg):
            parent = list(df_locations.loc[df_locations['Loc_ABS_Statistical_Area_3'] == reg, 'Loc_ABS_Statistical_Area_4'])[0]
            df_all_trees.loc[df_all_trees['parent'] == reg, 'color'] = color_dic3.get(color_dic2.get(parent, None), None)

        elif (reg != '') & (reg in others):
            parent = list(df_all_trees.loc[df_all_trees['id'] == reg, 'parent'])[0]
            df_all_trees.loc[df_all_trees['parent'] == reg, 'color'] = color_dic3.get(color_dic2.get(parent, None), None)

        elif reg in others_reg:
            parent = 'Others'
            df_all_trees.loc[df_all_trees['parent'] == reg, 'color'] = color_dic3.get(color_dic2.get(parent, None), None)
    
    df_all_trees.loc[df_all_trees['parent'] == '', 'color'] = '#F9F9F9'
    
    
    

    return {
        'data' : [go.Sunburst(
        ids = df_all_trees['id'],
        labels=df_all_trees['labels'],
        textfont = {'size' : 8},
        parents=df_all_trees['parent'],
        values=df_all_trees['value'],
        customdata = df_all_trees['labels'],
        branchvalues='total',
        maxdepth = 3,
        marker= dict(colors = df_all_trees.color.tolist(),
                     line = dict(width = 2,
                                 color = '#002660')),
        hovertemplate ='<b>Name:</b> <i>%{id}</i><br><b>Region:</b> <i>%{parent}</i><br><b>N. of Incidents:</b> <i>%{value}</i><br><b>% of Region Incidents:</b> <i>%{percentParent:.1%}</i><br><b>% of Total Incidents:</b> <i>%{percentRoot:.1%}</i><br>',
        name=''
        )],
        'layout' : go.Layout(
            title = 'Number of incidents per region(click in the region to expand the chart)',
            font = {'size' : 10},
            height = 600,
            hoverlabel = {'font' : {'size' : 10}},
            plot_bgcolor="#F9F9F9",
            paper_bgcolor="#F9F9F9",
            margin = dict(t=40, l=40, r=5, b=5))
    }, dff.to_json(date_format = 'iso', orient = 'split')


@app.callback(
    Output('streets_bar', 'figure'),
    [Input('sunburst', 'hoverData'),
    Input('df_streets_data', 'children')])
def update_streets(hoverData, json_df):

    if json_df is None:
        raise PreventUpdate

    dff_st = pd.read_json(json_df, orient = 'split')

    levels = ['Crash_Street', 'Loc_ABS_Statistical_Area_2', 'Loc_ABS_Statistical_Area_3', 'Loc_ABS_Statistical_Area_4'] # levels used for the hierarchical chart
    value_column = 'Total'

    dff = build_hierarchical_dataframe(dff_st, levels, value_column)

    name = 'Hover over the outer regions to see the streets with most incidents occurrences'

    color_dic = {'#cee4ff': '#106db2',
                '#b1ecfa': '#40818f',
                '#ceeac9': '#70966c',
                '#e4e5be': '#9faa48',
                '#ece3bd': '#cfbf25',
                '#f2e1bc': '#ffd302'}

    traces = []

    draft_template = go.layout.Template()
    draft_template.layout.annotations = [
    go.layout.Annotation(
            name="empty watermark",
            text="Empty",
            textangle= 0,
            opacity=0.1,
            font=dict(color="black", size=60),
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
    ]

    if not hoverData:

        return {
            'data' : [],

            'layout' : go.Layout(
                showlegend = False,
                title = name,
                xaxis  = {
                        'visible' : False,
                        'showline' : False,
                        'zeroline' : False,
                        'showgrid' : False},
                yaxis = {
                'visible' : False,
                'showline' : False,
                'showgrid' : False,
                'zeroline' : False},
                plot_bgcolor="#F9F9F9",
                paper_bgcolor="#F9F9F9",
                margin = dict(t=40, l=120, r=10, b=20),
                height = 600,
                template = draft_template)
        }

    else:

        if hoverData['points'][0]['parent'] in dff_st['Loc_ABS_Statistical_Area_3'].unique():

            
            name = hoverData['points'][0]['id']

            dff_graph = (dff.loc[dff['parent'] == name].sort_values('value', ascending = True)).copy()
            dff_graph.reset_index(drop = True, inplace = True)
            
            keys = []
            i = 1
            
            for rua in dff_graph['id']:
                if 'Others' in rua:
                    keys.append(0)
                else:
                    keys.append(i)
                    i+= 1
            
            dff_graph['keys'] = keys
            dff_graph.set_index('keys', inplace = True, drop = True)
            dff_graph.sort_index(inplace = True)
            total_region = dff_graph.value.sum()
            
            for i, street in enumerate(dff_graph.loc[dff_graph['parent'] == name, 'id']):
                percentage = round(((dff_graph.iloc[i]['value'])/total_region)*100, 1)

                traces.append(
                go.Bar(
                    name = street,
                    x = dff_graph.loc[dff_graph['id'] == street, 'value'],
                    y = dff_graph.loc[dff_graph['id'] == street, 'id'],
                    marker = dict(color = color_dic[hoverData['points'][0]['color']],
                                  line = dict(width = 1.5,
                                              color = '#002660')),
                    
                    text = str(percentage)+'%',
                    textposition = 'outside',
                    textfont= {'size' : 8},
                    orientation = 'h'))


            return {
                'data' : traces,

                'layout' : go.Layout(
                    showlegend = False,
                    title = name,
                    font = {'size' : 10},
                    xaxis  = {
                            'visible' : False,
                            'showline' : False,
                            'zeroline' : False,
                            'range' : [0, dff_graph['value'].max() * 1.2],
                            'showgrid' : False},
                    yaxis = {
                    'tickfont' : {'size' : 8},
                    'showline' : False,
                    'showgrid' : False,
                    'zeroline' : False},
                    plot_bgcolor="#F9F9F9",
                    paper_bgcolor="#F9F9F9",
                    margin = dict(t=40, l=120, r=10, b=20),
                    height = 600)
            }
        else:

            return {
                'data' : [],

                'layout' : go.Layout(
                    showlegend = False,
                    title = name,
                    font = {'size' : 10},
                    plot_bgcolor="#F9F9F9",
                    paper_bgcolor="#F9F9F9",
                    xaxis  = {
                            'visible' : False,
                            'showline' : False,
                            'zeroline' : False,
                            'showgrid' : False},
                    yaxis = {
                    'visible' : False,
                    'showline' : False,
                    'showgrid' : False,
                    'zeroline' : False},
                    margin = dict(t=40, l=120, r=10, b=20),
                    height = 600,
                    template = draft_template)
            }
'''
@app.callback(
    Output('map', 'figure'),
    [Input('select_region2', 'value'),
    Input('select_hour', 'value'),
    Input('select_sev', 'value'),
    Input('select_nature', 'value'),
    Input('range_year', 'value')])
def update_map(regions, hour, sev, nat, range_year):

    dff = filter_dataframe(df_locations, range_year)

    if len(regions) >= 1:
        regions_list = regions
    else:
        regions_list = sorted(dff['Loc_ABS_Statistical_Area_3'].unique())

    if len(hour) >= 1:
        hours_list = hour
    else:
        hours_list = sorted(dff['Crash_Hour'].unique())

    if len(sev) >= 1:
        sev_list = sev
    else:
        sev_list = sorted(dff['Crash_Severity'].unique())

    if len(nat) >= 1:
        nat_list = nat
    else:
        nat_list = sorted(dff['Crash_Nature'].unique())

    
    dff = dff.loc[dff['Loc_ABS_Statistical_Area_3'].isin(regions_list)]
    dff = dff.loc[dff['Crash_Hour'].isin(hours_list)]
    dff = dff.loc[dff['Crash_Severity'].isin(sev_list)]
    dff = dff.loc[dff['Crash_Nature'].isin(nat_list)]
    


    token = 'pk.eyJ1IjoidnNvdXNhIiwiYSI6ImNrNDBsZDZmbTAyemMza3FtMTR5b3B2OHoifQ.oLLaSUZvJ9_t2IQS9FN0DQ'

    return {
        'data' : [go.Scattermapbox(
            lat= dff.Crash_Latitude_GDA94,
            lon= dff.Crash_Longitude_GDA94,
            mode='markers',
            marker=dict(
                color = dff.Crash_Hour,
                size=4.5,
                colorscale= ['#009d56', '#029663', '#04906f', '#07897c', '#098388', '#0b7c95', '#0d76a1', '#0f6fae', 
                '#106db2', '#106db2', '#106db2', '#106db2', '#106db2', '#106db2', '#106db2', '#1b72ad', '#3b809e', 
                '#5c8f90', '#7d9e81', '#9dac72', '#bebb63', '#dec955', '#ffd846'],

                showscale = True,
                colorbar = {'title' : 'Hour of the Day', 'tickvals' : list(range(24)), 'tickfont' : {'size' : 8}},
            ),
            text= dff.text,
        )],
        'layout' : go.Layout(
            title = 'Incident details',
            font = {'size' : 10},
            height = 500,
            hovermode='closest',
            plot_bgcolor="#F9F9F9",
            paper_bgcolor="#F9F9F9",
            margin = dict(t = 50, b = 5, l = 5, r = 5),
            mapbox=go.layout.Mapbox(
                accesstoken= token,
                bearing=0,
                center=go.layout.mapbox.Center(
                            lat= -27.46794,
                            lon= 153.02809
                        ),
                pitch=0,
                zoom=13,
                style = 'light',
                )
        )

    }


@app.callback(
    Output('conditions_subplot', 'figure'),
    [Input('severity_selector2', 'value'),
    Input('range_year', 'value')])
def update_conditions_subplot(sev, range_year):

    dff = filter_dataframe(df_locations, range_year)

    if sev != 'all':
        dff = dff.loc[dff['Crash_Severity'] == sev].copy()
    else:
        sev = ['Fatal', 'Hospitalisation', 'Medical Treatment', 'Minor Injury']
        dff = dff.loc[dff['Crash_Severity'].isin(sev)].copy()
    
    def create_df(colname):
        dfname = pd.DataFrame(dff[colname].value_counts(ascending = True))
        dfname.rename(columns ={colname : 'Total'}, inplace = True)
        dfname.reset_index(inplace = True)
        dfname['percentage'] = dfname.apply(lambda x : str((round(x['Total']/sum(dfname['Total'])*100, 2))) + '%', axis = 1)
        return dfname

    df_roadway = create_df('Crash_Roadway_Feature')
    df_traffic = create_df('Crash_Traffic_Control')
    df_speed = create_df('Crash_Speed_Limit')
    df_surface = create_df('Crash_Road_Surface_Condition')
    df_atm = create_df('Crash_Atmospheric_Condition')
    df_light = create_df('Crash_Lighting_Condition')


    fig = make_subplots(
    rows = 3, cols = 3,
    #column_widths=[0.33, 0.33, 0.33],
    #row_heights=[0.8, 0.8],
    specs = [[{'rowspan' : 2}, {'rowspan' : 2}, {}], 
             [None, None, None],
             [{}, {}, {}]],
    subplot_titles = ['Roadway Feature', 'Traffic Control', 'Speed Limit', 'Road Surface Conditon', 'Atmospheric Conditon', 'Lighting Condition'],
    horizontal_spacing= 0.05,
    vertical_spacing= 0.1)

    ranges = [df_roadway['Total'].max(), df_traffic['Total'].max(), df_speed['Total'].max(),
              df_surface['Total'].max(), df_atm['Total'].max(), df_light['Total'].max()]

    fig.add_trace(go.Bar(
                        name = 'Roadway Feature',
                        x = df_roadway['Total'],
                        y = df_roadway['index'],
                        text = df_roadway['percentage'],
                        textposition = 'outside',
                        textfont= {'size' : 8},
                        orientation = 'h',
                        marker = dict(color  = '#106db2',
                                      line = dict(width = 2,
                                                   color = '#002660'))), row = 1, col = 1)

    fig.add_trace(go.Bar(
                        name = 'Traffic Control',
                        x = df_traffic['Total'],
                        y = df_traffic['index'],
                        text = df_traffic['percentage'],
                        textposition = 'outside',
                        textfont= {'size' : 8},
                        orientation = 'h',
                        #opacity = 0.8,
                        marker = dict(color  = '#40818f',
                                      line = dict(width = 2,
                                                   color = '#002660'))), row = 1, col = 2)


    fig.add_trace(go.Bar(
                        name = 'Speed Limit',
                        x = df_speed['Total'],
                        y = df_speed['index'],
                        text = df_speed['percentage'],
                        textposition = 'outside',
                        textfont= {'size' : 8},
                        orientation = 'h',
                        #opacity = 0.8,
                        marker = dict(color  = '#70966c',
                                      line = dict(width = 2,
                                                   color = '#002660'))), row = 1, col = 3)

    fig.add_trace(go.Bar(
                        name = 'Road Surface Conditon',
                        x = df_surface['Total'],
                        y = df_surface['index'],
                        text = df_surface['percentage'],
                        textposition = 'outside',
                        textfont= {'size' : 8},
                        orientation = 'h',
                        #opacity = 0.8,
                        marker = dict(color  = '#9faa48',
                                      line = dict(width = 2,
                                                   color = '#002660'))), row = 3, col = 1)

    fig.add_trace(go.Bar(
                        name = 'Atmospheric Conditon',
                        x = df_atm['Total'],
                        y = df_atm['index'],
                        text = df_atm['percentage'],
                        textposition = 'outside',
                        textfont= {'size' : 8},
                        orientation = 'h',
                        #opacity = 0.8,
                        marker = dict(color  = '#cfbf25',
                                      line = dict(width = 2,
                                                   color = '#002660'))), row = 3, col = 2)

    fig.add_trace(go.Bar(
                        name = 'Lighting Condition',
                        x = df_light['Total'],
                        y = df_light['index'],
                        text = df_light['percentage'],
                        textposition = 'outside',
                        textfont= {'size' : 8},
                        orientation = 'h',
                        #opacity = 0.8,
                        marker = dict(color  = '#ffd302',
                                      line = dict(width = 2,
                                                   color = '#002660'))), row = 3, col = 3)

    xaxes = ['xaxis1', 'xaxis2', 'xaxis3', 'xaxis4', 'xaxis5', 'xaxis6']
    yaxes = ['yaxis1', 'yaxis2', 'yaxis3', 'yaxis4', 'yaxis5', 'yaxis6']

    for x, axex in enumerate(xaxes):
        
        fig['layout'][axex].update({'visible' : False,
                                    'showline' : False,
                                    'zeroline' : False,
                                    'range' : [0, ranges[x]*1.3],
                                    'showgrid' : False})
    for axey in yaxes:
        
        fig['layout'][axey].update({'tickfont' : {'size' : 8},
                            'showline' : False,
                            'showgrid' : False,
                            'zeroline' : False})
            

    fig.update_layout(go.Layout(
                            showlegend = False,
                            title = 'Incidents conditions',
                            font = {'size' : 10}),
                            plot_bgcolor="#F9F9F9",
                            paper_bgcolor="#F9F9F9",
                            height = 800,
                            hoverlabel= dict(font = dict(size = 10)),
                            annotations=[go.layout.Annotation(
                            font = {'size' : 10})])
    
    return fig



#Build TreeMap Chart
@app.callback(
    Output('treemap', 'figure'),
    [Input('range_year', 'value')])
def update_treemap(range_year):

    df_vehicles = filter_dataframe(df_vehicles_m, range_year)

    motorcyclemask = df_vehicles['Involving_Motorcycle_Moped'] == 1
    truckmask = df_vehicles['Involving_Truck'] == 1
    busmask = df_vehicles['Involving_Bus'] == 1


    df_motorcycle = df_vehicles.loc[(motorcyclemask) & ~(truckmask) & ~(busmask)].copy()
    df_truck = df_vehicles.loc[~(motorcyclemask) & (truckmask) & ~(busmask)].copy()
    df_bus = df_vehicles.loc[~(motorcyclemask) & ~(truckmask) & (busmask)].copy()
    df_cars = df_vehicles.loc[~(motorcyclemask) & ~(truckmask) & ~(busmask)].copy()

    df_motortruck = df_vehicles.loc[(motorcyclemask) & (truckmask) & ~(busmask)].copy()
    df_motorbus = df_vehicles.loc[(motorcyclemask) & ~(truckmask) & (busmask)].copy()
    df_truckbus = df_vehicles.loc[~(motorcyclemask) & (truckmask) & (busmask)].copy()
    #df_motortruckbus = df_vehicles.loc[(motorcyclemask) & (truckmask) & (busmask)].copy()

    fig = go.Figure(go.Treemap(

        labels = ['Total', "Involving Car", "Involving Motorcycle", "Involving Truck", "Involving Bus", 
                 "Involving Motorcycle & Truck", "Involving Motorcycle & Bus", 'Involving Truck & Bus', 
                  '<i>Fatal_Car</i>', 'Fatal_Motorcycle', 'Fatal_Truck', 'Fatal_Bus', 'Fatal_Motorcycle & Truck', 'Fatal_Motorcycle & Bus', 'Fatal_Truck & Bus', 'Hospitalisation_Car', 'Hospitalisation_Motorcycle', 
                  'Hospitalisation_Truck', 'Hospitalisation_Bus', 'Hospitalisation_Motorcycle & Truck', 'Hospitalisation_Motorcycle & Bus', 'Hospitalisation_Truck & Bus', 'Medical treatment_Car',
                 'Medical treatment_Motorcycle', 'Medical treatment_Truck', 'Medical treatment_Bus', 'Medical treatment_Motorcycle & Truck', 'Medical treatment_Motorcycle & Bus', 'Medical treatment_Truck & Bus',
                 'Minor injury_Car', 'Minor injury_Motorcycle', 'Minor injury_Truck', 'Minor injury_Bus', 'Minor injury_Motorcycle & Truck', 'Minor injury_Motorcycle & Bus', 'Minor injury_Truck & Bus'],


        parents = ['', 'Total', 'Total', 'Total', 'Total' , 'Total', 'Total', 'Total', "Involving Car", "Involving Motorcycle", "Involving Truck", "Involving Bus", 
                 "Involving Motorcycle & Truck", "Involving Motorcycle & Bus", 'Involving Truck & Bus',
                  "Involving Car", "Involving Motorcycle", "Involving Truck", "Involving Bus", 
                 "Involving Motorcycle & Truck", "Involving Motorcycle & Bus", 'Involving Truck & Bus',
                  "Involving Car", "Involving Motorcycle", "Involving Truck", "Involving Bus", 
                 "Involving Motorcycle & Truck", "Involving Motorcycle & Bus", 'Involving Truck & Bus',
                  "Involving Car", "Involving Motorcycle", "Involving Truck", "Involving Bus", 
                 "Involving Motorcycle & Truck", "Involving Motorcycle & Bus", 'Involving Truck & Bus'],

        values = [df_vehicles['Count_Crashes'].sum(), df_cars['Count_Crashes'].sum(), 
                 df_motorcycle['Count_Crashes'].sum(),
                 df_truck['Count_Crashes'].sum(),
                 df_bus['Count_Crashes'].sum(),
                 df_motortruck['Count_Crashes'].sum(),
                 df_motorbus['Count_Crashes'].sum(),
                 df_truckbus['Count_Crashes'].sum(),
                 df_cars.loc[df_cars['Crash_Severity'] == 'Fatal', 'Count_Crashes'].sum(), 
                 df_motorcycle.loc[df_motorcycle['Crash_Severity'] == 'Fatal', 'Count_Crashes'].sum(),
                 df_truck.loc[df_truck['Crash_Severity'] == 'Fatal', 'Count_Crashes'].sum(),
                 df_bus.loc[df_bus['Crash_Severity'] == 'Fatal', 'Count_Crashes'].sum(),
                 df_motortruck.loc[df_motortruck['Crash_Severity'] == 'Fatal', 'Count_Crashes'].sum(),
                 df_motorbus.loc[df_motorbus['Crash_Severity'] == 'Fatal', 'Count_Crashes'].sum(),
                 df_truckbus.loc[df_truckbus['Crash_Severity'] == 'Fatal', 'Count_Crashes'].sum(),
                 df_cars.loc[df_cars['Crash_Severity'] == 'Hospitalisation', 'Count_Crashes'].sum(), 
                 df_motorcycle.loc[df_motorcycle['Crash_Severity'] == 'Hospitalisation', 'Count_Crashes'].sum(),
                 df_truck.loc[df_truck['Crash_Severity'] == 'Hospitalisation', 'Count_Crashes'].sum(),
                 df_bus.loc[df_bus['Crash_Severity'] == 'Hospitalisation', 'Count_Crashes'].sum(),
                 df_motortruck.loc[df_motortruck['Crash_Severity'] == 'Hospitalisation', 'Count_Crashes'].sum(),
                 df_motorbus.loc[df_motorbus['Crash_Severity'] == 'Hospitalisation', 'Count_Crashes'].sum(),
                 df_truckbus.loc[df_truckbus['Crash_Severity'] == 'Hospitalisation', 'Count_Crashes'].sum(),
                 df_cars.loc[df_cars['Crash_Severity'] == 'Medical treatment', 'Count_Crashes'].sum(), 
                 df_motorcycle.loc[df_motorcycle['Crash_Severity'] == 'Medical treatment', 'Count_Crashes'].sum(),
                 df_truck.loc[df_truck['Crash_Severity'] == 'Medical treatment', 'Count_Crashes'].sum(),
                 df_bus.loc[df_bus['Crash_Severity'] == 'Medical treatment', 'Count_Crashes'].sum(),
                 df_motortruck.loc[df_motortruck['Crash_Severity'] == 'Medical treatment', 'Count_Crashes'].sum(),
                 df_motorbus.loc[df_motorbus['Crash_Severity'] == 'Medical treatment', 'Count_Crashes'].sum(),
                 df_truckbus.loc[df_truckbus['Crash_Severity'] == 'Medical treatment', 'Count_Crashes'].sum(),
                 df_cars.loc[df_cars['Crash_Severity'] == 'Minor injury', 'Count_Crashes'].sum(), 
                 df_motorcycle.loc[df_motorcycle['Crash_Severity'] == 'Minor injury', 'Count_Crashes'].sum(),
                 df_truck.loc[df_truck['Crash_Severity'] == 'Minor injury', 'Count_Crashes'].sum(),
                 df_bus.loc[df_bus['Crash_Severity'] == 'Minor injury', 'Count_Crashes'].sum(),
                 df_motortruck.loc[df_motortruck['Crash_Severity'] == 'Minor injury', 'Count_Crashes'].sum(),
                 df_motorbus.loc[df_motorbus['Crash_Severity'] == 'Minor injury', 'Count_Crashes'].sum(),
                 df_truckbus.loc[df_truckbus['Crash_Severity'] == 'Minor injury', 'Count_Crashes'].sum()],
        branchvalues = "total",
        name = '',
        textinfo = "label+value+percent parent+percent entry",
        insidetextfont = {"size": 10},
        marker_colors = ['#106db2', '#327c99', '#548a80', '#769967', '#99a74d', '#bbb634', '#ddc41b', '#ffd302'],
        hovertemplate = '<b>%{label}<b><br><b>Number of Incidents:</b><i>%{value}</i><br><b>% of %{parent} Incidents:</b> <i>%{percentParent:.1%}</i><br><b>% of Total Incidents:</b> <i>%{percentRoot:.1%}</i><br>',
        maxdepth = 3,
    ))

    fig.update_layout(go.Layout(
                                showlegend = False,
                                title = 'Incidents vehicles types',
                                font = {'size' : 10},
                                hoverlabel = {'font' : {'size' : 10}},
                                plot_bgcolor="#F9F9F9",
                                paper_bgcolor="#F9F9F9",
                                margin = dict(t=60, l=20, r=20, b=20)),
                                height = 500)
    
    return fig


#Build Factors Chart
@app.callback(
    Output('factors_bar', 'figure'),
    [Input('range_year', 'value')])
def update_factors(range_year):

    df_factors = filter_dataframe(df_factors_m, range_year)

    drinkmask = df_factors['Involving_Drink_Driving'] == 1
    speedmask = df_factors['Involving_Driver_Speed'] == 1
    fatiguemask = df_factors['Involving_Fatigued_Driver'] == 1
    defectivemask = df_factors['Involving_Defective_Vehicle'] == 1


    df_others = df_factors.loc[~(drinkmask) & ~(speedmask) & ~(fatiguemask) & ~(defectivemask)].copy()
    df_drink = df_factors.loc[(drinkmask) & ~(speedmask) & ~(fatiguemask) & ~(defectivemask)].copy()
    df_speed = df_factors.loc[~(drinkmask) & (speedmask) & ~(fatiguemask) & ~(defectivemask)].copy()
    df_fatigue = df_factors.loc[~(drinkmask) & ~(speedmask) & (fatiguemask) & ~(defectivemask)].copy()
    df_defective = df_factors.loc[~(drinkmask) & ~(speedmask) & ~(fatiguemask) & (defectivemask)].copy()

    df_drinkspeed = df_factors.loc[(drinkmask) & (speedmask) & ~(fatiguemask) & ~(defectivemask)].copy()
    df_drinkfatigue = df_factors.loc[(drinkmask) & ~(speedmask) & (fatiguemask) & ~(defectivemask)].copy()
    df_drinkdefective = df_factors.loc[(drinkmask) & ~(speedmask) & ~(fatiguemask) & (defectivemask)].copy()
    df_speedfatigue = df_factors.loc[~(drinkmask) & (speedmask) & (fatiguemask) & ~(defectivemask)].copy()
    df_speeddefective = df_factors.loc[~(drinkmask) & (speedmask) & ~(fatiguemask) & (defectivemask)].copy()
    df_fatiguedefective = df_factors.loc[~(drinkmask) & ~(speedmask) & (fatiguemask) & (defectivemask)].copy()

    df_drinkspeedfatigue = df_factors.loc[(drinkmask) & (speedmask) & (fatiguemask) & ~(defectivemask)].copy()
    df_drinkspeeddefective = df_factors.loc[(drinkmask) & (speedmask) & ~(fatiguemask) & (defectivemask)].copy()
    df_drinkfatiguedefective = df_factors.loc[(drinkmask) & ~(speedmask) & (fatiguemask) & (defectivemask)].copy()
    df_speedfatiguedefective = df_factors.loc[~(drinkmask) & (speedmask) & (fatiguemask) & (defectivemask)].copy()

    names = [
    'Others factors',
    'Involving Drink Driving',
    'Involving Driver Speed',
    'Involving Fatigued Driver',
    'Involving Defective Vehicle',
    'Involving Drink Driving & Driver Speed',
    'Involving Drink Driving & Fatigued',
    'Involving Drink Driving & Defective Vehicle',
    'Involving Driver Speed & Fatigued Driver',
    'Involving Driver Speed & Defective Vehicle',
    'Involving Fatigued Driver & Defective Vehicle',
    'Involving Drink Driving, Driver Speed & Fatigued Driver',
    'Involving Drink Driving, Driver Speed & Defective Vehicle',
    'Involving Drink Driving, Fatigued Driver & Defective Vehicle',
    'Involving Driver Speed, Fatigued Driver & Defective Vehicle']

    dfs = [df_others, df_drink, df_speed, df_fatigue, df_defective, df_drinkspeed, df_drinkfatigue, 
        df_drinkdefective, df_speedfatigue, df_speeddefective, df_fatiguedefective, df_drinkspeedfatigue, 
        df_drinkspeeddefective, df_drinkfatiguedefective, df_speedfatiguedefective]

    dff = pd.DataFrame(columns = ['index', 'Fatal', 'Hospitalisation', 'Medical treatment', 'Minor injury', 'Property damage only'])

    for i, df in enumerate(dfs):
        df_temp = pd.DataFrame(df.groupby('Crash_Severity').Count_Crashes.sum()).T
        df_temp.rename(index = {'Count_Crashes' : names[i]}, inplace = True)
        df_temp.reset_index(inplace = True)
        dff = dff.append(df_temp, ignore_index= True, sort = False)

    dff = dff[['index', 'Fatal', 'Hospitalisation', 'Medical treatment', 'Minor injury', 'Property damage only']]
    dff.fillna(0, inplace = True)
    dff['Total'] = dff.sum(axis = 1)
    dff.sort_values('Total', ascending = True, inplace = True)
    dff.reset_index(inplace = True, drop = True)
    dff.drop(index = dff.index[dff['Total'] == 0].tolist(), axis = 1, inplace = True)
    keys = []
    i = 1

    for factor in dff['index']:
        if 'Others' in factor:
            keys.append(0)
        else:
            keys.append(i)
            i+= 1

    dff['keys'] = keys
    dff.set_index('keys', inplace = True, drop = True)
    dff.sort_index(inplace = True)

    dff['%Total'] = dff.apply(lambda x : str((round(x['Total']/sum(dff['Total'])*100, 2))) + '%', axis = 1)
    dff['%Fatal'] = dff.apply(lambda x: '<b>{}</b> - <i>Fatal</i><br><b>No. of Incidends:</b> <i>{}</i><br><b>% of Factor:<b> <i>{}</i>%'.format(x['index'], x['Fatal'], round(x['Fatal']/x['Total'], 4)*100), axis = 1)
    dff['%Hospitalisation'] =  dff.apply(lambda x: '<b>{}</b> - <i>Hospitalisation</i><br><b>No. of Incidends:</b> <i>{}</i><br><b>% of Factor:<b> <i>{}</i>%'.format(x['index'], x['Hospitalisation'], round(x['Hospitalisation']/x['Total'], 4)*100), axis = 1)
    dff['%Medical treatment'] =  dff.apply(lambda x: '<b>{}</b> - <i>Medical treatment</i><br><b>No. of Incidends:</b> <i>{}</i><br><b>% of Factor:<b> <i>{}</i>%'.format(x['index'], x['Medical treatment'], round(x['Medical treatment']/x['Total'], 4)*100), axis = 1)
    dff['%Minor injury'] =  dff.apply(lambda x: '<b>{}</b> - <i>Minor injury</i><br><b>No. of Incidends:</b> <i>{}</i><br><b>% of Factor:<b> <i>{}</i>%'.format(x['index'], x['Minor injury'], round(x['Minor injury']/x['Total'], 4)*100), axis = 1)
    dff['%Property damage only'] =  dff.apply(lambda x: '<b>{}</b> - <i>Property damage only</i><br><b>No. of Incidends:</b> <i>{}</i><br><b>% of Factor:<b> <i>{}</i>%'.format(x['index'], x['Property damage only'], round(x['Property damage only']/x['Total'], 4)*100), axis = 1)


    fig_factors = go.Figure()

    sev_list = ['Fatal', 'Hospitalisation', 'Medical treatment', 'Minor injury', 'Property damage only']
    colors = ['#106db2', '#4c8786', '#88a05a', '#c3ba2e', '#ffd302']


    for sev in sev_list:
        #for j, factor in enumerate(dff.index):
        
        if sev == 'Property damage only':
            
            fig_factors.add_trace(go.Bar(
                y=dff['index'].tolist(),
                x=dff['Total'].tolist(),
                name= sev,
                marker = dict(color = colors[sev_list.index('Property damage only')],
                            line = dict(width = 2,
                                        color = '#002660')),
                text = dff.loc[dff['Total'] > 0, '%Total'].tolist(),
                textposition = 'outside',
                textfont = {'size' : 8},
                hovertext = dff['%'+ sev],
                hoverinfo = 'text',
                orientation='h',
                )
            )
        else:
            
            fig_factors.add_trace(go.Bar(
                    y=dff.loc[dff['Total'] > 0, 'index'].tolist(),
                    x=dff.loc[dff['Total'] > 0, sev].tolist(),
                    name= sev,
                    marker = dict(color = colors[sev_list.index(sev)],
                                line = dict(width = 2,
                                            color = '#002660')),
                    hovertext = dff['%'+ sev],
                    hoverinfo = 'text',
                    orientation='h',
                    )
                )

                
    fig_factors.update_layout(
        title = 'Incidents factors',
        font = {'size' : 10},
        showlegend = True,
        barmode='stack',
        yaxis = {'visible' : True,
                'showgrid' : False,
                'showline' : True,
                'tickfont' : {'size' : 8}},
        xaxis = {'type' : 'log',
                'showgrid' : False,
                'autorange' : True,
                'tickfont' : {'size' : 8}},
        legend_orientation = 'h',
        legend = {'font':{'size':8},
                'x' : -0.3,
                'y' : 1.1},
        margin = dict(t = 100, b = 10, l = 20, r = 20),
        hoverlabel = dict(font = dict(size = 10)),
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        )



    return fig_factors


@app.callback(
    Output('demo_dots', 'figure'),
    [Input('demo_options', 'value'),
    Input('range_year', 'value')])
def update_demo_dots(categories, range_year):

    if len(categories) < 1:
        categories_list = demo_labels
    else:
        categories_list = categories

    biggest_string = max([len(label) for label in categories_list])


    df_demo = filter_dataframe(df_demographics, range_year)

    malemask = df_demo['Involving_Male_Driver'] == 1
    femalemask = df_demo['Involving_Female_Driver'] == 1

    df_mdemo = df_demo.loc[(malemask) & ~(femalemask)].copy()
    df_fdemo = df_demo.loc[~(malemask) & (femalemask)].copy()
    df_mfdemo = df_demo.loc[(malemask) & (femalemask)].copy()
    df_xdemo = df_demo.loc[~(malemask) & ~(femalemask)].copy()

    def create_masks(df):
    
        youngmask = df['Involving_Young_Driver_16-24'] == 1
        seniormask = df['Involving_Senior_Driver_60plus'] == 1
        provisionalmask = df['Involving_Provisional_Driver'] == 1
        overseasmask = df['Involving_Overseas_Licensed_Driver'] == 1
        unlicensedmask = df['Involving_Unlicensed_Driver'] == 1

        return youngmask, seniormask, provisionalmask, overseasmask, unlicensedmask
    
    myoung, msenior, mprovisional, moverseas, munlicensed = create_masks(df_mdemo)
    df_m_young = df_mdemo.loc[(myoung) & ~(msenior) & ~(mprovisional) & ~(moverseas) & ~(munlicensed)].copy()
    df_m_young_provisional = df_mdemo.loc[(myoung) & ~(msenior) & (mprovisional) & ~(moverseas) & ~(munlicensed)].copy()
    df_m_young_overseas = df_mdemo.loc[(myoung) & ~(msenior) & ~(mprovisional) & (moverseas) & ~(munlicensed)].copy()
    df_m_young_unlicensed = df_mdemo.loc[(myoung) & ~(msenior) & ~(mprovisional) & ~(moverseas) & (munlicensed)].copy()
    df_m_young_provisional_overseas = df_mdemo.loc[(myoung) & ~(msenior) & (mprovisional) & (moverseas) & ~(munlicensed)].copy()
    df_m_young_provisional_unlicensed = df_mdemo.loc[(myoung) & ~(msenior) & (mprovisional) & ~(moverseas) & (munlicensed)].copy()
    df_m_young_overseas_unlicensed = df_mdemo.loc[(myoung) & ~(msenior) & ~(mprovisional) & (moverseas) & (munlicensed)].copy()

    df_m_senior = df_mdemo.loc[~(myoung) & (msenior) & ~(mprovisional) & ~(moverseas) & ~(munlicensed)].copy()
    df_m_senior_provisional = df_mdemo.loc[~(myoung) & (msenior) & (mprovisional) & ~(moverseas) & ~(munlicensed)].copy()
    df_m_senior_overseas = df_mdemo.loc[~(myoung) & (msenior) & ~(mprovisional) & (moverseas) & ~(munlicensed)].copy()
    df_m_senior_unlicensed = df_mdemo.loc[~(myoung) & (msenior) & ~(mprovisional) & ~(moverseas) & (munlicensed)].copy()
    df_m_senior_provisional_overseas = df_mdemo.loc[~(myoung) & (msenior) & (mprovisional) & (moverseas) & ~(munlicensed)].copy()
    df_m_senior_provisional_unlicensed = df_mdemo.loc[~(myoung) & (msenior) & (mprovisional) & ~(moverseas) & (munlicensed)].copy()
    df_m_senior_overseas_unlicensed = df_mdemo.loc[~(myoung) & (msenior) & ~(mprovisional) & (moverseas) & (munlicensed)].copy()

    df_m_adult = df_mdemo.loc[~(myoung) & ~(msenior) & ~(mprovisional) & ~(moverseas) & ~(munlicensed)].copy()
    df_m_adult_provisional = df_mdemo.loc[~(myoung) & ~(msenior) & (mprovisional) & ~(moverseas) & ~(munlicensed)].copy()
    df_m_adult_overseas = df_mdemo.loc[~(myoung) & ~(msenior) & ~(mprovisional) & (moverseas) & ~(munlicensed)].copy()
    df_m_adult_unlicensed = df_mdemo.loc[~(myoung) & ~(msenior) & ~(mprovisional) & ~(moverseas) & (munlicensed)].copy()
    df_m_adult_provisional_overseas = df_mdemo.loc[~(myoung) & ~(msenior) & (mprovisional) & (moverseas) & ~(munlicensed)].copy()
    df_m_adult_provisional_unlicensed = df_mdemo.loc[~(myoung) & ~(msenior) & (mprovisional) & ~(moverseas) & (munlicensed)].copy()
    df_m_adult_overseas_unlicensed = df_mdemo.loc[~(myoung) & ~(msenior) & ~(mprovisional) & (moverseas) & (munlicensed)].copy()

    df_m_youngsenior = df_mdemo.loc[(myoung) & (msenior) & ~(mprovisional) & ~(moverseas) & ~(munlicensed)].copy()
    df_m_youngsenior_provisional = df_mdemo.loc[(myoung) & (msenior) & (mprovisional) & ~(moverseas) & ~(munlicensed)].copy()
    df_m_youngsenior_overseas = df_mdemo.loc[(myoung) & (msenior) & ~(mprovisional) & (moverseas) & ~(munlicensed)].copy()
    df_m_youngsenior_unlicensed = df_mdemo.loc[(myoung) & (msenior) & ~(mprovisional) & ~(moverseas) & (munlicensed)].copy()
    df_m_youngsenior_provisional_overseas = df_mdemo.loc[(myoung) & (msenior) & (mprovisional) & (moverseas) & ~(munlicensed)].copy()
    df_m_youngsenior_provisional_unlicensed = df_mdemo.loc[(myoung) & (msenior) & (mprovisional) & ~(moverseas) & (munlicensed)].copy()
    df_m_youngsenior_overseas_unlicensed =  df_mdemo.loc[(myoung) & (msenior) & ~(mprovisional) & (moverseas) & (munlicensed)].copy()



    fyoung, fsenior, fprovisional, foverseas, funlicensed = create_masks(df_fdemo)
    df_f_young = df_fdemo.loc[(fyoung) & ~(fsenior) & ~(fprovisional) & ~(foverseas) & ~(funlicensed)].copy()
    df_f_young_provisional = df_fdemo.loc[(fyoung) & ~(fsenior) & (fprovisional) & ~(foverseas) & ~(funlicensed)].copy()
    df_f_young_overseas = df_fdemo.loc[(fyoung) & ~(fsenior) & ~(fprovisional) & (foverseas) & ~(funlicensed)].copy()
    df_f_young_unlicensed = df_fdemo.loc[(fyoung) & ~(fsenior) & ~(fprovisional) & ~(foverseas) & (funlicensed)].copy()
    df_f_young_provisional_overseas = df_fdemo.loc[(fyoung) & ~(fsenior) & (fprovisional) & (foverseas) & ~(funlicensed)].copy()
    df_f_young_provisional_unlicensed = df_fdemo.loc[(fyoung) & ~(fsenior) & (fprovisional) & ~(foverseas) & (funlicensed)].copy()
    df_f_young_overseas_unlicensed = df_fdemo.loc[(fyoung) & ~(fsenior) & ~(fprovisional) & (foverseas) & (funlicensed)].copy()

    df_f_senior = df_fdemo.loc[~(fyoung) & (fsenior) & ~(fprovisional) & ~(foverseas) & ~(funlicensed)].copy()
    df_f_senior_provisional = df_fdemo.loc[~(fyoung) & (fsenior) & (fprovisional) & ~(foverseas) & ~(funlicensed)].copy()
    df_f_senior_overseas = df_fdemo.loc[~(fyoung) & (fsenior) & ~(fprovisional) & (foverseas) & ~(funlicensed)].copy()
    df_f_senior_unlicensed = df_fdemo.loc[~(fyoung) & (fsenior) & ~(fprovisional) & ~(foverseas) & (funlicensed)].copy()
    df_f_senior_provisional_overseas = df_fdemo.loc[~(fyoung) & (fsenior) & (fprovisional) & (foverseas) & ~(funlicensed)].copy()
    df_f_senior_provisional_unlicensed = df_fdemo.loc[~(fyoung) & (fsenior) & (fprovisional) & ~(foverseas) & (funlicensed)].copy()
    df_f_senior_overseas_unlicensed = df_fdemo.loc[~(fyoung) & (fsenior) & ~(fprovisional) & (foverseas) & (funlicensed)].copy()

    df_f_adult = df_fdemo.loc[~(fyoung) & ~(fsenior) & ~(fprovisional) & ~(foverseas) & ~(funlicensed)].copy()
    df_f_adult_provisional = df_fdemo.loc[~(fyoung) & ~(fsenior) & (fprovisional) & ~(foverseas) & ~(funlicensed)].copy()
    df_f_adult_overseas = df_fdemo.loc[~(fyoung) & ~(fsenior) & ~(fprovisional) & (foverseas) & ~(funlicensed)].copy()
    df_f_adult_unlicensed = df_fdemo.loc[~(fyoung) & ~(fsenior) & ~(fprovisional) & ~(foverseas) & (funlicensed)].copy()
    df_f_adult_provisional_overseas = df_fdemo.loc[~(fyoung) & ~(fsenior) & (fprovisional) & (foverseas) & ~(funlicensed)].copy()
    df_f_adult_provisional_unlicensed = df_fdemo.loc[~(fyoung) & ~(fsenior) & (fprovisional) & ~(foverseas) & (funlicensed)].copy()
    df_f_adult_overseas_unlicensed = df_fdemo.loc[~(fyoung) & ~(fsenior) & ~(fprovisional) & (foverseas) & (funlicensed)].copy()

    df_f_youngsenior = df_fdemo.loc[(fyoung) & (fsenior) & ~(fprovisional) & ~(foverseas) & ~(funlicensed)].copy()
    df_f_youngsenior_provisional = df_fdemo.loc[(fyoung) & (fsenior) & (fprovisional) & ~(foverseas) & ~(funlicensed)].copy()
    df_f_youngsenior_overseas = df_fdemo.loc[(fyoung) & (fsenior) & ~(fprovisional) & (foverseas) & ~(funlicensed)].copy()
    df_f_youngsenior_unlicensed = df_fdemo.loc[(fyoung) & (fsenior) & ~(fprovisional) & ~(foverseas) & (funlicensed)].copy()
    df_f_youngsenior_provisional_overseas = df_fdemo.loc[(fyoung) & (fsenior) & (fprovisional) & (foverseas) & ~(funlicensed)].copy()
    df_f_youngsenior_provisional_unlicensed = df_fdemo.loc[(fyoung) & (fsenior) & (fprovisional) & ~(foverseas) & (funlicensed)].copy()
    df_f_youngsenior_overseas_unlicensed =  df_fdemo.loc[(fyoung) & (fsenior) & ~(fprovisional) & (foverseas) & (funlicensed)].copy()






    mfyoung, mfsenior, mfprovisional, mfoverseas, mfunlicensed = create_masks(df_mfdemo)
    df_mf_young = df_mfdemo.loc[(mfyoung) & ~(mfsenior) & ~(mfprovisional) & ~(mfoverseas) & ~(mfunlicensed)].copy()
    df_mf_young_provisional = df_mfdemo.loc[(mfyoung) & ~(mfsenior) & (mfprovisional) & ~(mfoverseas) & ~(mfunlicensed)].copy()
    df_mf_young_overseas = df_mfdemo.loc[(mfyoung) & ~(mfsenior) & ~(mfprovisional) & (mfoverseas) & ~(mfunlicensed)].copy()
    df_mf_young_unlicensed = df_mfdemo.loc[(mfyoung) & ~(mfsenior) & ~(mfprovisional) & ~(mfoverseas) & (mfunlicensed)].copy()
    df_mf_young_provisional_overseas = df_mfdemo.loc[(mfyoung) & ~(mfsenior) & (mfprovisional) & (mfoverseas) & ~(mfunlicensed)].copy()
    df_mf_young_provisional_unlicensed = df_mfdemo.loc[(mfyoung) & ~(mfsenior) & (mfprovisional) & ~(mfoverseas) & (mfunlicensed)].copy()
    df_mf_young_overseas_unlicensed = df_mfdemo.loc[(mfyoung) & ~(mfsenior) & ~(mfprovisional) & (mfoverseas) & (mfunlicensed)].copy()

    df_mf_senior = df_mfdemo.loc[~(mfyoung) & (mfsenior) & ~(mfprovisional) & ~(mfoverseas) & ~(mfunlicensed)].copy()
    df_mf_senior_provisional = df_mfdemo.loc[~(mfyoung) & (mfsenior) & (mfprovisional) & ~(mfoverseas) & ~(mfunlicensed)].copy()
    df_mf_senior_overseas = df_mfdemo.loc[~(mfyoung) & (mfsenior) & ~(mfprovisional) & (mfoverseas) & ~(mfunlicensed)].copy()
    df_mf_senior_unlicensed = df_mfdemo.loc[~(mfyoung) & (mfsenior) & ~(mfprovisional) & ~(mfoverseas) & (mfunlicensed)].copy()
    df_mf_senior_provisional_overseas = df_mfdemo.loc[~(mfyoung) & (mfsenior) & (mfprovisional) & (mfoverseas) & ~(mfunlicensed)].copy()
    df_mf_senior_provisional_unlicensed = df_mfdemo.loc[~(mfyoung) & (mfsenior) & (mfprovisional) & ~(mfoverseas) & (mfunlicensed)].copy()
    df_mf_senior_overseas_unlicensed = df_mfdemo.loc[~(mfyoung) & (mfsenior) & ~(mfprovisional) & (mfoverseas) & (mfunlicensed)].copy()

    df_mf_adult = df_mfdemo.loc[~(mfyoung) & ~(mfsenior) & ~(mfprovisional) & ~(mfoverseas) & ~(mfunlicensed)].copy()
    df_mf_adult_provisional = df_mfdemo.loc[~(mfyoung) & ~(mfsenior) & (mfprovisional) & ~(mfoverseas) & ~(mfunlicensed)].copy()
    df_mf_adult_overseas = df_mfdemo.loc[~(mfyoung) & ~(mfsenior) & ~(mfprovisional) & (mfoverseas) & ~(mfunlicensed)].copy()
    df_mf_adult_unlicensed = df_mfdemo.loc[~(mfyoung) & ~(mfsenior) & ~(mfprovisional) & ~(mfoverseas) & (mfunlicensed)].copy()
    df_mf_adult_provisional_overseas = df_mfdemo.loc[~(mfyoung) & ~(mfsenior) & (mfprovisional) & (mfoverseas) & ~(mfunlicensed)].copy()
    df_mf_adult_provisional_unlicensed = df_mfdemo.loc[~(mfyoung) & ~(mfsenior) & (mfprovisional) & ~(mfoverseas) & (mfunlicensed)].copy()
    df_mf_adult_overseas_unlicensed = df_mfdemo.loc[~(mfyoung) & ~(mfsenior) & ~(mfprovisional) & (mfoverseas) & (mfunlicensed)].copy()
    df_mf_adult_overseas_provisional_unlicensed = df_mfdemo.loc[~(mfyoung) & ~(mfsenior) & (mfprovisional) & (mfoverseas) & (mfunlicensed)].copy()

    df_mf_youngsenior = df_mfdemo.loc[(mfyoung) & (mfsenior) & ~(mfprovisional) & ~(mfoverseas) & ~(mfunlicensed)].copy()
    df_mf_youngsenior_provisional = df_mfdemo.loc[(mfyoung) & (mfsenior) & (mfprovisional) & ~(mfoverseas) & ~(mfunlicensed)].copy()
    df_mf_youngsenior_overseas = df_mfdemo.loc[(mfyoung) & (mfsenior) & ~(mfprovisional) & (mfoverseas) & ~(mfunlicensed)].copy()
    df_mf_youngsenior_unlicensed = df_mfdemo.loc[(mfyoung) & (mfsenior) & ~(mfprovisional) & ~(mfoverseas) & (mfunlicensed)].copy()
    df_mf_youngsenior_provisional_overseas = df_mfdemo.loc[(mfyoung) & (mfsenior) & (mfprovisional) & (mfoverseas) & ~(mfunlicensed)].copy()
    df_mf_youngsenior_provisional_unlicensed = df_mfdemo.loc[(mfyoung) & (mfsenior) & (mfprovisional) & ~(mfoverseas) & (mfunlicensed)].copy()
    df_mf_youngsenior_overseas_unlicensed =  df_mfdemo.loc[(mfyoung) & (mfsenior) & ~(mfprovisional) & (mfoverseas) & (mfunlicensed)].copy()





    xyoung, xsenior, xprovisional, xoverseas, xunlicensed = create_masks(df_xdemo)
    df_x_young = df_xdemo.loc[(xyoung) & ~(xsenior) & ~(xprovisional) & ~(xoverseas) & ~(xunlicensed)].copy()
    df_x_young_provisional = df_xdemo.loc[(xyoung) & ~(xsenior) & (xprovisional) & ~(xoverseas) & ~(xunlicensed)].copy()
    df_x_young_overseas = df_xdemo.loc[(xyoung) & ~(xsenior) & ~(xprovisional) & (xoverseas) & ~(xunlicensed)].copy()
    df_x_young_unlicensed = df_xdemo.loc[(xyoung) & ~(xsenior) & ~(xprovisional) & ~(xoverseas) & (xunlicensed)].copy()
    df_x_young_provisional_overseas = df_xdemo.loc[(xyoung) & ~(xsenior) & (xprovisional) & (xoverseas) & ~(xunlicensed)].copy()
    df_x_young_provisional_unlicensed = df_xdemo.loc[(xyoung) & ~(xsenior) & (xprovisional) & ~(xoverseas) & (xunlicensed)].copy()
    df_x_young_overseas_unlicensed = df_xdemo.loc[(xyoung) & ~(xsenior) & ~(xprovisional) & (xoverseas) & (xunlicensed)].copy()

    df_x_senior = df_xdemo.loc[~(xyoung) & (xsenior) & ~(xprovisional) & ~(xoverseas) & ~(xunlicensed)].copy()
    df_x_senior_provisional = df_xdemo.loc[~(xyoung) & (xsenior) & (xprovisional) & ~(xoverseas) & ~(xunlicensed)].copy()
    df_x_senior_overseas = df_xdemo.loc[~(xyoung) & (xsenior) & ~(xprovisional) & (xoverseas) & ~(xunlicensed)].copy()
    df_x_senior_unlicensed = df_xdemo.loc[~(xyoung) & (xsenior) & ~(xprovisional) & ~(xoverseas) & (xunlicensed)].copy()
    df_x_senior_provisional_overseas = df_xdemo.loc[~(xyoung) & (xsenior) & (xprovisional) & (xoverseas) & ~(xunlicensed)].copy()
    df_x_senior_provisional_unlicensed = df_xdemo.loc[~(xyoung) & (xsenior) & (xprovisional) & ~(xoverseas) & (xunlicensed)].copy()
    df_x_senior_overseas_unlicensed = df_xdemo.loc[~(xyoung) & (xsenior) & ~(xprovisional) & (xoverseas) & (xunlicensed)].copy()

    df_x_adult = df_xdemo.loc[~(xyoung) & ~(xsenior) & ~(xprovisional) & ~(xoverseas) & ~(xunlicensed)].copy()
    df_x_adult_provisional = df_xdemo.loc[~(xyoung) & ~(xsenior) & (xprovisional) & ~(xoverseas) & ~(xunlicensed)].copy()
    df_x_adult_overseas = df_xdemo.loc[~(xyoung) & ~(xsenior) & ~(xprovisional) & (xoverseas) & ~(xunlicensed)].copy()
    df_x_adult_unlicensed = df_xdemo.loc[~(xyoung) & ~(xsenior) & ~(xprovisional) & ~(xoverseas) & (xunlicensed)].copy()
    df_x_adult_provisional_overseas = df_xdemo.loc[~(xyoung) & ~(xsenior) & (xprovisional) & (xoverseas) & ~(xunlicensed)].copy()
    df_x_adult_provisional_unlicensed = df_xdemo.loc[~(xyoung) & ~(xsenior) & (xprovisional) & ~(xoverseas) & (xunlicensed)].copy()
    df_x_adult_overseas_unlicensed = df_xdemo.loc[~(xyoung) & ~(xsenior) & ~(xprovisional) & (xoverseas) & (xunlicensed)].copy()

    df_x_youngsenior = df_xdemo.loc[(xyoung) & (xsenior) & ~(xprovisional) & ~(xoverseas) & ~(xunlicensed)].copy()
    df_x_youngsenior_provisional = df_xdemo.loc[(xyoung) & (xsenior) & (xprovisional) & ~(xoverseas) & ~(xunlicensed)].copy()
    df_x_youngsenior_overseas = df_xdemo.loc[(xyoung) & (xsenior) & ~(xprovisional) & (xoverseas) & ~(xunlicensed)].copy()
    df_x_youngsenior_unlicensed = df_xdemo.loc[(xyoung) & (xsenior) & ~(xprovisional) & ~(xoverseas) & (xunlicensed)].copy()
    df_x_youngsenior_provisional_overseas = df_xdemo.loc[(xyoung) & (xsenior) & (xprovisional) & (xoverseas) & ~(xunlicensed)].copy()
    df_x_youngsenior_provisional_unlicensed = df_xdemo.loc[(xyoung) & (xsenior) & (xprovisional) & ~(xoverseas) & (xunlicensed)].copy()
    df_x_youngsenior_overseas_unlicensed =  df_xdemo.loc[(xyoung) & (xsenior) & ~(xprovisional) & (xoverseas) & (xunlicensed)].copy()




    demo_mvalues = {'df_m_young' : df_m_young['Count_Crashes'].sum(),
               'df_m_young_provisional' : df_m_young_provisional['Count_Crashes'].sum(),
               'df_m_young_overseas' : df_m_young_overseas['Count_Crashes'].sum(),
               'df_m_young_unlicensed' : df_m_young_unlicensed['Count_Crashes'].sum(),
               'df_m_young_provisional_overseas' : df_m_young_provisional_overseas['Count_Crashes'].sum(),
               'df_m_young_provisional_unlicensed' : df_m_young_provisional_unlicensed['Count_Crashes'].sum(),
               'df_m_young_overseas_unlicensed' : df_m_young_overseas_unlicensed['Count_Crashes'].sum(),
               'df_m_senior' : df_m_senior['Count_Crashes'].sum(),
               'df_m_senior_provisional' : df_m_senior_provisional['Count_Crashes'].sum(),
               'df_m_senior_overseas' : df_m_senior_overseas['Count_Crashes'].sum(),
               'df_m_senior_unlicensed' : df_m_senior_unlicensed['Count_Crashes'].sum(),
               'df_m_senior_provisional_overseas' : df_m_senior_provisional_overseas['Count_Crashes'].sum(),
               'df_m_senior_provisional_unlicensed' : df_m_senior_provisional_unlicensed['Count_Crashes'].sum(),
               'df_m_senior_overseas_unlicensed' : df_m_senior_overseas_unlicensed['Count_Crashes'].sum(),
               'df_m_adult' : df_m_adult['Count_Crashes'].sum(),
               'df_m_adult_provisional' : df_m_adult_provisional['Count_Crashes'].sum(),
               'df_m_adult_overseas' : df_m_adult_overseas['Count_Crashes'].sum(),
               'df_m_adult_unlicensed' : df_m_adult_unlicensed['Count_Crashes'].sum(),
               'df_m_adult_provisional_overseas' : df_m_adult_provisional_overseas['Count_Crashes'].sum(),
               'df_m_adult_provisional_unlicensed' : df_m_adult_provisional_unlicensed['Count_Crashes'].sum(),
               'df_m_adult_overseas_unlicensed' : df_m_adult_overseas_unlicensed['Count_Crashes'].sum(),
               'df_f_adult_overseas_provisional_unlicensed' : 0,
               'df_m_youngsenior' : df_m_youngsenior['Count_Crashes'].sum(),
               'df_m_youngsenior_provisional' : df_m_youngsenior_provisional['Count_Crashes'].sum(),
               'df_m_youngsenior_overseas' : df_m_youngsenior_overseas['Count_Crashes'].sum(),
               'df_m_youngsenior_unlicensed' : df_m_youngsenior_unlicensed['Count_Crashes'].sum(),
               'df_m_youngsenior_provisional_overseas' : df_m_youngsenior_provisional_overseas['Count_Crashes'].sum(),
               'df_m_youngsenior_provisional_unlicensed' : df_m_youngsenior_provisional_unlicensed['Count_Crashes'].sum(), 
               'df_m_youngsenior_overseas_unlicensed' : df_m_youngsenior_overseas_unlicensed['Count_Crashes'].sum(),
               }
    

    demo_fvalues = {'df_f_young' : df_f_young['Count_Crashes'].sum(),
               'df_f_young_provisional' : df_f_young_provisional['Count_Crashes'].sum(),
               'df_f_young_overseas' : df_f_young_overseas['Count_Crashes'].sum(),
               'df_f_young_unlicensed' : df_f_young_unlicensed['Count_Crashes'].sum(),
               'df_f_young_provisional_overseas' : df_f_young_provisional_overseas['Count_Crashes'].sum(),
               'df_f_young_provisional_unlicensed' : df_f_young_provisional_unlicensed['Count_Crashes'].sum(),
               'df_f_young_overseas_unlicensed' : df_f_young_overseas_unlicensed['Count_Crashes'].sum(),
               'df_f_senior' : df_f_senior['Count_Crashes'].sum(),
               'df_f_senior_provisional' : df_f_senior_provisional['Count_Crashes'].sum(),
               'df_f_senior_overseas' : df_f_senior_overseas['Count_Crashes'].sum(),
               'df_f_senior_unlicensed' : df_f_senior_unlicensed['Count_Crashes'].sum(),
               'df_f_senior_provisional_overseas' : df_f_senior_provisional_overseas['Count_Crashes'].sum(),
               'df_f_senior_provisional_unlicensed' : df_f_senior_provisional_unlicensed['Count_Crashes'].sum(),
               'df_f_senior_overseas_unlicensed' : df_f_senior_overseas_unlicensed['Count_Crashes'].sum(),
               'df_f_adult' : df_f_adult['Count_Crashes'].sum(),
               'df_f_adult_provisional' : df_f_adult_provisional['Count_Crashes'].sum(),
               'df_f_adult_overseas' : df_f_adult_overseas['Count_Crashes'].sum(),
               'df_f_adult_unlicensed' : df_f_adult_unlicensed['Count_Crashes'].sum(),
               'df_f_adult_provisional_overseas' : df_f_adult_provisional_overseas['Count_Crashes'].sum(),
               'df_f_adult_provisional_unlicensed' : df_f_adult_provisional_unlicensed['Count_Crashes'].sum(),
               'df_f_adult_overseas_unlicensed' : df_f_adult_overseas_unlicensed['Count_Crashes'].sum(),
               'df_f_adult_overseas_provisional_unlicensed' : 0,
               'df_f_youngsenior' : df_f_youngsenior['Count_Crashes'].sum(),
               'df_f_youngsenior_provisional' : df_f_youngsenior_provisional['Count_Crashes'].sum(),
               'df_f_youngsenior_overseas' : df_f_youngsenior_overseas['Count_Crashes'].sum(),
               'df_f_youngsenior_unlicensed' : df_f_youngsenior_unlicensed['Count_Crashes'].sum(),
               'df_f_youngsenior_provisional_overseas' : df_f_youngsenior_provisional_overseas['Count_Crashes'].sum(),
               'df_f_youngsenior_provisional_unlicensed' : df_f_youngsenior_provisional_unlicensed['Count_Crashes'].sum(), 
               'df_f_youngsenior_overseas_unlicensed' : df_f_youngsenior_overseas_unlicensed['Count_Crashes'].sum(),
               }

    

    demo_mfvalues = {'df_mf_young' : df_mf_young['Count_Crashes'].sum(),
               'df_mf_young_provisional' : df_mf_young_provisional['Count_Crashes'].sum(),
               'df_mf_young_overseas' : df_mf_young_overseas['Count_Crashes'].sum(),
               'df_mf_young_unlicensed' : df_mf_young_unlicensed['Count_Crashes'].sum(),
               'df_mf_young_provisional_overseas' : df_mf_young_provisional_overseas['Count_Crashes'].sum(),
               'df_mf_young_provisional_unlicensed' : df_mf_young_provisional_unlicensed['Count_Crashes'].sum(),
               'df_mf_young_overseas_unlicensed' : df_mf_young_overseas_unlicensed['Count_Crashes'].sum(),
               'df_mf_senior' : df_mf_senior['Count_Crashes'].sum(),
               'df_mf_senior_provisional' : df_mf_senior_provisional['Count_Crashes'].sum(),
               'df_mf_senior_overseas' : df_mf_senior_overseas['Count_Crashes'].sum(),
               'df_mf_senior_unlicensed' : df_mf_senior_unlicensed['Count_Crashes'].sum(),
               'df_mf_senior_provisional_overseas' : df_mf_senior_provisional_overseas['Count_Crashes'].sum(),
               'df_mf_senior_provisional_unlicensed' : df_mf_senior_provisional_unlicensed['Count_Crashes'].sum(),
               'df_mf_senior_overseas_unlicensed' : df_mf_senior_overseas_unlicensed['Count_Crashes'].sum(),
               'df_mf_adult' : df_mf_adult['Count_Crashes'].sum(),
               'df_mf_adult_provisional' : df_mf_adult_provisional['Count_Crashes'].sum(),
               'df_mf_adult_overseas' : df_mf_adult_overseas['Count_Crashes'].sum(),
               'df_mf_adult_unlicensed' : df_mf_adult_unlicensed['Count_Crashes'].sum(),
               'df_mf_adult_provisional_overseas' : df_mf_adult_provisional_overseas['Count_Crashes'].sum(),
               'df_mf_adult_provisional_unlicensed' : df_mf_adult_provisional_unlicensed['Count_Crashes'].sum(),
               'df_mf_adult_overseas_unlicensed' : df_mf_adult_overseas_unlicensed['Count_Crashes'].sum(),
               'df_mf_adult_overseas_provisional_unlicensed' : df_mf_adult_overseas_provisional_unlicensed['Count_Crashes'].sum(),
               'df_mf_youngsenior' : df_mf_youngsenior['Count_Crashes'].sum(),
               'df_mf_youngsenior_provisional' : df_mf_youngsenior_provisional['Count_Crashes'].sum(),
               'df_mf_youngsenior_overseas' : df_mf_youngsenior_overseas['Count_Crashes'].sum(),
               'df_mf_youngsenior_unlicensed' : df_mf_youngsenior_unlicensed['Count_Crashes'].sum(),
               'df_mf_youngsenior_provisional_overseas' : df_mf_youngsenior_provisional_overseas['Count_Crashes'].sum(),
               'df_mf_youngsenior_provisional_unlicensed' : df_mf_youngsenior_provisional_unlicensed['Count_Crashes'].sum(), 
               'df_mf_youngsenior_overseas_unlicensed' : df_mf_youngsenior_overseas_unlicensed['Count_Crashes'].sum(),
               }



    demo_xvalues = {'df_x_young' : df_x_young['Count_Crashes'].sum(),
               'df_x_young_provisional' : df_x_young_provisional['Count_Crashes'].sum(),
               'df_x_young_overseas' : df_x_young_overseas['Count_Crashes'].sum(),
               'df_x_young_unlicensed' : df_x_young_unlicensed['Count_Crashes'].sum(),
               'df_x_young_provisional_overseas' : df_x_young_provisional_overseas['Count_Crashes'].sum(),
               'df_x_young_provisional_unlicensed' : df_x_young_provisional_unlicensed['Count_Crashes'].sum(),
               'df_x_young_overseas_unlicensed' : df_x_young_overseas_unlicensed['Count_Crashes'].sum(),
               'df_x_senior' : df_x_senior['Count_Crashes'].sum(),
               'df_x_senior_provisional' : df_x_senior_provisional['Count_Crashes'].sum(),
               'df_x_senior_overseas' : df_x_senior_overseas['Count_Crashes'].sum(),
               'df_x_senior_unlicensed' : df_x_senior_unlicensed['Count_Crashes'].sum(),
               'df_x_senior_provisional_overseas' : df_x_senior_provisional_overseas['Count_Crashes'].sum(),
               'df_x_senior_provisional_unlicensed' : df_x_senior_provisional_unlicensed['Count_Crashes'].sum(),
               'df_x_senior_overseas_unlicensed' : df_x_senior_overseas_unlicensed['Count_Crashes'].sum(),
               'df_x_adult' : df_x_adult['Count_Crashes'].sum(),
               'df_x_adult_provisional' : df_x_adult_provisional['Count_Crashes'].sum(),
               'df_x_adult_overseas' : df_x_adult_overseas['Count_Crashes'].sum(),
               'df_x_adult_unlicensed' : df_x_adult_unlicensed['Count_Crashes'].sum(),
               'df_x_adult_provisional_overseas' : df_x_adult_provisional_overseas['Count_Crashes'].sum(),
               'df_x_adult_provisional_unlicensed' : df_x_adult_provisional_unlicensed['Count_Crashes'].sum(),
               'df_x_adult_overseas_unlicensed' : df_x_adult_overseas_unlicensed['Count_Crashes'].sum(),
               'df_x_adult_overseas_provisional_unlicensed' : 0,
               'df_x_youngsenior' : df_x_youngsenior['Count_Crashes'].sum(),
               'df_x_youngsenior_provisional' : df_x_youngsenior_provisional['Count_Crashes'].sum(),
               'df_x_youngsenior_overseas' : df_x_youngsenior_overseas['Count_Crashes'].sum(),
               'df_x_youngsenior_unlicensed' : df_x_youngsenior_unlicensed['Count_Crashes'].sum(),
               'df_x_youngsenior_provisional_overseas' : df_x_youngsenior_provisional_overseas['Count_Crashes'].sum(),
               'df_x_youngsenior_provisional_unlicensed' : df_x_youngsenior_provisional_unlicensed['Count_Crashes'].sum(), 
               'df_x_youngsenior_overseas_unlicensed' : df_x_youngsenior_overseas_unlicensed['Count_Crashes'].sum(),
               }
    

    labels = ['Involving Young Driver (16-24)',
         'Involving Young Provisional Driver',
         'Involving Young Overseas Licensed Driver',
         'Involving Young Unlicensed_Driver',
         'Involving Young Provisional Driver & Overseas Licensed Driver',
         'Involving Young Provisional Driver & Unlicensed Driver',
         'Involving Young Overseas Licensed Driver & Unlicensed Driver',
         'Involving Senior Driver (60 plus)',
         'Involving Senior Provisional Driver',
         'Involving Senior Overseas Licensed Driver',
         'Involving Senior Unlicensed_Driver',
         'Involving Senior Provisional Driver & Overseas Licensed Driver',
         'Involving Senior Provisional Driver & Unlicensed Driver',
         'Involving Senior Overseas Licensed Driver & Unlicensed Driver',
         'Involving Adult Driver (25-59)',
         'Involving Adult Provisional Driver',
         'Involving Adult Overseas Licensed Driver',
         'Involving Adult Unlicensed_Driver',
         'Involving Adult Provisional Driver & Overseas Licensed Driver',
         'Involving Adult Provisional Driver & Unlicensed Driver',
         'Involving Adult Overseas Licensed Driver & Unlicensed Driver',
         'Involving Adult Overseas Licensed Driver, Provisional Driver & Unlicensed Driver', 
         'Involving Young & Senior Driver',
         'Involving Young & Senior Provisional Driver',
         'Involving Young & Senior Overseas Licensed Driver',
         'Involving Young & Senior Unlicensed_Driver',
         'Involving Young & Senior Provisional Driver & Overseas Licensed Driver',
         'Involving Young & Senior Provisional Driver & Unlicensed Driver',
         'Involving Young & Senior Overseas Licensed Driver & Unlicensed Driver',  
         ]


    df_demovalues = pd.DataFrame.from_dict(demo_mvalues, orient = 'index', columns =['Male'])
    df_demovalues['Female'] = demo_fvalues.values()
    df_demovalues['Both Male&Female'] = demo_mfvalues.values()
    df_demovalues['Undefined_Gender'] = demo_xvalues.values()
    df_demovalues['Desctription'] = labels
    df_demovalues = df_demovalues[['Desctription', 'Male', 'Female', 'Both Male&Female', 'Undefined_Gender']]
    df_demovalues.reset_index(drop = True, inplace = True)

    df_demovalues['Total'] = df_demovalues['Male'] + df_demovalues['Female'] + df_demovalues['Both Male&Female'] + df_demovalues['Undefined_Gender']
    df_demovalues['%_Male'] =  round(df_demovalues['Male']/df_demovalues['Total'] * 100, 2)
    df_demovalues['%_Female'] =  round(df_demovalues['Female']/df_demovalues['Total'] * 100, 2)
    df_demovalues['%_Both Male&Female'] =  round(df_demovalues['Both Male&Female']/df_demovalues['Total'] * 100, 2)
    df_demovalues['%_Undefined_Gender'] =  round(df_demovalues['Undefined_Gender']/df_demovalues['Total'] * 100, 2)

    df_demovalues['%_tMale'] =  round(df_demovalues['Male']/df_demovalues['Total'].sum() * 100, 2)
    df_demovalues['%_tFemale'] =  round(df_demovalues['Female']/df_demovalues['Total'].sum() * 100, 2)
    df_demovalues['%_tBoth Male&Female'] =  round(df_demovalues['Both Male&Female']/df_demovalues['Total'].sum() * 100, 2)
    df_demovalues['%_tUndefined_Gender'] =  round(df_demovalues['Undefined_Gender']/df_demovalues['Total'].sum() * 100, 2)
    df_demovalues.fillna(0, inplace = True)
    df_demovalues.sort_values('Male', inplace = True)
    df_demovalues = df_demovalues.loc[df_demovalues['Desctription'].isin(categories_list)].copy()
    df_demovalues.reset_index(drop = True, inplace = True)

    


    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_demovalues['Male'],
        y=df_demovalues['Desctription'],
        name='Male',
        text = ['<b>Percentage of Category:</b><i> {}%</b><br><b>Percentage of Total:</b><i> {}%<br>'.format(df_demovalues.iloc[i]['%_Male'], df_demovalues.iloc[i]['%_tMale']) for i in range(len(df_demovalues['Male']))],
        hovertemplate = '<b>%{y} - Male</b><br><b>N. of incidents:</b> <i>%{x}<br>%{text}',
        marker=dict(
            color='#006cb7',
            line = dict(width = 2,
                        color = '#002660'),
        )
    ))
    fig.add_trace(go.Scatter(
        x=df_demovalues['Female'], 
        y=df_demovalues['Desctription'],
        name='Female',
        text = ['<b>Percentage of Category:</b><i> {}%</b><br><b>Percentage of Total:</b><i> {}%<br>'.format(df_demovalues.iloc[i]['%_Female'], df_demovalues.iloc[i]['%_tFemale']) for i in range(len(df_demovalues['Female']))],
        hovertemplate = '<b>%{y} - Female</b><br><b>N. of incidents:</b> <i>%{x}<br>%{text}',
        marker=dict(
            color='#ffd302',
            line = dict(width = 2,
                        color = '#002660'),
        )
    ))

    fig.add_trace(go.Scatter(
        x=df_demovalues['Both Male&Female'], 
        y=df_demovalues['Desctription'],
        name='Both Male&Female',
        text = ['<b>Percentage of Category:</b><i> {}%</b><br><b>Percentage of Total:</b><i> {}%<br>'.format(df_demovalues.iloc[i]['%_Both Male&Female'], df_demovalues.iloc[i]['%_tBoth Male&Female']) for i in range(len(df_demovalues['Both Male&Female']))],
        hovertemplate = '<b>%{y} - Both Male&Female</b><br><b>N. of incidents:</b> <i>%{x}<br>%{text}',
        marker=dict(
            color='#88a05a',
            line = dict(width = 2,
                        color = '#002660'),
        )
    ))

    fig.update_traces(mode='markers', marker=dict(line_width=1.5, symbol='circle', size=((48/len(categories_list))+12)))

    fig.update_layout(
        title= 'Incidents demographic information',
        font = {'size' : 10},
        xaxis=dict(
            showgrid=False,
            linecolor='#d1d1d1',
            tickfont_color='black',
            tickfont = {'size' : 6},
            showticklabels = True,
            autorange = True,
            ticks='outside',
            type = 'log',
            tickcolor= 'black',
        ),

        yaxis = dict(
            showgrid=True,
            gridcolor = '#d1d1d1',
            tickfont = {'size' : 10},
        ),
        height=800,
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        hoverlabel = {'font' : {'size' : 10}},
        hovermode='closest',
        margin=dict(l=biggest_string*5.2, r=10, b=5, t=50),
        legend_orientation = 'h',
        legend=dict(
        font_size=10,
        x = -0.3,
        y = 1.01))
    
    return fig




@app.callback(
    Output('casualties_chart', 'figure'),
    [Input('casualty_selector', 'value'),
    Input('range_year', 'value')])
def update_casualties_chart(cas, range_year):

    dff = filter_dataframe(df_casualties, range_year)

    if cas != 'all':
        dff = dff.loc[dff['Casualty_Severity'] == cas].copy()
    else:
        cas = ['Hospitalised', 'Medically treated', 'Minor injury', 'Fatality']
        dff = dff.loc[dff['Casualty_Severity'].isin(cas)].copy()
    

    dff = pd.DataFrame(dff.groupby(['Casualty_AgeGroup', 'Casualty_Gender']).Casualty_Count.sum())
    dff.reset_index(inplace = True)
    dff.drop(index = dff.loc[dff['Casualty_Gender'] == 'Unknown'].index, axis = 1, inplace = True)
    dff['%total'] = dff.apply(lambda x: str(round(x['Casualty_Count']/dff['Casualty_Count'].sum()*100, 2))+'%', axis = 1)
    dff['%gender'] = dff.apply(lambda x: str(round(x['Casualty_Count']/dff.loc[dff['Casualty_Gender'] == 'Female', 'Casualty_Count'].sum()*100, 2))+'%' if x['Casualty_Gender'] == 'Female' else str(round(x['Casualty_Count']/dff.loc[dff['Casualty_Gender'] == 'Male', 'Casualty_Count'].sum()*100, 2))+'%' if x['Casualty_Gender'] == 'Male' else 0, axis = 1)
    ages = []
    for age in dff.Casualty_AgeGroup.unique():
        for i in range(len(dff)):
            if dff.iloc[i]['Casualty_AgeGroup'] == age:
                ages.append(str(round(dff.iloc[i]['Casualty_Count']/dff.loc[dff['Casualty_AgeGroup'] == age, 'Casualty_Count'].sum()*100, 2))+'%')

    dff['%ages'] = ages
    dff.sort_values(['Casualty_AgeGroup','Casualty_Gender'], inplace = True)
    dff['text'] = dff.apply(lambda x:'<b>Age Group:<b> <i>{}</i><br><b>N. of casualties:</b> <i>{}</i><br><b>% of Total:<b> <i>{}</i><br><b>% of Gender:<b> <i>{}</i><br><b>% of Age Group:<b> <i>{}</i><br>'.format(
                            x['Casualty_AgeGroup'], x['Casualty_Count'], x['%total'], x['%gender'], x['%ages']), axis = 1)



    colorscl = {'Male' : ['#eef4ff', '#d7e2f5', '#c0d0ec', '#a9bfe2', '#92aed9', '#799dcf', '#5f8cc5', '#417dbc', '#106db2'],
          'Female' : ['#f9f3e8', '#fdefd1', '#ffebbb', '#ffe7a7', '#ffe392', '#ffdf7b', '#ffdb60', '#ffd741', '#ffd302']}


    fig = go.Figure()
    for gender in dff.Casualty_Gender.unique():
        
        if gender != 'Unknown':
            
            fig.add_trace(go.Bar(
                            name = gender,
                            x = dff.loc[dff['Casualty_Gender'] == gender, 'Casualty_AgeGroup'],
                            y = dff.loc[dff['Casualty_Gender'] == gender, 'Casualty_Count'],
                            marker = dict(color = dff.loc[dff['Casualty_Gender'] == gender, 'Casualty_Count'],
                                colorscale = colorscl.get(gender),
                                line = dict(width = 2,
                                            color = '#002660')),
                            text = dff.loc[dff['Casualty_Gender'] == gender, 'text'],
                            hoverinfo = 'text+name',
                            #hovertemplate = '%{text}',
                            ))

            

    fig.update_layout(xaxis = {
                                'titlefont' : {'size' : 10},
                                'showgrid' : False,
                                'showgrid' : False,
                                'zeroline' : True,
                                'showspikes': False,
                                'nticks' : 10,
                                'tickfont' : {'size' : 8}},
                    
                    yaxis = {'title' : '',
                            'titlefont' : {'size' : 8},
                                'showticklabels' : True,
                            'tickfont' : {'size' : 8},
                                'showgrid' : False,},
                    
                    height=600,
                    barmode = 'group',
                    clickmode = 'event+select',
                    hoverlabel = {'font' : {'size' : 10}},
                    legend=dict(font_size=10),
                    title_text="Casualties by Gender and Age Group (click in the bar to see the road user type details)",
                    font = {'size' : 10},
                    plot_bgcolor="#F9F9F9",
                    paper_bgcolor="#F9F9F9",
                    margin=dict(l=0, r=0, b=0, t=40)),


                        
    return fig


last_value = 0
def has_pressed_button(n_clicks):
    global last_value
    if last_value == n_clicks:
        return False
    last_value = n_clicks
    return True


@app.callback(
    Output('casualties_bars', 'figure'),
    [Input('casualty_selector', 'value'),
    Input('casualties_chart', 'clickData'),
    Input('reset_total', 'n_clicks'),
    Input('range_year', 'value')])
def update_casualties_bars(cas, clickData, n_clicks, range_year):


    dff = filter_dataframe(df_casualties, range_year)

    if cas != 'all':
        dff = dff.loc[dff['Casualty_Severity'] == cas].copy()

    else:
        cas = ['Hospitalised', 'Medically treated', 'Minor injury', 'Fatality']
        dff = dff.loc[dff['Casualty_Severity'].isin(cas)].copy()
        
    
    if has_pressed_button(n_clicks):
        clickData = None

        

    
    if not clickData:
        dff_sub = pd.DataFrame(dff.groupby('Casualty_RoadUserType').Casualty_Count.sum())
        dff_sub.reset_index(inplace = True)
        dff_sub['percentage'] = dff_sub.apply(lambda x: str(round(x['Casualty_Count']/dff_sub['Casualty_Count'].sum()*100, 2))+'%', axis = 1)
        users = ['Driver', 'Passenger', 'Motorcyclist', 'Pedestrian', 'Bicyclist', 'Other']
        dff_sub['Casualty_RoadUserType'] = dff_sub['Casualty_RoadUserType'].astype(pd.api.types.CategoricalDtype(categories=users, ordered=True))
        dff_sub.sort_values('Casualty_RoadUserType', inplace = True)

        color_bars = '#88a05a'
        title = 'Road user type % Casualties: Total'

    elif clickData['points'][0]['curveNumber'] == 0:
        dff = dff.loc[dff['Casualty_AgeGroup'] == clickData['points'][0]['x']]
        dff = dff.loc[dff['Casualty_Gender'] == 'Female']
        dff_sub = pd.DataFrame(dff.groupby('Casualty_RoadUserType').Casualty_Count.sum())
        dff_sub.reset_index(inplace = True)
        dff_sub['percentage'] = dff_sub.apply(lambda x: str(round(x['Casualty_Count']/dff_sub['Casualty_Count'].sum()*100, 2))+'%', axis = 1)
        users = ['Driver', 'Passenger', 'Motorcyclist', 'Pedestrian', 'Bicyclist', 'Other']
        dff_sub['Casualty_RoadUserType'] = dff_sub['Casualty_RoadUserType'].astype(pd.api.types.CategoricalDtype(categories=users, ordered=True))
        dff_sub.sort_values('Casualty_RoadUserType', inplace = True)


        color_bars = '#ffd302'
        title = 'Road user type % Casualties: Female - ' + clickData['points'][0]['x'] + ' years'
    
    elif clickData['points'][0]['curveNumber'] == 1:
        dff = dff.loc[dff['Casualty_AgeGroup'] == clickData['points'][0]['x']]
        dff = dff.loc[dff['Casualty_Gender'] == 'Male']
        dff_sub = pd.DataFrame(dff.groupby('Casualty_RoadUserType').Casualty_Count.sum())
        dff_sub.reset_index(inplace = True)
        dff_sub['percentage'] = dff_sub.apply(lambda x: str(round(x['Casualty_Count']/dff_sub['Casualty_Count'].sum()*100, 2))+'%', axis = 1)
        users = ['Driver', 'Passenger', 'Motorcyclist', 'Pedestrian', 'Bicyclist', 'Other']
        dff_sub['Casualty_RoadUserType'] = dff_sub['Casualty_RoadUserType'].astype(pd.api.types.CategoricalDtype(categories=users, ordered=True))
        dff_sub.sort_values('Casualty_RoadUserType', inplace = True)


        color_bars = '#106db2'
        title = 'Road user type % Casualties: Male - ' + clickData['points'][0]['x'] + ' years'
    
    
    
    fig_sub = make_subplots(
    rows = 6, cols = 1,
    shared_xaxes=False,
    shared_yaxes=False,
    specs = [[{}], 
             [{}],
             [{}], 
             [{}], 
             [{}],
             [{}]],
    subplot_titles = ['Driver', 'Passenger', 'Motorcyclist', 'Pedestrian', 'Bicyclist', 'Other'],
    vertical_spacing= 0.10)

    for i, user in enumerate(dff_sub.Casualty_RoadUserType.unique()):
        
        
        fig_sub.add_trace(go.Bar(
                            name = user,
                            x = dff_sub.loc[dff_sub['Casualty_RoadUserType'] == user, 'Casualty_Count'],
                            y = [user],
                            marker = dict(color = color_bars,
                                            line = dict(width = 2,
                                                        color = '#002660')),
                            text = str('<b><i>{}</i></b>'.format(dff_sub.loc[dff_sub['Casualty_RoadUserType'] == user, 'percentage'].item())),
                            hovertemplate = '<b>No. of Casualties:</b> <i>%{x}</i>',
                            textposition = 'outside',
                            textfont= {'size' : 16},
                            orientation = 'h'), row = i+1, col = 1)

        
    xaxes = ['xaxis1', 'xaxis2', 'xaxis3', 'xaxis4', 'xaxis5', 'xaxis6']
    yaxes = ['yaxis1', 'yaxis2', 'yaxis3', 'yaxis4', 'yaxis5', 'yaxis6']

    for x, axex in enumerate(xaxes):    
        fig_sub['layout'][axex].update({
                                    'showline' : False,
                                    'zeroline' : False,
                                    'showticklabels' : False,
                                    'type' : 'log',
                                    'range' : [0, np.log10(dff_sub.Casualty_Count.max())*1.3],
                                    'tickfont' : {'size' : 8},
                                    'showgrid' : False})


    for y, axey in enumerate(yaxes): 
        fig_sub['layout'][axey].update({'tickfont' : {'size' : 8},
                                        'showticklabels' : False,
                                        'showline' : False,
                                        'showgrid' : False,
                                        'zeroline' : False})

    fig_sub.layout.images = [dict(
            source="https://raw.githubusercontent.com/vitoraugustosousa/dash_graph/master/driver1.png",
            xref="paper", yref="paper",
            x='14px', y=0.92,
            sizex=0.1, sizey=0.1,
            xanchor="center", yanchor="bottom"
        ), dict(
            source="https://raw.githubusercontent.com/vitoraugustosousa/dash_graph/master/passenger1.png",
            xref="paper", yref="paper",
            x='14px', y=0.73,
            sizex=0.1, sizey=0.1,
            xanchor="center", yanchor="bottom"
        ),
            dict(
            source="https://raw.githubusercontent.com/vitoraugustosousa/dash_graph/master/motorcyclist1.png",
            xref="paper", yref="paper",
            x='14px', y=0.54,
            sizex=0.11, sizey=0.11,
            xanchor="center", yanchor="bottom"
        ), dict(
            source="https://raw.githubusercontent.com/vitoraugustosousa/dash_graph/master/pedestrian1.png",
            xref="paper", yref="paper",
            x='14px', y=0.36,
            sizex=0.12, sizey=0.12,
            xanchor="center", yanchor="bottom"
        ), dict(
            source="https://raw.githubusercontent.com/vitoraugustosousa/dash_graph/master/bicyclist1.png",
            xref="paper", yref="paper",
            x='14px', y=0.17,
            sizex=0.12, sizey=0.12,
            xanchor="center", yanchor="bottom"
        ), dict(
            source="https://raw.githubusercontent.com/vitoraugustosousa/dash_graph/master/other1.png",
            xref="paper", yref="paper",
            x='14px', y=0,
            sizex=0.12, sizey=0.12,
            xanchor="center", yanchor="bottom"
        )]

    fig_sub.update_layout(

                        showlegend = False,
                        title = title,
                        font = {'size' : 10},
                        height = 600,
                        plot_bgcolor="#F9F9F9",
                        paper_bgcolor="#F9F9F9",
                        hoverlabel = dict(font = (dict(size = 10))),
                        margin=dict(l=50, r=20, b=20, t=60),
                        annotations=[go.layout.Annotation(
                        font = {'size' : 12})])
              

    return fig_sub


    

if __name__ == '__main__':
    app.run_server(debug = True)