import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Dashboard Components
const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${API}/analytics/dashboard`);
      setDashboardData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-lg">
        <h1 className="text-3xl font-bold mb-2">Emergent AI Multi-Agent System</h1>
        <p className="text-blue-100">Autonomous content creation powered by 7+ specialized AI agents</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
        <div className="bg-white p-4 sm:p-6 rounded-lg shadow-lg border">
          <h3 className="text-base sm:text-lg font-semibold text-gray-700 mb-2">Weekly Trending Topics</h3>
          <p className="text-2xl sm:text-3xl font-bold text-blue-600">{dashboardData?.trending_topics_this_week || 0}</p>
          <p className="text-xs sm:text-sm text-gray-500">Topics discovered this week</p>
        </div>

        <div className="bg-white p-4 sm:p-6 rounded-lg shadow-lg border">
          <h3 className="text-base sm:text-lg font-semibold text-gray-700 mb-2">Content Pieces</h3>
          <p className="text-2xl sm:text-3xl font-bold text-green-600">{dashboardData?.recent_content?.length || 0}</p>
          <p className="text-xs sm:text-sm text-gray-500">Recent content created</p>
        </div>

        <div className="bg-white p-4 sm:p-6 rounded-lg shadow-lg border sm:col-span-2 lg:col-span-1">
          <h3 className="text-base sm:text-lg font-semibold text-gray-700 mb-2">Platforms</h3>
          <p className="text-2xl sm:text-3xl font-bold text-purple-600">{dashboardData?.platform_distribution?.length || 0}</p>
          <p className="text-xs sm:text-sm text-gray-500">Active platforms</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-lg border">
          <h3 className="text-xl font-semibold mb-4">Recent Content</h3>
          <div className="space-y-3">
            {dashboardData?.recent_content?.slice(0, 5).map((content, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div>
                  <p className="font-medium">{content.title}</p>
                  <p className="text-sm text-gray-500">{content.platform} • {content.content_type}</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs ${
                  content.status === 'published' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {content.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-lg border">
          <h3 className="text-xl font-semibold mb-4">Platform Distribution</h3>
          <div className="space-y-3">
            {dashboardData?.platform_distribution?.map((platform, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="capitalize">{platform._id}</span>
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                  {platform.count} pieces
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const AgentsControl = () => {
  const [agentsStatus, setAgentsStatus] = useState({});
  const [workflowRunning, setWorkflowRunning] = useState(false);
  const [workflowResult, setWorkflowResult] = useState(null);

  useEffect(() => {
    fetchAgentsStatus();
    const interval = setInterval(fetchAgentsStatus, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchAgentsStatus = async () => {
    try {
      const response = await axios.get(`${API}/agents/status`);
      setAgentsStatus(response.data.agents);
    } catch (error) {
      console.error('Error fetching agents status:', error);
    }
  };

  const executeWorkflow = async () => {
    setWorkflowRunning(true);
    setWorkflowResult(null);
    
    try {
      const response = await axios.post(`${API}/agents/execute-workflow`);
      setWorkflowResult(response.data);
    } catch (error) {
      console.error('Error executing workflow:', error);
      setWorkflowResult({ status: 'error', error: error.message });
    } finally {
      setWorkflowRunning(false);
      fetchAgentsStatus();
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'idle': return 'bg-gray-100 text-gray-800';
      case 'running': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-lg border">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 space-y-4 sm:space-y-0">
          <h2 className="text-xl sm:text-2xl font-bold text-gray-800">Agent Control Center</h2>
          <button
            onClick={executeWorkflow}
            disabled={workflowRunning}
            className={`w-full sm:w-auto px-4 sm:px-6 py-3 rounded-lg font-semibold text-sm sm:text-base ${
              workflowRunning
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            } transition-colors`}
          >
            {workflowRunning ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Running Workflow...
              </div>
            ) : (
              'Execute Full Workflow'
            )}
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(agentsStatus).map(([key, agent]) => (
            <div key={key} className="p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-gray-700 text-sm sm:text-base truncate pr-2">{agent.name}</h3>
                <span className={`px-2 py-1 rounded text-xs flex-shrink-0 ${getStatusColor(agent.status)}`}>
                  {agent.status}
                </span>
              </div>
              <p className="text-xs sm:text-sm text-gray-500">ID: {agent.agent_id.slice(0, 8)}...</p>
            </div>
          ))}
        </div>

        {workflowResult && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold mb-2">Workflow Result:</h3>
            <pre className="text-sm text-gray-700 overflow-x-auto">
              {JSON.stringify(workflowResult, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

const TrendingTopics = () => {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTopics();
  }, []);

  const fetchTopics = async () => {
    try {
      const response = await axios.get(`${API}/trending-topics`);
      setTopics(response.data.topics);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching topics:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-lg border">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Trending Technology Topics</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {topics.map((topic, index) => (
            <div key={topic.id || index} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-gray-700">{topic.keyword}</h3>
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                  Score: {topic.trend_score}
                </span>
              </div>
              
              <div className="text-sm text-gray-500 space-y-1">
                <p>Search Volume: {topic.search_volume.toLocaleString()}</p>
                <p>Competition: {topic.competition_level}</p>
                <p>Platforms: {topic.platforms.join(', ')}</p>
                <p>Discovered: {new Date(topic.discovered_date).toLocaleDateString()}</p>
              </div>
            </div>
          ))}
        </div>
        
        {topics.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">No trending topics found. Run the workflow to discover new topics!</p>
          </div>
        )}
      </div>
    </div>
  );
};

const ContentLibrary = () => {
  const [content, setContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPlatform, setSelectedPlatform] = useState('');

  useEffect(() => {
    fetchContent();
  }, [selectedPlatform]);

  const fetchContent = async () => {
    try {
      const params = selectedPlatform ? `?platform=${selectedPlatform}` : '';
      const response = await axios.get(`${API}/content${params}`);
      setContent(response.data.content);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching content:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-lg border">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 space-y-4 sm:space-y-0">
          <h2 className="text-xl sm:text-2xl font-bold text-gray-800">Content Library</h2>
          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value)}
            className="w-full sm:w-auto px-4 py-2 border rounded-lg text-sm sm:text-base"
          >
            <option value="">All Platforms</option>
            <option value="youtube">YouTube</option>
            <option value="instagram">Instagram</option>
            <option value="tiktok">TikTok</option>
            <option value="twitter">Twitter</option>
          </select>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {content.map((item, index) => (
            <div key={item.id || index} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-2 flex-wrap gap-2">
                <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs">
                  {item.platform}
                </span>
                <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-xs">
                  {item.content_type}
                </span>
              </div>
              
              <h3 className="font-semibold text-gray-700 mb-2 text-sm sm:text-base line-clamp-2">{item.title}</h3>
              <p className="text-xs sm:text-sm text-gray-500 mb-3 line-clamp-3">{item.description.slice(0, 100)}...</p>
              
              {item.hashtags && item.hashtags.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-2">
                  {item.hashtags.slice(0, 3).map((tag, i) => (
                    <span key={i} className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded">
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
              
              <div className="text-xs text-gray-400">
                Created: {new Date(item.created_date).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>

        {content.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">No content found. Run the workflow to generate new content!</p>
          </div>
        )}
      </div>
    </div>
  );
};

const BrandingKit = () => {
  const [branding, setBranding] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBranding();
  }, []);

  const fetchBranding = async () => {
    try {
      const response = await axios.get(`${API}/branding`);
      setBranding(response.data.branding);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching branding:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-lg border">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Brand Identity</h2>
        
        {branding ? (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-3">Brand Name</h3>
              <p className="text-2xl font-bold text-blue-600">{branding.brand_name}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold mb-3">Primary Colors</h3>
                <div className="flex space-x-2">
                  {branding.primary_colors.map((color, index) => (
                    <div key={index} className="text-center">
                      <div
                        className="w-12 h-12 rounded-lg border"
                        style={{ backgroundColor: color }}
                      ></div>
                      <p className="text-xs mt-1 text-gray-500">{color}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-3">Secondary Colors</h3>
                <div className="flex space-x-2">
                  {branding.secondary_colors.map((color, index) => (
                    <div key={index} className="text-center">
                      <div
                        className="w-12 h-12 rounded-lg border"
                        style={{ backgroundColor: color }}
                      ></div>
                      <p className="text-xs mt-1 text-gray-500">{color}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-3">Typography</h3>
              <div className="space-y-2">
                <p><strong>Primary Font:</strong> {branding.fonts.primary}</p>
                <p><strong>Secondary Font:</strong> {branding.fonts.secondary}</p>
              </div>
            </div>

            {branding.style_guide && (
              <div>
                <h3 className="text-lg font-semibold mb-3">Style Guide</h3>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                    {JSON.stringify(branding.style_guide, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500">No branding kit found. Run the workflow to create your brand identity!</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Navigation Component
const Navigation = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <nav className="bg-white shadow-lg border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-gray-800 flex-shrink-0">
              TechPulse AI
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link 
              to="/" 
              className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Dashboard
            </Link>
            <Link 
              to="/agents" 
              className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Agents
            </Link>
            <Link 
              to="/topics" 
              className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Topics
            </Link>
            <Link 
              to="/content" 
              className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Content
            </Link>
            <Link 
              to="/branding" 
              className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Branding
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={toggleMobileMenu}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 transition-colors"
              aria-expanded="false"
            >
              <span className="sr-only">Open main menu</span>
              {!isMobileMenuOpen ? (
                /* Hamburger icon */
                <svg className="block h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              ) : (
                /* Close icon */
                <svg className="block h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <div className={`md:hidden ${isMobileMenuOpen ? 'block' : 'hidden'}`}>
        <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white border-t border-gray-200">
          <Link 
            to="/" 
            onClick={closeMobileMenu}
            className="text-gray-600 hover:text-gray-900 hover:bg-gray-100 block px-3 py-2 rounded-md text-base font-medium transition-colors"
          >
            Dashboard
          </Link>
          <Link 
            to="/agents" 
            onClick={closeMobileMenu}
            className="text-gray-600 hover:text-gray-900 hover:bg-gray-100 block px-3 py-2 rounded-md text-base font-medium transition-colors"
          >
            Agents
          </Link>
          <Link 
            to="/topics" 
            onClick={closeMobileMenu}
            className="text-gray-600 hover:text-gray-900 hover:bg-gray-100 block px-3 py-2 rounded-md text-base font-medium transition-colors"
          >
            Topics
          </Link>
          <Link 
            to="/content" 
            onClick={closeMobileMenu}
            className="text-gray-600 hover:text-gray-900 hover:bg-gray-100 block px-3 py-2 rounded-md text-base font-medium transition-colors"
          >
            Content
          </Link>
          <Link 
            to="/branding" 
            onClick={closeMobileMenu}
            className="text-gray-600 hover:text-gray-900 hover:bg-gray-100 block px-3 py-2 rounded-md text-base font-medium transition-colors"
          >
            Branding
          </Link>
        </div>
      </div>
    </nav>
  );
};

function App() {
  return (
    <div className="App min-h-screen bg-gray-50">
      <BrowserRouter>
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/agents" element={<AgentsControl />} />
            <Route path="/topics" element={<TrendingTopics />} />
            <Route path="/content" element={<ContentLibrary />} />
            <Route path="/branding" element={<BrandingKit />} />
          </Routes>
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;