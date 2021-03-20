import pandas as pd
pd.options.mode.chained_assignment = None
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from functools import lru_cache

app_colors = {
    'blue': '#003f5c',
    'orange': '#ffa600',
    'purple': '#7a5193',
    'pink': '#ef5675',
    'grey50': '#7f7f7f',
    'grey80': '#cccccc'
}


# @lru_cache(maxsize=None)
def _import_path(stem):
    return pd.read_csv(
        f'https://raw.githubusercontent.com/tonyelhabr/xengagement/master/inst/extdata/{stem}.csv'
    )


def import_colors_dicts():
    colors_df = (
        pd.read_csv(
            'https://raw.githubusercontent.com/tonyelhabr/xengagement/master/data-raw/team_mapping.csv'
        ).loc[:, ['team', 'color_pri', 'color_sec']].dropna(axis='rows')
    )
    tms = colors_df['team'].tolist()
    colors_pri = colors_df['color_pri'].tolist()
    colors_sec = colors_df['color_sec'].tolist()
    colors_pri_dict, colors_sec_dict = {}, {}
    for t, c in zip(tms, colors_pri):
        colors_pri_dict[t] = c
    for t, c in zip(tms, colors_sec):
        colors_sec_dict[t] = c
    # colors_pri_dict[''] = 'black'
    # colors_sec_dict[''] = 'black'
    return colors_pri_dict, colors_sec_dict


def import_shap():
    shap = _import_path('shap')
    shap['date'] = pd.to_datetime(shap['created_at']).dt.date
    return shap


# @lru_cache(maxsize=None)
def import_preds():
    preds = _import_path('preds')
    preds.sort_values('created_at', ascending=False, inplace=True)
    preds['date'] = pd.to_datetime(preds['created_at']).dt.date
    preds['total_diff_prnk'] = preds['total_diff_prnk'] * 100
    preds['link'] = (
        # '[\U0001f517](https://twitter.com/xGPhilosophy/status/' +
        '[Link](https://twitter.com/xGPhilosophy/status/' +
        preds['status_id'].astype(str) + ')'
    )
    # preds['lab_hover'] = preds['date'] + '<br/>' + preds['tm_h'] + ' - ' + preds['tm_a']
    return preds


# @lru_cache(maxsize=None)
def import_preds_by_team():
    preds_by_team = _import_path('preds_by_team')
    preds_by_team.sort_values('created_at', ascending=False, inplace=True)
    preds_by_team['date'] = pd.to_datetime(preds_by_team['created_at']).dt.date
    # preds_by_team['total_diff_prnk'] = preds_by_team['total_diff_prnk'] * 100
    return preds_by_team


def get_teams(preds_by_team=None):
    if preds_by_team is None:
        preds_by_team = import_preds_by_team()

    # print(preds_by_team.shape)
    teams = preds_by_team['team'].drop_duplicates().tolist()
    teams.sort()
    return teams

# @lru_cache(maxsize=None)
def get_team_init(preds_by_team=None):
    teams = get_teams(preds_by_team)
    # print(f'team[0] = {teams[0]}')
    return teams[0]


# @lru_cache(maxsize=None)
def get_tweet_init(preds=None):
    if preds is None:
        preds = import_preds()

    created_at_max = preds['created_at'].max()
    return preds['lab_text'].iloc[0]


def generate_about(preds=None):
    if preds is None:
        preds = import_preds()

    preds_sort = preds.sort_values('total_diff_prnk', ascending=False)
    pred_top = preds_sort.iloc[0]

    def _pull(col):
        return pred_top[[col]].astype(str).values[0]

    text_top = _pull('lab_text')
    date_top = _pull('date')
    link_top = _pull('link').replace('[Link]', '')
    about_md = dcc.Markdown(
        f'''
    
    [xGPhilosophy](https://twitter.com/xGPhilosophy) is a Twitter account that provides end-of-match xG summaries of major games across the football world, now focusing solely on the Premier League.

    This app shows the number of favorites (likes) and retweets that every xGPhilosphy end-of-match tweet has received, as well as "expected favorites" (xFavorites) and "expected retweets" (xRetweets) can be compared to the actual number of favorites and retweets to provide an indirect measure of how unexpected a match result is.

    For example, we can use the [__Engagement__ page](/apps/preds) to view the actual and expected engagement for the [Brighton (3.03) 2-3 (1.91) Man United game on 2020-09-26](https://twitter.com/xGPhilosophy/status/1309847833739231233). Below is a timeline of the number of retweets for all xGPhilosophy final match tweets since the beginning of the 2020/21 Premier League sesaon, with the Brighton - Man United game annotated with a black marker. (A similar plot is available for number of favorites.)
    
    ![](/assets/retweet-actuals-over-time-brighton-manu-2020-09-26.png)

    If the xRetweet model were perfect, we would be able to draw a line that would touch every point in a plot of actual and predicted number of retweets. However, since this match received an extraordinary amount of engagement relative to expectation, the marker for this match appears much above the line of perfect accuracy. 

    ![](/assets/retweet-actuals-v-preds-brighton-manu-2020-09-26-annotated.png)

    The number of retweets has exceeded the xRetweets number on several occasions for games involving Brighton in the 2020/21 season. (Toggle the [__Engagement__ page](/apps/preds) to view by team.)

    ![](/assets/retweet-actuals-v-preds-by-team-brighton.png)

    The [__Breakdown__ page](/apps/shap) describes the factors that go into the xFavorite and xRetweet numbers for each tweet using [SHAP values](https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html). A positive SHAP value indicates that a given feature contributed to making the prediction greater than the average prediction across all tweets, and visa versa for a negative SHAP value.

    For the Brighton 2-3 Man United example, we can see that the "xG-Goal Difference" feature (relative difference in xG differential and goal differential) contributed most to the xRetweets number. In other words, the model factors in that "Brighton won the xG" and lost, yet the model still vastly under-estimated how many retweets eventually occurred.

    ![](/assets/retweet-shap-brighton-manu-2020-09-26.png)

    The [__Leaderboard__ page](/apps/leaderboard) lists tweets in order of an "Engagement Over Expected (EOE)" metric that assigns each tweet a percentile based on the predicted and actual number of favorites and retweets, where 100 is the tweet receiving the most engagement compared to expectation.

    ![](/assets/leaderboard-annotated.png)

    If you have any questions, would like to make a suggestion, of just want to tell me how much these models suck, feel free to DM [xGPhilosophy xEngagement](https://twitter.com/punditratio) on Twitter.

    ```
    '''
    )
    return about_md


