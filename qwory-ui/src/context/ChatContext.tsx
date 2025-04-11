import React, { createContext, useContext, useState, useEffect, ReactNode, useRef, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { chatApi, Message as ApiMessage } from '../lib/api';
import { useSettings } from './SettingsContext';

// Define the Message type
export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: Date;
}

// Define the ChatContext type
interface ChatContextType {
  messages: Message[];
  sendMessage: (content: string) => void;
  clearMessages: () => void;
  isLoading: boolean;
}

// Create the context with a default undefined value
const ChatContext = createContext<ChatContextType | undefined>(undefined);

// Custom hook to use the chat context
export const useChat = (): ChatContextType => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

// Props for the ChatProvider component
interface ChatProviderProps {
  children: ReactNode;
}

// ChatProvider component
export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  // Get settings for model provider
  const { settings } = useSettings();
  
  // WebSocket reference
  const socketRef = useRef<WebSocket | null>(null);
  
  // Client ID for WebSocket connection
  const clientIdRef = useRef<string>(uuidv4());
  
  // Current streaming message reference
  const streamingMessageRef = useRef<Message | null>(null);
  
  // State for messages
  const [messages, setMessages] = useState<Message[]>(() => {
    // Load messages from localStorage if available
    const savedMessages = localStorage.getItem('chatMessages');
    return savedMessages ? JSON.parse(savedMessages).map((msg: any) => ({
      ...msg,
      timestamp: new Date(msg.timestamp)
    })) : [];
  });
  
  // State for loading status
  const [isLoading, setIsLoading] = useState(false);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('chatMessages', JSON.stringify(messages));
  }, [messages]);
  
  // Set up WebSocket connection
  useEffect(() => {
    // Initialize WebSocket connection
    const initWebSocket = () => {
      try {
        // Close existing connection if any
        if (socketRef.current && socketRef.current.readyState !== WebSocket.CLOSED) {
          socketRef.current.close();
        }
        
        // Create new WebSocket connection
        socketRef.current = chatApi.createWebSocket(clientIdRef.current);
        
        // Set up event handlers
        socketRef.current.onopen = () => {
          console.log('WebSocket connection established');
        };
        
        socketRef.current.onmessage = (event) => {
          try {
            // Handle incoming message
            const chunk = event.data;
            
            // Check if it's an end of message marker
            if (chunk.trim() === "[END]") {
              // Reset the streaming message reference
              streamingMessageRef.current = null;
              setIsLoading(false);
              return;
            }
            
            // If we're not currently streaming a message, create a new one
            if (!streamingMessageRef.current) {
              const newMessage: Message = {
                id: uuidv4(),
                content: chunk,
                role: 'assistant',
                timestamp: new Date()
              };
              streamingMessageRef.current = newMessage;
              setMessages(prev => [...prev, newMessage]);
            } else {
              // Update the existing streaming message
              streamingMessageRef.current.content += chunk;
              setMessages(prev => 
                prev.map(msg => 
                  msg.id === streamingMessageRef.current?.id
                    ? { ...streamingMessageRef.current }
                    : msg
                )
              );
            }
          } catch (error) {
            console.error('Error handling WebSocket message:', error);
            setIsLoading(false);
          }
        };
        
        socketRef.current.onclose = () => {
          console.log('WebSocket connection closed');
          streamingMessageRef.current = null;
          setIsLoading(false);
        };
        
        socketRef.current.onerror = (error) => {
          console.error('WebSocket error:', error);
          setIsLoading(false);
        };
      } catch (error) {
        console.error('Error initializing WebSocket:', error);
        setIsLoading(false);
      }
    };
    
    // Initialize WebSocket
    initWebSocket();
    
    // Cleanup on unmount
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);
  
  // Function to send a message
  const sendMessage = useCallback((content: string) => {
    if (!content.trim()) return;
    
    // Create a new user message
    const userMessage: Message = {
      id: uuidv4(),
      content,
      role: 'user',
      timestamp: new Date()
    };
    
    // Add the user message to the state
    setMessages(prevMessages => [...prevMessages, userMessage]);
    
    // Set loading state to true
    setIsLoading(true);
    
    // Reset streaming message reference
    streamingMessageRef.current = null;
    
    // Convert messages to API format
    const apiMessages: ApiMessage[] = [
      ...messages.map(msg => ({ role: msg.role, content: msg.content })),
      { role: userMessage.role, content: userMessage.content }
    ];
    
    // Check if WebSocket is open for streaming
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      // Send message through WebSocket for streaming response
      socketRef.current.send(JSON.stringify({
        messages: apiMessages,
        provider: settings.provider,
        model: settings.model,
        stream: true
      }));
    } else {
      // Fallback to regular API call if WebSocket is not available
      chatApi.sendMessage(apiMessages)
        .then(response => {
          // Create a new assistant message
          const assistantMessage: Message = {
            id: uuidv4(),
            content: response.content,
            role: response.role,
            timestamp: new Date()
          };
          
          // Add the assistant message to the state
          setMessages(prevMessages => [...prevMessages, assistantMessage]);
        })
        .catch(error => {
          console.error('Error sending message:', error);
          
          // Add error message
          const errorMessage: Message = {
            id: uuidv4(),
            content: `Error: ${error.message || 'Failed to get response'}`,
            role: 'system',
            timestamp: new Date()
          };
          
          setMessages(prevMessages => [...prevMessages, errorMessage]);
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [messages, settings]);

  // Function to clear all messages
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  // Value to be provided by the context
  const value = {
    messages,
    sendMessage,
    clearMessages,
    isLoading
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

export default ChatContext; 