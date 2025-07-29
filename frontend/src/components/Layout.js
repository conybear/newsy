import React from 'react';
import { useAuth } from './AuthContext';
import { LogOut, User, BookOpen, Users, Edit3 } from 'lucide-react';

const Layout = ({ children, currentPage = 'home' }) => {
  const { user, logout } = useAuth();

  const navigation = [
    { name: 'Weekly Edition', href: '/edition', icon: BookOpen, key: 'edition' },
    { name: 'My Stories', href: '/stories', icon: Edit3, key: 'stories' },
    { name: 'Friends', href: '/friends', icon: Users, key: 'friends' },
    { name: 'Archive', href: '/archive', icon: BookOpen, key: 'archive' },
    { name: '🔍 Debug', href: '/debug', icon: BookOpen, key: 'debug' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <BookOpen className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-2xl font-bold text-gray-900">
                Weekly Chronicles
              </span>
            </div>
            
            {/* Navigation */}
            <nav className="hidden md:flex space-x-8">
              {navigation.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentPage === item.key
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <item.icon className="h-4 w-4 mr-2" />
                  {item.name}
                </a>
              ))}
            </nav>

            {/* User menu */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <User className="h-5 w-5 text-gray-400" />
                <span className="text-sm font-medium text-gray-700">
                  {user?.full_name}
                </span>
              </div>
              <button
                onClick={logout}
                className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-500 hover:text-gray-700 hover:bg-gray-100"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
};

export default Layout;