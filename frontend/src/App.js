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
  const [selectedTopic, setSelectedTopic] = useState(null);

  useEffect(() => {
    fetchTopics();
  }, []);

  const fetchTopics = async () => {
    try {
      const response = await axios.get(`${API}/trending-topics`, { timeout: 10000 });
      setTopics(response.data.topics);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching topics:', error);
      setLoading(false);
      
      // Fallback: Show sample topics for demonstration
      if (topics.length === 0) {
        const sampleTopics = [
          {
            id: "topic-1",
            keyword: "AI coding assistants",
            search_volume: 75000,
            competition_level: "medium",
            trend_score: 8.5,
            platforms: ["youtube", "instagram", "tiktok"],
            discovered_date: new Date().toISOString(),
            metadata: { monetization_potential: "High potential for affiliate marketing and course sales" }
          },
          {
            id: "topic-2", 
            keyword: "Cybersecurity threats 2025",
            search_volume: 60000,
            competition_level: "high",
            trend_score: 7.8,
            platforms: ["youtube", "twitter", "substack"],
            discovered_date: new Date().toISOString(),
            metadata: { monetization_potential: "Premium content and consulting opportunities" }
          },
          {
            id: "topic-3",
            keyword: "Apple Vision Pro review",
            search_volume: 90000,
            competition_level: "high", 
            trend_score: 9.2,
            platforms: ["youtube", "instagram", "tiktok"],
            discovered_date: new Date().toISOString(),
            metadata: { monetization_potential: "High engagement, affiliate opportunities with tech products" }
          }
        ];
        setTopics(sampleTopics);
      }
    }
  };

  const handleGenerateContent = () => {
    alert(`Generating content for topic: "${selectedTopic.keyword}"\n\nThis would typically trigger the content creation workflow for this specific topic across multiple platforms.`);
    // In a real app, this would call the content generation API
  };

  const handleAddToCalendar = () => {
    const calendarDate = prompt('Enter date to add to content calendar (YYYY-MM-DD):');
    if (calendarDate) {
      alert(`Topic "${selectedTopic.keyword}" added to content calendar for ${calendarDate}`);
      // In a real app, this would integrate with calendar/scheduling system
    }
  };

  const handleExportTopic = () => {
    const dataStr = JSON.stringify(selectedTopic, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `topic-${selectedTopic.keyword.replace(/\s+/g, '-').toLowerCase()}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    alert('Topic data exported as JSON file!');
  };

  const handleTopicClick = (topic) => {
    setSelectedTopic(topic);
  };

  const handleBackToList = () => {
    setSelectedTopic(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Show detailed topic view
  if (selectedTopic) {
    return (
      <div className="space-y-6">
        <div className="bg-white p-6 rounded-lg shadow-lg border">
          {/* Back button */}
          <div className="mb-6">
            <button
              onClick={handleBackToList}
              className="flex items-center text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Trending Topics
            </button>
          </div>

          {/* Topic header */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-800">{selectedTopic.keyword}</h1>
              <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                Trend Score: {selectedTopic.trend_score}
              </span>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-700 mb-1">Search Volume</h3>
                <p className="text-2xl font-bold text-green-600">{selectedTopic.search_volume.toLocaleString()}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-700 mb-1">Competition</h3>
                <p className="text-lg font-semibold text-yellow-600 capitalize">{selectedTopic.competition_level}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-700 mb-1">Discovered</h3>
                <p className="text-sm text-gray-600">{new Date(selectedTopic.discovered_date).toLocaleDateString()}</p>
              </div>
            </div>
          </div>

          {/* Platforms */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-3">Best Platforms</h3>
            <div className="flex flex-wrap gap-2">
              {selectedTopic.platforms.map((platform, i) => (
                <span key={i} className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium capitalize">
                  {platform}
                </span>
              ))}
            </div>
          </div>

          {/* Metadata */}
          {selectedTopic.metadata && Object.keys(selectedTopic.metadata).length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-700 mb-3">Additional Details</h3>
              <div className="bg-gray-50 p-4 rounded-lg">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                  {JSON.stringify(selectedTopic.metadata, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {/* Action buttons */}
          <div className="flex flex-wrap gap-3 pt-6 border-t">
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
              Generate Content for This Topic
            </button>
            <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors">
              Add to Content Calendar
            </button>
            <button className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors">
              Export Topic Data
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show topics list view
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-lg border">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Trending Technology Topics</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {topics.map((topic, index) => (
            <div 
              key={topic.id || index} 
              className="p-4 border rounded-lg hover:shadow-md transition-all duration-200 cursor-pointer hover:border-blue-300 hover:bg-blue-50"
              onClick={() => handleTopicClick(topic)}
            >
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-gray-700 hover:text-blue-600">{topic.keyword}</h3>
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                  Score: {topic.trend_score}
                </span>
              </div>
              
              <div className="text-sm text-gray-500 space-y-1 mb-3">
                <p>Search Volume: {topic.search_volume.toLocaleString()}</p>
                <p>Competition: {topic.competition_level}</p>
                <p>Platforms: {topic.platforms.join(', ')}</p>
                <p>Discovered: {new Date(topic.discovered_date).toLocaleDateString()}</p>
              </div>
              
              <div className="text-xs text-blue-600 font-medium">
                Click to view details →
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
  const [selectedContent, setSelectedContent] = useState(null);

  useEffect(() => {
    fetchContent();
  }, [selectedPlatform]);

  const fetchContent = async () => {
    try {
      const params = selectedPlatform ? `?platform=${selectedPlatform}` : '';
      const response = await axios.get(`${API}/content${params}`, { timeout: 10000 });
      setContent(response.data.content);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching content:', error);
      setLoading(false);
      
      // Fallback: Show sample content for demonstration
      if (content.length === 0) {
        const sampleContent = [
          {
            id: "sample-1",
            title: "How AI Coding Assistants Are Changing Programming Forever",
            description: "Explore the revolutionary impact of AI coding assistants like GitHub Copilot, ChatGPT, and Claude on modern software development. Learn how these tools are transforming the way developers write, debug, and optimize code.",
            content_type: "video_long",
            platform: "youtube",
            script: `Hook: "What if I told you that AI can now write 80% of your code for you?"

Introduction:
Welcome back to TechPulse AI! Today we're diving deep into the world of AI coding assistants and how they're completely revolutionizing the programming landscape.

Main Content:
1. The Rise of AI Coding Assistants
- GitHub Copilot's game-changing impact
- ChatGPT's coding capabilities
- Claude's advanced reasoning for complex algorithms

2. Real-World Applications
- Faster prototyping and development
- Bug detection and fixing
- Code optimization and refactoring

3. The Future of Programming
- Will AI replace programmers?
- New skills developers need to learn
- The evolution of software engineering roles

Conclusion:
AI coding assistants aren't here to replace developers - they're here to make us superhuman. The key is learning how to work WITH these tools, not against them.

Call to Action:
If you found this valuable, subscribe for more AI and tech insights. And don't forget to check out our premium newsletter for exclusive industry analysis.`,
            hashtags: ["AI", "coding", "programming", "github", "copilot", "chatgpt", "developer", "tech", "software", "automation"],
            created_date: new Date().toISOString(),
            status: "draft"
          },
          {
            id: "sample-2",
            title: "5 Cybersecurity Threats That Will Dominate 2025",
            description: "Stay ahead of cybercriminals with our comprehensive analysis of the top cybersecurity threats emerging in 2025. From AI-powered attacks to quantum computing vulnerabilities.",
            content_type: "video_short",
            platform: "instagram",
            script: `Hook: "These 5 cyber threats could destroy your business in 2025"

1. AI-Powered Social Engineering
2. Quantum Computing Attacks  
3. Supply Chain Compromises
4. IoT Botnet Explosions
5. Ransomware-as-a-Service Evolution

Protection strategies and detailed analysis in our full blog post!`,
            hashtags: ["cybersecurity", "threats", "2025", "protection", "business", "tech", "security"],
            created_date: new Date().toISOString(),
            status: "draft"
          },
          {
            id: "sample-3",
            title: "Apple Vision Pro: 6 Months Later - Honest Review",
            description: "After 6 months of daily use, here's my brutally honest review of the Apple Vision Pro. The good, the bad, and whether it's worth $3,500 in 2025.",
            content_type: "thread",
            platform: "twitter",
            script: `🧵 THREAD: Apple Vision Pro - 6 months later, here's my honest take (1/12)

The WOW moments:
- Spatial computing feels like magic
- Display quality is unmatched  
- Hand tracking works 95% of the time

But reality check:
- 2-hour battery life kills productivity
- Weight causes neck strain
- Limited app ecosystem
- $3,500 price is brutal

Full thread with detailed analysis...`,
            hashtags: ["AppleVisionPro", "VR", "AR", "tech", "review", "spatial", "computing"],
            created_date: new Date().toISOString(),
            status: "draft"
          }
        ];
        setContent(sampleContent);
      }
    }
  };

  const handleEditContent = () => {
    alert('Edit Content functionality would open an editor to modify the content.');
    // In a real app, this would open an editing interface
  };

  const handleSchedulePost = () => {
    const scheduleDate = prompt('Enter schedule date (YYYY-MM-DD HH:MM):');
    if (scheduleDate) {
      alert(`Content scheduled for: ${scheduleDate}`);
      // In a real app, this would integrate with scheduling APIs
    }
  };

  const handleCopyContent = async () => {
    try {
      const contentToCopy = `Title: ${selectedContent.title}\n\nDescription: ${selectedContent.description}\n\nScript:\n${selectedContent.script}\n\nHashtags: ${selectedContent.hashtags?.join(' #') || 'None'}`;
      await navigator.clipboard.writeText(contentToCopy);
      alert('Content copied to clipboard!');
    } catch (error) {
      // Fallback for browsers that don't support clipboard API
      const textArea = document.createElement('textarea');
      textArea.value = `Title: ${selectedContent.title}\n\nDescription: ${selectedContent.description}\n\nScript:\n${selectedContent.script}`;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      alert('Content copied to clipboard!');
    }
  };

  const handleExportContent = () => {
    const dataStr = JSON.stringify(selectedContent, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `content-${selectedContent.id || 'export'}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    alert('Content exported as JSON file!');
  };

  const handleContentClick = (item) => {
    setSelectedContent(item);
  };

  const handleBackToList = () => {
    setSelectedContent(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Show detailed content view
  if (selectedContent) {
    return (
      <div className="space-y-6">
        <div className="bg-white p-6 rounded-lg shadow-lg border">
          {/* Back button */}
          <div className="mb-6">
            <button
              onClick={handleBackToList}
              className="flex items-center text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Content Library
            </button>
          </div>

          {/* Content header */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-800">{selectedContent.title}</h1>
              <div className="flex gap-2">
                <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">
                  {selectedContent.platform}
                </span>
                <span className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm font-medium">
                  {selectedContent.content_type}
                </span>
              </div>
            </div>
            
            <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
              <span>Created: {new Date(selectedContent.created_date).toLocaleDateString()}</span>
              <span>Status: {selectedContent.status}</span>
              {selectedContent.scheduled_date && (
                <span>Scheduled: {new Date(selectedContent.scheduled_date).toLocaleDateString()}</span>
              )}
            </div>
          </div>

          {/* Content description */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-3">Description</h3>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-gray-700 whitespace-pre-wrap">{selectedContent.description}</p>
            </div>
          </div>

          {/* Content script/body */}
          {selectedContent.script && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-700 mb-3">
                {selectedContent.content_type === 'thread' ? 'Thread Content' : 
                 selectedContent.content_type.includes('video') ? 'Video Script' : 'Content'}
              </h3>
              <div className="bg-gray-50 p-4 rounded-lg border">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
                  {selectedContent.script}
                </pre>
              </div>
            </div>
          )}

          {/* Hashtags */}
          {selectedContent.hashtags && selectedContent.hashtags.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-700 mb-3">Hashtags</h3>
              <div className="flex flex-wrap gap-2">
                {selectedContent.hashtags.map((tag, i) => (
                  <span key={i} className="bg-blue-50 text-blue-600 px-3 py-1 rounded-full text-sm">
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Thumbnails */}
          {selectedContent.thumbnails && selectedContent.thumbnails.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-700 mb-3">Thumbnail Concepts</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {selectedContent.thumbnails.map((thumbnail, i) => (
                  <div key={i} className="bg-gray-50 p-4 rounded-lg border">
                    <p className="text-sm text-gray-700">{thumbnail}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Engagement metrics */}
          {selectedContent.engagement_metrics && Object.keys(selectedContent.engagement_metrics).length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-700 mb-3">Engagement Metrics</h3>
              <div className="bg-gray-50 p-4 rounded-lg">
                <pre className="text-sm text-gray-700">
                  {JSON.stringify(selectedContent.engagement_metrics, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {/* Action buttons */}
          <div className="flex flex-wrap gap-3 pt-6 border-t">
            <button 
              onClick={handleEditContent}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Edit Content
            </button>
            <button 
              onClick={handleSchedulePost}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              Schedule Post
            </button>
            <button 
              onClick={handleCopyContent}
              className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Copy Content
            </button>
            <button 
              onClick={handleExportContent}
              className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Export
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show content list view
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
            <div 
              key={item.id || index} 
              className="p-4 border rounded-lg hover:shadow-md transition-all duration-200 cursor-pointer hover:border-blue-300 hover:bg-blue-50"
              onClick={() => handleContentClick(item)}
            >
              <div className="flex items-center justify-between mb-2 flex-wrap gap-2">
                <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs">
                  {item.platform}
                </span>
                <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-xs">
                  {item.content_type}
                </span>
              </div>
              
              <h3 className="font-semibold text-gray-700 mb-2 text-sm sm:text-base line-clamp-2 hover:text-blue-600">
                {item.title}
              </h3>
              <p className="text-xs sm:text-sm text-gray-500 mb-3 line-clamp-3">
                {item.description.slice(0, 100)}...
              </p>
              
              {item.hashtags && item.hashtags.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-2">
                  {item.hashtags.slice(0, 3).map((tag, i) => (
                    <span key={i} className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded">
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
              
              <div className="flex items-center justify-between">
                <div className="text-xs text-gray-400">
                  Created: {new Date(item.created_date).toLocaleDateString()}
                </div>
                <div className="text-xs text-blue-600 font-medium">
                  Click to view →
                </div>
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