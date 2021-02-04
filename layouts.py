import dash_core_components as dcc
import dash_html_components as html
import datetime
from app import app
from utils import *

# formatting
styles_current_page = {
    'text-decoration': 'underline',
    'text-decoration-color': '#ffffff',  # app_colors['blue'],
    'text-shadow': '0px 0px 1px #ffffff'
}

preds = import_preds()
leaderboard = generate_leaderboard(preds)
about = generate_about()
created_at_max = preds['created_at'].max()
initial_text = preds['text'].iloc[0]
# min_date = preds['date'].min()
# max_date = preds['date'].max()
min_date = datetime.date(2020, 1, 1)
max_date = datetime.date.today()
init_date = datetime.date(2020, 6, 1)


def get_header():

    header = html.Div(
        [
            html.Div([], className='col-1'),
            html.Div(
                [
                    html.H1(
                        children='xGPhilosophy xEngagement',
                        style={
                            'textAlign': 'left',
                            'font-weight': 'bold',
                        }
                    )
                ],
                className='col-10',
                style={'padding-top': '1%'}
            ),
            html.Div([], className='col-1'),
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
    if is_current:
        title = html.H4(children=name, style=styles_current_page)
    else:
        title = html.H4(children=name)

    return html.Div([dcc.Link(title, href='/apps/' + link)], className='col-2')


def get_navbar(p='about'):
    if p not in ['about', 'data-and-preds', 'shap', 'leaderboard']:
        return '404: Error'

    navbar = html.Div(
        [
            html.Div([], className='col-1'),
            get_navbar_item(name='About', link='about', p=p),
            get_navbar_item(
                name='Data & Predictions', link='data-and-preds', p=p
            ),
            get_navbar_item(name='Prediction Explanation', link='shap', p=p),
            get_navbar_item(name='Leaderboard', link='leaderboard', p=p),
        ],
        className='row',
        style={'background-color': app_colors['blue']}
    )
    return navbar


def get_blank_row(h='45px'):

    row = html.Div(
        [html.Div([html.Br()], className='col-12')],
        className='row',
        style={'height': h}
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
                            'text-align': 'left',
                            'color': app_colors['blue']
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
                                    'font-size': '12px',
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
                    'text-align': 'left',
                    'paddingLeft': 5
                }
            )
        ],
        className=get_generic_col_classname()
    )
    return res


def get_text_filter():
    res = html.Div(
        [
            html.Div(
                [
                    html.H5(
                        children='Select a Tweet to Emphasize',
                        style={
                            'text-align': 'left',
                            'color': app_colors['blue']
                        }
                    ),
                    html.Div(
                        [
                            dcc.Dropdown(
                                id='text-filter',
                                value=initial_text,
                                clearable=True,
                                className='dropdown',
                                style={
                                    'font-size': '12px',
                                    # 'display': 'inline-block',
                                    # 'border-radius': '2px',
                                    # 'border': '1px solid #ffffff',
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
                    'text-align': 'left',
                    'paddingLeft': 5
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
        html.Div([html.Br()], className='row sticky-top'),
        html.Div(
            [
                html.Div([], className='col-1'),
                html.Div([about], className='col-10'),
                html.Div([], className='col-1'),
            ],
            className='row'
        )
    ]
)


def get_filter_row():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div([], className='col-1'),
                            get_date_filter(),
                            get_text_filter(),
                            html.Div([], className='col-1'),
                        ],
                        className='row'
                    )
                ],
                className='col-12'
            ),
        ],
        className='row sticky-top'
    )


page_data_and_preds = html.Div(
    [
        get_header(),
        get_navbar('data-and-preds'),
        # get_blank_row(h='45px'),
        get_filter_row(),
        get_blank_row(h='10px'),
        row_div_graph_wrapper('over-time'),
        row_div_graph_wrapper('v-pred')
    ]
)

page_shap = html.Div(
    [
        get_header(),
        get_navbar('shap'),
        # html.Div([html.Br()], className='row sticky-top'),
        get_filter_row(),
        get_blank_row(h='10px'),
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
