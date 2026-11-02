from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

df = pd.read_excel(Path(__file__).resolve().parent / "data" / "Bengaluru Ola.xlsx")

df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
df["Hour"] = pd.to_datetime(
    df["Time"].astype(str),
    format="%H:%M:%S",
    errors="coerce"
).dt.hour

df_success = df[df["Booking Status"] == "Success"].copy()

vehicle_types = sorted(df_success["Vehicle Type"].dropna().unique())
payment_methods = sorted(df_success["Payment Method"].dropna().unique())

min_distance = int(df_success["Ride Distance"].min())
max_distance = int(df_success["Ride Distance"].max())

hour_series = df_success["Hour"].dropna()
if hour_series.empty:
    min_hour, max_hour = 0, 23
else:
    min_hour = int(hour_series.min())
    max_hour = int(hour_series.max())

THEME = {
    "navy": "#0b3c5d",
    "teal": "#2aa9a1",
    "sky": "#eaf6ff",
    "insight": "#d9efff"
}

heat_scale = [
    (0.0, "#edf8fb"),
    (0.5, "#7bccc4"),
    (1.0, "#084081")
]


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def card(children, header=None):
    return dbc.Card(
        [
            dbc.CardHeader(
                header,
                style={
                    "backgroundColor": THEME["navy"],
                    "color": "white",
                    "fontWeight": "700",
                    "textAlign": "center"
                }
            ) if header else None,
            dbc.CardBody(children)
        ],
        style={"borderRadius": "14px"}
    )

def insight(text):
    return html.Div(
        [
            html.B("Insight: "),
            text
        ],
        style={
            "marginTop": "10px",
            "padding": "10px 14px",
            "backgroundColor": THEME["insight"],
            "borderLeft": f"5px solid {THEME['teal']}",
            "borderRadius": "8px",
            "fontSize": "14px"
        }
    )

