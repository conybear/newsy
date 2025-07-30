import React from 'react';
import { PenTool, Clock, AlertCircle } from 'lucide-react';

const Stories = () => {
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

      {/* Coming Soon Notice */}
      <div className="roman-column rounded-lg p-8 text-center">
        <div className="w-16 h-16 bg-gradient-to-br from-purple-400 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <PenTool className="w-8 h-8 text-white" />
        </div>
        <h2 className="roman-header text-2xl font-semibold mb-4">
          Story Editor Coming Soon
        </h2>
        <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
          We're building a rich text editor with draft saving, image uploads, and deadline tracking. 
          This will be where you write your weekly stories with headlines, bold/italic formatting, and up to 3 images.
        </p>
        
        <div className="grid md:grid-cols-3 gap-6 max-w-3xl mx-auto">
          <div className="text-center">
            <Clock className="w-8 h-8 text-yellow-600 mx-auto mb-2" />
            <h3 className="font-semibold mb-1">Auto-Save Drafts</h3>
            <p className="text-sm text-gray-600">Never lose your work with automatic draft saving</p>
          </div>
          <div className="text-center">
            <PenTool className="w-8 h-8 text-yellow-600 mx-auto mb-2" />
            <h3 className="font-semibold mb-1">Rich Formatting</h3>
            <p className="text-sm text-gray-600">Bold, italic, underline, and more formatting options</p>
          </div>
          <div className="text-center">
            <AlertCircle className="w-8 h-8 text-yellow-600 mx-auto mb-2" />
            <h3 className="font-semibold mb-1">Deadline Tracking</h3>
            <p className="text-sm text-gray-600">Clear deadline reminders for Monday 11:59 PM EST</p>
          </div>
        </div>
      </div>

      {/* Feature Preview */}
      <div className="mt-8 roman-column rounded-lg p-6 bg-purple-50">
        <h3 className="font-semibold text-purple-900 mb-2">Story Requirements:</h3>
        <ul className="text-sm text-purple-800 space-y-1">
          <li>• One story per week maximum</li>
          <li>• Must include a headline that will appear in the newspaper</li>
          <li>• Submit by Monday 11:59 PM EST for Tuesday publication</li>
          <li>• Up to 3 images allowed per story</li>
          <li>• Drafts auto-saved as you write</li>
        </ul>
      </div>
    </div>
  );
};

export default Stories;