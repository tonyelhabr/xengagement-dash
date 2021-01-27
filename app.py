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
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None

external_stylesheets = [
    {
        'href':
            'https://fonts.googleapis.com/css2?'
            'family=Karla:wght@400;700&display=swap',
        'rel': 'stylesheet',
    }, dbc.themes.BOOTSTRAP
]
# from jupyter_dash import JupyterDash
shap = pd.read_csv('shap.csv')
preds = pd.read_csv('preds.csv')
preds.sort_values('created_at', ascending=False, inplace=True)
preds['date'] = pd.to_datetime(preds['created_at']).dt.date

created_at_max = preds['created_at'].max()
# initial_text = (
#     preds.loc[preds['created_at'] == created_at_max, :]['text'].to_string()
# )
initial_text = preds['text'].iloc[0]
COLORS = {
    'blue': '#003f5c',
    'orange': '#ffa600',
    'purple': '#7a5193',
    'pink': '#ef5675',
    'grey50': '#7f7f7f',
    'grey80': '#cccccc'
}

# min_date = preds['date'].min()
# max_date = preds['date'].max()
min_date = datetime.date(2020, 1, 1)
max_date = datetime.date.today()
init_date = datetime.date(2020, 6, 1)

about_md = dcc.Markdown(
    '''
[xGPhilosophy](https://twitter.com/xGPhilosophy) is a Twitter account that provides end-of-match xG summaries of major games across the football world, focusing mostly on the Premier League. For example, [see the recap tweet for the Liverpool vs. Man United 0-0 draw on Jan. 17, 2021](https://twitter.com/xGPhilosophy/status/1350871119784538114). The account started to make regular tweets around the beginning of 2020, and really picked up lots of attention in the summer of 2020.

>
> Block quotes are used to highlight text.
>

This app pulls in the actual number of favorites (likes) and retweets that every xGPhilosphy end-of-match tweet has received. Models have been trained and used to make predictions for these numbers, providing "expected favorites" and "expected predictions". The data and predictions are plotted in the __"Data & Predictions"__ tab (duh).

Taking the difference between the actual counts and the models' predictions gives us an "over/under expected" number quantifying how unexpected a given tweet's amount of engagement is. For example, a tweet that is predicted to receive 100 favorites and 10 retweets, but actually receives 200 favorites and 30 retweets tells us that the tweet received more attention than one might expect. This may tell us that the game was particularly interesting, perhaps due to something like a controversial, late-game VAR decision. For football fans, this is not so unlike comparing a strikers goals scored with their xG---a goals scored number greater than xG can be a sign of skill (or luck), telling us something about the nature of the player.

For those interested in why a prediction is a certain number, the __"Prediction Explanation"__ tab is your friend. A positive [SHAP](https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html) value indicates that a given feature (e.g. goals scored by the home team) contributed to making the prediction greater than the average prediction across all tweets, and visa versa for a negative SHAP value.

The __"Leaderboard"__ tab lists tweets in order of an "Engagement Over Expected" metric that scores tweets based on the predicted and actual number of favorites and retweets. Unfortunately, it's not a simple as

_Engagement over Expected = (Actual Favorites - Predicted Favorites) + (Actual Retweets - Predicted Retweets)_

for two reasons.

1. We must account for the fact that the xGPhilosophy account has gained lots of followers over time. If we did not account for this, then more recent tweets would always show up among the top.

2. Tweets tend to get a lot more favorites than retweets, so taking the sum of the two to quantify engagement would be over-weighting favorites.

Nonetheless, despite the above formula being flawed, it should provide a solid heuristic for the rankings generated by the actual methodology (not explained here).
```
'''
)


def _graph_wrapper(id):
    return dcc.Graph(
        id=id,
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d']
        }
    )


def col_graph_wrapper(id):
    return dbc.Col([_graph_wrapper(id)], width=12, lg=6)


