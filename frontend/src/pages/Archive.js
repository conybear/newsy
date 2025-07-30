import React from 'react';
import { Archive as ArchiveIcon, Calendar, Book } from 'lucide-react';

const Archive = () => {
  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="roman-header text-3xl font-bold mb-2">
          Archive
        </h1>
        <p className="text-gray-600 text-lg">
          Browse past editions of your Acta Diurna newspaper
        </p>
      </div>

      {/* Coming Soon Notice */}
      <div className="roman-column rounded-lg p-8 text-center">
        <div className="w-16 h-16 bg-gradient-to-br from-gray-400 to-gray-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <ArchiveIcon className="w-8 h-8 text-white" />
        </div>
        <h2 className="roman-header text-2xl font-semibold mb-4">
          Archive System Coming Soon
        </h2>
        <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
          Browse through your collection of past weekly newspapers. 
          Every edition will be preserved here for you to revisit memorable stories and moments.
        </p>
        
        <div className="grid md:grid-cols-3 gap-6 max-w-3xl mx-auto">
          <div className="text-center">
            <Calendar className="w-8 h-8 text-gray-600 mx-auto mb-2" />
            <h3 className="font-semibold mb-1">Chronological View</h3>
            <p className="text-sm text-gray-600">Browse editions by week and month</p>
          </div>
          <div className="text-center">
            <Book className="w-8 h-8 text-gray-600 mx-auto mb-2" />
            <h3 className="font-semibold mb-1">Full Editions</h3>
            <p className="text-sm text-gray-600">Complete newspapers with all stories intact</p>
          </div>
          <div className="text-center">
            <ArchiveIcon className="w-8 h-8 text-gray-600 mx-auto mb-2" />
            <h3 className="font-semibold mb-1">Permanent Storage</h3>
            <p className="text-sm text-gray-600">Your memories preserved forever</p>
          </div>
        </div>
      </div>

      {/* Preview */}
      <div className="mt-8 roman-column rounded-lg p-6">
        <h3 className="roman-header text-xl font-semibold mb-4">Archive Preview</h3>
        <div className="space-y-4">
          {[
            { week: '2024-W52', date: 'Dec 24, 2024', stories: 5 },
            { week: '2024-W51', date: 'Dec 17, 2024', stories: 7 },
            { week: '2024-W50', date: 'Dec 10, 2024', stories: 4 },
          ].map((edition) => (
            <div key={edition.week} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-semibold text-gray-900">Acta Diurna - {edition.week}</h4>
                  <p className="text-sm text-gray-600">Published {edition.date}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">{edition.stories} stories</p>
                  <p className="text-xs text-gray-500">Click to read</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-8 roman-column rounded-lg p-6 bg-gray-50">
        <h3 className="font-semibold text-gray-900 mb-2">Archive Features:</h3>
        <ul className="text-sm text-gray-800 space-y-1">
          <li>• Complete preservation of all weekly editions</li>
          <li>• Search through past stories and headlines</li>
          <li>• Download editions as PDF for offline reading</li>
          <li>• Share favorite past stories with friends</li>
          <li>• Timeline view of your publication history</li>
        </ul>
      </div>
    </div>
  );
};

export default Archive;