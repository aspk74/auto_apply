# autoapply_platform/dashboard/streamlit_analytics.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
import sys
sys.path.append("..")  # Add parent directory to path

class AutoApplyDashboard:
    def __init__(self):
        self.log_path = "../swipes/application_log.csv"
        self.greenhouse_path = "../data"
        self.lever_path = "../data"
    
    def run(self):
        """Run the Streamlit dashboard."""
        st.set_page_config(
            page_title="AutoApply Dashboard",
            page_icon="📊",
            layout="wide"
        )
        
        st.title("📊 AutoApply Analytics Dashboard")
        
        # Load data
        application_data = self._load_application_data()
        if application_data is None:
            st.error("No application data found. Please apply to some jobs first.")
            return
        
        # Dashboard tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Application Status", "Job Sources", "Settings"])
        
        with tab1:
            self._render_overview(application_data)
        
        with tab2:
            self._render_application_status(application_data)
        
        with tab3:
            self._render_job_sources(application_data)
        
        with tab4:
            self._render_settings()

    def _load_application_data(self):
        """Load application data from CSV file."""
        try:
            if not os.path.exists(self.log_path):
                return None
            
            df = pd.read_csv(self.log_path)
            
            # Convert applied_at to datetime
            df['applied_at'] = pd.to_datetime(df['applied_at'])
            
            # Add some derived columns
            df['application_date'] = df['applied_at'].dt.date
            df['application_week'] = df['applied_at'].dt.isocalendar().week
            df['application_month'] = df['applied_at'].dt.month
            
            return df
        except Exception as e:
            st.error(f"Error loading application data: {str(e)}")
            return None

    def _render_overview(self, df):
        """Render the overview tab."""
        st.header("Application Overview")
        
        # Key metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Applications", len(df))
        
        with col2:
            # Applications in the last 7 days
            last_week = datetime.now() - timedelta(days=7)
            recent_apps = df[df['applied_at'] > last_week]
            st.metric("Last 7 Days", len(recent_apps))
        
        with col3:
            # Response rate
            response_rate = len(df[df['response_received'] == True]) / len(df) * 100 if len(df) > 0 else 0
            st.metric("Response Rate", f"{response_rate:.1f}%")
        
        with col4:
            # Success metrics (interviews)
            interview_rate = len(df[df['status'] == 'interview']) / len(df) * 100 if len(df) > 0 else 0
            st.metric("Interview Rate", f"{interview_rate:.1f}%")
        
        # Applications over time
        st.subheader("Applications Over Time")
        date_counts = df.groupby('application_date').size().reset_index(name='count')
        date_counts = date_counts.set_index('application_date')
        
        # Fill in missing dates
        all_dates = pd.date_range(date_counts.index.min(), date_counts.index.max())
        date_counts = date_counts.reindex(all_dates, fill_value=0)
        
        # Plot
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(date_counts.index, date_counts['count'], marker='o')
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Applications')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        st.pyplot(fig)
        
        # Recent applications table
        st.subheader("Recent Applications")
        recent = df.sort_values('applied_at', ascending=False).head(10)
        st.dataframe(
            recent[['company', 'title', 'location', 'applied_at', 'status', 'response_received']],
            use_container_width=True
        )

    def _render_application_status(self, df):
        """Render the application status tab."""
        st.header("Application Status Breakdown")
        
        # Status pie chart
        st.subheader("Application Status Distribution")
        status_counts = df['status'].value_counts()
        
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        
        st.pyplot(fig)
        
        # Response time analysis
        st.subheader("Response Analysis")
        
        # This would be more complex in a real application
        # For MVP, we'll just show some dummy metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Average Response Time", "3.2 days")
        
        with col2:
            st.metric("No Response Rate", "35%")
        
        # Status by company
        st.subheader("Status by Company")
        
        # Create a cross-tabulation of company vs status
        company_status = pd.crosstab(df['company'], df['status'])
        
        st.dataframe(company_status, use_container_width=True)

    def _render_job_sources(self, df):
        """Render the job sources tab."""
        st.header("Job Sources Analysis")
        
        # Source distribution
        st.subheader("Applications by Source")
        source_counts = df['source'].value_counts()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=source_counts.index, y=source_counts.values, ax=ax)
        ax.set_xlabel('Source')
        ax.set_ylabel('Number of Applications')
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        st.pyplot(fig)
        
        # Response rate by source
        st.subheader("Response Rate by Source")
        
        # Group by source and calculate response rate
        source_response = df.groupby('source')['response_received'].mean() * 100
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=source_response.index, y=source_response.values, ax=ax)
        ax.set_xlabel('Source')
        ax.set_ylabel('Response Rate (%)')
        ax.set_ylim(0, 100)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        st.pyplot(fig)
        
        # Company distribution
        st.subheader("Applications by Company")
        company_counts = df['company'].value_counts().head(10)  # Top 10 companies
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=company_counts.index, y=company_counts.values, ax=ax)
        ax.set_xlabel('Company')
        ax.set_ylabel('Number of Applications')
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        st.pyplot(fig)

    def _render_settings(self):
        """Render the settings tab."""
        st.header("Dashboard Settings")
        
        st.subheader("Date Range")
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                datetime.now() - timedelta(days=30)
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                datetime.now()
            )
        
        st.subheader("Dashboard Refresh")
        refresh_interval = st.slider(
            "Refresh interval (minutes)",
            min_value=5,
            max_value=60,
            value=15,
            step=5
        )
        
        st.button("Refresh Now", type="primary")
        
        st.subheader("Export Data")
        export_format = st.selectbox(
            "Export Format",
            ["CSV", "Excel", "JSON"]
        )
        
        st.download_button(
            label=f"Export as {export_format}",
            data="Sample data export",  # This would be actual data in a real app
            file_name=f"autoapply_export_{datetime.now().strftime('%Y%m%d')}.{export_format.lower()}",
            mime="text/plain"
        )

if __name__ == "__main__":
    dashboard = AutoApplyDashboard()
    dashboard.run()
