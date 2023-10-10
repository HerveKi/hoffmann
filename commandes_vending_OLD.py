import pandas as pd
import plotly.express as px
from dash import Dash, dash_table, dcc, html, Input, Output, callback

df = pd.read_csv('https://raw.githubusercontent.com/HerveKi/hoffmann/main/commandes_vending.csv', parse_dates=['date_commande'], dayfirst=True)

gvl = pd.read_csv('https://raw.githubusercontent.com/HerveKi/hoffmann/main/gvl.csv')


df['montant'] = df['montant'].str.replace(" ", "").str.replace("€", "").str.replace(",", "").astype("float")

df['annee'] = df['date_commande'].dt.year

df = pd.concat([df, gvl])

region_dict = {
    'region' : ['FR001', 'FR002', 'FR003', 'FR004', 'FR005', 'FR006', 'FR007', 'FR008', 'FR009'],
    'seb' : ['Didier', 'Ali', 'Ali', 'Ali', 'Hervé', 'Ali', 'Ali', 'Didier', 'Hervé']
}

region = pd.DataFrame(region_dict)

df = pd.merge(df, region, how='inner', on='region')

# customers dataframe
clients = df[['region', 'gvl', 'seb', 'id_client', "annee"]].copy()

clients['nb_clients'] = 1

clients_1 = clients.loc[clients['id_client'].notna()].drop_duplicates('id_client')

clients_2 = clients.loc[clients['id_client'].isna()].copy()

clients_2['nb_clients'] = 0

clients = pd.concat([clients_1, clients_2])

# machines dataframe
machines = df[['region', 'gvl', 'seb',  'nb_armoires', 'annee']]

# turnover dataframe
ca = df[['region', 'gvl', 'seb',  'montant', 'annee']]

# installations dataframe
installations = df[['region', 'gvl', 'seb', 'nb_installations', 'annee']]

annee_min = df['annee'].min()
annee_max = df['annee'].max()

app = Dash(__name__)

app.layout = html.Div([

    html.H1("Tool24 Overview"),

    html.Label("Responsables de région :"),
    dcc.RadioItems(
        options=[
            "Tous",
            "Ali",
            "Didier",
            "Hervé"
        ],
        value="Tous",
        id='seb-radio'),

    html.Label("Données d'analyse :"),
    dcc.RadioItems(
        options=["Nombre de clients",
                 "Nombre d'armoires",
                 "Chiffre d'affaires",
                 "Nombre d'installations"],
        value="Nombre de clients",
        id='data-radio'),

    html.Label("Période d'analyse :"),
    dcc.RangeSlider(
        min = annee_min,
        max= annee_max,
        step = 1,
        value = [annee_min, annee_max],
        marks={i: str(i) for i in range(annee_min, annee_max+1)},
        id='year-slider'),

    html.Label("Total :"),
    html.Div(id='total'),

    dcc.Graph(figure={}, id='linechart'),

    dcc.Graph(figure={}, id='boxplot'),

    dcc.Graph(figure={}, id='barchart'),

    dash_table.DataTable(id='table')
])

