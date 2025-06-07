import { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [currentView, setCurrentView] = useState('upload');
  const [profile, setProfile] = useState(null);
  const [jobMatches, setJobMatches] = useState([]);
  const [learningRecs, setLearningRecs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileUpload = async (file) => {
    setIsLoading(true);
    setUploadProgress(20);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      setUploadProgress(50);
      const response = await axios.post(`${API}/upload-resume`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setUploadProgress(80);
      
      if (response.data.success) {
        setProfile(response.data.profile);
        setUploadProgress(100);
        
        // Auto-fetch job matches
        setTimeout(async () => {
          await fetchJobMatches(response.data.profile.id);
          await fetchLearningRecommendations(response.data.profile.id);
          setCurrentView('dashboard');
        }, 1000);
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Error uploading resume: ' + (error.response?.data?.detail || error.message));
    } finally {
      setIsLoading(false);
    }
  };

  const fetchJobMatches = async (profileId) => {
    try {
      const response = await axios.post(`${API}/match-jobs/${profileId}`);
      if (response.data.success) {
        setJobMatches(response.data.matches);
      }
    } catch (error) {
      console.error('Error fetching job matches:', error);
    }
  };

  const fetchLearningRecommendations = async (profileId) => {
    try {
      const response = await axios.post(`${API}/learning-recommendations/${profileId}`);
      if (response.data.success) {
        setLearningRecs(response.data.recommendations);
      }
    } catch (error) {
      console.error('Error fetching learning recommendations:', error);
    }
  };

  const FileUploadZone = () => {
    const [dragOver, setDragOver] = useState(false);

    const handleDragOver = (e) => {
      e.preventDefault();
      setDragOver(true);
    };

    const handleDragLeave = (e) => {
      e.preventDefault();
      setDragOver(false);
    };

    const handleDrop = (e) => {
      e.preventDefault();
      setDragOver(false);
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        handleFileUpload(files[0]);
      }
    };

    const handleFileSelect = (e) => {
      const file = e.target.files[0];
      if (file) {
        handleFileUpload(file);
      }
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center p-8">
        <div className="max-w-2xl w-full">
          <div className="text-center mb-12">
            <h1 className="text-6xl font-bold text-white mb-4 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
              Smart Job AI
            </h1>
            <p className="text-xl text-gray-300">
              Upload your resume and discover your perfect career match with AI-powered recommendations
            </p>
          </div>

          <div
            className={`relative border-4 border-dashed rounded-3xl p-16 text-center transition-all duration-300 cursor-pointer backdrop-blur-lg bg-white/10 hover:bg-white/20 ${
              dragOver ? 'border-cyan-400 bg-cyan-400/20' : 'border-gray-400'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById('fileInput').click()}
          >
            <input
              id="fileInput"
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={handleFileSelect}
              className="hidden"
            />
            
            <div className="text-center">
              <div className="w-24 h-24 mx-auto mb-8 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 flex items-center justify-center">
                <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              
              <h3 className="text-2xl font-bold text-white mb-4">Upload Your Resume</h3>
              <p className="text-gray-300 mb-6">
                Drag and drop your resume here, or click to browse
              </p>
              <p className="text-sm text-gray-400">
                Supports PDF, DOCX, and TXT files
              </p>
            </div>

            {isLoading && (
              <div className="absolute inset-0 bg-black/50 rounded-3xl flex items-center justify-center">
                <div className="text-center text-white">
                  <div className="w-16 h-16 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                  <p className="text-lg font-semibold">Processing Resume...</p>
                  <div className="w-48 h-2 bg-gray-600 rounded-full mx-auto mt-4">
                    <div 
                      className="h-full bg-gradient-to-r from-cyan-400 to-purple-500 rounded-full transition-all duration-500"
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-gray-300 mt-2">{uploadProgress}% Complete</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const Dashboard = () => {
    const [activeTab, setActiveTab] = useState('profile');

    const ProfileView = () => (
      <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border border-white/20">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-bold text-white">Profile Overview</h2>
          <button
            onClick={() => setCurrentView('upload')}
            className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl hover:from-purple-600 hover:to-pink-600 transition-all duration-300 font-semibold"
          >
            Upload New Resume
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-semibold text-cyan-400 mb-3">Personal Information</h3>
              <div className="space-y-2">
                <p className="text-white"><span className="text-gray-300">Name:</span> {profile?.name}</p>
                <p className="text-white"><span className="text-gray-300">Email:</span> {profile?.email}</p>
                <p className="text-white"><span className="text-gray-300">Experience:</span> {profile?.experience_years} years</p>
              </div>
            </div>
            
            <div>
              <h3 className="text-xl font-semibold text-cyan-400 mb-3">Skills Portfolio</h3>
              <div className="flex flex-wrap gap-2">
                {profile?.skills?.map((skill, index) => (
                  <span
                    key={index}
                    className="px-4 py-2 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-cyan-300 rounded-full text-sm font-medium border border-cyan-500/30"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>
          
          <div className="bg-gradient-to-br from-cyan-500/20 to-purple-500/20 rounded-2xl p-6 border border-cyan-500/30">
            <h3 className="text-xl font-semibold text-white mb-4">AI Analysis</h3>
            <div className="space-y-4">
              <div>
                <p className="text-gray-300 text-sm">Skills Detected</p>
                <p className="text-2xl font-bold text-cyan-400">{profile?.skills?.length || 0}</p>
              </div>
              <div>
                <p className="text-gray-300 text-sm">Experience Level</p>
                <p className="text-2xl font-bold text-purple-400">
                  {profile?.experience_years >= 5 ? 'Senior' : profile?.experience_years >= 2 ? 'Mid-Level' : 'Junior'}
                </p>
              </div>
              <div>
                <p className="text-gray-300 text-sm">Job Matches Found</p>
                <p className="text-2xl font-bold text-green-400">{jobMatches.length}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );

    const JobMatchesView = () => {
      
      const handleApplyNow = (job) => {
        // Open multiple job search platforms in new tabs
        const platforms = job.job_search_urls;
        const platformNames = ['LinkedIn', 'Indeed', 'Google Jobs'];
        
        platformNames.forEach((platform, index) => {
          if (platforms[platform]) {
            setTimeout(() => {
              window.open(platforms[platform], '_blank');
            }, index * 500); // Stagger the opening by 500ms to avoid browser blocking
          }
        });
      };

      return (
        <div className="space-y-6">
          <h2 className="text-3xl font-bold text-white mb-8">AI Job Recommendations</h2>
          
          {jobMatches.map((job, index) => (
            <div key={job.id} className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border border-white/20 hover:border-cyan-400/50 transition-all duration-300">
              <div className="flex items-start justify-between mb-6">
                <div className="flex-1">
                  <div className="flex items-center gap-4 mb-2">
                    <h3 className="text-2xl font-bold text-white">{job.title}</h3>
                    <div className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-full">
                      <span className="font-bold">{job.fit_score}% Match</span>
                    </div>
                  </div>
                  <p className="text-cyan-400 text-lg font-semibold mb-2">{job.company}</p>
                  <p className="text-gray-300 mb-4">{job.location} • {job.salary_range}</p>
                  <p className="text-gray-300 mb-6">{job.description}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-lg font-semibold text-green-400 mb-3">Your Matching Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {job.matched_skills.map((skill, skillIndex) => (
                      <span
                        key={skillIndex}
                        className="px-3 py-1 bg-green-500/20 text-green-300 rounded-full text-sm border border-green-500/30"
                      >
                        ✓ {skill}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h4 className="text-lg font-semibold text-orange-400 mb-3">Skills to Learn</h4>
                  <div className="flex flex-wrap gap-2">
                    {job.missing_skills.map((skill, skillIndex) => (
                      <span
                        key={skillIndex}
                        className="px-3 py-1 bg-orange-500/20 text-orange-300 rounded-full text-sm border border-orange-500/30"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="mt-6 pt-6 border-t border-white/20 flex gap-4">
                <button 
                  onClick={() => handleApplyNow(job)}
                  className="px-8 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-xl hover:from-cyan-600 hover:to-blue-600 transition-all duration-300 font-semibold"
                >
                  🚀 Apply Now (Opens LinkedIn, Indeed, Google)
                </button>
                <div className="flex-1">
                  <p className="text-xs text-gray-400 mt-2">
                    Will search on multiple job platforms for: "{job.title} at {job.company}"
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      );
    };

    const LearningPathView = () => (
      <div className="space-y-6">
        <h2 className="text-3xl font-bold text-white mb-8">Personalized Learning Path</h2>
        
        <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border border-white/20">
          <h3 className="text-2xl font-bold text-cyan-400 mb-6">Recommended Skills to Master</h3>
          <p className="text-gray-300 mb-8">
            Based on top job matches, here are the skills that will boost your career prospects:
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {learningRecs.map((rec, index) => (
              <div key={index} className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-2xl p-6 border border-purple-500/30 hover:border-purple-400/50 transition-all duration-300">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-xl font-bold text-white">{rec.skill}</h4>
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    rec.priority === 'high' 
                      ? 'bg-red-500/20 text-red-300 border border-red-500/30' 
                      : 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30'
                  }`}>
                    {rec.priority} priority
                  </span>
                </div>
                
                <p className="text-gray-300 text-sm mb-6">
                  Master this skill to increase your job match scores and unlock better opportunities.
                </p>
                
                <a
                  href={rec.google_search_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block w-full px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl hover:from-green-600 hover:to-emerald-600 transition-all duration-300 font-semibold text-center"
                >
                  🔍 Find Courses
                </a>
              </div>
            ))}
          </div>
        </div>
      </div>
    );

    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-8">
        <div className="max-w-7xl mx-auto">
          {/* Navigation */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-2 mb-8 border border-white/20">
            <div className="flex space-x-2">
              {[
                { id: 'profile', label: 'Profile', icon: '👤' },
                { id: 'jobs', label: 'Job Matches', icon: '💼' },
                { id: 'learning', label: 'Learning Path', icon: '🎓' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 px-6 py-4 rounded-xl font-semibold transition-all duration-300 ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white'
                      : 'text-gray-300 hover:text-white hover:bg-white/10'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Content */}
          {activeTab === 'profile' && <ProfileView />}
          {activeTab === 'jobs' && <JobMatchesView />}
          {activeTab === 'learning' && <LearningPathView />}
        </div>
      </div>
    );
  };

  return (
    <div className="App">
      {currentView === 'upload' ? <FileUploadZone /> : <Dashboard />}
    </div>
  );
}

export default App;