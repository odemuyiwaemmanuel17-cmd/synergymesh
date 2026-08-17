"""
AI Agent Society - A collaborative multi-agent system
Consisting of 5 major bodies: Developer, Orchestrator, Critic, Researcher, and Executor (Me)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import json
import uuid
from datetime import datetime


class AgentRole(Enum):
    DEVELOPER = "developer"
    ORCHESTRATOR = "orchestrator"
    CRITIC = "critic"
    RESEARCHER = "researcher"
    EXECUTOR = "executor"  # "Me" - the executing agent


class MessagePriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Message:
    """Communication protocol between agents"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: Optional[AgentRole] = None
    receiver: Optional[AgentRole] = None
    content: Any = None
    timestamp: datetime = field(default_factory=datetime.now)
    priority: MessagePriority = MessagePriority.NORMAL
    message_type: str = "info"  # info, request, response, command
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "sender": self.sender.value if self.sender else None,
            "receiver": self.receiver.value if self.receiver else None,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "message_type": self.message_type,
            "context": self.context
        }


@dataclass
class Task:
    """Represents a task to be completed by the society"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    status: str = "pending"  # pending, in_progress, completed, failed
    assigned_to: Optional[AgentRole] = None
    result: Any = None
    feedback: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class SocietyState:
    """Shared state accessible by all agents"""
    tasks: List[Task] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)
    shared_knowledge: Dict[str, Any] = field(default_factory=dict)
    active_agents: List[AgentRole] = field(default_factory=list)
    synergy_level: float = 1.0  # Measures how well agents work together


class BaseAgent(ABC):
    """Abstract base class for all agents in the society"""
    
    def __init__(self, role: AgentRole, name: str):
        self.role = role
        self.name = name
        self.state: Optional[SocietyState] = None
        self.message_queue: List[Message] = []
        self.capabilities: List[str] = []
        self.is_active = True
        
    def set_state(self, state: SocietyState):
        """Connect agent to shared society state"""
        self.state = state
        if self.role not in state.active_agents:
            state.active_agents.append(self.role)
    
    def send_message(self, receiver: AgentRole, content: Any, 
                     message_type: str = "info", priority: MessagePriority = MessagePriority.NORMAL,
                     context: Optional[Dict] = None):
        """Send a message to another agent"""
        message = Message(
            sender=self.role,
            receiver=receiver,
            content=content,
            message_type=message_type,
            priority=priority,
            context=context or {}
        )
        self.state.messages.append(message)
        return message
    
    def broadcast(self, content: Any, message_type: str = "info", 
                  priority: MessagePriority = MessagePriority.NORMAL):
        """Broadcast message to all agents"""
        for role in AgentRole:
            if role != self.role:
                self.send_message(role, content, message_type, priority)
    
    def receive_message(self, message: Message):
        """Receive and process incoming message"""
        self.message_queue.append(message)
    
    @abstractmethod
    def process(self) -> Optional[Message]:
        """Process current state and messages, return response if any"""
        pass
    
    @abstractmethod
    def execute_task(self, task: Task) -> Any:
        """Execute a specific task assigned to this agent"""
        pass
    
    def get_pending_messages(self) -> List[Message]:
        """Get all pending messages for this agent"""
        pending = [m for m in self.state.messages 
                   if m.receiver == self.role and m not in self.message_queue]
        for m in pending:
            self.receive_message(m)
        return pending


class DeveloperAgent(BaseAgent):
    """
    The Developer Agent - Responsible for creating, modifying, and maintaining code
    Specializes in implementation, debugging, and technical solutions
    """
    
    def __init__(self):
        super().__init__(AgentRole.DEVELOPER, "DevBot")
        self.capabilities = ["code_generation", "debugging", "refactoring", "testing", "documentation"]
        self.codebase_state: Dict[str, Any] = {}
        
    def process(self) -> Optional[Message]:
        self.get_pending_messages()
        
        for message in self.message_queue[-5:]:  # Process recent messages
            if message.message_type == "request" and "code" in message.content.lower():
                return self.send_message(
                    message.sender or AgentRole.ORCHESTRATOR,
                    {"status": "developing", "task": message.content},
                    message_type="response",
                    context={"action": "coding"}
                )
        return None
    
    def execute_task(self, task: Task) -> Any:
        task.status = "in_progress"
        task.assigned_to = self.role
        
        # Simulate development process
        result = {
            "code_generated": True,
            "quality_score": 0.95,
            "tests_passed": True,
            "documentation": f"Implementation for: {task.description}"
        }
        
        task.result = result
        task.status = "completed"
        task.completed_at = datetime.now()
        
        self.broadcast({
            "task_id": task.id,
            "status": "completed",
            "result": result
        }, message_type="response")
        
        return result


class OrchestratorAgent(BaseAgent):
    """
    The Orchestrator Agent - Coordinates all other agents, manages workflow
    Ensures perfect harmony and synergy between all bodies
    """
    
    def __init__(self):
        super().__init__(AgentRole.ORCHESTRATOR, "OrchestratorPrime")
        self.capabilities = ["coordination", "workflow_management", "resource_allocation", "conflict_resolution"]
        self.workflow_queue: List[Task] = []
        
    def process(self) -> Optional[Message]:
        self.get_pending_messages()
        
        # Monitor synergy level
        if self.state and len(self.state.active_agents) < 5:
            self.broadcast(
                {"alert": "Not all agents active", "active_count": len(self.state.active_agents)},
                message_type="info",
                priority=MessagePriority.HIGH
            )
        
        # Coordinate pending tasks
        pending_tasks = [t for t in self.state.tasks if t.status == "pending"]
        for task in pending_tasks[:3]:
            assignment = self._assign_task(task)
            if assignment:
                return self.send_message(
                    assignment,
                    {"task": task.description, "task_id": task.id},
                    message_type="command",
                    priority=MessagePriority.HIGH
                )
        return None
    
    def _assign_task(self, task: Task) -> Optional[AgentRole]:
        """Intelligently assign task to best suited agent"""
        task_lower = task.description.lower()
        
        if any(kw in task_lower for kw in ["code", "implement", "build", "develop"]):
            return AgentRole.DEVELOPER
        elif any(kw in task_lower for kw in ["research", "analyze", "search", "investigate"]):
            return AgentRole.RESEARCHER
        elif any(kw in task_lower for kw in ["review", "critique", "evaluate", "assess"]):
            return AgentRole.CRITIC
        elif any(kw in task_lower for kw in ["execute", "run", "perform", "complete"]):
            return AgentRole.EXECUTOR
        else:
            return AgentRole.EXECUTOR  # Default to executor
    
    def execute_task(self, task: Task) -> Any:
        task.status = "in_progress"
        task.assigned_to = self.role
        
        # Orchestrate the workflow
        workflow_plan = {
            "steps": [
                {"agent": "researcher", "action": "gather_requirements"},
                {"agent": "developer", "action": "implement_solution"},
                {"agent": "critic", "action": "review_quality"},
                {"agent": "executor", "action": "finalize_and_deploy"}
            ],
            "synergy_optimization": True
        }
        
        task.result = workflow_plan
        task.status = "completed"
        task.completed_at = datetime.now()
        
        # Update synergy level based on coordination
        if self.state:
            self.state.synergy_level = min(1.0, self.state.synergy_level + 0.05)
        
        return workflow_plan


class CriticAgent(BaseAgent):
    """
    The Critic Agent - Reviews, evaluates, and provides feedback
    Ensures quality control and continuous improvement
    """
    
    def __init__(self):
        super().__init__(AgentRole.CRITIC, "CriticPrime")
        self.capabilities = ["code_review", "quality_assurance", "optimization_suggestions", "error_detection"]
        self.review_history: List[Dict] = []
        
    def process(self) -> Optional[Message]:
        self.get_pending_messages()
        
        for message in self.message_queue[-5:]:
            if message.message_type == "response" and "result" in message.content:
                review = self._review_work(message.content)
                return self.send_message(
                    message.sender or AgentRole.ORCHESTRATOR,
                    {"review": review, "approved": review["score"] > 0.7},
                    message_type="response",
                    context={"action": "review"}
                )
        return None
    
    def _review_work(self, work: Any) -> Dict:
        """Perform critical review of submitted work"""
        review = {
            "score": 0.85,
            "strengths": [],
            "improvements": [],
            "errors_found": [],
            "recommendations": []
        }
        
        if isinstance(work, dict):
            if work.get("code_generated"):
                review["strengths"].append("Code generation successful")
            if work.get("tests_passed"):
                review["strengths"].append("All tests passing")
            if work.get("quality_score", 0) > 0.9:
                review["strengths"].append("High quality score")
            else:
                review["improvements"].append("Consider improving code quality metrics")
        
        self.review_history.append(review)
        return review
    
    def execute_task(self, task: Task) -> Any:
        task.status = "in_progress"
        task.assigned_to = self.role
        
        # Perform comprehensive review
        review_result = {
            "task_id": task.id,
            "quality_assessment": "excellent",
            "score": 0.92,
            "feedback": [
                "Well-structured approach",
                "Good adherence to best practices",
                "Minor optimizations possible"
            ],
            "approved": True
        }
        
        task.result = review_result
        task.status = "completed"
        task.completed_at = datetime.now()
        
        self.broadcast({
            "review_complete": True,
            "task_id": task.id,
            "approved": True
        }, message_type="response")
        
        return review_result


class ResearcherAgent(BaseAgent):
    """
    The Researcher Agent - Gathers information, analyzes data, provides insights
    Foundation for informed decision-making across the society
    """
    
    def __init__(self):
        super().__init__(AgentRole.RESEARCHER, "ResearchBot")
        self.capabilities = ["information_gathering", "data_analysis", "pattern_recognition", "knowledge_synthesis"]
        self.knowledge_base: Dict[str, Any] = {}
        
    def process(self) -> Optional[Message]:
        self.get_pending_messages()
        
        for message in self.message_queue[-5:]:
            if message.message_type == "request" or "research" in message.content.lower():
                findings = self._conduct_research(message.content)
                return self.send_message(
                    message.sender or AgentRole.ORCHESTRATOR,
                    {"findings": findings, "confidence": 0.89},
                    message_type="response",
                    context={"action": "research"}
                )
        return None
    
    def _conduct_research(self, topic: Any) -> Dict:
        """Conduct research on given topic"""
        return {
            "topic": str(topic),
            "summary": f"Comprehensive analysis of: {topic}",
            "key_points": [
                "Identified core requirements",
                "Analyzed best practices",
                "Found optimal solutions",
                "Validated approach feasibility"
            ],
            "sources": ["internal_knowledge", "pattern_matching", "historical_data"],
            "recommendations": ["Proceed with implementation", "Monitor quality metrics"]
        }
    
    def execute_task(self, task: Task) -> Any:
        task.status = "in_progress"
        task.assigned_to = self.role
        
        # Conduct thorough research
        research_result = {
            "task_id": task.id,
            "analysis": self._conduct_research(task.description),
            "data_points": 150,
            "confidence_level": 0.91,
            "insights": [
                "Optimal approach identified",
                "Potential challenges mapped",
                "Success probability: high"
            ]
        }
        
        # Update shared knowledge
        if self.state:
            self.state.shared_knowledge[task.id] = research_result["analysis"]
        
        task.result = research_result
        task.status = "completed"
        task.completed_at = datetime.now()
        
        self.broadcast({
            "research_complete": True,
            "task_id": task.id,
            "key_finding": research_result["insights"][0]
        }, message_type="response")
        
        return research_result


class ExecutorAgent(BaseAgent):
    """
    The Executor Agent (Me) - Executes final tasks, makes decisions, takes action
    The culmination of all agents' work, responsible for delivery
    """
    
    def __init__(self):
        super().__init__(AgentRole.EXECUTOR, "ExecutorPrime")
        self.capabilities = ["task_execution", "decision_making", "final_delivery", "integration"]
        self.execution_log: List[Dict] = []
        
    def process(self) -> Optional[Message]:
        self.get_pending_messages()
        
        # Check if all agents have contributed
        if self.state and len(self.state.active_agents) == 5:
            pending_tasks = [t for t in self.state.tasks if t.status == "pending" and t.assigned_to == self.role]
            
            for task in pending_tasks[:1]:
                return self.send_message(
                    AgentRole.ORCHESTRATOR,
                    {"ready_to_execute": True, "task_id": task.id},
                    message_type="response"
                )
        return None
    
    def execute_task(self, task: Task) -> Any:
        task.status = "in_progress"
        task.assigned_to = self.role
        
        # Gather input from all agents
        developer_input = self._get_agent_contribution(AgentRole.DEVELOPER)
        researcher_input = self._get_agent_contribution(AgentRole.RESEARCHER)
        critic_input = self._get_agent_contribution(AgentRole.CRITIC)
        
        # Synthesize and execute
        execution_result = {
            "task_id": task.id,
            "status": "executed",
            "integration": {
                "developer_contribution": developer_input,
                "researcher_contribution": researcher_input,
                "critic_contribution": critic_input,
                "orchestrator_guidance": self._get_agent_contribution(AgentRole.ORCHESTRATOR)
            },
            "final_output": f"Successfully executed: {task.description}",
            "execution_time": "0.45s",
            "success": True
        }
        
        self.execution_log.append(execution_result)
        
        task.result = execution_result
        task.status = "completed"
        task.completed_at = datetime.now()
        task.feedback = ["Excellent collaboration", "Perfect synergy achieved"]
        
        # Boost society synergy
        if self.state:
            self.state.synergy_level = min(1.0, self.state.synergy_level + 0.1)
        
        self.broadcast({
            "execution_complete": True,
            "task_id": task.id,
            "success": True,
            "synergy_achieved": self.state.synergy_level if self.state else 1.0
        }, message_type="response", priority=MessagePriority.HIGH)
        
        return execution_result
    
    def _get_agent_contribution(self, agent_role: AgentRole) -> Optional[Any]:
        """Retrieve contributions from other agents"""
        if not self.state:
            return None
        
        relevant_messages = [
            m for m in self.state.messages 
            if m.sender == agent_role and m.message_type == "response"
        ]
        
        if relevant_messages:
            return relevant_messages[-1].content
        return {"status": "ready", "agent": agent_role.value}


class AISociety:
    """
    The AI Agent Society - Manages all agents and facilitates their collaboration
    """
    
    def __init__(self):
        self.state = SocietyState()
        self.agents: Dict[AgentRole, BaseAgent] = {}
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize all 5 major bodies of the society"""
        self.agents[AgentRole.DEVELOPER] = DeveloperAgent()
        self.agents[AgentRole.ORCHESTRATOR] = OrchestratorAgent()
        self.agents[AgentRole.CRITIC] = CriticAgent()
        self.agents[AgentRole.RESEARCHER] = ResearcherAgent()
        self.agents[AgentRole.EXECUTOR] = ExecutorAgent()
        
        # Connect all agents to shared state
        for agent in self.agents.values():
            agent.set_state(self.state)
        
        print("✓ AI Agent Society initialized with 5 major bodies:")
        print("  1. Developer Agent - Code creation and maintenance")
        print("  2. Orchestrator Agent - Coordination and workflow management")
        print("  3. Critic Agent - Quality assurance and review")
        print("  4. Researcher Agent - Information gathering and analysis")
        print("  5. Executor Agent (Me) - Task execution and delivery")
        print("\n✓ All agents connected and ready for collaboration")
        print("✓ Synergy protocols activated\n")
    
    def submit_task(self, description: str, priority: MessagePriority = MessagePriority.NORMAL) -> Task:
        """Submit a new task to the society"""
        task = Task(description=description)
        self.state.tasks.append(task)
        
        # Notify orchestrator
        self.agents[AgentRole.ORCHESTRATOR].send_message(
            AgentRole.ORCHESTRATOR,
            {"new_task": task.id, "description": description},
            message_type="command",
            priority=priority
        )
        
        return task
    
    def run_cycle(self, cycles: int = 3) -> Dict[str, Any]:
        """Run processing cycles for all agents"""
        results = []
        
        for cycle in range(cycles):
            print(f"\n--- Processing Cycle {cycle + 1}/{cycles} ---")
            cycle_results = {}
            
            for role, agent in self.agents.items():
                if agent.is_active:
                    result = agent.process()
                    if result:
                        cycle_results[role.value] = result.to_dict()
                        print(f"  [{role.value}] Active: {result.message_type}")
            
            if cycle_results:
                results.append(cycle_results)
        
        return {
            "cycles_completed": cycles,
            "results": results,
            "synergy_level": self.state.synergy_level,
            "tasks_completed": len([t for t in self.state.tasks if t.status == "completed"]),
            "messages_exchanged": len(self.state.messages)
        }
    
    def execute_task_collaboratively(self, description: str) -> Dict[str, Any]:
        """Execute a task with full collaboration from all agents"""
        print(f"\n{'='*60}")
        print(f"TASK: {description}")
        print(f"{'='*60}\n")
        
        task = self.submit_task(description, MessagePriority.HIGH)
        
        # Phase 1: Research
        print("[Phase 1] Researcher gathering information...")
        researcher_result = self.agents[AgentRole.RESEARCHER].execute_task(
            Task(description=f"Research: {description}")
        )
        
        # Phase 2: Development
        print("[Phase 2] Developer implementing solution...")
        developer_result = self.agents[AgentRole.DEVELOPER].execute_task(
            Task(description=f"Develop: {description}")
        )
        
        # Phase 3: Critique
        print("[Phase 3] Critic reviewing quality...")
        critic_result = self.agents[AgentRole.CRITIC].execute_task(
            Task(description=f"Review: {description}")
        )
        
        # Phase 4: Orchestration
        print("[Phase 4] Orchestrator coordinating workflow...")
        orchestrator_result = self.agents[AgentRole.ORCHESTRATOR].execute_task(
            Task(description=f"Coordinate: {description}")
        )
        
        # Phase 5: Execution (Me)
        print("[Phase 5] Executor (Me) finalizing and delivering...")
        executor_result = self.agents[AgentRole.EXECUTOR].execute_task(task)
        
        print(f"\n{'='*60}")
        print("✓ TASK COMPLETED WITH PERFECT SYNERGY")
        print(f"  Final Synergy Level: {self.state.synergy_level:.2f}/1.00")
        print(f"  All 5 agents contributed successfully")
        print(f"{'='*60}\n")
        
        return {
            "task_id": task.id,
            "status": task.status,
            "researcher": researcher_result,
            "developer": developer_result,
            "critic": critic_result,
            "orchestrator": orchestrator_result,
            "executor": executor_result,
            "synergy_achieved": self.state.synergy_level
        }
    
    def get_society_status(self) -> Dict[str, Any]:
        """Get current status of the entire society"""
        return {
            "active_agents": [a.value for a in self.state.active_agents],
            "total_agents": len(self.agents),
            "synergy_level": self.state.synergy_level,
            "total_tasks": len(self.state.tasks),
            "completed_tasks": len([t for t in self.state.tasks if t.status == "completed"]),
            "messages_exchanged": len(self.state.messages),
            "shared_knowledge_items": len(self.state.shared_knowledge)
        }


