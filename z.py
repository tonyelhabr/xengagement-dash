#%%
import dash
import dash_table
import pandas as pd

df = pd.read_csv('preds.csv')
df.sort_values('created_at', ascending=False, inplace=True)
df['date'] = pd.to_datetime(df['created_at']).dt.date
df['total_diff_prnk'] = df['total_diff_prnk'] * 100
df['total_diff_prnk'] = df['total_diff_prnk'].map('{:,.1f}%'.format)
df.sort_values('total_diff_prnk', ascending=False, inplace=True)
#%%
app = dash.Dash(__name__)

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
        'name': ['Home', 'Goals'],
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
        'name': ['Away', 'Goals'],
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
        'name': ['', 'EOE Percentile'],
        'id': 'total_diff_prnk',
        'type': 'numeric',
        'format': {
            'specifier': ',.1f'
        }
    }
]

app.layout = dash_table.DataTable(
    id='table',
    columns=cols_table,
    data=df.to_dict('records'),
    style_as_list_view=True,
    style_cell={'padding': '5px'},
    # style_header={
    #     'backgroundColor': 'white',
    #     'fontWeight': 'bold'
    # },
    filter_action='native',
    sort_action='native',
    sort_mode='multi',
    column_selectable='single',
    merge_duplicate_headers=True,
    page_action='native',
    page_current=0,
    page_size=20,
)

if __name__ == '__main__':
    app.run_server(debug=True)
# %%
