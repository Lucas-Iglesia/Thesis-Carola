import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from pathlib import Path

# Page configuration
st.set_page_config(page_title="ATS Experiment Results", layout="wide")

# Title
st.title("ATS Experiment Results Analysis")
st.markdown("---")

# Get available CSV files
results_dir = Path("results")
csv_files = sorted([f.name for f in results_dir.glob("*.csv")])

# Sidebar - File selector
st.sidebar.header("File Selection")
if csv_files:
    selected_file = st.sidebar.selectbox(
        "Select Results File",
        options=csv_files,
        index=0
    )
else:
    st.error("No CSV files found in the results directory!")
    st.stop()

# Load data
@st.cache_data
def load_data(filename):
    df = pd.read_csv(f"results/{filename}")
    return df

df = load_data(selected_file)

# Sidebar filters
st.sidebar.header("Filters")
selected_profiles = st.sidebar.multiselect(
    "Select Profiles",
    options=df['profile_id'].tolist(),
    default=df['profile_id'].tolist()
)

# Filter dataframe
filtered_df = df[df['profile_id'].isin(selected_profiles)]

# Display summary statistics
st.header("📊 Summary Statistics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Profiles", len(filtered_df))
with col2:
    st.metric("Avg Mean Score", f"{filtered_df['mean_total_score'].mean():.1f}")
with col3:
    st.metric("Highest Score", f"{filtered_df['max_total_score'].max():.0f}")
with col4:
    st.metric("Lowest Score", f"{filtered_df['min_total_score'].min():.0f}")

st.markdown("---")

# Main visualizations
col1, col2 = st.columns(2)

with col1:
    st.subheader("Mean Total Scores by Profile")
    fig1 = px.bar(
        filtered_df,
        x='profile_id',
        y='mean_total_score',
        error_y='stdev_total_score',
        hover_data=['description'],
        color='mean_total_score',
        color_continuous_scale='Viridis',
        labels={'mean_total_score': 'Mean Score', 'profile_id': 'Profile'}
    )
    fig1.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Score Range (Min-Max) by Profile")
    fig2 = go.Figure()
    
    for idx, row in filtered_df.iterrows():
        fig2.add_trace(go.Box(
            y=[row['min_total_score'], row['mean_total_score'], row['max_total_score']],
            name=row['profile_id'],
            boxmean=True
        ))
    
    fig2.update_layout(
        yaxis_title="Score",
        xaxis_title="Profile",
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig2, use_container_width=True)

# Variability analysis
st.markdown("---")
st.subheader("Score Variability Analysis")

col1, col2 = st.columns(2)

with col1:
    fig3 = px.scatter(
        filtered_df,
        x='mean_total_score',
        y='stdev_total_score',
        size='iterations',
        hover_data=['profile_id', 'description'],
        color='profile_id',
        labels={
            'mean_total_score': 'Mean Score',
            'stdev_total_score': 'Standard Deviation',
            'iterations': 'Iterations'
        },
        title="Mean Score vs. Variability"
    )
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    # Score range (max - min)
    filtered_df_copy = filtered_df.copy()
    filtered_df_copy['score_range'] = filtered_df_copy['max_total_score'] - filtered_df_copy['min_total_score']
    
    fig4 = px.bar(
        filtered_df_copy,
        x='profile_id',
        y='score_range',
        hover_data=['description'],
        color='score_range',
        color_continuous_scale='RdYlGn_r',
        labels={'score_range': 'Score Range', 'profile_id': 'Profile'},
        title="Score Range by Profile"
    )
    fig4.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig4, use_container_width=True)

# Detailed comparison
st.markdown("---")
st.subheader("Detailed Score Comparison")

fig5 = go.Figure()

fig5.add_trace(go.Bar(
    name='Minimum',
    x=filtered_df['profile_id'],
    y=filtered_df['min_total_score'],
    marker_color='lightblue'
))

fig5.add_trace(go.Bar(
    name='Mean',
    x=filtered_df['profile_id'],
    y=filtered_df['mean_total_score'],
    marker_color='blue',
    error_y=dict(
        type='data',
        array=filtered_df['stdev_total_score'],
        visible=True
    )
))

fig5.add_trace(go.Bar(
    name='Maximum',
    x=filtered_df['profile_id'],
    y=filtered_df['max_total_score'],
    marker_color='darkblue'
))

fig5.update_layout(
    barmode='group',
    xaxis_title="Profile",
    yaxis_title="Score",
    height=500,
    hovermode='x unified'
)

st.plotly_chart(fig5, use_container_width=True)

# Data table
st.markdown("---")
st.subheader("📋 Raw Data")
st.dataframe(
    filtered_df.style.background_gradient(subset=['mean_total_score'], cmap='YlGn'),
    use_container_width=True
)

# Profile descriptions
st.markdown("---")
st.subheader("Profile Descriptions")
for idx, row in filtered_df.iterrows():
    with st.expander(f"{row['profile_id']} - Mean Score: {row['mean_total_score']:.1f}"):
        st.write(f"**Description:** {row['description']}")
        st.write(f"**Iterations:** {row['iterations']}")
        st.write(f"**Score Range:** {row['min_total_score']:.0f} - {row['max_total_score']:.0f}")
        st.write(f"**Standard Deviation:** {row['stdev_total_score']:.2f}")
