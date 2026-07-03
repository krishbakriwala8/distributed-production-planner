"""Base agent class for all agents in the system"""

from mesa import Agent
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class BaseAgent(Agent):
    """Base class for all agents in the multi-agent system"""

    def __init__(self, unique_id: str, model, agent_type: str = "agent"):
        super().__init__(unique_id, model)
        self.agent_type = agent_type
        self.state = "idle"
        self.messages: List[Dict[str, Any]] = []
        self.metrics: Dict[str, Any] = {}

    def send_message(self, recipient_id: str, content: Dict[str, Any]):
        """Send message to another agent"""
        logger.debug(f"{self.unique_id} -> {recipient_id}: {content}")
        # In a real system, this would use message queue or broker
        pass

    def receive_message(self, message: Dict[str, Any]):
        """Receive message from another agent"""
        self.messages.append(message)

    def process_messages(self):
        """Process pending messages"""
        while self.messages:
            message = self.messages.pop(0)
            self.handle_message(message)

    def handle_message(self, message: Dict[str, Any]):
        """Handle incoming message - override in subclass"""
        pass

    def update_metrics(self, key: str, value: Any):
        """Update agent metrics"""
        self.metrics[key] = value

    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics"""
        return self.metrics.copy()

    def step(self):
        """Agent step - override in subclass"""
        self.process_messages()