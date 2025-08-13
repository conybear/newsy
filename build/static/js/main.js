// Acta Diurna - Production Build JavaScript
// This file ensures deployment compatibility for Emergent/Kaniko builds

console.log('🎉 Acta Diurna Flask application loaded successfully');
console.log('📜 Build system: Emergent deployment ready');

// Immediate redirect function
function redirectToApp() {
  if (window.location.pathname === '/index.html' || window.location.pathname.includes('build/')) {
    console.log('🔄 Redirecting to Flask application...');
    window.location.href = '/';
  }
}

// Document ready handler
document.addEventListener('DOMContentLoaded', function() {
  console.log('📚 DOM loaded - checking for redirects');
  redirectToApp();
});

// Immediate execution
redirectToApp();

// Fallback redirect after 2 seconds
setTimeout(function() {
  if (window.location.pathname !== '/') {
    console.log('⏰ Fallback redirect activated');
    window.location.href = '/';
  }
}, 2000);

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    redirectToApp: redirectToApp
  };
}