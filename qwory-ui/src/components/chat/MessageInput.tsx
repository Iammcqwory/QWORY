import React, { useState, KeyboardEvent, useRef, useEffect } from 'react';
import { FaPaperPlane, FaSpinner } from 'react-icons/fa';

interface MessageInputProps {
  onSendMessage: (content: string) => void;
  isLoading: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({ onSendMessage, isLoading }) => {
  const [message, setMessage] = useState('');
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-focus the input when the component mounts
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Auto resize textarea based on content
  useEffect(() => {
    const textarea = inputRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
    }
  }, [message]);

  const handleSend = () => {
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="relative">
      <textarea
        ref={inputRef}
        className="w-full resize-none rounded-lg border border-gray-200 dark:border-[#323842] 
                 focus:ring-2 focus:ring-blue-500 dark:focus:ring-[#539bf5] focus:border-transparent py-3 px-4 pr-12
                 bg-white dark:bg-[#252b32] dark:text-[#e6edf3] min-h-[50px] max-h-[150px]
                 shadow-sm transition-all"
        placeholder="Type your message..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={isLoading}
      />
      
      <button
        className={`absolute right-3 bottom-3 w-8 h-8 flex items-center justify-center rounded-full transition-colors ${
          isLoading || !message.trim() 
            ? 'bg-gray-200 text-gray-400 dark:bg-[#323842] dark:text-[#768390] cursor-not-allowed' 
            : 'bg-blue-500 dark:bg-[#539bf5] text-white dark:text-[#e6edf3] hover:bg-blue-600 dark:hover:bg-[#4a88da]'
        }`}
        onClick={handleSend}
        disabled={isLoading || !message.trim()}
        aria-label="Send message"
      >
        {isLoading ? (
          <FaSpinner className="animate-spin" />
        ) : (
          <FaPaperPlane className="text-sm" />
        )}
      </button>
      
      <div className="text-xs text-gray-400 dark:text-[#768390] mt-2 ml-1">
        <kbd className="px-1 py-0.5 text-xs bg-gray-100 dark:bg-[#323842] border border-gray-300 dark:border-[#252b32] rounded">Shift</kbd>
        +
        <kbd className="px-1 py-0.5 text-xs bg-gray-100 dark:bg-[#323842] border border-gray-300 dark:border-[#252b32] rounded ml-1">Enter</kbd>
        <span className="ml-1">for new line</span>
      </div>
    </div>
  );
};

export default MessageInput; 