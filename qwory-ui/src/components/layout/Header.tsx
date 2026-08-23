import React from 'react';
import { FiMenu, FiMoon, FiSun } from 'react-icons/fi';
import { useTheme } from '../../context/ThemeContext';

interface HeaderProps {
  onMenuButtonClick?: () => void;
}

const Header: React.FC<HeaderProps> = ({ onMenuButtonClick }) => {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <header className="bg-[var(--sidebar-color)] border-b border-[var(--border-color)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <button
              onClick={onMenuButtonClick}
              className="px-4 border-r border-[var(--border-color)] text-[var(--muted-color)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)] md:hidden"
            >
              <span className="sr-only">Open sidebar</span>
              <FiMenu className="h-6 w-6" />
            </button>
            <div className="flex-shrink-0 flex items-center">
              <span className="text-xl font-bold text-[var(--accent-color)]">Qwory</span>
            </div>
          </div>
          <div className="flex items-center">
            <button
              onClick={toggleTheme}
              className="ml-4 p-2 rounded-md hover:bg-[var(--highlight-color)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-color)]"
            >
              {theme === 'dark' ? (
                <FiSun className="h-5 w-5" />
              ) : (
                <FiMoon className="h-5 w-5" />
              )}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header; 