import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json
import os
import uuid

from agent_clusters import BaseCluster, ClusterStatus
from event_bus import event_bus, EventTypes, EventPriority, event_handler
from emergentintegrations.llm.chat import LlmChat, UserMessage
from minimax_mcp_client import get_voice_clone_manager

logger = logging.getLogger(__name__)

class CreationEngine(BaseCluster):
    """
    Creation Engine - Handles multi-format content generation, voice cloning integration,
    visual asset creation, and quality assurance.
    """
    
    def __init__(self):
        super().__init__(
            "Creation Engine",
            "Generates multi-format content with voice cloning and visual assets"
        )
        
        # Creation-specific configuration
        self.config = {
            "supported_formats": ["video_script", "blog_post", "social_post", "tutorial", "infographic"],
            "voice_models": ["speech-02-hd", "speech-02-turbo"],
            "default_voice_emotion": "happy",
            "content_quality_threshold": 0.8,
            "max_parallel_tasks": 5,
            "auto_voice_generation": True
        }
        
        # Creation state
        self.active_projects = {}
        self.voice_manager = None
        self.content_templates = {}
        self.quality_metrics = {}
        
        # Initialize voice manager
        self._init_voice_manager()
        
        # Initialize database connection (will be set from server.py)
        self.db = None
    
    def _init_voice_manager(self):
        """Initialize voice cloning manager"""
        try:
            self.voice_manager = get_voice_clone_manager()
            logger.info("Creation Engine: Voice manager initialized")
        except Exception as e:
            logger.warning(f"Creation Engine: Failed to initialize voice manager: {str(e)}")
    
    def set_database(self, db):
        """Set database connection"""
        self.db = db
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process creation tasks"""
        task_type = task_data.get("type", "unknown")
        
        start_time = datetime.now(timezone.utc)
        try:
            self.status = ClusterStatus.PROCESSING
            
            if task_type == "generate_content":
                result = await self._generate_content(task_data.get("data", {}))
            elif task_type == "create_voice_audio":
                result = await self._create_voice_audio(task_data.get("data", {}))
            elif task_type == "generate_assets":
                result = await self._generate_visual_assets(task_data.get("data", {}))
            elif task_type == "quality_check":
                result = await self._quality_check(task_data.get("data", {}))
            elif task_type == "batch_create":
                result = await self._batch_create_content(task_data.get("data", {}))
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
    
    async def _generate_content(self, content_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content based on specification"""
        logger.info(f"Creation Engine: Generating content - {content_spec.get('topic', 'Unknown topic')}")
        
        content_type = content_spec.get("content_type", "blog_post")
        topic = content_spec.get("topic", "")
        platform = content_spec.get("platform", "youtube")
        voice_clone_needed = content_spec.get("voice_clone_needed", False)
        
        try:
            # Generate content based on type
            if content_type == "video_script":
                content = await self._generate_video_script(topic, platform)
            elif content_type == "blog_post":
                content = await self._generate_blog_post(topic)
            elif content_type == "social_post":
                content = await self._generate_social_post(topic, platform)
            elif content_type == "tutorial":
                content = await self._generate_tutorial(topic)
            else:
                content = await self._generate_generic_content(topic, content_type)
            
            # Add metadata
            content_item = {
                "id": str(uuid.uuid4()),
                "content_type": content_type,
                "topic": topic,
                "platform": platform,
                "content": content,
                "created_at": datetime.now(timezone.utc),
                "voice_clone_needed": voice_clone_needed,
                "quality_score": 0.85,  # Placeholder - would be calculated
                "status": "created"
            }
            
            # Generate voice audio if needed
            if voice_clone_needed and self.voice_manager:
                try:
                    voice_result = await self._add_voice_to_content(content_item)
                    content_item.update(voice_result)
                except Exception as e:
                    logger.warning(f"Voice generation failed: {str(e)}")
                    content_item["voice_error"] = str(e)
            
            # Save to database
            if self.db:
                await self._save_content_to_db(content_item)
            
            # Emit content created event
            await event_bus.emit(
                EventTypes.CONTENT_CREATED,
                content_item,
                source=self.cluster_name,
                priority=EventPriority.NORMAL
            )
            
            logger.info(f"Creation Engine: Content created successfully - {content_item['id']}")
            return content_item
            
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            raise
    
    async def _generate_video_script(self, topic: str, platform: str) -> Dict[str, Any]:
        """Generate video script for specified platform"""
        
        # Platform-specific script requirements
        platform_specs = {
            "youtube": {"duration": "8-12 minutes", "style": "educational", "hooks": True},
            "tiktok": {"duration": "30-60 seconds", "style": "engaging", "hooks": True},
            "instagram": {"duration": "30-90 seconds", "style": "visual", "hooks": True}
        }
        
        spec = platform_specs.get(platform, platform_specs["youtube"])
        
        prompt = f"""
        Create a compelling video script for {platform} about: {topic}
        
        Requirements:
        - Duration: {spec['duration']}
        - Style: {spec['style']}
        - Include hooks: {spec['hooks']}
        - Optimize for voice cloning (clear, natural speech patterns)
        
        Structure the script with:
        1. Hook (first 5 seconds)
        2. Introduction
        3. Main content (3-5 key points)
        4. Call to action
        5. Outro
        
        Respond in JSON format:
        {{
            "title": "video_title",
            "hook": "attention_grabbing_opening",
            "introduction": "introduction_text",
            "main_points": [
                {{"point": "main_point_1", "explanation": "detailed_explanation"}},
                {{"point": "main_point_2", "explanation": "detailed_explanation"}}
            ],
            "call_to_action": "cta_text",
            "outro": "closing_text",
            "full_script": "complete_narration_script",
            "estimated_duration": "duration_in_seconds",
            "voice_notes": "guidance_for_voice_delivery"
        }}
        """
        
        result = await self.llm_chat.run_chat([UserMessage(content=prompt)])
        
        try:
            script = json.loads(result.content)
        except json.JSONDecodeError:
            # Fallback script
            script = {
                "title": f"Mastering {topic}: Complete Guide",
                "hook": f"Did you know {topic} could revolutionize your workflow? Let me show you how.",
                "introduction": f"Welcome! Today we're diving deep into {topic} and I'll show you exactly how to get started.",
                "main_points": [
                    {"point": "Understanding the basics", "explanation": f"First, let's understand what {topic} is and why it matters."},
                    {"point": "Practical implementation", "explanation": "Now I'll walk you through the step-by-step process."},
                    {"point": "Advanced techniques", "explanation": "Here are some pro tips to take your skills to the next level."}
                ],
                "call_to_action": "If this helped you, please like and subscribe for more tutorials!",
                "outro": "Thanks for watching, and I'll see you in the next video!",
                "full_script": f"Did you know {topic} could revolutionize your workflow? Let me show you how. Welcome! Today we're diving deep into {topic}...",
                "estimated_duration": "480",
                "voice_notes": "Speak with enthusiasm and pause between main points"
            }
        
        return script
    
    async def _generate_blog_post(self, topic: str) -> Dict[str, Any]:
        """Generate comprehensive blog post"""
        
        prompt = f"""
        Write a comprehensive, SEO-optimized blog post about: {topic}
        
        Requirements:
        - 1500-2000 words
        - SEO-friendly structure with headers
        - Include actionable insights
        - Professional tone
        - Include call-to-action
        
        Structure:
        1. Compelling title and meta description
        2. Introduction with hook
        3. Main content with H2/H3 headers
        4. Practical examples or case studies
        5. Conclusion with CTA
        
        Respond in JSON format:
        {{
            "title": "seo_optimized_title",
            "meta_description": "meta_description_under_160_chars",
            "introduction": "engaging_introduction_paragraph",
            "sections": [
                {{"header": "section_title", "content": "section_content"}},
                {{"header": "section_title", "content": "section_content"}}
            ],
            "conclusion": "conclusion_with_cta",
            "tags": ["tag1", "tag2", "tag3"],
            "estimated_read_time": "minutes",
            "seo_keywords": ["keyword1", "keyword2"]
        }}
        """
        
        result = await self.llm_chat.run_chat([UserMessage(content=prompt)])
        
        try:
            blog_post = json.loads(result.content)
        except json.JSONDecodeError:
            # Fallback blog post
            blog_post = {
                "title": f"The Complete Guide to {topic}: Everything You Need to Know",
                "meta_description": f"Learn everything about {topic} with this comprehensive guide. Practical tips, examples, and actionable insights included.",
                "introduction": f"In today's rapidly evolving digital landscape, understanding {topic} has become crucial for success.",
                "sections": [
                    {"header": f"What is {topic}?", "content": f"Let's start with the fundamentals of {topic} and why it matters."},
                    {"header": "Getting Started", "content": "Here's your step-by-step guide to begin your journey."},
                    {"header": "Best Practices", "content": "These proven strategies will help you succeed."},
                    {"header": "Common Mistakes to Avoid", "content": "Learn from others' mistakes and avoid these pitfalls."}
                ],
                "conclusion": "Ready to get started? Subscribe to our newsletter for more insights and tutorials!",
                "tags": [topic.lower(), "tutorial", "guide"],
                "estimated_read_time": "8",
                "seo_keywords": [topic.lower(), f"{topic} guide", f"how to {topic}"]
            }
        
        return blog_post
    
    async def _generate_social_post(self, topic: str, platform: str) -> Dict[str, Any]:
        """Generate platform-specific social media post"""
        
        platform_specs = {
            "instagram": {"char_limit": 2200, "hashtags": 20, "style": "visual"},
            "twitter": {"char_limit": 280, "hashtags": 5, "style": "concise"},
            "facebook": {"char_limit": 500, "hashtags": 5, "style": "conversational"},
            "linkedin": {"char_limit": 3000, "hashtags": 10, "style": "professional"}
        }
        
        spec = platform_specs.get(platform, platform_specs["instagram"])
        
        prompt = f"""
        Create an engaging social media post for {platform} about: {topic}
        
        Requirements:
        - Character limit: {spec['char_limit']}
        - Style: {spec['style']}
        - Include up to {spec['hashtags']} relevant hashtags
        - Include call-to-action
        - Optimize for engagement
        
        Respond in JSON format:
        {{
            "post_text": "main_post_content",
            "hashtags": ["hashtag1", "hashtag2"],
            "call_to_action": "cta_text",
            "character_count": 150,
            "engagement_tips": ["tip1", "tip2"]
        }}
        """
        
        result = await self.llm_chat.run_chat([UserMessage(content=prompt)])
        
        try:
            social_post = json.loads(result.content)
        except json.JSONDecodeError:
            # Fallback social post
            social_post = {
                "post_text": f"🚀 Just discovered something amazing about {topic}! This could be a game-changer for anyone working in tech. What's your experience with {topic}? Share in the comments!",
                "hashtags": [f"#{topic.replace(' ', '')}", "#Tech", "#Innovation", "#AI", "#Tutorial"],
                "call_to_action": "Follow for more tech insights!",
                "character_count": 180,
                "engagement_tips": ["Ask questions", "Use emojis", "Post at optimal times"]
            }
        
        return social_post
    
    async def _generate_tutorial(self, topic: str) -> Dict[str, Any]:
        """Generate step-by-step tutorial"""
        
        prompt = f"""
        Create a detailed, step-by-step tutorial about: {topic}
        
        Requirements:
        - Clear, actionable steps
        - Include prerequisites
        - Add troubleshooting tips
        - Suitable for beginners to intermediate level
        
        Respond in JSON format:
        {{
            "title": "tutorial_title",
            "difficulty": "beginner/intermediate/advanced",
            "estimated_time": "completion_time",
            "prerequisites": ["prerequisite1", "prerequisite2"],
            "tools_needed": ["tool1", "tool2"],
            "steps": [
                {{"step_number": 1, "title": "step_title", "description": "detailed_description", "tips": ["tip1"]}},
                {{"step_number": 2, "title": "step_title", "description": "detailed_description", "tips": ["tip1"]}}
            ],
            "troubleshooting": [
                {{"issue": "common_issue", "solution": "solution_description"}}
            ],
            "next_steps": "what_to_do_after_completion"
        }}
        """
        
        result = await self.llm_chat.run_chat([UserMessage(content=prompt)])
        
        try:
            tutorial = json.loads(result.content)
        except json.JSONDecodeError:
            # Fallback tutorial
            tutorial = {
                "title": f"How to Get Started with {topic}: Step-by-Step Tutorial",
                "difficulty": "beginner",
                "estimated_time": "30 minutes",
                "prerequisites": ["Basic computer knowledge", "Internet connection"],
                "tools_needed": ["Web browser", "Text editor"],
                "steps": [
                    {"step_number": 1, "title": "Initial Setup", "description": f"First, let's set up your environment for {topic}.", "tips": ["Take your time", "Follow each step carefully"]},
                    {"step_number": 2, "title": "Configuration", "description": "Now we'll configure the basic settings.", "tips": ["Save your work frequently"]},
                    {"step_number": 3, "title": "Testing", "description": "Let's test to make sure everything works correctly.", "tips": ["Don't skip this step"]}
                ],
                "troubleshooting": [
                    {"issue": "Setup fails", "solution": "Check your internet connection and try again"}
                ],
                "next_steps": "Explore advanced features and customization options"
            }
        
        return tutorial
    
    async def _generate_generic_content(self, topic: str, content_type: str) -> Dict[str, Any]:
        """Generate generic content for unknown types"""
        
        prompt = f"""
        Create {content_type} content about: {topic}
        
        Make it engaging, informative, and actionable.
        Include relevant examples and practical insights.
        
        Respond in JSON format:
        {{
            "title": "content_title",
            "main_content": "primary_content_text",
            "key_points": ["point1", "point2", "point3"],
            "call_to_action": "cta_text",
            "additional_resources": ["resource1", "resource2"]
        }}
        """
        
        result = await self.llm_chat.run_chat([UserMessage(content=prompt)])
        
        try:
            content = json.loads(result.content)
        except json.JSONDecodeError:
            # Fallback content
            content = {
                "title": f"Understanding {topic}",
                "main_content": f"This comprehensive overview of {topic} covers the essential concepts and practical applications you need to know.",
                "key_points": ["Foundation concepts", "Practical applications", "Best practices"],
                "call_to_action": "Ready to learn more? Explore our additional resources!",
                "additional_resources": ["Official documentation", "Community forums", "Video tutorials"]
            }
        
        return content
    
    async def _add_voice_to_content(self, content_item: Dict[str, Any]) -> Dict[str, Any]:
        """Add voice audio to content item"""
        logger.info(f"Creation Engine: Adding voice to content - {content_item['id']}")
        
        try:
            # Extract text for voice generation
            text_content = self._extract_voice_text(content_item)
            
            if not text_content or len(text_content.strip()) == 0:
                return {"voice_error": "No text content found for voice generation"}
            
            # Use default voice or get from configuration
            voice_id = content_item.get("voice_id", "female-shaonv")  # Default voice
            
            # Generate voice audio
            audio_url = await self.voice_manager.generate_speech_with_voice(
                text=text_content[:1000],  # Limit to 1000 characters
                voice_id=voice_id,
                model="speech-02-hd",
                emotion=self.config["default_voice_emotion"]
            )
            
            # Emit voice clone ready event
            await event_bus.emit(
                EventTypes.VOICE_CLONE_READY,
                {
                    "content_id": content_item["id"],
                    "audio_url": audio_url,
                    "voice_id": voice_id,
                    "text_preview": text_content[:100] + "..."
                },
                source=self.cluster_name
            )
            
            return {
                "voice_audio_url": audio_url,
                "voice_id_used": voice_id,
                "voice_generation_success": True
            }
            
        except Exception as e:
            logger.warning(f"Voice generation failed for content {content_item['id']}: {str(e)}")
            return {
                "voice_error": str(e),
                "voice_generation_success": False
            }
    
    def _extract_voice_text(self, content_item: Dict[str, Any]) -> str:
        """Extract appropriate text for voice generation from content"""
        content = content_item.get("content", {})
        content_type = content_item.get("content_type", "")
        
        if content_type == "video_script":
            return content.get("full_script", "")
        elif content_type == "blog_post":
            # Use introduction for voice
            return content.get("introduction", "")
        elif content_type == "social_post":
            return content.get("post_text", "")
        elif content_type == "tutorial":
            # Create summary from tutorial
            title = content.get("title", "")
            steps = content.get("steps", [])
            if steps:
                first_step = steps[0].get("description", "")
                return f"{title}. {first_step}"
            return title
        else:
            # Generic extraction
            return content.get("main_content", "") or content.get("content", "")
    
    async def _batch_create_content(self, batch_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create multiple content pieces in parallel"""
        logger.info(f"Creation Engine: Starting batch content creation")
        
        content_specs = batch_spec.get("content_list", [])
        max_parallel = min(len(content_specs), self.config["max_parallel_tasks"])
        
        # Create content in parallel batches
        results = []
        errors = []
        
        for i in range(0, len(content_specs), max_parallel):
            batch = content_specs[i:i + max_parallel]
            
            # Create tasks for parallel execution
            tasks = [
                self._generate_content(spec) for spec in batch
            ]
            
            # Execute batch
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in batch_results:
                if isinstance(result, Exception):
                    errors.append(str(result))
                else:
                    results.append(result)
        
        # Emit batch ready event
        await event_bus.emit(
            EventTypes.CONTENT_BATCH_READY,
            {
                "batch_id": str(uuid.uuid4()),
                "content_items": results,
                "success_count": len(results),
                "error_count": len(errors),
                "errors": errors
            },
            source=self.cluster_name,
            priority=EventPriority.HIGH
        )
        
        logger.info(f"Creation Engine: Batch creation completed - {len(results)} success, {len(errors)} errors")
        
        return {
            "content_items": results,
            "success_count": len(results),
            "error_count": len(errors),
            "errors": errors
        }
    
    async def _save_content_to_db(self, content_item: Dict[str, Any]):
        """Save content to database"""
        try:
            if self.db:
                await self.db.content_pieces.insert_one(content_item)
                logger.info(f"Content saved to database: {content_item['id']}")
        except Exception as e:
            logger.warning(f"Failed to save content to database: {str(e)}")
    
    @event_handler(EventTypes.STRATEGY_READY)
    async def handle_strategy_ready(self, event):
        """Handle content strategy from Intelligence Engine"""
        strategy = event.data
        logger.info("Creation Engine: Received content strategy")
        
        # Extract content calendar and create batch
        content_calendar = strategy.get("content_calendar", [])
        
        if content_calendar:
            # Convert calendar items to content specs
            content_specs = []
            for calendar_item in content_calendar[:5]:  # Limit to 5 items
                spec = {
                    "topic": calendar_item.get("topic", ""),
                    "content_type": calendar_item.get("content_type", "blog_post"),
                    "platform": calendar_item.get("platform", "youtube"),
                    "voice_clone_needed": calendar_item.get("voice_clone_needed", False)
                }
                content_specs.append(spec)
            
            # Start batch creation
            await self.process_task({
                "type": "batch_create",
                "data": {"content_list": content_specs}
            })
    
    def get_creation_summary(self) -> Dict[str, Any]:
        """Get comprehensive creation summary"""
        return {
            "active_projects": len(self.active_projects),
            "voice_manager_available": self.voice_manager is not None,
            "supported_formats": self.config["supported_formats"],
            "quality_metrics": self.quality_metrics,
            "config": self.config
        }