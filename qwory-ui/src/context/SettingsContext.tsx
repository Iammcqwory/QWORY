import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { modelsApi, ModelInfo, ModelProviderInfo } from '../lib/api';

// Define model provider types
export type ModelProvider = 'ollama' | 'openrouter' | 'gemini' | 'openai';

// Settings interface
export interface Settings {
  provider: ModelProvider;
  model: string;
  apiKey?: string;
  ollamaUrl?: string;
}

// SettingsContext interface
interface SettingsContextType {
  settings: Settings;
  updateSettings: (newSettings: Partial<Settings>) => void;
  saveApiKey: (key: string) => void;
  clearApiKey: () => void;
  availableProviders: ModelProviderInfo[];
  availableModels: Record<string, ModelInfo[]>;
  isLoading: boolean;
}

// Create context
const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

// Hook to use the settings context
export const useSettings = (): SettingsContextType => {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};

// SettingsProvider props
interface SettingsProviderProps {
  children: ReactNode;
}

// Default settings
const defaultSettings: Settings = {
  provider: 'openrouter',
  model: 'deepseek/deepseek-chat',
  ollamaUrl: 'http://localhost:11434'
};

// SettingsProvider component
export const SettingsProvider: React.FC<SettingsProviderProps> = ({ children }) => {
  // Initialize settings from localStorage or use defaults
  const [settings, setSettings] = useState<Settings>(() => {
    const savedSettings = localStorage.getItem('qworySettings');
    return savedSettings ? JSON.parse(savedSettings) : defaultSettings;
  });

  // State for available providers and models
  const [availableProviders, setAvailableProviders] = useState<ModelProviderInfo[]>([]);
  const [availableModels, setAvailableModels] = useState<Record<string, ModelInfo[]>>({});
  const [isLoading, setIsLoading] = useState(true);

  // Save settings to localStorage when they change
  useEffect(() => {
    localStorage.setItem('qworySettings', JSON.stringify(settings));
  }, [settings]);

  // Fetch available providers and models
  useEffect(() => {
    const fetchModels = async () => {
      setIsLoading(true);
      try {
        // Fetch providers
        const providers = await modelsApi.listProviders();
        setAvailableProviders(providers);
        
        // Fetch models
        const models = await modelsApi.listModels();
        setAvailableModels(models);
        
        // If the current provider/model is not available, switch to a default
        const currentProviderExists = providers.some(p => p.id === settings.provider);
        if (!currentProviderExists && providers.length > 0) {
          setSettings(prev => ({ ...prev, provider: providers[0].id as ModelProvider }));
        }
        
        // Check if current model exists for provider
        const currentProviderModels = models[settings.provider] || [];
        const currentModelExists = currentProviderModels.some(m => m.id === settings.model);
        if (!currentModelExists && currentProviderModels.length > 0) {
          setSettings(prev => ({ ...prev, model: currentProviderModels[0].id }));
        }
      } catch (error) {
        console.error('Error fetching models:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchModels();
  }, []);

  // Update settings
  const updateSettings = useCallback((newSettings: Partial<Settings>) => {
    setSettings(prev => {
      const updated = { ...prev, ...newSettings };
      
      // If provider changed, select first model of that provider
      if (newSettings.provider && newSettings.provider !== prev.provider) {
        const providerModels = availableModels[newSettings.provider] || [];
        if (providerModels.length > 0) {
          updated.model = providerModels[0].id;
        }
      }
      
      return updated;
    });
  }, [availableModels]);

  // Save API key
  const saveApiKey = useCallback((key: string) => {
    if (!key.trim()) return;
    
    // In a real app, you might want to encrypt this
    setSettings(prev => ({ ...prev, apiKey: key }));
  }, []);

  // Clear API key
  const clearApiKey = useCallback(() => {
    setSettings(prev => {
      const newSettings = { ...prev };
      delete newSettings.apiKey;
      return newSettings;
    });
  }, []);

  const value = {
    settings,
    updateSettings,
    saveApiKey,
    clearApiKey,
    availableProviders,
    availableModels,
    isLoading
  };

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  );
};

export default SettingsContext; 