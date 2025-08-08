import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// HomePage Component
const HomePage = () => {
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStories();
  }, []);

  const fetchStories = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/stories`);
      setStories(response.data);
    } catch (error) {
      console.error('Error fetching stories:', error);
      setError('Failed to load stories');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-amber-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Error</h2>
          <p className="text-gray-600">{error}</p>
          <button
            onClick={fetchStories}
            className="mt-4 px-4 py-2 bg-amber-600 text-white rounded hover:bg-amber-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-100">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-amber-600 to-orange-700 text-white py-20">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">📜 Acta Diurna</h1>
          <p className="text-xl mb-8 opacity-90">Your Personal Daily Chronicle</p>
          <p className="text-lg opacity-80">Share stories and read the latest news from your friends</p>
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-white shadow-lg">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <nav className="flex space-x-8">
            <Link to="/" className="text-amber-600 hover:text-amber-800 font-medium">
              Friend Stories
            </Link>
            <Link to="/submit" className="text-gray-600 hover:text-amber-800 font-medium">
              Share Story
            </Link>
            <Link to="/flipbook" className="text-gray-600 hover:text-amber-800 font-medium">
              Weekly Chronicle
            </Link>
            <Link to="/invite" className="text-gray-600 hover:text-amber-800 font-medium">
              Invite Friends
            </Link>
          </nav>
        </div>
      </div>

      {/* Stories Section */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">Latest Stories from Friends</h2>
          <p className="text-gray-600">Discover the most recent stories shared by your circle of friends</p>
        </div>

        {stories.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📖</div>
            <h3 className="text-xl font-semibold text-gray-600 mb-2">No stories yet from your friends</h3>
            <p className="text-gray-500 mb-6">Be the first to share a story with your circle!</p>
            <div className="space-x-4">
              <Link
                to="/submit"
                className="inline-block px-6 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors"
              >
                Share Your Story
              </Link>
              <Link
                to="/invite"
                className="inline-block px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
              >
                Invite Friends
              </Link>
            </div>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {stories.map((story) => (
              <div key={story.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow story-card">
                <div className="p-6">
                  <h3 className="text-xl font-bold text-gray-800 mb-3 line-clamp-2">
                    {story.title}
                  </h3>
                  <p className="text-gray-600 mb-4 line-clamp-3">
                    {story.content}
                  </p>
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span className="font-medium">By {story.author}</span>
                    <span>{new Date(story.timestamp).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Story Submission Component
const SubmitStory = () => {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    author: ''
  });
  const [drafts, setDrafts] = useState([]);
  const [selectedDraft, setSelectedDraft] = useState(null);
  const [loading, setLoading] = useState(false);
  const [draftLoading, setDraftLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [draftSuccess, setDraftSuccess] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDrafts();
  }, []);

  const fetchDrafts = async () => {
    try {
      const response = await axios.get(`${API}/drafts`);
      setDrafts(response.data);
    } catch (error) {
      console.error('Error fetching drafts:', error);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleContentChange = (content) => {
    setFormData({
      ...formData,
      content: content
    });
  };

  const formatText = (command) => {
    document.execCommand(command, false, null);
    const content = document.getElementById('contentEditor').innerHTML;
    handleContentChange(content);
  };

  const handleEditorInput = () => {
    const content = document.getElementById('contentEditor').innerHTML;
    handleContentChange(content);
  };

  const loadDraft = async (draftId) => {
    const draft = drafts.find(d => d.id === draftId);
    if (draft) {
      setFormData({
        title: draft.title,
        content: draft.content,
        author: draft.author
      });
      setSelectedDraft(draftId);
      // Update the editor content
      document.getElementById('contentEditor').innerHTML = draft.content;
    }
  };

  const saveDraft = async () => {
    if (!formData.title && !formData.content) {
      setError('Please add some content before saving a draft');
      return;
    }

    try {
      setDraftLoading(true);
      setError(null);
      
      if (selectedDraft) {
        // Update existing draft
        await axios.put(`${API}/drafts/${selectedDraft}`, formData);
      } else {
        // Create new draft
        await axios.post(`${API}/drafts`, formData);
      }
      
      setDraftSuccess(true);
      setTimeout(() => setDraftSuccess(false), 3000);
      await fetchDrafts(); // Refresh drafts list
    } catch (error) {
      console.error('Error saving draft:', error);
      setError('Failed to save draft. Please try again.');
    } finally {
      setDraftLoading(false);
    }
  };

  const deleteDraft = async (draftId) => {
    try {
      await axios.delete(`${API}/drafts/${draftId}`);
      await fetchDrafts(); // Refresh drafts list
      if (selectedDraft === draftId) {
        setSelectedDraft(null);
        setFormData({ title: '', content: '', author: '' });
        document.getElementById('contentEditor').innerHTML = '';
      }
    } catch (error) {
      console.error('Error deleting draft:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title || !formData.content) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await axios.post(`${API}/stories`, formData);
      setSuccess(true);
      setFormData({ title: '', content: '', author: '' });
      document.getElementById('contentEditor').innerHTML = '';
      
      // Delete draft if it was loaded
      if (selectedDraft) {
        await deleteDraft(selectedDraft);
      }
    } catch (error) {
      console.error('Error submitting story:', error);
      setError('Failed to submit story. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-amber-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg text-center max-w-md">
          <div className="text-6xl mb-4">✅</div>
          <h2 className="text-2xl font-bold text-green-600 mb-4">Story Shared!</h2>
          <p className="text-gray-600 mb-6">Your story has been successfully shared and will appear in your friends' chronicles.</p>
          <div className="space-y-3">
            <Link
              to="/"
              className="block w-full px-4 py-2 bg-amber-600 text-white rounded hover:bg-amber-700"
            >
              View All Stories
            </Link>
            <button
              onClick={() => setSuccess(false)}
              className="block w-full px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Share Another Story
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-100">
      <div className="max-w-4xl mx-auto px-6 py-12">
        <div className="grid lg:grid-cols-3 gap-8">
          
          {/* Drafts Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg p-6 sticky top-6">
              <h3 className="text-lg font-bold text-gray-800 mb-4">📝 Saved Drafts</h3>
              
              {drafts.length === 0 ? (
                <p className="text-gray-500 text-sm">No saved drafts yet</p>
              ) : (
                <div className="space-y-3">
                  {drafts.map((draft) => (
                    <div key={draft.id} className="border border-gray-200 rounded-lg p-3 hover:border-amber-300 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 cursor-pointer" onClick={() => loadDraft(draft.id)}>
                          <h4 className="font-semibold text-sm text-gray-800 mb-1 line-clamp-1">
                            {draft.title || 'Untitled Draft'}
                          </h4>
                          <p className="text-xs text-gray-500 mb-1">
                            By {draft.author || 'Anonymous'}
                          </p>
                          <p className="text-xs text-gray-400">
                            {new Date(draft.updated_at).toLocaleDateString()}
                          </p>
                        </div>
                        <button
                          onClick={() => deleteDraft(draft.id)}
                          className="text-red-400 hover:text-red-600 ml-2"
                          title="Delete draft"
                        >
                          ✕
                        </button>
                      </div>
                      {selectedDraft === draft.id && (
                        <div className="mt-2 px-2 py-1 bg-amber-100 text-amber-800 text-xs rounded">
                          Currently editing
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Main Form */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h1 className="text-3xl font-bold text-gray-800 mb-2">Share Your Story</h1>
              <p className="text-gray-600 mb-8">Share your experiences, thoughts, or news with your circle of friends</p>

              {error && (
                <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700">
                  {error}
                </div>
              )}

              {draftSuccess && (
                <div className="mb-6 p-4 bg-green-50 border-l-4 border-green-500 text-green-700">
                  Draft saved successfully!
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                    Story Title *
                  </label>
                  <input
                    type="text"
                    id="title"
                    name="title"
                    value={formData.title}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                    placeholder="What happened? Give your story a compelling title"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="author" className="block text-sm font-medium text-gray-700 mb-2">
                    Your Name
                  </label>
                  <input
                    type="text"
                    id="author"
                    name="author"
                    value={formData.author}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                    placeholder="Your name (optional - defaults to Anonymous)"
                  />
                </div>

                <div>
                  <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-2">
                    Your Story *
                  </label>
                  
                  {/* Rich Text Editor Toolbar */}
                  <div className="border border-gray-300 rounded-t-lg bg-gray-50 px-4 py-2 flex items-center space-x-2">
                    <button
                      type="button"
                      onClick={() => formatText('bold')}
                      className="px-3 py-1 bg-white border border-gray-300 rounded text-sm font-bold hover:bg-gray-100"
                      title="Bold"
                    >
                      B
                    </button>
                    <button
                      type="button"
                      onClick={() => formatText('italic')}
                      className="px-3 py-1 bg-white border border-gray-300 rounded text-sm italic hover:bg-gray-100"
                      title="Italic"
                    >
                      I
                    </button>
                    <button
                      type="button"
                      onClick={() => formatText('underline')}
                      className="px-3 py-1 bg-white border border-gray-300 rounded text-sm underline hover:bg-gray-100"
                      title="Underline"
                    >
                      U
                    </button>
                    <div className="text-gray-400 text-xs ml-4">
                      Select text and click formatting buttons
                    </div>
                  </div>
                  
                  {/* Rich Text Editor */}
                  <div
                    id="contentEditor"
                    contentEditable
                    onInput={handleEditorInput}
                    className="w-full min-h-[300px] px-4 py-3 border-l border-r border-b border-gray-300 rounded-b-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent resize-y overflow-y-auto"
                    style={{ outline: 'none' }}
                    data-placeholder="Share your story with your friends... What happened? How did it make you feel? What did you learn?"
                  />
                </div>

                <div className="flex gap-4">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 px-6 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-semibold"
                  >
                    {loading ? 'Sharing...' : 'Share Story'}
                  </button>
                  
                  <button
                    type="button"
                    onClick={saveDraft}
                    disabled={draftLoading}
                    className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {draftLoading ? 'Saving...' : 'Save Draft'}
                  </button>
                  
                  <Link
                    to="/"
                    className="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-center"
                  >
                    Cancel
                  </Link>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Flipbook Component
const Flipbook = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const openFlipbook = () => {
    window.open(`${API}/newspaper/flipbook`, '_blank');
  };

  useEffect(() => {
    // Just check if API is accessible
    const checkAPI = async () => {
      try {
        await axios.get(`${API}/`);
        setLoading(false);
      } catch (error) {
        setError('Unable to connect to the server');
        setLoading(false);
      }
    };
    checkAPI();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-amber-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Error</h2>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-100">
      <div className="max-w-4xl mx-auto px-6 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">📜 Weekly Chronicle</h1>
          <p className="text-xl text-gray-600">Experience this week's stories from your friends in an interactive chronicle format</p>
        </div>

        <div className="bg-white rounded-lg shadow-xl p-8 text-center">
          <div className="mb-8">
            <div className="text-8xl mb-4">📖</div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Your Friends' Weekly Chronicle</h2>
            <p className="text-gray-600 mb-8">
              Click below to open this week's collection of stories from your circle of friends. 
              Navigate through pages using the buttons or keyboard arrow keys to read each story.
            </p>
          </div>

          <div className="space-y-4">
            <button
              onClick={openFlipbook}
              className="px-8 py-4 bg-gradient-to-r from-amber-600 to-orange-600 text-white rounded-lg text-lg font-semibold hover:from-amber-700 hover:to-orange-700 transition-all transform hover:scale-105 shadow-lg"
            >
              Open Weekly Chronicle
            </button>
            <p className="text-sm text-gray-500">
              The chronicle will open in a new tab for the best reading experience
            </p>
          </div>
        </div>

        <div className="mt-12 grid md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <div className="text-3xl mb-3">⌨️</div>
            <h3 className="font-semibold text-gray-800 mb-2">Keyboard Navigation</h3>
            <p className="text-gray-600 text-sm">Use left/right arrow keys to navigate</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <div className="text-3xl mb-3">📱</div>
            <h3 className="font-semibold text-gray-800 mb-2">Mobile Friendly</h3>
            <p className="text-gray-600 text-sm">Optimized for all screen sizes</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <div className="text-3xl mb-3">👥</div>
            <h3 className="font-semibold text-gray-800 mb-2">Friends Only</h3>
            <p className="text-gray-600 text-sm">Stories from your invited circle</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Invite Friends Component
const InviteFriends = () => {
  const [emails, setEmails] = useState(['']);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);
  const [successCount, setSuccessCount] = useState(0);

  const addEmailField = () => {
    if (emails.length < 50) {
      setEmails([...emails, '']);
    }
  };

  const removeEmailField = (index) => {
    const newEmails = emails.filter((_, i) => i !== index);
    setEmails(newEmails.length > 0 ? newEmails : ['']);
  };

  const handleEmailChange = (index, value) => {
    const newEmails = [...emails];
    newEmails[index] = value;
    setEmails(newEmails);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validEmails = emails.filter(email => email.trim() && email.includes('@'));
    
    if (validEmails.length === 0) {
      setError('Please enter at least one valid email address');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const inviteData = {
        emails: validEmails,
        message: "You've been invited to join Acta Diurna, a private chronicle where friends share stories!"
      };
      
      const response = await axios.post(`${API}/invite-friends`, inviteData);
      setSuccessCount(response.data.sent_count);
      setSuccess(true);
      setEmails(['']);
    } catch (error) {
      console.error('Error sending invites:', error);
      setError('Failed to send invitations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const importFromText = (text) => {
    const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
    const extractedEmails = text.match(emailRegex) || [];
    const uniqueEmails = [...new Set(extractedEmails)].slice(0, 50);
    setEmails(uniqueEmails.length > 0 ? uniqueEmails : ['']);
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-amber-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg text-center max-w-md">
          <div className="text-6xl mb-4">🎉</div>
          <h2 className="text-2xl font-bold text-green-600 mb-4">Invitations Sent!</h2>
          <p className="text-gray-600 mb-6">
            Successfully sent {successCount} invitation{successCount !== 1 ? 's' : ''} to your friends. 
            They'll receive an email with instructions to join your Acta Diurna circle.
          </p>
          <div className="space-y-3">
            <Link
              to="/"
              className="block w-full px-4 py-2 bg-amber-600 text-white rounded hover:bg-amber-700"
            >
              Back to Stories
            </Link>
            <button
              onClick={() => setSuccess(false)}
              className="block w-full px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Invite More Friends
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-100">
      <div className="max-w-4xl mx-auto px-6 py-12">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <div className="text-6xl mb-4">👥</div>
            <h1 className="text-3xl font-bold text-gray-800 mb-4">Invite Friends to Your Circle</h1>
            <p className="text-gray-600">
              Invite up to 50 friends to join your private Acta Diurna chronicle. Only invited friends can share and read stories.
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Friends' Email Addresses ({emails.filter(e => e.trim()).length}/50)
              </label>
              
              <div className="space-y-3">
                {emails.map((email, index) => (
                  <div key={index} className="flex gap-2">
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => handleEmailChange(index, e.target.value)}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                      placeholder="friend@example.com"
                    />
                    {emails.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeEmailField(index)}
                        className="px-3 py-2 text-red-600 hover:text-red-800 border border-red-300 rounded-lg hover:bg-red-50"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                ))}
              </div>

              {emails.length < 50 && (
                <button
                  type="button"
                  onClick={addEmailField}
                  className="mt-3 px-4 py-2 text-amber-600 hover:text-amber-800 border border-amber-300 rounded-lg hover:bg-amber-50"
                >
                  + Add Another Email
                </button>
              )}
            </div>

            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-gray-800 mb-2">Quick Import</h3>
              <p className="text-sm text-gray-600 mb-3">
                Paste a list of email addresses (separated by commas, spaces, or new lines) to import them automatically:
              </p>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                rows="3"
                placeholder="friend1@email.com, friend2@email.com, friend3@email.com"
                onChange={(e) => importFromText(e.target.value)}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-lg font-semibold"
            >
              {loading ? 'Sending Invitations...' : `Send ${emails.filter(e => e.trim()).length} Invitation${emails.filter(e => e.trim()).length !== 1 ? 's' : ''}`}
            </button>
          </form>

          <div className="mt-8 bg-amber-50 p-6 rounded-lg">
            <h3 className="font-semibold text-gray-800 mb-3">What your friends will receive:</h3>
            <ul className="space-y-2 text-gray-600">
              <li className="flex items-center">
                <span className="mr-2">📧</span>
                Personal invitation email with join instructions
              </li>
              <li className="flex items-center">
                <span className="mr-2">🔒</span>
                Access to your private circle of friends
              </li>
              <li className="flex items-center">
                <span className="mr-2">📖</span>
                Ability to share stories and read friends' chronicles
              </li>
              <li className="flex items-center">
                <span className="mr-2">📅</span>
                Weekly chronicle emails with everyone's stories
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

// Subscribe Component
const Subscribe = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) {
      setError('Please enter your email address');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await axios.post(`${API}/subscribe`, { email });
      setSuccess(true);
      setEmail('');
    } catch (error) {
      console.error('Error subscribing:', error);
      if (error.response?.status === 400) {
        setError('This email is already subscribed');
      } else {
        setError('Failed to subscribe. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-amber-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg text-center max-w-md">
          <div className="text-6xl mb-4">🎉</div>
          <h2 className="text-2xl font-bold text-green-600 mb-4">Successfully Subscribed!</h2>
          <p className="text-gray-600 mb-6">
            You'll receive the weekly chronicle with all your friends' stories every Monday at 9 AM.
          </p>
          <div className="space-y-3">
            <Link
              to="/"
              className="block w-full px-4 py-2 bg-amber-600 text-white rounded hover:bg-amber-700"
            >
              Back to Stories
            </Link>
            <button
              onClick={() => setSuccess(false)}
              className="block w-full px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Subscribe Another Email
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-100">
      <div className="max-w-2xl mx-auto px-6 py-12">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <div className="text-6xl mb-4">📧</div>
            <h1 className="text-3xl font-bold text-gray-800 mb-4">Subscribe to Your Chronicle</h1>
            <p className="text-gray-600">
              Get the weekly chronicle with stories from your circle of friends delivered every Monday
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent text-lg"
                placeholder="Enter your email address"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-lg font-semibold"
            >
              {loading ? 'Subscribing...' : 'Subscribe to Chronicle'}
            </button>
          </form>

          <div className="mt-8 bg-gray-50 p-6 rounded-lg">
            <h3 className="font-semibold text-gray-800 mb-3">What you'll receive:</h3>
            <ul className="space-y-2 text-gray-600">
              <li className="flex items-center">
                <span className="mr-2">📅</span>
                Weekly chronicle every Monday at 9 AM
              </li>
              <li className="flex items-center">
                <span className="mr-2">📜</span>
                Beautiful chronicle format with all friends' stories
              </li>
              <li className="flex items-center">
                <span className="mr-2">📧</span>
                HTML email that works on all devices
              </li>
              <li className="flex items-center">
                <span className="mr-2">👥</span>
                Stories only from your invited circle of friends
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/submit" element={<SubmitStory />} />
          <Route path="/flipbook" element={<Flipbook />} />
          <Route path="/invite" element={<InviteFriends />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;