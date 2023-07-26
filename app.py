import plotly.graph_objects as go
import plotly.io as pio
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from sklearn.linear_model import LinearRegression
import plotly.express as px

df = pd.read_csv("https://buypharmadata.s3.us-west-2.amazonaws.com/train_clean.csv")
start_date = pd.to_datetime("2023-01-01")
df['date'] = start_date + pd.to_timedelta(df['day'] - 1, unit='D')

# Read the first dataset from "Pharmacy_Global.csv"
df_global = pd.read_csv("Pharmacy_Global.csv")

# Convert 'TIME' column to numeric
df_global['TIME'] = pd.to_numeric(df_global['TIME'])

# Rename 'USD_PER' to 'USD_CAP'
df_global.rename(columns={'USD_PER': 'USD_CAP'}, inplace=True)

# Add 'MXN_CAP' column by multiplying 'USD_CAP' by 20
df_global['MXN_CAP'] = df_global['USD_CAP'] * 20

# Read the second dataset from "saleshourly1.csv"
df_sales_hourly = pd.read_csv("saleshourly.csv")
df_sales_hourly.rename(columns={
    "ACIDO ACETICO DERIVADOS Y RELACIONADOS": "M01AB",
    "ACIDO PROPIONICO Y DERIVADOS": "M01AE",
    "SALICÍLICO ÁCIDO Y DERIVADOS": "N02BA",
    "ANILIDAS": "N02BE",
    "ANSIOLITICOS": "N05B",
    "ANTIDEPRESIVOS": "N05C",
    "AGENTES CONTRA ALTERACIONES OBSTRUCTIVAS DE LAS VÍAS PULMONARES": "R03",
    "ANTIHISTAMINICOS PARA USO SISTEMICO": "R06"
}, inplace=True)

# Get unique values from the 'LOCATION' column in df_global
locations = df_global['LOCATION'].unique()

# Get unique values for the time metric
time_metrics = ['HOUR', 'DAY', 'MONTH', 'YEAR']

# Define the HTML table content
drug_table_data = {
    "M01AB": "ACIDO ACETICO DERIVADOS y RELACIONADOS",
    "M01AE": "ACIDO PROPIONICO Y DERIVADOS",
    "N02BA": "SALICÍLICO ÁCIDO Y DERIVADOS",
    "N02BE": "ANILIDAS",
    "N05B": "ANSIOLITICOS",
    "N05C": "ANTIDEPRESIVOS",
    "R03": "AGENTES CONTRA ALTERACIONES OBSTRUCTIVAS DE LAS VÍAS PULMONARES",
    "R06": "ANTIHISTAMINICOS PARA USO SISTEMICO"
}

# Define the colors for each row (codes are in order)
drug_table_colors = [
    '#636EFB',
    '#EF553B',
    '#01CC96',
    '#AB63FB',
    '#FEA15A',
    '#15D3F2',
    '#FF6692',
    '#B5E880'
]

