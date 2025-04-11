import React from 'react';
import { Message } from '../../context/ChatContext';
import { FaUser, FaRobot, FaExclamationTriangle } from 'react-icons/fa';

interface MessageItemProps {
  message: Message;
}

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  // Format timestamp
  const formattedTime = new Date(message.timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit'
  });

  const getAvatar = () => {
    switch (message.role) {
      case 'user':
        return <FaUser className="text-white" />;
      case 'system':
        return <FaExclamationTriangle className="text-yellow-800 dark:text-yellow-200" />;
      case 'assistant':
        return <FaRobot className="text-white" />;
      default:
        return null;
    }
  };

  return (
    <div 
      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
    >
      {message.role !== 'user' && (
        <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center mr-2 
          ${message.role === 'assistant' 
            ? 'bg-blue-500 dark:bg-[#539bf5]' 
            : message.role === 'system' 
              ? 'bg-yellow-100 dark:bg-yellow-700' 
              : 'bg-gray-300 dark:bg-[#323842]'
          }`}>
          {getAvatar()}
        </div>
      )}
      
      <div 
        className={`max-w-[80%] rounded-2xl px-4 py-3 shadow-sm
          ${message.role === 'user' 
            ? 'bg-blue-500 dark:bg-[#539bf5] text-white dark:text-[#e6edf3] rounded-tr-none' 
            : message.role === 'system' 
              ? 'bg-yellow-100 text-gray-800 dark:bg-yellow-800 dark:text-[#e6edf3] rounded-tl-none' 
              : 'bg-white text-gray-800 dark:bg-[#252b32] dark:text-[#e6edf3] rounded-tl-none border border-gray-100 dark:border-[#323842]'
          }`}
      >
        <div className="flex items-center mb-1">
          <span className="font-medium text-sm">
            {message.role === 'user' ? 'You' : message.role === 'system' ? 'System' : 'QWORY'}
          </span>
          <span className="text-xs opacity-70 ml-2">{formattedTime}</span>
        </div>
        <div className="whitespace-pre-wrap text-sm md:text-base leading-relaxed">
          {message.content}
        </div>
      </div>
      
      {message.role === 'user' && (
        <div className="flex-shrink-0 h-8 w-8 rounded-full bg-blue-600 dark:bg-[#539bf5] flex items-center justify-center ml-2">
          {getAvatar()}
        </div>
      )}
    </div>
  );
};

export default MessageItem; 