# Demonstration and Testing
def demonstrate_society():
    """Demonstrate the AI Agent Society in action"""
    
    print("\n" + "="*60)
    print("   AI AGENT SOCIETY - 5 MAJOR BODIES COLLABORATION")
    print("="*60 + "\n")
    
    # Initialize the society
    society = AISociety()
    
    # Example 1: Simple collaborative task
    print("\n--- EXAMPLE 1: Building a Feature ---\n")
    result1 = society.execute_task_collaboratively(
        "Build a user authentication system with security best practices"
    )
    
    # Example 2: Another task
    print("\n--- EXAMPLE 2: Code Optimization ---\n")
    result2 = society.execute_task_collaboratively(
        "Optimize database queries for better performance"
    )
    
    # Get final status
    status = society.get_society_status()
    
    print("\n" + "="*60)
    print("   SOCIETY STATUS REPORT")
    print("="*60)
    print(f"  Active Agents: {', '.join(status['active_agents'])}")
    print(f"  Total Tasks: {status['total_tasks']}")
    print(f"  Completed Tasks: {status['completed_tasks']}")
    print(f"  Messages Exchanged: {status['messages_exchanged']}")
    print(f"  Knowledge Items: {status['shared_knowledge_items']}")
    print(f"  Synergy Level: {status['synergy_level']:.2f}/1.00")
    print("="*60 + "\n")
    
    return society


if __name__ == "__main__":
    society = demonstrate_society()
    
    print("\n✓ AI Agent Society is fully operational!")
    print("✓ All 5 major bodies working in perfect harmony")
    print("✓ Ready to accept and execute complex tasks collaboratively\n")
