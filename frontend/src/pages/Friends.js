import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { Users, UserPlus, Mail, Search, Check, X, Clock, Send } from 'lucide-react';

const Friends = () => {
  const [friends, setFriends] = useState([]);
  const [pendingInvitations, setPendingInvitations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [email, setEmail] = useState('');
  const [sendingInvite, setSendingInvite] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;

  useEffect(() => {
    fetchFriends();
    fetchPendingInvitations();
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

  const fetchPendingInvitations = async () => {
    try {
      const response = await axios.get(`${API_BASE}/friends/invitations`);
      setPendingInvitations(response.data);
    } catch (error) {
      console.error('Failed to fetch invitations:', error);
    }
  };

  const handleSendInvite = async (e) => {
    e.preventDefault();
    setSendingInvite(true);
    setError('');
    setSuccessMessage('');

    try {
      const response = await axios.post(`${API_BASE}/friends/invite`, { email });
      setSuccessMessage(response.data.message);
      setEmail('');
      setShowInviteForm(false);
      fetchFriends();
      fetchPendingInvitations();
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to send invitation');
    } finally {
      setSendingInvite(false);
    }
  };

  const handleCancelInvitation = async (invitationId) => {
    try {
      await axios.delete(`${API_BASE}/friends/invitations/${invitationId}`);
      fetchPendingInvitations();
    } catch (error) {
      console.error('Failed to cancel invitation:', error);
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
            onClick={() => setShowInviteForm(!showInviteForm)}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <UserPlus className="h-5 w-5" />
            <span>Invite Friend</span>
          </button>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <Check className="h-5 w-5 text-green-600" />
              <div className="text-sm text-green-800">{successMessage}</div>
            </div>
          </div>
        )}

        {/* Friend limit warning */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <Users className="h-5 w-5 text-blue-600" />
            <div>
              <h3 className="text-sm font-medium text-blue-800">
                Friends: {friends.length}/50
              </h3>
              <p className="text-sm text-blue-600 mt-1">
                You can invite up to 50 friends who can contribute to your weekly editions.
              </p>
            </div>
          </div>
        </div>

        {/* Invite form */}
        {showInviteForm && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Invite a Friend</h3>
            
            <form onSubmit={handleSendInvite} className="space-y-4">
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
                <p className="text-sm text-gray-500 mt-2">
                  💡 If they don't have an account yet, they'll receive an invitation and will be automatically added as your friend when they sign up!
                </p>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <div className="text-sm text-red-600">{error}</div>
                </div>
              )}

              <div className="flex space-x-3">
                <button
                  type="submit"
                  disabled={sendingInvite}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  <Send className="h-4 w-4" />
                  <span>{sendingInvite ? 'Sending...' : 'Send Invitation'}</span>
                </button>
                <button
                  type="button"
                  onClick={() => setShowInviteForm(false)}
                  className="flex items-center space-x-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  <X className="h-4 w-4" />
                  <span>Cancel</span>
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Pending Invitations */}
        {pendingInvitations.length > 0 && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900 flex items-center">
                <Clock className="h-5 w-5 mr-2 text-yellow-500" />
                Pending Invitations ({pendingInvitations.length})
              </h3>
            </div>
            <div className="divide-y divide-gray-200">
              {pendingInvitations.map((invitation) => (
                <div key={invitation.id} className="px-6 py-4 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
                      <Mail className="h-5 w-5 text-yellow-600" />
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">{invitation.to_email}</h4>
                      <p className="text-sm text-gray-500">
                        Invited {formatDate(invitation.created_at)}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleCancelInvitation(invitation.id)}
                    className="text-sm text-red-600 hover:text-red-700"
                  >
                    Cancel
                  </button>
                </div>
              ))}
            </div>
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
            <p className="text-gray-500 mb-4">Invite friends to start building your social newspaper network!</p>
            <button
              onClick={() => setShowInviteForm(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Invite Your First Friend
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Your Friends ({friends.length})</h3>
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

        {/* How it works */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-900 mb-2">How Friend Invitations Work</h3>
          <div className="text-sm text-gray-600 space-y-1">
            <p>• <strong>Existing Users:</strong> If they already have an account, they'll be added as a friend immediately</p>
            <p>• <strong>New Users:</strong> They'll receive an invitation and become your friend automatically when they sign up</p>
            <p>• <strong>Weekly Editions:</strong> All your friends' stories will appear in your weekly newspaper</p>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Friends;