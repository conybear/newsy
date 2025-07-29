import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { Search, Users, BookOpen, Database } from 'lucide-react';

const DebugPage = () => {
  const [debugData, setDebugData] = useState(null);
  const [loading, setLoading] = useState(false);

  const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;

  const runDiagnostics = async () => {
    setLoading(true);
    try {
      // Get current user info
      const userResponse = await axios.get(`${API_BASE}/users/me`);
      const currentUser = userResponse.data;

      // Get friends list
      const friendsResponse = await axios.get(`${API_BASE}/friends`);
      const friends = friendsResponse.data;

      // Get my stories
      const myStoriesResponse = await axios.get(`${API_BASE}/stories/my`);
      const myStories = myStoriesResponse.data;

      // Get current edition
      const editionResponse = await axios.get(`${API_BASE}/editions/current`);
      const edition = editionResponse.data;

      setDebugData({
        currentUser,
        friends,
        myStories,
        edition
      });
    } catch (error) {
      console.error('Debug failed:', error);
      setDebugData({ error: error.message });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runDiagnostics();
  }, []);

  if (loading) {
    return (
      <Layout currentPage="debug">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  if (!debugData) {
    return (
      <Layout currentPage="debug">
        <div className="text-center">
          <button
            onClick={runDiagnostics}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg"
          >
            Run Diagnostics
          </button>
        </div>
      </Layout>
    );
  }

  if (debugData.error) {
    return (
      <Layout currentPage="debug">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="text-red-600">Error: {debugData.error}</div>
        </div>
      </Layout>
    );
  }

  const { currentUser, friends, myStories, edition } = debugData;

  return (
    <Layout currentPage="debug">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900">🔍 Debug Dashboard</h1>
          <button
            onClick={runDiagnostics}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Refresh Data
          </button>
        </div>

        {/* Current User Info */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <Users className="h-5 w-5 mr-2" />
            Your Account Info
          </h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <strong>Name:</strong> {currentUser?.full_name}
            </div>
            <div>
              <strong>Email:</strong> {currentUser?.email}
            </div>
            <div>
              <strong>User ID:</strong> {currentUser?.id}
            </div>
            <div>
              <strong>Created:</strong> {new Date(currentUser?.created_at).toLocaleDateString()}
            </div>
            <div>
              <strong>Friends Count:</strong> {currentUser?.friends?.length || 0}
            </div>
            <div>
              <strong>Contributors Count:</strong> {currentUser?.contributors?.length || 0}
            </div>
          </div>
          
          <div className="mt-4">
            <h3 className="font-semibold mb-2">Friend IDs:</h3>
            <div className="bg-gray-100 p-2 rounded text-xs font-mono">
              {JSON.stringify(currentUser?.friends || [], null, 2)}
            </div>
          </div>
          
          <div className="mt-4">
            <h3 className="font-semibold mb-2">Contributor IDs:</h3>
            <div className="bg-gray-100 p-2 rounded text-xs font-mono">
              {JSON.stringify(currentUser?.contributors || [], null, 2)}
            </div>
          </div>
        </div>

        {/* Friends List */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <Users className="h-5 w-5 mr-2" />
            Your Friends ({friends?.length || 0})
          </h2>
          {friends?.length > 0 ? (
            <div className="space-y-3">
              {friends.map((friend) => (
                <div key={friend.id} className="border rounded p-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-semibold">{friend.full_name}</div>
                      <div className="text-sm text-gray-600">{friend.email}</div>
                      <div className="text-xs text-gray-500 font-mono">ID: {friend.id}</div>
                    </div>
                    <div className="text-sm text-gray-500">
                      Joined: {new Date(friend.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-500">No friends found</div>
          )}
        </div>

        {/* My Stories */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <BookOpen className="h-5 w-5 mr-2" />
            Your Stories ({myStories?.length || 0})
          </h2>
          {myStories?.length > 0 ? (
            <div className="space-y-3">
              {myStories.map((story) => (
                <div key={story.id} className="border rounded p-3">
                  <div className="font-semibold">{story.title}</div>
                  <div className="text-sm text-gray-600">
                    Week: {story.week_of} | 
                    Created: {new Date(story.created_at).toLocaleDateString()} |
                    Images: {story.images?.length || 0} |
                    {story.is_headline ? ' HEADLINE' : ' Regular'}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {story.content.substring(0, 100)}...
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-500">No stories found</div>
          )}
        </div>

        {/* Weekly Edition */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <Database className="h-5 w-5 mr-2" />
            Weekly Edition Debug
          </h2>
          
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <strong>Edition Week:</strong> {edition?.week_of}
            </div>
            <div>
              <strong>Stories in Edition:</strong> {edition?.stories?.length || 0}
            </div>
            <div>
              <strong>Edition ID:</strong> {edition?.id}
            </div>
            <div>
              <strong>Created:</strong> {edition?.created_at ? new Date(edition.created_at).toLocaleDateString() : 'N/A'}
            </div>
          </div>

          <div className="mb-4">
            <h3 className="font-semibold mb-2">Stories in Edition:</h3>
            {edition?.stories?.length > 0 ? (
              <div className="space-y-2">
                {edition.stories.map((story, index) => (
                  <div key={story.id} className="bg-gray-50 p-3 rounded">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-semibold">
                          {index + 1}. {story.title}
                          {story.is_headline && <span className="ml-2 px-2 py-1 bg-red-100 text-red-800 text-xs rounded">HEADLINE</span>}
                        </div>
                        <div className="text-sm text-gray-600">
                          By: {story.author_name} | Week: {story.week_of}
                        </div>
                        <div className="text-xs text-gray-500 font-mono">
                          Author ID: {story.author_id}
                        </div>
                      </div>
                      <div className="text-sm text-gray-500">
                        {story.images?.length || 0} images
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-gray-500 bg-yellow-50 p-3 rounded">
                ⚠️ No stories in edition - This is the problem!
              </div>
            )}
          </div>

          {/* Analysis */}
          <div className="bg-blue-50 border border-blue-200 rounded p-4">
            <h3 className="font-semibold text-blue-800 mb-2">🔍 Analysis</h3>
            <div className="text-sm text-blue-700 space-y-1">
              <div>• Contributors in your account: {currentUser?.contributors?.length || 0}</div>
              <div>• Friends in your account: {currentUser?.friends?.length || 0}</div>
              <div>• Your stories: {myStories?.length || 0}</div>
              <div>• Stories in edition: {edition?.stories?.length || 0}</div>
              
              {(currentUser?.contributors?.length || 0) === 0 && (
                <div className="text-red-600 font-semibold">
                  ❌ Problem: No contributors! Friends aren't being added as contributors.
                </div>
              )}
              
              {(currentUser?.friends?.length || 0) > 0 && (currentUser?.contributors?.length || 0) === 0 && (
                <div className="text-orange-600 font-semibold">
                  ⚠️ You have friends but no contributors - this is the bug!
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default DebugPage;