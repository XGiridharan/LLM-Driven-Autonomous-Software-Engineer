"""
Memory management system for the autonomous software engineer
"""
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages context, conversation history, and project memory."""
    
    def __init__(self, project_name: str = "default"):
        """Initialize memory manager for a project."""
        self.project_name = project_name
        self.conversation_history: List[Dict[str, Any]] = []
        self.code_context: Dict[str, Any] = {}
        self.project_state: Dict[str, Any] = {}
        self.learning_memory: Dict[str, Any] = {}
        
        # Advanced memory features
        self.semantic_index: Dict[str, List[str]] = defaultdict(list)
        self.code_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.performance_metrics: Dict[str, Any] = {}
        self.error_patterns: List[Dict[str, Any]] = []
        self.success_patterns: List[Dict[str, Any]] = []
        
        # Create memory directory
        self.memory_dir = Path(f"./memory/{project_name}")
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing memory if available
        self._load_memory()
    
    def add_semantic_context(self, key: str, context: str, tags: List[str] = None):
        """Add semantic context with tags for better retrieval."""
        context_hash = hashlib.md5(context.encode()).hexdigest()
        
        self.semantic_index[key].append({
            "content": context,
            "hash": context_hash,
            "timestamp": datetime.now().isoformat(),
            "tags": tags or []
        })
        
        # Index by tags
        for tag in (tags or []):
            self.semantic_index[f"tag:{tag}"].append(key)
    
    def get_semantic_context(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve semantically relevant context."""
        # Simple keyword-based retrieval (can be enhanced with embeddings)
        query_words = set(query.lower().split())
        scored_contexts = []
        
        for key, contexts in self.semantic_index.items():
            if key.startswith("tag:"):
                continue
                
            for context_item in contexts:
                if isinstance(context_item, dict):
                    content = context_item.get("content", "")
                    content_words = set(content.lower().split())
                    score = len(query_words.intersection(content_words))
                    
                    if score > 0:
                        scored_contexts.append({
                            "key": key,
                            "content": content,
                            "score": score,
                            "timestamp": context_item.get("timestamp"),
                            "tags": context_item.get("tags", [])
                        })
        
        # Sort by score and return top results
        scored_contexts.sort(key=lambda x: x["score"], reverse=True)
        return scored_contexts[:limit]
    
    def track_code_dependency(self, file_path: str, dependencies: List[str]):
        """Track code dependencies for better context management."""
        self.code_dependencies[file_path].update(dependencies)
    
    def get_related_files(self, file_path: str) -> Set[str]:
        """Get files related to the given file through dependencies."""
        related = set()
        
        # Direct dependencies
        related.update(self.code_dependencies.get(file_path, set()))
        
        # Reverse dependencies (files that depend on this one)
        for path, deps in self.code_dependencies.items():
            if file_path in deps:
                related.add(path)
        
        return related
    
    def record_performance_metric(self, operation: str, duration: float, success: bool, metadata: Dict[str, Any] = None):
        """Record performance metrics for learning."""
        if operation not in self.performance_metrics:
            self.performance_metrics[operation] = {
                "total_calls": 0,
                "total_duration": 0.0,
                "success_count": 0,
                "failure_count": 0,
                "avg_duration": 0.0,
                "success_rate": 0.0
            }
        
        metrics = self.performance_metrics[operation]
        metrics["total_calls"] += 1
        metrics["total_duration"] += duration
        
        if success:
            metrics["success_count"] += 1
        else:
            metrics["failure_count"] += 1
        
        metrics["avg_duration"] = metrics["total_duration"] / metrics["total_calls"]
        metrics["success_rate"] = metrics["success_count"] / metrics["total_calls"]
        
        # Store detailed record
        record = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "duration": duration,
            "success": success,
            "metadata": metadata or {}
        }
        
        if success:
            self.success_patterns.append(record)
        else:
            self.error_patterns.append(record)
    
    def get_performance_insights(self, operation: str = None) -> Dict[str, Any]:
        """Get performance insights for optimization."""
        if operation:
            return self.performance_metrics.get(operation, {})
        
        return {
            "overall_metrics": self.performance_metrics,
            "total_operations": len(self.performance_metrics),
            "recent_errors": self.error_patterns[-10:],
            "recent_successes": self.success_patterns[-10:]
        }
    
    def learn_from_patterns(self) -> Dict[str, Any]:
        """Analyze patterns to provide learning insights."""
        insights = {
            "common_errors": {},
            "success_factors": {},
            "recommendations": []
        }
        
        # Analyze error patterns
        error_types = defaultdict(int)
        for error in self.error_patterns:
            error_type = error.get("metadata", {}).get("error_type", "unknown")
            error_types[error_type] += 1
        
        insights["common_errors"] = dict(error_types)
        
        # Analyze success patterns
        success_operations = defaultdict(list)
        for success in self.success_patterns:
            operation = success["operation"]
            duration = success["duration"]
            success_operations[operation].append(duration)
        
        for op, durations in success_operations.items():
            if durations:
                insights["success_factors"][op] = {
                    "avg_duration": sum(durations) / len(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations)
                }
        
        # Generate recommendations
        if error_types:
            most_common_error = max(error_types.items(), key=lambda x: x[1])
            insights["recommendations"].append(
                f"Focus on reducing '{most_common_error[0]}' errors (occurred {most_common_error[1]} times)"
            )
        
        return insights
    
    def add_conversation(
        self, 
        role: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a conversation entry to memory."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        
        self.conversation_history.append(entry)
        logger.debug(f"Added conversation entry: {role}")
    
    def add_code_context(
        self, 
        file_path: str, 
        content: str, 
        language: str = "python"
    ) -> None:
        """Add code context to memory."""
        self.code_context[file_path] = {
            "content": content,
            "language": language,
            "last_updated": datetime.now().isoformat(),
            "checksum": self._calculate_checksum(content)
        }
        logger.debug(f"Added code context for: {file_path}")
    
    def update_project_state(
        self, 
        key: str, 
        value: Any
    ) -> None:
        """Update project state information."""
        self.project_state[key] = {
            "value": value,
            "last_updated": datetime.now().isoformat()
        }
        logger.debug(f"Updated project state: {key}")
    
    def add_learning(
        self, 
        scenario: str, 
        solution: str, 
        success: bool
    ) -> None:
        """Add learning experience to memory."""
        if scenario not in self.learning_memory:
            self.learning_memory[scenario] = []
        
        self.learning_memory[scenario].append({
            "solution": solution,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
        logger.debug(f"Added learning for scenario: {scenario}")
    
    def get_relevant_context(
        self, 
        query: str, 
        max_entries: int = 5
    ) -> str:
        """Get relevant context based on a query."""
        # Simple keyword-based relevance (could be enhanced with embeddings)
        relevant_contexts = []
        
        for file_path, context in self.code_context.items():
            if any(keyword in context["content"].lower() 
                   for keyword in query.lower().split()):
                relevant_contexts.append(f"File: {file_path}\n{context['content']}")
        
        # Add recent conversation history
        recent_conversations = self.conversation_history[-max_entries:]
        if recent_conversations:
            conversation_context = "\n".join([
                f"{entry['role']}: {entry['content']}"
                for entry in recent_conversations
            ])
            relevant_contexts.append(f"Recent conversations:\n{conversation_context}")
        
        return "\n\n".join(relevant_contexts)
    
    def get_project_summary(self) -> Dict[str, Any]:
        """Get a summary of the current project state."""
        return {
            "project_name": self.project_name,
            "total_conversations": len(self.conversation_history),
            "code_files": list(self.code_context.keys()),
            "project_state": self.project_state,
            "learning_experiences": len(self.learning_memory),
            "last_updated": datetime.now().isoformat()
        }
    
    def save_memory(self) -> None:
        """Save memory to disk."""
        try:
            memory_data = {
                "conversation_history": self.conversation_history,
                "code_context": self.code_context,
                "project_state": self.project_state,
                "learning_memory": self.learning_memory
            }
            
            memory_file = self.memory_dir / "memory.json"
            with open(memory_file, 'w') as f:
                json.dump(memory_data, f, indent=2)
            
            logger.info(f"Memory saved to {memory_file}")
            
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
    
    def _load_memory(self) -> None:
        """Load memory from disk if available."""
        try:
            memory_file = self.memory_dir / "memory.json"
            if memory_file.exists():
                with open(memory_file, 'r') as f:
                    memory_data = json.load(f)
                
                self.conversation_history = memory_data.get("conversation_history", [])
                self.code_context = memory_data.get("code_context", {})
                self.project_state = memory_data.get("project_state", {})
                self.learning_memory = memory_data.get("learning_memory", {})
                
                logger.info(f"Memory loaded from {memory_file}")
                
        except Exception as e:
            logger.error(f"Failed to load memory: {e}")
    
    def _calculate_checksum(self, content: str) -> str:
        """Calculate a simple checksum for content."""
        return str(hash(content))[-8:]
    
    def clear_memory(self) -> None:
        """Clear all memory (use with caution)."""
        self.conversation_history.clear()
        self.code_context.clear()
        self.project_state.clear()
        self.learning_memory.clear()
        logger.warning("Memory cleared")
    
    def __del__(self):
        """Save memory when object is destroyed."""
        try:
            self.save_memory()
        except:
            pass
