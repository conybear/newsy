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
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
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
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white py-20">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">📰 Newsy</h1>
          <p className="text-xl mb-8 opacity-90">Your Digital Newspaper Platform</p>
          <p className="text-lg opacity-80">Share stories, read the latest news, and stay informed</p>
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-white shadow-lg">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <nav className="flex space-x-8">
            <Link to="/" className="text-blue-600 hover:text-blue-800 font-medium">
              Latest Stories
            </Link>
            <Link to="/submit" className="text-gray-600 hover:text-blue-800 font-medium">
              Submit Story
            </Link>
            <Link to="/flipbook" className="text-gray-600 hover:text-blue-800 font-medium">
              Weekly Flipbook
            </Link>
            <Link to="/subscribe" className="text-gray-600 hover:text-blue-800 font-medium">
              Subscribe
            </Link>
          </nav>
        </div>
      </div>

      {/* Stories Section */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">Latest Stories</h2>
          <p className="text-gray-600">Discover the most recent stories from our community</p>
        </div>

        {stories.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-xl font-semibold text-gray-600 mb-2">No stories yet</h3>
            <p className="text-gray-500 mb-6">Be the first to share a story!</p>
            <Link
              to="/submit"
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Submit Your Story
            </Link>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {stories.map((story) => (
              <div key={story.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
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
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
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
    } catch (error) {
      console.error('Error submitting story:', error);
      setError('Failed to submit story. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg text-center max-w-md">
          <div className="text-6xl mb-4">✅</div>
          <h2 className="text-2xl font-bold text-green-600 mb-4">Story Submitted!</h2>
          <p className="text-gray-600 mb-6">Your story has been successfully submitted and will appear in the latest stories.</p>
          <div className="space-y-3">
            <Link
              to="/"
              className="block w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              View All Stories
            </Link>
            <button
              onClick={() => setSuccess(false)}
              className="block w-full px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Submit Another Story
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-2xl mx-auto px-6 py-12">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Submit Your Story</h1>
          <p className="text-gray-600 mb-8">Share your news, experiences, or insights with our community</p>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700">
              {error}
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
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter an engaging title for your story"
                required
              />
            </div>

            <div>
              <label htmlFor="author" className="block text-sm font-medium text-gray-700 mb-2">
                Author Name
              </label>
              <input
                type="text"
                id="author"
                name="author"
                value={formData.author}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Your name (optional - defaults to Anonymous)"
              />
            </div>

            <div>
              <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-2">
                Story Content *
              </label>
              <textarea
                id="content"
                name="content"
                value={formData.content}
                onChange={handleChange}
                rows={10}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y"
                placeholder="Tell your story... What happened? Who was involved? When did it occur? Where did it take place? Why is it important?"
                required
              />
            </div>

            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Submitting...' : 'Submit Story'}
              </button>
              <Link
                to="/"
                className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-center"
              >
                Cancel
              </Link>
            </div>
          </form>
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
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
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
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      <div className="max-w-4xl mx-auto px-6 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">📖 Weekly Flipbook</h1>
          <p className="text-xl text-gray-600">Experience this week's stories in an interactive flipbook format</p>
        </div>

        <div className="bg-white rounded-lg shadow-xl p-8 text-center">
          <div className="mb-8">
            <div className="text-8xl mb-4">📰</div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Interactive Newspaper Experience</h2>
            <p className="text-gray-600 mb-8">
              Click below to open this week's newspaper in a beautiful flipbook format. 
              Use the navigation buttons or keyboard arrow keys to flip through pages.
            </p>
          </div>

          <div className="space-y-4">
            <button
              onClick={openFlipbook}
              className="px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg text-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-all transform hover:scale-105 shadow-lg"
            >
              Open Weekly Flipbook
            </button>
            <p className="text-sm text-gray-500">
              The flipbook will open in a new tab for the best reading experience
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
            <div className="text-3xl mb-3">🎨</div>
            <h3 className="font-semibold text-gray-800 mb-2">Beautiful Design</h3>
            <p className="text-gray-600 text-sm">Elegant newspaper-style layout</p>
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
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg text-center max-w-md">
          <div className="text-6xl mb-4">🎉</div>
          <h2 className="text-2xl font-bold text-green-600 mb-4">Successfully Subscribed!</h2>
          <p className="text-gray-600 mb-6">
            You'll receive our weekly newspaper flipbook every Monday at 9 AM.
          </p>
          <div className="space-y-3">
            <Link
              to="/"
              className="block w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-2xl mx-auto px-6 py-12">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <div className="text-6xl mb-4">📧</div>
            <h1 className="text-3xl font-bold text-gray-800 mb-4">Subscribe to Our Newsletter</h1>
            <p className="text-gray-600">
              Get the weekly flipbook newspaper delivered to your inbox every Monday
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
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                placeholder="Enter your email address"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-lg font-semibold"
            >
              {loading ? 'Subscribing...' : 'Subscribe to Newsletter'}
            </button>
          </form>

          <div className="mt-8 bg-gray-50 p-6 rounded-lg">
            <h3 className="font-semibold text-gray-800 mb-3">What you'll receive:</h3>
            <ul className="space-y-2 text-gray-600">
              <li className="flex items-center">
                <span className="mr-2">📅</span>
                Weekly newsletter every Monday at 9 AM
              </li>
              <li className="flex items-center">
                <span className="mr-2">📖</span>
                Beautiful flipbook format with all stories from the week
              </li>
              <li className="flex items-center">
                <span className="mr-2">📧</span>
                HTML email that works on all devices
              </li>
              <li className="flex items-center">
                <span className="mr-2">🔒</span>
                Your email is safe and secure with us
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
          <Route path="/subscribe" element={<Subscribe />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;