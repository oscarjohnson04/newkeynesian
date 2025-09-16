import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("New Keynesian Model")
col1, col2, col3 = st.columns(3)
with col1:
  user_beta = st.text_input("Enter Beta (Value between 0 and 1)", "0.5")
  beta = float(user_beta)
  user_sigma = st.text_input("Enter Sigma (Value between 0 and 1)", "0.5")
  sigma = float(user_sigma)
  user_expected_inflation = st.text_input("Enter inflation expectation", "2")
  pi = float(user_expected_inflation)
with col2:
  user_gamma = st.text_input("Enter Gamma (Value between 0 and 1)", "0.5")
  gamma = float(user_gamma)
  user_phi_pi = st.text_input("Enter CB coefficient for Inflation", "1.5")
  phi_pi = float(user_phi_pi)
  user_output_gap = st.text_input("Enter initial output gap", "20")
  output_gap = float(user_output_gap)
with col3:
  user_real_interest_rate = st.text_input("Enter real interest rate", "1")
  real_interest_rate = float(user_real_interest_rate)
  user_phi_y = st.text_input("Enter CB coefficient for Output Gap", "0.5")
  phi_y = float(user_phi_y)
  T = st.number_input("Enter simulation periods", 50)

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
    output_gap_path[t+1] = output_gap_next - (1/sigma) * (i_path[t] - Epi_next)

    # Phillips curve
    pi_path[t+1] = beta * Epi_next + gamma * output_gap_path[t] 

time = np.arange(T)

fig = go.Figure()
fig.add_trace(go.Scatter(x=time, y=100*pi_path, mode="lines+markers", name="Inflation (%)"))
fig.add_trace(go.Scatter(x=time, y=100*output_gap_path, mode="lines+markers", name="Output gap (%)"))
fig.add_trace(go.Scatter(x=time, y=100*i_path, mode="lines+markers", name="Interest rate (%)"))

fig.update_layout(
    title="Impulse Response in Simple NK Model",
    xaxis_title="Time",
    yaxis_title="Percent (deviation)",
    template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)
