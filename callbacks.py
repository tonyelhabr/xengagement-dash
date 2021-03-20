import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
import plotly.graph_objs as go
import pandas as pd
pd.options.mode.chained_assignment = None
# import dash
import datetime
from app import app
from utils import *

shap = import_shap()
preds = import_preds()
preds_by_team = import_preds_by_team()
teams = get_teams(preds_by_team)
colors_pri_dict, colors_sec_dict = import_colors_dicts()


def _convert_to_date(x):
    return datetime.datetime.strptime(x, '%Y-%m-%d').date()


def _filter_date_between(df, d1, d2):
    d1 = _convert_to_date(d1)
    d2 = _convert_to_date(d2)
    res = df.loc[(df['date'] >= d1) & (df['date'] <= d2), :]
    return res


def decipher_radio_value(option, text):
    # team = ''
    # print('here')
    # print(f'option = {option}')
    # print(f'text = {text}')
    if option == 'tweet':
        if text is None:
            text = get_tweet_init(preds)
        df, tweet, team = preds, text, None
    elif option == 'team':
        # For some reason I get erros here if it is switched from tweet to team
        if text is None: #  or text not in teams:
            text = get_team_init(preds_by_team)
            # text = 'Brighton'
        # print(f'team = {text}')
        df, tweet, team = preds_by_team, None, text
    return df, tweet, team


@app.callback(
    Output('text-filter', 'value'), [
        Input('radio', 'value')
    ]
)
def update_dropdown(option):
    if option == 'tweet':
        res = get_tweet_init()
    elif option == 'team':
        res = get_team_init()
    return res


@app.callback(
    Output('text-filter', 'options'), [
        Input('date-filter', 'start_date'),
        Input('date-filter', 'end_date'),
        Input('radio', 'value')
    ]
)
def update_dropdown(start_date, end_date, option):
    if option == 'tweet':
        preds_filt = _filter_date_between(preds, start_date, end_date)
        l = preds_filt['lab_text']
    elif option == 'team':
        preds_by_team_filt = _filter_date_between(
            preds_by_team, start_date, end_date
        )
        l = preds_by_team_filt['team'].drop_duplicates().tolist()
        l.sort()

    opts = [{'label': x, 'value': x} for x in l]
    return opts


def _split_df_by(df, col, value):
    selected = (df[col] == value)
    other = (df[col] != value)
    df_selected = df.loc[selected, :]
    df_other = df.loc[other, :]
    return df_selected, df_other


def _convert_stem_to_lab(stem):
    return f'{stem.capitalize()}s'


def _identify_stem_color(stem):
    return app_colors['orange'] if stem == 'retweet' else app_colors['blue']


def _update_common_layout_settings(fig, width=None, height=None):
    fig.update_layout(
    # fig.layout.update(
        {
            'showlegend': False,
            'hoverlabel_align': 'right',
            'plot_bgcolor': '#ffffff',
            'autosize': True,
            # 'width': width,
            # 'height': height,
            'margin': {
                'pad': 0
            },
            # 'clickmode': 'event+select',
            'font_family': 'Karla',
        }
    )
    if width is not None:
        fig.update_layout({'width': width})
    if height is not None:
        fig.update_layout({'height': height})
    return fig


def _update_common_xaxes_settings(fig, *args, **kwargs):
    return fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor=app_colors['grey80'],
        *args,
        **kwargs
    )


def _update_common_yaxes_settings(fig, *args, **kwargs):
    return fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor=app_colors['grey80'],
        *args,
        **kwargs
    )


