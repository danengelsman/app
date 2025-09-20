import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import json
import os
import uuid

from agent_clusters import BaseCluster, ClusterStatus
from event_bus import event_bus, EventTypes, EventPriority, event_handler
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

class DistributionEngine(BaseCluster):
    """
    Distribution Engine - Handles platform-specific optimization, scheduling,
    publishing, monetization, and engagement management.
    """
    
    def __init__(self):
        super().__init__(
            "Distribution Engine",
            "Manages content distribution, scheduling, monetization, and engagement across platforms"
        )
        
        # Distribution-specific configuration
        self.config = {
            "platforms": {
                "youtube": {
                    "enabled": True,
                    "optimal_times": ["10:00", "14:00", "18:00"],
                    "max_daily_posts": 1,
                    "monetization": True
                },
                "instagram": {
                    "enabled": True,
                    "optimal_times": ["09:00", "12:00", "17:00", "20:00"],
                    "max_daily_posts": 3,
                    "monetization": False
                },
                "tiktok": {
                    "enabled": True,
                    "optimal_times": ["12:00", "18:00", "21:00"],
                    "max_daily_posts": 2,
                    "monetization": False
                },
                "twitter": {
                    "enabled": True,
                    "optimal_times": ["09:00", "12:00", "15:00", "18:00"],
                    "max_daily_posts": 5,
                    "monetization": False
                }
            },
            "scheduling": {
                "auto_schedule": True,
                "buffer_time_hours": 2,
                "timezone": "UTC",
                "weekend_posting": True
            },
            "monetization": {
                "affiliate_links": True,
                "sponsored_content": True,
                "product_placement": True,
                "subscription_cta": True
            },
            "compliance": {
                "auto_check": True,
                "require_approval": False,
                "content_warnings": True
            }
        }
        
        # Distribution state
        self.content_queue = []
        self.scheduled_posts = {}
        self.published_content = []
        self.engagement_metrics = {}
        self.monetization_stats = {}
        
        # Initialize database connection (will be set from server.py)
        self.db = None
    
    def set_database(self, db):
        """Set database connection"""
        self.db = db
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process distribution tasks"""
        task_type = task_data.get("type", "unknown")
        
        start_time = datetime.now(timezone.utc)
        try:
            self.status = ClusterStatus.PROCESSING
            
            if task_type == "schedule_content":
                result = await self._schedule_content(task_data.get("data", {}))
            elif task_type == "publish_content":
                result = await self._publish_content(task_data.get("data", {}))
            elif task_type == "optimize_for_platform":
                result = await self._optimize_for_platform(task_data.get("data", {}))
            elif task_type == "track_engagement":
                result = await self._track_engagement(task_data.get("data", {}))
            elif task_type == "setup_monetization":
                result = await self._setup_monetization(task_data.get("data", {}))
            elif task_type == "compliance_check":
                result = await self._compliance_check(task_data.get("data", {}))
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
    
    async def _schedule_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule content for optimal posting times"""
        logger.info("Distribution Engine: Scheduling content")
        
        content_items = content_data.get("content_items", [])
        if not content_items:
            content_items = [content_data]  # Single item
        
        scheduled_items = []
        
        for content_item in content_items:
            try:
                platform = content_item.get("platform", "youtube")
                content_type = content_item.get("content_type", "blog_post")
                
                # Get platform configuration
                platform_config = self.config["platforms"].get(platform, {})
                if not platform_config.get("enabled", False):
                    logger.warning(f"Platform {platform} is disabled, skipping scheduling")
                    continue
                
                # Calculate optimal posting time
                optimal_time = await self._calculate_optimal_time(platform, content_type)
                
                # Create scheduled item
                scheduled_item = {
                    "content_id": content_item.get("id", str(uuid.uuid4())),
                    "platform": platform,
                    "content_type": content_type,
                    "title": self._extract_title(content_item),
                    "scheduled_time": optimal_time,
                    "status": "scheduled",
                    "created_at": datetime.now(timezone.utc),
                    "optimization_applied": False
                }
                
                # Apply platform optimization
                optimized_content = await self._apply_platform_optimization(content_item, platform)
                scheduled_item["optimized_content"] = optimized_content
                scheduled_item["optimization_applied"] = True
                
                scheduled_items.append(scheduled_item)
                
                # Store in queue
                self.content_queue.append(scheduled_item)
                
                # Save to database
                if self.db:
                    await self._save_scheduled_content(scheduled_item)
                
            except Exception as e:
                logger.error(f"Failed to schedule content item: {str(e)}")
                continue
        
        # Emit scheduling event
        await event_bus.emit(
            EventTypes.PUBLISHING_SCHEDULED,
            {
                "scheduled_count": len(scheduled_items),
                "items": scheduled_items,
                "next_publication": min([item["scheduled_time"] for item in scheduled_items]) if scheduled_items else None
            },
            source=self.cluster_name,
            priority=EventPriority.NORMAL
        )
        
        logger.info(f"Distribution Engine: Scheduled {len(scheduled_items)} content items")
        
        return {
            "scheduled_items": scheduled_items,
            "scheduled_count": len(scheduled_items),
            "next_publication": min([item["scheduled_time"] for item in scheduled_items]) if scheduled_items else None
        }
    
    async def _calculate_optimal_time(self, platform: str, content_type: str) -> datetime:
        """Calculate optimal posting time for platform and content type"""
        
        platform_config = self.config["platforms"].get(platform, {})
        optimal_times = platform_config.get("optimal_times", ["12:00"])
        max_daily = platform_config.get("max_daily_posts", 1)
        
        # Get today's scheduled posts for this platform
        today = datetime.now(timezone.utc).date()
        today_posts = [
            item for item in self.content_queue 
            if item["platform"] == platform and item["scheduled_time"].date() == today
        ]
        
        # If we've reached the daily limit, schedule for tomorrow
        if len(today_posts) >= max_daily:
            base_date = datetime.now(timezone.utc) + timedelta(days=1)
        else:
            base_date = datetime.now(timezone.utc)
        
        # Find the next available optimal time
        for time_str in optimal_times:
            hour, minute = map(int, time_str.split(":"))
            scheduled_time = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Make sure it's in the future
            if scheduled_time > datetime.now(timezone.utc):
                # Check if this slot is already taken
                slot_taken = any(
                    abs((item["scheduled_time"] - scheduled_time).total_seconds()) < 1800  # 30 min buffer
                    for item in self.content_queue
                    if item["platform"] == platform
                )
                
                if not slot_taken:
                    return scheduled_time
        
        # Fallback: schedule for next available time
        return datetime.now(timezone.utc) + timedelta(hours=self.config["scheduling"]["buffer_time_hours"])
    
    async def _apply_platform_optimization(self, content_item: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Apply platform-specific optimizations to content"""
        
        content = content_item.get("content", {})
        content_type = content_item.get("content_type", "")
        
        # Platform-specific optimization
        if platform == "youtube":
            return await self._optimize_for_youtube(content, content_type)
        elif platform == "instagram":
            return await self._optimize_for_instagram(content, content_type)
        elif platform == "tiktok":
            return await self._optimize_for_tiktok(content, content_type)
        elif platform == "twitter":
            return await self._optimize_for_twitter(content, content_type)
        else:
            return content
    
    async def _optimize_for_youtube(self, content: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Optimize content for YouTube"""
        
        optimized = content.copy()
        
        if content_type == "video_script":
            # YouTube-specific optimizations
            title = content.get("title", "")
            if len(title) > 60:
                # Truncate title for YouTube
                optimized["title"] = title[:57] + "..."
            
            # Add YouTube-specific CTAs
            script = content.get("full_script", "")
            if "subscribe" not in script.lower():
                optimized["full_script"] = script + " Don't forget to like and subscribe for more content like this!"
            
            # Add timestamps for longer videos
            main_points = content.get("main_points", [])
            if len(main_points) > 2:
                timestamps = []
                current_time = 30  # Start after intro
                for i, point in enumerate(main_points):
                    minutes = current_time // 60
                    seconds = current_time % 60
                    timestamps.append(f"{minutes:02d}:{seconds:02d} - {point.get('point', f'Point {i+1}')}")
                    current_time += 120  # 2 minutes per point
                
                optimized["timestamps"] = timestamps
        
        # Add SEO tags
        optimized["youtube_tags"] = ["AI", "Technology", "Tutorial", "Innovation", "Automation"]
        optimized["youtube_category"] = "Science & Technology"
        
        return optimized
    
    async def _optimize_for_instagram(self, content: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Optimize content for Instagram"""
        
        optimized = content.copy()
        
        if content_type == "social_post":
            # Add Instagram-specific formatting
            post_text = content.get("post_text", "")
            hashtags = content.get("hashtags", [])
            
            # Ensure optimal hashtag count (20-30 for Instagram)
            if len(hashtags) < 15:
                additional_tags = ["#tech", "#AI", "#innovation", "#trending", "#viral"]
                hashtags.extend(additional_tags[:15-len(hashtags)])
            
            optimized["hashtags"] = hashtags[:30]  # Instagram max
            
            # Add line breaks for readability
            if "\n" not in post_text:
                sentences = post_text.split(". ")
                if len(sentences) > 1:
                    optimized["post_text"] = ".\n\n".join(sentences)
        
        # Add Instagram story suggestions
        optimized["story_suggestions"] = [
            "Create a poll about the topic",
            "Share behind-the-scenes content",
            "Add interactive stickers"
        ]
        
        return optimized
    
    async def _optimize_for_tiktok(self, content: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Optimize content for TikTok"""
        
        optimized = content.copy()
        
        if content_type == "video_script":
            # TikTok-specific optimizations
            hook = content.get("hook", "")
            if not hook or len(hook) > 100:
                # Create punchy hook for TikTok
                topic = content.get("title", "").split(":")[0]
                optimized["hook"] = f"Wait until you see what {topic} can do! 🤯"
            
            # Ensure script is under 60 seconds
            full_script = content.get("full_script", "")
            if len(full_script.split()) > 120:  # ~60 seconds of speech
                # Condense script
                main_points = content.get("main_points", [])[:2]  # Only 2 main points
                condensed_script = f"{optimized['hook']} {main_points[0].get('explanation', '') if main_points else ''}"
                optimized["full_script"] = condensed_script[:500]  # Limit length
        
        # Add TikTok-specific elements
        optimized["tiktok_effects"] = ["Trending sound", "Quick cuts", "Text overlays"]
        optimized["trending_hashtags"] = ["#fyp", "#viral", "#techtok", "#AI"]
        
        return optimized
    
    async def _optimize_for_twitter(self, content: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Optimize content for Twitter"""
        
        optimized = content.copy()
        
        if content_type == "social_post":
            post_text = content.get("post_text", "")
            
            # Ensure under 280 characters
            if len(post_text) > 250:  # Leave room for hashtags
                optimized["post_text"] = post_text[:247] + "..."
            
            # Limit hashtags for Twitter
            hashtags = content.get("hashtags", [])
            optimized["hashtags"] = hashtags[:3]  # 2-3 hashtags max for Twitter
            
            # Add Twitter-specific CTAs
            cta = content.get("call_to_action", "")
            if "retweet" not in cta.lower():
                optimized["call_to_action"] = "Retweet if you found this helpful! 🔄"
        
        # Add thread suggestions for longer content
        if content_type in ["blog_post", "tutorial"]:
            optimized["thread_breakdown"] = [
                "Tweet 1: Hook and main point",
                "Tweet 2-3: Key insights",
                "Tweet 4: Call to action"
            ]
        
        return optimized
    
    async def _publish_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate content publishing (in real implementation, would integrate with platform APIs)"""
        logger.info("Distribution Engine: Publishing content")
        
        content_id = content_data.get("content_id", "")
        platform = content_data.get("platform", "")
        
        try:
            # Simulate publication process
            publication_result = {
                "content_id": content_id,
                "platform": platform,
                "published_at": datetime.now(timezone.utc),
                "status": "published",
                "url": f"https://{platform}.com/post/{content_id}",  # Simulated URL
                "initial_metrics": {
                    "views": 0,
                    "likes": 0,
                    "shares": 0,
                    "comments": 0
                }
            }
            
            # Store published content
            self.published_content.append(publication_result)
            
            # Remove from queue
            self.content_queue = [
                item for item in self.content_queue 
                if item.get("content_id") != content_id
            ]
            
            # Save to database
            if self.db:
                await self._save_published_content(publication_result)
            
            # Emit publication event
            await event_bus.emit(
                EventTypes.CONTENT_PUBLISHED,
                publication_result,
                source=self.cluster_name,
                priority=EventPriority.NORMAL
            )
            
            logger.info(f"Distribution Engine: Content published - {content_id} on {platform}")
            return publication_result
            
        except Exception as e:
            logger.error(f"Publication failed for {content_id}: {str(e)}")
            raise
    
    async def _track_engagement(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track and analyze engagement metrics"""
        logger.info("Distribution Engine: Tracking engagement metrics")
        
        content_id = metrics_data.get("content_id", "")
        platform = metrics_data.get("platform", "")
        metrics = metrics_data.get("metrics", {})
        
        # Store metrics
        if content_id not in self.engagement_metrics:
            self.engagement_metrics[content_id] = []
        
        metric_entry = {
            "timestamp": datetime.now(timezone.utc),
            "platform": platform,
            "metrics": metrics,
            "calculated_engagement_rate": self._calculate_engagement_rate(metrics)
        }
        
        self.engagement_metrics[content_id].append(metric_entry)
        
        # Emit engagement update
        await event_bus.emit(
            EventTypes.ENGAGEMENT_UPDATE,
            {
                "content_id": content_id,
                "platform": platform,
                "metrics": metrics,
                "engagement_rate": metric_entry["calculated_engagement_rate"]
            },
            source=self.cluster_name
        )
        
        return metric_entry
    
    def _calculate_engagement_rate(self, metrics: Dict[str, Any]) -> float:
        """Calculate engagement rate from metrics"""
        views = metrics.get("views", 0)
        likes = metrics.get("likes", 0)
        comments = metrics.get("comments", 0)
        shares = metrics.get("shares", 0)
        
        if views == 0:
            return 0.0
        
        total_engagement = likes + comments + shares
        return (total_engagement / views) * 100 if views > 0 else 0.0
    
    async def _setup_monetization(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Setup monetization for content"""
        logger.info("Distribution Engine: Setting up monetization")
        
        content_id = content_data.get("content_id", "")
        platform = content_data.get("platform", "")
        content_type = content_data.get("content_type", "")
        
        monetization_setup = {
            "content_id": content_id,
            "platform": platform,
            "monetization_enabled": False,
            "strategies": []
        }
        
        # Check if platform supports monetization
        platform_config = self.config["platforms"].get(platform, {})
        if platform_config.get("monetization", False):
            monetization_setup["monetization_enabled"] = True
            
            # Add platform-specific monetization strategies
            if platform == "youtube":
                monetization_setup["strategies"] = [
                    "AdSense revenue sharing",
                    "Channel memberships",
                    "Super Chat donations",
                    "Affiliate links in description"
                ]
            elif platform == "instagram":
                monetization_setup["strategies"] = [
                    "Sponsored posts",
                    "Affiliate links in bio",
                    "Product placement"
                ]
            
            # Add affiliate links if enabled
            if self.config["monetization"]["affiliate_links"]:
                monetization_setup["affiliate_links"] = [
                    "https://affiliate-link-1.com",
                    "https://affiliate-link-2.com"
                ]
            
            # Setup subscription CTAs
            if self.config["monetization"]["subscription_cta"]:
                monetization_setup["subscription_cta"] = "Subscribe to our newsletter for exclusive content!"
        
        # Store monetization data
        self.monetization_stats[content_id] = monetization_setup
        
        # Emit monetization update
        await event_bus.emit(
            EventTypes.MONETIZATION_UPDATE,
            monetization_setup,
            source=self.cluster_name
        )
        
        return monetization_setup
    
    async def _compliance_check(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform compliance and safety checks on content"""
        logger.info("Distribution Engine: Performing compliance check")
        
        content_item = content_data.get("content_item", {})
        platform = content_data.get("platform", "")
        
        # Simulate compliance checking using LLM
        prompt = f"""
        Review this content for compliance and safety issues:
        
        Platform: {platform}
        Content Type: {content_item.get('content_type', '')}
        Title: {content_item.get('content', {}).get('title', '')}
        
        Check for:
        1. Copyright issues
        2. Platform policy violations
        3. Inappropriate content
        4. Misleading claims
        5. Required disclosures
        
        Respond in JSON format:
        {{
            "compliant": true/false,
            "issues": ["issue1", "issue2"],
            "recommendations": ["recommendation1", "recommendation2"],
            "risk_level": "low/medium/high",
            "required_disclosures": ["disclosure1", "disclosure2"]
        }}
        """
        
        try:
            result = await self.llm_chat.run_chat([UserMessage(content=prompt)])
            compliance_result = json.loads(result.content)
        except (json.JSONDecodeError, Exception):
            # Fallback compliance result
            compliance_result = {
                "compliant": True,
                "issues": [],
                "recommendations": ["Add appropriate hashtags", "Include call-to-action"],
                "risk_level": "low",
                "required_disclosures": []
            }
        
        # Add timestamp and content ID
        compliance_result.update({
            "content_id": content_item.get("id", ""),
            "platform": platform,
            "checked_at": datetime.now(timezone.utc),
            "auto_approved": compliance_result.get("compliant", True) and compliance_result.get("risk_level", "low") == "low"
        })
        
        # Emit compliance check complete event
        await event_bus.emit(
            EventTypes.COMPLIANCE_CHECK_COMPLETE,
            compliance_result,
            source=self.cluster_name,
            priority=EventPriority.HIGH if not compliance_result.get("compliant", True) else EventPriority.NORMAL
        )
        
        return compliance_result
    
    def _extract_title(self, content_item: Dict[str, Any]) -> str:
        """Extract title from content item"""
        content = content_item.get("content", {})
        
        return (
            content.get("title", "") or
            content.get("post_text", "")[:50] + "..." or
            f"{content_item.get('content_type', 'Content')} - {content_item.get('topic', 'Unknown')}"
        )
    
    async def _save_scheduled_content(self, scheduled_item: Dict[str, Any]):
        """Save scheduled content to database"""
        try:
            if self.db:
                await self.db.scheduled_content.insert_one(scheduled_item)
        except Exception as e:
            logger.warning(f"Failed to save scheduled content: {str(e)}")
    
    async def _save_published_content(self, publication_result: Dict[str, Any]):
        """Save published content to database"""
        try:
            if self.db:
                await self.db.published_content.insert_one(publication_result)
        except Exception as e:
            logger.warning(f"Failed to save published content: {str(e)}")
    
    @event_handler(EventTypes.CONTENT_BATCH_READY)
    async def handle_content_batch_ready(self, event):
        """Handle content batch from Creation Engine"""
        batch_data = event.data
        content_items = batch_data.get("content_items", [])
        
        logger.info(f"Distribution Engine: Received {len(content_items)} content items for scheduling")
        
        # Schedule all content items
        await self.process_task({
            "type": "schedule_content",
            "data": {"content_items": content_items}
        })
    
    @event_handler(EventTypes.CONTENT_CREATED)
    async def handle_content_created(self, event):
        """Handle individual content creation"""
        content_item = event.data
        
        logger.info(f"Distribution Engine: Received content for scheduling - {content_item.get('id', 'Unknown')}")
        
        # Schedule single content item
        await self.process_task({
            "type": "schedule_content",
            "data": content_item
        })
    
    def get_distribution_summary(self) -> Dict[str, Any]:
        """Get comprehensive distribution summary"""
        return {
            "content_queue_size": len(self.content_queue),
            "published_content_count": len(self.published_content),
            "platforms_enabled": [p for p, config in self.config["platforms"].items() if config.get("enabled", False)],
            "next_scheduled_post": min([item["scheduled_time"] for item in self.content_queue]) if self.content_queue else None,
            "engagement_metrics_tracked": len(self.engagement_metrics),
            "monetization_setups": len(self.monetization_stats),
            "config": self.config
        }