import React from 'react';
import { Link, Outlet } from 'react-router-dom';
import { useTheme } from '../../context/ThemeContext';

const Layout: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen flex flex-col bg-[var(--bg-color)] text-[var(--text-color)]">
      <header className="py-4 px-6 flex justify-between items-center bg-[var(--sidebar-color)] border-b border-[var(--border-color)]">
        <div className="flex items-center">
          <img src="/favicon.svg" alt="Qwory Logo" className="w-8 h-8 mr-3" />
          <h1 className="text-xl font-bold">Qwory</h1>
        </div>
        <nav>
          <ul className="flex space-x-6">
            <li>
              <Link to="/" className="hover:text-[var(--accent-color)] transition-colors">Chat</Link>
            </li>
            <li>
              <Link to="/settings" className="hover:text-[var(--accent-color)] transition-colors">Settings</Link>
            </li>
            <li>
              <button 
                onClick={toggleTheme}
                className="p-2 rounded-full hover:bg-[var(--highlight-color)] transition-colors"
                aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
              >
                {theme === 'dark' ? (
                  // Sun icon for dark mode
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                ) : (
                  // Moon icon for light mode
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                  </svg>
                )}
              </button>
            </li>
          </ul>
        </nav>
      </header>
      <main className="flex-grow">
        <Outlet />
      </main>
      <footer className="py-4 px-6 text-center text-sm bg-[var(--sidebar-color)] text-[var(--muted-color)] border-t border-[var(--border-color)]">
        <p>Qwory Framework - Build and deploy LLM agents</p>
      </footer>
    </div>
  );
};

export default Layout; 