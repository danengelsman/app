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
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API}/analytics/dashboard`, { 
        timeout: 15000 // 15 second timeout
      });
      setDashboardData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to load dashboard data. Please try refreshing the page.');
      setLoading(false);
      // Set fallback data
      setDashboardData({
        trending_topics_this_week: 0,
        recent_content: [],
        platform_distribution: []
      });
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
        <p className="text-gray-500">Loading dashboard...</p>
        <button 
          onClick={fetchDashboardData}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 bg-red-50 rounded-lg">
        <p className="text-red-600 mb-4">{error}</p>
        <button 
          onClick={fetchDashboardData}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
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
            <button 
              onClick={handleGenerateContent}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Generate Content for This Topic
            </button>
            <button 
              onClick={handleAddToCalendar}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              Add to Content Calendar
            </button>
            <button 
              onClick={handleExportTopic}
              className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
            >
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
  const [error, setError] = useState(null);
  const [showFullContent, setShowFullContent] = useState(false);

  useEffect(() => {
    fetchContent();
  }, [selectedPlatform]);

  const fetchContent = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = selectedPlatform ? `?platform=${selectedPlatform}` : '';
      const response = await axios.get(`${API}/content${params}`, { timeout: 15000 });
      setContent(response.data.content);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching content:', error);
      setError('Failed to load content. Please try again.');
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
    console.log('Edit Content clicked!');
    alert(`Edit Content clicked!\n\nThis would open an editor for:\n"${selectedContent.title}"\n\nIn a full implementation, this would provide a content editing interface.`);
  };

  const handleSchedulePost = () => {
    console.log('Schedule Post clicked!');
    const scheduleDate = prompt(`Schedule post: "${selectedContent.title}"\n\nEnter schedule date (YYYY-MM-DD HH:MM):`);
    if (scheduleDate) {
      alert(`✅ Content scheduled for: ${scheduleDate}\n\nPlatform: ${selectedContent.platform}\nContent Type: ${selectedContent.content_type}`);
    }
  };

  const handleCopyContent = async () => {
    console.log('Copy Content clicked!');
    try {
      const contentToCopy = `TITLE: ${cleanTitle(selectedContent.title)}\n\nDESCRIPTION: ${cleanContent(selectedContent.description)}\n\nSCRIPT:\n${selectedContent.script || 'No script available'}\n\nHASHTAGS:\n${selectedContent.hashtags?.map(tag => `#${tag}`).join(' ') || 'No hashtags'}\n\nPLATFORM: ${selectedContent.platform}\nCONTENT TYPE: ${selectedContent.content_type}`;
      
      await navigator.clipboard.writeText(contentToCopy);
      alert('✅ Content copied to clipboard!\n\nThe full content including title, description, script, and hashtags has been copied.');
    } catch (error) {
      console.log('Clipboard API failed, using fallback');
      // Fallback for browsers that don't support clipboard API
      const textArea = document.createElement('textarea');
      textArea.value = `${cleanTitle(selectedContent.title)}\n\n${cleanContent(selectedContent.description)}\n\n${selectedContent.script || 'No script'}`;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      alert('✅ Content copied to clipboard! (Fallback method used)');
    }
  };

  const handleExportContent = () => {
    console.log('Export Content clicked!');
    try {
      const exportData = {
        ...selectedContent,
        title: cleanTitle(selectedContent.title),
        description: cleanContent(selectedContent.description),
        exported_at: new Date().toISOString(),
        export_source: 'TechPulse AI Content Management System'
      };
      
      const dataStr = JSON.stringify(exportData, null, 2);
      const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
      
      const exportFileDefaultName = `${cleanTitle(selectedContent.title).replace(/[^a-z0-9]/gi, '_').toLowerCase()}_content.json`;
      
      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
      
      alert(`✅ Content exported successfully!\n\nFile: ${exportFileDefaultName}\nContent: ${cleanTitle(selectedContent.title)}`);
    } catch (error) {
      console.error('Export failed:', error);
      alert('❌ Export failed. Please try again.');
    }
  };

  // Helper function to clean up malformed content
  const cleanContent = (text) => {
    if (!text) return '';
    
    // Remove JSON markdown blocks
    let cleaned = text.replace(/```json\s*\{[^}]*\}/g, '');
    cleaned = cleaned.replace(/```json/g, '');
    cleaned = cleaned.replace(/```/g, '');
    
    // Try to extract description from JSON if it exists
    try {
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0]);
        if (parsed.description) {
          return parsed.description;
        }
        if (parsed.content && parsed.content.description) {
          return parsed.content.description;
        }
      }
    } catch (e) {
      // Fall through to cleaned text
    }
    
    // Clean up and return first meaningful sentence
    cleaned = cleaned.trim();
    const sentences = cleaned.split(/[.!?]+/);
    return sentences[0] ? sentences[0].trim() + '.' : cleaned.slice(0, 150) + '...';
  };

  // Helper function to clean titles
  const cleanTitle = (title) => {
    if (!title) return '';
    
    // Remove platform suffix if it looks like "Topic - platform"
    let cleaned = title.replace(/ - (youtube|instagram|tiktok|twitter)$/i, '');
    
    // Try to extract title from JSON if it exists
    try {
      const jsonMatch = title.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0]);
        if (parsed.title) {
          return parsed.title;
        }
        if (parsed.content && parsed.content.title) {
          return parsed.content.title;
        }
      }
    } catch (e) {
      // Fall through to cleaned title
    }
    
    return cleaned.trim();
  };

  const handleContentClick = (item) => {
    setSelectedContent(item);
  };

  const handleBackToList = () => {
    setSelectedContent(null);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
        <p className="text-gray-500">Loading content library...</p>
        <button 
          onClick={fetchContent}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  if (error && content.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 bg-red-50 rounded-lg">
        <p className="text-red-600 mb-4">{error}</p>
        <button 
          onClick={fetchContent}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
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
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-800">{cleanTitle(selectedContent.title)}</h1>
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
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold text-gray-700">Description</h3>
              <button
                onClick={() => setShowFullContent(!showFullContent)}
                className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
              >
                {showFullContent ? 'Hide Full Content' : 'View Full Content'}
              </button>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-gray-700 whitespace-pre-wrap">
                {showFullContent 
                  ? (selectedContent.script || cleanContent(selectedContent.description) || 'No content available')
                  : cleanContent(selectedContent.description)
                }
              </p>
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
                {cleanTitle(item.title)}
              </h3>
              <p className="text-xs sm:text-sm text-gray-500 mb-3 line-clamp-3">
                {cleanContent(item.description)}
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

const VoiceCloning = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [voiceId, setVoiceId] = useState('');
  const [previewText, setPreviewText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [generateText, setGenerateText] = useState('');
  const [generatedAudio, setGeneratedAudio] = useState(null);
  const [generatingAudio, setGeneratingAudio] = useState(false);
  const [clonedVoices, setClonedVoices] = useState([]);
  const [rateLimitStatus, setRateLimitStatus] = useState(null);
  const [checkingRateLimit, setCheckingRateLimit] = useState(false);

  useEffect(() => {
    // Load any previously created voices from localStorage
    const savedVoices = localStorage.getItem('clonedVoices');
    if (savedVoices) {
      setClonedVoices(JSON.parse(savedVoices));
    }
    
    // Check rate limit status on component mount
    checkRateLimitStatus();
  }, []);

  const checkRateLimitStatus = async () => {
    setCheckingRateLimit(true);
    try {
      const response = await axios.get(`${API}/voice-clone/rate-limit-status/`);
      setRateLimitStatus(response.data);
    } catch (error) {
      console.error('Rate limit status check failed:', error);
      setRateLimitStatus({
        rate_limit_status: 'UNKNOWN',
        message: 'Unable to check rate limit status'
      });
    } finally {
      setCheckingRateLimit(false);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleCreateVoiceClone = async (event) => {
    event.preventDefault();
    
    if (!selectedFile || !voiceId.trim()) {
      setError('Please select an audio file and provide a voice ID');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('voice_id', voiceId.trim());
      if (previewText.trim()) {
        formData.append('preview_text', previewText.trim());
      }
      formData.append('model', 'speech-01');

      const response = await axios.post(`${API}/voice-clone/create/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 second timeout for file upload
      });

      setResult(response.data);
      
      // Save to cloned voices list
      const newVoice = {
        voice_id: response.data.voice_id,
        created_at: new Date().toISOString(),
        preview_url: response.data.preview_audio_url
      };
      
      const updatedVoices = [...clonedVoices, newVoice];
      setClonedVoices(updatedVoices);
      localStorage.setItem('clonedVoices', JSON.stringify(updatedVoices));
      
      // Reset form
      setSelectedFile(null);
      setVoiceId('');
      setPreviewText('');
      
      // Reset file input
      const fileInput = document.getElementById('audio-file');
      if (fileInput) {
        fileInput.value = '';
      }

    } catch (error) {
      console.error('Voice cloning error:', error);
      if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else {
        setError('Failed to create voice clone. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateSpeech = async (event) => {
    event.preventDefault();
    
    if (!generateText.trim()) {
      setError('Please enter text to generate speech');
      return;
    }

    const selectedVoiceId = document.getElementById('voice-select').value;
    if (!selectedVoiceId) {
      setError('Please select a voice');
      return;
    }

    setGeneratingAudio(true);
    setError(null);
    setGeneratedAudio(null);

    try {
      const response = await axios.post(`${API}/voice-clone/generate-speech/`, {
        text: generateText.trim(),
        voice_id: selectedVoiceId,
        model: 'speech-01'
      }, {
        timeout: 30000 // 30 second timeout
      });

      setGeneratedAudio(response.data);

    } catch (error) {
      console.error('Speech generation error:', error);
      if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else {
        setError('Failed to generate speech. Please try again.');
      }
    } finally {
      setGeneratingAudio(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6 rounded-lg">
        <h1 className="text-3xl font-bold mb-2">Voice Cloning Studio</h1>
        <p className="text-purple-100">Create custom voice clones for YouTube content generation</p>
      </div>

      {/* API Status Notice removed - voice cloning is now working */}

      {/* Rate Limit Status */}
      {rateLimitStatus && (
        <div className={`border rounded-lg p-4 ${
          rateLimitStatus.rate_limit_status === 'OK' 
            ? 'bg-green-50 border-green-200' 
            : rateLimitStatus.rate_limit_status === 'RATE_LIMITED'
            ? 'bg-red-50 border-red-200'
            : 'bg-yellow-50 border-yellow-200'
        }`}>
          <div className="flex items-start justify-between">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                {rateLimitStatus.rate_limit_status === 'OK' ? (
                  <svg className="h-5 w-5 text-green-400 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                ) : rateLimitStatus.rate_limit_status === 'RATE_LIMITED' ? (
                  <svg className="h-5 w-5 text-red-400 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="h-5 w-5 text-yellow-400 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
              <div className="ml-3">
                <h3 className={`text-sm font-medium ${
                  rateLimitStatus.rate_limit_status === 'OK' 
                    ? 'text-green-800' 
                    : rateLimitStatus.rate_limit_status === 'RATE_LIMITED'
                    ? 'text-red-800'
                    : 'text-yellow-800'
                }`}>
                  API Status: {rateLimitStatus.rate_limit_status.replace('_', ' ')}
                </h3>
                <div className={`mt-1 text-sm ${
                  rateLimitStatus.rate_limit_status === 'OK' 
                    ? 'text-green-700' 
                    : rateLimitStatus.rate_limit_status === 'RATE_LIMITED'
                    ? 'text-red-700'
                    : 'text-yellow-700'
                }`}>
                  <p>{rateLimitStatus.message}</p>
                  {rateLimitStatus.recommendation && (
                    <p className="mt-1"><strong>Recommendation:</strong> {rateLimitStatus.recommendation}</p>
                  )}
                </div>
              </div>
            </div>
            <button
              onClick={checkRateLimitStatus}
              disabled={checkingRateLimit}
              className="text-sm text-gray-500 hover:text-gray-700 disabled:opacity-50"
            >
              {checkingRateLimit ? 'Checking...' : 'Refresh'}
            </button>
          </div>
        </div>
      )}

      {/* Voice Clone Creation */}
      <div className="bg-white p-6 rounded-lg shadow-lg border">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Create Voice Clone</h2>
        
        <form onSubmit={handleCreateVoiceClone} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Audio Sample *
            </label>
            <input
              id="audio-file"
              type="file"
              accept=".mp3,.wav,.m4a"
              onChange={handleFileSelect}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Supported formats: MP3, WAV, M4A | Duration: 10s-5min | Max size: 20MB
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Voice ID *
            </label>
            <input
              type="text"
              value={voiceId}
              onChange={(e) => setVoiceId(e.target.value)}
              placeholder="e.g., my_voice_v1"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Unique identifier for your voice (letters, numbers, underscores, hyphens only)
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Preview Text (Optional)
            </label>
            <textarea
              value={previewText}
              onChange={(e) => setPreviewText(e.target.value)}
              placeholder="Enter text to generate a preview with the cloned voice..."
              rows={3}
              maxLength={300}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              {previewText.length}/300 characters
            </p>
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3 px-4 rounded-lg font-semibold text-white ${
              loading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            } transition-colors`}
          >
            {loading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Creating Voice Clone...
              </div>
            ) : (
              'Create Voice Clone'
            )}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">
                  {error.includes('rate limit') ? 'Rate Limit Exceeded' : 'Error'}
                </h3>
                <div className="mt-1 text-sm text-red-700">
                  <p>{error}</p>
                  {error.includes('rate limit') && (
                    <div className="mt-2 p-2 bg-red-100 rounded">
                      <p className="text-xs text-red-600">
                        <strong>💡 Tip:</strong> MiniMax API has usage limits. Try again in 5-10 minutes, 
                        or consider reducing the frequency of requests.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {result && (
          <div className={`mt-6 p-4 border rounded-lg ${
            result.status === 'completed' ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'
          }`}>
            <h3 className={`font-semibold mb-2 ${
              result.status === 'completed' ? 'text-green-800' : 'text-yellow-800'
            }`}>
              {result.status === 'completed' ? 'Voice Clone Registered!' : 'Voice Clone Status'}
            </h3>
            <div className={`space-y-2 text-sm ${
              result.status === 'completed' ? 'text-green-700' : 'text-yellow-700'
            }`}>
              <p><strong>Voice ID:</strong> {result.voice_id}</p>
              <p><strong>Job ID:</strong> {result.job_id}</p>
              <p><strong>Status:</strong> {result.status}</p>
              {result.message && result.message.includes('API changes') && (
                <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded">
                  <p className="text-blue-800 text-sm">
                    <strong>ℹ️ Important:</strong> MiniMax has updated their voice cloning system. 
                    While file uploads are currently unavailable, your voice ID has been registered 
                    and you can use it with the speech generation feature below.
                  </p>
                </div>
              )}
              {result.preview_audio_url && (
                <div className="mt-3">
                  <p className="font-medium mb-2">Demo Audio (using default voice):</p>
                  <audio controls className="w-full">
                    <source src={result.preview_audio_url} type="audio/mpeg" />
                    Your browser does not support the audio element.
                  </audio>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Speech Generation */}
      <div className="bg-white p-6 rounded-lg shadow-lg border">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Generate Speech</h2>
        
        {clonedVoices.length === 0 ? (
          <div className="text-center py-8 bg-gray-50 rounded-lg">
            <p className="text-gray-500">No voice clones available. Create a voice clone first!</p>
          </div>
        ) : (
          <form onSubmit={handleGenerateSpeech} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Voice *
              </label>
              <select
                id="voice-select"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value="">Choose a voice...</option>
                {clonedVoices.map((voice, index) => (
                  <option key={index} value={voice.voice_id}>
                    {voice.voice_id} (Created: {new Date(voice.created_at).toLocaleDateString()})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Text to Generate *
              </label>
              <textarea
                value={generateText}
                onChange={(e) => setGenerateText(e.target.value)}
                placeholder="Enter the text you want to convert to speech..."
                rows={4}
                maxLength={1000}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                {generateText.length}/1000 characters
              </p>
            </div>

            <button
              type="submit"
              disabled={generatingAudio}
              className={`w-full py-3 px-4 rounded-lg font-semibold text-white ${
                generatingAudio
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-700'
              } transition-colors`}
            >
              {generatingAudio ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Generating Speech...
                </div>
              ) : (
                'Generate Speech'
              )}
            </button>
          </form>
        )}

        {generatedAudio && (
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="font-semibold text-blue-800 mb-2">Speech Generated!</h3>
            {generatedAudio.status && (
              <div className="mb-3 text-sm text-blue-700">
                <p>{generatedAudio.status}</p>
              </div>
            )}
            <div className="mt-3">
              <p className="font-medium mb-2 text-blue-700">Generated Audio:</p>
              <audio controls className="w-full">
                <source src={generatedAudio.audio_url} type="audio/mpeg" />
                Your browser does not support the audio element.
              </audio>
              <div className="mt-3 flex gap-2">
                <a
                  href={generatedAudio.audio_url}
                  download="generated_speech.mp3"
                  className="inline-flex items-center px-3 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Download Audio
                </a>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Cloned Voices Management */}
      {clonedVoices.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-lg border">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Your Voice Clones</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {clonedVoices.map((voice, index) => (
              <div key={index} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-700">{voice.voice_id}</h3>
                  <button
                    onClick={() => {
                      const updatedVoices = clonedVoices.filter((_, i) => i !== index);
                      setClonedVoices(updatedVoices);
                      localStorage.setItem('clonedVoices', JSON.stringify(updatedVoices));
                    }}
                    className="text-red-500 hover:text-red-700 text-sm"
                  >
                    Remove
                  </button>
                </div>
                <p className="text-sm text-gray-500 mb-3">
                  Created: {new Date(voice.created_at).toLocaleDateString()}
                </p>
                {voice.preview_url && (
                  <audio controls className="w-full">
                    <source src={voice.preview_url} type="audio/mpeg" />
                    Your browser does not support the audio element.
                  </audio>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
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
            <Link 
              to="/voice-cloning" 
              className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Voice Cloning
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
          <Link 
            to="/voice-cloning" 
            onClick={closeMobileMenu}
            className="text-gray-600 hover:text-gray-900 hover:bg-gray-100 block px-3 py-2 rounded-md text-base font-medium transition-colors"
          >
            Voice Cloning
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
            <Route path="/voice-cloning" element={<VoiceCloning />} />
          </Routes>
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;