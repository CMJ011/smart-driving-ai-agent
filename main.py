from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import os

from agent import run_agent, run_agent_stream

app = FastAPI()

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据格式
class UserMessage(BaseModel):
    text: str
    session_id: str = "default_user"

# 根路径测试
@app.get("/")
def read_root():
    return {"message": "欢迎来到智能驾驶AI系统！", "status": "后端服务已成功启动"}

# 普通接口
@app.post("/chat")
def chat_with_ai(message: UserMessage):
    reply = run_agent(message.text, message.session_id)
    return {"reply": reply}

# 流式接口
@app.post("/chat_stream")
async def chat_stream(message: UserMessage):
    async def event_generator():
        try:
            async for chunk in run_agent_stream(message.text, message.session_id):
                # 封装成标准 SSE 格式
                data = json.dumps({"text": chunk}, ensure_ascii=False)
                yield f"data: {data}\n\n"
        except Exception as e:
            print(f"⚠️ 后端报错: {e}")
            # 修复了 f-string 的语法报错，把 json.dumps 提出来
            error_msg = json.dumps({"text": "\n[系统提示] 出现网络或内部错误"}, ensure_ascii=False)
            yield f"data: {error_msg}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )