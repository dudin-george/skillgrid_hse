import React from 'react';

const Home: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] bg-gradient-to-b from-gray-50 to-gray-100 px-4">
      <div className="text-center">
        <img 
          src="/hero-image.svg" 
          alt="SkillGrid Logo" 
          className="w-64 h-64 mx-auto mb-8"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = "https://via.placeholder.com/256x256?text=SkillGrid";
          }}
        />
        <h1 className="text-5xl font-bold text-primary mb-12">SkillGrid</h1>
        
        <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 justify-center">
          <button className="px-8 py-3 rounded-lg bg-primary text-white font-medium hover:bg-primary-dark transition min-w-[150px]">
            Sign In
          </button>
          <button className="px-8 py-3 rounded-lg border border-gray-300 bg-white text-gray-700 font-medium hover:bg-gray-50 transition min-w-[150px]">
            Sign Up
          </button>
        </div>
      </div>
    </div>
  );
};

export default Home; 