import React from 'react';
import { Calendar, FileText, Users, Clock } from 'lucide-react';

const NewspaperStats = ({ newspaper }) => {
  if (!newspaper || !newspaper.stories) {
    return null;
  }

  const contributors = [...new Set(newspaper.stories.map(s => s.author_name))];
  const totalWords = newspaper.stories.reduce((total, story) => {
    const text = story.content.replace(/<[^>]*>/g, ''); // Strip HTML
    const words = text.trim().split(/\s+/).filter(word => word.length > 0);
    return total + words.length;
  }, 0);

  const totalImages = newspaper.stories.reduce((total, story) => {
    return total + (story.images ? story.images.length : 0);
  }, 0);

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div className="roman-column rounded-lg p-4 text-center">
        <Calendar className="w-6 h-6 text-yellow-600 mx-auto mb-2" />
        <div className="text-2xl font-bold text-gray-900">{newspaper.week_of}</div>
        <div className="text-sm text-gray-600">Week</div>
      </div>
      
      <div className="roman-column rounded-lg p-4 text-center">
        <FileText className="w-6 h-6 text-yellow-600 mx-auto mb-2" />
        <div className="text-2xl font-bold text-gray-900">{newspaper.stories.length}</div>
        <div className="text-sm text-gray-600">Stories</div>
      </div>
      
      <div className="roman-column rounded-lg p-4 text-center">
        <Users className="w-6 h-6 text-yellow-600 mx-auto mb-2" />
        <div className="text-2xl font-bold text-gray-900">{contributors.length}</div>
        <div className="text-sm text-gray-600">Contributors</div>
      </div>
      
      <div className="roman-column rounded-lg p-4 text-center">
        <Clock className="w-6 h-6 text-yellow-600 mx-auto mb-2" />
        <div className="text-2xl font-bold text-gray-900">{Math.ceil(totalWords / 200)}</div>
        <div className="text-sm text-gray-600">Min Read</div>
      </div>
    </div>
  );
};

export default NewspaperStats;