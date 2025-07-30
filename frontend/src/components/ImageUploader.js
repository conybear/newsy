import React, { useState, useCallback } from 'react';
import { Upload, X, Image as ImageIcon, AlertCircle } from 'lucide-react';

const ImageUploader = ({ 
  images = [], 
  onImagesChange, 
  maxImages = 3, 
  maxSizeInMB = 5,
  disabled = false 
}) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const convertToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = error => reject(error);
    });
  };

  const handleFileUpload = useCallback(async (files) => {
    if (disabled) return;
    
    setError('');
    setUploading(true);

    try {
      const fileArray = Array.from(files);
      
      // Check total number of images
      if (images.length + fileArray.length > maxImages) {
        setError(`Maximum ${maxImages} images allowed per story`);
        setUploading(false);
        return;
      }

      const newImages = [];

      for (const file of fileArray) {
        // Validate file type
        if (!file.type.startsWith('image/')) {
          setError('Please select only image files');
          setUploading(false);
          return;
        }

        // Validate file size
        if (file.size > maxSizeInMB * 1024 * 1024) {
          setError(`Image "${file.name}" is too large. Maximum size is ${maxSizeInMB}MB`);
          setUploading(false);
          return;
        }

        // Convert to base64
        const base64 = await convertToBase64(file);
        
        newImages.push({
          id: Date.now() + Math.random(),
          filename: file.name,
          content_type: file.type,
          data: base64.split(',')[1], // Remove data:image/jpeg;base64, prefix
          preview: base64
        });
      }

      onImagesChange([...images, ...newImages]);
    } catch (err) {
      setError('Failed to process images: ' + err.message);
    } finally {
      setUploading(false);
    }
  }, [images, onImagesChange, maxImages, maxSizeInMB, disabled]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    handleFileUpload(files);
  }, [handleFileUpload]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
  }, []);

  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files) {
      handleFileUpload(files);
    }
  };

  const removeImage = (imageId) => {
    if (disabled) return;
    const updatedImages = images.filter(img => img.id !== imageId);
    onImagesChange(updatedImages);
  };

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      {images.length < maxImages && !disabled && (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-yellow-400 transition-colors cursor-pointer"
        >
          <input
            type="file"
            multiple
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
            id="image-upload"
            disabled={uploading || disabled}
          />
          <label htmlFor="image-upload" className="cursor-pointer">
            <div className="space-y-2">
              {uploading ? (
                <div className="w-8 h-8 border-2 border-yellow-600 border-t-transparent rounded-full animate-spin mx-auto" />
              ) : (
                <Upload className="w-8 h-8 text-gray-400 mx-auto" />
              )}
              <div>
                <p className="text-gray-600">
                  {uploading ? 'Uploading...' : 'Drop images here or click to upload'}
                </p>
                <p className="text-sm text-gray-500">
                  Up to {maxImages} images, max {maxSizeInMB}MB each
                </p>
              </div>
            </div>
          </label>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="error flex items-center space-x-2">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      {/* Image Grid */}
      {images.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {images.map((image) => (
            <div key={image.id} className="relative group">
              <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                <img
                  src={image.preview || `data:${image.content_type};base64,${image.data}`}
                  alt={image.filename}
                  className="w-full h-full object-cover"
                />
              </div>
              
              {!disabled && (
                <button
                  onClick={() => removeImage(image.id)}
                  className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                  title="Remove image"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
              
              <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white p-2 rounded-b-lg">
                <p className="text-xs truncate">{image.filename}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Image Count */}
      <div className="text-sm text-gray-500 text-center">
        {images.length} of {maxImages} images
      </div>
    </div>
  );
};

export default ImageUploader;