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
const ORY_SDK_URL = process.env.REACT_APP_ORY_URL || "https://infallible-shaw-gpsjwuc0lg.projects.oryapis.com";
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
    
    // Check session on mount
    const checkSession = async () => {
      try {
        console.log(`Checking session from origin: ${CURRENT_ORIGIN}`);
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
        }
      } catch (error: any) {
        console.error('Session check failed:', error);
        
        // Check if this is a CORS error
        if (error.message && error.message.includes('NetworkError')) {
          console.error('Possible CORS issue detected. Make sure your domain is allowed in Ory CORS settings');
          setCorsError(true);
        }
        
        setIsAuthenticated(false);
        setUserInfo(null);
      } finally {
        setIsLoading(false);
      }
    };
    
    checkSession();
  }, []);

  const login = () => {
    // Redirect to the Ory login page with return_to parameter
    const returnUrl = `${CURRENT_ORIGIN}/dashboard`;
    window.location.href = `${ORY_SDK_URL}/ui/login?project=${ORY_PROJECT_ID}&return_to=${encodeURIComponent(returnUrl)}`;
  };

  const signup = () => {
    // Redirect to the Ory registration page with return_to parameter
    const returnUrl = `${CURRENT_ORIGIN}/dashboard`;
    window.location.href = `${ORY_SDK_URL}/ui/registration?project=${ORY_PROJECT_ID}&return_to=${encodeURIComponent(returnUrl)}`;
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
CORS ERROR DETECTED: Your domain (${CURRENT_ORIGIN}) is not allowed in Ory CORS settings

Please update your Ory CORS configuration to include this domain:
1. Go to https://console.ory.sh/
2. Select project with ID: ${ORY_PROJECT_ID}
3. Navigate to Configuration → CORS
4. Add "${CURRENT_ORIGIN}" to allowed_origins list
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