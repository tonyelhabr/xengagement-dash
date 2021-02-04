import dash

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        {
            'href':
                'https://fonts.googleapis.com/css2?'
                'family=Karla:wght@400;700&display=swap',
            'rel': 'stylesheet',
        },
    ],
    meta_tags=[
        {
            'name': 'viewport',
            'content': 'width=device-width, initial-scale=1.0'
        }
    ]
)
# server = app.server