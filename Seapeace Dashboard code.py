from dash import Dash, html, dcc, Input, Output  # pip install dash
import plotly.express as px
import dash_ag_grid as dag                       # pip install dash-ag-grid
import dash_bootstrap_components as dbc          # pip install dash-bootstrap-components
import pandas as pd                              # pip install pandas
import datetime
from datetime import date

import matplotlib                                # pip install matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO

df = pd.read_csv("/Users/chris/Downloads/SeapeaceTestingData.csv")

def extract_date(s):
    year = int(s / 10000)
    month = int((s % 10000) / 100)
    day = int(s % 100)
    return date(year, month, day)

dates = df['CleanupDate'].apply(extract_date)#.tolist()
df['Date'] = dates


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container([     #This is everything that exists on the page
    html.H1("Seapeace Data Collection", className='mb-2', style={'textAlign':'center'}),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='category',
                value=20240310,
                clearable=False,
                options=[{'label': str(date), 'value': date} for date in df['CleanupDate']])
        ], width=4)
    ]),

    dbc.Row([
        dbc.Col([
            html.Img(id='bar-graph-matplotlib')
        ], width=12)
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar-graph-plotly', figure={})
        ], width=12, md=6),
        dbc.Col([
            dag.AgGrid(
                id='grid',
                rowData=df.to_dict("records"),
                columnDefs=[{"field": i} for i in df.columns],
                columnSize="sizeToFit",
            )
        ], width=12, md=6),
    ], className='mt-4'),

])

# Create interactivity between dropdown component and graph
@app.callback(
    Output(component_id='bar-graph-matplotlib', component_property='src'),
    Output('bar-graph-plotly', 'figure'),
    Output('grid', 'defaultColDef'),
    Input('category', 'value'),
)
def plot_data(selected_yaxis): #Meaning wise is = selected cleanup date
    
    # Build the matplotlib figure
    fig = plt.figure(figsize=(14, 5))
    row = df[df['CleanupDate'] == selected_yaxis]
    y = row.iloc[:, 2:7].values.flatten()
    plt.bar(df.columns[2:7], y)
    plt.ylabel('Amount Collected')
    plt.xticks(rotation=10)

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    fig_bar_matplotlib = f'data:image/png;base64,{fig_data}'

    # Build the Plotly figure
    # df['Date'] = df['CleanupDate'].apply(extract_date)
    # df_filtered = df[df['Date'] == selected_yaxis]
    fig_bar_plotly = px.bar(df, x='Date', y='PlasticBottles').update_xaxes(tickangle=330)

    my_cellStyle = {
        "styleConditions": [
            {
                "condition": f"params.colDef.field == '{selected_yaxis}'",
                "style": {"backgroundColor": "#d3d3d3"},
            },
            {   "condition": f"params.colDef.field != '{selected_yaxis}'",
                "style": {"color": "black"}
            },
        ]
    }

    return fig_bar_matplotlib, fig_bar_plotly, {'cellStyle': my_cellStyle}


if __name__ == '__main__':
    app.run_server(debug=True, port=8002)