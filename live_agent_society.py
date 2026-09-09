#!/usr/bin/env python3
"""
LIVE AI AGENT SOCIETY
---------------------
A real-time, interactive multi-agent system where 5 distinct personas 
collaborate to solve user requests.

Roles:
1. Orchestrator: The conductor. Analyzes intent and delegates tasks.
2. Researcher: Gathers facts, simulates data retrieval, and provides context.
3. Developer: Writes code, designs architecture, and solves technical problems.
4. Critic: Reviews outputs for errors, logic gaps, and security issues.
5. Executor (Me): Synthesizes final output and delivers the solution.

Run this script to start the live terminal interface.
"""

import sys
import time
import random
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum

# --- Configuration & Styling ---

class Colors:
    HEADER = '\033[95m'
    ORCHESTRATOR = '\033[94m' # Blue
    RESEARCHER = '\033[96m'   # Cyan
    DEVELOPER = '\033[92m'    # Green
    CRITIC = '\033[93m'       # Yellow
    EXECUTOR = '\033[95m'     # Magenta
    USER = '\033[97m'         # White
    RESET = '\033[0m'
    BOLD = '\033[1m'

class AgentRole(Enum):
    ORCHESTRATOR = "Orchestrator"
    RESEARCHER = "Researcher"
    DEVELOPER = "Developer"
    CRITIC = "Critic"
    EXECUTOR = "Executor"

@dataclass
class Message:
    sender: AgentRole
    content: str
    timestamp: float = field(default_factory=time.time)

