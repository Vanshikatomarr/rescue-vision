import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { DetectionPage } from './pages/DetectionPage';
import { IncidentsPage } from './pages/IncidentsPage';
import { TrainingPage } from './pages/TrainingPage';
import { ModelsPage } from './pages/ModelsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { SettingsPage } from './pages/SettingsPage';
import { RescuePlannerPage } from './pages/RescuePlannerPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/detect" element={<DetectionPage />} />
          <Route path="/incidents" element={<IncidentsPage />} />
          <Route path="/training" element={<TrainingPage />} />
          <Route path="/models" element={<ModelsPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/routes" element={<RescuePlannerPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