# Create the app with suppress_callback_exceptions=True
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Create the layout
app.layout = html.Div(
    style={
        'font-family': 'Arial, sans-serif',
        'max-width': '800px',
        'margin': 'auto',
        'padding': '20px'
    },
    children=[
        html.H1(
            'Gasto en medicamento en MXN per cápita',
            style={
                'text-align': 'center',
                'margin-bottom': '40px'
            }
        ),
        html.Div(
            style={'text-align': 'center'},
            children=[
                html.Label(
                    'Elige un país:',
                    style={'margin-right': '10px'}
                ),
                dcc.Dropdown(
                    id='location-dropdown',
                    options=[{'label': location, 'value': location} for location in locations],
                    value='All',
                    style={'display': 'inline-block', 'width': '200px'}
                )
            ]
        ),
        dcc.Graph(
            id='bar-chart',
            style={'margin-top': '40px'}
        ),

        html.H1(
            'Análisis ventas farmacia USA 24-2019',
            style={
                'text-align': 'center',
                'margin-bottom': '40px'
            }
        ),
        html.Div(
            style={'text-align': 'center'},
            children=[
                html.Label(
                    'Elige una métrica de tiempo:',
                    style={'margin-right': '10px'}
                ),
                dcc.Dropdown(
                    id='time-dropdown',
                    options=[{'label': metric, 'value': metric} for metric in time_metrics],
                    value='HOUR',
                    style={'display': 'inline-block', 'width': '200px'}
                )
            ]
        ),
        dcc.Graph(
            id='line-chart',
            style={'margin-top': '40px'}
        ),
        
        # Add the HTML table after the second chart and before the date range filter
        html.Div(
            style={
                'margin-top': '40px',
                'margin-bottom': '40px',
                'text-align': 'center'
            },
            children=[
                html.H2('Información de las categorías de medicamentos'),
                html.Table(
                    style={
                        'margin': 'auto',
                        'border-collapse': 'collapse',
                        'width': '80%'
                    },
                    children=[
                        html.Thead(
                            children=[
                                html.Tr(
                                    children=[
                                        html.Th('Código'),
                                        html.Th('Categoría de Medicamento')
                                    ]
                                )
                            ]
                        ),
                        html.Tbody(
                            children=[
                                html.Tr(
                                    children=[
                                        html.Td(
                                            code,
                                            style={
                                                'color': drug_table_colors[i],
                                                'padding': '8px'
                                            }
                                        ),
                                        html.Td(
                                            category,
                                            style={
                                                'color': '#141414',
                                                'padding': '8px'
                                            }
                                        )
                                    ]
                                )
                                for i, (code, category) in enumerate(drug_table_data.items())
                            ]
                        )
                    ]
                )
            ]
        ),

        # Date range filter for selecting start and end dates
        html.Div(
            style={'text-align': 'center'},
            children=[
                html.H1(
            'Comportamiento e-commerce durante 92 días',
            style={
                'text-align': 'center',
                'margin-bottom': '40px'
            }
        ),
                html.Label('Elige la fecha de inicio:'),
                dcc.DatePickerSingle(
                    id='start-date-picker',
                    min_date_allowed=df['date'].min(),
                    max_date_allowed=df['date'].max(),
                    initial_visible_month=df['date'].min(),
                    date=df['date'].min()
                ),
                html.Label('Elige la fecha final:'),
                dcc.DatePickerSingle(
                    id='end-date-picker',
                    min_date_allowed=df['date'].min(),
                    max_date_allowed=df['date'].max(),
                    initial_visible_month=df['date'].max(),
                    date=df['date'].max()
                )
            ]
        ),
        dcc.Graph(
            id='metric-comparison',
            style={'margin-top': '40px'}
        ),
    ]
)

# Define the first callback function
@app.callback(
    dash.dependencies.Output('bar-chart', 'figure'),
    dash.dependencies.Input('location-dropdown', 'value')
)
def update_bar_chart(selected_location):
    if selected_location == 'All':
        filtered_df = df_global
        title = 'Todos'
    else:
        filtered_df = df_global[df_global['LOCATION'] == selected_location]
        title = selected_location

    # Separate data into features (X) and target (y)
    X = filtered_df[['TIME']]
    y = filtered_df['MXN_CAP']

    # Fit linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Create future time values for prediction
    future_years = [2022, 2023, 2024, 2025]
    future_X = pd.DataFrame({'TIME': future_years})

    # Predict the MXN_CAP values for future years
    future_predictions = model.predict(future_X)

    fig = go.Figure(data=[
        go.Bar(x=filtered_df['TIME'], y=filtered_df['MXN_CAP'], name='Datos actuales'),
        go.Bar(x=future_years, y=future_predictions, name='Predicción')
    ])
    fig.update_layout(
        title=title,
        xaxis_title='AÑO',
        yaxis_title='MXN_CAP',
        template='plotly_white',
        barmode='group'
    )
    return fig


# Define the second callback function
@app.callback(
    dash.dependencies.Output('line-chart', 'figure'),
    dash.dependencies.Input('time-dropdown', 'value')
)
def update_line_chart(selected_time_metric):
    filtered_df = df_sales_hourly

    mean_sales = filtered_df.groupby(selected_time_metric)[[
        "M01AB",
        "M01AE",
        "N02BA",
        "N02BE",
        "N05B",
        "N05C",
        "R03",
        "R06"
    ]].mean().reset_index()

    fig = go.Figure()
    for column in mean_sales.columns[1:]:
        fig.add_trace(go.Line(x=mean_sales[selected_time_metric], y=mean_sales[column], name=column))

    fig.update_layout(
        title='Promedio de ventas por {}'.format(selected_time_metric),
        xaxis_title=selected_time_metric,
        yaxis_title='Mean Sales',
        template='plotly_white'
    )
    return fig


# Define the third callback function with date range inputs
@app.callback(
    dash.dependencies.Output('metric-comparison', 'figure'),
    dash.dependencies.Input('start-date-picker', 'date'),
    dash.dependencies.Input('end-date-picker', 'date')
)
def update_metric_comparison(start_date, end_date):
    # Convert selected date strings to datetime objects
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter the data based on the selected date range
    filtered_data = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    # Group the data by date and calculate the total for each metric
    grouped_data = filtered_data.groupby('date').agg({
        'click': 'sum',
        'basket': 'sum',
        'order': 'sum'
    }).reset_index()

    # Create the plot using Plotly express
    fig = px.line(grouped_data, x='date', y=['click', 'basket', 'order'],
                  labels={'date': 'Fecha', 'value': 'Total'})

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)