# if local:
#     app = JupyterDash(__name__, external_stylesheets=external_stylesheets)
# else:
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#     server = app.server  # prod
app.title = 'xGPhilosophy\'s xEngagement'

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
                            # style={'background': COLORS['blue']},
                            min_date_allowed=min_date,
                            max_date_allowed=max_date,
                            start_date=init_date,
                            end_date=max_date
                        ),
                    ],
                    width=12,
                    lg=4
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
                    width=12,
                    lg=8
                )
            ]
        ),
        html.Hr(),
        dbc.Tabs(
            # id='tabs',
            # active_tab='data-and-preds',
            [
                dbc.Tab(
                    label='About',
                    tab_id='about',
                    # children=[html.Div(about_md)]
                    children=[html.Div(about_md)]
                ),
                dbc.Tab(
                    label='Data & Predictions',
                    tab_id='data-and-preds',
                    children=[
                        dbc.Row(
                            [
                                col_graph_wrapper('favorites-over-time'),
                                col_graph_wrapper('retweets-over-time'),
                            ]
                        ),
                        dbc.Row(
                            [
                                col_graph_wrapper('favorites-v-pred'),
                                col_graph_wrapper('retweets-v-pred'),
                            ]
                        )
                    ]
                ),
                dbc.Tab(
                    label='Prediction Explanation',
                    tab_id='shap',
                    children=[
                        dbc.Row(
                            [
                                col_graph_wrapper('favorites-shap'),
                                col_graph_wrapper('retweets-shap'),
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# @app.callback(
#     Output('tab-content', 'children'),
#     [Input('tabs', 'active_tab')],
# )
# def render_tab_content(active_tab):
#     if active_tab == 'data-and-preds':
#         res = [
#             dbc.Row(
#                 [
#                     col_graph_wrapper('favorites-over-time'),
#                     col_graph_wrapper('retweets-over-time'),
#                 ]
#             ),
#             dbc.Row(
#                 [
#                     col_graph_wrapper('favorites-v-pred'),
#                     col_graph_wrapper('retweets-v-pred'),
#                 ]
#             )
#         ]
#     elif active_tab == 'shap':
#         res = dbc.Row(
#             [
#                 col_graph_wrapper('favorites-shap'),
#                 col_graph_wrapper('retweets-shap'),
#             ]
#         )
#     else:
#         res = 'No tab selected.'
#     return res


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
    return COLORS['orange'] if stem == 'retweet' else COLORS['blue']


def _update_common_layout_settings(fig, width=512, height=400):
    fig.update_layout(
        {
            'showlegend': False,
            'hoverlabel_align': 'right',
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'autosize': True,
            'width': width,
            'height': height,
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


def _update_common_xaxes_settings(fig, *args, **kwargs):
    return fig.update_xaxes(
        showgrid=True, gridwidth=1, gridcolor=COLORS['grey80'], *args, **kwargs
    )


def _update_common_yaxes_settings(fig, *args, **kwargs):
    return fig.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor=COLORS['grey80'], *args, **kwargs
    )


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
            # text=df['text'],
            text=df['lab_hover'],
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
    fig = _update_common_xaxes_settings(fig)
    fig = _update_common_yaxes_settings(fig, rangemode='tozero')
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
    lab_y = f'Actual: '
    lab_x = f'Predicted: '
    title_text = f'Actual vs. Predicted {lab_stem}'
    hovertemplate = '%{text}<br>' + lab_y + ': %{y:0,000}</br>' + lab_x + ': %{x:,.0f}<br></br><extra></extra>'
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


def _identify_sign_color(sign):
    if sign == 'neg':
        color = COLORS['purple']
    elif sign == 'pos':
        color = COLORS['pink']
    else:
        color = COLORS['grey50']
    return color


def _plot_shap(df, stem, text):
    selected = (df['text'] == text)
    df_selected = df.loc[selected, :]
    # print(len(df_selected))

    if len(df_selected) == 0:
        return None

    col_y = 'lab'
    col_x = f'{stem}_shap_value'
    lab_stem = _convert_stem_to_lab(stem)
    # bar_colors = _identify_sign_color(df['sign'])
    hovertemplate = '%{y}<br>SHAP value: %{x:.2f}</br><extra></extra>'
    lab_y = f'# of {lab_stem}'
    title_text = f'{lab_stem} SHAP values'

    def _plot_bar(fig, sign):

        df_sign = df_selected.loc[df_selected[f'{stem}_sign'] == sign, :]
        if sign == 'pos':
            df_sign.sort_values(col_x, inplace=True, ascending=True)
        elif sign == 'neg':
            df_sign.sort_values(col_x, inplace=True, ascending=True)
        c = _identify_sign_color(sign)
        fig.add_trace(
            go.Bar(
                x=df_sign[col_x],
                y=df_sign[col_y],
                orientation='h',
                marker_color=c,
                hovertemplate=hovertemplate
            )
        )
        return fig

    fig = go.Figure()
    fig = _plot_bar(fig, 'neg')
    fig = _plot_bar(fig, 'pos')

    fig = _update_common_layout_settings(fig, height=700)
    fig.update_layout(
        {
            'title_text': title_text,
            # 'xaxis_text': 'SHAP value',
            'xaxis_tickformat': ',.',
        }
    )
    fig = _update_common_xaxes_settings(fig)
    # fig = _update_common_yaxes_settings(fig)
    fig.update_yaxes(showgrid=False)
    return fig


@app.callback(
    [
        Output('favorites-over-time', 'figure'),
        Output('retweets-over-time', 'figure'),
        Output('favorites-v-pred', 'figure'),
        Output('retweets-v-pred', 'figure'),
        Output('favorites-shap', 'figure'),
        Output('retweets-shap', 'figure')
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
    favorites_shap = _plot_shap(shap, 'favorite', text)
    retweets_shap = _plot_shap(shap, 'retweet', text)
    return favorites_over_time, retweets_over_time, favorites_v_pred, retweets_v_pred, favorites_shap, retweets_shap


app.run_server(debug=True, port=8050)
