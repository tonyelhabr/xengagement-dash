import pandas as pd
pd.options.mode.chained_assignment = None
import dash_core_components as dcc
import dash_html_components as html
import dash_table
# from functools import lru_cache

app_colors = {
    'blue': '#003f5c',
    'orange': '#ffa600',
    'purple': '#7a5193',
    'pink': '#ef5675',
    'grey50': '#7f7f7f',
    'grey80': '#cccccc'
}


# @lru_cache(maxsize=None)
def import_shap():
    return pd.read_csv(
        'https://raw.githubusercontent.com/tonyelhabr/xengagement-dash/master/data/shap.csv'
    )


# @lru_cache(maxsize=None)
def import_preds():
    preds = pd.read_csv(
        'https://raw.githubusercontent.com/tonyelhabr/xengagement-dash/master/data/preds.csv'
    )
    preds.sort_values('created_at', ascending=False, inplace=True)
    preds['date'] = pd.to_datetime(preds['created_at']).dt.date
    preds['total_diff_prnk'] = preds['total_diff_prnk'] * 100
    preds['link'] = (
        # '[\U0001f517](https://twitter.com/xGPhilosophy/status/' +
        '[Link](https://twitter.com/xGPhilosophy/status/' +
        preds['status_id'].astype(str) + ')'
    )
    return preds


def generate_about(preds=import_preds()):
    preds_sort = preds.sort_values('total_diff_prnk', ascending=False)
    pred_top = preds_sort.iloc[0]

    def _pull(col):
        return pred_top[[col]].astype(str).values[0]

    text_top = _pull('text')
    date_top = _pull('date')
    link_top = _pull('link').replace('[Link]', '')
    about_md = dcc.Markdown(
        f'''
    
    [xGPhilosophy](https://twitter.com/xGPhilosophy) is a Twitter account that provides end-of-match xG summaries of major games across the football world, focusing mostly on the Premier League.

    This app pulls in the number of favorites (likes) and retweets that every xGPhilosphy end-of-match tweet has received. Models have been trained and used to make predictions for these numbers, providing "expected favorites" (xFavorites) and "expected retweets" (xRetweets) that can be viewed on the [__"Data & Predictions"__ page](/apps/data-and-predictions).

    The [__"Prediction Explanation"__ page](/apps/shap) describes the factors that go into the xFavorite and xRetweet numbers for each tweet using [SHAP values](https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html). A positive SHAP value indicates that a given feature (e.g. goals scored by the home team) contributed to making the prediction greater than the average prediction across all tweets, and visa versa for a negative SHAP value.

    The [__"Leaderboard"__ page](/apps/leaderboard) lists tweets in order of an "Engagement Over Expected (EOE)" metric that assigns each tweet a percentile based on the predicted and actual number of favorites and retweets, where 100 is the tweet receiving the most engagement compared to expectation. As of today, the tweet with the top EOE was the recap for [{text_top}]{link_top}.
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
            'id': 'tm_h',
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
            'id': 'tm_a',
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
            # 'backgroundColor': 'transparent',
            'fontFamily': 'Karla',
            'fontWeight': 'bold',
            'font-size': '14px',
            'color': '#003f5c',
            'border': '1px solid #003f5c',
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
        page_size=10,
    )
