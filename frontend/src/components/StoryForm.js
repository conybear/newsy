import React, { useState } from 'react';
import { Upload, X, Plus, Save } from 'lucide-react';
import axios from 'axios';

const StoryForm = ({ onStoryCreated }) => {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    is_headline: false
  });
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files);
    const remainingSlots = 3 - images.length;
    
    if (files.length > remainingSlots) {
      alert(`You can only upload ${remainingSlots} more image(s)`);
      return;
    }

    files.forEach(file => {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        alert('Image size must be less than 5MB');
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        setImages(prev => [...prev, {
          id: Date.now() + Math.random(),
          file: file,
          preview: e.target.result,
          name: file.name
        }]);
      };
      reader.readAsDataURL(file);
    });
  };

  const removeImage = (id) => {
    setImages(prev => prev.filter(img => img.id !== id));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Create the story first
      const storyResponse = await axios.post(`${API_BASE}/stories`, formData);
      const storyId = storyResponse.data.id;

      // Upload images if any
      for (const image of images) {
        const imageFormData = new FormData();
        imageFormData.append('file', image.file);
        
        await axios.post(`${API_BASE}/stories/${storyId}/images`, imageFormData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
      }

      // Reset form
      setFormData({
        title: '',
        content: '',
        is_headline: false
      });
      setImages([]);
      
      // Notify parent component
      if (onStoryCreated) {
        onStoryCreated();
      }

    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to create story');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Submit Your Weekly Story</h2>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Title */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
              Story Title
            </label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter a compelling title for your story"
            />
          </div>

          {/* Headline checkbox */}
          <div>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                name="is_headline"
                checked={formData.is_headline}
                onChange={handleChange}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700">
                Mark as headline story (major life event)
              </span>
            </label>
          </div>

          {/* Content */}
          <div>
            <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-2">
              Story Content
            </label>
            <textarea
              id="content"
              name="content"
              value={formData.content}
              onChange={handleChange}
              required
              rows={8}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              placeholder="Tell your story... Share what's been happening in your life this week."
            />
          </div>

          {/* Image upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Images (up to 3)
            </label>
            
            {/* Image previews */}
            {images.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                {images.map((image) => (
                  <div key={image.id} className="relative group">
                    <img
                      src={image.preview}
                      alt={image.name}
                      className="w-full h-32 object-cover rounded-lg"
                    />
                    <button
                      type="button"
                      onClick={() => removeImage(image.id)}
                      className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Upload button */}
            {images.length < 3 && (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors">
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handleImageUpload}
                  className="hidden"
                  id="image-upload"
                />
                <label
                  htmlFor="image-upload"
                  className="cursor-pointer flex flex-col items-center space-y-2"
                >
                  <Upload className="h-8 w-8 text-gray-400" />
                  <span className="text-sm text-gray-600">
                    Click to upload images ({images.length}/3)
                  </span>
                </label>
              </div>
            )}
          </div>

          {/* Error message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="text-sm text-red-600">{error}</div>
            </div>
          )}

          {/* Submit button */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Save className="h-5 w-5" />
              <span>{loading ? 'Saving...' : 'Submit Story'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default StoryForm;