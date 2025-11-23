from dash import Input, Output, State, ALL, callback, ctx
from dash import html

def time_select_period():
    options = [
        ("4 weeks", "Last 4 Weeks"),
        ("6 months", "Last 6 Months"),
        ("12 months", "Last 12 Months"),
    ]

    return html.Div(
        className="time-period-select",
        children=[
            html.Div(
                className="time-period-buttons",
                children=[
                    html.Button(
                        label,
                        id={"type": "time-period-button", "value": value},
                        className="time-period-button heading-4",
                        n_clicks=0,
                    )
                    for value, label in options
                ],
            )
        ],
    )


@callback(
    Output({"type": "time-period-button", "value": ALL}, "className"),
    Output({"type": "time-period-button", "value": ALL}, "disabled"),
    Output("selected-time-period", "data"),
    Input({"type": "time-period-button", "value": ALL}, "n_clicks"),
    State({"type": "time-period-button", "value": ALL}, "id"),
)
def update_active_button(n_clicks_list, ids):
    if not any(n_clicks_list) or ctx.triggered_id is None:
        active_value = ids[0]["value"]
    else:
        triggered = ctx.triggered_id
        active_value = triggered["value"]

    classnames = [
        (
            "time-period-button heading-4 active"
            if id_["value"] == active_value
            else "time-period-button heading-4"
        )
        for id_ in ids
    ]

    disabled_list = [
        (id_["value"] == active_value)
        for id_ in ids
    ]

    return classnames, disabled_list, active_value