app.layout = dbc.Container(
    [

        # ----------------- HEADER -----------------
        dbc.Card(
            dbc.CardBody(
                [
                    html.H2(
                        "Bengaluru Ola Ride Analytics Dashboard",
                        style={"textAlign": "center", "color": "white", "fontWeight": "700"}
                    ),
                    html.Div(
                        "Interactive Analysis Of Bengaluru Ola Ride Data Covering Demand Trends,"
                        " Distance Patterns, and Payment Behavior.",
                        style={"textAlign": "center", "color": "rgba(255,255,255,0.9)"}
                    )
                ]
            ),
            style={
                "background": f"linear-gradient(90deg, {THEME['navy']}, {THEME['teal']})",
                "borderRadius": "18px",
                "margin": "16px 0"
            }
        ),

        # ---------------- SECTION 1 -----------------
        card(
            [
                html.Label("Ride Distance Range (km)", style={"fontWeight": "600"}),
                dcc.RangeSlider(
                    id="distance_slider",
                    min=min_distance,
                    max=max_distance,
                    value=[min_distance, min_distance + 10],
                    marks={i: str(i) for i in range(min_distance, max_distance + 1, 5)}
                ),
                html.Hr(),

                dbc.Row([
                    dbc.Col(dcc.Graph(id="bubble_chart"), md=6),
                    dbc.Col(dcc.Graph(id="ridecount_bar"), md=6),
                ]),

                insight(
                    "This section compare how ride distance relates to booking value and ride volume across vehicle types."
                    "The bubble chart compares average booking value and distance, with bubble size indicating ride frequency."
                    "The bar chart highlights which vehicle types are most commonly used within the selected distance range."
                )
            ],
            header="Section 1: Distance-Based Overview"
        ),

        # ------------------- SECTION 2 -----------------
        card(
            [
                dbc.Row([
                    dbc.Col(
                        card(
                            [
                                html.Label("Vehicle Type", style={"fontWeight": "600"}),
                                dcc.Dropdown(
                                    id="vehicle_dropdown",
                                    options=[{"label": v, "value": v} for v in vehicle_types],
                                    value=vehicle_types[0]
                                ),
                                html.Br(),
                                html.Label("Day Hour Range", style={"fontWeight": "600"}),
                                dcc.RangeSlider(
                                    id="time_slider",
                                    min=min_hour,
                                    max=max_hour,
                                    value=[min_hour, min_hour + 6],
                                    marks={h: f"{h}:00" for h in range(min_hour, max_hour + 1, 3)}
                                )
                            ],
                            header="Filters"
                        ),
                        md=3
                    ),
                    dbc.Col(
                        card(dcc.Graph(id="heatmap"), header="Ride Density Heatmap"),
                        md=9
                    )
                ]),

                insight(
                    "This heatmap shows ride demand across pickup locations and hours of the day "
                    "for the selected vehicle type. Darker colors indicate higher ride volumes, "
                    "helping identify peak demand hours and high-traffic locations."
                )
            ],
            header="Section 2: Pickup Location × Hour Demand Pattern"
        ),

        # ------------------ SECTION 3 ------------------
        card(
            [
                html.Label("Payment Methods", style={"fontWeight": "600"}),
                dcc.Dropdown(
                    id="payment_dropdown",
                    options=[{"label": p, "value": p} for p in payment_methods],
                    value=payment_methods,
                    multi=True
                ),
                html.Hr(),
                dcc.Graph(id="payment_chart"),

                insight(
                    "The lollipop chart highlights revenue contribution by payment channel. "
                    "The length of each lollipop represents the revenue contribution of a payment method, "
                    "while the color intensity reinforces relative differences. This design emphasizes comparison "
                    "while maintaining clarity, helping identify which payment channels contribute most significantly "
                    "to overall booking revenue. "
                )
            ],
            header="Section 3: Revenue Contribution by Payment Channel"
        ),

        # ------------------ SECTION 4 -------------------
        card(
            [
                dbc.Row([
                    dbc.Col(
                        card(
                            [
                                html.Label("Vehicle Type", style={"fontWeight": "600"}),
                                dcc.RadioItems(
                                    id="vehicle_radio",
                                    options=[{"label": v, "value": v} for v in vehicle_types],
                                    value=vehicle_types[0]
                                ),
                                html.Br(),
                                html.Label("Pickup Location", style={"fontWeight": "600"}),
                                dcc.Dropdown(id="area_dropdown", multi=True)
                            ],
                            header="Chained Filters"
                        ),
                        md=3
                    ),
                    dbc.Col(
                        card(dcc.Graph(id="chained_chart"),
                             header="Booking Value by Payment Method"),
                        md=9
                    )
                ]),

                insight(
                    "This section demonstrates chained interaction where the available pickup "
                    "locations dynamically update based on the selected vehicle type. "
                    "The resulting chart displays total booking value by payment method for the "
                    "chosen vehicle type and pickup locations. This interaction illustrates "
                    "how multiple filters can work together to provide more focused insights, "
                    "enabling deeper analysis of customer payment behavior in specific operational contexts."
                )
            ],
            header="Section 4: Chained Callback"
        )

    ],
    fluid=True,
    style={"backgroundColor": THEME["sky"]}
)

