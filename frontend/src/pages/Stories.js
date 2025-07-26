import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import StoryForm from '../components/StoryForm';
import { Edit3, Calendar, Image as ImageIcon, Star, RefreshCw } from 'lucide-react';

const Stories = () => {
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [hasSubmittedThisWeek, setHasSubmittedThisWeek] = useState(false);

  const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;

  useEffect(() => {
    fetchMyStories();
  }, []);

  const fetchMyStories = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/stories/my`);
      setStories(response.data);
      
      // Check if user has submitted a story this week
      const currentWeek = getCurrentWeek();
      const hasStoryThisWeek = response.data.some(story => story.week_of === currentWeek);
      setHasSubmittedThisWeek(hasStoryThisWeek);
    } catch (error) {
      console.error('Failed to fetch stories:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCurrentWeek = () => {
    // Match backend calculation exactly
    const now = new Date();
    return now.toLocaleDateString('en-CA', { 
      year: 'numeric', 
      month: '2-digit', 
      day: '2-digit' 
    }).replace(/-/g, '') + '-W' + 
    String(Math.ceil((now.getTime() - new Date(now.getFullYear(), 0, 1).getTime()) / (7 * 24 * 60 * 60 * 1000))).padStart(2, '0');
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const onStoryCreated = () => {
    setShowForm(false);
    fetchMyStories();
  };

  if (loading) {
    return (
      <Layout currentPage="stories">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout currentPage="stories">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Stories</h1>
            <p className="text-gray-600 mt-1">Manage your weekly submissions</p>
          </div>
          
          {!hasSubmittedThisWeek && (
            <button
              onClick={() => setShowForm(!showForm)}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Edit3 className="h-5 w-5" />
              <span>Write Story</span>
            </button>
          )}
        </div>

        {/* Submission status */}
        <div className={`rounded-lg p-4 ${
          hasSubmittedThisWeek 
            ? 'bg-green-50 border border-green-200' 
            : 'bg-yellow-50 border border-yellow-200'
        }`}>
          <div className="flex items-center space-x-2">
            {hasSubmittedThisWeek ? (
              <>
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm font-medium text-green-800">
                  You've submitted your story for this week!
                </span>
              </>
            ) : (
              <>
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <span className="text-sm font-medium text-yellow-800">
                  You haven't submitted a story this week yet. Deadline is Monday!
                </span>
              </>
            )}
          </div>
        </div>

        {/* Story form */}
        {showForm && (
          <StoryForm onStoryCreated={onStoryCreated} />
        )}

        {/* Stories list */}
        {stories.length === 0 ? (
          <div className="text-center py-12">
            <Edit3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No stories yet</h3>
            <p className="text-gray-500 mb-4">Start by writing your first weekly story!</p>
            {!hasSubmittedThisWeek && (
              <button
                onClick={() => setShowForm(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Write Your First Story
              </button>
            )}
          </div>
        ) : (
          <div className="grid gap-6">
            {stories.map((story) => (
              <div key={story.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="text-xl font-bold text-gray-900">{story.title}</h3>
                      {story.is_headline && (
                        <span className="inline-flex items-center px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded">
                          <Star className="h-3 w-3 mr-1" />
                          HEADLINE
                        </span>
                      )}
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <div className="flex items-center space-x-1">
                        <Calendar className="h-4 w-4" />
                        <span>{formatDate(story.created_at)}</span>
                      </div>
                      {story.images?.length > 0 && (
                        <div className="flex items-center space-x-1">
                          <ImageIcon className="h-4 w-4" />
                          <span>{story.images.length} image{story.images.length > 1 ? 's' : ''}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Images */}
                {story.images?.length > 0 && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    {story.images.map((image) => (
                      <img
                        key={image.id}
                        src={`data:${image.content_type};base64,${image.data}`}
                        alt={image.filename}
                        className="w-full h-32 object-cover rounded-lg"
                      />
                    ))}
                  </div>
                )}

                <div className="text-gray-700 leading-relaxed">
                  {story.content.length > 300 
                    ? `${story.content.substring(0, 300)}...` 
                    : story.content
                  }
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Stories;