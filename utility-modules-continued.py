# autoapply_platform/utils/job_filtering.py (continued)

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
    if 'job_titles' in criteria:
        title_keywords = criteria['job_titles']
        title_pattern = '|'.join(title_keywords)
        title_filter = filtered['title'].str.contains(title_pattern, case=False, na=False)
        filtered = filtered[title_filter]
    
    # Filter by location
    if 'locations' in criteria:
        location_keywords = criteria['locations']
        
        # Handle remote preference
        if criteria.get('remote_preferences', {}).get('fully_remote', False):
            location_keywords.append('Remote')
        
        location_pattern = '|'.join(location_keywords)
        location_filter = filtered['location'].str.contains(location_pattern, case=False, na=False)
        filtered = filtered[location_filter]
    
    # Filter by recency
    if 'max_days_old' in criteria:
        if 'updated_at' in filtered.columns:
            max_days = criteria['max_days_old']
            cutoff_date = (datetime.now() - timedelta(days=max_days)).isoformat()
            filtered = filtered[filtered['updated_at'] >= cutoff_date]
    
    # Filter out excluded companies
    if 'excluded_companies' in criteria:
        excluded = criteria['excluded_companies']
        if excluded:
            excluded_pattern = '|'.join(excluded)
            excluded_filter = ~filtered['company'].str.contains(excluded_pattern, case=False, na=False)
            filtered = filtered[excluded_filter]
    
    # Filter by experience level
    if 'experience_level' in criteria:
        exp_levels = criteria['experience_level'].get('levels', [])
        if exp_levels:
            # Look for experience level terms in the title or description
            exp_pattern = '|'.join(exp_levels)
            
            # Check title for experience level
            title_exp_filter = filtered['title'].str.contains(exp_pattern, case=False, na=False)
            
            # Check description for experience level if it exists
            if 'description' in filtered.columns:
                desc_exp_filter = filtered['description'].str.contains(exp_pattern, case=False, na=False)
                exp_filter = title_exp_filter | desc_exp_filter
            else:
                exp_filter = title_exp_filter
            
            filtered = filtered[exp_filter]
    
    # Custom keyword filtering
    if 'keywords' in criteria:
        keywords = criteria['keywords']
        if keywords:
            keyword_pattern = '|'.join(keywords)
            
            # Check title for keywords
            title_keyword_filter = filtered['title'].str.contains(keyword_pattern, case=False, na=False)
            
            # Check description for keywords if it exists
            if 'description' in filtered.columns:
                desc_keyword_filter = filtered['description'].str.contains(keyword_pattern, case=False, na=False)
                keyword_filter = title_keyword_filter | desc_keyword_filter
            else:
                keyword_filter = title_keyword_filter
            
            filtered = filtered[keyword_filter]
    
    return filtered

def rank_jobs(jobs_df, criteria, user_profile):
    """
    Rank jobs based on relevance to user criteria and profile.
    
    Args:
        jobs_df (pandas.DataFrame): DataFrame containing job listings
        criteria (dict): Dictionary of user criteria
        user_profile (dict): User profile information
        
    Returns:
        pandas.DataFrame: DataFrame with added relevance score
    """
    if jobs_df.empty:
        return jobs_df
    
    # Create a base relevance score
    jobs_df['relevance_score'] = 1.0
    
    # Boost score based on title match
    if 'job_titles' in criteria and 'title' in jobs_df.columns:
        for title in criteria['job_titles']:
            # Exact match gets higher boost
            jobs_df.loc[jobs_df['title'].str.contains(f"\\b{title}\\b", case=False, regex=True), 'relevance_score'] += 2.0
            # Partial match gets smaller boost
            jobs_df.loc[jobs_df['title'].str.contains(title, case=False), 'relevance_score'] += 1.0
    
    # Boost score based on location match
    if 'locations' in criteria and 'location' in jobs_df.columns:
        for location in criteria['locations']:
            jobs_df.loc[jobs_df['location'].str.contains(location, case=False, na=False), 'relevance_score'] += 1.5
    
    # Boost for recency
    if 'updated_at' in jobs_df.columns:
        # Convert to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(jobs_df['updated_at']):
            jobs_df['updated_at'] = pd.to_datetime(jobs_df['updated_at'], errors='coerce')
        
        # Calculate days since posting and apply decay factor
        current_time = pd.Timestamp.now()
        jobs_df['days_since_posting'] = (current_time - jobs_df['updated_at']).dt.total_seconds() / (24 * 3600)
        jobs_df['recency_factor'] = np.exp(-0.1 * jobs_df['days_since_posting'])
        jobs_df['relevance_score'] *= jobs_df['recency_factor']
        
        # Drop temporary columns
        jobs_df = jobs_df.drop(['days_since_posting', 'recency_factor'], axis=1)
    
    # Boost based on skill match (if description available)
    if 'skills' in user_profile and 'description' in jobs_df.columns:
        all_skills = []
        for skill_category in user_profile['skills'].values():
            all_skills.extend(skill_category)
        
        for skill in all_skills:
            # Use regex to find word boundaries for more accurate matching
            pattern = f"\\b{re.escape(skill)}\\b"
            jobs_df.loc[jobs_df['description'].str.contains(pattern, case=False, na=False, regex=True), 'relevance_score'] += 0.5
    
    # Sort by relevance score (descending)
    jobs_df = jobs_df.sort_values('relevance_score', ascending=False)
    
    return jobs_df

def calculate_match_percentage(job, user_profile):
    """
    Calculate match percentage between a job and user profile.
    
    Args:
        job (pandas.Series): Job listing
        user_profile (dict): User profile information
        
    Returns:
        float: Match percentage (0-100)
    """
    total_points = 0
    earned_points = 0
    
    # Title match (up to 30 points)
    if 'title' in job and 'job_titles' in user_profile.get('job_search', {}):
        total_points += 30
        for title in user_profile['job_search']['job_titles']:
            if title.lower() in job['title'].lower():
                earned_points += 30
                break
    
    # Location match (up to 20 points)
    if 'location' in job and 'locations' in user_profile.get('job_search', {}):
        total_points += 20
        for location in user_profile['job_search']['locations']:
            if location.lower() in job['location'].lower():
                earned_points += 20
                break
        
        # Remote work preference
        if (user_profile.get('job_search', {}).get('remote_preferences', {}).get('fully_remote', False) and
            'remote' in job['location'].lower()):
            earned_points += 5
    
    # Skills match (up to 50 points)
    if 'description' in job and 'skills' in user_profile:
        total_points += 50
        skill_points = 0
        all_skills = []
        
        # Flatten all skills into a list
        for skill_category, skills in user_profile['skills'].items():
            all_skills.extend(skills)
        
        # Count matching skills
        for skill in all_skills:
            # Check for whole word matches
            pattern = f"\\b{re.escape(skill)}\\b"
            if re.search(pattern, job['description'], re.IGNORECASE):
                skill_points += 3  # 3 points per matching skill
        
        # Cap skill points at 50
        earned_points += min(skill_points, 50)
    
    # Calculate percentage
    match_percentage = (earned_points / total_points * 100) if total_points > 0 else 0
    
    return round(match_percentage, 1)
