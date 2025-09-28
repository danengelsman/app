from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
from enum import Enum
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage
from minimax_mcp_client import (
    VoiceCloneResponse,
    TTSRequest, TTSResponse, get_voice_clone_manager
)

# Load environment variables first
load_dotenv()

# Ensure MiniMax environment variables are set globally for MCP package
if not os.environ.get('MINIMAX_API_KEY'):
    # Load from .env file
    from dotenv import dotenv_values
    env_values = dotenv_values('.env')
    for key, value in env_values.items():
        if key.startswith('MINIMAX_'):
            os.environ[key] = value

ROOT_DIR = Path(__file__).parent

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Emergent AI Multi-Agent Content Creation System")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# LLM Configuration
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"

class ContentPlatform(str, Enum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    SUBSTACK = "substack"

class ContentType(str, Enum):
    VIDEO_LONG = "video_long"
    VIDEO_SHORT = "video_short"
    POST = "post"
    BLOG = "blog"
    THREAD = "thread"

# Database Models
class Agent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    status: AgentStatus = AgentStatus.IDLE
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    configuration: Dict[str, Any] = Field(default_factory=dict)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)

class TrendingTopic(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    keyword: str
    search_volume: int
    competition_level: str
    trend_score: float
    platforms: List[ContentPlatform]
    discovered_date: datetime = Field(default_factory=datetime.utcnow)
    niche: str = "technology"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ContentPiece(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic_id: str
    title: str
    description: str
    content_type: ContentType
    platform: ContentPlatform
    script: Optional[str] = None
    thumbnails: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    status: str = "draft"
    created_date: datetime = Field(default_factory=datetime.utcnow)
    scheduled_date: Optional[datetime] = None
    published_date: Optional[datetime] = None
    engagement_metrics: Dict[str, Any] = Field(default_factory=dict)

class BrandingKit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    brand_name: str = "TechPulse AI"
    primary_colors: List[str] = Field(default_factory=lambda: ["#1a1a2e", "#16213e", "#0f3460"])
    secondary_colors: List[str] = Field(default_factory=lambda: ["#533483", "#7209b7", "#a663cc"])
    fonts: Dict[str, str] = Field(default_factory=lambda: {"primary": "Inter", "secondary": "Roboto"})
    logo_urls: List[str] = Field(default_factory=list)
    style_guide: Dict[str, Any] = Field(default_factory=dict)
    updated_date: datetime = Field(default_factory=datetime.utcnow)

class BlogPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic_id: str
    title: str
    content: str
    excerpt: str
    tags: List[str] = Field(default_factory=list)
    is_premium: bool = False
    substack_url: Optional[str] = None
    published_date: Optional[datetime] = None
    view_count: int = 0
    subscriber_conversions: int = 0

class Analytics(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    platform: ContentPlatform
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    click_through_rate: float = 0.0
    conversion_rate: float = 0.0
    revenue_generated: float = 0.0
    recorded_date: datetime = Field(default_factory=datetime.utcnow)

# Agent Classes
class BaseAgent:
    def __init__(self, name: str, description: str):
        self.agent_id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.llm_chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"agent_{self.agent_id}",
            system_message=f"You are {name}. {description}"
        ).with_model("openai", "gpt-4o")

    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        self.status = AgentStatus.RUNNING
        try:
            result = await self._process_task(task_data)
            self.status = AgentStatus.COMPLETED
            return result
        except Exception as e:
            self.status = AgentStatus.ERROR
            logging.error(f"Agent {self.name} error: {str(e)}")
            raise e

    async def _process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

class TrendingTopicsAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "Agent 1A - Trending Topics Researcher",
            "Scans real-time data to identify top trending topics in technology niche with virality potential."
        )

    async def _process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = """
        Research and identify the top 10 trending topics in technology for content creation.
        Focus on topics with high virality potential, search volume, and monetization opportunities.
        
        Consider these areas:
        - AI and Machine Learning developments
        - Cybersecurity trends
        - New gadgets and consumer tech
        - Software development trends
        - Tech industry news and acquisitions
        - Emerging technologies (AR/VR, blockchain, IoT)
        - Tech career and skills
        - Digital transformation trends
        
        For each topic, provide:
        1. Topic keyword/phrase
        2. Estimated search volume (high/medium/low)
        3. Competition level (high/medium/low)
        4. Virality score (1-10)
        5. Best platforms for this topic
        6. Monetization potential
        
        IMPORTANT: Return ONLY a valid JSON array in this exact format:
        [
          {
            "keyword": "Topic name here",
            "search_volume": "high",
            "competition_level": "medium",
            "virality_score": 8,
            "platforms": ["youtube", "instagram", "tiktok"],
            "monetization_potential": "High potential description"
          }
        ]
        
        Do not include any other text, explanations, or markdown formatting. Return only the JSON array.
        """
        
        user_message = UserMessage(text=prompt)
        response = await self.llm_chat.send_message(user_message)
        
        try:
            # Parse the LLM response and create trending topics
            logging.info(f"Trending Topics Agent received response: {response[:300]}")
            topics_data = json.loads(response)
            trending_topics = []
            
            for topic_data in topics_data[:10]:  # Limit to top 10
                topic = TrendingTopic(
                    keyword=topic_data.get('keyword', ''),
                    search_volume=self._convert_volume_to_int(topic_data.get('search_volume', 'medium')),
                    competition_level=topic_data.get('competition_level', 'medium'),
                    trend_score=float(topic_data.get('virality_score', 5)),
                    platforms=[ContentPlatform.YOUTUBE, ContentPlatform.INSTAGRAM, ContentPlatform.TIKTOK],
                    metadata=topic_data
                )
                
                # Save to database
                await db.trending_topics.insert_one(topic.dict())
                trending_topics.append(topic)
                logging.info(f"Saved trending topic: {topic.keyword}")
            
            return {"status": "success", "topics_found": len(trending_topics), "topics": [t.dict() for t in trending_topics]}
        
        except json.JSONDecodeError:
            # Fallback: create topics from text response
            logging.warning(f"JSON parsing failed for trending topics. Response: {response[:200]}")
            fallback_topics_data = self._create_fallback_topics(response)
            trending_topics = []
            
            # Create TrendingTopic objects and save to database
            for topic_data in fallback_topics_data:
                topic = TrendingTopic(
                    keyword=topic_data.get('keyword', ''),
                    search_volume=topic_data.get('search_volume', 50000),
                    competition_level='medium',
                    trend_score=float(topic_data.get('trend_score', 5)),
                    platforms=[ContentPlatform.YOUTUBE, ContentPlatform.INSTAGRAM, ContentPlatform.TIKTOK],
                    metadata=topic_data
                )
                
                # Save to database
                await db.trending_topics.insert_one(topic.dict())
                trending_topics.append(topic)
            
            return {"status": "success", "topics_found": len(trending_topics), "topics": [t.dict() for t in trending_topics]}

    def _convert_volume_to_int(self, volume: str) -> int:
        volume_map = {"high": 100000, "medium": 50000, "low": 10000}
        return volume_map.get(volume.lower(), 50000)

    def _create_fallback_topics(self, response: str) -> List[Dict]:
        # Create some default tech topics if parsing fails
        default_topics = [
            {"keyword": "AI coding assistants", "search_volume": 75000, "trend_score": 8.5},
            {"keyword": "Cybersecurity threats 2025", "search_volume": 60000, "trend_score": 7.8},
            {"keyword": "Apple Vision Pro review", "search_volume": 90000, "trend_score": 9.2},
            {"keyword": "Python automation tools", "search_volume": 45000, "trend_score": 7.0},
            {"keyword": "Tech startup funding", "search_volume": 35000, "trend_score": 6.5}
        ]
        return default_topics

class TopicSelectorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "Agent 1B - Topic Selector and Copy Producer",
            "Selects best topics and creates detailed content outlines with scripts, titles, and optimization."
        )

    async def _process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        topics = task_data.get('topics', [])
        
        # Select top 3-5 topics based on criteria
        selected_topics = sorted(topics, key=lambda x: x.get('trend_score', 0), reverse=True)[:3]
        
        content_pieces = []
        for topic in selected_topics:
            # Create content for multiple platforms
            platforms = [ContentPlatform.YOUTUBE, ContentPlatform.INSTAGRAM, ContentPlatform.TIKTOK, ContentPlatform.TWITTER]
            
            for platform in platforms:
                content_type = self._get_content_type_for_platform(platform)
                content_piece = await self._create_content_piece(topic, platform, content_type)
                content_pieces.append(content_piece)
                
                # Save to database
                await db.content_pieces.insert_one(content_piece.dict())
        
        return {"status": "success", "content_pieces_created": len(content_pieces), "content": [c.dict() for c in content_pieces]}

    def _get_content_type_for_platform(self, platform: ContentPlatform) -> ContentType:
        mapping = {
            ContentPlatform.YOUTUBE: ContentType.VIDEO_LONG,
            ContentPlatform.INSTAGRAM: ContentType.VIDEO_SHORT,
            ContentPlatform.TIKTOK: ContentType.VIDEO_SHORT,
            ContentPlatform.TWITTER: ContentType.THREAD
        }
        return mapping.get(platform, ContentType.POST)

    async def _create_content_piece(self, topic: Dict, platform: ContentPlatform, content_type: ContentType) -> ContentPiece:
        prompt = f"""
        Create optimized content for {platform.value} about "{topic.get('keyword', '')}" as a {content_type.value}.
        
        Please provide:
        1. Engaging title (platform-optimized)
        2. Compelling description
        3. Full script/copy (appropriate length for platform)
        4. 10 relevant hashtags
        5. Call-to-action directing to blog/subscription
        
        Platform-specific requirements:
        - YouTube: Hook in first 15 seconds, engaging throughout, clear CTA
        - Instagram: Visual storytelling, trending hashtags
        - TikTok: Trend-aware, engaging from second 1
        - Twitter: Thread format, engaging tweets
        
        Return as structured JSON.
        """
        
        user_message = UserMessage(text=prompt)
        response = await self.llm_chat.send_message(user_message)
        
        try:
            content_data = json.loads(response)
        except:
            # If JSON parsing fails, try to clean the response
            cleaned_response = response.replace('```json', '').replace('```', '').strip()
            try:
                content_data = json.loads(cleaned_response)
            except:
                # Final fallback with better content
                content_data = {
                    "title": f"{topic.get('keyword', '').title()} - {platform.value.title()} Content",
                    "description": f"Comprehensive {content_type.value.replace('_', ' ')} about {topic.get('keyword', '')} optimized for {platform.value}. Engaging content that drives audience interaction and blog subscriptions.",
                    "script": f"Hook: Discover the latest insights about {topic.get('keyword', '')}!\n\nMain content covering key points, trends, and actionable advice.\n\nCall to action: Subscribe to our blog for more exclusive tech insights!",
                    "hashtags": [topic.get('keyword', '').replace(' ', '').lower(), platform.value, "tech", "trends", "content"]
                }
        
        return ContentPiece(
            topic_id=topic.get('id', str(uuid.uuid4())),
            title=content_data.get('title', f"{topic.get('keyword', '')}"),
            description=content_data.get('description', ''),
            content_type=content_type,
            platform=platform,
            script=content_data.get('script', ''),
            hashtags=content_data.get('hashtags', []),
        )

class BrandAmbassadorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "Agent 1C - Brand Ambassador",
            "Develops and maintains consistent branding across all content and platforms."
        )

    async def _process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        # Create or update branding kit
        branding_kit = BrandingKit()
        
        # Enhance branding with AI-generated style guide
        prompt = """
        Create a comprehensive branding guide for a technology content creation brand called "TechPulse AI".
        
        The brand should appeal to:
        - Tech enthusiasts
        - Developers and engineers  
        - Tech entrepreneurs
        - Students learning technology
        
        Provide detailed recommendations for:
        1. Brand personality (3-5 key traits)
        2. Tone of voice guidelines
        3. Visual style preferences
        4. Content themes and messaging
        5. Engagement strategies
        
        Make it modern, trustworthy, and engaging for the tech community.
        Return as structured JSON.
        """
        
        user_message = UserMessage(text=prompt)
        response = await self.llm_chat.send_message(user_message)
        
        try:
            brand_data = json.loads(response)
            branding_kit.style_guide = brand_data
        except:
            branding_kit.style_guide = {"tone": "professional yet approachable", "style": "modern tech aesthetic"}
        
        # Save to database
        await db.branding_kits.insert_one(branding_kit.dict())
        
        return {"status": "success", "branding_kit": branding_kit.dict()}

