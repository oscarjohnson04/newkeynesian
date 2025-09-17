import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("New Keynesian Model")
st.subheader("Parameters")
col1, col2, col3 = st.columns(3)
with col1:
  user_beta = st.text_input("Enter Beta (Value between 0 and 1)", "0.1")
  beta = float(user_beta)
  user_sigma = st.text_input("Enter Sigma (Value between 0 and 1)", "0.1")
  sigma = float(user_sigma)
  user_expected_inflation = st.text_input("Enter inflation expectation", "0.1")
  pi = float(user_expected_inflation)
with col2:
  user_gamma = st.text_input("Enter output gap weight for the Phillips Curve (Value between 0 and 1)", "0.1")
  gamma = float(user_gamma)
  user_phi_pi = st.text_input("Enter CB coefficient for Inflation", "0.1")
  phi_pi = float(user_phi_pi)
  user_output_gap = st.text_input("Enter initial output gap", "1")
  output_gap = float(user_output_gap)
with col3:
  user_real_interest_rate = st.text_input("Enter real interest rate", "0.1")
  real_interest_rate = float(user_real_interest_rate)
  user_phi_y = st.text_input("Enter CB coefficient for Output Gap", "0.1")
  phi_y = float(user_phi_y)
  T = st.number_input("Enter simulation periods", 1)

st.sidebar.header("Shock Settings")
shock_location = st.sidebar.selectbox("Shock affects", ["Phillips Curve (Supply Shock)", "IS Curve (Demand Shock)"])
shock_type = st.sidebar.selectbox("Select shock type", ["None", "Single", "Persistent"])
if shock_type != "None":
  shock_size = st.sidebar.number_input("Shock size (%)", -100.0, 100.0, 1.0) / 100
  shock_time = st.sidebar.number_input("Shock start period")
  if shock_type == "Persistent":
    shock_duration = st.sidebar.number_input("Shock duration")

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
fig.add_trace(go.Scatter(x=time, y=pi_path, mode="lines+markers", name="Inflation"))
fig.add_trace(go.Scatter(x=time, y=output_gap_path, mode="lines+markers", name="Output gap"))
fig.add_trace(go.Scatter(x=time, y=i_path, mode="lines+markers", name="Interest rate"))
fig.add_trace(go.Bar(x=time, y=100*u, name="Shock (%)", opacity=0.3))

fig.update_layout(
    title="Impulse Response in Simple NK Model",
    xaxis_title="Time",
    yaxis_title="Value",
    template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)
