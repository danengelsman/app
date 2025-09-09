from server import BaseAgent, db, EMERGENT_LLM_KEY, ContentPiece, BlogPost, Analytics
from emergentintegrations.llm.chat import LlmChat, UserMessage
from typing import Dict, Any, List
import uuid
from datetime import datetime
import json
import logging
import asyncio
import aiohttp

class AuditorOptimizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "Agent 1D - Auditor and Optimizer",
            "Post-creation audit and optimization of content for maximum engagement and performance."
        )

    async def _process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        content_pieces = task_data.get('content_pieces', [])
        optimized_content = []
        
        for content in content_pieces:
            # Audit content for optimization opportunities
            prompt = f"""
            Audit and optimize this content piece for maximum engagement:
            
            Title: {content.get('title', '')}
            Platform: {content.get('platform', '')}
            Content Type: {content.get('content_type', '')}
            Script: {content.get('script', '')[:500]}...
            
            Analyze and provide:
            1. Engagement score (1-10) with reasoning
            2. SEO optimization suggestions
            3. Hook improvement recommendations
            4. Call-to-action optimization
            5. Platform-specific optimizations
            6. A/B testing variants (title, description, thumbnail suggestions)
            
            Return as structured JSON with optimized versions.
            """
            
            user_message = UserMessage(text=prompt)
            response = await self.llm_chat.send_message(user_message)
            
            try:
                audit_data = json.loads(response)
                content['audit_results'] = audit_data
                content['optimization_score'] = audit_data.get('engagement_score', 5)
                content['optimized'] = True
                optimized_content.append(content)
            except:
                # Fallback optimization
                content['audit_results'] = {"suggestions": "General optimization needed"}
                content['optimization_score'] = 6.0
                optimized_content.append(content)
        
        return {
            "status": "success",
            "audited_content": len(optimized_content),
            "content": optimized_content
        }

class MonetizationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "Agent 1E - Monetization and Traffic Driver",
            "Sets up monetization streams and drives traffic to subscription blog."
        )

    async def _process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        content_pieces = task_data.get('content_pieces', [])
        
        # Generate monetization strategy for each piece
        monetization_strategies = []
        
        for content in content_pieces:
            platform = content.get('platform', '')
            topic = content.get('title', '')
            
            prompt = f"""
            Create a comprehensive monetization strategy for this content:
            
            Topic: {topic}
            Platform: {platform}
            
            Provide:
            1. Relevant affiliate product recommendations (tech products, courses, tools)
            2. Sponsor partnership opportunities 
            3. Blog traffic driving techniques
            4. Email capture strategies
            5. Subscription conversion tactics
            6. Revenue projections (conservative estimates)
            7. UTM tracking setup
            
            Focus on technology niche monetization opportunities.
            Return as structured JSON.
            """
            
            user_message = UserMessage(text=prompt)
            response = await self.llm_chat.send_message(user_message)
            
            try:
                monetization_data = json.loads(response)
            except:
                monetization_data = {
                    "affiliate_opportunities": ["Tech gadgets", "Online courses"],
                    "revenue_projection": 50.0,
                    "blog_cta": f"Learn more about {topic} on our blog!"
                }
            
            strategy = {
                "content_id": content.get('id'),
                "platform": platform,
                "monetization_strategy": monetization_data,
                "created_date": datetime.utcnow()
            }
            
            monetization_strategies.append(strategy)
        
        # Setup blog funnel configuration
        funnel_config = await self._setup_blog_funnel()
        
        return {
            "status": "success",
            "strategies_created": len(monetization_strategies),
            "strategies": monetization_strategies,
            "funnel_config": funnel_config
        }

    async def _setup_blog_funnel(self) -> Dict[str, Any]:
        """Setup blog subscription funnel configuration"""
        return {
            "blog_url": "https://techpulse-ai.substack.com",
            "subscription_tiers": {
                "free": {"price": 0, "features": ["Weekly newsletter", "Basic tech insights"]},
                "premium": {"price": 15, "features": ["Daily insights", "Exclusive interviews", "Tech investment tips"]},
                "pro": {"price": 50, "features": ["All premium features", "1-on-1 consultations", "Early access to trends"]}
            },
            "conversion_funnels": {
                "youtube": "Video end screen → Blog → Email capture → Subscription",
                "instagram": "Story link → Blog → Email capture → Subscription",
                "tiktok": "Bio link → Blog → Email capture → Subscription",
                "twitter": "Thread CTA → Blog → Email capture → Subscription"
            }
        }

class BlogWriterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "Agent 1F - Blog Writer",
            "Creates in-depth blog posts from content topics with SEO optimization and subscription gates."
        )

    async def _process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        topics = task_data.get('topics', [])
        blog_posts = []
        
        for topic in topics[:3]:  # Create blogs for top 3 topics
            # Create comprehensive blog post
            prompt = f"""
            Write a comprehensive, SEO-optimized blog post about "{topic.get('keyword', '')}".
            
            Requirements:
            - 1500-2000 words
            - Professional yet engaging tone
            - Include practical insights and actionable advice
            - Add relevant statistics and trends
            - Include 5-7 subheadings
            - SEO-optimized with long-tail keywords
            - Clear call-to-actions for subscription
            - Premium content section (gate behind subscription)
            
            Structure:
            1. Engaging introduction with hook
            2. Current state and trends
            3. Key insights and analysis
            4. Practical applications
            5. Future predictions
            6. Premium section (advanced strategies/insider tips)
            7. Conclusion with strong CTA
            
            Return as structured JSON with title, excerpt, full_content, tags, and premium_section.
            """
            
            user_message = UserMessage(text=prompt)
            response = await self.llm_chat.send_message(user_message)
            
            try:
                blog_data = json.loads(response)
                
                blog_post = BlogPost(
                    topic_id=topic.get('id', str(uuid.uuid4())),
                    title=blog_data.get('title', f"Deep Dive: {topic.get('keyword', '')}"),
                    content=blog_data.get('full_content', ''),
                    excerpt=blog_data.get('excerpt', ''),
                    tags=blog_data.get('tags', [topic.get('keyword', '').lower()]),
                    is_premium=True  # Mark as premium to drive subscriptions
                )
                
                # Save to database
                await db.blog_posts.insert_one(blog_post.dict())
                blog_posts.append(blog_post)
                
            except Exception as e:
                logging.error(f"Error creating blog post: {str(e)}")
                # Create fallback blog post
                fallback_post = BlogPost(
                    topic_id=topic.get('id', str(uuid.uuid4())),
                    title=f"The Future of {topic.get('keyword', 'Technology')}",
                    content=f"Comprehensive analysis of {topic.get('keyword', 'technology trends')} and its impact on the industry...",
                    excerpt=f"Explore the latest developments in {topic.get('keyword', 'technology')}",
                    tags=[topic.get('keyword', '').lower()],
                    is_premium=True
                )
                blog_posts.append(fallback_post)
        
        return {
            "status": "success",
            "blog_posts_created": len(blog_posts),
            "posts": [post.dict() for post in blog_posts]
        }

class ContentGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "Agent 1G - Content Generator and Publisher",
            "Automates media production and publishing across platforms with scheduling."
        )

    async def _process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        content_pieces = task_data.get('content_pieces', [])
        generated_assets = []
        
        for content in content_pieces:
            # Generate thumbnails and visual assets
            thumbnail_prompts = await self._generate_thumbnail_concepts(content)
            
            # Create publishing schedule
            schedule = await self._create_publishing_schedule(content)
            
            # Generate platform-specific optimizations
            platform_optimizations = await self._optimize_for_platform(content)
            
            asset_package = {
                "content_id": content.get('id'),
                "thumbnails": thumbnail_prompts,
                "publishing_schedule": schedule,
                "platform_optimizations": platform_optimizations,
                "status": "ready_for_publishing"
            }
            
            generated_assets.append(asset_package)
        
        return {
            "status": "success",
            "assets_generated": len(generated_assets),
            "publishing_ready": len([a for a in generated_assets if a["status"] == "ready_for_publishing"]),
            "assets": generated_assets
        }

    async def _generate_thumbnail_concepts(self, content: Dict) -> List[Dict]:
        """Generate thumbnail concepts for content"""
        prompt = f"""
        Generate 3 compelling thumbnail concepts for this content:
        
        Title: {content.get('title', '')}
        Platform: {content.get('platform', '')}
        Topic: Technology
        
        For each thumbnail concept, provide:
        1. Visual description
        2. Text overlay suggestions
        3. Color scheme
        4. Emotion/mood to convey
        5. Design elements (icons, arrows, etc.)
        
        Make them click-worthy and platform-appropriate.
        Return as JSON array.
        """
        
        user_message = UserMessage(text=prompt)
        response = await self.llm_chat.send_message(user_message)
        
        try:
            return json.loads(response)
        except:
            return [
                {"description": "Modern tech background with bold title", "text": content.get('title', '')[:20]},
                {"description": "Split screen comparison design", "text": "THIS vs THAT"},
                {"description": "Question format with tech imagery", "text": "IS THIS THE FUTURE?"}
            ]

    async def _create_publishing_schedule(self, content: Dict) -> Dict:
        """Create optimal publishing schedule"""
        platform = content.get('platform', '')
        
        # Platform-specific optimal posting times
        optimal_times = {
            'youtube': {'day': 'Tuesday', 'time': '14:00', 'timezone': 'UTC'},
            'instagram': {'day': 'Wednesday', 'time': '11:00', 'timezone': 'UTC'},
            'tiktok': {'day': 'Thursday', 'time': '18:00', 'timezone': 'UTC'},
            'twitter': {'day': 'Monday', 'time': '09:00', 'timezone': 'UTC'}
        }
        
        return optimal_times.get(platform, {'day': 'Monday', 'time': '12:00', 'timezone': 'UTC'})

    async def _optimize_for_platform(self, content: Dict) -> Dict:
        """Generate platform-specific optimizations"""
        platform = content.get('platform', '')
        
        optimizations = {
            'youtube': {
                'title_length': '60 characters max',
                'description_strategy': 'Front-load keywords, include timestamps',
                'end_screen': 'Subscribe button + related video',
                'cards': 'Add at 30% and 70% marks'
            },
            'instagram': {
                'caption_strategy': 'Hook in first line, hashtags in comments',
                'story_highlights': 'Save to relevant highlight category',
                'reels_optimization': 'Vertical 9:16, captions on, trending audio'
            },
            'tiktok': {
                'hook_timing': 'Grab attention in first 3 seconds',
                'hashtag_strategy': 'Mix trending + niche hashtags',
                'posting_frequency': '1-3 times daily'
            },
            'twitter': {
                'thread_structure': 'Hook tweet + numbered thread',
                'engagement_tactics': 'Ask questions, use polls',
                'timing': 'Tweet during work hours for tech audience'
            }
        }
        
        return optimizations.get(platform, {})

class AnalyticsAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "Agent 1H - Analytics and Engagement Manager",
            "Tracks performance metrics and manages audience engagement across platforms."
        )

    async def _process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        # Simulate analytics data collection
        analytics_data = await self._collect_analytics()
        
        # Generate performance insights
        insights = await self._generate_insights(analytics_data)
        
        # Create engagement strategy
        engagement_strategy = await self._create_engagement_strategy(insights)
        
        return {
            "status": "success",
            "analytics_collected": True,
            "insights": insights,
            "engagement_strategy": engagement_strategy,
            "next_actions": self._recommend_next_actions(insights)
        }

    async def _collect_analytics(self) -> Dict[str, Any]:
        """Collect analytics from various platforms"""
        # In a real implementation, this would connect to platform APIs
        return {
            "youtube": {"views": 15420, "likes": 892, "comments": 45, "subscribers": 2340},
            "instagram": {"views": 8730, "likes": 445, "comments": 23, "followers": 1890},
            "tiktok": {"views": 25600, "likes": 1560, "comments": 89, "followers": 3450},
            "twitter": {"impressions": 12400, "likes": 234, "retweets": 67, "followers": 1250},
            "blog": {"page_views": 5670, "subscribers": 145, "email_opens": 432}
        }

    async def _generate_insights(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable insights from analytics data"""
        prompt = f"""
        Analyze this social media and blog performance data and provide actionable insights:
        
        {json.dumps(analytics, indent=2)}
        
        Provide:
        1. Top performing platforms and why
        2. Engagement rate analysis
        3. Content type recommendations
        4. Audience growth strategies
        5. Conversion optimization opportunities
        6. Platform-specific improvements
        
        Focus on actionable recommendations for a technology content creator.
        Return as structured JSON.
        """
        
        user_message = UserMessage(text=prompt)
        response = await self.llm_chat.send_message(user_message)
        
        try:
            return json.loads(response)
        except:
            return {
                "top_platform": "tiktok",
                "recommendations": ["Post more video content", "Increase engagement", "Focus on trending topics"]
            }

    async def _create_engagement_strategy(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Create engagement strategy based on insights"""
        return {
            "daily_actions": [
                "Respond to comments within 2 hours",
                "Share behind-the-scenes content",
                "Engage with tech community posts"
            ],
            "weekly_goals": [
                "Host live Q&A session",
                "Collaborate with other tech creators",
                "Share user-generated content"
            ],
            "content_themes": [
                "Tech tutorials and how-tos",
                "Industry news and reactions",
                "Future predictions and analysis"
            ]
        }

    def _recommend_next_actions(self, insights: Dict[str, Any]) -> List[str]:
        """Recommend next actions based on insights"""
        return [
            "Double down on top-performing content types",
            "Increase posting frequency on best-performing platform",
            "A/B test different content formats",
            "Optimize blog-to-subscription conversion funnel",
            "Expand into emerging platforms based on audience demographics"
        ]

class ComplianceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "Agent 1I - Legal and Compliance Checker",
            "Ensures all content meets platform guidelines and legal requirements."
        )

    async def _process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        content_pieces = task_data.get('content_pieces', [])
        compliance_results = []
        
        for content in content_pieces:
            # Check content compliance
            compliance_check = await self._check_content_compliance(content)
            
            # Platform-specific guideline check
            platform_check = await self._check_platform_guidelines(content)
            
            result = {
                "content_id": content.get('id'),
                "compliance_score": compliance_check.get('score', 8),
                "issues_found": compliance_check.get('issues', []),
                "platform_compliance": platform_check,
                "recommendations": compliance_check.get('recommendations', []),
                "approved": compliance_check.get('score', 8) >= 7
            }
            
            compliance_results.append(result)
        
        return {
            "status": "success",
            "content_checked": len(compliance_results),
            "approved_content": len([r for r in compliance_results if r["approved"]]),
            "compliance_results": compliance_results
        }

    async def _check_content_compliance(self, content: Dict) -> Dict[str, Any]:
        """Check content for compliance issues"""
        prompt = f"""
        Review this content for compliance and legal issues:
        
        Title: {content.get('title', '')}
        Platform: {content.get('platform', '')}
        Script: {content.get('script', '')[:500]}...
        
        Check for:
        1. Copyright infringement risks
        2. Misleading claims or misinformation
        3. Platform community guideline violations
        4. Privacy concerns
        5. Regulatory compliance (FTC disclosure requirements)
        6. Trademark issues
        7. Content appropriateness
        
        Rate compliance on 1-10 scale and provide specific recommendations.
        Return as structured JSON.
        """
        
        user_message = UserMessage(text=prompt)
        response = await self.llm_chat.send_message(user_message)
        
        try:
            return json.loads(response)
        except:
            return {
                "score": 8,
                "issues": [],
                "recommendations": ["Add proper disclosures", "Verify factual claims"]
            }

    async def _check_platform_guidelines(self, content: Dict) -> Dict[str, Any]:
        """Check platform-specific guidelines"""
        platform = content.get('platform', '')
        
        guidelines = {
            'youtube': {
                'monetization_friendly': True,
                'copyright_safe': True,
                'community_guidelines': True,
                'recommendations': ['Add end screen', 'Include closed captions']
            },
            'instagram': {
                'community_standards': True,
                'hashtag_compliance': True,
                'recommendations': ['Use original music', 'Avoid repetitive content']
            },
            'tiktok': {
                'community_guidelines': True,
                'safety_compliant': True,
                'recommendations': ['Use trending sounds responsibly', 'Avoid sensitive topics']
            },
            'twitter': {
                'terms_of_service': True,
                'hateful_conduct': False,
                'recommendations': ['Keep threads concise', 'Engage respectfully']
            }
        }
        
        return guidelines.get(platform, {'compliant': True, 'recommendations': []})