import { useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export const useAutoSave = (data, enabled = true, interval = 30000) => {
  const saveDraft = useCallback(async (draftData) => {
    try {
      await axios.post(`${API_BASE}/api/stories/draft`, draftData);
      console.log('Draft auto-saved');
    } catch (error) {
      console.error('Auto-save failed:', error);
    }
  }, []);

  useEffect(() => {
    if (!enabled || !data || (!data.title && !data.headline && !data.content)) {
      return;
    }

    const timer = setInterval(() => {
      saveDraft(data);
    }, interval);

    return () => clearInterval(timer);
  }, [data, enabled, interval, saveDraft]);

  return { saveDraft };
};

export const useLocalStorageAutoSave = (key, data, enabled = true) => {
  useEffect(() => {
    if (!enabled || !key || !data) return;

    const timer = setTimeout(() => {
      localStorage.setItem(key, JSON.stringify(data));
    }, 1000);

    return () => clearTimeout(timer);
  }, [key, data, enabled]);

  const loadFromLocalStorage = useCallback(() => {
    if (!key) return null;
    
    try {
      const saved = localStorage.getItem(key);
      return saved ? JSON.parse(saved) : null;
    } catch (error) {
      console.error('Failed to load from localStorage:', error);
      return null;
    }
  }, [key]);

  const clearLocalStorage = useCallback(() => {
    if (key) {
      localStorage.removeItem(key);
    }
  }, [key]);

  return { loadFromLocalStorage, clearLocalStorage };
};