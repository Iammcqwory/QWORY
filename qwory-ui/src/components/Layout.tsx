import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
// Import icons
import { FaComments, FaCog, FaMoon, FaSun, FaRobot } from 'react-icons/fa';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-[#1a1e24] text-gray-900 dark:text-[#e6edf3]">
      {/* Sidebar */}
      <div className="w-64 bg-white dark:bg-[#252b32] border-r border-gray-200 dark:border-[#323842] shadow-sm">
        <div className="p-4 border-b border-gray-200 dark:border-[#323842] flex items-center space-x-3">
          <FaRobot className="text-blue-500 dark:text-[#539bf5] text-xl" />
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-500 to-purple-600 dark:from-[#539bf5] dark:to-[#539bf5] bg-clip-text text-transparent">QWORY</h1>
        </div>
        <nav className="p-4">
          <ul className="space-y-2">
            <li>
              <Link 
                to="/" 
                className={`flex items-center space-x-3 p-2 rounded-lg transition-colors ${
                  isActive('/') 
                    ? 'bg-blue-500 dark:bg-[#539bf5] text-white dark:text-[#e6edf3]' 
                    : 'hover:bg-gray-100 dark:hover:bg-[#2b313a]'
                }`}
              >
                <FaComments />
                <span>Chat</span>
              </Link>
            </li>
            <li>
              <Link 
                to="/settings" 
                className={`flex items-center space-x-3 p-2 rounded-lg transition-colors ${
                  isActive('/settings') 
                    ? 'bg-blue-500 dark:bg-[#539bf5] text-white dark:text-[#e6edf3]' 
                    : 'hover:bg-gray-100 dark:hover:bg-[#2b313a]'
                }`}
              >
                <FaCog />
                <span>Settings</span>
              </Link>
            </li>
          </ul>
        </nav>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white dark:bg-[#252b32] border-b border-gray-200 dark:border-[#323842] shadow-sm">
          <div className="p-4 flex justify-between items-center">
            <h2 className="text-lg font-semibold">
              {location.pathname === '/' ? 'Chat' : 'Settings'}
            </h2>
            <button 
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-[#2b313a] transition-colors"
              aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
            >
              {theme === 'light' ? <FaMoon className="text-gray-600" /> : <FaSun className="text-[#e6edf3]" />}
            </button>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-4 bg-gray-50 dark:bg-[#1a1e24]">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout; 