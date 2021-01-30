import dash_bootstrap_components as dbc
import dash_core_components as dcc


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
    return dbc.Col([_graph_wrapper(id)], width=12, md=6)