def generate_leaderboard(preds):
    # preds['total_diff_prnk'] = preds['total_diff_prnk'].map('{:,.1f}%'.format)
    preds_sort = preds.sort_values('total_diff_prnk', ascending=False)
    # preds.sort_values('created_at', ascending=False, inplace=True)
    preds_sort['link'] = (
        # '[\U0001f517](https://twitter.com/xGPhilosophy/status/' +
        '[Link](https://twitter.com/xGPhilosophy/status/' +
        preds_sort['status_id'].astype(str) + ')'
    )
    cols_table = [
        {
            'name': ['', 'Date'],
            'id': 'date',
            'type': 'datetime'
        }, {
            'name': ['Home', 'Team'],
            'id': 'team_h',
            'type': 'text'
        }, {
            'name': ['Home', 'G'],
            'id': 'g_h',
            'type': 'numeric'
        }, {
            'name': ['Home', 'xG'],
            'id': 'xg_h',
            'type': 'numeric'
        }, {
            'name': ['Away', 'Team'],
            'id': 'team_a',
            'type': 'text'
        }, {
            'name': ['Away', 'G'],
            'id': 'g_a',
            'type': 'numeric'
        }, {
            'name': ['Away', 'xG'],
            'id': 'xg_a',
            'type': 'numeric'
        }, {
            'name': ['Favorites', 'Actual'],
            'id': 'favorite_count',
            'type': 'numeric',
            'format': {
                'specifier': ',.0f'
            }
        }, {
            'name': ['Favorites', 'Predicted'],
            'id': 'favorite_pred',
            'type': 'numeric',
            'format': {
                'specifier': ',.0f'
            }
        }, {
            'name': ['Retweets', 'Actual'],
            'id': 'retweet_count',
            'type': 'numeric',
            'format': {
                'specifier': ',.0f'
            }
        }, {
            'name': ['Retweets', 'Predicted'],
            'id': 'retweet_pred',
            'type': 'numeric',
            'format': {
                'specifier': ',.0f'
            }
        }, {
            'name': ['', 'EOE'],
            'id': 'total_diff_prnk',
            'type': 'numeric',
            'format': {
                'specifier': ',.1f'
            }
        }, {
            'name': ['', 'Link'],
            'id': 'link',
            'type': 'text',
            'presentation': 'markdown'
        }
    ]
    return dash_table.DataTable(
        id='leaderboard-table',
        style_header={
            'backgroundColor': 'transparent',
            'fontFamily': 'Karla',
            'fontWeight': 'bold',
            'font-size': '14px',
            'color': '#003f5c',
            # 'border': '1px solid #003f5c',
            'border': '0px transparent',
            # 'textAlign': 'center'
        },
        style_cell={
            # 'backgroundColor': 'transparent',
            'fontFamily': 'Karla',
            'font-size': '14px',
            # 'color': '#ffffff',
            'border': '1px solid #cccccc',
            # 'textAlign': 'center'
        },
        cell_selectable=False,
        column_selectable=False,
        columns=cols_table,
        data=preds_sort.to_dict('records'),
        # style_as_list_view=True,
        # style_cell={
        #     'font-family': 'Karla',
        #     'font-size': '12px',
        #     'padding': '5px'
        # },
        # style_header={
        #     # 'backgroundColor': '#003f5c',
        #     'fontWeight': 'bold',
        # },
        # style_data={
        #     'whiteSpace': 'normal',
        #     'height': 'auto',
        # },
        # style_table={'overflowX': 'auto'},
        filter_action='native',
        sort_action='native',
        # sort_mode='single',
        # column_selectable='single',
        merge_duplicate_headers=True,
        # page_action='native',
        page_current=0,
        page_size=20,
    )
