import React from 'react';
import { Link, Outlet } from 'react-router-dom';
import { useOry } from '../context/OryContext';

const Layout: React.FC = () => {
  const { isAuthenticated, isLoading, login, signup, logout } = useOry();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex flex-col">
      {/* Navigation */}
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="text-2xl font-bold text-primary">SkillGrid</Link>
            </div>
            <div className="flex items-center space-x-4">
              {isLoading ? (
                <div className="text-primary">Loading...</div>
              ) : isAuthenticated ? (
                <button 
                  onClick={logout} 
                  className="px-4 py-2 rounded bg-primary text-white hover:bg-primary-dark transition"
                >
                  Sign Out
                </button>
              ) : (
                <>
                  <button 
                    onClick={login} 
                    className="px-4 py-2 rounded text-primary hover:bg-gray-100 transition"
                  >
                    Sign In
                  </button>
                  <button 
                    onClick={signup} 
                    className="px-4 py-2 rounded bg-primary text-white hover:bg-primary-dark transition"
                  >
                    Sign Up
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-grow">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout; 