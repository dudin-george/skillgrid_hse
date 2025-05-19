import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useOry } from '../context/OryContext';

// Sample job data (in a real app, this would come from an API)
const sampleJobs = [
  {
    id: 1,
    title: "Full Stack Developer",
    company: "TechSolutions Inc.",
    salaryRange: "$3,500 - $4,800 / month",
    level: "Mid-Level"
  },
  {
    id: 2,
    title: "UI/UX Designer",
    company: "Creative Minds",
    salaryRange: "$2,800 - $3,600 / month",
    level: "Junior"
  },
  {
    id: 3,
    title: "DevOps Engineer",
    company: "Cloud Systems",
    salaryRange: "$4,200 - $5,500 / month",
    level: "Senior"
  },
  {
    id: 4,
    title: "Data Scientist",
    company: "Insight Analytics",
    salaryRange: "$3,800 - $4,900 / month",
    level: "Mid-Level"
  },
  {
    id: 5,
    title: "Mobile App Developer",
    company: "AppWorks",
    salaryRange: "$3,200 - $4,300 / month",
    level: "Mid-Level"
  }
];

const VacanciesPage: React.FC = () => {
  const { isLoading } = useOry();
  const navigate = useNavigate();

  // In a real application, you would check authentication with an API call
  // and redirect to home if not authenticated
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check authentication status with backend
        const response = await fetch('https://api.skillgrid.tech/auth', {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          }
        });
        
        // If not authenticated, redirect to home
        if (!response.ok) {
          navigate('/');
        }
      } catch (error) {
        console.error('Authentication check failed:', error);
        // On error, it's safer to redirect to home
        navigate('/');
      }
    };
    
    // Only check auth when component mounts and not loading
    if (!isLoading) {
      checkAuth();
    }
  }, [isLoading, navigate]);

  const goToProfile = () => {
    // Will be implemented in the future
    console.log('Navigate to profile page');
    // navigate('/profile');
  };

  const viewJobDetails = (jobId: number) => {
    navigate(`/vacancy/${jobId}`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      {/* Navigation Bar - Fixed to top */}
      <nav className="bg-white shadow-sm fixed top-0 left-0 right-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <span 
                className="text-2xl font-bold text-gray-900 cursor-pointer"
                onClick={() => navigate('/')}
              >
                SkillGrid
              </span>
            </div>
            <div className="flex items-center">
              <button
                onClick={goToProfile}
                className="px-4 py-2 rounded-md bg-blue-600 text-white font-medium hover:bg-blue-700 transition"
              >
                My Profile
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content with padding top to account for fixed navbar */}
      <div className="pt-24 pb-16 px-4">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl font-bold text-center text-gray-900 mb-8">
            Available Job Opportunities
          </h1>

          {/* Job Listings */}
          <div className="space-y-6">
            {sampleJobs.map(job => (
              <div 
                key={job.id} 
                className="bg-white rounded-lg shadow-sm p-6 transition duration-300 hover:shadow-md"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-xl font-bold text-gray-900 mb-1">{job.title}</h2>
                    <p className="text-gray-600 mb-3">{job.company}</p>
                    
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center text-gray-700">
                        <svg className="w-5 h-5 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span>{job.salaryRange}</span>
                      </div>
                      
                      <div className="flex items-center text-gray-700">
                        <svg className="w-5 h-5 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                        <span>{job.level}</span>
                      </div>
                    </div>
                  </div>
                  
                  <button 
                    onClick={() => viewJobDetails(job.id)}
                    className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition"
                  >
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Simplified Footer */}
      <footer className="bg-gray-100 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-center">
            <p className="text-gray-600 text-center">© 2025 SkillGrid. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default VacanciesPage; 