def _plot_actual(
    df,
    stem,
    tweet=None,
    team=None,
    col_x='date',
    title_text='title',
    hovertemplate='%{text}<extra></extra>'
):
    has_tweet = True if tweet is not None else False
    has_team = True if team is not None else False
    if(stem == 'favorite'):
        print(f'tweet = {tweet}, has_tweet = {has_tweet}')
        print(f'team = {team}, has_team = {has_team}')
    if (not has_tweet and not has_team) or (has_tweet and has_team):
        print('in hell')
        return go.Figure(go.Scatter())
    if has_tweet:
        # df_selected, df_other = _split_df_by_tweet(df, tweet=tweet)
        df_selected, df_other = _split_df_by(df, col='lab_text', value=tweet)
    else:
        df_selected, df_other = _split_df_by(df, col='team', value=team)

    col_y = f'{stem}_count'
    lab_stem = _convert_stem_to_lab(stem)
    lab_y = f'# of {lab_stem}'
    marker_color = _identify_stem_color(stem)

    def _plot(df, which='other'):
        o = 0.5 if which == 'other' else 1
        if has_tweet:
            c1, c2 = 'black', 'black'
        else:
            c1, c2 = colors_pri_dict[team], colors_sec_dict[team]
        c1 = marker_color if which == 'other' else c1
        c2 = marker_color if which == 'other' else c2
        s = 5 if which == 'other' else 10
        return go.Scatter(
            x=df[col_x],
            y=df[col_y],
            mode='markers',
            # text=df['lab_text'],
            text=df['lab_text'],
            opacity=o,
            hovertemplate=hovertemplate,
            marker={
                'size': s,
                'color': c1,
                'line': {
                    'width': 2,
                    'color': c2
                }
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


def _plot_over_time(df, stem, tweet=None, team=None):
    col_x = 'created_at'
    lab_stem = _convert_stem_to_lab(stem)
    lab_y = f'# of {lab_stem}'
    title_text = f'{lab_stem} over Time'
    hovertemplate = '%{text}<br>' + lab_y + ': %{y:0,000}</br><extra></extra>'
    fig = _plot_actual(
        df=df,
        stem=stem,
        tweet=tweet,
        team=team,
        col_x=col_x,
        title_text=title_text,
        hovertemplate=hovertemplate
    )
    return fig


def _plot_v_pred(df, stem, tweet=None, team=None):
    col_x = f'{stem}_pred'
    lab_stem = _convert_stem_to_lab(stem)
    lab_y = f'Actual'
    lab_x = f'Predicted'
    title_text = f'Actual vs. Predicted {lab_stem}'
    hovertemplate = '%{text}<br>' + lab_y + ': %{y:0,000}</br>' + lab_x + ': %{x:,.0f}<br></br><extra></extra>'
    fig = _plot_actual(
        df=df,
        stem=stem,
        tweet=tweet,
        team=team,
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
        color = app_colors['purple']
    elif sign == 'pos':
        color = app_colors['pink']
    else:
        color = app_colors['grey50']
    return color


def _plot_shap(df, stem, tweet):
    if tweet in teams:
        print('had to re-initialize tweet')
        tweet = get_tweet_init()

    # print(f'tweet = {tweet}')
    selected = (df['lab_text'] == tweet)
    df_selected = df.loc[selected, :]
    print(df_selected.shape)
    if len(df_selected) == 0:
        return {}

    col_y = 'lab'
    col_x = f'{stem}_shap_value'
    lab_stem = _convert_stem_to_lab(stem)
    # bar_app_colors = _identify_sign_color(df['sign'])
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
    fig.update_xaxes(tickformat='.1f')
    fig.update_yaxes(showgrid=False, type='category')
    return fig

# idk why having all callbacks toegether use to work, but now it doesn't
@app.callback(
    [
        Output('favorites-over-time', 'figure'),
        Output('retweets-over-time', 'figure')
    ],
    [
        Input('date-filter', 'start_date'),
        Input('date-filter', 'end_date'),
        Input('text-filter', 'value')
    ], [
        State('radio', 'value')
    ]
)
def update_over_time_plots(start_date, end_date, text, option):
    df, tweet, team = decipher_radio_value(option, text)
    df_filt = _filter_date_between(df, start_date, end_date)
    favorites_over_time = _plot_over_time(
        df_filt, stem='favorite', tweet=tweet, team=team
    )
    retweets_over_time = _plot_over_time(
        df_filt, stem='retweet', tweet=tweet, team=team
    )
    return favorites_over_time, retweets_over_time


@app.callback(
    [Output('favorites-v-pred', 'figure'),
     Output('retweets-v-pred', 'figure')], [
         Input('date-filter', 'start_date'),
         Input('date-filter', 'end_date'),
         Input('text-filter', 'value')
     ], [
         State('radio', 'value'),
     ]
)
def update_v_pred_plots(start_date, end_date, text, option):
    df, tweet, team = decipher_radio_value(option, text)
    df_filt = _filter_date_between(df, start_date, end_date)
    favorites_v_pred = _plot_v_pred(
        df_filt, stem='favorite', tweet=tweet, team=team
    )
    retweets_v_pred = _plot_v_pred(
        df_filt, stem='retweet', tweet=tweet, team=team
    )
    return favorites_v_pred, retweets_v_pred


@app.callback(
    [
        Output('favorites-shap', 'figure'),
        Output('retweets-shap', 'figure') # ,
        # Output('radio', 'value')
     ],
    [
        Input('date-filter', 'start_date'),
        Input('date-filter', 'end_date'),
        Input('text-filter', 'value')
    ],
)
def update_shap_plots(start_date, end_date, text):
    # print(shap.shape)
    shap_filt = _filter_date_between(shap, start_date, end_date)
    # print(shap_filt.shape)
    favorites_shap = _plot_shap(shap_filt, stem='favorite', tweet=text)
    retweets_shap = _plot_shap(shap_filt, stem='retweet', tweet=text)
    return favorites_shap, retweets_shap # , 'tweet'
