import requests
import unittest
import os
import io
import time
from pathlib import Path

class SmartJobRecommendationAPITest(unittest.TestCase):
    def setUp(self):
        # Get the backend URL from the frontend .env file
        env_path = Path("/app/frontend/.env")
        backend_url = None
        
        if env_path.exists():
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("REACT_APP_BACKEND_URL="):
                        backend_url = line.strip().split("=")[1].strip('"')
                        break
        
        if not backend_url:
            raise ValueError("Could not find REACT_APP_BACKEND_URL in frontend/.env")
            
        self.base_url = f"{backend_url}/api"
        self.profile_id = None
        print(f"Using backend URL: {self.base_url}")
        
        # Create a sample resume text file for testing
        self.sample_resume = "John Doe\nemail: john@example.com\nPython developer with 3 years experience.\nSkills: Python, JavaScript, React, SQL, Git"
        
    def test_01_api_root(self):
        """Test the API root endpoint"""
        print("\n🔍 Testing API root endpoint...")
        response = requests.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        print("✅ API root endpoint test passed")
        
    def test_02_upload_resume(self):
        """Test resume upload functionality"""
        print("\n🔍 Testing resume upload...")
        
        # Create a text file in memory
        file_content = self.sample_resume.encode('utf-8')
        files = {'file': ('resume.txt', io.BytesIO(file_content), 'text/plain')}
        
        response = requests.post(f"{self.base_url}/upload-resume", files=files)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("profile", data)
        self.assertIn("id", data["profile"])
        self.assertIn("skills", data["profile"])
        
        # Save profile ID for subsequent tests
        self.profile_id = data["profile"]["id"]
        
        print(f"✅ Resume upload test passed. Profile ID: {self.profile_id}")
        print(f"   Detected skills: {data['profile']['skills']}")
        print(f"   Experience years: {data['profile']['experience_years']}")
        
        return self.profile_id
        
    def test_03_match_jobs(self):
        """Test job matching functionality"""
        if not self.profile_id:
            self.profile_id = self.test_02_upload_resume()
            
        print(f"\n🔍 Testing job matching for profile {self.profile_id}...")
        
        response = requests.post(f"{self.base_url}/match-jobs/{self.profile_id}")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("matches", data)
        self.assertGreater(len(data["matches"]), 0)
        
        # Check job match structure
        job = data["matches"][0]
        self.assertIn("title", job)
        self.assertIn("company", job)
        self.assertIn("fit_score", job)
        self.assertIn("matched_skills", job)
        self.assertIn("missing_skills", job)
        
        # Check for job search URLs
        self.assertIn("job_search_urls", job)
        self.assertIsInstance(job["job_search_urls"], dict)
        self.assertGreater(len(job["job_search_urls"]), 0)
        
        # Check for specific job platforms
        expected_platforms = ["LinkedIn", "Indeed", "Google Jobs"]
        for platform in expected_platforms:
            self.assertIn(platform, job["job_search_urls"])
            self.assertTrue(job["job_search_urls"][platform].startswith("http"))
            
        print(f"✅ Job matching test passed. Found {len(data['matches'])} matches")
        print(f"   Top match: {job['title']} at {job['company']} with {job['fit_score']}% fit")
        print(f"   Matched skills: {job['matched_skills']}")
        print(f"   Missing skills: {job['missing_skills']}")
        print(f"   Job search platforms: {list(job['job_search_urls'].keys())}")
        
    def test_04_learning_recommendations(self):
        """Test learning recommendations functionality"""
        if not self.profile_id:
            self.profile_id = self.test_02_upload_resume()
            
        print(f"\n🔍 Testing learning recommendations for profile {self.profile_id}...")
        
        response = requests.post(f"{self.base_url}/learning-recommendations/{self.profile_id}")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("recommendations", data)
        
        if len(data["recommendations"]) > 0:
            # Check recommendation structure
            rec = data["recommendations"][0]
            self.assertIn("skill", rec)
            self.assertIn("google_search_url", rec)
            self.assertIn("priority", rec)
            
            print(f"✅ Learning recommendations test passed. Found {len(data['recommendations'])} recommendations")
            for rec in data["recommendations"][:3]:  # Show first 3 recommendations
                print(f"   Skill: {rec['skill']} (Priority: {rec['priority']})")
                print(f"   Search URL: {rec['google_search_url']}")
        else:
            print("⚠️ No learning recommendations found, but API returned successfully")
            
    def test_05_get_profiles(self):
        """Test getting all profiles"""
        print("\n🔍 Testing get all profiles...")
        
        response = requests.get(f"{self.base_url}/profiles")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("profiles", data)
        
        print(f"✅ Get profiles test passed. Found {len(data['profiles'])} profiles")
        
    def run_all_tests(self):
        """Run all tests in sequence"""
        try:
            self.test_01_api_root()
            self.test_02_upload_resume()
            self.test_03_match_jobs()
            self.test_04_learning_recommendations()
            self.test_05_get_profiles()
            print("\n✅ All backend API tests passed successfully!")
        except AssertionError as e:
            print(f"\n❌ Test failed: {str(e)}")
        except Exception as e:
            print(f"\n❌ Error during testing: {str(e)}")

if __name__ == "__main__":
    tester = SmartJobRecommendationAPITest()
    tester.setUp()  # Explicitly call setUp to initialize base_url
    tester.run_all_tests()
