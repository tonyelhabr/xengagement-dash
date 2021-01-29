import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html


def generate_about_tab():
    about_md = dcc.Markdown(
        '''
    
    [xGPhilosophy](https://twitter.com/xGPhilosophy) is a Twitter account that provides end-of-match xG summaries of major games across the football world, focusing mostly on the Premier League.

    This app pulls in the number of favorites (likes) and retweets that every xGPhilosphy end-of-match tweet has received. Models have been trained and used to make predictions for these numbers, providing "expected favorites" (xFavorites) and "expected retweets" (xRetweets) that can be viewed on the __"Data & Predictions"__ tab.

    The __"Prediction Explanation"__ tab describes the factors that go into the xFavorite and xRetweet numbers for each tweet using [SHAP values](https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html). A positive SHAP value indicates that a given feature (e.g. goals scored by the home team) contributed to making the prediction greater than the average prediction across all tweets, and visa versa for a negative SHAP value.

    The __"Leaderboard"__ tab lists tweets in order of an "Engagement Over Expected (EOE)" metric that assigns each tweet a percentile (100 being the most over-achieving in engagement compared to expectation) based on the predicted and actual number of favorites and retweets. As of Jan. 26, 2021, the twee with the top EOE was [the recap for the 2-3 Brighton loss to Man United on Sep. 20, 2020](https://twitter.com/xGPhilosophy/status/1309847833739231233).
    ```
    '''
    )

    return dbc.Tab(
        label='About',
        tab_id='about',
        # children=[html.Div(about_md)]
        children=[html.Div(about_md)]
    )