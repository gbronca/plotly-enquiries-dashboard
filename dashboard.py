import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime


df = pd.read_excel('Data/Enquiry Report.xlsm',
                    sheet_name='Enquiry Report DataSheet',
                    index_col=None, na_values=['NA'])

# Exclude anything before January 1st 2016
df = df[df['Date'] > datetime(2015,12,31)]

# Create new columns in dataframe for metrics with multiple criterias
df['Total Enquiries'] = df['OL Enq less TBD'] + df ['Store Enq less TBD']
df['Store Reservations'] = df['StoreConversion'].fillna(df['Stores Res'])
df['Online Enq Res Online'] = df['OnlineResPurConversion'].fillna(df['OnlineRes'])
df['Online Enq Res in Store'] = (df['OnlineDropOutConversion']+df['WCFConversion']).fillna((df['RES WCF']+df['Online Dropouts']))
df['Online Reservations'] = df['Online Enq Res Online'] + df['Online Enq Res in Store']
df['Total Reservations'] = df['Online Reservations'] + df['Store Reservations']


df_total = df.groupby(['Date']).sum().reindex()



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



app = dash.Dash()

app.layout = html.Section([
        html.H1('Enquiries & Reservations',
                style={'text-align': 'center'}
        ),
        html.Div([
            dcc.Dropdown(id='enquiry-type',
            options = options,
            value = options[0]['value'])
        ], style={'width': '250px',
                  'display': 'inline-block',
                  'marginLeft': '20px'}),

        
        html.Div([
            dcc.Graph(id='company-total')
            
        ])

])

@app.callback(Output('company-total', 'figure'),
              [Input('enquiry-type', 'value')])
def update_graph(yaxis_value):

    chart_title = [label for label in options if label['value'] == yaxis_value]

    figure={
        'data': [
            {'x': df_total.index, 
            'y': df_total[yaxis_value]}
        ],
        'layout':{'title': chart_title[0]['label'],
                'xaxis':{'title':'Date'},
                'yaxis':{'title': 'Enquiries'},
                'margin':{'l': '20px', 'b': '20px', 't': '15px', 'r': '20px'}
        }        
    }
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
