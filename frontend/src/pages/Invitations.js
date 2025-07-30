import React, { useState, useEffect } from 'react';
import { Mail, Send, Check, X, User } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const Invitations = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [sentInvitations, setSentInvitations] = useState([]);

  useEffect(() => {
    fetchSentInvitations();
  }, []);

  const fetchSentInvitations = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/invitations/sent`);
      setSentInvitations(response.data);
    } catch (error) {
      console.error('Failed to fetch invitations:', error);
    }
  };

  const handleSendInvitation = async (e) => {
    e.preventDefault();
    if (!email.trim()) return;

    setLoading(true);
    setError('');
    setMessage('');

    try {
      await axios.post(`${API_BASE}/api/invitations/send`, { email });
      setMessage(`Invitation sent to ${email}`);
      setEmail('');
      fetchSentInvitations();
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to send invitation');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      case 'accepted': return 'text-green-600 bg-green-100';
      case 'declined': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return <Send className="w-4 h-4" />;
      case 'accepted': return <Check className="w-4 h-4" />;
      case 'declined': return <X className="w-4 h-4" />;
      default: return <Mail className="w-4 h-4" />;
    }
  };

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="roman-header text-3xl font-bold mb-2">
          Invite Friends
        </h1>
        <p className="text-gray-600 text-lg">
          Invite up to 50 friends to join your Acta Diurna network
        </p>
      </div>

      {/* Send Invitation Form */}
      <div className="roman-column rounded-lg p-6 mb-8">
        <h2 className="roman-header text-xl font-semibold mb-4 flex items-center">
          <Mail className="w-5 h-5 mr-2" />
          Send New Invitation
        </h2>

        {message && (
          <div className="success mb-4">
            {message}
          </div>
        )}

        {error && (
          <div className="error mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSendInvitation} className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter friend's email address"
              className="roman-input w-full"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="roman-button flex items-center justify-center px-6"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <Send className="w-4 h-4 mr-2" />
                Send Invitation
              </>
            )}
          </button>
        </form>
      </div>

      {/* Sent Invitations List */}
      <div className="roman-column rounded-lg p-6">
        <h2 className="roman-header text-xl font-semibold mb-4">
          Sent Invitations ({sentInvitations.length})
        </h2>

        {sentInvitations.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <User className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No invitations sent yet</p>
            <p className="text-sm">Send your first invitation above to get started</p>
          </div>
        ) : (
          <div className="space-y-4">
            {sentInvitations.map((invitation) => (
              <div key={invitation.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                      <User className="w-5 h-5 text-gray-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{invitation.to_email}</p>
                      <p className="text-sm text-gray-500">
                        Sent {new Date(invitation.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(invitation.status)}`}>
                    {getStatusIcon(invitation.status)}
                    <span className="ml-2 capitalize">{invitation.status}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Help Text */}
      <div className="mt-8 roman-column rounded-lg p-6 bg-blue-50">
        <h3 className="font-semibold text-blue-900 mb-2">How it works:</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Send email invitations to friends you want in your network</li>
          <li>• Friends will receive an email with a link to join Acta Diurna</li>
          <li>• Once they register, the invitation status will change to "accepted"</li>
          <li>• You can then add them as contributors to include their stories in your newspaper</li>
        </ul>
      </div>
    </div>
  );
};

export default Invitations;