# ----------------------------------------------------
# CALLBACKS
# ----------------------------------------------------
@app.callback(
    Output("bubble_chart", "figure"),
    Output("ridecount_bar", "figure"),
    Input("distance_slider", "value")
)
def update_section1(dist):
    dff = df_success[df_success["Ride Distance"].between(dist[0], dist[1])]
    agg = dff.groupby("Vehicle Type", as_index=False).agg(
        AvgBooking=("Booking Value", "mean"),
        AvgDistance=("Ride Distance", "mean"),
        RideCount=("Booking ID", "count")
    )

    bubble = px.scatter(
        agg, x="AvgBooking", y="AvgDistance", size="RideCount",
        color="Vehicle Type", text="Vehicle Type", size_max=30
    )
    bubble.update_layout(
        title=f"Avg Booking Value vs Avg Ride Distance (Distance {dist[0]}–{dist[1]} km)",
        height=500, plot_bgcolor="rgba(0,0,0,0)"
    )
    bubble.update_xaxes(showgrid=False)
    bubble.update_yaxes(showgrid=False)

    bar = px.bar(
        agg, x="Vehicle Type", y="RideCount",
        color="Vehicle Type", text="RideCount"
    )
    bar.update_layout(
        title=f"Ride Count by Vehicle Type (Distance {dist[0]}–{dist[1]} km)",
        height=500, plot_bgcolor="rgba(0,0,0,0)"
    )
    bar.update_xaxes(showgrid=False)
    bar.update_yaxes(showgrid=False)

    return bubble, bar


@app.callback(
    Output("heatmap", "figure"),
    Input("vehicle_dropdown", "value"),
    Input("time_slider", "value")
)
def update_heatmap(vehicle, hours):
    dff = df_success[
        (df_success["Vehicle Type"] == vehicle) &
        (df_success["Hour"].between(hours[0], hours[1]))
    ]

    agg = dff.groupby(["Pickup Location", "Hour"]).size().reset_index(name="RideCount")
    top_areas = agg.groupby("Pickup Location")["RideCount"].sum().nlargest(10).index
    agg = agg[agg["Pickup Location"].isin(top_areas)]

    fig = px.density_heatmap(
        agg, x="Hour", y="Pickup Location", z="RideCount",
        color_continuous_scale=heat_scale
    )
    fig.update_layout(
        title=f"Ride Density for {vehicle} Vehicles (Hours {hours[0]}–{hours[1]})",
        height=500, plot_bgcolor="rgba(0,0,0,0)"
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig


@app.callback(
    Output("payment_chart", "figure"),
    Input("payment_dropdown", "value")
)
def update_payment(payments):
    dff = df_success[df_success["Payment Method"].isin(payments)]
    agg = dff.groupby("Payment Method", as_index=False)["Booking Value"].sum().sort_values("Booking Value")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=agg["Booking Value"], y=agg["Payment Method"],
        mode="lines", line=dict(color="rgba(0,0,0,0.25)", width=2)
    ))
    fig.add_trace(go.Scatter(
        x=agg["Booking Value"], y=agg["Payment Method"],
        mode="markers+text",
        marker=dict(size=18, color=agg["Booking Value"], colorscale="Plasma", showscale=True),
        text=[f"₹{v:,.0f}" for v in agg["Booking Value"]],
        textposition="middle right"
    ))

    fig.update_layout(
        title="Revenue Contribution by Payment Channel",
        height=520, plot_bgcolor="rgba(0,0,0,0)"
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig


@app.callback(
    Output("area_dropdown", "options"),
    Output("area_dropdown", "value"),
    Input("vehicle_radio", "value")
)
def update_area(vehicle):
    areas = sorted(df_success[df_success["Vehicle Type"] == vehicle]["Pickup Location"].dropna().unique())
    return [{"label": a, "value": a} for a in areas], areas[:2]


@app.callback(
    Output("chained_chart", "figure"),
    Input("vehicle_radio", "value"),
    Input("area_dropdown", "value")
)
def update_chained(vehicle, areas):
    dff = df_success[
        (df_success["Vehicle Type"] == vehicle) &
        (df_success["Pickup Location"].isin(areas))
    ]
    agg = dff.groupby("Payment Method", as_index=False)["Booking Value"].sum()

    fig = px.bar(
        agg, x="Booking Value", y="Payment Method",
        orientation="h", text="Booking Value",
        color="Booking Value", color_continuous_scale="Viridis"
    )
    fig.update_layout(
        title=f"Booking Value by Payment Method ({vehicle})",
        height=500, plot_bgcolor="rgba(0,0,0,0)"
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig

if __name__ == "__main__":
    app.run(debug=False, port=8050)
