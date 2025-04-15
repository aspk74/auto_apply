# AutoApply Platform

AutoApply is an automated job application platform that allows users to discover and apply to relevant job opportunities with minimal effort. The platform fetches job listings from multiple sources, filters them based on user preferences, and provides a simple "swipe" interface for selecting which jobs to apply to.

## Architecture

The platform is built with a modular MVP (Minimum Viable Product) architecture:

```
autoapply_platform/
├── job_feed/              # Fetch jobs from different sources
│   └── fetch_greenhouse_jobs.py
│   └── fetch_lever_jobs.py
├── user_profile/          # User data and preferences
│   └── resume.json
│   └── profile.yaml
├── swipes/                # Job application mechanism
│   └── swipe_applicator.py
│   └── application_log.csv
├── dashboard/             # Analytics and monitoring
│   └── streamlit_analytics.py
├── utils/                 # Shared utilities
│   └── job_filtering.py
│   └── apply_via_api.py
├── data/                  # Data storage directory
└── README.md
```

## Features

- **Multi-source Job Fetching**: Automatically gather job listings from various job boards (currently Greenhouse and Lever)
- **Smart Job Filtering**: Filter jobs based on user preferences, skills, and experience
- **Swipe Interface**: Simple "swipe right" to apply, "swipe left" to reject interface
- **Profile Management**: Store and manage user resume and application preferences
- **Automated Applications**: Apply to jobs automatically using the appropriate APIs
- **Analytics Dashboard**: Track application status, response rates, and overall statistics

## Setup and Installation

### Prerequisites

- Python 3.8+
- Required packages:
  - pandas
  - requests
  - pyyaml
  - streamlit
  - beautifulsoup4
  - matplotlib
  - seaborn

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/autoapply_platform.git
   cd autoapply_platform
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create data directory:
   ```bash
   mkdir -p data
   ```

4. Set up your user profile:
   - Edit `user_profile/resume.json` with your resume information
   - Edit `user_profile/profile.yaml` with your job preferences

## Usage

### Fetch Jobs

To fetch jobs from Greenhouse:

```bash
cd job_feed
python fetch_greenhouse_jobs.py
```

To fetch jobs from Lever:

```bash
cd job_feed
python fetch_lever_jobs.py
```

### Apply to Jobs

To start the application process:

```bash
cd swipes
python swipe_applicator.py
```

### View Analytics Dashboard

To launch the analytics dashboard:

```bash
cd dashboard
streamlit run streamlit_analytics.py
```

## Customization

### Job Filtering

Edit your preferences in `user_profile/profile.yaml` to customize job filtering criteria:

```yaml
job_search:
  job_titles:
    - Software Engineer
    - Full Stack Developer
  
  locations:
    - San Francisco, CA
    - Remote
  
  remote_preferences:
    fully_remote: true
    hybrid: true
    onsite: false
```

### Application Limits

Configure daily, weekly, and monthly application limits:

```yaml
application_limits:
  daily_max: 15
  weekly_max: 50
  monthly_max: 150
```

### Resume and Cover Letter

Update your resume in `user_profile/resume.json` and customize cover letter templates in the application API utilities.

## Future Enhancements

- Additional job sources (LinkedIn, Indeed, etc.)
- ML-based job matching algorithms
- Interview scheduling and preparation assistance
- Integration with applicant tracking systems
- Mobile application interface

## Disclaimer

This platform is intended for educational purposes. Please use responsibly and in accordance with the terms of service of any job platforms you interact with.

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
