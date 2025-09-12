import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
import uuid

# Mock data for testing navigation
mock_topics = [
    {
        "id": str(uuid.uuid4()),
        "keyword": "AI coding assistants",
        "search_volume": 75000,
        "competition_level": "medium",
        "trend_score": 8.5,
        "platforms": ["youtube", "instagram", "tiktok"],
        "discovered_date": datetime.utcnow(),
        "niche": "technology",
        "metadata": {"monetization_potential": "High potential for affiliate marketing"}
    },
    {
        "id": str(uuid.uuid4()),
        "keyword": "Cybersecurity threats 2025",
        "search_volume": 60000,
        "competition_level": "high",
        "trend_score": 7.8,
        "platforms": ["youtube", "twitter", "substack"],
        "discovered_date": datetime.utcnow(),
        "niche": "technology",
        "metadata": {"monetization_potential": "Premium content opportunity"}
    },
    {
        "id": str(uuid.uuid4()),
        "keyword": "Apple Vision Pro review",
        "search_volume": 90000,
        "competition_level": "high",
        "trend_score": 9.2,
        "platforms": ["youtube", "instagram", "tiktok"],
        "discovered_date": datetime.utcnow(),
        "niche": "technology",
        "metadata": {"monetization_potential": "High engagement potential"}
    }
]

