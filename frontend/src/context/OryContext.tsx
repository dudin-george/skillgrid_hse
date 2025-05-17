import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { Configuration, FrontendApi, Session, Identity } from '@ory/client';

// Define our own user info type
interface UserInfo {
  id: string;
  traits?: {
    email?: string;
    name?: string;
    username?: string;
    [key: string]: any;
  };
}

interface OryContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  userInfo: UserInfo | null;
  login: () => void;
  signup: () => void;
  logout: () => void;
}

const OryContext = createContext<OryContextType | undefined>(undefined);

// Ory project configuration
const ORY_SDK_URL = process.env.REACT_APP_ORY_URL || "https://auth.skillgrid.tech";
const ORY_PROJECT_ID = "cd3eac85-ed95-41dd-9969-9012ab8dea73";

// Get current origin for debugging
const CURRENT_ORIGIN = window.location.origin;

// Do not use return_to parameter directly - we'll handle redirection within the app
// after successful authentication instead of relying on Ory's redirect

export const OryProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [corsError, setCorsError] = useState<boolean>(false);

  // Create Ory client with improved configuration
  const ory = new FrontendApi(
    new Configuration({
      basePath: ORY_SDK_URL,
      baseOptions: {
        withCredentials: true,
        headers: {
          'X-Ory-Project-Id': ORY_PROJECT_ID,
          'Origin': CURRENT_ORIGIN
        }
      }
    })
  );

  useEffect(() => {
    // Check if we're returning from Ory with a flow ID
    const url = new URL(window.location.href);
    const flowId = url.searchParams.get('flow');
    
    // Check if we've just returned from an Ory authentication flow
    const isReturningFromOry = () => {
      // Check for common return parameters from Ory
      const fromOry = url.searchParams.has('flow') || 
                     url.searchParams.has('id') || 
                     url.pathname.includes('/dashboard') &&
                     document.referrer.includes('auth.skillgrid.tech');
      
      if (fromOry) {
        console.log('Detected return from Ory authentication flow');
      }
      
      return fromOry;
    };
    
    // Check session on mount with retry
    const checkSession = async (retryCount = 0) => {
      try {
        // If returning from Ory, wait a bit longer before the first attempt
        // to allow cookies to be properly set
        if (retryCount === 0 && isReturningFromOry() && !flowId) {
          console.log('Returning from Ory flow, delaying first session check...');
          setTimeout(() => checkSession(retryCount), 1500);
          return;
        }
        
        console.log(`Checking session from origin: ${CURRENT_ORIGIN} (attempt ${retryCount + 1})`);
        console.log(`Using Ory SDK URL: ${ORY_SDK_URL}`);
        console.log('Sending request with credentials and headers:', {
          withCredentials: true,
          'X-Ory-Project-Id': ORY_PROJECT_ID,
          'Origin': CURRENT_ORIGIN
        });
        
        const { data } = await ory.toSession();
        setIsAuthenticated(!!data.active);
        setCorsError(false);
        
        if (data.identity) {
          const identity = data.identity as Identity;
          // Convert to our UserInfo format
          setUserInfo({
            id: identity.id,
            traits: identity.traits as UserInfo['traits']
          });
          console.log("Session active, user authenticated");
        } else {
          console.log("Session checked, but no active identity found");
        }
      } catch (error: any) {
        console.error(`Session check failed (attempt ${retryCount + 1}):`, error);
        
        // Check if this is a CORS error
        if (error.message && error.message.includes('NetworkError')) {
          console.error('Possible CORS issue detected. Make sure your domain is allowed in Ory CORS settings');
          setCorsError(true);
        }
        
        // Retry logic - wait and retry if we haven't exceeded max retries
        if (retryCount < 2) { // Try up to 3 times total
          console.log(`Retrying session check in 1 second... (${retryCount + 1}/3)`);
          setTimeout(() => checkSession(retryCount + 1), 1000);
          return; // Exit early, don't update state yet
        }
        
        setIsAuthenticated(false);
        setUserInfo(null);
      } finally {
        if (retryCount === 2 || !corsError) { // Only set loading to false on final attempt or success
          setIsLoading(false);
        }
      }
    };
    
    checkSession();
  }, []);

  const login = () => {
    // Redirect to the Ory login page with return_to parameter
    const returnUrl = `${CURRENT_ORIGIN}/dashboard`;
    
    // Add a timestamp to avoid caching issues
    const timestamp = new Date().getTime();
    
    // Clear any existing session cookies before redirecting
    document.cookie = "ory_kratos_session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    
    // Redirect to Ory login
    console.log(`Redirecting to login: ${ORY_SDK_URL}/ui/login?project=${ORY_PROJECT_ID}&return_to=${encodeURIComponent(returnUrl)}&t=${timestamp}`);
    window.location.href = `${ORY_SDK_URL}/ui/login?project=${ORY_PROJECT_ID}&return_to=${encodeURIComponent(returnUrl)}&t=${timestamp}`;
  };

  const signup = () => {
    // Redirect to the Ory registration page with return_to parameter
    const returnUrl = `${CURRENT_ORIGIN}/dashboard`;
    
    // Add a timestamp to avoid caching issues
    const timestamp = new Date().getTime();
    
    // Clear any existing session cookies before redirecting
    document.cookie = "ory_kratos_session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    
    // Redirect to Ory registration
    console.log(`Redirecting to signup: ${ORY_SDK_URL}/ui/registration?project=${ORY_PROJECT_ID}&return_to=${encodeURIComponent(returnUrl)}&t=${timestamp}`);
    window.location.href = `${ORY_SDK_URL}/ui/registration?project=${ORY_PROJECT_ID}&return_to=${encodeURIComponent(returnUrl)}&t=${timestamp}`;
  };

  const logout = async () => {
    try {
      const { data } = await ory.createBrowserLogoutFlow();
      window.location.href = data.logout_url;
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  // If CORS error detected, show instructions in browser console
  useEffect(() => {
    if (corsError) {
      console.error(`
=======================================================================
CORS ERROR DETECTED: Unable to connect to auth.skillgrid.tech

This application uses a proxy domain (auth.skillgrid.tech) to communicate with Ory.
If you're seeing this error, please check:

1. Browser Console: Look for specific CORS error messages
   - Check if preflight OPTIONS requests are failing
   - Look for missing Access-Control-Allow-Origin headers

2. Ory CORS Configuration:
   - Verify that https://skillgrid.tech is in the allowed_origins list
   - Ensure allow_credentials is set to true
   - Check that all necessary headers are included

3. Try clearing browser cache and cookies:
   - Delete all cookies for skillgrid.tech and auth.skillgrid.tech
   - Clear browser cache completely

4. Try using Chrome or Firefox, as Safari has stricter CORS policies

For developers: Run the test-ory-conn.sh script to diagnose connection issues.
=======================================================================
      `);
    }
  }, [corsError]);

  return (
    <OryContext.Provider value={{ isAuthenticated, isLoading, userInfo, login, signup, logout }}>
      {children}
    </OryContext.Provider>
  );
};

export const useOry = (): OryContextType => {
  const context = useContext(OryContext);
  if (context === undefined) {
    throw new Error('useOry must be used within an OryProvider');
  }
  return context;
}; 