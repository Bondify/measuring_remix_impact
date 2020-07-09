# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 17:25:08 2020

@author: santi
"""
import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import math

dictionary = {
    'agency_to_community':['1 - Primarily internal','2','3','4','5 - Primarily community-facing'],
    'size_of_impact': ['1- One person', '2','3','4','5 - Whole city/system'],
    'score': [1,2,3,4,5]
    }

score = pd.DataFrame.from_dict(dictionary)

wins = pd.read_csv("https://raw.githubusercontent.com/Bondify/measuring_remix_impact/master/data.csv")

# Keep this out of source code repository - save in a file or a database
VALID_USERNAME_PASSWORD_PAIRS = {
    'example@remix.com': 'janejacobs'
}

app = dash.Dash()
server = app.server

app.title('Remix Impact')

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

wins_scored = pd.merge(wins, 
                       score.loc[:,['agency_to_community', 'score']], 
                       left_on='Agency centric to Community Centric', 
                       right_on='agency_to_community', 
                       how='left').drop('agency_to_community', axis=1)

wins_scored.rename(columns={'score':'score_agency_to_community'}, inplace=True)

wins_scored = pd.merge(wins_scored, 
                       score.loc[:,['size_of_impact', 'score']], 
                       left_on='Size of the impact from Small to Large', 
                       right_on='size_of_impact', 
                       how='left').drop('size_of_impact', axis=1)

wins_scored.rename(columns={'score':'score_size_of_impact'}, inplace=True)

wins_scored = wins_scored.loc[~wins_scored['Win Date'].isnull()]
wins_scored = wins_scored.loc[~wins_scored['score_agency_to_community'].isnull()]
wins_scored = wins_scored.loc[~wins_scored['score_size_of_impact'].isnull()]
wins_scored['year'] = [i[-4:] for i in wins_scored['Win Date']]
wins_scored['size'] = wins_scored.score_agency_to_community * wins_scored.score_size_of_impact
wins_scored['id'] = wins_scored.score_agency_to_community.map(str) + '-' + wins_scored.score_size_of_impact.map(str)

check = wins_scored.pivot_table('Win: Win Name', index=['id'], aggfunc='count').reset_index()
check.columns = ['id', 'count']
check['alpha'] = math.pi*2/(check['count'])

repeated = check.loc[check['count']>1,'id']
df = wins_scored.loc[~wins_scored.id.isin(repeated)]
df_new = wins_scored.loc[wins_scored.id.isin(repeated)]

df_aux = pd.DataFrame()

for i in repeated:
    df_iterate = df_new.loc[df_new.id==i].reset_index()
    alpha = check.loc[check.id==i, 'alpha']
    r = 0.1
    for j in range(0, len(df_iterate)):
        df_iterate.loc[j, 'score_agency_to_community'] = df_iterate.loc[j, 'score_agency_to_community'] + r*math.cos(alpha*(j))
        df_iterate.loc[j, 'score_size_of_impact'] = df_iterate.loc[j, 'score_size_of_impact'] + r*math.sin(alpha*(j))
    
    df_aux = df_aux.append(df_iterate)
    
df = df.append(df_aux)
    
    
df = df.append(df_aux)

dark_blue = "#13264B"
dark_grey = '#787E81'
remix_blue = '#005BAA'

traces = [
    go.Scatter(
        x = df.score_agency_to_community,
        y = df.score_size_of_impact,
        hovertemplate = '<b>%{hovertext}</b><extra></extra>',
        hovertext = df['Win: Win Name'].unique(),
        ids = df['Win: Win Name'].unique(),
        marker = dict(
            color = remix_blue,
            opacity = 0.8,
            size = df['size'],
            sizemode = 'area',
            sizeref = 0.032,
            symbol = 'circle'
        ),
        showlegend = False,
        mode = 'markers',
        customdata = df['Win Description'],
    )
]

annotation_family = "Raleway, sans-serif"
annotation_size = 16
axis_size = 14

shapes = [
    dict(# Center Vertical line
        type="line",
            x0=3,#2.5,
            y0=.75,#-.25,
            x1=3,#2.5,
            y1=5.25,
            line=dict(
                color= 'rgb(0,0,0)',
                width=2
            )
        ),
    dict(# Middle Horizontal Line
            type="line",
            x0=0.75,
            y0=3,#2.5,
            x1=5.25,
            y1=3,#2.5,
            line=dict(
                color = 'rgb(0,0,0)',
                width=2
            )
    ),
    dict(# Lower Horizontal Line
            type="line",
            x0=0.75,
            y0=.75,
            x1=5.25,
            y1=.75,
            line=dict(
                color = 'rgb(0,0,0)',
                width=1
            )
    ),
    dict(# Upper Line Horizontal
            type="line",
            x0=0.75,
            y0=5.25,
            x1=5.25,
            y1=5.25,
            line=dict(
                color = 'rgb(0,0,0)',
                width=1
            )
    ),
    dict(# Left Vertical Line
        type="line",
            x0=.75,#-.25,
            y0=.75,
            x1=.75,#-.25,
            y1=5.25,
            line=dict(
                color= 'rgb(0,0,0)',
                width=1
            )
        ),
    dict(# Right Vertical Line
        type="line",
            x0=5.25,
            y0=.75,
            x1=5.25,
            y1=5.25,
            line=dict(
                color= 'rgb(0,0,0)',
                width=1
            )
        ),
]

#u"\u03A6"
annotations=[
    dict(x=1.25, y=.55, #xref="paper", #yref="paper", 
         text="Agency centric to Community Centric "+ u"\u2192", showarrow=False, 
             font=dict(family=annotation_family,
                       size=annotation_size,
                       color='rgb(135,135,135)')
        ),
    dict(x=0.65, y=1.5, #xref="paper", #yref="paper", 
         text="Low to high impact " + u"\u2192", showarrow=False,
         textangle=270,
             font=dict(family=annotation_family,
                       size=annotation_size,
                       color='rgb(135,135,135)')
        ),
    
        dict(x=1.75,
        y=1.75,
        xref="x",
        yref="y",
        text="Small Impact<br>+<br>Agency Centric",
        showarrow=False,
        font=dict(
                family=annotation_family,
                size=annotation_size,
                color='rgb(135,135,135)') 
            ),
        dict(x=1.75,
        y=4.25,
        xref="x",
        yref="y",
        text="Large Impact<br>+<br>Agency Centric",
        showarrow=False,
        font=dict(
                family=annotation_family,
                size=annotation_size,
                color='rgb(135,135,135)') 
            ),
    dict(x=4.25,
        y=1.75,
        xref="x",
        yref="y",
        text="Small Impact<br>+<br>Community Centric",
        showarrow=False,
        font=dict(
                family=annotation_family,
                size=annotation_size,
                color='rgb(135,135,135)') 
        ),
    dict(x=4.25,
        y=4.25,
        xref="x",
        yref="y",
        text="Large Impact<br>+<br>Community Centric",
        showarrow=False,
        font=dict(
                family=annotation_family,
                size=annotation_size,
                color='rgb(135,135,135)') 
        )
]

layout = go.Layout(annotations = annotations, shapes = shapes,
    showlegend=False, hovermode='closest', template='simple_white', height=650,
    coloraxis_showscale=False, font=dict(family=annotation_family, size=annotation_size,),
    margin = dict(l = 0, b = 10, t=10, r=0)
                  )

fig = go.Figure(data=traces, layout=layout)

fig.update_xaxes(visible=False, range = [0.5,5.5])
fig.update_yaxes(visible=False, range = [0.5,5.5])

app.layout = html.Div(
    [
        html.H1("Measure Remix Impact", 
                style = {"font-family":"Raleway, sans-serif", "color":"#13264B", 'font-size':32, 'marginLeft':35, 'marginTop':35}
                ),
        
        html.P('The plot below highlights Remix wins by the size of their social impact for 2019 and 2020.',
              style = {'line-height': 20, 'font-family': "Raleway, sans-serif", "color":dark_blue, 'font-size':18, 'marginLeft':35},
            ),

       html.Div([
           html.Div([
            dcc.Graph(id="graph", 
                 hoverData={'points': [{'customdata': 'Erie using Remix maps to tell advertisers about their system demographics'}]},
                 config={'displayModeBar': False},
                 style={'marginBottom':10}
                 ),        
            html.Div([
                html.Div(id='account_name', style = {'font-weight': 'bold', 'marginBottom': 10}),
                html.Div(id = 'win_description', style={'line-height': 25})
                ], style={"width": "20%", "float": "right", "font-family":"Raleway, sans-serif",
                       "padding":'50 10 0 10', 'marginTop': 25, 'marginRight':20,'display': 'inline-block',
                       #'marginBottom': 50, 
                       },
            ),
           
           ] ),
    ], style = {'background-image': 'url("/assets/background-image1.png")',
                'background-size': 'cover',
                #'height': '100%',
                'overflow': 'hidden'
                }
)

@app.callback(
        dash.dependencies.Output('graph', 'figure'),
        [dash.dependencies.Input('graph', 'hoverData')]
        )

def show_fig(hover_data):
    return fig

@app.callback(
        dash.dependencies.Output('account_name', 'children'),
        [dash.dependencies.Input('graph', 'hoverData')]
        )

def account_name_div(hover_data):
    description = hover_data['points'][0]['customdata']
    return df.loc[df['Win Description']== description, 'Account Name']

@app.callback(
        dash.dependencies.Output('win_description', 'children'),
        [dash.dependencies.Input('graph', 'hoverData')]
        )

def update_output_div(hover_data):
    description = hover_data['points'][0]['customdata']
    return description #'Win description: "{}"'.format(description)

if __name__ == '__main__':
    app.run_server(debug=False)