mock_content = [
    {
        "id": str(uuid.uuid4()),
        "topic_id": mock_topics[0]["id"],
        "title": "How AI Coding Assistants Are Changing Programming Forever",
        "description": "Explore the revolutionary impact of AI coding assistants like GitHub Copilot, ChatGPT, and Claude on modern software development. Learn how these tools are transforming the way developers write, debug, and optimize code.",
        "content_type": "video_long",
        "platform": "youtube",
        "script": """
        Hook: "What if I told you that AI can now write 80% of your code for you?"
        
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
        If you found this valuable, subscribe for more AI and tech insights. And don't forget to check out our premium newsletter for exclusive industry analysis and investment opportunities in the AI space.
        """,
        "thumbnails": [
            "Split screen: Human programmer vs AI assistant coding",
            "Before/After: Traditional coding vs AI-assisted coding",
            "Futuristic coding setup with AI hologram"
        ],
        "hashtags": ["AI", "coding", "programming", "github", "copilot", "chatgpt", "developer", "tech", "software", "automation"],
        "status": "draft",
        "created_date": datetime.utcnow(),
        "engagement_metrics": {"estimated_views": 15000, "estimated_engagement": 8.5}
    },
    {
        "id": str(uuid.uuid4()),
        "topic_id": mock_topics[1]["id"],
        "title": "5 Cybersecurity Threats That Will Dominate 2025",
        "description": "Stay ahead of cybercriminals with our comprehensive analysis of the top cybersecurity threats emerging in 2025. From AI-powered attacks to quantum computing vulnerabilities.",
        "content_type": "video_short",
        "platform": "instagram",
        "script": """
        Hook: "These 5 cyber threats could destroy your business in 2025"
        
        1. AI-Powered Social Engineering
        - Deepfake voice calls
        - Personalized phishing attacks
        - AI-generated fake identities
        
        2. Quantum Computing Attacks
        - Breaking current encryption
        - Timeline: 5-10 years away
        - Preparation needed NOW
        
        3. Supply Chain Compromises
        - Third-party software risks
        - Hardware backdoors
        - Cloud service vulnerabilities
        
        4. IoT Botnet Explosions
        - Smart home device takeovers
        - Industrial IoT attacks
        - 5G network exploitation
        
        5. Ransomware-as-a-Service Evolution
        - Lower barrier to entry
        - Targeted industry attacks
        - Double and triple extortion
        
        Protection Strategy:
        - Zero-trust architecture
        - Regular security audits
        - Employee training programs
        - Incident response planning
        
        CTA: Follow for daily cybersecurity insights and check our blog for detailed protection guides!
        """,
        "thumbnails": [
            "Dark hacker silhouette with 2025 neon text",
            "Shield vs various cyber threat icons",
            "Warning alert with cybersecurity elements"
        ],
        "hashtags": ["cybersecurity", "hacking", "2025", "threats", "protection", "business", "tech", "security", "privacy", "data"],
        "status": "draft",
        "created_date": datetime.utcnow(),
        "engagement_metrics": {"estimated_views": 8500, "estimated_engagement": 9.2}
    },
    {
        "id": str(uuid.uuid4()),
        "topic_id": mock_topics[2]["id"],
        "title": "Apple Vision Pro: 6 Months Later - Honest Review",
        "description": "After 6 months of daily use, here's my brutally honest review of the Apple Vision Pro. The good, the bad, and whether it's worth $3,500 in 2025.",
        "content_type": "thread",
        "platform": "twitter",
        "script": """
        🧵 THREAD: Apple Vision Pro - 6 months later, here's my honest take (1/12)
        
        2/ First, the WOW moments:
        - Spatial computing feels like magic
        - The display quality is unmatched
        - Hand tracking works 95% of the time
        - Immersive environments are incredible
        
        3/ But the reality check hits hard:
        - 2-hour battery life kills productivity
        - Weight causes neck strain after 1 hour
        - Limited app ecosystem
        - $3,500 price point is brutal
        
        4/ Productivity use cases that actually work:
        ✅ Virtual monitors (game changer)
        ✅ 3D design and modeling
        ✅ Immersive presentations
        ❌ Long coding sessions
        ❌ Video editing (too heavy)
        
        5/ Entertainment is where it shines:
        - Movies feel like private IMAX
        - Spatial photos/videos are emotional
        - Gaming potential is huge (but limited titles)
        
        6/ The ecosystem problem:
        - Most apps are iPad ports
        - Native spatial apps are rare
        - Developers waiting for adoption
        - Classic chicken-and-egg scenario
        
        7/ Who should buy it in 2025:
        ✅ Early adopters with disposable income
        ✅ 3D designers and architects
        ✅ Content creators (for the novelty)
        ❌ General consumers
        ❌ Budget-conscious buyers
        
        8/ Compared to Meta Quest 3:
        Vision Pro: Premium experience, limited content
        Quest 3: Broader ecosystem, lower quality
        Different markets entirely
        
        9/ The future potential:
        - Vision Pro 2 will fix weight/battery
        - Ecosystem will mature
        - Price will drop (eventually)
        - This is iPhone 1 moment
        
        10/ My verdict after 6 months:
        It's the best worst product Apple has made
        - Incredible technology
        - Poor execution on basics
        - Too early for mainstream
        
        11/ Should you buy it?
        If you have $3,500 to experiment: Maybe
        If you need practical value: Wait for Gen 2
        If you're curious: Try it at Apple Store first
        
        12/ What's your take on Vision Pro? Are you waiting for improvements or diving in now?
        
        For more detailed tech reviews and analysis, check out our newsletter: [link]
        """,
        "hashtags": ["AppleVisionPro", "VR", "AR", "Apple", "tech", "review", "spatialcomputing", "mixed reality", "innovation", "future"],
        "status": "draft",
        "created_date": datetime.utcnow(),
        "engagement_metrics": {"estimated_views": 25000, "estimated_engagement": 7.8}
    }
]

async def populate_test_data():
    """Populate MongoDB with test data for navigation testing"""
    try:
        # Connect to MongoDB
        mongo_url = "mongodb://localhost:27017"
        client = AsyncIOMotorClient(mongo_url)
        db = client["test_database"]
        
        print("🔍 Populating test data for navigation testing...")
        
        # Clear existing data
        await db.trending_topics.delete_many({})
        await db.content_pieces.delete_many({})
        print("✅ Cleared existing data")
        
        # Insert mock topics
        await db.trending_topics.insert_many(mock_topics)
        print(f"✅ Inserted {len(mock_topics)} trending topics")
        
        # Insert mock content
        await db.content_pieces.insert_many(mock_content)
        print(f"✅ Inserted {len(mock_content)} content pieces")
        
        # Verify data
        topics_count = await db.trending_topics.count_documents({})
        content_count = await db.content_pieces.count_documents({})
        
        print(f"📊 Database populated:")
        print(f"   - Topics: {topics_count}")
        print(f"   - Content: {content_count}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error populating test data: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(populate_test_data())