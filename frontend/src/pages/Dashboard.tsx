import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useOry } from '../context/OryContext';

interface UserData {
  id: string;
  email?: string;
  name?: string;
  surname?: string;
  person_type?: 'candidate' | 'recruiter';
  [key: string]: any;
}

const Dashboard: React.FC = () => {
  const { isAuthenticated, isLoading } = useOry();
  const navigate = useNavigate();
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        // Check if there's an active session first
        if (!isLoading && !isAuthenticated) {
          // Not authenticated, redirect to home
          navigate('/');
          return;
        }
        
        // If authenticated, fetch user data from the API
        const response = await fetch('https://api.skillgrid.tech/auth', {
          method: 'GET',
          credentials: 'include', // Important to include cookies
          headers: {
            'Content-Type': 'application/json',
          }
        });
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        setUserData(data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching user data:', err);
        setError(err instanceof Error ? err.message : 'Unknown error occurred');
        setLoading(false);
      }
    };

    fetchUserData();
  }, [isAuthenticated, isLoading, navigate]);

  // Show loading state
  if (isLoading || loading) {
    return (
      <div className="flex justify-center items-center min-h-[calc(100vh-4rem)]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Loading your profile...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="flex justify-center items-center min-h-[calc(100vh-4rem)]">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md w-full">
          <h2 className="text-xl font-semibold text-red-700 mb-2">Error Loading Profile</h2>
          <p className="text-gray-700 mb-4">{error}</p>
          <button 
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark transition"
          >
            Return to Home
          </button>
        </div>
      </div>
    );
  }

  // Show the user data
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] bg-gradient-to-b from-gray-50 to-gray-100 px-4">
      <div className="bg-white p-8 rounded-lg shadow-md max-w-lg w-full">
        <h1 className="text-2xl font-bold text-gray-900 mb-6 text-center">Your Profile</h1>
        
        {userData ? (
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-700 mb-2">User Information</h2>
              <div className="bg-gray-100 p-4 rounded-md">
                {/* Display full name if available */}
                {(userData.name || userData.surname) && (
                  <p className="mb-1">
                    <span className="font-medium">Name:</span> {[userData.name, userData.surname].filter(Boolean).join(' ') || 'Not provided'}
                  </p>
                )}
                <p className="mb-1"><span className="font-medium">Email:</span> {userData.email || 'Not provided'}</p>
                <p className="mb-1"><span className="font-medium">Account Type:</span> {userData.person_type ? userData.person_type.charAt(0).toUpperCase() + userData.person_type.slice(1) : 'Not specified'}</p>
                <p><span className="font-medium">ID:</span> {userData.id}</p>
              </div>
            </div>
            
            {/* Display any additional user traits that might be returned */}
            {Object.entries(userData)
              .filter(([key]) => !['id', 'email', 'person_type', 'name', 'surname'].includes(key))
              .length > 0 && (
              <div>
                <h2 className="text-lg font-semibold text-gray-700 mb-2">Additional Information</h2>
                <div className="bg-gray-100 p-4 rounded-md">
                  {Object.entries(userData)
                    .filter(([key]) => !['id', 'email', 'person_type', 'name', 'surname'].includes(key))
                    .map(([key, value]) => (
                      <p key={key} className="mb-1">
                        <span className="font-medium">{key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')}:</span>{' '}
                        {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                      </p>
                    ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <p className="text-center text-gray-500">No user data available</p>
        )}
      </div>
    </div>
  );
};

export default Dashboard; 