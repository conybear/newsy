import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import FlipBook from '../components/FlipBook';
import { Calendar, RefreshCw, AlertCircle, Wifi, WifiOff } from 'lucide-react';

const WeeklyEdition = () => {
  const [edition, setEdition] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [retryCount, setRetryCount] = useState(0);

  const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;

  useEffect(() => {
    fetchCurrentEdition();
  }, []);

  const fetchCurrentEdition = async (isRetry = false) => {
    try {
      setLoading(true);
      setError('');
      
      const response = await axios.get(`${API_BASE}/editions/current`);
      setEdition(response.data);
      setRetryCount(0); // Reset retry count on success
    } catch (error) {
      console.error('Failed to load weekly edition:', error);
      
      if (error.code === 'NETWORK_ERROR' || !error.response) {
        setError('Network connection lost. Please check your internet connection.');
      } else if (error.response?.status === 401) {
        setError('Your session has expired. Please refresh the page to log in again.');
      } else if (error.response?.status >= 500) {
        setError('Server is temporarily unavailable. Trying again...');
        // Auto-retry for server errors
        if (retryCount < 3) {
          setTimeout(() => {
            setRetryCount(prev => prev + 1);
            fetchCurrentEdition(true);
          }, 2000);
        }
      } else {
        setError(error.response?.data?.detail || 'Failed to load weekly edition');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    setRetryCount(0);
    fetchCurrentEdition(true);
  };

  const getWeekDisplay = (weekOf) => {
    try {
      const [year, week] = weekOf.split('-W');
      return `Week ${week}, ${year}`;
    } catch (error) {
      return weekOf;
    }
  };

  if (loading && !edition) {
    return (
      <Layout currentPage="edition">
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
          <p className="text-gray-600">Loading your weekly edition...</p>
        </div>
      </Layout>
    );
  }

  if (error && !edition) {
    const isNetworkError = error.includes('Network') || error.includes('connection');
    
    return (
      <Layout currentPage="edition">
        <div className="max-w-2xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-start space-x-3">
              {isNetworkError ? (
                <WifiOff className="h-6 w-6 text-red-600 mt-1" />
              ) : (
                <AlertCircle className="h-6 w-6 text-red-600 mt-1" />
              )}
              <div className="flex-1">
                <h3 className="text-lg font-medium text-red-800 mb-2">
                  {isNetworkError ? 'Connection Problem' : 'Error Loading Edition'}
                </h3>
                <p className="text-sm text-red-600 mb-4">{error}</p>
                
                {retryCount > 0 && (
                  <p className="text-sm text-red-500 mb-4">
                    Retry attempt {retryCount}/3...
                  </p>
                )}
                
                <div className="flex space-x-3">
                  <button
                    onClick={handleRetry}
                    disabled={loading}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 transition-colors"
                  >
                    {loading ? 'Retrying...' : 'Try Again'}
                  </button>
                  
                  {isNetworkError && (
                    <button
                      onClick={() => window.location.reload()}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                    >
                      Refresh Page
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout currentPage="edition">
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Weekly Edition</h1>
          <div className="flex items-center justify-center space-x-2 text-gray-600">
            <Calendar className="h-5 w-5" />
            <span>{getWeekDisplay(edition?.week_of)}</span>
          </div>
        </div>

        {/* Network error banner for partial loading */}
        {error && edition && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <Wifi className="h-5 w-5 text-yellow-600" />
              <div>
                <h3 className="text-sm font-medium text-yellow-800">Connection Issues</h3>
                <p className="text-sm text-yellow-600 mt-1">
                  {error} Content may not be fully up to date.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Edition stats */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600">
                {edition?.stories?.length || 0}
              </div>
              <div className="text-sm text-gray-600">Total Stories</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-600">
                {edition?.stories?.filter(s => s.is_headline).length || 0}
              </div>
              <div className="text-sm text-gray-600">Headlines</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">
                {edition?.stories?.reduce((acc, story) => acc + (story.images?.length || 0), 0) || 0}
              </div>
              <div className="text-sm text-gray-600">Images</div>
            </div>
          </div>
        </div>

        {/* FlipBook */}
        <FlipBook stories={edition?.stories || []} />
      </div>
    </Layout>
  );
};

export default WeeklyEdition;