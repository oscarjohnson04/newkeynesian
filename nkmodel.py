import streamlit as st
import numpy as np
import plotly.graph_objects as go
from fredapi import Fred
import pandas as pd
import datetime as dt
from statsmodels.api import tsa
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")
st.title("New Keynesian Model")

end = dt.datetime(2024,1,1)
start = dt.datetime(1950,1,1)

st.subheader("Parameters")
col1, col2, col3 = st.columns(3)
with col1:
  user_beta = st.text_input("Enter Beta (Value between 0 and 1)", "0.1")
  beta = float(user_beta)
  user_sigma = st.text_input("Enter Sigma (Value between 0 and 1)", "0.1")
  sigma = float(user_sigma)
with col2:
  user_gamma = st.text_input("Enter output gap weight for the Phillips Curve (Value between 0 and 1)", "0.1")
  gamma = float(user_gamma)
  user_phi_pi = st.text_input("Enter CB coefficient for Inflation", "0.1")
  phi_pi = float(user_phi_pi)
with col3:
  user_phi_y = st.text_input("Enter CB coefficient for Output Gap", "0.1")
  phi_y = float(user_phi_y)
  T = st.number_input("Enter simulation periods", 1)

fred = Fred(api_key='00edddc751dd47fb05bd7483df1ed0a3')
pi = round(fred.get_series("MEDCPIM158SFRBCLE").iloc[-1], 2)
gdp = fred.get_series('GDPC1', start, end) 
gdp_cycle, gdp_trend = tsa.filters.hpfilter(gdp)
output_gap = (gdp_cycle / gdp_trend) * 100
output_gap = round(output_gap.iloc[-1], 2)
real_interest_rate = round(fred.get_series("REAINTRATREARAT1MO").iloc[-1], 2)

st.sidebar.header("Shock Settings")
shock_location = st.sidebar.selectbox("Shock affects", ["Phillips Curve (Supply Shock)", "IS Curve (Demand Shock)"])
shock_type = st.sidebar.selectbox("Select shock type", ["None", "Single", "Persistent"])
if shock_type != "None":
  shock_size = st.sidebar.number_input("Shock size (%)", -100.0, 100.0, 1.0)
  shock_time = st.sidebar.number_input("Shock start period", min_value=0, max_value=T-1, value=0, step=1)
  if shock_type == "Persistent":
    shock_duration = st.sidebar.number_input("Shock duration", min_value=0, max_value=T-1, value=0, step=1)

u = np.zeros(T)
if shock_type == "Single":
    u[shock_time] = shock_size
elif shock_type == "Persistent":
    u[shock_time:shock_time+shock_duration] = shock_size

pi_path = np.zeros(T)
output_gap_path = np.zeros(T)
i_path = np.zeros(T)
pi_path[0] = pi
output_gap_path[0] = output_gap

for t in range(T-1):
    # Expectations = last period values (simple approximation)
    output_gap_next = output_gap_path[t]
    Epi_next = pi_path[t]
    # Taylor rule
    i_path[t] = real_interest_rate + phi_pi * pi_path[t] + phi_y * output_gap_path[t] 

    # IS curve
    if shock_location == "IS Curve (Demand Shock)":
        output_gap_path[t+1] = output_gap_next - (1/sigma) * (i_path[t] - Epi_next) + u[t]
    else:
        output_gap_path[t+1] = output_gap_next - (1/sigma) * (i_path[t] - Epi_next)

    # Phillips curve
    if shock_location == "Phillips Curve (Supply Shock)":
        pi_path[t+1] = beta * Epi_next + gamma * output_gap_path[t] + u[t]
    else:
        pi_path[t+1] = beta * Epi_next + gamma * output_gap_path[t]

time = np.arange(T)

fig = go.Figure()
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=time, y=pi_path, mode="lines+markers", name="Inflation"), secondary_y = False)
fig.add_trace(go.Scatter(x=time, y=output_gap_path, mode="lines+markers", name="Output gap"), secondary_y = True)
fig.add_trace(go.Scatter(x=time, y=i_path, mode="lines+markers", name="Interest rate"), secondary_y = False)
fig.add_trace(go.Bar(x=time, y=u, name="Shock (%)", opacity=0.3), secondary_y = False)

fig.update_layout(
    title="Impulse Response in Simple NK Model",
    xaxis_title="Time",
    yaxis_title="Value",
    template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)
