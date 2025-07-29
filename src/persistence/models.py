from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from dataclasses import dataclass

Base = declarative_base()

class FeedModel(Base):
    __tablename__ = "feeds"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    url = Column(String(500))
    description = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    articles = relationship("ArticleModel", back_populates="feed")

class ArticleModel(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, index=True)
    content = Column(Text)
    summary = Column(Text)
    published_date = Column(DateTime)
    source = Column(String(500))
    feed_id = Column(Integer, ForeignKey("feeds.id"))
    
    # Status fields
    read_status = Column(Boolean, default=False)
    starred = Column(Boolean, default=False)
    tags = Column(JSON, default=list)
    
    # ML/Analysis fields
    topic_scores = Column(JSON, default=dict)  # {topic: score}
    relevance_score = Column(Float, default=0.0)
    surprise_factor = Column(Float, default=0.0)
    processed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    feed = relationship("FeedModel", back_populates="articles")

class UserPreferenceModel(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    preference_type = Column(String(100), nullable=False)  # topic_weight, source_preference, etc.
    key = Column(String(200), nullable=False)  # topic name, source name, etc.
    value = Column(Float, nullable=False)  # weight/score value
    additional_data = Column(JSON, default=dict)  # additional data
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TrainingDataModel(Base):
    __tablename__ = "training_data"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    feedback_type = Column(String(50), nullable=False)  # like, dislike, relevant, irrelevant
    feedback_value = Column(Float, nullable=False)  # numeric feedback score
    context = Column(JSON, default=dict)  # context when feedback was given
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    article = relationship("ArticleModel")

class NewsletterModel(Base):
    __tablename__ = "newsletters"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # Generated newsletter content
    article_ids = Column(JSON, default=list)  # IDs of articles included
    surprise_article_ids = Column(JSON, default=list)  # IDs of surprise articles
    
    # Generation settings
    generation_settings = Column(JSON, default=dict)
    
    # Output files
    markdown_file = Column(String(500))  # Path to generated markdown file
    obsidian_file = Column(String(500))  # Path to Obsidian-compatible file
    
    created_at = Column(DateTime, default=datetime.utcnow)

# Data classes for API/transfer
@dataclass
class ArticleCreate:
    title: str
    url: str
    content: str = ""
    summary: str = ""
    published_date: Optional[datetime] = None
    source: str = ""
    feed_id: int = 0
    read_status: bool = False
    starred: bool = False
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass 
class FeedCreate:
    name: str
    url: str = ""
    description: str = ""
    active: bool = True

@dataclass
class UserFeedback:
    article_id: int
    feedback_type: str  # like, dislike, relevant, irrelevant
    feedback_value: float
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

@dataclass
class TopicScore:
    topic: str
    score: float
    confidence: float = 0.0
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []