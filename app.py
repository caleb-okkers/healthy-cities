import numpy as np
import pandas as pd
import streamlit as st

from src.metrics import add_derived_metrics, quadrant_labels
from src.charts import scatter_health_vs_cost, bar_top_n

st.set_page_config(page_title="Healthy Lifestyle Cities – Health vs Cost", layout="wide")

# Modern (B) look: subtle spacing + card-like containers
st.markdown(
    """
    <style>
      .block-container { padding-top: 2.0rem; padding-bottom: 2.0rem; max-width: 1200px; }
      h1 { font-size: 2.0rem !important; margin-bottom: 0.15rem; }
      .subtle { color: rgba(0,0,0,0.62); font-size: 0.95rem; margin-bottom: 1.25rem; }
      div[data-testid="stMetric"] { background: rgba(0,0,0,0.03); padding: 14px 14px; border-radius: 16px; }
      .section { margin-top: 1.25rem; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Healthy Lifestyle Cities – Health vs Cost Index")
st.markdown(
    '<div class="subtle">Built on an AWS serverless data lake (S3 + Glue Catalog + Athena). Dashboard uses the exported gold dataset.</div>',
    unsafe_allow_html=True
)

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    if path.endswith(".parquet"):
        df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path)

    df.columns = [c.strip() for c in df.columns]

    # Normalize key fields
    df["city"] = df["city"].astype(str).str.strip()
    for c in ["rank", "health_score", "cost_proxy"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Keep only usable rows
    df = df.dropna(subset=["city", "health_score", "cost_proxy"])

    return df

df = load_data("data/final.csv")
df = add_derived_metrics(df)

# Cosmetic rounding for display
df["health_score"] = df["health_score"].round(2)
df["cost_proxy"] = df["cost_proxy"].round(2)

with st.sidebar:
    st.header("Filters")
    st.caption("Use filters to explore clusters and outliers.")

    min_health, max_health = float(df["health_score"].min()), float(df["health_score"].max())
    min_cost, max_cost = float(df["cost_proxy"].min()), float(df["cost_proxy"].max())

    health_range = st.slider(
        "Health score range",
        min_value=min_health,
        max_value=max_health,
        value=(min_health, max_health)
    )

    cost_range = st.slider(
        "Cost proxy range",
        min_value=min_cost,
        max_value=max_cost,
        value=(min_cost, max_cost)
    )

    show_quadrants = st.toggle("Show quadrant split (median)", value=True)

filtered = df[
    (df["health_score"].between(*health_range)) &
    (df["cost_proxy"].between(*cost_range))
].copy()

# KPI row
c1, c2, c3, c4 = st.columns(4)

c1.metric("Cities", f"{len(filtered)}")

c2.metric(
    "Avg health",
    f"{filtered['health_score'].mean():.2f}" if len(filtered) else "—"
)

c3.metric(
    "Avg cost proxy",
    f"{filtered['cost_proxy'].mean():.2f}" if len(filtered) else "—"
)

best_city = "—"
if len(filtered):
    best_city = filtered.sort_values("value_score", ascending=False).iloc[0]["city"]
c4.metric("Best value city", best_city)

# Scatter
st.markdown('<div class="section"></div>', unsafe_allow_html=True)
st.subheader("Health vs Cost (Quadrants)")

x_mid = y_mid = None
if show_quadrants and len(filtered) >= 4:
    x_mid, y_mid = quadrant_labels(filtered, "cost_proxy", "health_score")

st.plotly_chart(
    scatter_health_vs_cost(filtered, x_mid=x_mid, y_mid=y_mid),
    use_container_width=True
)

# Rankings
st.markdown('<div class="section"></div>', unsafe_allow_html=True)
st.subheader("Rankings")

left, right = st.columns(2)

with left:
    st.plotly_chart(
        bar_top_n(filtered, col="health_score", title="Top 10 healthiest cities", n=10, ascending=False),
        use_container_width=True
    )

with right:
    st.plotly_chart(
        bar_top_n(filtered, col="value_score", title="Top 10 best value cities (health / cost)", n=10, ascending=False),
        use_container_width=True
    )

# Table
st.markdown('<div class="section"></div>', unsafe_allow_html=True)
st.subheader("Dataset")

table_cols = [
    "city", "rank", "health_score", "cost_proxy", "value_score",
    "life_expectancy_years_country", "pollution_index_city", "obesity_levels_country",
    "happiness_levels_country", "sunshine_hours_city", "annual_avg_hours_worked",
    "cost_monthly_gym_membership_city", "cost_bottle_water_city",
    "outdoor_activities_city", "number_takeout_places_city"
]
table_cols = [c for c in table_cols if c in filtered.columns]

st.dataframe(
    filtered[table_cols].sort_values(["health_score", "value_score"], ascending=[False, False]),
    use_container_width=True
)
