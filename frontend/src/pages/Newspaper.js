import React from 'react';
import { Newspaper as NewspaperIcon, Calendar, Users } from 'lucide-react';

const Newspaper = () => {
  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="roman-header text-3xl font-bold mb-2">
          Weekly Newspaper
        </h1>
        <p className="text-gray-600 text-lg">
          Read your personalized Acta Diurna edition
        </p>
      </div>

      {/* Coming Soon Notice */}
      <div className="roman-column rounded-lg p-8 text-center">
        <div className="w-16 h-16 bg-gradient-to-br from-yellow-500 to-yellow-700 rounded-full flex items-center justify-center mx-auto mb-4">
          <NewspaperIcon className="w-8 h-8 text-white" />
        </div>
        <h2 className="roman-header text-2xl font-semibold mb-4">
          Flipbook Interface Coming Soon
        </h2>
        <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
          Experience your weekly stories in a beautiful, interactive flipbook format. 
          Published every Tuesday at 8:00 AM EST with stories from all your contributors.
        </p>
        
        <div className="grid md:grid-cols-3 gap-6 max-w-3xl mx-auto">
          <div className="text-center">
            <Calendar className="w-8 h-8 text-yellow-600 mx-auto mb-2" />
            <h3 className="font-semibold mb-1">Weekly Publication</h3>
            <p className="text-sm text-gray-600">Fresh edition every Tuesday morning</p>
          </div>
          <div className="text-center">
            <Users className="w-8 h-8 text-yellow-600 mx-auto mb-2" />
            <h3 className="font-semibold mb-1">Contributor Stories</h3>
            <p className="text-sm text-gray-600">Stories from all your network contributors</p>
          </div>
          <div className="text-center">
            <NewspaperIcon className="w-8 h-8 text-yellow-600 mx-auto mb-2" />
            <h3 className="font-semibold mb-1">Flipbook Experience</h3>
            <p className="text-sm text-gray-600">Interactive page turning with Roman styling</p>
          </div>
        </div>
      </div>

      {/* Preview */}
      <div className="mt-8">
        <h3 className="roman-header text-xl font-semibold mb-4">Preview Layout</h3>
        <div className="newspaper max-w-4xl">
          <div className="newspaper-header">
            <h1 className="newspaper-title">ACTA DIURNA</h1>
            <p className="newspaper-subtitle">Your Weekly Social Newspaper • Week 2024-W52</p>
          </div>
          
          <div className="story">
            <h2 className="story-headline">Sample Headline: Local Community Garden Flourishes</h2>
            <h3 className="story-title">Growing Together in Times of Change</h3>
            <p className="story-author">By John Smith</p>
            <div className="story-content">
              <p>
                This is a preview of how your stories will appear in the weekly newspaper. 
                Each contributor's story will be beautifully formatted with their headline, 
                title, and content displayed in classic newspaper style with Roman-inspired typography.
              </p>
              <p>
                Stories will include images, formatted text, and proper attribution. 
                The flipbook interface will allow readers to turn pages naturally, 
                creating an engaging reading experience for your weekly publications.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 roman-column rounded-lg p-6 bg-yellow-50">
        <h3 className="font-semibold text-yellow-900 mb-2">How it works:</h3>
        <ul className="text-sm text-yellow-800 space-y-1">
          <li>• Stories are collected from all your contributors each week</li>
          <li>• Automatic publication every Tuesday at 8:00 AM EST</li>
          <li>• Beautiful flipbook interface with page turning animations</li>
          <li>• Stories include headlines, images, and rich formatting</li>
          <li>• Archive of past editions available for browsing</li>
        </ul>
      </div>
    </div>
  );
};

export default Newspaper;