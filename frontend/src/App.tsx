/**
 * Main App component
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store';
import { HomePage } from './pages/HomePage';
import { CallPage } from './pages/CallPage';
import { HistoryPage } from './pages/HistoryPage';
import { CallDetailPage } from './pages/CallDetailPage';
import './styles/global.css';

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/call/:callId" element={<CallPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/call-detail/:callId" element={<CallDetailPage />} />
        </Routes>
      </Router>
    </Provider>
  );
};

export default App;
