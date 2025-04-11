import React from 'react';
import { useSettings } from '../../context/SettingsContext';

const ModelSettings: React.FC = () => {
  const { 
    settings, 
    updateSettings, 
    availableProviders, 
    availableModels,
    isLoading 
  } = useSettings();

  if (isLoading) {
    return (
      <div className="py-4">
        <div className="animate-pulse flex space-x-4">
          <div className="flex-1 space-y-4 py-1">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div className="space-y-2">
              <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded"></div>
              <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium mb-2">Model Provider</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {availableProviders.map(provider => (
            <button
              key={provider.id}
              className={`px-4 py-2 rounded-md border ${
                settings.provider === provider.id
                  ? 'bg-blue-100 border-blue-500 dark:bg-blue-900 dark:border-blue-500'
                  : 'border-gray-300 dark:border-gray-700'
              } ${provider.status !== 'available' ? 'opacity-50' : ''}`}
              onClick={() => updateSettings({ provider: provider.id as any })}
              disabled={provider.status !== 'available'}
              title={provider.status !== 'available' ? `Status: ${provider.status}` : ''}
            >
              {provider.name}
              {provider.status !== 'available' && (
                <span className="block text-xs mt-1 text-red-500">
                  {provider.status === 'no_api_key' ? 'Needs API Key' : 'Unavailable'}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-medium mb-2">Model</h3>
        <select
          className="w-full px-4 py-2 rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800"
          value={settings.model}
          onChange={(e) => updateSettings({ model: e.target.value })}
          aria-label="Select AI model"
        >
          {(availableModels[settings.provider] || []).map(model => (
            <option key={model.id} value={model.id}>
              {model.name}
            </option>
          ))}
        </select>
      </div>

      {(settings.provider === 'openai' || settings.provider === 'openrouter' || settings.provider === 'gemini') && (
        <div>
          <h3 className="text-lg font-medium mb-2">API Key</h3>
          <input
            type="password"
            className="w-full px-4 py-2 rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800"
            placeholder={`Enter your ${settings.provider === 'openai' ? 'OpenAI' : settings.provider === 'openrouter' ? 'OpenRouter' : 'Google AI'} API key`}
            value={settings.apiKey || ''}
            onChange={(e) => updateSettings({ apiKey: e.target.value })}
          />
          <p className="text-sm text-gray-500 mt-1">
            Your API key is stored locally and never sent to our servers.
          </p>
        </div>
      )}

      {settings.provider === 'ollama' && (
        <div>
          <h3 className="text-lg font-medium mb-2">Ollama URL</h3>
          <input
            type="text"
            className="w-full px-4 py-2 rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800"
            placeholder="http://localhost:11434"
            value={settings.ollamaUrl || ''}
            onChange={(e) => updateSettings({ ollamaUrl: e.target.value })}
          />
        </div>
      )}
    </div>
  );
};

export default ModelSettings; 