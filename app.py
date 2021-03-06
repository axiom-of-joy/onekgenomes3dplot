import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import numpy as np
import pickle

# Method for loading Python objects.
def load_obj(file):
    with open(file, 'rb') as fid:
        return pickle.load(fid)

# Style sheet.
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Embeddings.
dualAll = np.load("./data/dimReduc/dualPCA/embeddedAll.npy")
dualNum = np.load("./data/dimReduc/dualPCA/embeddedNum.npy")
kernelAll = np.load("./data/dimReduc/kernelPCA/embeddedAll.npy")
kernelNum = np.load("./data/dimReduc/kernelPCA/embeddedNum.npy")


# Sample data.
df = pd.read_csv("./data/cleaned/sampleData.csv", index_col=0)

# Lists and dictionaries.
spops = ['AFR', 'AMR', 'EAS', 'EUR', 'SAS']
spop2descrip = load_obj("./data/cleaned/spop2descrip.pkl")
spop_colors = ['rgb(220,20,60)', 'rgb(30,144,255)', 'rgb(50,205,50)', 'rgb(255,69,0)', 'rgb(139,0,139)']
spop2rgb = dict(zip(spops, spop_colors))

pops = load_obj("./data/cleaned/pops.pkl")
pop2descrip = load_obj("./data/cleaned/pop2descrip.pkl")
pop2rgb = load_obj("./data/cleaned/pop2rgb.pkl")

genders = ['male', 'female']
gender2descrip = dict(zip(genders, ['Male', 'Female']))
gender_colors =  ['rgb(0,191,255)', 'rgb(255,99,71)']
gender2rgb = dict(zip(genders, gender_colors))


app.layout = html.Div([
    html.Div([
        html.Div([
            html.Label('PCA Type'),
            dcc.Dropdown(
                id='pca-type',
                options=[{'label': 'Dual', 'value': 'dual'},
                        {'label': 'Kernel', 'value': 'kernel'}],
                value='dual'
            ),
        ], style={'width': '20%', 'display': 'inline-block', 'padding': '10px 20px 10px 20px', 'text-align': 'left'}),
        html.Div([
            html.Label('Include Sex Chromosomes?'),
            dcc.Dropdown(
                id='include-xy',
                options=[{'label': 'Yes', 'value': 'whole-genome'},
                        {'label': 'No', 'value': 'exclude-xy'}],
                value='whole-genome'
            ),
        ], style={'width': '20%', 'display': 'inline-block', 'padding': '10px 20px 10px 20px', 'text-align': 'left'}),
        html.Div([
            html.Label('Group By'),
            dcc.Dropdown(
                id='group-by',
                options=[{'label': 'Super Population', 'value': 'spop'},
                        {'label': 'Population', 'value': 'pop'},
                        {'label': 'Gender', 'value': 'gender'}],
                value='spop'
            ),
        ], style={'width': '20%', 'display': 'inline-block', 'padding': '10px 20px 10px 20px', 'text-align': 'left'}),
    ], style={'text-align': 'center'}),

    dcc.Graph(id='genome-scatter', style={'height': '800'})


])



@app.callback(
    dash.dependencies.Output('genome-scatter', 'figure'),
    [dash.dependencies.Input('pca-type', 'value'),
     dash.dependencies.Input('include-xy', 'value'),
     dash.dependencies.Input('group-by', 'value')])

def update_graph(pca_type, include_xy, group_by):
    # Do some stuff here.

    if pca_type == 'dual':
        if include_xy == 'whole-genome':
            data = dualAll
        else:
            data = dualNum
    else:
        if include_xy == 'whole-genome':
            data = kernelAll
        else:
            data = kernelNum

    if group_by == 'spop':
        vals = df['Super Population'].values
        groups = spops
        descrip_dict = spop2descrip
        color_dict = spop2rgb
    elif group_by == 'pop':
        vals = df['Population'].values
        groups = pops
        descrip_dict = pop2descrip
        color_dict = pop2rgb
    else:
        vals = df['Gender'].values
        groups = genders
        descrip_dict = gender2descrip
        color_dict = gender2rgb

    traces = list()
    for group in groups:
        ind = vals == group
        groupData = data[ind,:]
        trace = go.Scatter3d(
            x=groupData[:,0],
            y=groupData[:,1],
            z=groupData[:,2],
            mode='markers',
            marker={
                'size': 5,
                'opacity': 0.5,
                'color': color_dict[group]
            },
            name=descrip_dict[group]
        )
        traces.append(trace)

    return {
        'data': traces,
        'layout': go.Layout(
            margin={'l': 0, 'b': 0, 't': 0, 'r': 0},
            legend=dict(x=0, y=1)
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)
