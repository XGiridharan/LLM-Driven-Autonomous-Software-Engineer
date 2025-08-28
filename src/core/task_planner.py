"""
Task planning and breakdown system for the autonomous software engineer
"""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class TaskPriority(Enum):
    """Priority of a task."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Task:
    """Represents a single task."""
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    dependencies: List[str]
    task_type: str = "generic"  # Added missing task_type attribute
    estimated_time: Optional[int] = None  # in minutes
    actual_time: Optional[int] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TaskPlanner:
    """Plans and manages software development tasks."""
    
    def __init__(self):
        """Initialize the task planner."""
        self.tasks: Dict[str, Task] = {}
        self.task_counter = 0
    
    def create_task(
        self,
        title: str,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: List[str] = None,
        task_type: str = "generic",
        estimated_time: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Task:
        """Create a new task."""
        task_id = f"task_{self.task_counter:04d}"
        self.task_counter += 1
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            priority=priority,
            dependencies=dependencies or [],
            task_type=task_type,
            estimated_time=estimated_time,
            created_at=self._get_timestamp(),
            metadata=metadata
        )
        
        self.tasks[task_id] = task
        logger.info(f"Created task: {title} (ID: {task_id})")
        
        return task_id
    
    def plan_from_requirement(self, requirement: str) -> List[str]:
        """
        Plan tasks from a natural language requirement.
        
        Args:
            requirement: Natural language requirement
            
        Returns:
            List of task IDs created
        """
        # This is a simplified planner - in a real implementation,
        # this would use the LLM to break down requirements
        
        task_ids = []
        
        # Common software development phases
        phases = [
            ("Requirements Analysis", "Analyze and clarify the requirements", TaskPriority.HIGH),
            ("Architecture Design", "Design the system architecture", TaskPriority.HIGH),
            ("Database Design", "Design database schema and models", TaskPriority.MEDIUM),
            ("Backend Development", "Implement backend API and logic", TaskPriority.HIGH),
            ("Frontend Development", "Implement user interface", TaskPriority.MEDIUM),
            ("Testing", "Write and run tests", TaskPriority.MEDIUM),
            ("Documentation", "Create user and technical documentation", TaskPriority.LOW),
            ("Deployment", "Deploy the application", TaskPriority.HIGH)
        ]
        
        previous_task_id = None
        
        for title, description, priority in phases:
            dependencies = [previous_task_id] if previous_task_id else []
            task_type = title.lower().replace(" ", "_")
            task_id = self.create_task(
                title=title,
                description=f"{description} for: {requirement}",
                priority=priority,
                dependencies=dependencies,
                task_type=task_type,
                estimated_time=60  # Default 1 hour
            )
            
            task_ids.append(task_id)
            previous_task_id = task_id
        
        logger.info(f"Planned {len(task_ids)} tasks from requirement")
        return task_ids
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready to execute (no blocked dependencies)."""
        ready_tasks = []
        
        for task in self.tasks.values():
            if (task.status == TaskStatus.PENDING and 
                self._are_dependencies_completed(task.dependencies)):
                ready_tasks.append(task)
        
        return sorted(ready_tasks, key=lambda t: t.priority.value, reverse=True)
    
    def start_task(self, task_id: str) -> bool:
        """Start working on a task."""
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return False
        
        task = self.tasks[task_id]
        
        if task.status != TaskStatus.PENDING:
            logger.warning(f"Task {task_id} is not in pending status")
            return False
        
        if not self._are_dependencies_completed(task.dependencies):
            logger.warning(f"Task {task_id} dependencies not completed")
            return False
        
        task.status = TaskStatus.IN_PROGRESS
        logger.info(f"Started task: {task.title}")
        return True
    
    def complete_task(self, task_id: str, actual_time: Optional[int] = None) -> bool:
        """Mark a task as completed."""
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return False
        
        task = self.tasks[task_id]
        
        if task.status != TaskStatus.IN_PROGRESS:
            logger.warning(f"Task {task_id} is not in progress")
            return False
        
        task.status = TaskStatus.COMPLETED
        task.actual_time = actual_time
        task.completed_at = self._get_timestamp()
        
        logger.info(f"Completed task: {task.title}")
        return True
    
    def fail_task(self, task_id: str, reason: str = "Unknown error") -> bool:
        """Mark a task as failed."""
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return False
        
        task = self.tasks[task_id]
        task.status = TaskStatus.FAILED
        
        if not task.metadata:
            task.metadata = {}
        task.metadata["failure_reason"] = reason
        
        logger.warning(f"Task {task.title} failed: {reason}")
        return True
    
    def get_task_progress(self) -> Dict[str, Any]:
        """Get overall progress of all tasks."""
        total_tasks = len(self.tasks)
        if total_tasks == 0:
            return {"progress": 0, "status": "No tasks"}
        
        completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        in_progress = sum(1 for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS)
        failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        pending = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
        
        progress = (completed / total_tasks) * 100
        
        return {
            "total_tasks": total_tasks,
            "completed": completed,
            "in_progress": in_progress,
            "failed": failed,
            "pending": pending,
            "progress_percentage": round(progress, 2),
            "status": self._get_overall_status(completed, failed, total_tasks)
        }
    
    def _are_dependencies_completed(self, dependencies: List[str]) -> bool:
        """Check if all dependencies are completed."""
        for dep_id in dependencies:
            if dep_id not in self.tasks:
                logger.warning(f"Dependency {dep_id} not found")
                return False
            
            if self.tasks[dep_id].status != TaskStatus.COMPLETED:
                return False
        
        return True
    
    def _get_overall_status(self, completed: int, failed: int, total: int) -> str:
        """Get overall project status."""
        if failed > 0:
            return "has_issues"
        elif completed == total:
            return "completed"
        elif completed > 0:
            return "in_progress"
        else:
            return "not_started"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_task_by_id(self, task_id: str) -> str:
        """Get a task by its ID."""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        return list(self.tasks.values())
    
    def clear_completed_tasks(self) -> None:
        """Remove completed tasks to free memory."""
        completed_ids = [
            task_id for task_id, task in self.tasks.items()
            if task.status == TaskStatus.COMPLETED
        ]
        
        for task_id in completed_ids:
            del self.tasks[task_id]
        
        logger.info(f"Cleared {len(completed_ids)} completed tasks")
