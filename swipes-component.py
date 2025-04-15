# autoapply_platform/swipes/swipe_applicator.py

import pandas as pd
import json
import yaml
import os
from datetime import datetime
import time
import random

class SwipeApplicator:
    def __init__(self, profile_path=None, resume_path=None):
        """
        Initialize the SwipeApplicator for job applications.
        
        Args:
            profile_path (str): Path to profile YAML file
            resume_path (str): Path to resume JSON file
        """
        self.profile_path = profile_path or "../user_profile/profile.yaml"
        self.resume_path = resume_path or "../user_profile/resume.json"
        self.log_path = "application_log.csv"
        
        # Load user profile and resume
        self.profile = self._load_profile()
        self.resume = self._load_resume()
        
        # Initialize or load application log
        self._initialize_log()
        
        # Track application limits
        self.today_count = self._get_today_application_count()
    
    def _load_profile(self):
        """Load user profile from YAML file."""
        try:
            with open(self.profile_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Error loading profile: {str(e)}")
            return {}
    
    def _load_resume(self):
        """Load resume from JSON file."""
        try:
            with open(self.resume_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading resume: {str(e)}")
            return {}
    
    def _initialize_log(self):
        """Initialize or load the application log."""
        if not os.path.exists(self.log_path):
            df = pd.DataFrame(columns=[
                'job_id', 'company', 'title', 'location', 'source', 
                'applied_at', 'status', 'response_received', 'notes'
            ])
            df.to_csv(self.log_path, index=False)
        
        self.log_df = pd.read_csv(self.log_path)
    
    def _get_today_application_count(self):
        """Get the count of applications made today."""
        today = datetime.now().strftime("%Y-%m-%d")
        return len(self.log_df[self.log_df['applied_at'].str.startswith(today)])
    
    def get_job_recommendations(self):
        """
        Get job recommendations based on user profile.
        
        Returns:
            pandas.DataFrame: DataFrame of recommended jobs
        """
        # In a real implementation, this would use the job_filtering.py utility
        # For this MVP, we'll simulate by loading sample jobs
        try:
            # Try to load the most recent job files
            job_files = [f for f in os.listdir("../data") if f.endswith(".csv")]
            if not job_files:
                return pd.DataFrame()
            
            latest_file = sorted(job_files)[-1]
            jobs_df = pd.read_csv(f"../data/{latest_file}")
            
            # Apply filters based on user preferences
            filtered_jobs = self._filter_jobs(jobs_df)
            return filtered_jobs
            
        except Exception as e:
            print(f"Error getting job recommendations: {str(e)}")
            # Return empty DataFrame if there's an error
            return pd.DataFrame()
    
    def _filter_jobs(self, jobs_df):
        """Filter jobs based on user preferences."""
        # This is a simplified filter - in a real app, you'd use the job_filtering.py utility
        filtered = jobs_df.copy()
        
        # Filter by job title if specified in profile
        if 'job_titles' in self.profile.get('job_search', {}):
            title_keywords = self.profile['job_search']['job_titles']
            title_filter = filtered['title'].str.contains('|'.join(title_keywords), case=False)
            filtered = filtered[title_filter]
        
        # Filter by location if specified
        if 'locations' in self.profile.get('job_search', {}):
            location_keywords = self.profile['job_search']['locations']
            
            # Include 'Remote' jobs if remote preference is true
            if self.profile.get('job_search', {}).get('remote_preferences', {}).get('fully_remote', False):
                location_keywords.append('Remote')
                
            location_filter = filtered['location'].str.contains('|'.join(location_keywords), case=False)
            filtered = filtered[location_filter]
        
        # Filter out excluded companies
        if 'excluded_companies' in self.profile.get('job_search', {}):
            excluded = self.profile['job_search']['excluded_companies']
            excluded_filter = ~filtered['company'].str.contains('|'.join(excluded), case=False)
            filtered = filtered[excluded_filter]
        
        return filtered
    
    def swipe_right(self, job_id):
        """
        Apply to a job (swipe right).
        
        Args:
            job_id (str): ID of the job to apply to
            
        Returns:
            bool: True if application was successful, False otherwise
        """
        # Check if already applied
        if job_id in self.log_df['job_id'].values:
            print(f"Already applied to job {job_id}")
            return False
        
        # Check daily limit
        if self.today_count >= self.profile.get('application_limits', {}).get('daily_max', 15):
            print("Daily application limit reached")
            return False
        
        # Get job details
        job_df = self.get_job_recommendations()
        job = job_df[job_df['id'] == job_id]
        
        if job.empty:
            print(f"Job {job_id} not found")
            return False
        
        # In a real implementation, this would call apply_via_api.py
        # For this MVP, we'll simulate the application
        success = self._simulate_application(job.iloc[0])
        
        if success:
            # Log the application
            self._log_application(job.iloc[0])
            self.today_count += 1
        
        return success
    
    def _simulate_application(self, job):
        """Simulate applying to a job (for MVP purposes)."""
        # Simulate API call delay
        time.sleep(random.uniform(1, 3))
        
        # 90% success rate for simulation
        return random.random() < 0.9
    
    def _log_application(self, job):
        """Log a successful application."""
        new_row = {
            'job_id': job['id'],
            'company': job['company'],
            'title': job['title'],
            'location': job['location'],
            'source': job['source'],
            'applied_at': datetime.now().isoformat(),
            'status': 'applied',
            'response_received': False,
            'notes': ''
        }
        
        self.log_df = pd.concat([self.log_df, pd.DataFrame([new_row])], ignore_index=True)
        self.log_df.to_csv(self.log_path, index=False)
    
    def swipe_left(self, job_id, reason=None):
        """
        Reject a job (swipe left).
        
        Args:
            job_id (str): ID of the job to reject
            reason (str, optional): Reason for rejection
        """
        # In a production app, you might want to log rejections too
        print(f"Rejected job {job_id}" + (f" - Reason: {reason}" if reason else ""))
    
    def get_application_stats(self):
        """
        Get application statistics.
        
        Returns:
            dict: Dictionary with application statistics
        """
        stats = {
            'total_applications': len(self.log_df),
            'today_applications': self.today_count,
            'responses_received': len(self.log_df[self.log_df['response_received'] == True]),
            'by_status': self.log_df['status'].value_counts().to_dict(),
            'by_company': self.log_df['company'].value_counts().to_dict(),
            'by_source': self.log_df['source'].value_counts().to_dict()
        }
        
        return stats

if __name__ == "__main__":
    applicator = SwipeApplicator()
    jobs = applicator.get_job_recommendations()
    
    if not jobs.empty:
        print(f"Found {len(jobs)} recommended jobs")
        
        # Demo: Apply to the first job
        first_job_id = jobs.iloc[0]['id']
        success = applicator.swipe_right(first_job_id)
        
        if success:
            print(f"Successfully applied to job: {jobs.iloc[0]['title']} at {jobs.iloc[0]['company']}")
        else:
            print("Application failed")
        
        # Print application stats
        print("\nApplication Statistics:")
        stats = applicator.get_application_stats()
        for key, value in stats.items():
            print(f"{key}: {value}")
    else:
        print("No recommended jobs found")
