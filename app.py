# local = True
# from jupyter_dash import JupyterDash # only for local dev
import datetime
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Output, Input
import pandas as pd
import numpy as np
external_stylesheets = [
    {
        'href':
            'https://fonts.googleapis.com/css2?'
            'family=Karla:wght@400;700&display=swap',
        'rel': 'stylesheet',
    }, dbc.themes.BOOTSTRAP
]
# from jupyter_dash import JupyterDash

preds = pd.read_csv('preds.csv')
preds.sort_values('created_at', ascending=False, inplace=True)
preds['date'] = pd.to_datetime(preds['created_at']).dt.date

created_at_max = preds['created_at'].max()
# initial_text = (
#     preds.loc[preds['created_at'] == created_at_max, :]['text'].to_string()
# )
# print(str(initial_text))
# print(preds['text'][0])
# print(preds['text'].iloc[0])
initial_text = preds['text'].iloc[0]
BLUE = '#003f5c'
ORANGE = '#ffa600'

# min_date = preds['date'].min()
# max_date = preds['date'].max()
min_date = datetime.date(2020, 1, 1)
max_date = datetime.date.today()
init_date = datetime.date(2020, 6, 1)


def graph_wrapper(id):
    return dcc.Graph(
        id=id,
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d']
        }
    )


# if local:
#     app = JupyterDash(__name__, external_stylesheets=external_stylesheets)
# else:
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#     server = app.server  # prod
app.title = 'xGPhilosophy\'s Expected Twitter Engagement (xEngagement)'

app.layout = dbc.Container(
    fluid=False,
    style={'margin': 'auto'},
    children=[
        html.Div(
            html.H3(
                children='xGPhilosophy\'s Expected Engagment (xEngagement)',
                className='header-title'
            ),
            className='header'
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(children='Date Range', className='menu-title'),
                        dcc.DatePickerRange(
                            id='date-filter',
                            # style={'background': BLUE},
                            min_date_allowed=min_date,
                            max_date_allowed=max_date,
                            start_date=init_date,
                            end_date=max_date
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.Div(children='Tweets', className='menu-title'),
                        dcc.Dropdown(
                            id='text-filter',
                            value=initial_text,
                            clearable=True,
                            className='dropdown',
                        ),
                    ],
                    md=6
                )
            ]
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id='favorites-over-time',
                            config={
                                'displayModeBar': True,
                                'displaylogo': False,
                                'modeBarButtonsToRemove': ['pan2d', 'lasso2d']
                            }
                        )
                    ],
                    md=6
                ),
                dbc.Col([graph_wrapper('retweets-over-time')], md=6),
            ]
        ),
        dbc.Row(
            [
                dbc.Col([graph_wrapper('favorites-v-pred')], md=6),
                dbc.Col([graph_wrapper('retweets-v-pred')], md=6),
            ]
        ),
    ],
)


def _convert_to_date(x):
    return datetime.datetime.strptime(x, '%Y-%m-%d').date()


def _filter_date_between(df, d1, d2):
    d1 = _convert_to_date(d1)
    d2 = _convert_to_date(d2)
    res = df.loc[(df['date'] >= d1) & (df['date'] <= d2), :]
    return res


@app.callback(
    Output('text-filter', 'options'),
    [Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date')]
)
def update_text_dropdown(start_date, end_date):
    preds_filt = _filter_date_between(preds, start_date, end_date)
    # preds_filt = preds.loc[selected, :]
    # preds_filt = preds
    opts = [{'label': x, 'value': x} for x in preds_filt['text']]
    return opts


def _split_df_by_text(df, text):
    selected = (df['text'] == text)
    other = (df['text'] != text)
    df_selected = df.loc[selected, :]
    df_other = df.loc[other, :]
    return df_selected, df_other


def _convert_stem_to_lab(stem):
    return f'{stem.capitalize()}s'


def _identify_stem_color(stem):
    return ORANGE if stem == 'retweet' else BLUE


def _update_common_layout_settings(fig):
    fig.update_layout(
        {
            'showlegend': False,
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'autosize': True,
            'width': 450,
            'height': 300,
            'margin': {
                # 'l': 10,
                # 'r': 10,
                # 'b': 50,
                # 't': 50,
                'pad': 0
            },
            # 'clickmode': 'event+select',
            'font_family': 'Karla',
        }
    )
    return fig


def _plot_actual(df, stem, text, col_x, title_text, hovertemplate):
    df_selected, df_other = _split_df_by_text(df, text)
    col_y = f'{stem}_count'
    lab_stem = _convert_stem_to_lab(stem)
    lab_y = f'# of {lab_stem}'
    marker_color = _identify_stem_color(stem)

    def _plot(df, which='other'):
        o = 0.5 if which == 'other' else 1
        c = marker_color if which == 'other' else 'black'
        s = 5 if which == 'other' else 10
        return go.Scatter(
            x=df[col_x],
            y=df[col_y],
            mode='markers',
            text=df['text'],
            opacity=o,
            hovertemplate=hovertemplate,
            marker={
                'size': s,
                'color': c
            }
        )

    fig = go.Figure(_plot(df_other, 'other'))
    fig.add_trace(_plot(df_selected, 'selected'))

    fig = _update_common_layout_settings(fig)
    fig.update_layout({
        'title_text': title_text,
        'yaxis_tickformat': ',.',
    })
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#cccccc')
    fig.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor='#cccccc', rangemode='tozero'
    )
    return fig


def _plot_over_time(df, stem, text):
    col_x = 'created_at'
    lab_stem = _convert_stem_to_lab(stem)
    lab_y = f'# of {lab_stem}'
    title_text = f'{lab_stem} over Time'
    hovertemplate = '%{text}<br>' + lab_y + ': %{y:0,000}</br><extra></extra>'
    fig = _plot_actual(
        df,
        stem,
        text,
        col_x=col_x,
        title_text=title_text,
        hovertemplate=hovertemplate
    )
    return fig


def _plot_v_pred(df, stem, text):
    col_x = f'{stem}_pred'
    lab_stem = _convert_stem_to_lab(stem)
    lab_y = f'Actual # of {lab_stem}'
    lab_x = f'Predicted # of {lab_stem}'
    title_text = f'Actual vs. Predicted {lab_stem}'
    hovertemplate = '%{text}<br>' + lab_y + ': %{y:0,000}</br>' + lab_x + ': %{x:0,000}<br></br><extra></extra>'
    fig = _plot_actual(
        df,
        stem,
        text,
        col_x=col_x,
        title_text=title_text,
        hovertemplate=hovertemplate
    )
    fig.update_layout({
        'xaxis_tickformat': ',.',
    })
    return fig


@app.callback(
    [
        Output('favorites-over-time', 'figure'),
        Output('retweets-over-time', 'figure'),
        Output('favorites-v-pred', 'figure'),
        Output('retweets-v-pred', 'figure')
    ],
    [
        Input('date-filter', 'start_date'),
        Input('date-filter', 'end_date'),
        Input('text-filter', 'value')
    ],
)
def update_charts(start_date, end_date, text):
    preds_filt = _filter_date_between(preds, start_date, end_date)
    favorites_over_time = _plot_over_time(preds_filt, 'favorite', text)
    retweets_over_time = _plot_over_time(preds_filt, 'retweet', text)
    favorites_v_pred = _plot_v_pred(preds_filt, 'favorite', text)
    retweets_v_pred = _plot_v_pred(preds_filt, 'retweet', text)
    return favorites_over_time, retweets_over_time, favorites_v_pred, retweets_v_pred


app.run_server(debug=True, port=8050)
