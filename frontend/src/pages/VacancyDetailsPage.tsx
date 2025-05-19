import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useOry } from '../context/OryContext';

// Sample job data (in a real app, this would come from an API)
const sampleVacancyDetails = {
  id: 1,
  title: "Backend Developer",
  company: "TechNova",
  salaryRange: "$2,500 – $3,200 / month",
  experienceRequired: "1–2 years",
  location: "Remote",
  benefits: "Flexible hours, Education budget, Health insurance",
  description: "As a Backend Developer at TechNova, you will be responsible for developing and maintaining our server-side applications. You will work closely with frontend developers, product managers, and UX designers to build scalable and efficient APIs and services.",
  aboutCompany: "TechNova is a leading technology company focused on innovative cloud solutions for businesses of all sizes.",
  requirements: [
    "Proficiency in Python and Django/Flask",
    "1+ year experience with SQL and database design",
    "Experience with RESTful API design",
    "Knowledge of Git version control",
    "Basic understanding of frontend technologies (HTML, CSS, JavaScript)"
  ],
  workConditions: [
    "Remote work",
    "40 hours/week",
    "Flexible schedule",
    "Quarterly team meetups",
    "Personal development time"
  ],
  assessmentCompleted: false
};

const VacancyDetailsPage: React.FC = () => {
  const { vacancyId } = useParams<{ vacancyId: string }>();
  const { isLoading } = useOry();
  const navigate = useNavigate();
  const [vacancy, setVacancy] = useState(sampleVacancyDetails);
  const [loading, setLoading] = useState(true);

  // In a real application, you would fetch vacancy details from an API
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
          return;
        }
        
        // In a real app, you would fetch vacancy details here
        // For now, we just simulate a network request
        setTimeout(() => {
          // Map vacancy IDs to different job titles for a more realistic demo
          let vacancyTitle = "Backend Developer";
          let vacancyCompany = "TechNova";
          
          const id = parseInt(vacancyId || '1', 10);
          
          // Match with sample jobs from VacanciesPage
          if (id === 1) {
            vacancyTitle = "Full Stack Developer";
            vacancyCompany = "TechSolutions Inc.";
          } else if (id === 2) {
            vacancyTitle = "UI/UX Designer";
            vacancyCompany = "Creative Minds";
          } else if (id === 3) {
            vacancyTitle = "DevOps Engineer";
            vacancyCompany = "Cloud Systems";
          } else if (id === 4) {
            vacancyTitle = "Data Scientist";
            vacancyCompany = "Insight Analytics";
          } else if (id === 5) {
            vacancyTitle = "Mobile App Developer";
            vacancyCompany = "AppWorks";
          }
          
          setVacancy({
            ...sampleVacancyDetails,
            id: id,
            title: vacancyTitle,
            company: vacancyCompany
          });
          setLoading(false);
        }, 500);
        
      } catch (error) {
        console.error('Authentication check failed:', error);
        navigate('/');
      }
    };
    
    if (!isLoading) {
      checkAuth();
    }
  }, [isLoading, navigate, vacancyId]);

  const goToProfile = () => {
    // Will be implemented in the future
    console.log('Navigate to profile page');
  };

  const startAssessment = () => {
    console.log(`Starting general assessment`);
    // Navigate to the general assessment page
    navigate('/assessment');
  };

  const goBack = () => {
    navigate('/vacancies');
  };

  if (isLoading || loading) {
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
        <div className="max-w-4xl mx-auto">
          {/* Back button */}
          <div className="mb-4">
            <button 
              onClick={goBack}
              className="flex items-center text-blue-600 hover:text-blue-800"
            >
              <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Vacancies
            </button>
          </div>

          {/* Job Summary Card */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
            <div className="flex flex-col md:flex-row justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 mb-2">{vacancy.title}</h1>
                <p className="text-lg text-gray-600 mb-4">{vacancy.company}</p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-y-3 gap-x-6 mb-4">
                  <div className="flex items-center">
                    <svg className="w-5 h-5 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-gray-700">{vacancy.salaryRange}</span>
                  </div>
                  
                  <div className="flex items-center">
                    <svg className="w-5 h-5 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <span className="text-gray-700">Experience: {vacancy.experienceRequired}</span>
                  </div>
                  
                  <div className="flex items-center">
                    <svg className="w-5 h-5 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <span className="text-gray-700">{vacancy.location}</span>
                  </div>
                  
                  <div className="flex items-center">
                    <svg className="w-5 h-5 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                    <span className="text-gray-700">Benefits: <span className="text-gray-600">{vacancy.benefits}</span></span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Action Buttons */}
            <div className="flex flex-col space-y-3 mt-4">
              <div className="flex space-x-4">
                <button
                  onClick={startAssessment}
                  className="px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition"
                >
                  Start Assessment
                </button>
                <button
                  disabled={!vacancy.assessmentCompleted}
                  className={`px-4 py-2 rounded-md font-medium ${
                    vacancy.assessmentCompleted
                      ? 'bg-green-600 text-white hover:bg-green-700'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  } transition`}
                >
                  Apply
                </button>
              </div>
              <p className="text-sm text-gray-600">
                Complete the skills assessment to unlock application for all jobs
              </p>
            </div>
          </div>

          {/* Main Content Area */}
          <div className="space-y-8">
            {/* About the Job */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-3">About the Job</h2>
              <div className="bg-white rounded-lg shadow-sm p-6">
                <p className="text-gray-700">{vacancy.description}</p>
              </div>
            </section>

            {/* About the Company */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-3">About the Company</h2>
              <div className="bg-white rounded-lg shadow-sm p-6">
                <p className="text-gray-700">{vacancy.aboutCompany}</p>
              </div>
            </section>

            {/* Requirements */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-3">Requirements</h2>
              <div className="bg-white rounded-lg shadow-sm p-6">
                <ul className="list-disc pl-5 space-y-2 text-gray-700">
                  {vacancy.requirements.map((req, idx) => (
                    <li key={idx}>{req}</li>
                  ))}
                </ul>
              </div>
            </section>

            {/* Work Conditions */}
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-3">Work Conditions</h2>
              <div className="bg-white rounded-lg shadow-sm p-6">
                <ul className="list-disc pl-5 space-y-2 text-gray-700">
                  {vacancy.workConditions.map((condition, idx) => (
                    <li key={idx}>{condition}</li>
                  ))}
                </ul>
              </div>
            </section>
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

export default VacancyDetailsPage; 