# 🚗 智能驾驶 AI 助手 (Smart Driving AI Agent)

一个基于 LangGraph 和多 Agent 架构的车载 AI 应用，专为智能座舱场景设计。

## 🌟 核心功能
- **意图识别与工具调用**：基于 LangGraph 构建 StateGraph，大模型可根据用户输入自动决策，调用“车辆电量查询”等外部工具。
- **多轮记忆管理**：利用 MemorySaver 实现按 `session_id` 隔离的多轮对话记忆，用户可进行连续追问。
- **流式输出体验**：基于 FastAPI SSE 技术，实现类似 ChatGPT 的打字机流式响应，首字延迟极低。
- **全栈交互**：提供原生响应式前端界面，无缝对接后端 API。

## 🛠️ 技术栈
- **后端**：Python, FastAPI, Uvicorn
- **AI 编排**：LangGraph, LangChain, DeepSeek API (兼容 OpenAI SDK)
- **前端**：HTML5, CSS3, 原生 JavaScript (Fetch API / EventStream)

## 🚀 快速启动
1. 克隆项目并创建虚拟环境：
   `python -m venv venv`
   `venv\Scripts\activate` (Windows)
2. 安装依赖：
   `pip install fastapi uvicorn langchain langgraph langchain-openai python-dotenv`
3. 配置 API Key：
   复制 `.env.example` 为 `.env`，并填入你的 DeepSeek API Key。
4. 启动后端服务：
   `uvicorn main:app --reload`
5. 运行前端：
   直接用浏览器打开 `index.html` 即可。

## 📸 效果展示
*(这里可以把你刚才截图的笑话或者去机场的截图贴进来)*