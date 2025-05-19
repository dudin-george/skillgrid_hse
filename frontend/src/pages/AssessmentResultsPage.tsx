import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useOry } from '../context/OryContext';

// Sample assessment result data structure
const sampleAssessmentResults = {
  "Python": {
    overallScore: 78,
    skills: {
      "Data Types": {
        score: 92,
        subskills: ["int", "float", "string", "bool", "list", "tuple", "dict", "set", "NoneType"]
      },
      "Control Flow": {
        score: 85,
        subskills: ["if", "else", "elif", "match", "ternary operator"]
      },
      "Loops": {
        score: 80,
        subskills: ["for", "while", "break", "continue", "enumerate", "zip"]
      },
      "Functions": {
        score: 75,
        subskills: ["def", "return", "lambda", "args", "kwargs", "recursion"]
      },
      "Classes/OOP": {
        score: 65,
        subskills: ["class", "__init__", "self", "inheritance", "encapsulation", "staticmethod", "classmethod"]
      }
    }
  },
  "FastAPI": {
    overallScore: 72,
    skills: {
      "Routing": {
        score: 88,
        subskills: ["@app.get", "@app.post", "path parameters", "query parameters"]
      },
      "Request Handling": {
        score: 75,
        subskills: ["Request body", "pydantic models", "Form data", "File uploads"]
      },
      "Responses": {
        score: 82,
        subskills: ["Response model", "status_code", "JSONResponse", "RedirectResponse"]
      },
      "Validation": {
        score: 62,
        subskills: ["pydantic validation", "Field constraints", "Custom validators"]
      }
    }
  },
  "SQL": {
    overallScore: 85,
    skills: {
      "Basic Queries": {
        score: 95,
        subskills: ["SELECT", "FROM", "WHERE", "ORDER BY", "LIMIT", "OFFSET"]
      },
      "Filtering": {
        score: 90,
        subskills: ["AND", "OR", "NOT", "IN", "BETWEEN", "LIKE"]
      },
      "Joins": {
        score: 82,
        subskills: ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"]
      },
      "Grouping/Aggregation": {
        score: 78,
        subskills: ["GROUP BY", "HAVING", "COUNT", "SUM", "AVG", "MIN", "MAX"]
      }
    }
  }
};

const AssessmentResultsPage: React.FC = () => {
  const { isLoading } = useOry();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [assessmentData, setAssessmentData] = useState(sampleAssessmentResults);

  // In a real application, you would fetch assessment results from an API
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
        
        // In a real app, you would fetch assessment results here
        // For now, we just simulate a network request
        setTimeout(() => {
          setAssessmentData(sampleAssessmentResults);
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
  }, [isLoading, navigate]);

  const goToProfile = () => {
    // Will be implemented in the future
    console.log('Navigate to profile page');
  };

  const goToVacancies = () => {
    navigate('/vacancies');
  };

  // Helper function to get color intensity based on score
  const getColorIntensity = (score: number) => {
    if (score >= 90) return 'bg-blue-600';
    if (score >= 80) return 'bg-blue-500';
    if (score >= 70) return 'bg-blue-400';
    if (score >= 60) return 'bg-blue-300';
    return 'bg-blue-200';
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
          {/* Congratulations Section */}
          <div className="bg-white rounded-lg shadow-sm p-8 mb-8 text-center">
            <div className="flex justify-center mb-4">
              <div className="w-20 h-20 rounded-full bg-blue-100 flex items-center justify-center">
                <svg className="w-12 h-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Congratulations!</h1>
            <p className="text-xl text-gray-600">You've successfully completed the assessment. Great job!</p>
          </div>

          {/* Performance Breakdown Section */}
          <div className="bg-white rounded-lg shadow-sm p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Your Performance</h2>
            
            {/* Loop through domains */}
            <div className="space-y-10">
              {Object.entries(assessmentData).map(([domain, domainData]) => (
                <div key={domain} className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xl font-semibold text-gray-800">{domain}</h3>
                    <span className="text-lg font-medium text-gray-600">{domainData.overallScore}%</span>
                  </div>
                  
                  {/* Domain overall score */}
                  <div className="h-6 w-full bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${getColorIntensity(domainData.overallScore)} rounded-full flex items-center justify-end pr-2`} 
                      style={{ width: `${domainData.overallScore}%` }}
                    >
                      <span className="text-white text-sm font-semibold">{domainData.overallScore}%</span>
                    </div>
                  </div>
                  
                  {/* Skills within this domain */}
                  <div className="pl-4 space-y-6">
                    {Object.entries(domainData.skills).map(([skill, skillData]) => (
                      <div key={skill} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <h4 className="text-lg font-medium text-gray-700">{skill}</h4>
                          <span className="text-md font-medium text-gray-600">{skillData.score}%</span>
                        </div>
                        
                        {/* Skill score */}
                        <div className="h-5 w-full bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className={`h-full ${getColorIntensity(skillData.score)} rounded-full flex items-center justify-end pr-2`} 
                            style={{ width: `${skillData.score}%` }}
                          >
                            <span className="text-white text-xs font-semibold">{skillData.score}%</span>
                          </div>
                        </div>
                        
                        {/* Subskills */}
                        <div className="pl-4 py-2">
                          <p className="text-sm text-gray-500">
                            <span className="font-medium">Covered topics:</span> {skillData.subskills.join(", ")}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Call-to-action Button */}
          <div className="flex justify-center pt-4">
            <button
              onClick={goToVacancies}
              className="px-8 py-3 text-lg bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 transition shadow-md"
            >
              Go to Job Listings
            </button>
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

export default AssessmentResultsPage; 