// API client for connecting to the Qwory API backend

// API base URL
const API_BASE_URL = 'http://localhost:8000';

// Message type definition
export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

// API response types
export interface ChatResponse {
  message: Message;
}

export interface ModelInfo {
  id: string;
  name: string;
}

export interface ModelProviderInfo {
  id: string;
  name: string;
  models: ModelInfo[];
  status: string;
}

// Error handling
class ApiError extends Error {
  status: number;
  
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

// Helper function for making API requests
async function apiRequest<T>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new ApiError(
      `API request failed: ${errorText}`,
      response.status
    );
  }
  
  return await response.json() as T;
}

// Chat API functions
export const chatApi = {
  sendMessage: async (messages: Message[]): Promise<Message> => {
    const response = await apiRequest<ChatResponse>('/api/chat/message', {
      method: 'POST',
      body: JSON.stringify({ messages }),
    });
    
    return response.message;
  },
  
  createWebSocket: (clientId: string): WebSocket => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = API_BASE_URL.replace(/^https?:\/\//, '');
    const wsUrl = `${protocol}//${host}/api/chat/ws/${clientId}`;
    
    const socket = new WebSocket(wsUrl);
    return socket;
  }
};

// Models API functions
export const modelsApi = {
  listProviders: async (): Promise<ModelProviderInfo[]> => {
    return await apiRequest<ModelProviderInfo[]>('/api/models/providers');
  },
  
  listModels: async (): Promise<Record<string, ModelInfo[]>> => {
    return await apiRequest<Record<string, ModelInfo[]>>('/api/models');
  },
  
  listProviderModels: async (providerId: string): Promise<ModelInfo[]> => {
    return await apiRequest<ModelInfo[]>(`/api/models/${providerId}`);
  }
};

// Export a default object with all API functions
export default {
  chat: chatApi,
  models: modelsApi
}; 