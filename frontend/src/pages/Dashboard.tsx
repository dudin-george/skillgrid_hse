import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useOry } from '../context/OryContext';

const Dashboard: React.FC = () => {
  const { isAuthenticated, isLoading, userInfo } = useOry();
  const navigate = useNavigate();
  const [retryCount, setRetryCount] = useState(0);
  
  // Redirect to home if not authenticated, with retry logic
  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        console.log('User authenticated, showing dashboard');
      } else {
        if (retryCount < 3) {
          // Try a few times before redirecting, as session might be loading
          console.log(`Not authenticated, retry ${retryCount + 1}/3`);
          const timer = setTimeout(() => {
            setRetryCount(prev => prev + 1);
          }, 1000);
          return () => clearTimeout(timer);
        } else {
          console.log('Authentication failed after retries, redirecting to home');
          navigate('/');
        }
      }
    }
  }, [isLoading, isAuthenticated, navigate, retryCount]);

  if (isLoading || (!isAuthenticated && retryCount < 3)) {
    return (
      <div className="flex justify-center items-center min-h-[calc(100vh-4rem)]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Checking authentication...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect via the useEffect
  }

  // Extract user email
  const userEmail = userInfo?.traits?.email || 'No email found';

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] bg-gradient-to-b from-gray-50 to-gray-100 px-4">
      <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
        <h1 className="text-2xl font-bold text-gray-900 mb-4 text-center">Welcome!</h1>
        <p className="text-lg text-gray-700 mb-6 text-center">
          You are authenticated as:
        </p>
        <div className="bg-gray-100 p-4 rounded-md text-center font-mono break-all">
          {userEmail}
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 