@app.callback(
    Output('total', 'children'),
    Output('linechart', 'figure'),
    Output('boxplot', 'figure'),
    Output('barchart', 'figure'),
    Output('table', 'data'),
    Input('seb-radio', 'value'),
    Input('data-radio', 'value'),
    Input('year-slider', 'value')
)
def update_table(selected_seb, selected_data, selected_years):

    year_min_selected = selected_years[0]

    year_max_selected = selected_years[1]

    if selected_seb == 'Tous':

        selected_seb = ['Ali', 'Didier', 'Hervé']

    else:

        selected_seb = [selected_seb]

    if selected_data == "Nombre de clients":

        data = clients.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')[['gvl', 'nb_clients']].groupby('gvl').sum().sort_values('nb_clients', ascending=False).reset_index().rename(columns={'gvl': 'Commercial', 'nb_clients': "Nombre de clients"}).to_dict('records')

        boxplot = px.box(
            data_frame = clients.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')[['gvl', 'nb_clients']].groupby('gvl').sum().reset_index().rename(columns={'gvl': 'Commercial', 'nb_clients': "Nombre de clients"}),
            y = "Nombre de clients"
        )

        linechart = px.line(
            data_frame = clients.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')[['annee', 'nb_clients']].groupby('annee').sum().reset_index().rename(columns={'annee': 'Année', 'nb_clients': "Nombre de clients"}),
            x = "Année",
            y = "Nombre de clients"
        )

        total = clients.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')["nb_clients"].sum()

        barchart = px.bar(
            data_frame = clients.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')[['gvl', 'nb_clients']].groupby('gvl').sum().sort_values('nb_clients').reset_index().rename(columns={'gvl': 'Commercial', 'nb_clients': "Nombre de clients"}).tail(10),
            x="Nombre de clients",
            y="Commercial"
        )

    if selected_data == "Nombre d'armoires":

        data = machines.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')[['gvl', 'nb_armoires']].groupby('gvl').sum().sort_values('nb_armoires', ascending=False).reset_index().rename(columns={'gvl': 'Commercial', 'nb_armoires': "Nombre d'armoires"}).to_dict('records')

        boxplot = px.box(
            data_frame = machines.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')[['gvl', 'nb_armoires']].groupby('gvl').sum().reset_index().rename(columns={'gvl': 'Commercial', 'nb_armoires': "Nombre d'armoires"}),
            y = "Nombre d'armoires"
        )

        linechart = px.line(
            data_frame = machines.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')[['annee', 'nb_armoires']].groupby('annee').sum().reset_index().rename(columns={'annee': 'Année', 'nb_armoires': "Nombre d'armoires"}),
            x = "Année",
            y = "Nombre d'armoires"
        )

        barchart = px.bar(
            data_frame = machines.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')[['gvl', 'nb_armoires']].groupby('gvl').sum().sort_values('nb_armoires').reset_index().rename(columns={'gvl': 'Commercial', 'nb_armoires': "Nombre d'armoires"}).tail(10),
            x="Nombre d'armoires",
            y="Commercial"
        )

        total = machines.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')["nb_armoires"].sum()

    if selected_data == "Chiffre d'affaires":

        data = ca.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')[['gvl', 'montant']].groupby('gvl').sum().sort_values('montant', ascending=False).reset_index().rename(columns={'gvl': 'Commercial', 'montant': "Chiffre d'affaires"}).to_dict('records')

        boxplot = px.box(
            data_frame = ca.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')[['gvl', 'montant']].groupby('gvl').sum().reset_index().rename(columns={'gvl': 'Commercial', 'montant': "Chiffre d'affaires"}),
            y = "Chiffre d'affaires"
        )

        linechart = px.line(
            data_frame = ca.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')[['annee', 'montant']].groupby('annee').sum().reset_index().rename(columns={'annee': 'Année', 'montant': "Chiffre d'affaires"}),
            x = "Année",
            y = "Chiffre d'affaires"
        )

        barchart = px.bar(
            data_frame = ca.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')[['gvl', 'montant']].groupby('gvl').sum().sort_values('montant').reset_index().rename(columns={'gvl': 'Commercial', 'montant': "Chiffre d'affaires"}).tail(10),
            x="Chiffre d'affaires",
            y="Commercial"
        )

        total = ca.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')["montant"].sum()

    if selected_data == "Nombre d'installations":

        data = installations.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')[["gvl", "nb_installations"]].groupby('gvl').sum().sort_values('nb_installations', ascending=False).reset_index().rename(columns={'gvl': 'Commercial', 'nb_installations': "Nombre d'installations"}).to_dict('records')

        boxplot = px.box(
            data_frame = installations.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')[["gvl", "nb_installations"]].groupby('gvl').sum().reset_index().rename(columns={'gvl': 'Commercial', 'nb_installations': "Nombre d'installations"}),
            y = "Nombre d'installations"
        )

        linechart = px.line(
            data_frame = installations.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')[['annee', 'nb_installations']].groupby('annee').sum().reset_index().rename(columns={'annee': 'Année', 'nb_installations': "Nombre d'installations"}),
            x = "Année",
            y = "Nombre d'installations"
        )

        barchart = px.bar(
            data_frame = installations.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')[["gvl", "nb_installations"]].groupby('gvl').sum().sort_values('nb_installations').reset_index().rename(columns={'gvl': 'Commercial', 'nb_installations': "Nombre d'installations"}).tail(10),
            x="Nombre d'installations",
            y="Commercial"
        )

        total = installations.query('seb in @selected_seb and annee.between(@year_min_selected, @year_max_selected)')['nb_installations'].sum()

    return total, linechart, boxplot, barchart, data

if __name__ == '__main__':
    app.run_server(debug=True)

