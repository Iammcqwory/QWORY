# Google ADK Integration for Qwory

This package provides integration between the Qwory framework and Google's Agent Development Kit (ADK), allowing Qwory developers to leverage ADK's robust agent architecture, tool ecosystem, and deployment options.

## Overview

The ADK integration package provides adapter classes that bridge between Qwory's architecture and ADK's components, enabling bidirectional interoperability:

- Use ADK agents within Qwory
- Use Qwory agents within ADK
- Leverage ADK models with Qwory's model interface
- Use Qwory tools with ADK agents and vice versa

## Installation

1. First, install the Google ADK package:

```bash
pip install google-adk
```

2. The Qwory integration is included in the main Qwory package.

## Usage Examples

### Using an ADK Agent in Qwory

```python
from qwory.integrations.adk.agent_adapter import ADKAgentAdapter, create_adk_llm_agent
from qwory.integrations.adk.model_adapter import create_google_llm_adapter

# Create an ADK model via the adapter
adk_model = create_google_llm_adapter(
    model_name="gemini-pro",
    api_key="YOUR_GOOGLE_API_KEY"
)

# Create an ADK agent
adk_agent = create_adk_llm_agent(
    model=adk_model,
    system_prompt="You are a helpful AI assistant.",
    tools=[]
)

# Wrap the ADK agent with the Qwory adapter
qwory_agent = ADKAgentAdapter(
    adk_agent=adk_agent,
    name="adk-example-agent"
)

# Use the agent through Qwory's interface
response = qwory_agent.process("What's the weather in New York today?")
print(response['content'])
```

### Using Qwory Tools with ADK

```python
from qwory.tools import SearchTool, FileAccessTool
from qwory.integrations.adk.tool_adapter import register_qwory_tools_with_adk

# Create Qwory tools
search_tool = SearchTool()
file_tool = FileAccessTool(base_path="./data")

# Register Qwory tools with ADK
adk_tools = register_qwory_tools_with_adk([search_tool, file_tool])

# Now you can use these tools with ADK agents
adk_agent = create_adk_llm_agent(
    model=adk_model,
    system_prompt="You are a helpful AI assistant.",
    tools=adk_tools
)
```

### Using ADK Models in Qwory

```python
from qwory.integrations.adk.model_adapter import create_anthropic_llm_adapter
from qwory.agents import SingleAgent

# Create an ADK model adapter
adk_model = create_anthropic_llm_adapter(
    model_name="claude-3-opus",
    api_key="YOUR_ANTHROPIC_API_KEY"
)

# Use the ADK model with a standard Qwory agent
agent = SingleAgent(
    model=adk_model,
    tools=[SearchTool()],
    config={
        "system_prompt": "You are a helpful AI assistant."
    }
)

response = agent.process("Tell me about quantum computing.")
print(response['content'])
```

## Advanced Features

### Deploying to Google Cloud

The ADK integration enables deployment of Qwory agents to Google Cloud services:

```python
# This is a placeholder example - actual implementation may vary
from qwory.integrations.adk.deployment import deploy_to_vertex_ai

# Deploy a Qwory agent to Vertex AI
deploy_to_vertex_ai(
    agent_class="my_package.MyAgent",
    project_id="my-google-cloud-project",
    region="us-central1"
)
```

### Using LangGraph for Complex Workflows

ADK's LangGraph integration enables complex agent workflows:

```python
# This is a placeholder example - actual implementation may vary
from qwory.integrations.adk.langgraph_agent import QworyLanggraphAgent

# Define a graph workflow
graph_definition = {
    "nodes": [...],
    "edges": [...]
}

# Create a LangGraph agent
agent = QworyLanggraphAgent(graph_definition)

# Use the agent
response = agent.process("Analyze this data and create a visualization.")
```

## Compatibility Notes

- The ADK integration is designed to be compatible with Qwory's existing architecture
- All adapter classes maintain the same interfaces as their native counterparts
- Existing Qwory code will continue to work without modification

## Requirements

- Python 3.9+
- google-adk package
- Qwory framework

## Further Documentation

For more detailed information, see the following resources:

- [ADK Integration Plan](../../docs/ADK_INTEGRATION_PLAN.md)
- [Example Code](../../examples/adk_integration_example.py)
- [Google ADK Documentation](https://github.com/google/agent-development-kit-python)