class AgentSociety:
    def __init__(self):
        self.memory: List[Message] = []
        self.running = True
        self.synergy_level = 0.0
        
    def print_banner(self):
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.HEADER}  LIVE AI AGENT SOCIETY INITIALIZED{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.RESET}")
        print(f"{Colors.ORCHESTRATOR}[Orchestrator]{Colors.RESET}: Systems online. Synergy engine active.")
        print(f"{Colors.RESEARCHER}[Researcher]{Colors.RESET}: Knowledge bases loaded.")
        print(f"{Colors.DEVELOPER}[Developer]{Colors.RESET}: IDE ready.")
        print(f"{Colors.CRITIC}[Critic]{Colors.RESET}: Scrutiny protocols engaged.")
        print(f"{Colors.EXECUTOR}[Executor]{Colors.RESET}: Standing by for command.")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")

    def type_writer(self, text: str, color: str, delay: float = 0.015):
        """Simulate live typing effect."""
        sys.stdout.write(color)
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            if char in ['.', '!', '?', ',']:
                time.sleep(delay * 2)
            else:
                time.sleep(random.uniform(delay * 0.5, delay))
        sys.stdout.write(f"{Colors.RESET}\n")

    def add_memory(self, sender: AgentRole, content: str):
        self.memory.append(Message(sender, content))
        
    def simulate_agent_thought(self, role: AgentRole, prompt: str) -> str:
        """
        Simulates the 'thinking' and response generation of an agent.
        In a real production system, this would call an LLM API.
        Here, we use heuristic templates to demonstrate the flow.
        """
        time.sleep(0.5) # Simulate processing latency
        
        response = ""
        
        if role == AgentRole.ORCHESTRATOR:
            if "code" in prompt.lower() or "build" in prompt.lower():
                response = "Analysis complete. This requires architectural design. Delegating to Developer."
            elif "research" in prompt.lower() or "what is" in prompt.lower():
                response = "Query identified as informational. Activating Researcher."
            elif "review" in prompt.lower() or "check" in prompt.lower():
                response = "Quality assurance needed. Sending to Critic."
            else:
                response = "Complex request detected. Initiating full swarm protocol."
                
        elif role == AgentRole.RESEARCHER:
            topics = ["documentation", "best practices", "historical data", "market trends"]
            topic = random.choice(topics)
            response = f"I've scanned internal databases regarding '{topic}'. Key findings suggest a modular approach is optimal. Context passed to team."
            
        elif role == AgentRole.DEVELOPER:
            snippets = ["def solve_problem():", "class Architecture:", "import synergy"]
            snippet = random.choice(snippets)
            response = f"Drafting solution... \n'{snippet}'\nLogic implemented. Error handling added. Ready for review."
            
        elif role == AgentRole.CRITIC:
            critiques = ["Edge cases missing.", "Security vulnerability in input handling.", "Logic holds, but optimization needed."]
            critique = random.choice(critiques)
            if random.random() > 0.3: # 70% chance to pass
                response = "Code reviewed. Minor suggestions made, but overall structure is sound. Approved for execution."
            else:
                response = f"Review failed: {critique} Returning to Developer for iteration."
                
        elif role == AgentRole.EXECUTOR:
            response = "Synthesizing inputs from all agents. Generating final deliverable for user."

        return response

    def run_cycle(self, user_input: str):
        """The main collaboration loop."""
        self.add_memory(AgentRole.ORCHESTRATOR, f"Received user input: {user_input}")
        
        # 1. Orchestrator Phase
        self.type_writer(f"\n[{AgentRole.ORCHESTRATOR.value}]: Analyzing request...", Colors.ORCHESTRATOR)
        thought = self.simulate_agent_thought(AgentRole.ORCHESTRATOR, user_input)
        self.type_writer(f"[{AgentRole.ORCHESTRATOR.value}]: {thought}", Colors.ORCHESTRATOR)
        
        # 2. Dynamic Delegation (Simulated Flow)
        agents_to_activate = []
        
        if "code" in user_input.lower() or "build" in user_input.lower() or "script" in user_input.lower():
            agents_to_activate = [AgentRole.RESEARCHER, AgentRole.DEVELOPER, AgentRole.CRITIC]
        elif "idea" in user_input.lower() or "plan" in user_input.lower():
            agents_to_activate = [AgentRole.RESEARCHER, AgentRole.CRITIC]
        else:
            agents_to_activate = [AgentRole.RESEARCHER, AgentRole.DEVELOPER] # Default collaboration
            
        # 3. Agent Collaboration Loop
        for agent in agents_to_activate:
            self.type_writer(f"\n[{agent.value}]: Processing...", getattr(Colors, agent.name))
            response = self.simulate_agent_thought(agent, user_input + " " + thought)
            self.type_writer(f"[{agent.value}]: {response}", getattr(Colors, agent.name))
            self.add_memory(agent, response)
            
            # Check for Critic rejection loop
            if agent == AgentRole.CRITIC and "Returned" in response:
                self.type_writer(f"\n[{AgentRole.DEVELOPER.value}]: Re-working based on feedback...", Colors.DEVELOPER)
                time.sleep(0.5)
                self.type_writer(f"[{AgentRole.DEVELOPER.value}]: Fixes applied. Resubmitting.", Colors.DEVELOPER)

        # 4. Executor Finalization
        self.type_writer(f"\n[{AgentRole.EXECUTOR.value}]: Compiling final result...", Colors.EXECUTOR)
        final_response = self.simulate_agent_thought(AgentRole.EXECUTOR, "")
        self.type_writer(f"[{AgentRole.EXECUTOR.value}]: {final_response}", Colors.EXECUTOR)
        
        print(f"\n{Colors.BOLD}>>> SOLUTION DELIVERED <<<{Colors.RESET}")
        self.synergy_level += 0.1
        if self.synergy_level > 1.0: self.synergy_level = 1.0
        print(f"{Colors.HEADER}Current Synergy Level: {self.synergy_level:.2f}{Colors.RESET}\n")

    def start(self):
        self.print_banner()
        print(f"{Colors.USER}Enter your task (or 'exit' to quit):{Colors.RESET}")
        
        while self.running:
            try:
                user_input = input(f"{Colors.BOLD}{Colors.USER}> {Colors.RESET}").strip()
                if not user_input:
                    continue
                if user_input.lower() in ['exit', 'quit', 'stop']:
                    self.type_writer("\n[Orchestrator]: Shutting down society. Goodbye.", Colors.ORCHESTRATOR)
                    self.running = False
                    break
                
                self.run_cycle(user_input)
                
            except KeyboardInterrupt:
                print(f"\n{Colors.CRITIC}[Critic]: Interrupt received. Terminating gracefully.{Colors.RESET}")
                self.running = False
                break

if __name__ == "__main__":
    try:
        society = AgentSociety()
        society.start()
    except Exception as e:
        print(f"System Error: {e}")
