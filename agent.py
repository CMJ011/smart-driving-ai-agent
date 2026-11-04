import os
from typing import Annotated
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

# 1. 定义工具
@tool
def check_battery() -> str:
    """查询车辆当前的剩余电量。当用户想要导航或询问车辆状态时调用。"""
    return "当前车辆剩余电量为 15%，电量较低。"

# 2. 初始化大模型
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    temperature=0.3
)
llm_with_tools = llm.bind_tools([check_battery])

# 3. 定义状态
class AgentState(dict):
    messages: Annotated[list, add_messages]

# 4. 核心节点
def chatbot(state: AgentState):
    messages = state["messages"]
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content="你是一个专业的智能驾驶助手。如果有工具结果，请结合结果回答。")] + messages
    
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# 5. 构建工作流
workflow = StateGraph(AgentState)
workflow.add_node("chatbot", chatbot)
workflow.add_node("tools", ToolNode(tools=[check_battery]))
workflow.set_entry_point("chatbot")
workflow.add_conditional_edges("chatbot", tools_condition)
workflow.add_edge("tools", "chatbot")

# 编译图（带记忆）
memory = MemorySaver()
agent_app = workflow.compile(checkpointer=memory)

# 6. 普通调用
def run_agent(user_input: str, session_id: str):
    config = {"configurable": {"thread_id": session_id}}
    state = {"messages": [HumanMessage(content=user_input)]}
    result = agent_app.invoke(state, config=config)
    return result["messages"][-1].content

# 7. 流式输出（终极稳定版）
async def run_agent_stream(user_input: str, session_id: str):
    config = {"configurable": {"thread_id": session_id}}
    state = {"messages": [HumanMessage(content=user_input)]}
    
    # 使用 stream_mode="messages" 获取纯净的流式文本
    async for msg_chunk, metadata in agent_app.astream(state, config=config, stream_mode="messages"):
        if msg_chunk.content:
            yield msg_chunk.content