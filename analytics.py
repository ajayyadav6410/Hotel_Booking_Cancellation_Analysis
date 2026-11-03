from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

DATA_FILE = Path(__file__).parent / "dataset.csv"

month_names = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
               7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
month_order = list(month_names.values())


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    df = df[df["LeadTime"] >= 0]
    df["IsCanceled"] = df["IsCanceled"].map({"Yes": 1, "No": 0})
    df["MonthName"] = df["ArrivalDateMonth"].map(month_names)
    return df


def bar_chart(data, title, xlabel, ylabel, color="steelblue", ylim=None):
    fig, ax = plt.subplots(figsize=(7, 4))
    data.plot(kind="bar", ax=ax, color=color, edgecolor="black")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if ylim:
        ax.set_ylim(*ylim)
    ax.tick_params(axis="x", rotation=45)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f", fontsize=8)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def show_dashboard():
    df = load_data()

    st.subheader("Hotel booking cancellation analytics")
    st.write("Python analysis of 10,000 hotel bookings: how many get cancelled, and why it matters.")

    # ---------- Filters ----------
    deposit_options = sorted(df["DepositType"].unique())
    country_options = sorted(df["Country"].unique())

    f1, f2, f3 = st.columns(3)
    selected_months = f1.multiselect("Month", month_order, default=month_order)
    selected_deposits = f2.multiselect("Deposit type", deposit_options, default=deposit_options)
    selected_countries = f3.multiselect("Country", country_options, default=country_options)

    filtered = df[
        df["MonthName"].isin(selected_months)
        & df["DepositType"].isin(selected_deposits)
        & df["Country"].isin(selected_countries)
    ]

    if filtered.empty:
        st.warning("No bookings match the selected filters.")
        return

    # ---------- KPI cards ----------
    total_bookings = len(filtered)
    cancelled = int(filtered["IsCanceled"].sum())
    cancel_rate = filtered["IsCanceled"].mean() * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Total bookings", f"{total_bookings:,}")
    col2.metric("Cancelled bookings", f"{cancelled:,}")
    col3.metric("Cancellation rate", f"{cancel_rate:.2f}%")

    # ---------- Charts ----------
    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Cancellation rate by month")
        month_rate = filtered.groupby("MonthName")["IsCanceled"].mean() * 100
        month_rate = month_rate.reindex(month_order).dropna()
        bar_chart(month_rate, "Cancellation rate by month", "Month", "Cancellation %", ylim=(0, 100))

    with right:
        st.subheader("Cancellation rate by deposit type")
        deposit_rate = filtered.groupby("DepositType")["IsCanceled"].mean() * 100
        bar_chart(deposit_rate, "Cancellation rate by deposit type", "Deposit type", "Cancellation %", ylim=(0, 100))

    st.subheader("Bookings by month")
    bookings_month = filtered["MonthName"].value_counts().reindex(month_order).dropna()
    bar_chart(bookings_month, "Number of bookings by month", "Month", "Bookings", color="seagreen")

    # ---------- Key insights ----------
    st.divider()
    st.subheader("Key insights")

    revenue = filtered["ADR"] * (filtered["StaysInWeekendNights"] + filtered["StaysInWeekNights"])
    total_revenue = revenue.sum()
    lost_revenue = revenue[filtered["IsCanceled"] == 1].sum()
    loss_pct = lost_revenue / total_revenue * 100

    st.markdown("**For the current filter selection:**")
    st.markdown(f"- Revenue lost to cancellations: **{lost_revenue:,.0f}** out of {total_revenue:,.0f} ({loss_pct:.2f}%)")
    st.markdown(f"- Busiest month: **{bookings_month.idxmax()}** ({int(bookings_month.max())} bookings)")
    if len(month_rate) > 1:
        st.markdown(f"- Highest cancellation month: **{month_rate.idxmax()}** ({month_rate.max():.1f}%), "
                    f"lowest: **{month_rate.idxmin()}** ({month_rate.min():.1f}%)")

    st.markdown("**Across the full dataset:**")
    st.markdown(
        "- Cancellation rate stays between about 88% and 92% for every month, deposit type, "
        "customer type, country and lead-time group I checked.\n"
        "- Higher price (ADR) and longer waiting lists did not lead to clearly more cancellations.\n"
        "- No numeric column has a strong link with cancellations (all correlations between -0.02 and +0.02)."
    )

    # ---------- Limitations ----------
    st.subheader("Limitations")
    st.info(
        "The cancellation rate is about 90%, much higher than real hotels usually see, and no factor "
        "showed a clear link with cancellations. The dataset may be synthetic, so these results should "
        "not be treated as real-world hotel behaviour. The dataset also has no hotel type or booking "
        "date columns, and some groups are small (for example, only 174 bookings had a waiting list "
        "of 4 to 7 days)."
    )