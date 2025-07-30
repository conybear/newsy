import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Newspaper, Eye, EyeOff } from 'lucide-react';

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login, register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Check if we should show register form based on URL
  React.useEffect(() => {
    setIsLogin(location.pathname === '/login');
  }, [location.pathname]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      let result;
      
      if (isLogin) {
        result = await login(email, password);
      } else {
        if (!fullName.trim()) {
          setError('Full name is required');
          setLoading(false);
          return;
        }
        result = await register(email, password, fullName);
      }

      if (result.success) {
        navigate('/');
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('An unexpected error occurred');
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen roman-bg flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-gradient-to-br from-yellow-600 to-yellow-800 rounded-full flex items-center justify-center mb-4">
            <Newspaper className="h-8 w-8 text-white" />
          </div>
          <h1 className="roman-header text-4xl font-bold mb-2">
            Acta Diurna
          </h1>
          <p className="text-gray-600 text-lg italic">
            "The daily acts" - Your social newspaper network
          </p>
        </div>

        {/* Form */}
        <div className="roman-column rounded-lg shadow-xl p-8">
          <div className="text-center mb-6">
            <h2 className="roman-header text-2xl font-semibold">
              {isLogin ? 'Welcome Back' : 'Join Acta Diurna'}
            </h2>
            <p className="text-gray-600 mt-2">
              {isLogin 
                ? 'Sign in to your account' 
                : 'Create your account to start sharing stories'
              }
            </p>
          </div>

          {error && (
            <div className="error mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {!isLogin && (
              <div>
                <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name
                </label>
                <input
                  id="fullName"
                  name="fullName"
                  type="text"
                  required={!isLogin}
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="roman-input w-full"
                  placeholder="Enter your full name"
                />
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="roman-input w-full"
                placeholder="Enter your email"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="roman-input w-full pr-10"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="roman-button w-full flex justify-center py-3 text-base"
              >
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  isLogin ? 'Sign In' : 'Create Account'
                )}
              </button>
            </div>
          </form>

          <div className="text-center mt-6">
            <p className="text-sm text-gray-600">
              {isLogin ? "Don't have an account? " : "Already have an account? "}
              <Link
                to={isLogin ? '/register' : '/login'}
                className="font-medium text-yellow-700 hover:text-yellow-600 transition-colors"
              >
                {isLogin ? 'Sign up' : 'Sign in'}
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-gray-500">
          <p>Share your weekly stories with friends</p>
          <p className="mt-1">Publication every Tuesday at 8:00 AM EST</p>
        </div>
      </div>
    </div>
  );
};

export default Login;