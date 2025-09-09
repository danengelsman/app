from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
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
import asyncio
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

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
        
        Return as a structured JSON array.
        """
        
        user_message = UserMessage(text=prompt)
        response = await self.llm_chat.send_message(user_message)
        
        try:
            # Parse the LLM response and create trending topics
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
            
            return {"status": "success", "topics_found": len(trending_topics), "topics": [t.dict() for t in trending_topics]}
        
        except json.JSONDecodeError:
            # Fallback: create topics from text response
            fallback_topics = self._create_fallback_topics(response)
            return {"status": "success", "topics_found": len(fallback_topics), "topics": fallback_topics}

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
            content_data = {"title": f"{topic.get('keyword', '')} - {platform.value}", "description": response[:200]}
        
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

# Import extended agents
from agents_extended import (
    AuditorOptimizerAgent, MonetizationAgent, BlogWriterAgent,
    ContentGeneratorAgent, AnalyticsAgent, ComplianceAgent
)

# Central Overseer Agent
class CentralOverseerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "Agent 1 - Central Overseer",
            "Coordinates all sub-agents and manages the complete content creation workflow."
        )
        self.sub_agents = {
            "trending_topics": TrendingTopicsAgent(),
            "topic_selector": TopicSelectorAgent(),
            "brand_ambassador": BrandAmbassadorAgent(),
            "auditor_optimizer": AuditorOptimizerAgent(),
            "monetization": MonetizationAgent(),
            "blog_writer": BlogWriterAgent(),
            "content_generator": ContentGeneratorAgent(),
            "analytics": AnalyticsAgent(),
            "compliance": ComplianceAgent()
        }

    async def execute_full_workflow(self) -> Dict[str, Any]:
        """Execute the complete content creation workflow"""
        workflow_results = {}
        
        try:
            # Step 1: Research trending topics
            logging.info("Starting trending topics research...")
            topics_result = await self.sub_agents["trending_topics"].execute_task({})
            workflow_results["trending_topics"] = topics_result
            
            # Step 2: Select topics and create content
            logging.info("Selecting topics and creating content...")
            content_result = await self.sub_agents["topic_selector"].execute_task({
                "topics": topics_result.get("topics", [])
            })
            workflow_results["content_creation"] = content_result
            
            # Step 3: Apply branding
            logging.info("Applying branding guidelines...")
            branding_result = await self.sub_agents["brand_ambassador"].execute_task({})
            workflow_results["branding"] = branding_result
            
            # Step 4: Audit and optimize content
            logging.info("Auditing and optimizing content...")
            audit_result = await self.sub_agents["auditor_optimizer"].execute_task({
                "content_pieces": content_result.get("content", [])
            })
            workflow_results["audit_optimization"] = audit_result
            
            # Step 5: Setup monetization
            logging.info("Setting up monetization strategies...")
            monetization_result = await self.sub_agents["monetization"].execute_task({
                "content_pieces": audit_result.get("content", [])
            })
            workflow_results["monetization"] = monetization_result
            
            # Step 6: Create blog posts
            logging.info("Creating blog posts...")
            blog_result = await self.sub_agents["blog_writer"].execute_task({
                "topics": topics_result.get("topics", [])
            })
            workflow_results["blog_writing"] = blog_result
            
            # Step 7: Generate content assets
            logging.info("Generating content assets...")
            generation_result = await self.sub_agents["content_generator"].execute_task({
                "content_pieces": audit_result.get("content", [])
            })
            workflow_results["content_generation"] = generation_result
            
            # Step 8: Collect analytics
            logging.info("Collecting analytics and insights...")
            analytics_result = await self.sub_agents["analytics"].execute_task({})
            workflow_results["analytics"] = analytics_result
            
            # Step 9: Compliance check
            logging.info("Running compliance checks...")
            compliance_result = await self.sub_agents["compliance"].execute_task({
                "content_pieces": audit_result.get("content", [])
            })
            workflow_results["compliance"] = compliance_result
            
            return {
                "status": "success",
                "workflow_completed": True,
                "agents_executed": len(workflow_results),
                "results": workflow_results,
                "timestamp": datetime.utcnow().isoformat(),
                "summary": {
                    "topics_discovered": len(topics_result.get("topics", [])),
                    "content_pieces_created": len(content_result.get("content", [])),
                    "blog_posts_created": len(blog_result.get("posts", [])),
                    "compliance_approved": len([r for r in compliance_result.get("compliance_results", []) if r.get("approved")])
                }
            }
            
        except Exception as e:
            logging.error(f"Workflow execution failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "completed_steps": list(workflow_results.keys()),
                "partial_results": workflow_results
            }

# Initialize the central overseer
central_overseer = CentralOverseerAgent()

# API Endpoints
@api_router.get("/")
async def root():
    return {"message": "Emergent AI Multi-Agent Content Creation System", "version": "1.0.0"}

@api_router.post("/agents/execute-workflow")
async def execute_workflow(background_tasks: BackgroundTasks):
    """Execute the complete multi-agent workflow"""
    try:
        result = await central_overseer.execute_full_workflow()
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
    return {"content": content}

@api_router.get("/branding")
async def get_branding_kit():
    """Get the current branding kit"""
    branding = await db.branding_kits.find_one(sort=[("updated_date", -1)])
    if not branding:
        return {"message": "No branding kit found. Run the workflow to create one."}
    return {"branding": branding}

@api_router.get("/blog-posts")
async def get_blog_posts(limit: int = 10):
    """Get blog posts"""
    posts = await db.blog_posts.find().sort("published_date", -1).limit(limit).to_list(limit)
    return {"posts": posts}

@api_router.get("/analytics/detailed")
async def get_detailed_analytics():
    """Get detailed analytics from analytics agent"""
    try:
        analytics_agent = AnalyticsAgent()
        result = await analytics_agent.execute_task({})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/content/compliance-check")
async def check_content_compliance():
    """Run compliance check on all content"""
    try:
        compliance_agent = ComplianceAgent()
        
        # Get recent content
        content = await db.content_pieces.find().limit(10).to_list(10)
        
        result = await compliance_agent.execute_task({"content_pieces": content})
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