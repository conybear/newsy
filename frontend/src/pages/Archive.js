import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import FlipBook from '../components/FlipBook';
import { Calendar, Archive as ArchiveIcon, Eye, RefreshCw } from 'lucide-react';

const Archive = () => {
  const [editions, setEditions] = useState([]);
  const [selectedEdition, setSelectedEdition] = useState(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'view'

  const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;

  useEffect(() => {
    fetchArchive();
  }, []);

  const fetchArchive = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/editions/archive`);
      setEditions(response.data);
    } catch (error) {
      console.error('Failed to fetch archive:', error);
    } finally {
      setLoading(false);
    }
  };

  const viewEdition = (edition) => {
    setSelectedEdition(edition);
    setViewMode('view');
  };

  const backToList = () => {
    setSelectedEdition(null);
    setViewMode('list');
  };

  const getWeekDisplay = (weekOf) => {
    try {
      const [year, week] = weekOf.split('-W');
      return `Week ${week}, ${year}`;
    } catch (error) {
      return weekOf;
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <Layout currentPage="archive">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      </Layout>
    );
  }

  if (viewMode === 'view' && selectedEdition) {
    return (
      <Layout currentPage="archive">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <button
                onClick={backToList}
                className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 mb-2"
              >
                <Calendar className="h-4 w-4" />
                <span>← Back to Archive</span>
              </button>
              <h1 className="text-3xl font-bold text-gray-900">
                {getWeekDisplay(selectedEdition.week_of)}
              </h1>
              <p className="text-gray-600">
                Published {formatDate(selectedEdition.created_at)}
              </p>
            </div>
          </div>

          {/* Edition stats */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-blue-600">
                  {selectedEdition.stories?.length || 0}
                </div>
                <div className="text-sm text-gray-600">Stories</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-red-600">
                  {selectedEdition.stories?.filter(s => s.is_headline).length || 0}
                </div>
                <div className="text-sm text-gray-600">Headlines</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">
                  {selectedEdition.stories?.reduce((acc, story) => acc + (story.images?.length || 0), 0) || 0}
                </div>
                <div className="text-sm text-gray-600">Images</div>
              </div>
            </div>
          </div>

          {/* FlipBook */}
          <FlipBook stories={selectedEdition.stories || []} />
        </div>
      </Layout>
    );
  }

  return (
    <Layout currentPage="archive">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Archive</h1>
          <p className="text-gray-600 mt-1">Browse past weekly editions</p>
        </div>

        {/* Archive list */}
        {editions.length === 0 ? (
          <div className="text-center py-12">
            <ArchiveIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No archived editions</h3>
            <p className="text-gray-500">Your past weekly editions will appear here once they're published.</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {editions.map((edition) => (
              <div key={edition.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <Calendar className="h-5 w-5 text-gray-400" />
                      <h3 className="text-lg font-medium text-gray-900">
                        {getWeekDisplay(edition.week_of)}
                      </h3>
                    </div>
                    
                    <div className="flex items-center space-x-6 text-sm text-gray-600">
                      <span>Published {formatDate(edition.created_at)}</span>
                      <span>{edition.stories?.length || 0} stories</span>
                      <span>{edition.stories?.filter(s => s.is_headline).length || 0} headlines</span>
                      <span>
                        {edition.stories?.reduce((acc, story) => acc + (story.images?.length || 0), 0) || 0} images
                      </span>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => viewEdition(edition)}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Eye className="h-4 w-4" />
                    <span>View</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Archive;