import React, { useEffect, useRef } from 'react';
import { useChat } from '../../context/ChatContext';
import { useSettings } from '../../context/SettingsContext';
import MessageItem from './MessageItem';
import MessageInput from './MessageInput';
import LoadingIndicator from '../ui/LoadingIndicator';
import { FaTrash, FaRobot, FaServer } from 'react-icons/fa';

const ChatInterface: React.FC = () => {
  const { messages, sendMessage, clearMessages, isLoading } = useChat();
  const { settings, isLoading: settingsLoading } = useSettings();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleSendMessage = (content: string) => {
    sendMessage(content);
  };

  const handleClearChat = () => {
    if (window.confirm('Are you sure you want to clear the chat history?')) {
      clearMessages();
    }
  };
  
  return (
    <div className="flex flex-col h-full bg-gray-50 dark:bg-[#1a1e24] rounded-lg shadow-sm">
      <div className="bg-white dark:bg-[#252b32] p-4 border-b border-gray-200 dark:border-[#323842] flex justify-between items-center rounded-t-lg">
        <div className="flex items-center space-x-3">
          <FaRobot className="text-blue-500 dark:text-[#539bf5]" />
          <div>
            <h2 className="text-lg font-semibold">AI Assistant</h2>
            {!settingsLoading && (
              <div className="text-sm text-gray-500 dark:text-[#768390] flex items-center">
                <FaServer className="mr-1 text-xs" />
                {settings.provider} / {settings.model}
              </div>
            )}
          </div>
        </div>
        <button
          onClick={handleClearChat}
          className="flex items-center space-x-1 text-sm px-3 py-1.5 bg-gray-100 dark:bg-[#2b313a] hover:bg-gray-200 dark:hover:bg-[#323842] rounded-lg transition-colors"
        >
          <FaTrash className="text-gray-500 dark:text-[#768390] text-xs" />
          <span>Clear</span>
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-[#1a1e24]">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 dark:text-[#768390] p-8">
            <FaRobot className="text-5xl text-gray-300 dark:text-[#323842] mb-4" />
            <h3 className="text-xl font-medium mb-2">Welcome to QWORY</h3>
            <p className="text-center max-w-md">
              Your AI assistant powered by {!settingsLoading && 
                <span className="font-semibold text-blue-500 dark:text-[#539bf5]">
                  {settings.model}
                </span>
              }
            </p>
            <p className="text-center text-sm mt-4 max-w-md text-gray-400 dark:text-[#768390]">
              Ask me anything! I can help with research, coding, creative writing, and more.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {messages.map((message) => (
              <MessageItem key={message.id} message={message} />
            ))}
          </div>
        )}
        {isLoading && <LoadingIndicator />}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="p-4 bg-white dark:bg-[#252b32] border-t border-gray-200 dark:border-[#323842] rounded-b-lg">
        <MessageInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
};

export default ChatInterface; 