import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { Users, UserPlus, Mail, Search, Check, X } from 'lucide-react';

const Friends = () => {
  const [friends, setFriends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddFriend, setShowAddFriend] = useState(false);
  const [email, setEmail] = useState('');
  const [addingFriend, setAddingFriend] = useState(false);
  const [error, setError] = useState('');

  const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;

  useEffect(() => {
    fetchFriends();
  }, []);

  const fetchFriends = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/friends`);
      setFriends(response.data);
    } catch (error) {
      console.error('Failed to fetch friends:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddFriend = async (e) => {
    e.preventDefault();
    setAddingFriend(true);
    setError('');

    try {
      await axios.post(`${API_BASE}/friends/request`, { email });
      setEmail('');
      setShowAddFriend(false);
      fetchFriends();
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to add friend');
    } finally {
      setAddingFriend(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <Layout currentPage="friends">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Friends</h1>
            <p className="text-gray-600 mt-1">Manage your newspaper contributors</p>
          </div>
          
          <button
            onClick={() => setShowAddFriend(!showAddFriend)}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <UserPlus className="h-5 w-5" />
            <span>Add Friend</span>
          </button>
        </div>

        {/* Friend limit warning */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <Users className="h-5 w-5 text-blue-600" />
            <div>
              <h3 className="text-sm font-medium text-blue-800">
                Friends: {friends.length}/50
              </h3>
              <p className="text-sm text-blue-600 mt-1">
                You can have up to 50 friends who can contribute to your weekly editions.
              </p>
            </div>
          </div>
        </div>

        {/* Add friend form */}
        {showAddFriend && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Add a Friend</h3>
            
            <form onSubmit={handleAddFriend} className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Friend's Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                  <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter their email address"
                  />
                </div>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <div className="text-sm text-red-600">{error}</div>
                </div>
              )}

              <div className="flex space-x-3">
                <button
                  type="submit"
                  disabled={addingFriend}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  <Check className="h-4 w-4" />
                  <span>{addingFriend ? 'Adding...' : 'Add Friend'}</span>
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddFriend(false)}
                  className="flex items-center space-x-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  <X className="h-4 w-4" />
                  <span>Cancel</span>
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Friends list */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : friends.length === 0 ? (
          <div className="text-center py-12">
            <Users className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No friends yet</h3>
            <p className="text-gray-500 mb-4">Add friends to start building your social newspaper network!</p>
            <button
              onClick={() => setShowAddFriend(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Add Your First Friend
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Your Friends</h3>
            </div>
            <div className="divide-y divide-gray-200">
              {friends.map((friend) => (
                <div key={friend.id} className="px-6 py-4 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-medium">
                        {friend.full_name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">{friend.full_name}</h4>
                      <p className="text-sm text-gray-500">{friend.email}</p>
                    </div>
                  </div>
                  <div className="text-sm text-gray-500">
                    Joined {formatDate(friend.created_at)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Contributors note */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-900 mb-2">About Contributors</h3>
          <p className="text-sm text-gray-600">
            All your friends are automatically contributors to your weekly edition. 
            Their stories will appear in your newspaper each week when they submit them.
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default Friends;