import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime
import copy

# Configures the ModeBar on the charts
config_charts = dict({
    'displayModeBar': 'hover',
    'displaylogo': False,
})

df = pd.read_excel('Data/Enquiry Report.xlsx',
                    sheet_name='Enquiry Report DataSheet',
                    index_col=None, na_values=['NA'])


# Exclude anything before January 1st 2016
df = df[df['Date'] > datetime(2015,12,31)]

# Converts column Date into Datetime Series
df['Date'] = pd.DatetimeIndex(df['Date'])

# Creates a list of unique years and months
year_list = pd.DatetimeIndex(df['Date']).year.unique().to_list()
month_list = pd.DatetimeIndex(df['Date']).month.unique().to_list()

# Create new columns in dataframe for metrics with multiple criterias
df['Total Enquiries'] = df['OL Enq less TBD'] + df ['Store Enq less TBD']
df['Store Reservations'] = df['StoreConversion'].fillna(df['Stores Res'])
df['Online Enq Res Online'] = df['OnlineResPurConversion'].fillna(df['OnlineRes'])
df['Online Enq Res in Store'] = (
    df['OnlineDropOutConversion']+df['WCFConversion']).fillna(
        (df['RES WCF']+df['Online Dropouts']))
df['Online Reservations'] = df['Online Enq Res Online'] + df['Online Enq Res in Store']
df['Total Reservations'] = df['Online Reservations'] + df['Store Reservations']


df_total = df.groupby(['Date']).sum().reindex()
df_total['year'] = pd.DatetimeIndex(df_total.index).year
df_total['month'] = pd.DatetimeIndex(df_total.index).month
df_total['month_name'] = pd.to_datetime(df_total['month'], format='%m').dt.month_name()


options = [{'label': 'Online Enquiries', 'value': 'OL Enq less TBD'},
           {'label': 'Store Enquiries', 'value': 'Store Enq less TBD'},
           {'label': 'Total Enquiries', 'value': 'Total Enquiries'},
           {'label': 'Walk-in Enquiries', 'value': 'STwalkin less TBD'},
           {'label': 'Phone-in Enquiries', 'value': 'STInCall less TBD'},
           {'label': 'Online Reservations', 'value': 'Online Reservations'},
           {'label': 'Store Reservations', 'value': 'Store Reservations'},
           {'label': 'Total Reservations', 'value': 'Total Reservations'},
           {'label': 'Walk-in Reservations', 'value': 'StResWalkin'},
           {'label': 'Phone-in Reservations', 'value': 'StResInCall'}
          ]

min_year = df_total['year'].min()
max_year = df_total['year'].max()

app = dash.Dash(__name__)

app.layout = html.Section(
    [
        html.Div(
            [
                html.H1(
                    'Enquiries & Reservations',
                    style={
                        'margin-bottom': '0px',
                    },
                ),
                html.H3(
                    'Marketing Overview',
                    style={
                        'margin-top': '0px',
                        'margin-bottom': '20px',
                    },
                ),
            ],
        ),

        # * Grid Container
        html.Div(
            [
                # * YoY Control Panel
                html.Div(
                    [
                        html.P(
                            'Filter by type of Enquiry/Reservation:',
                            className='label',
                        ),
                        dcc.Dropdown(
                            id='enquiry-type',
                            options = options,
                            value = options[0]['value'],
                            clearable=False,
                        ),
                        html.P(
                            'Slide to add/remove years:',
                            className='label',
                        ),
                        dcc.RangeSlider(
                            id='slider-years',
                            min=min_year,
                            max=max_year,
                            step=1,
                            value=[max_year -2, max_year],
                            className='yoy-slider',
                        ),
                    ],
                    id='yoy-panel',
                    className='styled-panel control-panel',
                ),

                # * YoY Chart
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Graph(
                                    id='totals-yoy',
                                    config=config_charts,
                                    style=dict(
                                        height='350px',
                                    )
                                ),
                            ],
                            className='styled-panel',
                        ),
                    ],
                    id='yoy-chart',
                    className='chart-container',
                ),
                html.Div(
                    [
                        dcc.Graph(
                            id='metric-trend-chart',
                            config=config_charts,
                            style=dict(
                                height='350px',
                            )
                        ),
                    ],
                    id='trend-chart',
                    className='styled-panel',
                ),
            ],
            className='grid-container',
        ),
    ],
    id="main-section",
)


@app.callback(Output('totals-yoy', 'figure'),
             [Input('enquiry-type', 'value'),
              Input('slider-years', 'value')])
def update_totals_yoy(yaxis_value, years_range):

    chart_title = [label for label in options if label['value'] == yaxis_value]

    data = []
    for year in year_list[::-1]:
        if year >= years_range[0] and year <= years_range[1]:
            trace = go.Scatter(
                        x=df_total['month_name'],
                        y=df_total[df_total['year']==year][yaxis_value],
                        mode='lines+markers',
                        name=year,
                        line=dict(
                            shape='spline',
                            smoothing=0.7,
                        )
                    )
            data.append(trace)

    layout = go.Layout(
                title={
                    'text': chart_title[0]['label'],
                    'y':0.99,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                },
                xaxis={
                    # 'title': 'Month',
                    'gridcolor': '#eeeeee',
                },
                yaxis={'title': 'Enquiries'},
                hovermode='x',
                plot_bgcolor='#F9F9F9',
                paper_bgcolor='#F9F9F9',
                autosize=True,
                margin=dict(l=60, r=20, b=30, t=30),
                template=None,
            )

    figure = go.Figure(data=data, layout=layout)
    return figure


@app.callback(Output('metric-trend-chart', 'figure'),
              [Input('enquiry-type', 'value')])
def update_graph(yaxis_value):

    chart_title = [label for label in options if label['value'] == yaxis_value]
    
    # layout_chart = copy.deepcopy(layout)

    figure={
        'data': [
            go.Scatter(
                x=df_total.index,
                y=df_total[yaxis_value],
                mode='lines+markers',
                line=dict(
                    shape='spline',
                    smoothing=0.7,
                )
            )
        ],
        'layout':
            go.Layout(
                title=chart_title[0]['label'],
                # xaxis={'title': 'Date'},
                yaxis={'title': 'Enquiries'},
                xaxis_tickformat='%B %Y',
                hovermode='closest',
                plot_bgcolor='#F9F9F9',
                paper_bgcolor='#F9F9F9',
                autosize=True,
                margin=dict(l=60, r=20, b=30, t=30),
            ),
    }
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
