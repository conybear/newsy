import React, { useState, useEffect } from 'react';
import { Users, Plus, Trash2, UserCheck } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const Contributors = () => {
  const [contributors, setContributors] = useState([]);
  const [receivedInvitations, setReceivedInvitations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [contributorsResponse, invitationsResponse] = await Promise.all([
        axios.get(`${API_BASE}/api/contributors/my`),
        axios.get(`${API_BASE}/api/invitations/received`)
      ]);

      setContributors(contributorsResponse.data);
      setReceivedInvitations(invitationsResponse.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleAddContributor = async (invitationId) => {
    try {
      await axios.post(`${API_BASE}/api/contributors/add`, {
        invitation_id: invitationId
      });
      setMessage('Contributor added successfully');
      fetchData();
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to add contributor');
    }
  };

  const handleRemoveContributor = async (contributorId) => {
    if (!window.confirm('Are you sure you want to remove this contributor?')) {
      return;
    }

    try {
      await axios.delete(`${API_BASE}/api/contributors/${contributorId}`);
      setMessage('Contributor removed successfully');
      fetchData();
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to remove contributor');
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="roman-header text-xl">Loading contributors...</div>
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="roman-header text-3xl font-bold mb-2">
          My Contributors
        </h1>
        <p className="text-gray-600 text-lg">
          Manage who contributes stories to your weekly newspaper
        </p>
      </div>

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

      {/* Add Contributors Section */}
      {receivedInvitations.length > 0 && (
        <div className="roman-column rounded-lg p-6 mb-8">
          <h2 className="roman-header text-xl font-semibold mb-4 flex items-center">
            <Plus className="w-5 h-5 mr-2" />
            Available to Add ({receivedInvitations.length})
          </h2>
          <p className="text-gray-600 mb-4">
            People who have invited you and are available to add as contributors:
          </p>
          
          <div className="space-y-4">
            {receivedInvitations.map((invitation) => {
              const isAlreadyContributor = contributors.some(
                c => c.contributor_id === invitation.from_user_id
              );
              
              return (
                <div key={invitation.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center">
                        <Users className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{invitation.from_user_name}</p>
                        <p className="text-sm text-gray-500">{invitation.from_user_email}</p>
                      </div>
                    </div>
                    {isAlreadyContributor ? (
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium text-green-600 bg-green-100">
                        <UserCheck className="w-4 h-4 mr-1" />
                        Already Added
                      </span>
                    ) : (
                      <button
                        onClick={() => handleAddContributor(invitation.id)}
                        className="roman-button text-sm px-4 py-2"
                      >
                        <Plus className="w-4 h-4 mr-1" />
                        Add as Contributor
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Current Contributors */}
      <div className="roman-column rounded-lg p-6">
        <h2 className="roman-header text-xl font-semibold mb-4 flex items-center">
          <Users className="w-5 h-5 mr-2" />
          Current Contributors ({contributors.length})
        </h2>

        {contributors.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="font-medium">No contributors yet</p>
            <p className="text-sm">
              {receivedInvitations.length > 0 
                ? 'Add contributors from the section above'
                : 'Invite friends first, then add them as contributors'
              }
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {contributors.map((contributor) => (
              <div key={contributor.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center">
                      <Users className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{contributor.contributor_name}</p>
                      <p className="text-sm text-gray-500">{contributor.contributor_email}</p>
                      <p className="text-xs text-gray-400">
                        Added {new Date(contributor.added_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleRemoveContributor(contributor.contributor_id)}
                    className="text-red-600 hover:text-red-800 p-2 rounded-full hover:bg-red-50 transition-colors"
                    title="Remove contributor"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="mt-8 roman-column rounded-lg p-6 bg-green-50">
        <h3 className="font-semibold text-green-900 mb-2">About Contributors:</h3>
        <ul className="text-sm text-green-800 space-y-1">
          <li>• Contributors can submit one story per week to your newspaper</li>
          <li>• Stories must be submitted by Monday 11:59 PM EST</li>
          <li>• Contributors only appear in YOUR newspaper - they manage their own contributor lists</li>
          <li>• You can have up to 50 contributors in your network</li>
        </ul>
      </div>
    </div>
  );
};

export default Contributors;