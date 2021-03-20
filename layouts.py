import dash_core_components as dcc
import dash_html_components as html
import datetime
from app import app
from utils import *

styles_current_page = {
    'text-align': 'center',
    'text-decoration': 'underline',
    'text-decoration-color': '#ffffff',  # app_colors['blue'],
    'text-shadow': '0px 0px 1px #ffffff'
}


def _graph_wrapper(id):
    return dcc.Graph(
        id=id,
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d']
        }
    )


def get_generic_col_classname():
    return 'col-lg-6 col-md-12 col-sm-12 col-xs-12'


def get_small_col_classname():
    return 'col-lg-3 col-md-12 col-sm-12 col-xs-12'


# def get_navbar_small_col_classname():
#     return 'col-lg-2 col-md-2 col-sm-10 col-xs-10'


def _div_graph_wrapper(id):
    return html.Div(
        [_graph_wrapper(id=id)], className=get_generic_col_classname()
    )


def row_div_graph_wrapper(suffix):
    id1 = 'favorites-' + suffix
    id2 = 'retweets-' + suffix
    return html.Div(
        [
            # html.Div([], className='col-1'),
            _div_graph_wrapper(id1),
            _div_graph_wrapper(id2),
            # html.Div([], className='col-1'),
        ],
        className='row'
    )


preds = import_preds()
leaderboard = generate_leaderboard(preds)
about = generate_about()
created_at_max = preds['created_at'].max()
tweet_init = get_tweet_init(preds)
team_init = get_team_init()
# min_date = preds['date'].min()
# max_date = preds['date'].max()
min_date = datetime.date(2020, 1, 1)
max_date = datetime.date.today()
init_date = datetime.date(2020, 9, 12)

def get_header():

    header = html.Div(
        [
            # html.Div([], className='col-1'),
            html.Div(
                [
                    html.H1(
                        children='xGPhilosophy xEngagement',
                        style={
                            'text-align': 'center',
                            'font-weight': 'bold',
                        }
                    )
                ],
                className='col-12',
                style={'padding-top': '1%'}
            ),
            # html.Div([], className='col-1'),
        ],
        className='row',
        style={
            # 'height': '4%',
            'background-color': app_colors['blue']
        }
    )

    return header


def get_navbar_item(name, link, p):
    is_current = True if link == p else False
    # col-lg-5 col-md-5 col-sm-10 col-xs-10
    if is_current:
        title = html.H4(
            children=name,
            style=styles_current_page
        )
    else:
        title = html.H4(children=name, style={'text-align': 'center'})

    return html.Div([dcc.Link(title, href='/apps/' + link)], className=get_small_col_classname())


def get_navbar(p='about'):
    if p not in ['about', 'preds', 'shap', 'leaderboard']:
        return '404: Error'

    navbar = html.Div(
        [
            # html.Div([], className='col-1'),
            get_navbar_item(name='About', link='about', p=p),
            get_navbar_item(
                name='Engagement', link='preds', p=p
            ),
            get_navbar_item(name='Breakdown', link='shap', p=p),
            get_navbar_item(name='Leaderboard', link='leaderboard', p=p),
        ],
        className='row',
        style={'background-color': app_colors['blue']}
    )
    return navbar


def get_blank_row(h='10px'):

    row = html.Div(
        [html.Div([html.Br()], className='col-12')],
        className='row',
        style={'height': h}
    )

    return row

def get_warning_row(h='20px'):
    row = html.Div(
        [
            # html.Div([], className='col-1'),
            html.Div(
                html.P('Warning: Count of favorites and retweets for tweets made less than 10 minutes ago will likely be much less than final counts.',
                    style={
                        'font-size': 12,
                        'text-align': 'center',
                        'font-style': 'italic'
                    }
                ),
                className='col-12'
            ),
            # html.Div([], className='col-1'),
        ],
        className='row sticky-top',
        style={'height': h, 'background-color': 'white'}
    )

    return row

def get_date_filter():
    res = html.Div(
        [
            html.Div(
                [
                    html.H5(
                        children='Date Range',
                        style={
                            'text-align': 'center',
                            'color': 'black'  # app_colors['blue']
                        }
                    ),
                    html.Div(
                        [
                            dcc.DatePickerRange(
                                id='date-filter',
                                min_date_allowed=min_date,
                                max_date_allowed=max_date,
                                start_date=init_date,
                                end_date=max_date,
                                start_date_placeholder_text='Start date',
                                # display_format='DD-MMM-YYYY',
                                # first_day_of_week=1,
                                end_date_placeholder_text='End date',
                                style={
                                    'font-size': '14px',
                                    'display': 'inline-block',
                                    'border-radius': '2px',
                                    'border': '1px solid #ffffff',
                                    'color': app_colors['blue'],
                                    'border-spacing': '0',
                                    'border-collapse': 'separate'
                                }
                            )
                        ],
                        style={'margin-top': '5px'}
                    )
                ],
                style={
                    'margin-top': '10px',
                    'margin-bottom': '5px',
                    'text-align': 'center',
                    # 'paddingLeft': 15
                }
            )
        ],
        className=get_small_col_classname()
    )
    return res

