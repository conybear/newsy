import React, { useState, useEffect } from 'react';
import { 
  Archive as ArchiveIcon, 
  Calendar, 
  FileText, 
  Users, 
  Search,
  Download,
  Eye
} from 'lucide-react';
import axios from 'axios';
import FlipBook from '../components/FlipBook';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const Archive = () => {
  const [archive, setArchive] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedNewspaper, setSelectedNewspaper] = useState(null);
  const [loadingNewspaper, setLoadingNewspaper] = useState(false);

  useEffect(() => {
    fetchArchive();
  }, []);

  const fetchArchive = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await axios.get(`${API_BASE}/api/newspapers/archive`);
      setArchive(response.data);
    } catch (error) {
      console.error('Failed to fetch archive:', error);
      setError('Failed to load archive');
    } finally {
      setLoading(false);
    }
  };

  const loadNewspaper = async (week) => {
    try {
      setLoadingNewspaper(true);
      setError('');
      
      const response = await axios.get(`${API_BASE}/api/newspapers/week/${week}`);
      setSelectedNewspaper(response.data);
    } catch (error) {
      console.error('Failed to load newspaper:', error);
      setError('Failed to load newspaper for ' + week);
    } finally {
      setLoadingNewspaper(false);
    }
  };

  const filteredArchive = archive.filter(newspaper => 
    newspaper.week_of.toLowerCase().includes(searchTerm.toLowerCase()) ||
    newspaper.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getWeekRange = (weekString) => {
    // Convert week string like "2024-W52" to date range
    const [year, week] = weekString.split('-W');
    const jan1 = new Date(parseInt(year), 0, 1);
    const daysOffset = (parseInt(week) - 1) * 7;
    const startDate = new Date(jan1.getTime() + daysOffset * 24 * 60 * 60 * 1000);
    const endDate = new Date(startDate.getTime() + 6 * 24 * 60 * 60 * 1000);
    
    return {
      start: startDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      end: endDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    };
  };

  if (loading) {
    return (
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="loading">
          <div className="roman-header text-xl">Loading archive...</div>
        </div>
      </div>
    );
  }

  if (selectedNewspaper) {
    return (
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <button
            onClick={() => setSelectedNewspaper(null)}
            className="flex items-center space-x-2 text-yellow-600 hover:text-yellow-700 transition-colors mb-4"
          >
            ← Back to Archive
          </button>
          
          <div className="flex items-center justify-between">
            <div>
              <h1 className="roman-header text-3xl font-bold mb-2">
                {selectedNewspaper.title}
              </h1>
              <p className="text-gray-600 text-lg">
                Week {selectedNewspaper.week_of} • Published {formatDate(selectedNewspaper.published_at)}
              </p>
            </div>
            <div className="text-sm text-gray-500">
              {selectedNewspaper.stories?.length || 0} stories
            </div>
          </div>
        </div>

        <FlipBook newspaper={selectedNewspaper} />
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="roman-header text-3xl font-bold mb-2">
          Archive
        </h1>
        <p className="text-gray-600 text-lg">
          Browse past editions of your Acta Diurna newspaper
        </p>
      </div>

      {error && (
        <div className="error mb-6">
          {error}
        </div>
      )}

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search by week or title..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="roman-input w-full pl-10"
          />
        </div>
      </div>

      {/* Archive List */}
      {filteredArchive.length === 0 ? (
        <div className="roman-column rounded-lg p-8 text-center">
          <ArchiveIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="roman-header text-2xl font-semibold mb-4">
            {archive.length === 0 ? 'No Newspapers Yet' : 'No Results Found'}
          </h2>
          <p className="text-gray-600 mb-6">
            {archive.length === 0 
              ? 'Your newspaper archive will appear here once you start publishing weekly editions.'
              : 'Try adjusting your search terms to find the newspaper you\'re looking for.'
            }
          </p>
          {archive.length === 0 && (
            <button
              onClick={() => window.location.href = '/stories'}
              className="roman-button"
            >
              Write Your First Story
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredArchive.map((newspaper) => {
            const weekRange = getWeekRange(newspaper.week_of);
            
            return (
              <div key={newspaper.week_of} className="roman-column rounded-lg p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="roman-header text-xl font-semibold text-gray-900">
                        {newspaper.title}
                      </h3>
                      <span className="text-sm text-gray-500">•</span>
                      <span className="text-sm font-medium text-yellow-700">
                        Week {newspaper.week_of}
                      </span>
                    </div>
                    
                    <p className="text-gray-600 mb-3">
                      Published {formatDate(newspaper.published_at)}
                    </p>
                    
                    <div className="flex items-center space-x-6 text-sm text-gray-500">
                      <div className="flex items-center space-x-1">
                        <FileText className="w-4 h-4" />
                        <span>{newspaper.story_count} stories</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Users className="w-4 h-4" />
                        <span>{newspaper.contributor_count} contributors</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Calendar className="w-4 h-4" />
                        <span>{weekRange.start} - {weekRange.end}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 ml-4">
                    <button
                      onClick={() => loadNewspaper(newspaper.week_of)}
                      disabled={loadingNewspaper}
                      className="flex items-center space-x-2 roman-button text-sm px-4 py-2"
                    >
                      {loadingNewspaper ? (
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <Eye className="w-4 h-4" />
                      )}
                      <span>Read</span>
                    </button>
                  </div>
                </div>
                
                {/* Quick preview of contributors if multiple */}
                {newspaper.contributor_count > 1 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-xs text-gray-500">
                      Multi-contributor edition with stories from your network
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Archive Stats */}
      {archive.length > 0 && (
        <div className="mt-8 roman-column rounded-lg p-6 bg-green-50">
          <h3 className="font-semibold text-green-900 mb-4">Archive Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-800">
                {archive.length}
              </div>
              <div className="text-sm text-green-700">Total Editions</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-800">
                {archive.reduce((sum, n) => sum + n.story_count, 0)}
              </div>
              <div className="text-sm text-green-700">Total Stories</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-800">
                {Math.max(...archive.map(n => n.contributor_count), 0)}
              </div>
              <div className="text-sm text-green-700">Max Contributors</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-800">
                {archive.length > 0 ? Math.round(archive.reduce((sum, n) => sum + n.story_count, 0) / archive.length) : 0}
              </div>
              <div className="text-sm text-green-700">Avg Stories/Week</div>
            </div>
          </div>
        </div>
      )}

      {/* Help Section */}
      <div className="mt-8 roman-column rounded-lg p-6 bg-gray-50">
        <h3 className="font-semibold text-gray-900 mb-2">About the Archive:</h3>
        <ul className="text-sm text-gray-800 space-y-1">
          <li>• Every weekly edition is automatically saved to your archive</li>
          <li>• Use the search function to find specific weeks or editions</li>
          <li>• Click "Read" to view any past edition in the flipbook format</li>
          <li>• Archives are preserved permanently for your newspaper history</li>
          <li>• Share archive links with friends to show them past editions</li>
        </ul>
      </div>
    </div>
  );
};

export default Archive;