# autoapply_platform/utils/apply_via_api.py

import requests
import json
import time
import logging
import os
from datetime import datetime
import random
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("apply_api.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("apply_api")

class JobApplicationAPI:
    def __init__(self, user_profile_path=None, resume_path=None):
        """
        Initialize the Job Application API client.
        
        Args:
            user_profile_path (str): Path to user profile YAML
            resume_path (str): Path to resume JSON
        """
        self.user_profile_path = user_profile_path or "../user_profile/profile.yaml"
        self.resume_path = resume_path or "../user_profile/resume.json"
        
        # Load user profile and resume
        self.user_profile = self._load_user_profile()
        self.resume = self._load_resume()
        
        # API request headers
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "AutoApplyPlatform/1.0.0"
        }
        
        # API rate limiting settings
        self.min_delay = 5  # minimum seconds between requests
        self.max_delay = 15  # maximum seconds between requests
        self.last_request_time = 0
    
    def _load_user_profile(self):
        """Load user profile from YAML file."""
        try:
            if os.path.exists(self.user_profile_path):
                with open(self.user_profile_path, 'r') as file:
                    return yaml.safe_load(file)
            else:
                logger.warning(f"User profile not found at: {self.user_profile_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading user profile: {str(e)}")
            return {}
    
    def _load_resume(self):
        """Load resume from JSON file."""
        try:
            if os.path.exists(self.resume_path):
                with open(self.resume_path, 'r') as file:
                    return json.load(file)
            else:
                logger.warning(f"Resume not found at: {self.resume_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading resume: {str(e)}")
            return {}
    
    def _rate_limit(self):
        """Apply rate limiting to API requests."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.min_delay:
            sleep_time = random.uniform(self.min_delay - elapsed, self.max_delay - elapsed)
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def apply_to_greenhouse_job(self, job_id, company_board, cover_letter=None):
        """
        Apply to a job via Greenhouse API.
        
        Args:
            job_id (str): Greenhouse job ID
            company_board (str): Company board name (e.g., 'airbnb')
            cover_letter (str, optional): Custom cover letter text
            
        Returns:
            dict: Response data or error information
        """
        self._rate_limit()
        
        # Prepare application data
        application_data = self._prepare_greenhouse_application(cover_letter)
        
        # Greenhouse application endpoint
        url = f"https://boards-api.greenhouse.io/v1/boards/{company_board}/jobs/{job_id}/apply"
        
        try:
            logger.info(f"Submitting application to Greenhouse for job ID: {job_id} at {company_board}")
            
            # In a real implementation, this would be an actual API call
            # For this MVP, we'll simulate the API response
            response = self._simulate_api_response("greenhouse")
            
            if response.get("success", False):
                logger.info(f"Application submitted successfully. Reference: {response.get('reference_id')}")
            else:
                logger.error(f"Application failed: {response.get('error')}")
            
            return response
            
        except Exception as e:
            error_msg = f"Error applying to job {job_id}: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def apply_to_lever_job(self, job_id, company_name, cover_letter=None):
        """
        Apply to a job via Lever API.
        
        Args:
            job_id (str): Lever job ID
            company_name (str): Company name (e.g., 'netflix')
            cover_letter (str, optional): Custom cover letter text
            
        Returns:
            dict: Response data or error information
        """
        self._rate_limit()
        
        # Prepare application data
        application_data = self._prepare_lever_application(cover_letter)
        
        # Lever application endpoint
        url = f"https://jobs.lever.co/api/v0/postings/{company_name}/{job_id}/apply"
        
        try:
            logger.info(f"Submitting application to Lever for job ID: {job_id} at {company_name}")
            
            # In a real implementation, this would be an actual API call
            # For this MVP, we'll simulate the API response
            response = self._simulate_api_response("lever")
            
            if response.get("success", False):
                logger.info(f"Application submitted successfully. Reference: {response.get('reference_id')}")
            else:
                logger.error(f"Application failed: {response.get('error')}")
            
            return response
            
        except Exception as e:
            error_msg = f"Error applying to job {job_id}: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _prepare_greenhouse_application(self, cover_letter=None):
        """Prepare Greenhouse application data from user profile and resume."""
        # This is a simplified implementation
        # In a real app, you would map all the fields properly
        
        application = {
            "first_name": self.resume.get("personal_info", {}).get("name", "").split()[0],
            "last_name": self.resume.get("personal_info", {}).get("name", "").split()[-1],
            "email": self.resume.get("personal_info", {}).get("email", ""),
            "phone": self.resume.get("personal_info", {}).get("phone", ""),
            "resume": "base64-encoded-resume-would-go-here",
            "cover_letter": cover_letter or self._generate_cover_letter(),
            "linkedin_url": self.resume.get("personal_info", {}).get("linkedin", ""),
            "website": self.resume.get("personal_info", {}).get("portfolio", ""),
            "github": self.resume.get("personal_info", {}).get("github", ""),
        }
        
        return application
    
    def _prepare_lever_application(self, cover_letter=None):
        """Prepare Lever application data from user profile and resume."""
        # This is a simplified implementation
        # In a real app, you would map all the fields properly
        
        application = {
            "name": self.resume.get("personal_info", {}).get("name", ""),
            "email": self.resume.get("personal_info", {}).get("email", ""),
            "phone": self.resume.get("personal_info", {}).get("phone", ""),
            "resume": "base64-encoded-resume-would-go-here",
            "cover_letter": cover_letter or self._generate_cover_letter(),
            "linkedin": self.resume.get("personal_info", {}).get("linkedin", ""),
            "website": self.resume.get("personal_info", {}).get("portfolio", ""),
            "github": self.resume.get("personal_info", {}).get("github", ""),
        }
        
        return application
    
    def _generate_cover_letter(self):
        """Generate a cover letter from template and user profile."""
        # In a real app, this would generate a custom cover letter
        # For the MVP, we'll use a sample
        
        template = """
        Dear Hiring Manager,
        
        I am writing to express my interest in the {position} position at {company}. 
        With my background in {skills}, I believe I would be a great addition to your team.
        
        {custom_paragraph}
        
        Thank you for considering my application. I look forward to the opportunity to discuss 
        how my skills and experience align with your needs.
        
        Sincerely,
        {name}
        """
        
        # This would be customized based on the job and user profile
        custom_paragraph = "I am particularly drawn to this role because it aligns with my career goals and interests. My experience with similar challenges has prepared me to make an immediate contribution to your team."
        
        # Fill in template
        cover_letter = template.format(
            position="[Position]",
            company="[Company]",
            skills=", ".join(self.resume.get("skills", {}).get("programming_languages", []))[:3],
            custom_paragraph=custom_paragraph,
            name=self.resume.get("personal_info", {}).get("name", "")
        )
        
        return cover_letter
    
    def _simulate_api_response(self, platform):
        """Simulate API response for testing purposes."""
        # This is only for MVP purposes
        # In a real app, this would be replaced with actual API calls
        
        # Simulate success with 90% probability
        if random.random() < 0.9:
            return {
                "success": True,
                "reference_id": f"{platform}-{random.randint(10000, 99999)}",
                "status": "submitted",
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Simulate failure
            errors = [
                "Required field missing",
                "Application period closed",
                "Rate limit exceeded",
                "Already applied to this position"
            ]
            return {
                "success": False,
                "error": random.choice(errors),
                "timestamp": datetime.now().isoformat()
            }

if __name__ == "__main__":
    # Example usage
    api = JobApplicationAPI()
    
    # Example Greenhouse application
    greenhouse_response = api.apply_to_greenhouse_job(
        job_id="12345",
        company_board="airbnb"
    )
    print("Greenhouse Response:", greenhouse_response)
    
    # Example Lever application
    lever_response = api.apply_to_lever_job(
        job_id="54321",
        company_name="netflix"
    )
    print("Lever Response:", lever_response)
