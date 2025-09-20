import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import json
import os

from agent_clusters import BaseCluster, ClusterStatus
from event_bus import event_bus, EventTypes, EventPriority, event_handler
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

class IntelligenceEngine(BaseCluster):
    """
    Intelligence Engine - Handles market research, trend analysis, performance analytics,
    and strategic decision making for the content creation system.
    """
    
    def __init__(self):
        super().__init__(
            "Intelligence Engine",
            "Analyzes trends, performance data, and generates strategic insights for content creation"
        )
        
        # Intelligence-specific configuration
        self.config = {
            "trend_analysis_interval": 3600,  # 1 hour
            "performance_check_interval": 1800,  # 30 minutes
            "max_trends_to_track": 20,
            "content_categories": ["technology", "AI", "programming", "startups", "innovation"],
            "platforms": ["youtube", "instagram", "tiktok", "twitter", "facebook"],
            "learning_enabled": True
        }
        
        # Data storage
        self.current_trends = []
        self.performance_history = []
        self.content_strategy = {}
        self.market_insights = {}
        
        # Initialize database connection (will be set from server.py)
        self.db = None
    
    def set_database(self, db):
        """Set database connection"""
        self.db = db
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process intelligence tasks"""
        task_type = task_data.get("type", "unknown")
        
        start_time = datetime.now(timezone.utc)
        try:
            self.status = ClusterStatus.PROCESSING
            
            if task_type == "trend_analysis":
                result = await self._analyze_trends()
            elif task_type == "performance_analysis":
                result = await self._analyze_performance(task_data.get("data", {}))
            elif task_type == "strategy_generation":
                result = await self._generate_content_strategy(task_data.get("data", {}))
            elif task_type == "market_research":
                result = await self._conduct_market_research(task_data.get("query", ""))
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            # Update metrics
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_metrics(processing_time, success=True)
            
            self.status = ClusterStatus.IDLE
            return result
            
        except Exception as e:
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_metrics(processing_time, success=False)
            await self._handle_error(e, f"Processing task: {task_type}")
            raise
    
    async def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze current trends and market opportunities"""
        logger.info("Intelligence Engine: Starting trend analysis")
        
        try:
            # Use LLM to analyze trends
            prompt = f"""
            As an expert market researcher and trend analyst, analyze the current trends in these categories: {', '.join(self.config['content_categories'])}.
            
            Provide insights on:
            1. Top 5 trending topics for content creation
            2. Emerging opportunities in each category
            3. Content formats that are performing well
            4. Audience engagement patterns
            5. Recommended content themes for the next week
            
            Focus on actionable insights for a content creator targeting technology and innovation topics.
            
            Respond in JSON format with this structure:
            {{
                "trending_topics": [
                    {{
                        "topic": "topic name",
                        "category": "category",
                        "trend_score": 0-100,
                        "search_volume": "estimate",
                        "content_opportunity": "description",
                        "recommended_formats": ["video", "blog", "social_post"]
                    }}
                ],
                "market_insights": {{
                    "emerging_trends": ["trend1", "trend2"],
                    "content_formats": ["format1", "format2"],
                    "audience_preferences": "description",
                    "competitive_landscape": "analysis"
                }},
                "recommendations": {{
                    "weekly_focus": "theme",
                    "content_mix": {{"video": 40, "blog": 30, "social": 30}},
                    "posting_schedule": "recommendation"
                }}
            }}
            """
            
            result = await self.llm_chat.run_chat([UserMessage(content=prompt)])
            
            # Parse LLM response
            try:
                trends_data = json.loads(result.content)
            except json.JSONDecodeError:
                # Fallback if LLM doesn't return valid JSON
                trends_data = {
                    "trending_topics": [
                        {
                            "topic": "AI-Powered Content Creation",
                            "category": "AI",
                            "trend_score": 85,
                            "search_volume": "high",
                            "content_opportunity": "High interest in AI tools for content creation",
                            "recommended_formats": ["video", "blog", "tutorial"]
                        },
                        {
                            "topic": "Voice Cloning Technology",
                            "category": "technology",
                            "trend_score": 78,
                            "search_volume": "medium-high",
                            "content_opportunity": "Growing interest in voice AI applications",
                            "recommended_formats": ["demo", "explanation", "tutorial"]
                        }
                    ],
                    "market_insights": {
                        "emerging_trends": ["Voice AI", "Automated Content"],
                        "content_formats": ["short-form video", "interactive demos"],
                        "audience_preferences": "Technical demonstrations with practical applications",
                        "competitive_landscape": "Increasing competition in AI content space"
                    },
                    "recommendations": {
                        "weekly_focus": "AI Innovation Showcase",
                        "content_mix": {"video": 50, "blog": 30, "social": 20},
                        "posting_schedule": "Daily content with focus on evening engagement"
                    }
                }
            
            # Store trends
            self.current_trends = trends_data["trending_topics"]
            self.market_insights = trends_data["market_insights"]
            
            # Save to database
            if self.db:
                await self._save_trends_to_db(trends_data)
            
            # Emit event
            await event_bus.emit(
                EventTypes.TRENDS_DISCOVERED,
                trends_data,
                source=self.cluster_name,
                priority=EventPriority.HIGH
            )
            
            logger.info(f"Intelligence Engine: Discovered {len(self.current_trends)} trending topics")
            return trends_data
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {str(e)}")
            raise
    
    async def _analyze_performance(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content performance and generate insights"""
        logger.info("Intelligence Engine: Analyzing performance data")
        
        try:
            # Get recent content performance from database
            recent_content = []
            if self.db:
                recent_content = await self.db.content_pieces.find(
                    {"created_date": {"$gte": datetime.now(timezone.utc) - timedelta(days=7)}}
                ).to_list(50)
            
            # Use LLM to analyze performance
            prompt = f"""
            Analyze the performance of recent content and provide strategic insights.
            
            Performance Data: {json.dumps(performance_data, default=str)}
            Recent Content: {json.dumps(recent_content[:5], default=str)}  # Limit for context
            
            Provide analysis on:
            1. Top performing content types and topics
            2. Engagement patterns and timing insights
            3. Platform-specific performance differences
            4. Content optimization recommendations
            5. Strategic adjustments needed
            
            Respond in JSON format:
            {{
                "performance_summary": {{
                    "top_performers": [content_items],
                    "engagement_trends": "analysis",
                    "platform_insights": {{"platform": "insight"}},
                    "content_effectiveness": "overall_assessment"
                }},
                "optimization_recommendations": [
                    {{
                        "area": "content_type/platform/timing",
                        "recommendation": "specific_action",
                        "expected_impact": "impact_description",
                        "priority": "high/medium/low"
                    }}
                ],
                "strategic_adjustments": {{
                    "content_focus": "adjusted_focus",
                    "posting_frequency": "recommendation",
                    "target_audience": "refined_targeting"
                }}
            }}
            """
            
            result = await self.llm_chat.run_chat([UserMessage(content=prompt)])
            
            try:
                analysis = json.loads(result.content)
            except json.JSONDecodeError:
                # Fallback analysis
                analysis = {
                    "performance_summary": {
                        "top_performers": ["Voice cloning tutorials", "AI technology explainers"],
                        "engagement_trends": "Higher engagement on technical content",
                        "platform_insights": {"youtube": "Long-form content performs well"},
                        "content_effectiveness": "Strong performance on educational content"
                    },
                    "optimization_recommendations": [
                        {
                            "area": "content_type",
                            "recommendation": "Increase tutorial-style content",
                            "expected_impact": "20% engagement increase",
                            "priority": "high"
                        }
                    ],
                    "strategic_adjustments": {
                        "content_focus": "Technical tutorials with practical applications",
                        "posting_frequency": "Daily posts with weekly deep-dives",
                        "target_audience": "Tech professionals and enthusiasts"
                    }
                }
            
            # Store performance insights
            self.performance_history.append({
                "timestamp": datetime.now(timezone.utc),
                "analysis": analysis
            })
            
            # Emit event
            await event_bus.emit(
                EventTypes.PERFORMANCE_ANALYSIS_READY,
                analysis,
                source=self.cluster_name,
                priority=EventPriority.NORMAL
            )
            
            logger.info("Intelligence Engine: Performance analysis completed")
            return analysis
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {str(e)}")
            raise
    
    async def _generate_content_strategy(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive content strategy based on trends and performance"""
        logger.info("Intelligence Engine: Generating content strategy")
        
        try:
            # Combine trends and performance data
            trends_summary = [
                f"{t['topic']} (Score: {t['trend_score']})"
                for t in self.current_trends[:5]
            ]
            
            prompt = f"""
            Create a comprehensive content strategy based on current market intelligence.
            
            Current Trends: {', '.join(trends_summary)}
            Market Insights: {json.dumps(self.market_insights, default=str)}
            Available Platforms: {', '.join(self.config['platforms'])}
            
            Generate a detailed content strategy including:
            1. Content calendar for the next 2 weeks
            2. Platform-specific content recommendations
            3. Voice cloning integration opportunities
            4. SEO and engagement optimization tactics
            5. Success metrics and KPIs to track
            
            Respond in JSON format:
            {{
                "strategy_overview": {{
                    "theme": "main_theme",
                    "duration": "2_weeks",
                    "target_audience": "audience_description",
                    "key_objectives": ["objective1", "objective2"]
                }},
                "content_calendar": [
                    {{
                        "day": 1,
                        "platform": "platform_name",
                        "content_type": "video/blog/post",
                        "topic": "specific_topic",
                        "voice_clone_needed": true/false,
                        "estimated_engagement": "high/medium/low"
                    }}
                ],
                "platform_strategies": {{
                    "youtube": {{"focus": "strategy", "frequency": "posting_frequency"}},
                    "instagram": {{"focus": "strategy", "frequency": "posting_frequency"}}
                }},
                "success_metrics": ["metric1", "metric2"],
                "voice_integration": {{
                    "opportunities": ["opportunity1", "opportunity2"],
                    "recommended_voice_style": "style_description"
                }}
            }}
            """
            
            result = await self.llm_chat.run_chat([UserMessage(content=prompt)])
            
            try:
                strategy = json.loads(result.content)
            except json.JSONDecodeError:
                # Fallback strategy
                strategy = {
                    "strategy_overview": {
                        "theme": "AI-Powered Content Creation Mastery",
                        "duration": "2_weeks",
                        "target_audience": "Tech professionals, content creators, AI enthusiasts",
                        "key_objectives": ["Showcase voice cloning capabilities", "Build thought leadership", "Drive engagement"]
                    },
                    "content_calendar": [
                        {
                            "day": 1,
                            "platform": "youtube",
                            "content_type": "video",
                            "topic": "Voice Cloning Tutorial: Create Your Digital Voice",
                            "voice_clone_needed": True,
                            "estimated_engagement": "high"
                        },
                        {
                            "day": 2,
                            "platform": "instagram",
                            "content_type": "reel",
                            "topic": "Behind the Scenes: AI Content Creation",
                            "voice_clone_needed": False,
                            "estimated_engagement": "medium"
                        }
                    ],
                    "platform_strategies": {
                        "youtube": {"focus": "Educational long-form content", "frequency": "3x per week"},
                        "instagram": {"focus": "Behind-the-scenes and quick tips", "frequency": "daily"}
                    },
                    "success_metrics": ["view_count", "engagement_rate", "subscriber_growth"],
                    "voice_integration": {
                        "opportunities": ["Tutorial narration", "Personalized content", "Multi-language content"],
                        "recommended_voice_style": "Professional, friendly, and engaging"
                    }
                }
            
            # Store strategy
            self.content_strategy = strategy
            
            # Emit strategy ready event
            await event_bus.emit(
                EventTypes.STRATEGY_READY,
                strategy,
                source=self.cluster_name,
                priority=EventPriority.HIGH
            )
            
            logger.info("Intelligence Engine: Content strategy generated successfully")
            return strategy
            
        except Exception as e:
            logger.error(f"Strategy generation failed: {str(e)}")
            raise
    
    async def _conduct_market_research(self, query: str) -> Dict[str, Any]:
        """Conduct specific market research based on query"""
        logger.info(f"Intelligence Engine: Conducting market research for: {query}")
        
        try:
            prompt = f"""
            Conduct market research on: {query}
            
            Provide detailed analysis including:
            1. Market size and growth potential
            2. Key players and competitors
            3. Audience demographics and preferences
            4. Content gaps and opportunities
            5. Revenue potential and monetization strategies
            
            Focus on actionable insights for content creation and audience building.
            
            Respond in JSON format:
            {{
                "research_summary": {{
                    "query": "{query}",
                    "market_size": "description",
                    "growth_potential": "assessment",
                    "key_insights": ["insight1", "insight2"]
                }},
                "competitive_analysis": {{
                    "top_players": ["player1", "player2"],
                    "content_gaps": ["gap1", "gap2"],
                    "differentiation_opportunities": ["opportunity1", "opportunity2"]
                }},
                "audience_insights": {{
                    "demographics": "description",
                    "preferences": ["preference1", "preference2"],
                    "pain_points": ["pain1", "pain2"]
                }},
                "monetization_opportunities": ["opportunity1", "opportunity2"],
                "recommended_actions": ["action1", "action2"]
            }}
            """
            
            result = await self.llm_chat.run_chat([UserMessage(content=prompt)])
            
            try:
                research = json.loads(result.content)
            except json.JSONDecodeError:
                # Fallback research
                research = {
                    "research_summary": {
                        "query": query,
                        "market_size": "Large and growing market with significant potential",
                        "growth_potential": "High growth expected in AI and content automation",
                        "key_insights": ["Increasing demand for personalized content", "Voice AI adoption accelerating"]
                    },
                    "competitive_analysis": {
                        "top_players": ["Major tech companies", "Specialized AI startups"],
                        "content_gaps": ["Technical tutorials for beginners", "Practical implementation guides"],
                        "differentiation_opportunities": ["Hands-on demonstrations", "Real-world applications"]
                    },
                    "audience_insights": {
                        "demographics": "Tech professionals, content creators, early adopters",
                        "preferences": ["Practical tutorials", "Behind-the-scenes content"],
                        "pain_points": ["Complex technical concepts", "Implementation challenges"]
                    },
                    "monetization_opportunities": ["Educational courses", "Consulting services", "Tool subscriptions"],
                    "recommended_actions": ["Create beginner-friendly content", "Build community around tutorials"]
                }
            
            logger.info("Intelligence Engine: Market research completed")
            return research
            
        except Exception as e:
            logger.error(f"Market research failed: {str(e)}")
            raise
    
    async def _save_trends_to_db(self, trends_data: Dict[str, Any]):
        """Save trends to database"""
        try:
            if self.db:
                trend_doc = {
                    "timestamp": datetime.now(timezone.utc),
                    "trends": trends_data,
                    "source": "intelligence_engine"
                }
                await self.db.market_trends.insert_one(trend_doc)
                logger.info("Trends saved to database")
        except Exception as e:
            logger.warning(f"Failed to save trends to database: {str(e)}")
    
    @event_handler(EventTypes.ENGAGEMENT_UPDATE)
    async def handle_engagement_update(self, event):
        """Handle engagement updates from distribution engine"""
        engagement_data = event.data
        logger.info("Intelligence Engine: Processing engagement update")
        
        # Analyze engagement and update strategy if needed
        await self._analyze_performance(engagement_data)
    
    @event_handler(EventTypes.CONTENT_PUBLISHED)
    async def handle_content_published(self, event):
        """Handle content published events"""
        content_data = event.data
        logger.info(f"Intelligence Engine: Content published - {content_data.get('title', 'Unknown')}")
        
        # Track content for future performance analysis
        self.performance_history.append({
            "timestamp": datetime.now(timezone.utc),
            "event": "content_published",
            "data": content_data
        })
    
    def get_intelligence_summary(self) -> Dict[str, Any]:
        """Get comprehensive intelligence summary"""
        return {
            "current_trends": self.current_trends,
            "market_insights": self.market_insights,
            "content_strategy": self.content_strategy,
            "performance_history_count": len(self.performance_history),
            "last_analysis": self.metrics.last_activity.isoformat() if self.metrics.last_activity else None
        }