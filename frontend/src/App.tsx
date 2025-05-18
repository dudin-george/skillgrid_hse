import React from 'react';
import { OryProvider } from './context/OryContext';

const EmptySlate: React.FC = () => {
  return (
    <div className="flex justify-center items-center min-h-screen bg-gradient-to-br from-gray-100 to-gray-200">
      <div className="text-center p-8 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">SkillGrid</h1>
        <p className="text-gray-600">Ready for redesign</p>
      </div>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <OryProvider>
      <EmptySlate />
    </OryProvider>
  );
};

export default App;
