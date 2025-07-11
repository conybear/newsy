import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import FlipBook from '../components/FlipBook';
import { Calendar, RefreshCw, AlertCircle } from 'lucide-react';

const WeeklyEdition = () => {
  const [edition, setEdition] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;

  useEffect(() => {
    fetchCurrentEdition();
  }, []);

  const fetchCurrentEdition = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/editions/current`);
      setEdition(response.data);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to load weekly edition');
    } finally {
      setLoading(false);
    }
  };

  const getWeekDisplay = (weekOf) => {
    try {
      const [year, week] = weekOf.split('-W');
      return `Week ${week}, ${year}`;
    } catch (error) {
      return weekOf;
    }
  };

  if (loading) {
    return (
      <Layout currentPage="edition">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout currentPage="edition">
        <div className="max-w-2xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <div>
                <h3 className="text-lg font-medium text-red-800">Error loading edition</h3>
                <p className="text-sm text-red-600 mt-1">{error}</p>
              </div>
            </div>
            <button
              onClick={fetchCurrentEdition}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Try Again
            </button>
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