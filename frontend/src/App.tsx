import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { OryProvider } from './context/OryContext';
import LandingPage from './pages/LandingPage';
import VacanciesPage from './pages/VacanciesPage';
import VacancyDetailsPage from './pages/VacancyDetailsPage';
import AssessmentPage from './pages/AssessmentPage';
import AssessmentResultsPage from './pages/AssessmentResultsPage';

const App: React.FC = () => {
  return (
    <OryProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/vacancies" element={<VacanciesPage />} />
          <Route path="/vacancy/:vacancyId" element={<VacancyDetailsPage />} />
          <Route path="/assessment" element={<AssessmentPage />} />
          <Route path="/assessment-results" element={<AssessmentResultsPage />} />
        </Routes>
      </BrowserRouter>
    </OryProvider>
  );
};

export default App;
