import React from 'react';
import ModelSettings from '../components/settings/ModelSettings';

const SettingsPage: React.FC = () => {
  return (
    <div className="max-w-2xl mx-auto p-4">
      <h2 className="text-2xl font-bold mb-6">Settings</h2>
      
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mb-6">
        <h3 className="text-xl font-semibold mb-4">Model Configuration</h3>
        <ModelSettings />
      </div>
      
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mb-6">
        <h3 className="text-xl font-semibold mb-4">About</h3>
        <p className="mb-2">
          Qwory is an open-source AI agent framework designed for task automation.
        </p>
        <p className="mb-2">
          This web UI allows you to interact with Qwory agents using various model providers,
          including locally-hosted models via Ollama.
        </p>
        <p>
          <a 
            href="https://github.com/yourusername/qwory" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-500 hover:underline"
          >
            View on GitHub
          </a>
        </p>
      </div>
    </div>
  );
};

export default SettingsPage; 