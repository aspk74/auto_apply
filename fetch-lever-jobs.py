# autoapply_platform/job_feed/fetch_lever_jobs.py

import requests
import json
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

def fetch_lever_jobs(companies=None):
    """
    Fetch job listings from Lever API for specified companies.
    
    Args:
        companies (list): List of company sites to fetch jobs from
                         e.g. ['netflix', 'figma', 'slack']
    
    Returns:
        pandas.DataFrame: DataFrame containing job listings
    """
    if companies is None:
        companies = ['netflix', 'figma', 'slack']  # Default companies
    
    all_jobs = []
    
    for company in companies:
        try:
            url = f"https://api.lever.co/v0/postings/{company}"
            response = requests.get(url)
            
            if response.status_code == 200:
                jobs = response.json()
                
                for job in jobs:
                    job_data = {
                        'id': job.get('id'),
                        'title': job.get('text'),
                        'location': job.get('categories', {}).get('location', 'Remote'),
                        'team': job.get('categories', {}).get('team', 'Not specified'),
                        'updated_at': job.get('createdAt'),
                        'absolute_url': job.get('hostedUrl'),
                        'company': company,
                        'source': 'lever',
                        'fetched_at': datetime.now().isoformat()
                    }
                    
                    # Parse description
                    if 'description' in job:
                        soup = BeautifulSoup(job['description'], 'html.parser')
                        job_data['description'] = soup.get_text()
                    
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
    df.to_csv(f"data/lever_jobs_{timestamp}.csv", index=False)
    
    return df

if __name__ == "__main__":
    jobs = fetch_lever_jobs()
    print(f"Total jobs fetched: {len(jobs)}")
