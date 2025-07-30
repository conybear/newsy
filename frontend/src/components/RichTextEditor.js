import React, { useState, useRef, useEffect } from 'react';
import { Bold, Italic, Underline, Image, Save, Eye, EyeOff } from 'lucide-react';

const RichTextEditor = ({ 
  value = '', 
  onChange, 
  placeholder = 'Start writing your story...', 
  maxLength = 5000,
  autoSave = false,
  autoSaveKey = null
}) => {
  const editorRef = useRef(null);
  const [showPreview, setShowPreview] = useState(false);
  const [wordCount, setWordCount] = useState(0);

  useEffect(() => {
    if (editorRef.current) {
      editorRef.current.innerHTML = value;
      updateWordCount();
    }
  }, [value]);

  useEffect(() => {
    if (autoSave && autoSaveKey && value) {
      const timer = setTimeout(() => {
        localStorage.setItem(autoSaveKey, value);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [value, autoSave, autoSaveKey]);

  const updateWordCount = () => {
    if (editorRef.current) {
      const text = editorRef.current.innerText || '';
      const words = text.trim().split(/\s+/).filter(word => word.length > 0);
      setWordCount(words.length);
    }
  };

  const handleInput = () => {
    if (editorRef.current) {
      const content = editorRef.current.innerHTML;
      onChange(content);
      updateWordCount();
    }
  };

  const formatText = (command, value = null) => {
    document.execCommand(command, false, value);
    editorRef.current.focus();
    handleInput();
  };

  const handleKeyDown = (e) => {
    // Handle keyboard shortcuts
    if (e.ctrlKey || e.metaKey) {
      switch (e.key) {
        case 'b':
          e.preventDefault();
          formatText('bold');
          break;
        case 'i':
          e.preventDefault();
          formatText('italic');
          break;
        case 'u':
          e.preventDefault();
          formatText('underline');
          break;
        default:
          break;
      }
    }
  };

  const isCommandActive = (command) => {
    return document.queryCommandState(command);
  };

  const renderPreview = () => {
    return (
      <div 
        className="story-content p-4 border rounded-lg bg-white min-h-64"
        dangerouslySetInnerHTML={{ __html: value }}
      />
    );
  };

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border">
        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={() => formatText('bold')}
            className={`p-2 rounded transition-colors ${
              isCommandActive('bold') 
                ? 'bg-yellow-200 text-yellow-800' 
                : 'hover:bg-gray-200 text-gray-600'
            }`}
            title="Bold (Ctrl+B)"
          >
            <Bold className="w-4 h-4" />
          </button>
          
          <button
            type="button"
            onClick={() => formatText('italic')}
            className={`p-2 rounded transition-colors ${
              isCommandActive('italic') 
                ? 'bg-yellow-200 text-yellow-800' 
                : 'hover:bg-gray-200 text-gray-600'
            }`}
            title="Italic (Ctrl+I)"
          >
            <Italic className="w-4 h-4" />
          </button>
          
          <button
            type="button"
            onClick={() => formatText('underline')}
            className={`p-2 rounded transition-colors ${
              isCommandActive('underline') 
                ? 'bg-yellow-200 text-yellow-800' 
                : 'hover:bg-gray-200 text-gray-600'
            }`}
            title="Underline (Ctrl+U)"
          >
            <Underline className="w-4 h-4" />
          </button>

          <div className="h-6 w-px bg-gray-300 mx-2" />

          <button
            type="button"
            onClick={() => setShowPreview(!showPreview)}
            className="p-2 rounded hover:bg-gray-200 text-gray-600 transition-colors"
            title="Toggle Preview"
          >
            {showPreview ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>

        <div className="text-sm text-gray-500">
          {wordCount} words {maxLength && `• ${Math.max(0, maxLength - (value?.length || 0))} chars left`}
        </div>
      </div>

      {/* Editor/Preview */}
      {showPreview ? (
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Preview</label>
          {renderPreview()}
        </div>
      ) : (
        <div className="space-y-2">
          <div
            ref={editorRef}
            contentEditable
            onInput={handleInput}
            onKeyDown={handleKeyDown}
            className="roman-input min-h-64 p-4 focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500"
            style={{
              minHeight: '200px',
              maxHeight: '400px',
              overflowY: 'auto',
              lineHeight: '1.6',
              fontSize: '16px'
            }}
            data-placeholder={placeholder}
            suppressContentEditableWarning={true}
          />
        </div>
      )}

      {/* Keyboard shortcuts help */}
      <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
        <strong>Shortcuts:</strong> Ctrl+B (Bold), Ctrl+I (Italic), Ctrl+U (Underline)
      </div>
    </div>
  );
};

export default RichTextEditor;