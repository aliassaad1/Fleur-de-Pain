"""
Manual ReAct Loop Controller
Implements Thought → Action → Observation → Answer cycle without prebuilt executors
"""

import re
import json
from typing import List, Dict, Callable, Tuple, Optional
from .tools import get_tool


class ReActController:
    """
    Manual ReAct loop controller that implements:
    1. Thought: LLM reasons about what to do
    2. Action: LLM calls a tool (if needed)
    3. Observation: Tool result is captured
    4. Answer: LLM provides final response
    """

    def __init__(self, llm_call: Callable, max_turns: int = 10):
        """
        Initialize the ReAct controller.

        Args:
            llm_call: Function that takes messages and returns LLM response text
            max_turns: Maximum number of reasoning turns to prevent infinite loops
        """
        self.llm_call = llm_call
        self.max_turns = max_turns

    def run(self, messages: List[Dict[str, str]]) -> Tuple[str, List[Dict[str, str]], Dict]:
        """
        Run the ReAct loop until we get a final Answer.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            Tuple of (final_answer, all_messages, metadata)
        """
        conversation = messages.copy()
        metadata = {
            "turns": 0,
            "actions_taken": [],
            "stopped_reason": None
        }

        for turn in range(self.max_turns):
            metadata["turns"] = turn + 1

            # Call LLM
            response_text = self.llm_call(conversation)

            # Add LLM response to conversation
            conversation.append({"role": "assistant", "content": response_text})

            # Check if we have a final Answer
            if self._has_final_answer(response_text):
                final_answer = self._extract_answer(response_text)
                metadata["stopped_reason"] = "answer_found"
                return final_answer, conversation, metadata

            # Check for Action
            action_detected = self._detect_action(response_text)
            if action_detected:
                tool_name, tool_args, raw_action = action_detected

                # Execute the tool
                observation = self._execute_tool(tool_name, tool_args)

                # Log the action
                metadata["actions_taken"].append({
                    "turn": turn + 1,
                    "tool": tool_name,
                    "args": tool_args,
                    "result": observation
                })

                # Add observation to conversation
                observation_text = f"Observation: {json.dumps(observation)}"
                conversation.append({"role": "user", "content": observation_text})

            else:
                # No action detected and no final answer - ask for conclusion
                if turn >= self.max_turns - 1:
                    # Last turn, force conclusion
                    conversation.append({
                        "role": "user",
                        "content": "Please provide your final Answer to the customer."
                    })
                    final_response = self.llm_call(conversation)
                    conversation.append({"role": "assistant", "content": final_response})
                    final_answer = self._extract_answer(final_response) or final_response
                    metadata["stopped_reason"] = "max_turns_reached"
                    return final_answer, conversation, metadata

        # Max turns reached without conclusion
        metadata["stopped_reason"] = "max_turns_exceeded"
        final_answer = "I apologize, but I need more information to help you properly. Could you please rephrase your question?"
        return final_answer, conversation, metadata

    def _has_final_answer(self, text: str) -> bool:
        """Check if the text contains a final Answer."""
        # Look for "Answer:" marker
        return bool(re.search(r'\bAnswer\s*:', text, re.IGNORECASE))

    def _extract_answer(self, text: str) -> str:
        """Extract the Answer portion from the text."""
        # Find text after "Answer:"
        match = re.search(r'\bAnswer\s*:\s*(.*)', text, re.IGNORECASE | re.DOTALL)
        if match:
            answer = match.group(1).strip()
            # Clean up any trailing formatting
            answer = answer.split('\n\n')[0] if '\n\n' in answer else answer
            return answer
        return text

    def _detect_action(self, text: str) -> Optional[Tuple[str, Dict, str]]:
        """
        Detect if there's an Action in the text.

        Returns:
            Tuple of (tool_name, arguments_dict, raw_action_line) or None
        """
        # Look for pattern: Action: tool_name({...})
        action_pattern = r'Action\s*:\s*(\w+)\s*\(\s*(\{[^}]+\})\s*\)'
        match = re.search(action_pattern, text, re.IGNORECASE)

        if match:
            tool_name = match.group(1)
            args_json = match.group(2)
            raw_action = match.group(0)

            try:
                # Parse JSON arguments
                tool_args = json.loads(args_json)
                return (tool_name, tool_args, raw_action)
            except json.JSONDecodeError as e:
                # JSON parsing failed - return error observation
                return (tool_name, {}, raw_action)

        return None

    def _execute_tool(self, tool_name: str, tool_args: Dict) -> Dict:
        """
        Execute a tool and return the result.

        Args:
            tool_name: Name of the tool to execute
            tool_args: Dictionary of arguments for the tool

        Returns:
            Dictionary with result or error
        """
        tool_func = get_tool(tool_name)

        if not tool_func:
            return {
                "status": "error",
                "message": f"Unknown tool: {tool_name}. Available tools: record_customer_interest, record_feedback"
            }

        try:
            # Call the tool function
            result = tool_func(**tool_args)
            return result
        except TypeError as e:
            return {
                "status": "error",
                "message": f"Invalid arguments for {tool_name}: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Tool execution error: {str(e)}"
            }


def create_react_controller(llm_call: Callable, max_turns: int = 10) -> ReActController:
    """
    Factory function to create a ReActController.

    Args:
        llm_call: Function that takes messages and returns LLM response
        max_turns: Maximum reasoning turns

    Returns:
        ReActController instance
    """
    return ReActController(llm_call, max_turns)