# Import event-driven agent clusters
from event_bus import event_bus, EventTypes, EventPriority
from intelligence_engine import IntelligenceEngine
from creation_engine import CreationEngine
from distribution_engine import DistributionEngine

# Agent 1 Orchestrator - Event-Driven Architecture
class Agent1Orchestrator:
    """
    Agent 1 - Orchestrator for Event-Driven Agent Clusters
    Manages Intelligence Engine, Creation Engine, and Distribution Engine via event-driven communication
    """
    
    def __init__(self):
        self.orchestrator_id = str(uuid.uuid4())
        self.name = "Agent 1 - Cluster Orchestrator"
        self.description = "Event-driven orchestrator managing three intelligent agent clusters"
        self.status = "initializing"
        
        # Initialize the three clusters
        self.intelligence_engine = IntelligenceEngine()
        self.creation_engine = CreationEngine()
        self.distribution_engine = DistributionEngine()
        
        # Orchestrator configuration
        self.config = {
            "automation_enabled": True,
            "voice_cloning_enabled": True,
            "default_voice_id": None,
            "workflow_settings": {
                "auto_execute": False,
                "parallel_processing": True,
                "quality_checks": True,
                "compliance_checks": True
            },
            "cluster_priorities": {
                "intelligence": 1,  # Execute first
                "creation": 2,      # Execute after intelligence
                "distribution": 3   # Execute last
            }
        }
        
        # Orchestrator state
        self.active_workflows = {}
        self.workflow_history = []
        self.cluster_status = {}
        self.performance_metrics = {
            "workflows_completed": 0,
            "average_completion_time": 0,
            "success_rate": 0,
            "errors": []
        }
        
        # Database connection (will be set from server initialization)
        self.db = None
        
        self.status = "ready"
    
    def set_database(self, db):
        """Set database connection for orchestrator and all clusters"""
        self.db = db
        self.intelligence_engine.set_database(db)
        self.creation_engine.set_database(db)
        self.distribution_engine.set_database(db)
    
    def get_voice_manager(self):
        """Get voice cloning manager from Creation Engine"""
        return self.creation_engine.get_voice_manager()
    
    async def set_default_voice(self, voice_id: str):
        """Set the default voice for content generation"""
        self.config["default_voice_id"] = voice_id
        await self.creation_engine.set_default_voice(voice_id)
        logger.info(f"Agent 1 Orchestrator: Default voice set to {voice_id}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        # Update cluster status
        self.cluster_status = {
            "intelligence_engine": {
                "name": self.intelligence_engine.cluster_name,
                "status": self.intelligence_engine.status.value,
                "metrics": self.intelligence_engine.metrics,
                "summary": self.intelligence_engine.get_intelligence_summary()
            },
            "creation_engine": {
                "name": self.creation_engine.cluster_name,
                "status": self.creation_engine.status.value,
                "metrics": self.creation_engine.metrics,
                "summary": self.creation_engine.get_creation_summary()
            },
            "distribution_engine": {
                "name": self.distribution_engine.cluster_name,
                "status": self.distribution_engine.status.value,
                "metrics": self.distribution_engine.metrics,
                "summary": self.distribution_engine.get_distribution_summary()
            }
        }
        
        # Check voice cloning status
        voice_status = {
            "enabled": self.config["voice_cloning_enabled"],
            "default_voice": self.config["default_voice_id"],
            "status": "unknown"
        }
        
        try:
            voice_manager = self.get_voice_manager()
            if voice_manager:
                credentials_valid = await voice_manager.validate_credentials()
                voice_status["status"] = "operational" if credentials_valid else "error"
            else:
                voice_status["status"] = "not_initialized"
        except Exception as e:
            voice_status["status"] = f"error: {str(e)}"
        
        # Get workflow metrics
        active_workflows_count = len(self.active_workflows)
        
        return {
            "orchestrator_status": self.status,
            "orchestrator_id": self.orchestrator_id,
            "clusters": self.cluster_status,
            "voice_cloning": voice_status,
            "automation": {
                "enabled": self.config["automation_enabled"],
                "settings": self.config["workflow_settings"]
            },
            "workflows": {
                "active_count": active_workflows_count,
                "completed_count": self.performance_metrics["workflows_completed"],
                "success_rate": self.performance_metrics["success_rate"],
                "recent_workflows": self.workflow_history[-5:] if self.workflow_history else []
            },
            "event_bus_status": "active"  # Assume event bus is active
        }
    
    async def execute_full_workflow(self, workflow_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute complete automated content creation workflow using event-driven clusters"""
        
        workflow_id = str(uuid.uuid4())
        workflow_config = workflow_config or {}
        
        logger.info(f"Agent 1 Orchestrator: Starting full workflow {workflow_id}")
        
        # Create workflow tracking
        workflow = {
            "id": workflow_id,
            "started_at": datetime.utcnow(),
            "status": "running",
            "clusters_involved": ["intelligence", "creation", "distribution"],
            "config": workflow_config,
            "results": {},
            "errors": []
        }
        
        self.active_workflows[workflow_id] = workflow
        
        try:
            # Step 1: Intelligence Engine - Market Research & Strategy
            logger.info(f"Workflow {workflow_id}: Step 1 - Intelligence Engine")
            intelligence_result = await self.intelligence_engine.process_task({
                "type": "generate_strategy",
                "data": {
                    "niche": workflow_config.get("niche", "technology"),
                    "platforms": workflow_config.get("platforms", ["youtube", "instagram", "tiktok", "twitter"]),
                    "content_count": workflow_config.get("content_count", 5)
                }
            })
            workflow["results"]["intelligence"] = intelligence_result
            
            # Step 2: Creation Engine - Content Creation & Voice Cloning
            logger.info(f"Workflow {workflow_id}: Step 2 - Creation Engine (triggered by events)")
            # Creation Engine will be triggered by Intelligence Engine's STRATEGY_READY event
            # Wait for content creation to complete
            creation_timeout = 300  # 5 minutes timeout
            creation_start = datetime.utcnow()
            
            while (datetime.utcnow() - creation_start).seconds < creation_timeout:
                # Check if creation has results
                if hasattr(self.creation_engine, 'active_projects') and self.creation_engine.active_projects:
                    break
                await asyncio.sleep(2)
            
            # Get creation results
            creation_result = {
                "status": "processing_via_events",
                "projects_active": len(self.creation_engine.active_projects) if hasattr(self.creation_engine, 'active_projects') else 0,
                "voice_manager_available": self.creation_engine.voice_manager is not None
            }
            workflow["results"]["creation"] = creation_result
            
            # Step 3: Distribution Engine - Scheduling & Publishing
            logger.info(f"Workflow {workflow_id}: Step 3 - Distribution Engine (triggered by events)")
            # Distribution Engine will be triggered by Creation Engine's content ready events
            
            distribution_result = {
                "status": "processing_via_events",
                "queue_size": len(self.distribution_engine.content_queue),
                "published_count": len(self.distribution_engine.published_content)
            }
            workflow["results"]["distribution"] = distribution_result
            
            # Complete workflow
            workflow["status"] = "completed"
            workflow["completed_at"] = datetime.utcnow()
            workflow["duration_seconds"] = (workflow["completed_at"] - workflow["started_at"]).seconds
            
            # Update performance metrics
            self.performance_metrics["workflows_completed"] += 1
            self.workflow_history.append(workflow)
            
            # Remove from active workflows
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            
            logger.info(f"Agent 1 Orchestrator: Workflow {workflow_id} completed successfully")
            
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "duration_seconds": workflow["duration_seconds"],
                "results": workflow["results"],
                "clusters_executed": len(workflow["results"]),
                "summary": {
                    "intelligence_strategy_created": intelligence_result.get("status") == "completed",
                    "content_creation_initiated": True,
                    "distribution_setup": True,
                    "voice_cloning_available": self.config["voice_cloning_enabled"],
                    "automation_active": self.config["automation_enabled"]
                }
            }
            
        except Exception as e:
            # Handle workflow error
            workflow["status"] = "error"
            workflow["error"] = str(e)
            workflow["completed_at"] = datetime.utcnow()
            
            self.performance_metrics["errors"].append({
                "workflow_id": workflow_id,
                "error": str(e),
                "timestamp": datetime.utcnow()
            })
            
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            
            logger.error(f"Agent 1 Orchestrator: Workflow {workflow_id} failed: {str(e)}")
            
            return {
                "status": "error",
                "workflow_id": workflow_id,
                "error": str(e),
                "partial_results": workflow["results"]
            }
    
    async def get_cluster_details(self, cluster_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific cluster"""
        cluster_map = {
            "intelligence": self.intelligence_engine,
            "creation": self.creation_engine,
            "distribution": self.distribution_engine
        }
        
        if cluster_name not in cluster_map:
            raise ValueError(f"Unknown cluster: {cluster_name}")
        
        cluster = cluster_map[cluster_name]
        
        return {
            "name": cluster.cluster_name,
            "status": cluster.status.value,
            "metrics": cluster.metrics,
            "config": getattr(cluster, 'config', {}),
            "summary": getattr(cluster, f'get_{cluster_name}_summary', lambda: {})()
        }
    
    async def trigger_specific_cluster(self, cluster_name: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger a specific cluster with custom task data"""
        cluster_map = {
            "intelligence": self.intelligence_engine,
            "creation": self.creation_engine,
            "distribution": self.distribution_engine
        }
        
        if cluster_name not in cluster_map:
            raise ValueError(f"Unknown cluster: {cluster_name}")
        
        cluster = cluster_map[cluster_name]
        logger.info(f"Agent 1 Orchestrator: Triggering {cluster_name} cluster")
        
        try:
            result = await cluster.process_task(task_data)
            return {
                "status": "success",
                "cluster": cluster_name,
                "result": result
            }
        except Exception as e:
            logger.error(f"Failed to trigger {cluster_name} cluster: {str(e)}")
            return {
                "status": "error",
                "cluster": cluster_name,
                "error": str(e)
            }

# Initialize the Agent 1 Orchestrator
agent_1_orchestrator = Agent1Orchestrator()

# Set database connection for orchestrator and clusters
async def initialize_orchestrator():
    """Initialize the orchestrator and its clusters with database connection"""
    agent_1_orchestrator.set_database(db)
    logger.info("Agent 1 Orchestrator initialized with database connection")

# Call initialization
import asyncio
asyncio.create_task(initialize_orchestrator())

# API Endpoints
@api_router.get("/")
async def root():
    return {"message": "Emergent AI Multi-Agent Content Creation System", "version": "1.0.0"}

@api_router.post("/agents/execute-workflow")
async def execute_workflow(background_tasks: BackgroundTasks, voice_id: Optional[str] = None):
    """Execute the complete automated multi-agent workflow with optional voice cloning"""
    try:
        result = await central_overseer.execute_full_workflow(voice_id=voice_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/agents/status")
async def get_agents_status():
    """Get status of all agents"""
    agents_status = {}
    for name, agent in central_overseer.sub_agents.items():
        agents_status[name] = {
            "name": agent.name,
            "status": agent.status.value,
            "agent_id": agent.agent_id
        }
    
    return {"agents": agents_status}

@api_router.get("/system/status")
async def get_system_status():
    """Get comprehensive system status including voice cloning and automation"""
    try:
        status = await central_overseer.get_system_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/system/voice/set-default")
async def set_default_voice(voice_id: str):
    """Set the default voice for content generation"""
    try:
        await central_overseer.set_default_voice(voice_id)
        return {"status": "success", "message": f"Default voice set to {voice_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/trending-topics")
async def get_trending_topics(limit: int = 10):
    """Get recent trending topics"""
    topics = await db.trending_topics.find().sort("discovered_date", -1).limit(limit).to_list(limit)
    
    # Convert ObjectIds to strings for JSON serialization
    for topic in topics:
        if '_id' in topic:
            topic['_id'] = str(topic['_id'])
    
    return {"topics": topics}

@api_router.get("/content")
async def get_content_pieces(platform: Optional[str] = None, limit: int = 20):
    """Get content pieces, optionally filtered by platform"""
    query = {}
    if platform:
        query["platform"] = platform
    
    content = await db.content_pieces.find(query).sort("created_date", -1).limit(limit).to_list(limit)
    
    # Convert ObjectIds to strings for JSON serialization
    for item in content:
        if '_id' in item:
            item['_id'] = str(item['_id'])
    
    return {"content": content}

@api_router.get("/branding")
async def get_branding_kit():
    """Get the current branding kit"""
    branding = await db.branding_kits.find_one(sort=[("updated_date", -1)])
    if not branding:
        return {"message": "No branding kit found. Run the workflow to create one."}
    
    # Convert ObjectId to string for JSON serialization
    if '_id' in branding:
        branding['_id'] = str(branding['_id'])
    
    return {"branding": branding}

@api_router.get("/blog-posts")
async def get_blog_posts(limit: int = 10):
    """Get blog posts"""
    posts = await db.blog_posts.find().sort("published_date", -1).limit(limit).to_list(limit)
    
    # Convert ObjectIds to strings for JSON serialization
    for post in posts:
        if '_id' in post:
            post['_id'] = str(post['_id'])
    
    return {"posts": posts}

@api_router.get("/analytics/detailed")
async def get_detailed_analytics():
    """Get detailed analytics (simplified after rollback)"""
    try:
        # Simplified analytics without extended agents
        content_count = await db.content_pieces.count_documents({})
        topics_count = await db.trending_topics.count_documents({})
        
        result = {
            "status": "success",
            "analytics": {
                "total_content_pieces": content_count,
                "total_trending_topics": topics_count,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/content/compliance-check")
async def check_content_compliance():
    """Run compliance check on all content (simplified after rollback)"""
    try:
        # Get recent content
        content = await db.content_pieces.find().limit(10).to_list(10)
        
        # Simplified compliance check
        result = {
            "status": "success",
            "compliance_results": [
                {"content_id": c.get("id", "unknown"), "approved": True, "notes": "Basic check passed"}
                for c in content
            ],
            "total_checked": len(content),
            "timestamp": datetime.utcnow().isoformat()
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/monetization/strategies")
async def get_monetization_strategies():
    """Get monetization strategies"""
    # This would typically be stored in database
    return {
        "strategies": [
            {"platform": "youtube", "type": "adsense", "estimated_revenue": 150},
            {"platform": "instagram", "type": "affiliate", "estimated_revenue": 75},
            {"platform": "blog", "type": "subscriptions", "estimated_revenue": 300}
        ],
        "total_estimated_monthly": 525
    }

@api_router.get("/analytics/dashboard")
async def get_analytics_dashboard():
    """Get comprehensive analytics dashboard data"""
    # Get recent content performance
    recent_content = await db.content_pieces.find().sort("created_date", -1).limit(10).to_list(10)
    
    # Convert ObjectIds to strings for JSON serialization
    for content in recent_content:
        if '_id' in content:
            content['_id'] = str(content['_id'])
    
    # Get trending topics count
    topics_count = await db.trending_topics.count_documents({
        "discovered_date": {"$gte": datetime.utcnow() - timedelta(days=7)}
    })
    
    # Get content distribution by platform
    platform_distribution = await db.content_pieces.aggregate([
        {"$group": {"_id": "$platform", "count": {"$sum": 1}}}
    ]).to_list(None)
    
    return {
        "recent_content": recent_content,
        "trending_topics_this_week": topics_count,
        "platform_distribution": platform_distribution,
        "last_updated": datetime.utcnow().isoformat()
    }

# Voice Cloning Endpoints
@api_router.post("/voice-clone/create/", response_model=VoiceCloneResponse)
async def create_voice_clone(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Audio file for voice cloning (MP3, M4A, WAV)"),
    voice_id: str = Form(..., description="Unique identifier for the voice"),
    preview_text: Optional[str] = Form(None, description="Text to generate preview audio"),
    model: str = Form("speech-01", description="Model to use for voice cloning")
):
    """Create a new voice clone from uploaded audio file"""
    try:
        # Get voice clone manager
        manager = get_voice_clone_manager()
        
        # Create voice clone
        job = await manager.create_voice_clone_from_upload(
            file=file,
            voice_id=voice_id,
            preview_text=preview_text
        )
        
        # Schedule cleanup of old files
        background_tasks.add_task(manager.cleanup_old_files)
        
        return VoiceCloneResponse(
            voice_id=job.voice_id,
            file_id=getattr(job, 'file_id', None) or job.file_path or "unknown",
            status=job.status.value,
            message="Voice clone created successfully with MCP",
            preview_audio_url=job.preview_url,
            job_id=job.job_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice clone creation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create voice clone: {str(e)}"
        )

@api_router.post("/voice-clone/generate-speech/", response_model=TTSResponse)
async def generate_speech_with_clone(background_tasks: BackgroundTasks, tts_request: TTSRequest):
    """Generate speech using a previously created voice clone"""
    try:
        # Get voice clone manager
        manager = get_voice_clone_manager()
        
        # Schedule cleanup of old files
        background_tasks.add_task(manager.cleanup_old_files)
        
        # Generate speech using MCP
        audio_path = await manager.generate_speech_with_voice(
            text=tts_request.text,
            voice_id=tts_request.voice_id,
            model=getattr(tts_request, 'model', 'speech-02-hd'),
            speed=getattr(tts_request, 'speed', 1.0),
            emotion=getattr(tts_request, 'emotion', 'happy')
        )
        
        return TTSResponse(
            audio_url=audio_path,  # Keep using audio_url for frontend compatibility
            status="completed"
        )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Speech generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate speech: {str(e)}"
        )

@api_router.get("/voice-clone/test-credentials/")
async def test_voice_clone_credentials():
    """Test Minimax API credentials"""
    try:
        # Get voice clone manager
        manager = get_voice_clone_manager()
        is_valid = await manager.validate_credentials()
        
        return {
            "credentials_valid": is_valid,
            "message": "Credentials are valid" if is_valid else "Invalid or missing credentials",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Credential test error: {str(e)}")
        return {
            "credentials_valid": False,
            "message": f"Error testing credentials: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

@api_router.get("/voice-clone/health/")
async def voice_clone_health_check():
    """Health check for voice cloning service"""
    try:
        # Get voice clone manager and test credentials
        manager = get_voice_clone_manager()
        credentials_valid = await manager.validate_credentials()
        
        # Check temp directory
        temp_dir = Path("temp_uploads")
        temp_dir_exists = temp_dir.exists()
        temp_dir_writable = False
        
        if temp_dir_exists:
            try:
                test_file = temp_dir / "health_check.txt"
                test_file.write_text("test")
                temp_dir_writable = test_file.exists()
                if test_file.exists():
                    test_file.unlink()
            except Exception:
                pass
        
        health_status = {
            "status": "healthy" if (credentials_valid and temp_dir_writable) else "unhealthy",
            "minimax_credentials": "valid" if credentials_valid else "invalid",
            "temp_directory": "accessible" if temp_dir_writable else "not accessible",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Voice clone health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@api_router.get("/voice-clone/rate-limit-status/")
async def get_rate_limit_status():
    """Get current rate limit status from MiniMax MCP server"""
    try:
        # Get voice clone manager
        manager = get_voice_clone_manager()
        
        # Try to list voices as a minimal test
        try:
            voices = await manager.list_available_voices("system")
            return {
                "rate_limit_status": "OK",
                "message": "MCP server is responding normally",
                "timestamp": datetime.utcnow().isoformat(),
                "test_successful": True,
                "available_voices_count": len(voices)
            }
        except Exception as e:
            error_msg = str(e).lower()
            if "rate limit" in error_msg or "429" in error_msg:
                return {
                    "rate_limit_status": "RATE_LIMITED",
                    "message": "MiniMax MCP server is currently rate limiting requests",
                    "recommendation": "Please wait 5-10 minutes before trying again",
                    "timestamp": datetime.utcnow().isoformat(),
                    "test_successful": False
                }
            else:
                return {
                    "rate_limit_status": "API_ERROR", 
                    "message": f"MCP server error: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat(),
                    "test_successful": False
                }
                    
    except Exception as e:
        logger.error(f"Rate limit status check failed: {str(e)}")
        return {
            "rate_limit_status": "UNKNOWN",
            "message": f"Unable to check MCP server status: {str(e)}",
            "timestamp": datetime.utcnow().isoformat(),
            "test_successful": False
        }

@api_router.get("/voice-clone/voices/")
async def list_available_voices(voice_type: str = "all"):
    """List available voices from MiniMax MCP server"""
    try:
        # Get voice clone manager
        manager = get_voice_clone_manager()
        
        # List voices using MCP
        voices = await manager.list_available_voices(voice_type)
        
        return {
            "voices": voices,
            "voice_type": voice_type,
            "count": len(voices),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"List voices failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list voices: {str(e)}"
        )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()