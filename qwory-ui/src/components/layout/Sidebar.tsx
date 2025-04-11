import React, { useState } from "react";
import { Link } from 'react-router-dom';
import { Home, Settings, X } from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}

const Sidebar = ({ isOpen, setIsOpen }: SidebarProps) => {
  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-20 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
      
      {/* Sidebar */}
      <div 
        className={`fixed inset-y-0 left-0 z-30 w-64 transform bg-[var(--sidebar-color)] border-r border-[var(--border-color)] transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between p-4 border-b border-[var(--border-color)]">
          <h1 className="text-xl font-bold">QWORY</h1>
          <button 
            onClick={() => setIsOpen(false)}
            className="p-1 rounded-md hover:bg-[var(--highlight-color)] lg:hidden"
            aria-label="Close sidebar"
          >
            <X size={24} />
          </button>
        </div>
        
        <nav className="p-4">
          <ul className="space-y-2">
            <li>
              <Link 
                to="/" 
                className="flex items-center p-2 rounded-md hover:bg-[var(--highlight-color)]"
                onClick={() => setIsOpen(false)}
              >
                <Home className="mr-3" size={20} />
                <span>Chat</span>
              </Link>
            </li>
            <li>
              <Link 
                to="/settings" 
                className="flex items-center p-2 rounded-md hover:bg-[var(--highlight-color)]"
                onClick={() => setIsOpen(false)}
              >
                <Settings className="mr-3" size={20} />
                <span>Settings</span>
              </Link>
            </li>
          </ul>
        </nav>
      </div>
    </>
  );
};

export default Sidebar; 