def get_radio(which='preds'):
    if which == 'preds':
        opts = [
            {'label': 'Tweet', 'value': 'tweet'},
            {'label': 'Team', 'value': 'team'}
        ]
    elif which == 'shap':
        opts = [{'label': 'Tweet', 'value': 'tweet'}]

    res = html.Div(
        [
            html.Div(
                [
                    html.H5(
                        children='Emphasize...',
                        style={
                            'text-align': 'center',
                            'color': 'black' # app_colors['blue']
                        }
                    ),
                    html.Div(
                        [
                            dcc.RadioItems(
                                id='radio',
                                options=opts,
                                inputStyle={'margin-left': '10px', 'margin-right': '10px'},
                                value='tweet'
                            )
                        ],
                        style={'margin-top': '5px'}
                    )
                ],
                style={
                    'margin-top': '10px',
                    'margin-bottom': '5px',
                    'text-align': 'center',
                    # 'paddingLeft': 15
                    # 'padding-left': '15px',
                }
            )
        ],
        className=get_small_col_classname()
    )

    return res

def get_dummy_radio():
    res = html.Div([], className='col-2')
    return res


def get_text_filter():
    res = html.Div(
        [
            html.Div(
                [
                    html.H5(
                        children='Select a Tweet/Team to Emphasize',
                        style={
                            'text-align': 'center',
                            'color': 'black' # app_colors['blue']
                        }
                    ),
                    html.Div(
                        [
                            dcc.Dropdown(
                                id='text-filter',
                                value=tweet_init,
                                # clearable=True,
                                clearable=False,
                                # multi=True,
                                className='dropdown',
                                style={
                                    'font-size': '14px',
                                    # 'display': 'inline-block',
                                    # 'border-radius': '2px',
                                    # 'border': '1px solid #ffffff',
                                    # 'margin-left': '10px',
                                    # 'margin-right': '10px',
                                    'border-spacing': '0',
                                    'border-collapse': 'separate'
                                }
                                # inputStyle={}
                            )
                        ],
                        style={'margin-top': '5px', 'margin-left': '50px', 'margin-right': '50px'}
                    )
                ],
                style={
                    'margin-top': '10px',
                    'margin-bottom': '5px',
                    'text-align': 'left',
                    # 'paddingLeft': 5
                }
            )
        ],
        className=get_generic_col_classname()
    )

    return res

page_about = html.Div(
    [
        get_header(),
        get_navbar('about'),
        html.Div([html.Br()], style={'background-color': 'white'}, className='row sticky-top'),
        html.Div(
            [
                html.Div([], className='col-1'),
                html.Div([about], style={'font-size': 14}, className='col-10'),
                html.Div([], className='col-1'),
            ],
            className='row'
        )
    ]
)


def get_filter_row(which='preds'):
    # extra_filter =  get_radio() if which == 'preds' else get_dummy_radio()
    # extra_filter = get_radio()
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div([], className='col-1'),
                            html.Div(
                                html.P('Warning: Count of favorites and retweets for tweets made less than 10 minutes ago will likely be much less than final counts.',
                                    style={
                                        'font-size': 12,
                                        'text-align': 'center',
                                        'font-style': 'italic'
                                    }
                                ),
                                className='col-10'
                            ),
                            html.Div([], className='col-1'),
                        ],
                        className='row'
                    ),
                ],
                className='col-12'
            ),
            html.Div(
                [
                    html.Div(
                        [
                            # html.Div([], className='col-1'),
                            get_date_filter(),
                            get_radio(which=which),
                            # html.Div([], className='col-1'),
                            get_text_filter(),
                            # html.Div([], className='col-1'),
                        ],
                        className='row'
                    )
                ],
                className='col-12'
            ),
        ],
        style={'background-color': 'white'},
        className='row sticky-top'
    )

page_preds = html.Div(
    [
        get_header(),
        get_navbar('preds'),
        get_blank_row(),
        # get_warning_row(),
        get_filter_row('preds'),
        get_blank_row(),
        row_div_graph_wrapper('over-time'),
        row_div_graph_wrapper('v-pred')
    ]
)

page_shap = html.Div(
    [
        get_header(),
        get_navbar('shap'),
        # html.Div([html.Br()], className='row sticky-top'),
        get_blank_row(),
        get_filter_row('shap'),
        get_blank_row(),
        row_div_graph_wrapper('shap')
    ]
)


page_leaderboard = html.Div(
    [
        get_header(),
        get_navbar('leaderboard'),
        get_blank_row(h='20px'),
        html.Div(
            [
                html.Div([], className='col-1'),
                html.Div([leaderboard], className='col-10'),
                html.Div([], className='col-1'),
            ],
            className='row'
        )
    ]
)
