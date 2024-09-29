Title: Migrating off ConversationBufferMemory or ConversationStringBufferMemory | 🦜️🔗 LangChain

URL Source: https://python.langchain.com/docs/versions/migrating_memory/conversation_buffer_memory/

Markdown Content:
[ConversationBufferMemory](https://python.langchain.com/api_reference/langchain/memory/langchain.memory.buffer.ConversationBufferMemory.html) and [ConversationStringBufferMemory](https://python.langchain.com/api_reference/langchain/memory/langchain.memory.buffer.ConversationStringBufferMemory.html) were used to keep track of a conversation between a human and an ai asstistant without any additional processing.

note

The `ConversationStringBufferMemory` is equivalent to `ConversationBufferMemory` but was targeting LLMs that were not chat models.

The methods for handling conversation history using existing modern primitives are:

1.  Using [LangGraph persistence](https://langchain-ai.github.io/langgraph/how-tos/persistence/) along with appropriate processing of the message history
2.  Using LCEL with [RunnableWithMessageHistory](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html#) combined with appropriate processing of the message history.

Most users will find [LangGraph persistence](https://langchain-ai.github.io/langgraph/how-tos/persistence/) both easier to use and configure than the equivalent LCEL, especially for more complex use cases.

Set up[​](https://python.langchain.com/docs/versions/migrating_memory/conversation_buffer_memory/#set-up "Direct link to Set up")
---------------------------------------------------------------------------------------------------------------------------------

```
%%capture --no-stderr%pip install --upgrade --quiet langchain-openai langchain
```

```
import osfrom getpass import getpassif "OPENAI_API_KEY" not in os.environ:    os.environ["OPENAI_API_KEY"] = getpass()
```

Usage with LLMChain / ConversationChain[​](https://python.langchain.com/docs/versions/migrating_memory/conversation_buffer_memory/#usage-with-llmchain--conversationchain "Direct link to Usage with LLMChain / ConversationChain")
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

This section shows how to migrate off `ConversationBufferMemory` or `ConversationStringBufferMemory` that's used together with either an `LLMChain` or a `ConversationChain`.

### Legacy[​](https://python.langchain.com/docs/versions/migrating_memory/conversation_buffer_memory/#legacy "Direct link to Legacy")

Below is example usage of `ConversationBufferMemory` with an `LLMChain` or an equivalent `ConversationChain`.

Details

```
from langchain.chains import LLMChainfrom langchain.memory import ConversationBufferMemoryfrom langchain_core.messages import SystemMessagefrom langchain_core.prompts import ChatPromptTemplatefrom langchain_core.prompts.chat import (    ChatPromptTemplate,    HumanMessagePromptTemplate,    MessagesPlaceholder,)from langchain_openai import ChatOpenAIprompt = ChatPromptTemplate(    [        MessagesPlaceholder(variable_name="chat_history"),        HumanMessagePromptTemplate.from_template("{text}"),    ])memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)legacy_chain = LLMChain(    llm=ChatOpenAI(),    prompt=prompt,    memory=memory,)legacy_result = legacy_chain.invoke({"text": "my name is bob"})print(legacy_result)legacy_result = legacy_chain.invoke({"text": "what was my name"})
```

```
{'text': 'Hello Bob! How can I assist you today?', 'chat_history': [HumanMessage(content='my name is bob', additional_kwargs={}, response_metadata={}), AIMessage(content='Hello Bob! How can I assist you today?', additional_kwargs={}, response_metadata={})]}
```

```
'Your name is Bob. How can I assist you today, Bob?'
```

note

Note that there is no support for separating conversation threads in a single memory object

### LangGraph[​](https://python.langchain.com/docs/versions/migrating_memory/conversation_buffer_memory/#langgraph "Direct link to LangGraph")

The example below shows how to use LangGraph to implement a `ConversationChain` or `LLMChain` with `ConversationBufferMemory`.

This example assumes that you're already somewhat familiar with `LangGraph`. If you're not, then please see the [LangGraph Quickstart Guide](https://langchain-ai.github.io/langgraph/tutorials/introduction/) for more details.

`LangGraph` offers a lot of additional functionality (e.g., time-travel and interrupts) and will work well for other more complex (and realistic) architectures.

Details

```
import uuidfrom IPython.display import Image, displayfrom langchain_core.messages import HumanMessagefrom langgraph.checkpoint.memory import MemorySaverfrom langgraph.graph import START, MessagesState, StateGraph# Define a new graphworkflow = StateGraph(state_schema=MessagesState)# Define a chat modelmodel = ChatOpenAI()# Define the function that calls the modeldef call_model(state: MessagesState):    response = model.invoke(state["messages"])    # We return a list, because this will get added to the existing list    return {"messages": response}# Define the two nodes we will cycle betweenworkflow.add_edge(START, "model")workflow.add_node("model", call_model)# Adding memory is straight forward in langgraph!memory = MemorySaver()app = workflow.compile(    checkpointer=memory)# The thread id is a unique key that identifies# this particular conversation.# We'll just generate a random uuid here.# This enables a single application to manage conversations among multiple users.thread_id = uuid.uuid4()config = {"configurable": {"thread_id": thread_id}}input_message = HumanMessage(content="hi! I'm bob")for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):    event["messages"][-1].pretty_print()# Here, let's confirm that the AI remembers our name!input_message = HumanMessage(content="what was my name?")for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):    event["messages"][-1].pretty_print()
```

```
================================[1m Human Message [0m=================================hi! I'm bob==================================[1m Ai Message [0m==================================Hello Bob! How can I assist you today?================================[1m Human Message [0m=================================what was my name?==================================[1m Ai Message [0m==================================Your name is Bob. How can I help you today, Bob?
```

### LCEL RunnableWithMessageHistory[​](https://python.langchain.com/docs/versions/migrating_memory/conversation_buffer_memory/#lcel-runnablewithmessagehistory "Direct link to LCEL RunnableWithMessageHistory")

Alternatively, if you have a simple chain, you can wrap the chat model of the chain within a [RunnableWithMessageHistory](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html).

Please refer to the following [migration guide](https://python.langchain.com/docs/versions/migrating_chains/conversation_chain/) for more information.

Usasge with a pre-built agent[​](https://python.langchain.com/docs/versions/migrating_memory/conversation_buffer_memory/#usasge-with-a-pre-built-agent "Direct link to Usasge with a pre-built agent")
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

This example shows usage of an Agent Executor with a pre-built agent constructed using the [create\_tool\_calling\_agent](https://python.langchain.com/api_reference/langchain/agents/langchain.agents.tool_calling_agent.base.create_tool_calling_agent.html) function.

If you are using one of the [old LangChain pre-built agents](https://python.langchain.com/v0.1/docs/modules/agents/agent_types/), you should be able to replace that code with the new [langgraph pre-built agent](https://langchain-ai.github.io/langgraph/how-tos/create-react-agent/) which leverages native tool calling capabilities of chat models and will likely work better out of the box.

### Legacy Usage[​](https://python.langchain.com/docs/versions/migrating_memory/conversation_buffer_memory/#legacy-usage "Direct link to Legacy Usage")

Details

```
from langchain import hubfrom langchain.agents import AgentExecutor, create_tool_calling_agentfrom langchain.memory import ConversationBufferMemoryfrom langchain_core.tools import toolfrom langchain_openai import ChatOpenAImodel = ChatOpenAI(temperature=0)@tooldef get_user_age(name: str) -> str:    """Use this tool to find the user's age."""    # This is a placeholder for the actual implementation    if "bob" in name.lower():        return "42 years old"    return "41 years old"tools = [get_user_age]prompt = ChatPromptTemplate.from_messages(    [        ("placeholder", "{chat_history}"),        ("human", "{input}"),        ("placeholder", "{agent_scratchpad}"),    ])# Construct the Tools agentagent = create_tool_calling_agent(model, tools, prompt)# Instantiate memorymemory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)# Create an agentagent = create_tool_calling_agent(model, tools, prompt)agent_executor = AgentExecutor(    agent=agent,    tools=tools,    memory=memory,  # Pass the memory to the executor)# Verify that the agent can use toolsprint(agent_executor.invoke({"input": "hi! my name is bob what is my age?"}))print()# Verify that the agent has access to conversation history.# The agent should be able to answer that the user's name is bob.print(agent_executor.invoke({"input": "do you remember my name?"}))
```

```
{'input': 'hi! my name is bob what is my age?', 'chat_history': [HumanMessage(content='hi! my name is bob what is my age?', additional_kwargs={}, response_metadata={}), AIMessage(content='Bob, you are 42 years old.', additional_kwargs={}, response_metadata={})], 'output': 'Bob, you are 42 years old.'}{'input': 'do you remember my name?', 'chat_history': [HumanMessage(content='hi! my name is bob what is my age?', additional_kwargs={}, response_metadata={}), AIMessage(content='Bob, you are 42 years old.', additional_kwargs={}, response_metadata={}), HumanMessage(content='do you remember my name?', additional_kwargs={}, response_metadata={}), AIMessage(content='Yes, your name is Bob.', additional_kwargs={}, response_metadata={})], 'output': 'Yes, your name is Bob.'}
```

### LangGraph[​](https://python.langchain.com/docs/versions/migrating_memory/conversation_buffer_memory/#langgraph-1 "Direct link to LangGraph")

You can follow the standard LangChain tutorial for [building an agent](https://python.langchain.com/docs/tutorials/agents/) an in depth explanation of how this works.

This example is shown here explicitly to make it easier for users to compare the legacy implementation vs. the corresponding langgraph implementation.

This example shows how to add memory to the [pre-built react agent](https://langchain-ai.github.io/langgraph/reference/prebuilt/#create_react_agent) in langgraph.

For more details, please see the [how to add memory to the prebuilt ReAct agent](https://langchain-ai.github.io/langgraph/how-tos/create-react-agent-memory/) guide in langgraph.

Details

```
import uuidfrom langchain_core.messages import HumanMessagefrom langchain_core.tools import toolfrom langchain_openai import ChatOpenAIfrom langgraph.checkpoint.memory import MemorySaverfrom langgraph.prebuilt import create_react_agent@tooldef get_user_age(name: str) -> str:    """Use this tool to find the user's age."""    # This is a placeholder for the actual implementation    if "bob" in name.lower():        return "42 years old"    return "41 years old"memory = MemorySaver()model = ChatOpenAI()app = create_react_agent(    model,    tools=[get_user_age],    checkpointer=memory,)# The thread id is a unique key that identifies# this particular conversation.# We'll just generate a random uuid here.# This enables a single application to manage conversations among multiple users.thread_id = uuid.uuid4()config = {"configurable": {"thread_id": thread_id}}# Tell the AI that our name is Bob, and ask it to use a tool to confirm# that it's capable of working like an agent.input_message = HumanMessage(content="hi! I'm bob. What is my age?")for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):    event["messages"][-1].pretty_print()# Confirm that the chat bot has access to previous conversation# and can respond to the user saying that the user's name is Bob.input_message = HumanMessage(content="do you remember my name?")for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):    event["messages"][-1].pretty_print()
```

```
================================[1m Human Message [0m=================================hi! I'm bob. What is my age?==================================[1m Ai Message [0m==================================Tool Calls:  get_user_age (call_oEDwEbIDNdokwqhAV6Azn47c) Call ID: call_oEDwEbIDNdokwqhAV6Azn47c  Args:    name: bob=================================[1m Tool Message [0m=================================Name: get_user_age42 years old==================================[1m Ai Message [0m==================================Bob, you are 42 years old! If you need any more assistance or information, feel free to ask.================================[1m Human Message [0m=================================do you remember my name?==================================[1m Ai Message [0m==================================Yes, your name is Bob. If you have any other questions or need assistance, feel free to ask!
```

If we use a different thread ID, it'll start a new conversation and the bot will not know our name!

```
config = {"configurable": {"thread_id": "123456789"}}input_message = HumanMessage(content="hi! do you remember my name?")for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):    event["messages"][-1].pretty_print()
```

```
================================[1m Human Message [0m=================================hi! do you remember my name?==================================[1m Ai Message [0m==================================Hello! Yes, I remember your name. It's great to see you again! How can I assist you today?
```

Next steps[​](https://python.langchain.com/docs/versions/migrating_memory/conversation_buffer_memory/#next-steps "Direct link to Next steps")
---------------------------------------------------------------------------------------------------------------------------------------------

Explore persistence with LangGraph:

*   [LangGraph quickstart tutorial](https://langchain-ai.github.io/langgraph/tutorials/introduction/)
*   [How to add persistence ("memory") to your graph](https://langchain-ai.github.io/langgraph/how-tos/persistence/)
*   [How to manage conversation history](https://langchain-ai.github.io/langgraph/how-tos/memory/manage-conversation-history/)
*   [How to add summary of the conversation history](https://langchain-ai.github.io/langgraph/how-tos/memory/add-summary-conversation-history/)

Add persistence with simple LCEL (favor langgraph for more complex use cases):

*   [How to add message history](https://python.langchain.com/docs/how_to/message_history/)

Working with message history:

*   [How to trim messages](https://python.langchain.com/docs/how_to/trim_messages/)
*   [How to filter messages](https://python.langchain.com/docs/how_to/filter_messages/)
*   [How to merge message runs](https://python.langchain.com/docs/how_to/merge_message_runs/)
