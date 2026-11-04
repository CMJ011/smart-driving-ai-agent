import os
from typing import Annotated
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

# ================= 1. 定义完整的“技能矩阵”工具 =================

@tool
def control_ac(action: str, temperature: int = None) -> str:
    """控制空调系统。action 可以是 'on'（打开）, 'off'（关闭）, 'temp_up'（调高温度）, 'temp_down'（调低温度）。temperature 可选，用于设定具体温度，如 22。"""
    if action == "on":
        return "【执行成功】：空调已打开，设定温度为22℃。"
    elif action == "off":
        return "【执行成功】：空调已关闭。"
    elif action == "temp_up":
        return "【执行成功】：空调温度已调高。"
    elif action == "temp_down":
        return "【执行成功】：空调温度已调低。"
    return "【执行失败】：不支持的空调操作。"

@tool
def control_media(action: str, query: str = None) -> str:
    """控制媒体娱乐系统。action 可以是 'play'（播放）, 'pause'（暂停）, 'next'（下一首）, 'prev'（上一首）。query 可选，用于指定要播放的歌曲或歌手，如 '周杰伦'。"""
    if action == "play":
        if query:
            return f"【执行成功】：正在为您播放 {query} 的音乐。"
        return "【执行成功】：音乐已开始播放。"
    elif action == "pause":
        return "【执行成功】：音乐已暂停。"
    elif action == "next":
        return "【执行成功】：已切换到下一首。"
    elif action == "prev":
        return "【执行成功】：已切换到上一首。"
    return "【执行失败】：不支持的媒体操作。"

@tool
def control_body(target: str, action: str, level: str = "full") -> str:
    """控制车身与门窗。target 可以是 'window'（车窗）, 'sunroof'（天窗）, 'trunk'（后备箱）, 'door'（车门）。action 可以是 'open'（打开）, 'close'（关闭）。level 可选，用于控制开合程度，如 'half'（一半）, 'full'（全开）。"""
    if target == "window" and action == "open":
        return f"【执行成功】：车窗已打开（{'一半' if level == 'half' else '全开'}）。"
    elif target == "trunk" and action == "open":
        return "【执行成功】：后备箱已打开。"
    elif target == "sunroof" and action == "close":
        return "【执行成功】：天窗已关闭。"
    return f"【执行成功】：{target} 已 {action}。"

@tool
def control_seat(target: str, action: str) -> str:
    """控制座椅功能。target 可以是 'driver'（主驾）, 'passenger'（副驾）。action 可以是 'heat_on'（加热开）, 'heat_off'（加热关）, 'ventilate_on'（通风开）, 'massage_on'（按摩开）, 'recline'（躺平）。"""
    return f"【执行成功】：{target} 座椅的 {action} 指令已执行。"

@tool
def navigate_to(destination: str) -> str:
    """导航到指定目的地。destination 是目的地名称，如 '公司', '机场', '深圳北站'。"""
    return f"【执行成功】：已为您规划前往 {destination} 的路线，当前路况良好。"

@tool
def get_vehicle_status(item: str) -> str:
    """查询车辆状态。item 可以是 'battery'（电量）, 'tire_pressure'（胎压）, 'range'（续航）, 'mileage'（里程）。"""
    if item == "battery":
        return "当前车辆剩余电量为 15%，电量较低。"
    elif item == "tire_pressure":
        return "当前四轮胎压均在正常范围（2.5 bar）。"
    elif item == "range":
        return "当前表显剩余续航为 80 公里。"
    elif item == "mileage":
        return "当前总里程 15000 公里。"
    return "未能获取该车辆状态信息。"

@tool
def set_scene_mode(mode: str) -> str:
    """启动特定的车辆情景模式。mode 可以是 'camping'（露营模式）, 'rest'（休息模式）, 'pet'（宠物模式）。"""
    return f"【执行成功】：已切换至 {mode} 模式。"

@tool
def control_light(target: str, action: str) -> str:
    """控制灯光系统。target 可以是 'ambient'（氛围灯）, 'reading'（阅读灯）。action 可以是 'on'（开）, 'off'（关）。"""
    return f"【执行成功】：{target} 已 {action}。"

@tool
def control_system(action: str) -> str:
    """控制车机系统。action 可以是 'go_home'（返回桌面）, 'open_settings'（打开设置）, 'open_camera'（打开全景影像）。"""
    return f"【执行成功】：系统已执行 {action}。"

@tool
def control_speed(target_speed: int) -> str:
    """控制车速。target_speed 是目标速度值（km/h），例如 90。用于定速巡航或调整车速。"""
    if target_speed == 0:
        return "【执行成功】：已发送停车指令，车辆正在减速。"
    return f"【执行成功】：已设定定速巡航速度为 {target_speed} km/h。"

# ================= 2. 初始化与绑定工具 =================
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    temperature=0.3
)

# 将所有工具注册给大模型
all_tools = [
    control_ac, control_media, control_body, control_seat, 
    navigate_to, get_vehicle_status, set_scene_mode, 
    control_light, control_system, control_speed
]
llm_with_tools = llm.bind_tools(all_tools)

# ================= 3. 状态与节点定义 =================
class AgentState(dict):
    messages: Annotated[list, add_messages]

def chatbot(state: AgentState):
    messages = state["messages"]
    if not any(isinstance(m, SystemMessage) for m in messages):
        sys_prompt = """你是一个全能的智能座舱 AI 助手，可以控制车辆的各项功能。
        请根据用户的指令，从可用工具中选择合适的一个或多个进行调用。
        如果用户的指令包含多个意图（例如：“打开空调、播放音乐并导航去公司”），请同时调用多个对应的工具。
        执行后，请用自然语言确认你的操作。"""
        messages = [SystemMessage(content=sys_prompt)] + messages
    
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# ================= 4. 构建工作流 =================
workflow = StateGraph(AgentState)
workflow.add_node("chatbot", chatbot)
workflow.add_node("tools", ToolNode(tools=all_tools))
workflow.set_entry_point("chatbot")
workflow.add_conditional_edges("chatbot", tools_condition)
workflow.add_edge("tools", "chatbot")

memory = MemorySaver()
agent_app = workflow.compile(checkpointer=memory)

# ================= 5. 对外调用函数 =================
def run_agent(user_input: str, session_id: str):
    config = {"configurable": {"thread_id": session_id}}
    state = {"messages": [HumanMessage(content=user_input)]}
    result = agent_app.invoke(state, config=config)
    return result["messages"][-1].content

async def run_agent_stream(user_input: str, session_id: str):
    config = {"configurable": {"thread_id": session_id}}
    state = {"messages": [HumanMessage(content=user_input)]}
    async for msg_chunk, metadata in agent_app.astream(state, config=config, stream_mode="messages"):
        if msg_chunk.content:
            yield msg_chunk.content