import os
from typing import Dict, Optional, List
import json
import random

# Try to import OpenAI, but make it optional
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class AIAgent:
    """
    AI Agent for handling chat interactions with optional LLM integration.
    Falls back to simple deterministic responses if LLM is not available.
    """
    
    def __init__(self):
        self.client = None
        self.model = "gpt-4"  # Default model
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if self.api_key and OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=self.api_key)
            # Try to use a smaller model if available
            try:
                models = self.client.models.list()
                if any(m.id == "gpt-4-turbo" for m in models.data):
                    self.model = "gpt-4-turbo"
                elif any(m.id == "gpt-3.5-turbo" for m in models.data):
                    self.model = "gpt-3.5-turbo"
            except Exception:
                # If we can't list models, use the default
                pass
    
    async def call_llm(
        self, 
        message: str, 
        system_prompt: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> str:
        """
        Call the LLM with the given message and optional system prompt.
        Falls back to simple responses if LLM is not available.
        
        Args:
            message: The user's message
            system_prompt: Optional system prompt to guide the LLM
            context: Optional additional context (e.g., user profile, recommendations)
            
        Returns:
            The assistant's response
        """
        if self.client and self.api_key:
            return await self._call_openai(message, system_prompt, context)
        else:
            return self._simple_response(message, context)
    
    async def _call_openai(
        self, 
        message: str, 
        system_prompt: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> str:
        """Call the OpenAI API with the given message and context."""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            if context:
                # Add context as a system message
                context_str = json.dumps(context, indent=2)
                messages.append({
                    "role": "system",
                    "content": f"Here is some context about the user and their learning path:\n{context_str}"
                })
            
            messages.append({"role": "user", "content": message})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fall back to simple response if API call fails
            print(f"Error calling OpenAI API: {e}")
            return self._simple_response(message, context)
    
    def _simple_response(self, message: str, context: Optional[Dict] = None) -> str:
        """Generate a simple deterministic response when LLM is not available."""
        # Simple keyword-based responses
        greetings = ["hello", "hi", "hey", "greetings"]
        thanks = ["thank", "thanks", "appreciate"]
        
        message_lower = message.lower()
        
        # Check for greetings
        if any(word in message_lower for word in greetings):
            return "Hello! I'm your learning assistant. How can I help you with your learning journey today?"
        
        # Check for thanks
        if any(word in message_lower for word in thanks):
            return "You're welcome! Is there anything else I can help you with?"
        
        # Check for learning-related keywords
        learning_keywords = {
            "learn": "Learning new skills takes time and practice. ",
            "difficult": "Challenging topics can be tough, but don't give up! ",
            "help": "I'm here to help you with your learning journey. ",
            "recommend": "Based on your profile, I'd recommend focusing on ",
            "what": "That's a great question! "
        }
        
        # Build a response based on keywords
        response_parts = []
        for keyword, text in learning_keywords.items():
            if keyword in message_lower:
                response_parts.append(text)
        
        # If we found matching keywords, use them
        if response_parts:
            response = " ".join(response_parts)
        else:
            # Default response
            response = "I understand you're asking about your learning path. "
        
        # Add context if available
        if context and "recommendations" in context:
            recommendations = context["recommendations"]
            if recommendations and len(recommendations) > 0:
                first_rec = recommendations[0]
                if "recommended_job_roles" in first_rec and first_rec["recommended_job_roles"]:
                    job = first_rec["recommended_job_roles"][0]
                    response += f"I see you're interested in {job}. "
                
                if "pathway" in first_rec and first_rec["pathway"]:
                    next_step = first_rec["pathway"][0]
                    response += f"Your next step is to {next_step.get('description', 'continue learning')}. "
        
        # Add a closing phrase
        closings = [
            "Would you like me to elaborate on any of these points?",
            "How can I assist you further with your learning goals?",
            "Is there anything specific you'd like to know more about?",
            "Would you like me to suggest some learning resources?"
        ]
        
        response += random.choice(closings)
        return response

# Create a singleton instance
ai_agent = AIAgent()
