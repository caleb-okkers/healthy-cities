import pandas as pd
import plotly.express as px


TOOLTIP_COLS = [
    ("rank", "Rank", ":.0f"),
    ("health_score", "Health score", ":.2f"),
    ("cost_proxy", "Cost proxy", ":.2f"),
    ("value_score", "Value (health/cost)", ":.4f"),
    ("life_expectancy_years_country", "Life expectancy (yrs)", ":.2f"),
    ("pollution_index_city", "Pollution index", ":.2f"),
    ("obesity_levels_country", "Obesity (%)", ":.2f"),
    ("happiness_levels_country", "Happiness", ":.2f"),
    ("sunshine_hours_city", "Sunshine (hrs)", ":.0f"),
    ("annual_avg_hours_worked", "Annual hours worked", ":.0f"),
    ("cost_monthly_gym_membership_city", "Gym monthly cost", ":.2f"),
    ("cost_bottle_water_city", "Bottle water cost", ":.2f"),
    ("outdoor_activities_city", "Outdoor activities", ":.0f"),
    ("number_takeout_places_city", "Takeout places", ":.0f"),
]


def _hover_data_map(df: pd.DataFrame) -> dict:
    hover = {}
    for col, _, fmt in TOOLTIP_COLS:
        if col in df.columns:
            hover[col] = fmt
    return hover


def scatter_health_vs_cost(
    df: pd.DataFrame,
    x_col: str = "cost_proxy",
    y_col: str = "health_score",
    x_mid: float | None = None,
    y_mid: float | None = None,
):
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        hover_name="city",
        hover_data=_hover_data_map(df),
    )

    # Modern, clean defaults (no custom colors)
    fig.update_traces(marker=dict(size=10, opacity=0.85), selector=dict(mode="markers"))

    # Quadrant lines + labels (median split)
    if x_mid is not None and y_mid is not None:
        xmin, xmax = float(df[x_col].min()), float(df[x_col].max())
        ymin, ymax = float(df[y_col].min()), float(df[y_col].max())

        fig.add_shape(type="line", x0=x_mid, x1=x_mid, y0=ymin, y1=ymax)
        fig.add_shape(type="line", x0=xmin, x1=xmax, y0=y_mid, y1=y_mid)

        # Place labels inside plot area (subtle)
        pad_x = (xmax - xmin) * 0.02
        pad_y = (ymax - ymin) * 0.03

        fig.add_annotation(
            x=xmin + pad_x, y=ymax - pad_y,
            text="High Health / Low Cost",
            showarrow=False
        )
        fig.add_annotation(
            x=xmax - pad_x, y=ymax - pad_y,
            text="High Health / High Cost",
            showarrow=False, xanchor="right"
        )
        fig.add_annotation(
            x=xmin + pad_x, y=ymin + pad_y,
            text="Low Health / Low Cost",
            showarrow=False, yanchor="bottom"
        )
        fig.add_annotation(
            x=xmax - pad_x, y=ymin + pad_y,
            text="Low Health / High Cost",
            showarrow=False, xanchor="right", yanchor="bottom"
        )

    fig.update_layout(
        xaxis_title="Cost proxy (Gym + Water)",
        yaxis_title="Health score (0–100)",
        height=620,
        margin=dict(l=16, r=16, t=40, b=16),
        template="plotly_white",
        font=dict(size=14),
        hoverlabel=dict(font_size=13),
    )

    # Slightly reduce grid intensity
    fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.06)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.06)")

    return fig


def bar_top_n(df: pd.DataFrame, col: str, title: str, n: int = 10, ascending: bool = False):
    top = df.sort_values(col, ascending=ascending).head(n).copy()

    fig = px.bar(
        top,
        x="city",
        y=col,
        title=title,
        hover_data=_hover_data_map(top),
    )

    fig.update_layout(
        height=460,
        margin=dict(l=16, r=16, t=60, b=16),
        template="plotly_white",
        font=dict(size=14),
    )
    fig.update_xaxes(title_text="", tickangle=-25, showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.06)")
    return fig
