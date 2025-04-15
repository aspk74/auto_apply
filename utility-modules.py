# autoapply_platform/utils/job_filtering.py

import re
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def filter_jobs(jobs_df, criteria):
    """
    Filter jobs based on specified criteria.
    
    Args:
        jobs_df (pandas.DataFrame): DataFrame containing job listings
        criteria (dict): Dictionary of filtering criteria
        
    Returns:
        pandas.DataFrame: Filtered DataFrame
    """
    if jobs_df.empty:
        return jobs_df
    
    filtered = jobs_df.copy()
    
    # Filter by job title
    if 'job_titles'