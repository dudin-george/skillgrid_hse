import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { OryProvider } from './context/OryContext';
import LandingPage from './pages/LandingPage';

const App: React.FC = () => {
  return (
    <OryProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
        </Routes>
      </BrowserRouter>
    </OryProvider>
  );
};

export default App;
