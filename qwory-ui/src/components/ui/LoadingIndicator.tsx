import React from 'react';
import { FaRobot } from 'react-icons/fa';

const LoadingIndicator: React.FC = () => {
  return (
    <div className="flex justify-start">
      <div className="flex-shrink-0 h-8 w-8 rounded-full bg-blue-500 dark:bg-[#539bf5] flex items-center justify-center mr-2">
        <FaRobot className="text-white dark:text-[#e6edf3]" />
      </div>
      
      <div className="bg-white dark:bg-[#252b32] border border-gray-100 dark:border-[#323842] rounded-2xl rounded-tl-none px-4 py-3 max-w-[80%] shadow-sm">
        <div className="flex items-center mb-1">
          <span className="font-medium text-sm text-gray-800 dark:text-[#e6edf3]">QWORY</span>
        </div>
        <div className="flex items-center space-x-1.5 h-6">
          <div className="w-2 h-2 rounded-full bg-blue-500 dark:bg-[#539bf5] animate-pulse" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 rounded-full bg-blue-500 dark:bg-[#539bf5] animate-pulse" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 rounded-full bg-blue-500 dark:bg-[#539bf5] animate-pulse" style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator; 