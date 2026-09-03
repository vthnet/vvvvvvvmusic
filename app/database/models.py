"""MongoDB data models for VTH Music Bot."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class User(BaseModel):
    """User data model."""
    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    is_blocked: bool = False
    is_premium: bool = False
    favorite_count: int = 0
    history_count: int = 0
    
    class Config:
        collection = "users"


class Group(BaseModel):
    """Group data model."""
    group_id: int
    title: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    member_count: int = 0
    is_active: bool = True
    
    class Config:
        collection = "groups"


class Track(BaseModel):
    """Track/Song data model."""
    track_id: str
    title: str
    artist: str
    duration: int
    thumbnail: Optional[str] = None
    url: Optional[str] = None
    webpage_url: Optional[str] = None
    genre: Optional[str] = None
    
    class Config:
        use_enum_values = True


class Favorite(BaseModel):
    """User favorite track."""
    user_id: int
    track_id: str
    title: str
    artist: str
    duration: int
    thumbnail: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        collection = "favorites"


class HistoryEntry(BaseModel):
    """User listening history entry."""
    user_id: int
    track_id: str
    title: str
    artist: str
    duration: int
    thumbnail: Optional[str] = None
    url: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    played_duration: int = 0  # Seconds played
    
    class Config:
        collection = "history"


class GroupSettings(BaseModel):
    """Group settings and preferences."""
    group_id: int
    music_enabled: bool = True
    admin_only_controls: bool = False
    dj_mode: bool = False
    autoplay_enabled: bool = True
    delete_play_commands: bool = True
    leave_when_empty: bool = True
    leave_timeout: int = 300  # seconds
    default_volume: int = 100  # 0-100
    default_loop: str = "off"  # off, one, all
    language: str = "en"
    player_style: str = "compact"
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        collection = "settings"


class DJ(BaseModel):
    """DJ user in a group."""
    group_id: int
    user_id: int
    added_by: int
    added_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        collection = "djs"


class Statistics(BaseModel):
    """Bot statistics snapshot."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_users: int = 0
    total_groups: int = 0
    songs_played: int = 0
    searches_performed: int = 0
    downloads_completed: int = 0
    active_players: int = 0
    total_listening_time: int = 0  # seconds
    
    class Config:
        collection = "statistics"


class BroadcastMessage(BaseModel):
    """Broadcast message to users."""
    message_id: str
    text: str
    photo_url: Optional[str] = None
    buttons: Optional[List[Dict[str, Any]]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending, sent, failed
    total_users: int = 0
    sent_count: int = 0
    failed_count: int = 0
    
    class Config:
        collection = "broadcasts"
