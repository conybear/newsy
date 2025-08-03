import React from 'react';
import { useAuth } from '../auth/SimpleAuth';

const SimpleDashboard = () => {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-100">
      <div className="container mx-auto p-8">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-amber-900">WELCOME TO ACTA DIURNA</h1>
              <p className="text-amber-700">Hello, {user?.full_name}!</p>
            </div>
            <button
              onClick={logout}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Logout
            </button>
          </div>

          <div className="text-center">
            <h2 className="text-2xl font-bold text-green-600 mb-4">
              🎉 AUTHENTICATION SUCCESS! 🎉
            </h2>
            <p className="text-gray-700 mb-4">
              Your minimal authentication system is working perfectly!
            </p>
            <div className="bg-green-100 p-4 rounded-lg">
              <p className="text-green-800">
                <strong>User:</strong> {user?.email}<br/>
                <strong>Name:</strong> {user?.full_name}<br/>
                <strong>Status:</strong> Successfully authenticated
              </p>
            </div>
          </div>

          <div className="mt-8 text-center">
            <p className="text-gray-600">
              This minimal authentication system is ready for your demo!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleDashboard;