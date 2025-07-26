import React, { useState, useEffect, useRef } from 'react';
import { Upload, X, Plus, Save, Bold, Italic, Underline, FileText } from 'lucide-react';
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
  const [draftSaved, setDraftSaved] = useState(false);
  const contentRef = useRef(null);

  const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;
  const DRAFT_KEY = 'weekly_story_draft';

  // Load draft on component mount
  useEffect(() => {
    const savedDraft = localStorage.getItem(DRAFT_KEY);
    if (savedDraft) {
      try {
        const draft = JSON.parse(savedDraft);
        setFormData(draft.formData || formData);
        setImages(draft.images || []);
        setDraftSaved(true);
        
        // Set content in the editor
        if (contentRef.current && draft.formData?.content) {
          contentRef.current.innerHTML = draft.formData.content;
        }
      } catch (error) {
        console.error('Failed to load draft:', error);
      }
    }
    
    // Initialize contentEditable properly
    if (contentRef.current) {
      contentRef.current.setAttribute('dir', 'ltr');
      contentRef.current.style.textAlign = 'left';
      contentRef.current.style.direction = 'ltr';
    }
  }, []);

  // Handle contentEditable focus and blur for placeholder
  useEffect(() => {
    const editor = contentRef.current;
    if (!editor) return;

    const handleFocus = () => {
      if (editor.innerHTML === '' || editor.innerHTML === '<br>') {
        editor.innerHTML = '';
      }
      editor.style.color = '#000';
    };

    const handleBlur = () => {
      if (editor.innerHTML === '' || editor.innerHTML === '<br>') {
        editor.innerHTML = '';
        editor.style.color = '#9CA3AF';
      } else {
        editor.style.color = '#000';
      }
    };

    editor.addEventListener('focus', handleFocus);
    editor.addEventListener('blur', handleBlur);

    // Initial setup
    if (!formData.content) {
      editor.style.color = '#9CA3AF';
    }

    return () => {
      editor.removeEventListener('focus', handleFocus);
      editor.removeEventListener('blur', handleBlur);
    };
  }, [formData.content]);

  // Auto-save draft as user types
  useEffect(() => {
    const saveDraft = () => {
      if (formData.title || formData.content) {
        const draft = {
          formData,
          images,
          timestamp: new Date().toISOString()
        };
        localStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
        setDraftSaved(true);
        
        // Clear the saved indicator after 2 seconds
        setTimeout(() => setDraftSaved(false), 2000);
      }
    };

    // Debounce the save operation
    const timeoutId = setTimeout(saveDraft, 1000);
    return () => clearTimeout(timeoutId);
  }, [formData, images]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleContentChange = (e) => {
    // Ensure proper text direction
    if (contentRef.current) {
      contentRef.current.style.direction = 'ltr';
      contentRef.current.style.textAlign = 'left';
    }
    
    setFormData(prev => ({
      ...prev,
      content: e.target.innerHTML
    }));
  };

  const formatText = (command) => {
    if (!contentRef.current) return;
    
    // Save selection
    const selection = window.getSelection();
    const range = selection.rangeCount > 0 ? selection.getRangeAt(0) : null;
    
    // Apply formatting
    document.execCommand(command, false, null);
    
    // Restore focus and ensure proper direction
    contentRef.current.focus();
    if (range) {
      selection.removeAllRanges();
      selection.addRange(range);
    }
    
    // Ensure text direction remains correct
    contentRef.current.style.direction = 'ltr';
    contentRef.current.style.textAlign = 'left';
    
    // Update the content in state
    setFormData(prev => ({
      ...prev,
      content: contentRef.current.innerHTML
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

  const clearDraft = () => {
    localStorage.removeItem(DRAFT_KEY);
    setDraftSaved(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Clean HTML content - remove formatting tags but keep line breaks
      const cleanContent = formData.content
        .replace(/<div>/g, '\n')
        .replace(/<\/div>/g, '')
        .replace(/<br>/g, '\n')
        .replace(/<[^>]*>/g, '')
        .trim();

      // Create the story first
      const storyData = {
        ...formData,
        content: cleanContent
      };
      
      const storyResponse = await axios.post(`${API_BASE}/stories`, storyData);
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

      // Clear draft after successful submission
      clearDraft();
      
      // Reset form
      setFormData({
        title: '',
        content: '',
        is_headline: false
      });
      setImages([]);
      
      // Clear the content editor properly
      if (contentRef.current) {
        contentRef.current.innerHTML = '';
        contentRef.current.style.direction = 'ltr';
        contentRef.current.style.textAlign = 'left';
      }
      
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
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Submit Your Weekly Story</h2>
          {draftSaved && (
            <div className="flex items-center space-x-2 text-green-600">
              <FileText className="h-4 w-4" />
              <span className="text-sm">Draft saved</span>
            </div>
          )}
        </div>
        
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

          {/* Content with formatting */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Story Content
            </label>
            
            {/* Formatting toolbar */}
            <div className="border border-gray-300 rounded-t-lg bg-gray-50 px-4 py-2 flex items-center space-x-2">
              <button
                type="button"
                onClick={() => formatText('bold')}
                className="p-2 rounded hover:bg-gray-200 transition-colors"
                title="Bold"
              >
                <Bold className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={() => formatText('italic')}
                className="p-2 rounded hover:bg-gray-200 transition-colors"
                title="Italic"
              >
                <Italic className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={() => formatText('underline')}
                className="p-2 rounded hover:bg-gray-200 transition-colors"
                title="Underline"
              >
                <Underline className="h-4 w-4" />
              </button>
              <span className="text-gray-400">|</span>
              <span className="text-sm text-gray-600">Select text and click to format</span>
            </div>
            
            <div
              ref={contentRef}
              contentEditable
              onInput={handleContentChange}
              className="w-full min-h-[200px] px-4 py-3 border-l border-r border-b border-gray-300 rounded-b-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none content-editable-fix"
              style={{ 
                minHeight: '200px',
                maxHeight: '400px',
                overflowY: 'auto',
                direction: 'ltr',
                textAlign: 'left',
                unicodeBidi: 'normal',
                writingMode: 'lr-tb'
              }}
              data-placeholder="Tell your story... Share what's been happening in your life this week."
            />
            
            <style jsx>{`
              .content-editable-fix {
                direction: ltr !important;
                text-align: left !important;
                unicode-bidi: normal !important;
                writing-mode: lr-tb !important;
              }
              .content-editable-fix:empty:before {
                content: attr(data-placeholder);
                color: #9CA3AF;
                pointer-events: none;
                position: absolute;
              }
              .content-editable-fix:focus:empty:before {
                content: '';
              }
            `}</style>
            <p className="text-sm text-gray-500 mt-1">
              💡 Auto-saves as you type. Use the toolbar to format your text.
            </p>
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
          <div className="flex justify-between items-center">
            <button
              type="button"
              onClick={clearDraft}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Clear Draft
            </button>
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