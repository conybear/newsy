import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Users, 
  UserPlus, 
  PenTool, 
  Newspaper, 
  Clock,
  Calendar,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    contributors: 0,
    pendingInvitations: 0,
    thisWeekStory: false,
    submissionsOpen: true,
    currentWeek: '',
    nextDeadline: ''
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch health check for submission status
      const healthResponse = await axios.get(`${API_BASE}/api/health`);
      const healthData = healthResponse.data;

      // Fetch contributors count
      const contributorsResponse = await axios.get(`${API_BASE}/api/contributors/my`);
      const contributors = contributorsResponse.data;

      // Fetch sent invitations
      const invitationsResponse = await axios.get(`${API_BASE}/api/invitations/sent`);
      const invitations = invitationsResponse.data;
      const pendingInvitations = invitations.filter(inv => inv.status === 'pending').length;

      setStats({
        contributors: contributors.length,
        pendingInvitations,
        thisWeekStory: false, // TODO: Check if user has submitted story this week
        submissionsOpen: healthData.submissions_open,
        currentWeek: healthData.current_week,
        nextDeadline: 'Monday 11:59 PM EST' // TODO: Calculate actual deadline
      });
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="roman-header text-xl">Loading dashboard...</div>
      </div>
    );
  }

  const quickActions = [
    {
      title: 'Invite Friends',
      description: 'Send invitations to join your network',
      icon: UserPlus,
      link: '/invitations',
      color: 'bg-blue-500',
      count: stats.pendingInvitations > 0 ? `${stats.pendingInvitations} pending` : null
    },
    {
      title: 'Manage Contributors',
      description: 'Add or remove story contributors',
      icon: Users,
      link: '/contributors',
      color: 'bg-green-500',
      count: `${stats.contributors} active`
    },
    {
      title: 'Write Story',
      description: stats.submissionsOpen ? 'Submit your weekly story' : 'Submissions closed',
      icon: PenTool,
      link: '/stories',
      color: stats.submissionsOpen ? 'bg-purple-500' : 'bg-gray-400',
      disabled: !stats.submissionsOpen
    },
    {
      title: 'Read Newspaper',
      description: 'View the latest published edition',
      icon: Newspaper,
      link: '/newspaper',
      color: 'bg-yellow-600'
    }
  ];

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="roman-header text-3xl font-bold mb-2">
          Welcome back, {user?.full_name}
        </h1>
        <p className="text-gray-600 text-lg">
          Ready to share your story with the world?
        </p>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="roman-column rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Current Week</p>
              <p className="text-2xl font-bold roman-accent">{stats.currentWeek}</p>
            </div>
            <Calendar className="h-8 w-8 text-yellow-600" />
          </div>
        </div>

        <div className="roman-column rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Submissions</p>
              <p className={`text-2xl font-bold ${stats.submissionsOpen ? 'text-green-600' : 'text-red-600'}`}>
                {stats.submissionsOpen ? 'Open' : 'Closed'}
              </p>
            </div>
            {stats.submissionsOpen ? (
              <CheckCircle className="h-8 w-8 text-green-600" />
            ) : (
              <AlertCircle className="h-8 w-8 text-red-600" />
            )}
          </div>
        </div>

        <div className="roman-column rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Contributors</p>
              <p className="text-2xl font-bold roman-accent">{stats.contributors}</p>
            </div>
            <Users className="h-8 w-8 text-yellow-600" />
          </div>
        </div>

        <div className="roman-column rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Next Deadline</p>
              <p className="text-sm font-bold text-gray-800">{stats.nextDeadline}</p>
            </div>
            <Clock className="h-8 w-8 text-yellow-600" />
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="roman-header text-2xl font-bold mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {quickActions.map((action, index) => {
            const Icon = action.icon;
            return (
              <Link
                key={index}
                to={action.link}
                className={`group block ${action.disabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer hover:shadow-lg'} transition-all duration-200`}
                onClick={(e) => action.disabled && e.preventDefault()}
              >
                <div className="roman-column rounded-lg p-6 h-full">
                  <div className="flex items-center justify-between mb-4">
                    <div className={`p-3 rounded-lg ${action.color}`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    {action.count && (
                      <span className="text-xs bg-gray-100 px-2 py-1 rounded-full text-gray-600">
                        {action.count}
                      </span>
                    )}
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">{action.title}</h3>
                  <p className="text-sm text-gray-600">{action.description}</p>
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="roman-column rounded-lg p-6">
        <h2 className="roman-header text-xl font-bold mb-4">Getting Started</h2>
        <div className="space-y-4">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-yellow-800">1</span>
            </div>
            <div>
              <p className="font-medium text-gray-900">Invite your friends</p>
              <p className="text-sm text-gray-600">Send email invitations to up to 50 friends who will contribute stories</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-yellow-800">2</span>
            </div>
            <div>
              <p className="font-medium text-gray-900">Add contributors</p>
              <p className="text-sm text-gray-600">Once friends accept, add them as contributors to include their stories</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-yellow-800">3</span>
            </div>
            <div>
              <p className="font-medium text-gray-900">Write and submit stories</p>
              <p className="text-sm text-gray-600">Everyone submits one story per week by Monday 11:59 PM EST</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-yellow-800">4</span>
            </div>
            <div>
              <p className="font-medium text-gray-900">Read your newspaper</p>
              <p className="text-sm text-gray-600">Every Tuesday at 8:00 AM EST, your personalized newspaper is published</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;