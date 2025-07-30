import React, { useState, useEffect } from 'react';
import { 
  PenTool, 
  Clock, 
  AlertCircle, 
  Send, 
  Save, 
  Calendar,
  CheckCircle,
  Edit,
  Eye
} from 'lucide-react';
import axios from 'axios';
import RichTextEditor from '../components/RichTextEditor';
import ImageUploader from '../components/ImageUploader';
import { useAutoSave, useLocalStorageAutoSave } from '../hooks/useAutoSave';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const Stories = () => {
  const [activeTab, setActiveTab] = useState('write'); // 'write' or 'history'
  const [storyData, setStoryData] = useState({
    title: '',
    headline: '',
    content: '',
    images: []
  });
  const [status, setStatus] = useState(null);
  const [myStories, setMyStories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // Auto-save hooks
  const { saveDraft } = useAutoSave(storyData, activeTab === 'write');
  const { loadFromLocalStorage, clearLocalStorage } = useLocalStorageAutoSave(
    'acta-diurna-story-draft', 
    storyData, 
    activeTab === 'write'
  );

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (status && !status.has_submitted && !status.has_draft) {
      // Load from localStorage if no server draft exists
      const localDraft = loadFromLocalStorage();
      if (localDraft) {
        setStoryData(localDraft);
      }
    }
  }, [status, loadFromLocalStorage]);

  const fetchData = async () => {
    try {
      const [statusResponse, storiesResponse, draftResponse] = await Promise.all([
        axios.get(`${API_BASE}/api/stories/status`),
        axios.get(`${API_BASE}/api/stories/my`),
        axios.get(`${API_BASE}/api/stories/draft`)
      ]);

      setStatus(statusResponse.data);
      setMyStories(storiesResponse.data);
      
      // Load draft if exists
      const draft = draftResponse.data;
      if (draft && (draft.title || draft.headline || draft.content)) {
        setStoryData({
          title: draft.title || '',
          headline: draft.headline || '',
          content: draft.content || '',
          images: draft.images || []
        });
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
      setError('Failed to load story data');
    } finally {
      setLoading(false);
    }
  };

  const handleStoryChange = (field, value) => {
    setStoryData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSaveDraft = async () => {
    setSaving(true);
    setError('');
    
    try {
      await saveDraft(storyData);
      setMessage('Draft saved successfully');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setError('Failed to save draft');
    } finally {
      setSaving(false);
    }
  };

  const handleSubmitStory = async () => {
    if (!storyData.title.trim() || !storyData.headline.trim() || !storyData.content.trim()) {
      setError('Title, headline, and content are required');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      await axios.post(`${API_BASE}/api/stories/submit`, {
        title: storyData.title,
        headline: storyData.headline,
        content: storyData.content
      });

      setMessage('Story submitted successfully!');
      clearLocalStorage();
      fetchData(); // Refresh data
      setTimeout(() => setMessage(''), 5000);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to submit story');
    } finally {
      setSubmitting(false);
    }
  };

  const getDeadlineColor = () => {
    if (!status?.submissions_open) return 'text-red-600';
    // Could add more sophisticated deadline warning logic here
    return 'text-green-600';
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="roman-header text-xl">Loading your stories...</div>
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="roman-header text-3xl font-bold mb-2">
          My Stories
        </h1>
        <p className="text-gray-600 text-lg">
          Write and manage your weekly story submissions
        </p>
      </div>

      {/* Status Banner */}
      {status && (
        <div className="roman-column rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Calendar className="w-5 h-5 text-yellow-600" />
              <div>
                <p className="font-medium">Week {status.current_week}</p>
                <p className="text-sm text-gray-600">
                  Deadline: <span className={getDeadlineColor()}>{status.deadline}</span>
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {status.has_submitted ? (
                <div className="flex items-center text-green-600">
                  <CheckCircle className="w-4 h-4 mr-1" />
                  <span className="text-sm font-medium">Submitted</span>
                </div>
              ) : status.submissions_open ? (
                <div className="flex items-center text-yellow-600">
                  <Clock className="w-4 h-4 mr-1" />
                  <span className="text-sm font-medium">Open for Submission</span>
                </div>
              ) : (
                <div className="flex items-center text-red-600">
                  <AlertCircle className="w-4 h-4 mr-1" />
                  <span className="text-sm font-medium">Submissions Closed</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

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

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('write')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'write'
                ? 'border-yellow-500 text-yellow-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <PenTool className="w-4 h-4 inline mr-2" />
            Write Story
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'history'
                ? 'border-yellow-500 text-yellow-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Eye className="w-4 h-4 inline mr-2" />
            My Stories ({myStories.length})
          </button>
        </nav>
      </div>

      {/* Write Story Tab */}
      {activeTab === 'write' && (
        <div className="space-y-6">
          {status?.has_submitted ? (
            <div className="roman-column rounded-lg p-8 text-center bg-green-50">
              <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
              <h3 className="roman-header text-xl font-semibold mb-2">
                Story Submitted!
              </h3>
              <p className="text-gray-600 mb-4">
                You've already submitted your story for week {status.current_week}. 
                Check back next week to submit a new story.
              </p>
              <button
                onClick={() => setActiveTab('history')}
                className="roman-button"
              >
                View My Stories
              </button>
            </div>
          ) : !status?.submissions_open ? (
            <div className="roman-column rounded-lg p-8 text-center bg-red-50">
              <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
              <h3 className="roman-header text-xl font-semibold mb-2">
                Submissions Closed
              </h3>
              <p className="text-gray-600">
                The deadline for week {status?.current_week} has passed. 
                New submissions will open next week.
              </p>
            </div>
          ) : (
            <div className="roman-column rounded-lg p-6">
              <form className="space-y-6">
                {/* Title */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Story Title *
                  </label>
                  <input
                    type="text"
                    value={storyData.title}
                    onChange={(e) => handleStoryChange('title', e.target.value)}
                    className="roman-input w-full"
                    placeholder="Enter your story title..."
                    maxLength={100}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {100 - storyData.title.length} characters remaining
                  </p>
                </div>

                {/* Headline */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Newspaper Headline *
                  </label>
                  <input
                    type="text"
                    value={storyData.headline}
                    onChange={(e) => handleStoryChange('headline', e.target.value)}
                    className="roman-input w-full"
                    placeholder="Enter the headline that will appear in the newspaper..."
                    maxLength={150}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    This headline will be prominently displayed in the newspaper • {150 - storyData.headline.length} characters remaining
                  </p>
                </div>

                {/* Content */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Story Content *
                  </label>
                  <RichTextEditor
                    value={storyData.content}
                    onChange={(content) => handleStoryChange('content', content)}
                    placeholder="Start writing your story..."
                    maxLength={5000}
                    autoSave={true}
                    autoSaveKey="acta-diurna-content"
                  />
                </div>

                {/* Images */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Images (Optional)
                  </label>
                  <ImageUploader
                    images={storyData.images}
                    onImagesChange={(images) => handleStoryChange('images', images)}
                    maxImages={3}
                    maxSizeInMB={5}
                  />
                </div>

                {/* Actions */}
                <div className="flex flex-col sm:flex-row gap-4 pt-6 border-t">
                  <button
                    type="button"
                    onClick={handleSaveDraft}
                    disabled={saving}
                    className="flex items-center justify-center px-6 py-3 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                  >
                    {saving ? (
                      <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <Save className="w-4 h-4 mr-2" />
                    )}
                    Save Draft
                  </button>
                  
                  <button
                    type="button"
                    onClick={handleSubmitStory}
                    disabled={submitting || !storyData.title.trim() || !storyData.headline.trim() || !storyData.content.trim()}
                    className="roman-button flex items-center justify-center px-6 py-3 flex-1"
                  >
                    {submitting ? (
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <Send className="w-4 h-4 mr-2" />
                    )}
                    Submit Story
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      )}

      {/* My Stories Tab */}
      {activeTab === 'history' && (
        <div className="space-y-6">
          {myStories.length === 0 ? (
            <div className="roman-column rounded-lg p-8 text-center">
              <PenTool className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="roman-header text-xl font-semibold mb-2">
                No Stories Yet
              </h3>
              <p className="text-gray-600 mb-4">
                You haven't submitted any stories yet. Start writing your first story!
              </p>
              <button
                onClick={() => setActiveTab('write')}
                className="roman-button"
              >
                Write Your First Story
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {myStories.map((story) => (
                <div key={story.id} className="roman-column rounded-lg p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="roman-header text-lg font-semibold mb-1">
                        {story.headline}
                      </h3>
                      <p className="text-gray-600 font-medium">{story.title}</p>
                      <p className="text-sm text-gray-500">
                        Week {story.week_of} • Submitted {new Date(story.submitted_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center text-green-600">
                      <CheckCircle className="w-4 h-4 mr-1" />
                      <span className="text-sm">Published</span>
                    </div>
                  </div>
                  
                  <div 
                    className="prose prose-sm max-w-none text-gray-700"
                    dangerouslySetInnerHTML={{ __html: story.content }}
                  />
                  
                  {story.images && story.images.length > 0 && (
                    <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-2">
                      {story.images.map((image, index) => (
                        <img
                          key={index}
                          src={`data:${image.content_type};base64,${image.data}`}
                          alt={image.filename}
                          className="w-full h-24 object-cover rounded"
                        />
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Help Section */}
      <div className="mt-8 roman-column rounded-lg p-6 bg-yellow-50">
        <h3 className="font-semibold text-yellow-900 mb-2">Story Guidelines:</h3>
        <ul className="text-sm text-yellow-800 space-y-1">
          <li>• Submit one story per week by Monday 11:59 PM EST</li>
          <li>• Include a compelling headline for the newspaper</li>
          <li>• Use bold, italic, and underline to format your text</li>
          <li>• Add up to 3 images to enhance your story</li>
          <li>• Stories are published every Tuesday at 8:00 AM EST</li>
          <li>• Drafts are automatically saved as you write</li>
        </ul>
      </div>
    </div>
  );
};

export default Stories;