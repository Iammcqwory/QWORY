import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { ChatProvider } from './context/ChatContext';
import { SettingsProvider } from './context/SettingsContext';
import Layout from './components/Layout';
import ChatPage from './pages/ChatPage';
import SettingsPage from './pages/SettingsPage';

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <SettingsProvider>
        <ChatProvider>
          <Router>
            <Layout>
              <Routes>
                <Route path="/" element={<ChatPage />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Routes>
            </Layout>
          </Router>
        </ChatProvider>
      </SettingsProvider>
    </ThemeProvider>
  );
};

export default App;
