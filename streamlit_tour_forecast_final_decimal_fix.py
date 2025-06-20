
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import math

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

        # Integer ticket sales per week (rounded down to avoid over-selling)
        total_tickets = target_capacity
        tickets_per_week = total_tickets // weeks_to_show
        cumulative_tickets = [tickets_per_week * (i + 1) for i in range(weeks_to_show)]

        # Adjust final week to use up full capacity
        if cumulative_tickets[-1] < total_tickets:
            cumulative_tickets[-1] = total_tickets

        # Revenue and costs
        weekly_revenue = [round(tickets_per_week * avg_ticket_price, 2)] * (weeks_to_show - 1)
        final_week_tickets = total_tickets - tickets_per_week * (weeks_to_show - 1)
        final_week_revenue = round(final_week_tickets * avg_ticket_price, 2)
        weekly_revenue.append(final_week_revenue)

        cumulative_revenue = [round(sum(weekly_revenue[:i+1]), 2) for i in range(weeks_to_show)]

        # Net profit/loss = cumulative revenue - proportional marketing spend - fixed other costs
        cumulative_net = [
            round(cumulative_revenue[i] - (weekly_budget * (i + 1)) - other_costs, 2)
            for i in range(weeks_to_show)
        ]

        forecast_df = pd.DataFrame({
            "Week": weeks,
            "Week Start Date": [announce_date + timedelta(weeks=i) for i in range(weeks_to_show)],
            "Tickets Sold (Cumulative)": cumulative_tickets,
            "Gross Revenue (£, Cumulative)": [f"{val:.2f}" for val in cumulative_revenue],
            "Net Profit/Loss (£, Cumulative)": [f"{val:.2f}" for val in cumulative_net]
        })

        st.subheader("📊 Weekly Forecast")
        st.dataframe(forecast_df)

        # Plotly Chart
        st.subheader("📈 Forecast Charts")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=forecast_df["Week"], y=cumulative_tickets, mode='lines+markers', name='Tickets Sold'))
        fig.add_trace(go.Scatter(x=forecast_df["Week"], y=cumulative_revenue, mode='lines+markers', name='Gross Revenue'))
        fig.add_trace(go.Scatter(x=forecast_df["Week"], y=cumulative_net, mode='lines+markers', name='Net Profit/Loss'))

        fig.update_layout(
            xaxis_title="Week",
            yaxis_title="Cumulative Values",
            legend_title="Metrics"
        )

        st.plotly_chart(fig)

        # Downloadable CSV
        csv = forecast_df.to_csv(index=False)
        st.download_button("Download Forecast as CSV", csv, "tour_sales_forecast.csv", "text/csv")
