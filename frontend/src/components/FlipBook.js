import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Calendar, User, Image as ImageIcon, BookOpen } from 'lucide-react';

const FlipBook = ({ stories = [] }) => {
  const [currentPage, setCurrentPage] = useState(0);
  const [isFlipping, setIsFlipping] = useState(false);

  const headlines = stories.filter(story => story.is_headline);
  const regularStories = stories.filter(story => !story.is_headline);
  const orderedStories = [...headlines, ...regularStories];

  const nextPage = () => {
    if (currentPage < orderedStories.length - 1) {
      setIsFlipping(true);
      setTimeout(() => {
        setCurrentPage(currentPage + 1);
        setIsFlipping(false);
      }, 300);
    }
  };

  const prevPage = () => {
    if (currentPage > 0) {
      setIsFlipping(true);
      setTimeout(() => {
        setCurrentPage(currentPage - 1);
        setIsFlipping(false);
      }, 300);
    }
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch (error) {
      return dateString;
    }
  };

  if (orderedStories.length === 0) {
    return (
      <div className="flex items-center justify-center h-96 bg-white rounded-lg shadow-lg">
        <div className="text-center">
          <BookOpen className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No stories this week</h3>
          <p className="text-gray-500">Check back later for new stories from your friends!</p>
        </div>
      </div>
    );
  }

  const currentStory = orderedStories[currentPage];

  return (
    <div className="max-w-4xl mx-auto">
      {/* Page indicator */}
      <div className="flex justify-center mb-6">
        <div className="flex space-x-2">
          {orderedStories.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentPage(index)}
              className={`w-3 h-3 rounded-full transition-colors ${
                index === currentPage ? 'bg-blue-600' : 'bg-gray-300'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Flipbook container */}
      <div className="relative bg-white rounded-lg shadow-2xl overflow-hidden" style={{ aspectRatio: '8.5/11' }}>
        {/* Newspaper-style header */}
        <div className="bg-gray-900 text-white p-4 border-b-4 border-red-600">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold tracking-wide">WEEKLY CHRONICLES</h1>
              <p className="text-sm text-gray-300">Your Social Newspaper Network</p>
            </div>
            <div className="text-right">
              <p className="text-sm">{formatDate(currentStory?.created_at)}</p>
              <p className="text-xs text-gray-400">Page {currentPage + 1} of {orderedStories.length}</p>
            </div>
          </div>
        </div>

        {/* Story content */}
        <div className={`p-8 h-full transition-all duration-300 ${isFlipping ? 'scale-95 opacity-50' : 'scale-100 opacity-100'}`}>
          {/* Story header */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <User className="h-5 w-5 text-gray-600" />
                <span className="text-sm font-medium text-gray-900">
                  {currentStory?.author_name}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <Calendar className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-500">
                  {formatDate(currentStory?.created_at)}
                </span>
              </div>
            </div>
            
            <h2 className={`font-bold text-gray-900 leading-tight ${
              currentStory?.is_headline ? 'text-3xl mb-4' : 'text-2xl mb-3'
            }`}>
              {currentStory?.title}
              {currentStory?.is_headline && (
                <span className="inline-block ml-3 px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded">
                  HEADLINE
                </span>
              )}
            </h2>
          </div>

          {/* Story images */}
          {currentStory?.images && currentStory.images.length > 0 && (
            <div className="mb-6">
              <div className={`grid gap-4 ${
                currentStory.images.length === 1 ? 'grid-cols-1' : 
                currentStory.images.length === 2 ? 'grid-cols-2' : 'grid-cols-3'
              }`}>
                {currentStory.images.map((image, index) => (
                  <div key={image.id} className="relative group">
                    <img
                      src={`data:${image.content_type};base64,${image.data}`}
                      alt={image.filename}
                      className="w-full h-48 object-cover rounded-lg shadow-md"
                    />
                    <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-opacity rounded-lg flex items-center justify-center">
                      <ImageIcon className="h-8 w-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Story content */}
          <div className="prose prose-gray max-w-none">
            <div className="text-gray-800 leading-relaxed whitespace-pre-wrap">
              {currentStory?.content}
            </div>
          </div>
        </div>

        {/* Navigation buttons */}
        <div className="absolute bottom-4 left-0 right-0 flex justify-between px-6">
          <button
            onClick={prevPage}
            disabled={currentPage === 0}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-900 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-800 transition-colors"
          >
            <ChevronLeft className="h-5 w-5" />
            <span>Previous</span>
          </button>
          
          <button
            onClick={nextPage}
            disabled={currentPage === orderedStories.length - 1}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-900 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-800 transition-colors"
          >
            <span>Next</span>
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default FlipBook;