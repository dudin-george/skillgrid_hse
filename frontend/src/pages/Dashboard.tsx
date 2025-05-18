import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useOry } from '../context/OryContext';

interface UserTraits {
  email?: string;
  name?: string;
  surname?: string;
  person_type?: 'candidate' | 'recruiter';
  [key: string]: any;
}

interface UserData {
  id?: string;
  traits?: UserTraits;
  [key: string]: any;
}

const Dashboard: React.FC = () => {
  const { isLoading: oryIsLoading } = useOry(); // Only used for initial loading state
  const navigate = useNavigate();
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        console.log('Directly fetching user data from API without prior authentication check...');
        
        // Don't check isAuthenticated from Ory context - just try the API directly
        // The backend will handle authentication via the cookie
        const response = await fetch('https://api.skillgrid.tech/auth', {
          method: 'GET',
          credentials: 'include', // Important to include cookies
          headers: {
            'Content-Type': 'application/json',
          }
        });
        
        console.log('API response status:', response.status);
        
        if (!response.ok) {
          // For debugging - try to get response text even when not ok
          const errorText = await response.text();
          console.error('API error response:', errorText);
          
          // If unauthorized (401) or forbidden (403), redirect to home
          if (response.status === 401 || response.status === 403) {
            console.log('Not authenticated according to backend, redirecting to home');
            navigate('/');
            return;
          }
          
          throw new Error(`API error: ${response.status} - ${errorText || 'No response body'}`);
        }
        
        const data = await response.json();
        console.log('Received user data:', data);
        setUserData(data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching user data:', err);
        
        // Try alternative API URL with http if https failed
        try {
          console.log('Trying alternative API URL...');
          const altResponse = await fetch('http://api.skillgrid.tech/auth', {
            method: 'GET',
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json',
            }
          });
          
          if (altResponse.ok) {
            const data = await altResponse.json();
            console.log('Received user data from alternative URL:', data);
            setUserData(data);
            setLoading(false);
            return;
          } else if (altResponse.status === 401 || altResponse.status === 403) {
            // If unauthorized, redirect to home
            console.log('Not authenticated according to backend (alt URL), redirecting to home');
            navigate('/');
            return;
          }
        } catch (altErr) {
          console.error('Alternative API request also failed:', altErr);
        }
        
        // If all attempts failed, set error
        setError(err instanceof Error ? err.message : 'Unknown error occurred');
        setLoading(false);
      }
    };

    // Only start fetching when the component is fully mounted
    fetchUserData();
  }, [navigate]); // Removed isAuthenticated dependency

  // Create dummy data for testing if needed
  const createDummyData = () => {
    const dummyData: UserData = {
      id: "test-user-id",
      traits: {
        email: "test@example.com",
        name: "Test",
        surname: "User",
        person_type: "candidate"
      }
    };
    setUserData(dummyData);
    setLoading(false);
    setError(null);
  };

  // Show loading state
  if (oryIsLoading || loading) {
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
          <div className="flex flex-col space-y-2">
            <button 
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark transition"
            >
              Try Again
            </button>
            <button 
              onClick={() => navigate('/')}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition"
            >
              Return to Home
            </button>
            {/* For development/testing only */}
            <button 
              onClick={createDummyData}
              className="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition"
            >
              Use Test Data
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Extract user traits from the response
  const userTraits = userData?.traits || {};
  const userId = userData?.id || '';

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
                {(userTraits.name || userTraits.surname) && (
                  <p className="mb-1">
                    <span className="font-medium">Name:</span> {[userTraits.name, userTraits.surname].filter(Boolean).join(' ') || 'Not provided'}
                  </p>
                )}
                <p className="mb-1"><span className="font-medium">Email:</span> {userTraits.email || 'Not provided'}</p>
                <p className="mb-1"><span className="font-medium">Account Type:</span> {
                  userTraits.person_type 
                    ? userTraits.person_type.charAt(0).toUpperCase() + userTraits.person_type.slice(1) 
                    : 'Not specified'
                }</p>
                <p><span className="font-medium">ID:</span> {userId}</p>
              </div>
            </div>
            
            {/* Display any additional user traits that might be returned */}
            {Object.entries(userTraits)
              .filter(([key]) => !['email', 'person_type', 'name', 'surname'].includes(key))
              .length > 0 && (
              <div>
                <h2 className="text-lg font-semibold text-gray-700 mb-2">Additional Information</h2>
                <div className="bg-gray-100 p-4 rounded-md">
                  {Object.entries(userTraits)
                    .filter(([key]) => !['email', 'person_type', 'name', 'surname'].includes(key))
                    .map(([key, value]) => (
                      <p key={key} className="mb-1">
                        <span className="font-medium">{key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')}:</span>{' '}
                        {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                      </p>
                    ))}
                </div>
              </div>
            )}
            
            {/* Display non-trait properties from the response */}
            {Object.entries(userData)
              .filter(([key]) => !['id', 'traits'].includes(key))
              .length > 0 && (
              <div>
                <h2 className="text-lg font-semibold text-gray-700 mb-2">Response Metadata</h2>
                <div className="bg-gray-100 p-4 rounded-md">
                  {Object.entries(userData)
                    .filter(([key]) => !['id', 'traits'].includes(key))
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