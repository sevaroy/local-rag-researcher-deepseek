"""
簡化版 LINE Bot 實現
"""

import os
import json
import hashlib
import hmac
import base64
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from linebot import LineBotApi
from linebot.models import TextSendMessage

# 初始化 FastAPI 應用
app = FastAPI()

# 環境變數
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")

# 初始化 LINE Bot API
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN) if LINE_CHANNEL_ACCESS_TOKEN else None


def verify_signature(body: bytes, signature: str) -> bool:
    """驗證 LINE webhook 簽名"""
    if not signature or not LINE_CHANNEL_SECRET:
        return False
    
    try:
        channel_secret = LINE_CHANNEL_SECRET.encode('utf-8')
        hash_digest = hmac.new(channel_secret, body, hashlib.sha256).digest()
        expected_signature = base64.b64encode(hash_digest).decode('utf-8')
        return hmac.compare_digest(signature, expected_signature)
    except Exception:
        return False


@app.get("/")
async def root():
    """健康檢查端點"""
    return {"message": "LINE Bot 正在運行中", "status": "OK"}


@app.post("/webhook")
async def webhook(request: Request):
    """LINE Bot webhook 端點"""
    try:
        # 取得請求內容和簽名
        body = await request.body()
        signature = request.headers.get('X-Line-Signature', '')
        
        # 驗證簽名
        if not verify_signature(body, signature):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # 解析事件
        body_json = json.loads(body.decode('utf-8'))
        events = body_json.get('events', [])
        
        # 處理每個事件
        for event in events:
            await process_event(event)
        
        return JSONResponse(status_code=200, content={"status": "OK"})
        
    except Exception as e:
        print(f"Webhook 處理錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_event(event):
    """處理 LINE 事件"""
    if not line_bot_api:
        print("LINE Bot API 未初始化")
        return
    
    event_type = event.get('type')
    
    if event_type == 'message':
        message = event.get('message', {})
        message_type = message.get('type')
        reply_token = event.get('replyToken')
        
        if message_type == 'text':
            user_message = message.get('text', '')
            
            # 簡單的回覆邏輯
            if user_message.lower() in ['hi', 'hello', '你好']:
                reply_text = "您好！歡迎使用 RAG 研究助手 LINE Bot！\n\n請直接發送您想研究的問題，我會為您提供詳細的分析報告。"
            elif user_message.lower() in ['help', '說明', '幫助']:
                reply_text = "🤖 RAG 研究助手使用說明\n\n📝 功能:\n• 發送問題進行研究查詢\n• 上傳文件進行分析\n• 獲得詳細的研究報告\n\n💬 試試發送: '台灣AI發展趨勢'"
            else:
                reply_text = f"收到您的查詢: {user_message}\n\n這是一個簡化版實現。完整的 RAG 研究功能正在開發中，敬請期待！"
            
            # 發送回覆
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=reply_text)
            )


if __name__ == "__main__":
    if not LINE_CHANNEL_SECRET or not LINE_CHANNEL_ACCESS_TOKEN:
        print("請設定 LINE_CHANNEL_SECRET 和 LINE_CHANNEL_ACCESS_TOKEN 環境變數")
    else:
        import uvicorn
        uvicorn.run("simple_linebot:app", host="0.0.0.0", port=8000, reload=True)