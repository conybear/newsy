import React, { useState, useEffect } from 'react';
import { 
  ChevronLeft, 
  ChevronRight, 
  RotateCcw, 
  Maximize, 
  Calendar,
  Users,
  FileText
} from 'lucide-react';

const FlipBook = ({ newspaper, onPageChange }) => {
  const [currentPage, setCurrentPage] = useState(0);
  const [isFlipping, setIsFlipping] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);

  // Create pages from newspaper data
  const createPages = () => {
    if (!newspaper || !newspaper.stories) return [];
    
    const pages = [];
    
    // Cover page
    pages.push({
      type: 'cover',
      data: {
        title: newspaper.title || 'Acta Diurna',
        week: newspaper.week_of,
        date: new Date(newspaper.published_at).toLocaleDateString('en-US', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        }),
        storyCount: newspaper.stories.length,
        contributors: [...new Set(newspaper.stories.map(s => s.author_name))].length
      }
    });

    // Story pages (2 stories per page spread)
    for (let i = 0; i < newspaper.stories.length; i += 2) {
      const leftStory = newspaper.stories[i];
      const rightStory = newspaper.stories[i + 1];
      
      pages.push({
        type: 'stories',
        data: {
          left: leftStory,
          right: rightStory
        }
      });
    }

    // Back cover
    pages.push({
      type: 'back-cover',
      data: {
        title: newspaper.title || 'Acta Diurna',
        week: newspaper.week_of,
        totalStories: newspaper.stories.length,
        contributors: [...new Set(newspaper.stories.map(s => s.author_name))]
      }
    });

    return pages;
  };

  const pages = createPages();
  const totalPages = pages.length;

  const nextPage = () => {
    if (currentPage < totalPages - 1 && !isFlipping) {
      setIsFlipping(true);
      setTimeout(() => {
        setCurrentPage(prev => prev + 1);
        setIsFlipping(false);
        onPageChange && onPageChange(currentPage + 1);
      }, 300);
    }
  };

  const prevPage = () => {
    if (currentPage > 0 && !isFlipping) {
      setIsFlipping(true);
      setTimeout(() => {
        setCurrentPage(prev => prev - 1);
        setIsFlipping(false);
        onPageChange && onPageChange(currentPage - 1);
      }, 300);
    }
  };

  const goToPage = (pageNum) => {
    if (pageNum >= 0 && pageNum < totalPages && pageNum !== currentPage && !isFlipping) {
      setIsFlipping(true);
      setTimeout(() => {
        setCurrentPage(pageNum);
        setIsFlipping(false);
        onPageChange && onPageChange(pageNum);
      }, 300);
    }
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault();
        nextPage();
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        prevPage();
      } else if (e.key === 'Escape') {
        setFullscreen(false);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [currentPage, isFlipping]);

  const renderCoverPage = (pageData) => (
    <div className="h-full bg-gradient-to-br from-yellow-50 to-yellow-100 p-8 flex flex-col justify-center items-center text-center border-r border-yellow-200">
      <div className="space-y-6">
        <div className="space-y-2">
          <h1 className="roman-header text-5xl font-bold text-yellow-900 tracking-wider">
            {pageData.title}
          </h1>
          <p className="text-yellow-700 text-lg italic">
            "The Daily Acts" - Your Social Newspaper Network
          </p>
        </div>
        
        <div className="h-px bg-yellow-300 w-32 mx-auto"></div>
        
        <div className="space-y-4">
          <h2 className="roman-header text-2xl font-semibold text-yellow-800">
            Week {pageData.week}
          </h2>
          <p className="text-yellow-700 text-lg">
            {pageData.date}
          </p>
        </div>
        
        <div className="space-y-3 bg-white bg-opacity-50 p-4 rounded-lg">
          <div className="flex items-center justify-center space-x-2 text-yellow-800">
            <FileText className="w-5 h-5" />
            <span className="font-medium">{pageData.storyCount} Stories</span>
          </div>
          <div className="flex items-center justify-center space-x-2 text-yellow-800">
            <Users className="w-5 h-5" />
            <span className="font-medium">{pageData.contributors} Contributors</span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderStoryPage = (story, isLeft = true) => (
    <div className={`h-full p-6 ${isLeft ? 'border-r border-gray-200' : ''} overflow-y-auto`}>
      {story ? (
        <div className="space-y-4">
          {/* Headline */}
          <div className="border-b-2 border-yellow-600 pb-3">
            <h1 className="roman-header text-2xl font-bold text-yellow-900 leading-tight">
              {story.headline}
            </h1>
          </div>
          
          {/* Story Title & Author */}
          <div className="space-y-1">
            <h2 className="text-lg font-semibold text-gray-900">
              {story.title}
            </h2>
            <p className="text-sm text-gray-600 italic">
              By {story.author_name}
            </p>
          </div>
          
          {/* Images */}
          {story.images && story.images.length > 0 && (
            <div className="grid grid-cols-1 gap-2 mb-4">
              {story.images.slice(0, 2).map((image, index) => (
                <img
                  key={index}
                  src={`data:${image.content_type};base64,${image.data}`}
                  alt={image.filename}
                  className="w-full h-32 object-cover rounded shadow-sm"
                />
              ))}
            </div>
          )}
          
          {/* Content */}
          <div 
            className="text-sm leading-relaxed text-gray-800 prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: story.content }}
          />
          
          {/* Additional images */}
          {story.images && story.images.length > 2 && (
            <div className="mt-4">
              <img
                src={`data:${story.images[2].content_type};base64,${story.images[2].data}`}
                alt={story.images[2].filename}
                className="w-full h-24 object-cover rounded shadow-sm"
              />
            </div>
          )}
        </div>
      ) : (
        <div className="h-full flex items-center justify-center text-gray-400">
          <div className="text-center">
            <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No story for this page</p>
          </div>
        </div>
      )}
    </div>
  );

  const renderBackCover = (pageData) => (
    <div className="h-full bg-gradient-to-br from-gray-100 to-gray-200 p-8 flex flex-col justify-center items-center text-center border-l border-gray-300">
      <div className="space-y-6">
        <h1 className="roman-header text-3xl font-bold text-gray-800">
          Thank You for Reading
        </h1>
        
        <div className="space-y-4 bg-white bg-opacity-70 p-6 rounded-lg">
          <h2 className="roman-header text-xl font-semibold text-gray-700">
            This Week's Edition
          </h2>
          <div className="space-y-2 text-gray-600">
            <p><strong>Week:</strong> {pageData.week}</p>
            <p><strong>Stories:</strong> {pageData.totalStories}</p>
            <p><strong>Contributors:</strong></p>
            <div className="text-sm">
              {pageData.contributors.map((contributor, index) => (
                <span key={index}>
                  {contributor}
                  {index < pageData.contributors.length - 1 ? ', ' : ''}
                </span>
              ))}
            </div>
          </div>
        </div>
        
        <p className="text-gray-500 text-sm italic">
          Next edition published Tuesday at 8:00 AM EST
        </p>
      </div>
    </div>
  );

  const renderPage = (page) => {
    if (!page) return null;

    switch (page.type) {
      case 'cover':
        return renderCoverPage(page.data);
      case 'stories':
        return (
          <div className="h-full flex">
            <div className="flex-1">
              {renderStoryPage(page.data.left, true)}
            </div>
            <div className="flex-1">
              {renderStoryPage(page.data.right, false)}
            </div>
          </div>
        );
      case 'back-cover':
        return renderBackCover(page.data);
      default:
        return null;
    }
  };

  if (!newspaper || !newspaper.stories) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-100 rounded-lg">
        <div className="text-center text-gray-500">
          <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p>No newspaper available</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative ${fullscreen ? 'fixed inset-0 z-50 bg-black bg-opacity-90 flex items-center justify-center' : ''}`}>
      {/* Controls */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => goToPage(0)}
            className="flex items-center space-x-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded transition-colors"
            title="Go to cover"
          >
            <RotateCcw className="w-4 h-4" />
            <span className="text-sm">Cover</span>
          </button>
          
          <button
            onClick={() => setFullscreen(!fullscreen)}
            className="flex items-center space-x-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded transition-colors"
            title="Toggle fullscreen"
          >
            <Maximize className="w-4 h-4" />
            <span className="text-sm">Fullscreen</span>
          </button>
        </div>
        
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <span>Page {currentPage + 1} of {totalPages}</span>
        </div>
      </div>

      {/* Flipbook */}
      <div className={`relative ${fullscreen ? 'w-4/5 h-4/5' : 'w-full h-96'} bg-white rounded-lg shadow-2xl overflow-hidden`}>
        {/* Page Container */}
        <div className="relative w-full h-full">
          {/* Current Page */}
          <div 
            className={`absolute inset-0 transition-transform duration-300 ${isFlipping ? 'scale-95 opacity-80' : 'scale-100 opacity-100'}`}
          >
            {renderPage(pages[currentPage])}
          </div>
          
          {/* Page Navigation Overlays */}
          <div className="absolute inset-0 flex">
            {/* Left half - Previous page */}
            <div 
              className="flex-1 cursor-pointer flex items-center justify-start pl-4 hover:bg-black hover:bg-opacity-5 transition-colors"
              onClick={prevPage}
              style={{ visibility: currentPage > 0 ? 'visible' : 'hidden' }}
            >
              <ChevronLeft className="w-8 h-8 text-gray-400 opacity-0 hover:opacity-100 transition-opacity" />
            </div>
            
            {/* Right half - Next page */}
            <div 
              className="flex-1 cursor-pointer flex items-center justify-end pr-4 hover:bg-black hover:bg-opacity-5 transition-colors"
              onClick={nextPage}
              style={{ visibility: currentPage < totalPages - 1 ? 'visible' : 'hidden' }}
            >
              <ChevronRight className="w-8 h-8 text-gray-400 opacity-0 hover:opacity-100 transition-opacity" />
            </div>
          </div>
        </div>
      </div>

      {/* Page Indicators */}
      <div className="flex items-center justify-center mt-4 space-x-2">
        {pages.map((_, index) => (
          <button
            key={index}
            onClick={() => goToPage(index)}
            className={`w-3 h-3 rounded-full transition-colors ${
              index === currentPage 
                ? 'bg-yellow-600' 
                : 'bg-gray-300 hover:bg-gray-400'
            }`}
            title={`Go to page ${index + 1}`}
          />
        ))}
      </div>

      {/* Keyboard Instructions */}
      <div className="text-center mt-4 text-sm text-gray-500">
        Use arrow keys or click to navigate • Space for next page • ESC to exit fullscreen
      </div>
    </div>
  );
};

export default FlipBook;