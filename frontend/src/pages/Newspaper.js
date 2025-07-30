import React, { useState, useEffect } from 'react';
import { 
  Newspaper as NewspaperIcon, 
  RefreshCw, 
  AlertCircle, 
  Download,
  Share2,
  Clock,
  CheckCircle
} from 'lucide-react';
import axios from 'axios';
import FlipBook from '../components/FlipBook';
import NewspaperStats from '../components/NewspaperStats';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const Newspaper = () => {
  const [newspaper, setNewspaper] = useState(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [currentPage, setCurrentPage] = useState(0);

  useEffect(() => {
    fetchCurrentNewspaper();
  }, []);

  const fetchCurrentNewspaper = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await axios.get(`${API_BASE}/api/newspapers/current`);
      setNewspaper(response.data);
      
      // Show success message if newspaper has stories
      if (response.data.stories && response.data.stories.length > 0) {
        setMessage(`Loaded ${response.data.stories.length} stories from ${[...new Set(response.data.stories.map(s => s.author_name))].length} contributors`);
        setTimeout(() => setMessage(''), 5000);
      }
    } catch (error) {
      console.error('Failed to fetch newspaper:', error);
      setError(error.response?.data?.detail || 'Failed to load newspaper');
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerateNewspaper = async () => {
    try {
      setRegenerating(true);
      setError('');
      
      const response = await axios.post(`${API_BASE}/api/newspapers/regenerate`);
      setNewspaper(response.data.newspaper);
      setMessage('Newspaper regenerated successfully!');
      setTimeout(() => setMessage(''), 5000);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to regenerate newspaper');
    } finally {
      setRegenerating(false);
    }
  };

  const handleShare = async () => {
    if (navigator.share && newspaper) {
      try {
        await navigator.share({
          title: newspaper.title,
          text: `Check out this week's ${newspaper.title} - ${newspaper.stories.length} stories from our contributors!`,
          url: window.location.href
        });
      } catch (error) {
        // Fallback to copying URL
        navigator.clipboard.writeText(window.location.href);
        setMessage('Link copied to clipboard!');
        setTimeout(() => setMessage(''), 3000);
      }
    } else {
      // Fallback to copying URL
      navigator.clipboard.writeText(window.location.href);
      setMessage('Link copied to clipboard!');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const isPublished = () => {
    if (!newspaper) return false;
    const publishDate = new Date(newspaper.published_at);
    const now = new Date();
    return now >= publishDate;
  };

  const getPublicationStatus = () => {
    if (!newspaper) return null;
    
    const now = new Date();
    const publishDate = new Date(newspaper.published_at);
    
    if (now >= publishDate) {
      return {
        status: 'published',
        icon: CheckCircle,
        text: 'Published',
        color: 'text-green-600'
      };
    } else {
      return {
        status: 'pending',
        icon: Clock,
        text: 'Publishing Tuesday 8:00 AM EST',
        color: 'text-yellow-600'
      };
    }
  };

  if (loading) {
    return (
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="loading">
          <div className="roman-header text-xl">Loading your newspaper...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="roman-header text-3xl font-bold mb-2">
              Weekly Newspaper
            </h1>
            <p className="text-gray-600 text-lg">
              Your personalized Acta Diurna edition
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            {newspaper && getPublicationStatus() && (
              <div className={`flex items-center space-x-2 ${getPublicationStatus().color}`}>
                {React.createElement(getPublicationStatus().icon, { className: "w-5 h-5" })}
                <span className="font-medium">{getPublicationStatus().text}</span>
              </div>
            )}
            
            <button
              onClick={handleRegenerateNewspaper}
              disabled={regenerating}
              className="flex items-center space-x-2 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors disabled:opacity-50"
            >
              {regenerating ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4" />
              )}
              <span>{regenerating ? 'Regenerating...' : 'Refresh'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Messages */}
      {message && (
        <div className="success mb-6">
          {message}
        </div>
      )}

      {error && (
        <div className="error mb-6">
          {error}
        </div>
      )}

      {/* No Stories State */}
      {newspaper && (!newspaper.stories || newspaper.stories.length === 0) && (
        <div className="roman-column rounded-lg p-8 text-center">
          <NewspaperIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="roman-header text-2xl font-semibold mb-4">
            No Stories This Week
          </h2>
          <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
            There are no submitted stories for this week yet. 
            {newspaper.week_of && (
              <>
                <br />
                <strong>Week {newspaper.week_of}</strong> - Stories will appear here once contributors submit them.
              </>
            )}
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={handleRegenerateNewspaper}
              className="roman-button"
            >
              Check for New Stories
            </button>
          </div>
        </div>
      )}

      {/* Newspaper with Stories */}
      {newspaper && newspaper.stories && newspaper.stories.length > 0 && (
        <div className="space-y-6">
          {/* Newspaper Stats */}
          <NewspaperStats newspaper={newspaper} />
          
          {/* Action Bar */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h2 className="roman-header text-xl font-semibold">
                {newspaper.title}
              </h2>
              <span className="text-gray-500">•</span>
              <span className="text-gray-600">
                Page {currentPage + 1}
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={handleShare}
                className="flex items-center space-x-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded transition-colors"
                title="Share newspaper"
              >
                <Share2 className="w-4 h-4" />
                <span className="hidden sm:inline">Share</span>
              </button>
            </div>
          </div>

          {/* FlipBook */}
          <div className="bg-gray-50 p-6 rounded-lg">
            <FlipBook 
              newspaper={newspaper}
              onPageChange={setCurrentPage}
            />
          </div>

          {/* Story Summary */}
          <div className="roman-column rounded-lg p-6">
            <h3 className="roman-header text-lg font-semibold mb-4">
              Stories in This Edition
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              {newspaper.stories.map((story, index) => (
                <div key={story.id || index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-900 mb-1">
                        {story.headline}
                      </h4>
                      <p className="text-sm text-gray-600 mb-2">
                        {story.title}
                      </p>
                      <p className="text-xs text-gray-500">
                        By {story.author_name}
                      </p>
                    </div>
                    {story.images && story.images.length > 0 && (
                      <div className="ml-4">
                        <img
                          src={`data:${story.images[0].content_type};base64,${story.images[0].data}`}
                          alt={story.images[0].filename}
                          className="w-16 h-16 object-cover rounded"
                        />
                      </div>
                    )}
                  </div>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>
                      {story.images ? story.images.length : 0} images
                    </span>
                    <span>
                      ~{Math.ceil((story.content.replace(/<[^>]*>/g, '').length || 0) / 1000)} min read
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Publication Schedule Info */}
      <div className="mt-8 roman-column rounded-lg p-6 bg-blue-50">
        <h3 className="font-semibold text-blue-900 mb-2">Publication Schedule:</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Stories must be submitted by Monday 11:59 PM EST</li>
          <li>• Newspapers are automatically published Tuesday 8:00 AM EST</li>
          <li>• Each edition includes stories from all your contributors</li>
          <li>• Use the "Refresh" button to check for newly submitted stories</li>
          <li>• Past editions are archived and can be viewed anytime</li>
        </ul>
      </div>
    </div>
  );
};

export default Newspaper;