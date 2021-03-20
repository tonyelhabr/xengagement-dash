import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from app import server

from layouts import page_about, page_preds, page_shap, page_leaderboard
import callbacks

app.layout = html.Div(
    [dcc.Location(id='url', refresh=False),
     html.Div(id='page-content')]
)
# app.title = 'xEngagement'

@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    [dash.dependencies.Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/apps/about':
        return page_about
    elif pathname == '/apps/preds':
        return page_preds
    elif pathname == '/apps/shap':
        return page_shap
    elif pathname == '/apps/leaderboard':
        return page_leaderboard
    else:
        return page_about


if __name__ == '__main__':
    app.title = 'xEngagement'
    app.run_server(debug=False)
