
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

st.title("🤓 Tour Sales Forecasting Tool")

# Input form
with st.form("show_input"):
    show_date = st.date_input("Show Date")
    avg_ticket_price = st.number_input("Average Ticket Price (£)", min_value=0.0, value=50.0)
    marketing_budget = st.number_input("Total Marketing Budget (£)", min_value=0.0, value=1000.0)
    other_costs = st.number_input("Other Costs (£)", min_value=0.0, value=500.0)
    target_capacity = st.number_input("Target Capacity (Total Tickets)", min_value=0, value=500)
    announce_date = st.date_input("Announcement Date", value=datetime.today())

    submitted = st.form_submit_button("Generate Forecast")

if submitted:
    # Calculate time range
    weeks_to_show = ((show_date - announce_date).days) // 7
    if weeks_to_show < 1:
        st.error("Show date must be at least one week after the announcement date.")
    else:
        weeks = list(range(1, weeks_to_show + 1))
        weekly_budget = marketing_budget / weeks_to_show

        # Linear sales forecast model
        total_tickets = target_capacity
        tickets_per_week = total_tickets / weeks_to_show
        cumulative_tickets = [tickets_per_week * (i + 1) for i in range(weeks_to_show)]
        weekly_revenue = [tickets_per_week * avg_ticket_price] * weeks_to_show
        cumulative_revenue = [sum(weekly_revenue[:i+1]) for i in range(weeks_to_show)]

        weekly_net = [rev - weekly_budget - (other_costs / weeks_to_show) for rev in weekly_revenue]
        cumulative_net = [sum(weekly_net[:i+1]) for i in range(weeks_to_show)]

        forecast_df = pd.DataFrame({
            "Week": weeks,
            "Week Start Date": [announce_date + timedelta(weeks=i) for i in range(weeks_to_show)],
            "Tickets Sold (Cumulative)": cumulative_tickets,
            "Gross Revenue (£, Cumulative)": cumulative_revenue,
            "Net Profit/Loss (£, Cumulative)": cumulative_net
        })

        st.subheader("📊 Weekly Forecast")
        st.dataframe(forecast_df)

        # Plotly Chart
        st.subheader("📈 Forecast Charts")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=forecast_df["Week"], y=forecast_df["Tickets Sold (Cumulative)"], mode='lines+markers', name='Tickets Sold'))
        fig.add_trace(go.Scatter(x=forecast_df["Week"], y=forecast_df["Gross Revenue (£, Cumulative)"], mode='lines+markers', name='Gross Revenue'))
        fig.add_trace(go.Scatter(x=forecast_df["Week"], y=forecast_df["Net Profit/Loss (£, Cumulative)"], mode='lines+markers', name='Net Profit/Loss'))

        fig.update_layout(
            xaxis_title="Week",
            yaxis_title="Cumulative Values",
            legend_title="Metrics"
        )

        st.plotly_chart(fig)

        # Downloadable CSV
        csv = forecast_df.to_csv(index=False)
        st.download_button("Download Forecast as CSV", csv, "tour_sales_forecast.csv", "text/csv")
