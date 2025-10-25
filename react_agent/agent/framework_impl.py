"""
LangGraph Framework Implementation
Wires the custom ReAct loop into LangGraph's state machine architecture
"""

from typing import TypedDict, List, Dict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator

from .react_loop import ReActController
from .personas import get_persona_prompt


class AgentState(TypedDict):
    """State for the ReAct agent graph."""
    messages: Annotated[List[Dict[str, str]], operator.add]
    persona: str
    business_context: str
    final_answer: str
    metadata: Dict
    iteration: int


class LangGraphReActAgent:
    """
    LangGraph-based ReAct agent that uses our custom loop controller.

    Architecture:
    - Node 1 (thought): LLM thinks and decides on action
    - Node 2 (action): Execute tool if needed
    - Node 3 (observe): Capture tool result
    - Node 4 (answer): Provide final response

    Our custom ReActController handles the actual logic, LangGraph provides the structure.
    """

    def __init__(self, llm_call, persona: str = "friendly_advisor", max_turns: int = 10):
        """
        Initialize the LangGraph ReAct agent.

        Args:
            llm_call: Function to call LLM
            persona: Persona name to use
            max_turns: Maximum reasoning iterations
        """
        self.llm_call = llm_call
        self.persona = persona
        self.max_turns = max_turns
        self.react_controller = ReActController(llm_call, max_turns)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine.

        Graph structure:
        START → process_message → END

        Note: We keep it simple since our ReActController handles the complex loop internally.
        """
        workflow = StateGraph(AgentState)

        # Add single processing node that runs our custom ReAct loop
        workflow.add_node("process_message", self._process_with_react_loop)

        # Set entry point
        workflow.set_entry_point("process_message")

        # Always end after processing (our loop handles iterations internally)
        workflow.add_edge("process_message", END)

        return workflow.compile()

    def _process_with_react_loop(self, state: AgentState) -> AgentState:
        """
        Process messages using our custom ReAct loop.

        Args:
            state: Current agent state

        Returns:
            Updated state with results
        """
        messages = state["messages"]

        # Run our custom ReAct controller
        final_answer, all_messages, metadata = self.react_controller.run(messages)

        # Update state
        return {
            "messages": all_messages,
            "persona": state["persona"],
            "business_context": state.get("business_context", ""),
            "final_answer": final_answer,
            "metadata": metadata,
            "iteration": state.get("iteration", 0) + 1
        }

    def run(self, user_message: str, business_context: str) -> Dict:
        """
        Run the agent on a user message.

        Args:
            user_message: User's input
            business_context: Business information to ground responses

        Returns:
            Dictionary with final_answer and metadata
        """
        # Get persona prompt
        system_prompt = get_persona_prompt(self.persona, business_context)

        # Initialize state
        initial_state = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "persona": self.persona,
            "business_context": business_context,
            "final_answer": "",
            "metadata": {},
            "iteration": 0
        }

        # Run the graph
        result = self.graph.invoke(initial_state)

        return {
            "final_answer": result["final_answer"],
            "metadata": result["metadata"],
            "persona": self.persona,
            "conversation": result["messages"]
        }


def create_langgraph_agent(llm_call, persona: str = "friendly_advisor", max_turns: int = 10):
    """
    Factory function to create a LangGraph ReAct agent.

    Args:
        llm_call: Function to call LLM
        persona: Persona to use
        max_turns: Max reasoning turns

    Returns:
        LangGraphReActAgent instance
    """
    return LangGraphReActAgent(llm_call, persona, max_turns)
