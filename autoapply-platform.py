# autoapply_platform/job_feed/fetch_greenhouse_jobs.py

import requests
import json
import pandas as pd
from datetime import datetime

def fetch_greenhouse_jobs(companies=None):
    """
    Fetch job listings from Greenhouse API for specified companies.
    
    Args:
        companies (list): List of company boards to fetch jobs from
                         e.g. ['airbnb', 'stripe', 'coinbase']
    
    Returns:
        pandas.DataFrame: DataFrame containing job listings
    """
    if companies is None:
        companies = ['airbnb', 'stripe', 'coinbase']  # Default companies
    
    all_jobs = []
    
    for company in companies:
        try:
            url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('jobs', [])
                
                for job in jobs:
                    job_data = {
                        'id': job.get('id'),
                        'title': job.get('title'),
                        'location': job.get('location', {}).get('name', 'Remote'),
                        'updated_at': job.get('updated_at'),
                        'absolute_url': job.get('absolute_url'),
                        'company': company,
                        'source': 'greenhouse',
                        'fetched_at': datetime.now().isoformat()
                    }
                    all_jobs.append(job_data)
                
                print(f"Successfully fetched {len(jobs)} jobs from {company}")
            else:
                print(f"Failed to fetch jobs from {company}. Status code: {response.status_code}")
        
        except Exception as e:
            print(f"Error fetching jobs from {company}: {str(e)}")
    
    # Convert to DataFrame
    df = pd.DataFrame(all_jobs)
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    df.to_csv(f"data/greenhouse_jobs_{timestamp}.csv", index=False)
    
    return df

if __name__ == "__main__":
    jobs = fetch_greenhouse_jobs()
    print(f"Total jobs fetched: {len(jobs)}")
