# Importar bibliotecas necesarias
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Cargar datos de SpaceX con ruta absoluta
spacex_df = pd.read_csv("/home/project/spacex_launch_dash.csv")

# Obtener valores mínimos y máximos de carga útil
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Definir el diseño de la aplicación
app.layout = html.Div([
    html.H1("SpaceX Launch Records Dashboard",
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    html.Br(),

    # Menú desplegable para seleccionar el sitio de lanzamiento
    html.Div([
        html.Label("Select a Launch Site:", style={'font-size': '20px', 'color': 'black'}),
        dcc.Dropdown(
            id='site-dropdown',
            options=[{'label': 'All Sites', 'value': 'ALL'}] +
                    [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
            value='ALL',
            placeholder="Select a Launch Site here",
            searchable=True,
            style={'width': '50%', 'display': 'block'}
        )
    ]),

    html.Br(),

    # Control deslizante para seleccionar el rango de carga útil
    html.Div([
        html.Label("Select Payload Range (Kg):", style={'font-size': '20px', 'color': 'black'}),
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            value=[min_payload, max_payload],
            marks={i: str(i) for i in range(0, 11000, 2500)}
        )
    ]),

    html.Br(),

    # Gráfico de pastel para mostrar éxitos en los lanzamientos
    html.Div([
        dcc.Graph(id='success-pie-chart')
    ]),

    html.Br(),

    # Gráfico de dispersión para mostrar la relación entre carga útil y éxito
    html.Div([
        dcc.Graph(id='success-payload-scatter-chart')
    ])
])

# Callback para actualizar el gráfico de pastel según el sitio seleccionado
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        fig = px.pie(spacex_df, values='class', names='Launch Site', title='Total Successful Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(filtered_df, names='class', title=f'Success vs Failure for {selected_site}')
    return fig

# Callback para actualizar el gráfico de dispersión según el sitio y rango de carga útil seleccionados
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                            (spacex_df['Payload Mass (kg)'] <= payload_range[1])]

    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category',
                     title=f'Payload vs. Outcome for {selected_site}')
    return fig

# Ejecutar la aplicación en un puerto diferente para evitar conflictos
if __name__ == '__main__':
    print("La aplicación se está ejecutando correctamente.")
    app.run(debug=True, port=8060)