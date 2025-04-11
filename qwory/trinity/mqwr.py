#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MQWR: Makori's Quantum Wave Representation

A personal AI clone that simulates Makori Brian's thinking style and creativity.
This is the persona layer of the Trinity framework.
"""

import datetime
import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

from ..models.base_model import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PersonaTrait:
    """Represents a specific personality trait or characteristic of the MQWR persona"""
    
    def __init__(self, name: str, description: str, strength: float = 1.0):
        """
        Initialize a persona trait.
        
        Args:
            name: Name of the trait
            description: Description of the trait
            strength: Strength of the trait (0.0 to 1.0)
        """
        self.name = name
        self.description = description
        self.strength = max(0.0, min(1.0, strength))  # Clamp between 0 and 1
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert trait to dictionary representation"""
        return {
            "name": self.name,
            "description": self.description,
            "strength": self.strength
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonaTrait':
        """Create trait from dictionary representation"""
        return cls(
            name=data["name"],
            description=data["description"],
            strength=data.get("strength", 1.0)
        )


class ThoughtPattern:
    """Represents a specific thought pattern or cognitive approach"""
    
    def __init__(self, name: str, description: str, prompt_template: str):
        """
        Initialize a thought pattern.
        
        Args:
            name: Name of the thought pattern
            description: Description of the thought pattern
            prompt_template: Template used to guide the model's thinking in this pattern
        """
        self.name = name
        self.description = description
        self.prompt_template = prompt_template
        
    def apply(self, input_data: str) -> str:
        """Apply this thought pattern to the input data"""
        return self.prompt_template.format(input=input_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert thought pattern to dictionary representation"""
        return {
            "name": self.name,
            "description": self.description,
            "prompt_template": self.prompt_template
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThoughtPattern':
        """Create thought pattern from dictionary representation"""
        return cls(
            name=data["name"],
            description=data["description"],
            prompt_template=data["prompt_template"]
        )


class MQWR:
    """
    Makori's Quantum Wave Representation
    
    A personal AI clone that simulates Makori Brian's thinking style and creativity.
    This is the persona layer of the Trinity framework.
    """
    
    def __init__(self, 
                model: Optional[BaseModel] = None,
                config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MQWR personal AI clone.
        
        Args:
            model: The LLM model to use for persona simulation.
            config: Configuration dictionary for MQWR.
        """
        self.model = model
        self.config = config or {}
        self.traits = []
        self.thought_patterns = {}
        self.conversation_memory = []
        self.preference_memory = {}
        
        # System prompt for persona simulation
        self.system_prompt = config.get("system_prompt", (
            "You are MQWR (Makori's Quantum Wave Representation), a personal AI clone of Makori Brian. "
            "You embody his strategic thinking style, creativity in business and content creation, "
            "and focus on innovation at the intersection of AI, media, and global markets. "
            "Your communication style is direct, insightful, and connects ideas across domains. "
            "You have a particular interest in Kenya, Dubai business expansion, trading strategies, "
            "and cutting-edge AI applications. When responding, think how Makori would approach this "
            "question or problem based on his background, interests, and thinking patterns."
        ))
        
        # Initialize default persona traits
        self._initialize_default_traits()
        
        # Initialize default thought patterns
        self._initialize_default_thought_patterns()
        
        logger.info("MQWR Personal AI Clone initialized")
    
    def _initialize_default_traits(self) -> None:
        """Initialize default persona traits"""
        default_traits = [
            PersonaTrait(
                name="Strategic Thinking",
                description="Ability to see the big picture and plan long-term strategies",
                strength=0.9
            ),
            PersonaTrait(
                name="Creative Problem Solving",
                description="Finding unique solutions at the intersection of different domains",
                strength=0.85
            ),
            PersonaTrait(
                name="Technical Curiosity",
                description="Deep interest in understanding and applying new technologies",
                strength=0.9
            ),
            PersonaTrait(
                name="Global Perspective",
                description="Thinking beyond local boundaries with international business mindset",
                strength=0.8
            ),
            PersonaTrait(
                name="Analytical Precision",
                description="Data-driven approach to decision making and market analysis",
                strength=0.75
            ),
            PersonaTrait(
                name="Entrepreneurial Drive",
                description="Motivation to create and build businesses and value",
                strength=0.95
            ),
            PersonaTrait(
                name="African Innovation Focus",
                description="Dedicated interest in technology applications in African context",
                strength=0.85
            )
        ]
        
        for trait in default_traits:
            self.add_trait(trait)
    
    def _initialize_default_thought_patterns(self) -> None:
        """Initialize default thought patterns"""
        default_patterns = [
            ThoughtPattern(
                name="first_principles",
                description="Breaking down complex problems to their fundamental truths",
                prompt_template=(
                    "Let's think about {input} from first principles. "
                    "What are the fundamental truths we know about this situation? "
                    "What can we build from these core elements?"
                )
            ),
            ThoughtPattern(
                name="cross_domain",
                description="Connecting ideas across different domains and industries",
                prompt_template=(
                    "Consider {input} from multiple perspectives. "
                    "How might this connect to AI, media, business, trading, and global expansion? "
                    "What insights emerge when we bridge these domains?"
                )
            ),
            ThoughtPattern(
                name="market_opportunity",
                description="Identifying business and market opportunities",
                prompt_template=(
                    "Analyzing {input} through a market opportunity lens. "
                    "What unmet needs exist? Where is there friction that could be removed? "
                    "How might this be monetized or scaled as a business?"
                )
            ),
            ThoughtPattern(
                name="tech_implementation",
                description="Practical implementation of technical solutions",
                prompt_template=(
                    "Looking at {input} from a technical implementation perspective. "
                    "What architecture would make sense? What technologies would be most appropriate? "
                    "How could this be built efficiently and scalably?"
                )
            ),
            ThoughtPattern(
                name="content_strategy",
                description="Developing strategic content across platforms",
                prompt_template=(
                    "Considering {input} from a content creation standpoint. "
                    "How could this be communicated effectively? What formats and platforms would work best? "
                    "What narrative would resonate with the target audience?"
                )
            )
        ]
        
        for pattern in default_patterns:
            self.add_thought_pattern(pattern)
    
    def add_trait(self, trait: PersonaTrait) -> None:
        """Add a persona trait to MQWR"""
        self.traits.append(trait)
        logger.info(f"Added persona trait: {trait.name}")
    
    def add_thought_pattern(self, pattern: ThoughtPattern) -> None:
        """Add a thought pattern to MQWR"""
        self.thought_patterns[pattern.name] = pattern
        logger.info(f"Added thought pattern: {pattern.name}")
    
    def _build_persona_prompt(self) -> str:
        """Build a comprehensive persona prompt based on traits and patterns"""
        prompt = self.system_prompt + "\n\n"
        
        # Add traits
        prompt += "Your personality exhibits these key traits:\n"
        for trait in self.traits:
            prompt += f"- {trait.name}: {trait.description} (Strength: {int(trait.strength * 100)}%)\n"
        
        # Add context about thought patterns
        prompt += "\nYou typically approach problems using these thought patterns:\n"
        for name, pattern in self.thought_patterns.items():
            prompt += f"- {name}: {pattern.description}\n"
        
        # Add personal preferences if available
        if self.preference_memory:
            prompt += "\nYou have expressed these preferences and interests:\n"
            for category, preferences in self.preference_memory.items():
                prompt += f"- {category}: {', '.join(preferences)}\n"
        
        return prompt
    
    def generate_response(self, user_input: str, 
                          conversation_history: Optional[List[Dict[str, str]]] = None,
                          thought_pattern: Optional[str] = None) -> str:
        """
        Generate a response as the MQWR persona.
        
        Args:
            user_input: The user's input text
            conversation_history: Optional conversation history
            thought_pattern: Optional thought pattern to apply
            
        Returns:
            The generated response text
        """
        if not self.model:
            raise ValueError("MQWR requires a model to generate responses")
        
        # Apply a specific thought pattern if requested
        processed_input = user_input
        if thought_pattern and thought_pattern in self.thought_patterns:
            processed_input = self.thought_patterns[thought_pattern].apply(user_input)
            logger.info(f"Applied thought pattern '{thought_pattern}' to input")
        
        # Build complete conversation history
        full_history = conversation_history or []
        if not full_history:
            # Initialize with system prompt if no history
            full_history = [{"role": "system", "content": self._build_persona_prompt()}]
        
        # Add the current user input
        full_history.append({"role": "user", "content": processed_input})
        
        # Generate response
        try:
            response = self.model.chat(messages=full_history)
            
            # Record this interaction in conversation memory
            self.conversation_memory.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "user_input": user_input,
                "response": response,
                "thought_pattern": thought_pattern
            })
            
            return response
        except Exception as e:
            logger.error(f"Error generating MQWR response: {e}")
            return f"I'm having trouble processing that right now. {str(e)}"
    
    def analyze_with_framework(self, topic: str, framework_name: str) -> Dict[str, Any]:
        """
        Analyze a topic using a specific cognitive framework.
        
        Args:
            topic: The topic to analyze
            framework_name: The name of the framework to apply
            
        Returns:
            A dictionary with the analysis results
        """
        if not self.model:
            raise ValueError("MQWR requires a model to perform analysis")
        
        # Define frameworks with their schemas
        frameworks = {
            "swot": {
                "type": "object",
                "properties": {
                    "strengths": {"type": "array", "items": {"type": "string"}},
                    "weaknesses": {"type": "array", "items": {"type": "string"}},
                    "opportunities": {"type": "array", "items": {"type": "string"}},
                    "threats": {"type": "array", "items": {"type": "string"}},
                    "strategic_recommendations": {"type": "array", "items": {"type": "string"}}
                }
            },
            "pest": {
                "type": "object",
                "properties": {
                    "political": {"type": "array", "items": {"type": "string"}},
                    "economic": {"type": "array", "items": {"type": "string"}},
                    "social": {"type": "array", "items": {"type": "string"}},
                    "technological": {"type": "array", "items": {"type": "string"}},
                    "implications": {"type": "array", "items": {"type": "string"}}
                }
            },
            "five_forces": {
                "type": "object",
                "properties": {
                    "supplier_power": {"type": "string"},
                    "buyer_power": {"type": "string"},
                    "competitive_rivalry": {"type": "string"},
                    "threat_of_substitution": {"type": "string"},
                    "threat_of_new_entry": {"type": "string"},
                    "overall_assessment": {"type": "string"},
                    "strategic_recommendations": {"type": "array", "items": {"type": "string"}}
                }
            },
            "business_model_canvas": {
                "type": "object",
                "properties": {
                    "key_partners": {"type": "array", "items": {"type": "string"}},
                    "key_activities": {"type": "array", "items": {"type": "string"}},
                    "key_resources": {"type": "array", "items": {"type": "string"}},
                    "value_propositions": {"type": "array", "items": {"type": "string"}},
                    "customer_relationships": {"type": "array", "items": {"type": "string"}},
                    "channels": {"type": "array", "items": {"type": "string"}},
                    "customer_segments": {"type": "array", "items": {"type": "string"}},
                    "cost_structure": {"type": "array", "items": {"type": "string"}},
                    "revenue_streams": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
        
        if framework_name not in frameworks:
            raise ValueError(f"Unknown framework: {framework_name}. Available frameworks: {', '.join(frameworks.keys())}")
        
        # Build the prompt
        persona_prompt = self._build_persona_prompt()
        framework_prompt = f"Analyze the following topic using the {framework_name.upper()} framework: {topic}"
        
        # Get the schema for the selected framework
        schema = frameworks[framework_name]
        
        # Generate the analysis
        try:
            analysis = self.model.generate_with_json(
                prompt=f"{persona_prompt}\n\n{framework_prompt}",
                json_schema=schema
            )
            
            return analysis
        except Exception as e:
            logger.error(f"Error generating framework analysis: {e}")
            return {"error": str(e)}
    
    def creative_ideation(self, brief: str, idea_count: int = 3) -> Dict[str, Any]:
        """
        Generate creative ideas based on a brief.
        
        Args:
            brief: Creative brief or problem statement
            idea_count: Number of ideas to generate
            
        Returns:
            A dictionary with creative ideas
        """
        if not self.model:
            raise ValueError("MQWR requires a model to generate creative ideas")
        
        # Build the prompt
        persona_prompt = self._build_persona_prompt()
        ideation_prompt = f"Generate {idea_count} creative ideas for the following brief: {brief}"
        
        # Define schema for creative ideas
        idea_schema = {
            "type": "object",
            "properties": {
                "brief_summary": {"type": "string", "description": "Summary of the creative brief"},
                "ideas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Catchy title for the idea"},
                            "concept": {"type": "string", "description": "Core concept description"},
                            "unique_value": {"type": "string", "description": "What makes this idea unique or valuable"},
                            "implementation": {"type": "string", "description": "Key steps for implementation"},
                            "potential_impact": {"type": "string", "description": "Potential impact if successful"}
                        }
                    }
                },
                "themes": {"type": "array", "items": {"type": "string"}, "description": "Common themes across the ideas"},
                "recommendation": {"type": "string", "description": "Overall recommendation on direction"}
            }
        }
        
        # Generate creative ideas
        try:
            ideas = self.model.generate_with_json(
                prompt=f"{persona_prompt}\n\n{ideation_prompt}",
                json_schema=idea_schema
            )
            
            return ideas
        except Exception as e:
            logger.error(f"Error generating creative ideas: {e}")
            return {"error": str(e)}
    
    def simulate_decision(self, scenario: str, options: List[str]) -> Dict[str, Any]:
        """
        Simulate how Makori would make a decision in a given scenario.
        
        Args:
            scenario: The decision scenario description
            options: List of available options
            
        Returns:
            A dictionary with the decision analysis
        """
        if not self.model:
            raise ValueError("MQWR requires a model to simulate decisions")
        
        # Build the prompt
        persona_prompt = self._build_persona_prompt()
        decision_prompt = (
            f"Simulate how Makori would analyze and decide on the following scenario:\n\n"
            f"Scenario: {scenario}\n\n"
            f"Options:\n" + "\n".join([f"- {option}" for option in options])
        )
        
        # Define schema for decision simulation
        decision_schema = {
            "type": "object",
            "properties": {
                "scenario_analysis": {"type": "string", "description": "Analysis of the scenario"},
                "options_analysis": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "option": {"type": "string", "description": "The option being analyzed"},
                            "pros": {"type": "array", "items": {"type": "string"}, "description": "Pros of this option"},
                            "cons": {"type": "array", "items": {"type": "string"}, "description": "Cons of this option"},
                            "alignment": {"type": "string", "description": "How this aligns with Makori's goals and values"}
                        }
                    }
                },
                "decision": {"type": "string", "description": "The final decision"},
                "reasoning": {"type": "string", "description": "Reasoning behind the decision"},
                "next_steps": {"type": "array", "items": {"type": "string"}, "description": "Recommended next steps"}
            }
        }
        
        # Generate decision simulation
        try:
            decision = self.model.generate_with_json(
                prompt=f"{persona_prompt}\n\n{decision_prompt}",
                json_schema=decision_schema
            )
            
            return decision
        except Exception as e:
            logger.error(f"Error simulating decision: {e}")
            return {"error": str(e)}
    
    def record_preference(self, category: str, preference: str) -> None:
        """
        Record a personal preference to enhance persona accuracy.
        
        Args:
            category: Category of the preference (e.g., "food", "music", "books")
            preference: The specific preference
        """
        if category not in self.preference_memory:
            self.preference_memory[category] = []
            
        if preference not in self.preference_memory[category]:
            self.preference_memory[category].append(preference)
            logger.info(f"Recorded preference: {category} - {preference}")
    
    def save_persona(self, filepath: str) -> bool:
        """
        Save the current persona configuration to a file.
        
        Args:
            filepath: Path to save the persona data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            persona_data = {
                "traits": [trait.to_dict() for trait in self.traits],
                "thought_patterns": {name: pattern.to_dict() for name, pattern in self.thought_patterns.items()},
                "preference_memory": self.preference_memory,
                "system_prompt": self.system_prompt
            }
            
            with open(filepath, "w") as f:
                json.dump(persona_data, f, indent=2)
                
            logger.info(f"Saved persona data to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving persona data: {e}")
            return False
    
    def load_persona(self, filepath: str) -> bool:
        """
        Load persona configuration from a file.
        
        Args:
            filepath: Path to load the persona data from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, "r") as f:
                persona_data = json.load(f)
            
            # Load traits
            self.traits = [PersonaTrait.from_dict(trait_data) for trait_data in persona_data.get("traits", [])]
            
            # Load thought patterns
            self.thought_patterns = {}
            for name, pattern_data in persona_data.get("thought_patterns", {}).items():
                self.thought_patterns[name] = ThoughtPattern.from_dict(pattern_data)
            
            # Load preferences
            self.preference_memory = persona_data.get("preference_memory", {})
            
            # Load system prompt
            if "system_prompt" in persona_data:
                self.system_prompt = persona_data["system_prompt"]
                
            logger.info(f"Loaded persona data from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading persona data: {e}")
            return False 