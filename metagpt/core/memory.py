#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Meta Agent Persistent Memory Module

@Time    : 2026/02/15
@Author  : Meta Agent (Orchestrator Prime)
@File    : memory.py
@Mission : Provide persistent memory for the Meta Agent across sessions
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Any
import hashlib


class MemoryType(str):
    """Types of memories stored."""
    
    EPISODIC = "episodic"      # Events and experiences
    SEMANTIC = "semantic"      # Facts and knowledge
    PROCEDURAL = "procedural"  # Skills and procedures
    WORKING = "working"        # Current task context
    MISSION = "mission"        # Mission-critical information


@dataclass
class MemoryEntry:
    """A single memory entry."""
    
    id: str
    content: str
    memory_type: str
    timestamp: str
    importance: float = 0.5  # 0.0 to 1.0
    access_count: int = 0
    last_accessed: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type,
            "timestamp": self.timestamp,
            "importance": self.importance,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "MemoryEntry":
        """Deserialize from dictionary."""
        return cls(**data)


class PersistentMemory:
    """
    Persistent memory system for the Meta Agent.
    
    This module provides long-term storage for the Meta Agent's memories,
    including mission context, learned patterns, and important experiences.
    Memory is persisted to disk and loaded on startup.
    
    Features:
    - Episodic memory: Events and experiences
    - Semantic memory: Facts and knowledge
    - Procedural memory: Skills and procedures
    - Working memory: Current task context
    - Mission memory: Mission-critical information
    
    Attributes:
        storage_path: Path to the memory storage file
        memories: Dictionary of all memories by ID
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the persistent memory.
        
        Args:
            storage_path: Path to store memory file. Defaults to 'memory/meta-agent-memory.json'
        """
        if storage_path is None:
            # Default to memory directory in project root
            memory_dir = Path(__file__).parent.parent.parent / "memory"
            memory_dir.mkdir(parents=True, exist_ok=True)
            storage_path = str(memory_dir / "meta-agent-memory.json")
        
        self.storage_path = storage_path
        self.memories: dict[str, MemoryEntry] = {}
        self._working_memory: dict[str, Any] = {}
        
        # Load existing memories
        self._load()
    
    def _generate_id(self, content: str, memory_type: str) -> str:
        """Generate a unique ID for a memory entry."""
        hash_input = f"{content}:{memory_type}:{datetime.utcnow().isoformat()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]
    
    def _load(self) -> None:
        """Load memories from disk."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for entry_data in data.get("memories", []):
                        entry = MemoryEntry.from_dict(entry_data)
                        self.memories[entry.id] = entry
            except (json.JSONDecodeError, KeyError) as e:
                # If file is corrupted, start fresh
                self.memories = {}
    
    def _save(self) -> None:
        """Save memories to disk."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        data = {
            "version": "1.0",
            "last_updated": datetime.utcnow().isoformat(),
            "memories": [m.to_dict() for m in self.memories.values()],
        }
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def store(self, content: str, memory_type: str = MemoryType.EPISODIC,
              importance: float = 0.5, metadata: Optional[dict] = None) -> str:
        """
        Store a new memory.
        
        Args:
            content: The memory content
            memory_type: Type of memory (episodic, semantic, procedural, working, mission)
            importance: Importance score (0.0 to 1.0)
            metadata: Additional metadata
            
        Returns:
            The ID of the stored memory
        """
        memory_id = self._generate_id(content, memory_type)
        
        entry = MemoryEntry(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            timestamp=datetime.utcnow().isoformat(),
            importance=max(0.0, min(1.0, importance)),
            metadata=metadata or {},
        )
        
        self.memories[memory_id] = entry
        self._save()
        
        return memory_id
    
    def recall(self, memory_id: str) -> Optional[MemoryEntry]:
        """
        Recall a specific memory by ID.
        
        Args:
            memory_id: The ID of the memory to recall
            
        Returns:
            The memory entry, or None if not found
        """
        entry = self.memories.get(memory_id)
        if entry:
            entry.access_count += 1
            entry.last_accessed = datetime.utcnow().isoformat()
            self._save()
        return entry
    
    def search(self, query: str, memory_type: Optional[str] = None,
               limit: int = 10) -> list[MemoryEntry]:
        """
        Search memories by content.
        
        Args:
            query: Search query
            memory_type: Filter by memory type (optional)
            limit: Maximum number of results
            
        Returns:
            List of matching memories, sorted by relevance
        """
        query_lower = query.lower()
        results = []
        
        for entry in self.memories.values():
            if memory_type and entry.memory_type != memory_type:
                continue
            
            if query_lower in entry.content.lower():
                results.append(entry)
        
        # Sort by importance and access count
        results.sort(key=lambda e: (e.importance, e.access_count), reverse=True)
        
        return results[:limit]
    
    def get_by_type(self, memory_type: str) -> list[MemoryEntry]:
        """Get all memories of a specific type."""
        return [e for e in self.memories.values() if e.memory_type == memory_type]
    
    def get_mission_memories(self) -> list[MemoryEntry]:
        """Get all mission-critical memories."""
        return self.get_by_type(MemoryType.MISSION)
    
    def get_recent(self, limit: int = 10) -> list[MemoryEntry]:
        """Get most recent memories."""
        sorted_memories = sorted(
            self.memories.values(),
            key=lambda e: e.timestamp,
            reverse=True
        )
        return sorted_memories[:limit]
    
    def forget(self, memory_id: str) -> bool:
        """
        Remove a memory.
        
        Args:
            memory_id: The ID of the memory to forget
            
        Returns:
            True if memory was removed, False if not found
        """
        if memory_id in self.memories:
            del self.memories[memory_id]
            self._save()
            return True
        return False
    
    def consolidate(self) -> int:
        """
        Consolidate memories by removing low-importance, unused entries.
        
        Returns:
            Number of memories removed
        """
        to_remove = []
        
        for memory_id, entry in self.memories.items():
            # Remove low importance memories that haven't been accessed
            if entry.importance < 0.3 and entry.access_count == 0:
                to_remove.append(memory_id)
            # Remove very old working memories
            elif entry.memory_type == MemoryType.WORKING:
                # Working memories expire after 24 hours conceptually
                # In practice, we keep them but mark for review
                pass
        
        for memory_id in to_remove:
            del self.memories[memory_id]
        
        if to_remove:
            self._save()
        
        return len(to_remove)
    
    def set_working(self, key: str, value: Any) -> None:
        """Set a value in working memory."""
        self._working_memory[key] = {
            "value": value,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def get_working(self, key: str) -> Optional[Any]:
        """Get a value from working memory."""
        entry = self._working_memory.get(key)
        return entry["value"] if entry else None
    
    def clear_working(self) -> None:
        """Clear all working memory."""
        self._working_memory.clear()
    
    def export_state(self) -> dict:
        """Export the full memory state."""
        return {
            "memories": [m.to_dict() for m in self.memories.values()],
            "working_memory": self._working_memory.copy(),
        }
    
    def import_state(self, state: dict) -> None:
        """Import a memory state."""
        for entry_data in state.get("memories", []):
            entry = MemoryEntry.from_dict(entry_data)
            self.memories[entry.id] = entry
        
        self._working_memory = state.get("working_memory", {})
        self._save()
    
    def get_stats(self) -> dict:
        """Get memory statistics."""
        type_counts = {}
        for entry in self.memories.values():
            type_counts[entry.memory_type] = type_counts.get(entry.memory_type, 0) + 1
        
        return {
            "total_memories": len(self.memories),
            "by_type": type_counts,
            "working_memory_items": len(self._working_memory),
            "storage_path": self.storage_path,
        }


# Singleton instance
_memory_instance: Optional[PersistentMemory] = None


def get_memory() -> PersistentMemory:
    """Get the singleton PersistentMemory instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = PersistentMemory()
    return _memory_instance


def remember(content: str, memory_type: str = MemoryType.EPISODIC,
             importance: float = 0.5, metadata: Optional[dict] = None) -> str:
    """
    Convenience function to store a memory.
    
    Args:
        content: The memory content
        memory_type: Type of memory
        importance: Importance score (0.0 to 1.0)
        metadata: Additional metadata
        
    Returns:
        The ID of the stored memory
    """
    return get_memory().store(content, memory_type, importance, metadata)


def recall_memory(query: str, memory_type: Optional[str] = None,
                  limit: int = 10) -> list[MemoryEntry]:
    """
    Convenience function to search memories.
    
    Args:
        query: Search query
        memory_type: Filter by memory type (optional)
        limit: Maximum number of results
        
    Returns:
        List of matching memories
    """
    return get_memory().search(query, memory_type, limit)


# Export
__all__ = [
    "PersistentMemory",
    "MemoryEntry",
    "MemoryType",
    "get_memory",
    "remember",
    "recall_memory",
]
