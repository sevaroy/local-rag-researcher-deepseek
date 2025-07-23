"""
LineBot 服務模組 - 提供 LINE Bot 核心服務功能
"""

import logging
import json
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from linebot import LineBotApi
from linebot.models import (
    TextSendMessage, FlexSendMessage, MessageEvent, TextMessage,
    FileMessage, PostbackEvent, FollowEvent, UnfollowEvent
)

logger = logging.getLogger(__name__)

# 數據模型
@dataclass
class UserConfig:
    max_search_queries: int = 3
    enable_web_search: bool = False
    preferred_report_format: str = "standard"
    language: str = "zh-TW"
    notification_enabled: bool = True

@dataclass
class ResearchQuery:
    query_id: str
    user_query: str
    generated_queries: List[str]
    status: str
    result: Optional[str] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class UserSession:
    user_id: str
    current_context: str = ""
    research_history: List[ResearchQuery] = None
    last_activity: datetime = None
    config: UserConfig = None
    state: str = "idle"

    def __post_init__(self):
        if self.research_history is None:
            self.research_history = []
        if self.last_activity is None:
            self.last_activity = datetime.now()
        if self.config is None:
            self.config = UserConfig()

# 服務類別
class LineBotHandler:
    """處理 LINE Webhook 請求和驗證"""
    
    def __init__(self, channel_secret: str, channel_access_token: str):
        self.channel_secret = channel_secret
        self.channel_access_token = channel_access_token
        self.message_router = None
    
    def set_message_router(self, router):
        """設置訊息路由器"""
        self.message_router = router
    
    async def handle_webhook(self, request: Request) -> JSONResponse:
        """處理 LINE Webhook 請求"""
        try:
            # 獲取請求內容和簽名
            body = await request.body()
            signature = request.headers.get('X-Line-Signature', '')
            
            # 驗證簽名
            if not await self.verify_signature(body, signature):
                logger.warning("Invalid signature received")
                raise HTTPException(status_code=401, detail="Invalid signature")
            
            # 解析事件
            events = json.loads(body.decode('utf-8')).get('events', [])
            
            # 處理每個事件
            for event in events:
                await self.process_event(event)
            
            return JSONResponse(status_code=200, content={"status": "OK"})
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Webhook handling error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def verify_signature(self, body: bytes, signature: str) -> bool:
        """驗證 LINE Webhook 簽名"""
        if not signature or not self.channel_secret:
            return False
        
        try:
            channel_secret = self.channel_secret.encode('utf-8')
            hash_digest = hmac.new(channel_secret, body, hashlib.sha256).digest()
            expected_signature = base64.b64encode(hash_digest).decode('utf-8')
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    async def process_event(self, event: Dict[str, Any]) -> None:
        """處理 LINE 事件"""
        if not self.message_router:
            logger.error("Message router not set")
            return
        
        event_type = event.get('type')
        
        try:
            if event_type == 'message':
                await self.message_router.route_message(event)
            elif event_type == 'postback':
                await self.message_router.handle_postback(event)
            elif event_type == 'follow':
                await self.message_router.handle_follow(event)
            elif event_type == 'unfollow':
                await self.message_router.handle_unfollow(event)
            else:
                logger.info(f"Unhandled event type: {event_type}")
        except Exception as e:
            logger.error(f"Error processing event: {e}")


class MessageRouter:
    """路由和處理不同類型的 LINE 訊息"""
    
    def __init__(self, line_bot_api: LineBotApi):
        self.line_bot_api = line_bot_api
        self.session_manager = None
        self.research_service = None
        self.file_handler = None
        self.config_service = None
    
    def set_services(self, session_manager=None, research_service=None, 
                    file_handler=None, config_service=None):
        """設置相關服務"""
        self.session_manager = session_manager
        self.research_service = research_service
        self.file_handler = file_handler
        self.config_service = config_service
    
    async def route_message(self, event: Dict[str, Any]) -> None:
        """根據訊息類型路由到不同處理器"""
        message = event.get('message', {})
        message_type = message.get('type')
        
        if message_type == 'text':
            await self.handle_text_message(event)
        elif message_type in ['image', 'file', 'audio', 'video']:
            await self.handle_file_message(event)
        else:
            # 處理其他類型訊息
            user_id = event.get('source', {}).get('userId')
            reply_token = event.get('replyToken')
            if user_id and reply_token:
                self.line_bot_api.reply_message(
                    reply_token,
                    TextSendMessage(text="抱歉，我目前無法處理這種類型的訊息。")
                )
    
    async def handle_text_message(self, event: Dict[str, Any]) -> None:
        """處理文字訊息"""
        message = event.get('message', {})
        text = message.get('text', '')
        user_id = event.get('source', {}).get('userId')
        reply_token = event.get('replyToken')
        
        if not user_id or not reply_token:
            logger.error("Missing user_id or reply_token in event")
            return
        
        # 獲取用戶會話
        session = await self.session_manager.get_session(user_id)
        
        # 處理命令
        if text.startswith('/'):
            await self._handle_command(text, user_id, reply_token, session)
            return
        
        # 處理研究查詢
        if self.research_service:
            # 更新會話狀態
            session.current_context = text
            session.state = "researching"
            await self.session_manager.update_session(user_id, session)
            
            # 發送處理中訊息
            self.line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text="正在處理您的研究查詢，這可能需要一些時間...")
            )
            
            # 非同步處理研究查詢
            try:
                config = asdict(session.config)
                result = await self.research_service.process_research_query(user_id, text, config)
                
                # 分段發送結果（如果結果太長）
                if len(result) > 5000:
                    chunks = [result[i:i+5000] for i in range(0, len(result), 5000)]
                    for i, chunk in enumerate(chunks):
                        prefix = "研究結果 (續):\n\n" if i > 0 else "研究結果:\n\n"
                        self.line_bot_api.push_message(
                            user_id,
                            TextSendMessage(text=f"{prefix}{chunk}")
                        )
                else:
                    self.line_bot_api.push_message(
                        user_id,
                        TextSendMessage(text=f"研究結果:\n\n{result}")
                    )
                
                # 更新會話狀態
                session.state = "idle"
                await self.session_manager.update_session(user_id, session)
                
            except Exception as e:
                logger.error(f"Research processing error: {e}")
                self.line_bot_api.push_message(
                    user_id,
                    TextSendMessage(text="處理您的查詢時發生錯誤，請稍後再試。")
                )
                session.state = "idle"
                await self.session_manager.update_session(user_id, session)
    
    async def _handle_command(self, text: str, user_id: str, reply_token: str, session: UserSession) -> None:
        """處理命令訊息"""
        command = text.lower().split()[0]
        
        if command == '/help':
            self.line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=(
                    "🤖 RAG 研究助手使用說明\n\n"
                    "📝 功能:\n"
                    "• 發送問題進行研究查詢\n"
                    "• 上傳文件進行分析\n"
                    "• 獲得詳細的研究報告\n\n"
                    "💬 命令:\n"
                    "/help - 顯示此幫助訊息\n"
                    "/config - 顯示配置選項\n"
                    "/reset - 重置當前會話\n"
                    "/status - 顯示當前研究狀態\n\n"
                    "試試發送: '台灣AI發展趨勢'"
                ))
            )
        elif command == '/config':
            if self.config_service:
                config = await self.config_service.get_user_config(user_id)
                config_text = (
                    "⚙️ 當前配置:\n\n"
                    f"最大搜索查詢數: {config.max_search_queries}\n"
                    f"啟用網絡搜索: {'是' if config.enable_web_search else '否'}\n"
                    f"首選報告格式: {config.preferred_report_format}\n"
                    f"語言: {config.language}\n"
                    f"通知: {'開啟' if config.notification_enabled else '關閉'}\n\n"
                    "要更改配置，請使用 /config 命令後跟選項和值，例如:\n"
                    "/config web_search on"
                )
                self.line_bot_api.reply_message(reply_token, TextSendMessage(text=config_text))
        elif command == '/reset':
            await self.session_manager.clear_session(user_id)
            self.line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text="您的會話已重置。")
            )
        elif command == '/status':
            status_text = f"當前狀態: {session.state}\n"
            if session.state == "researching":
                status_text += "正在處理您的研究查詢..."
            self.line_bot_api.reply_message(reply_token, TextSendMessage(text=status_text))
        else:
            self.line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=f"未知命令: {command}\n使用 /help 查看可用命令。")
            )
    
    async def handle_file_message(self, event: Dict[str, Any]) -> None:
        """處理文件訊息"""
        if not self.file_handler:
            logger.error("File handler not set")
            return
        
        message = event.get('message', {})
        message_id = message.get('id')
        message_type = message.get('type')
        user_id = event.get('source', {}).get('userId')
        reply_token = event.get('replyToken')
        
        if not user_id or not reply_token or not message_id:
            logger.error("Missing required event data")
            return
        
        # 發送處理中訊息
        self.line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="正在處理您的文件，這可能需要一些時間...")
        )
        
        try:
            # 下載並處理文件
            result = await self.file_handler.process_message(message_id, message_type)
            
            if result:
                self.line_bot_api.push_message(
                    user_id,
                    TextSendMessage(text="文件處理成功！您現在可以查詢與此文件相關的問題。")
                )
            else:
                self.line_bot_api.push_message(
                    user_id,
                    TextSendMessage(text="文件處理失敗。請確保文件格式正確且未超過大小限制。")
                )
        except Exception as e:
            logger.error(f"File processing error: {e}")
            self.line_bot_api.push_message(
                user_id,
                TextSendMessage(text="處理您的文件時發生錯誤，請稍後再試。")
            )
    
    async def handle_postback(self, event: Dict[str, Any]) -> None:
        """處理 Postback 事件"""
        data = event.get('postback', {}).get('data', '')
        user_id = event.get('source', {}).get('userId')
        reply_token = event.get('replyToken')
        
        if not user_id or not reply_token:
            logger.error("Missing user_id or reply_token in event")
            return
        
        # 解析 postback 數據
        try:
            params = dict(item.split('=') for item in data.split('&'))
            action = params.get('action')
            
            if action == 'config':
                # 處理配置更改
                if self.config_service:
                    option = params.get('option')
                    value = params.get('value')
                    
                    if option and value:
                        config = await self.config_service.get_user_config(user_id)
                        
                        if option == 'web_search':
                            config.enable_web_search = value.lower() == 'true'
                        elif option == 'max_queries':
                            config.max_search_queries = int(value)
                        elif option == 'report_format':
                            config.preferred_report_format = value
                        
                        await self.config_service.update_user_config(user_id, config)
                        self.line_bot_api.reply_message(
                            reply_token,
                            TextSendMessage(text=f"配置已更新: {option} = {value}")
                        )
            elif action == 'cancel_research':
                # 取消正在進行的研究
                if self.research_service:
                    cancelled = await self.research_service.cancel_research(user_id)
                    if cancelled:
                        self.line_bot_api.reply_message(
                            reply_token,
                            TextSendMessage(text="研究已取消。")
                        )
                        # 更新會話狀態
                        session = await self.session_manager.get_session(user_id)
                        session.state = "idle"
                        await self.session_manager.update_session(user_id, session)
                    else:
                        self.line_bot_api.reply_message(
                            reply_token,
                            TextSendMessage(text="無法取消研究，可能已經完成或不存在。")
                        )
        except Exception as e:
            logger.error(f"Postback handling error: {e}")
            self.line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text="處理您的請求時發生錯誤，請稍後再試。")
            )
    
    async def handle_follow(self, event: Dict[str, Any]) -> None:
        """處理關注事件"""
        user_id = event.get('source', {}).get('userId')
        reply_token = event.get('replyToken')
        
        if not user_id or not reply_token:
            logger.error("Missing user_id or reply_token in event")
            return
        
        # 發送歡迎訊息
        welcome_message = (
            "👋 歡迎使用 RAG 研究助手！\n\n"
            "我可以幫助您進行深入的研究和分析。您可以：\n"
            "• 發送問題進行研究查詢\n"
            "• 上傳文件進行分析\n"
            "• 獲得詳細的研究報告\n\n"
            "使用 /help 查看更多使用說明。"
        )
        self.line_bot_api.reply_message(reply_token, TextSendMessage(text=welcome_message))
        
        # 創建用戶會話
        if self.session_manager:
            await self.session_manager.get_session(user_id)
    
    async def handle_unfollow(self, event: Dict[str, Any]) -> None:
        """處理取消關注事件"""
        user_id = event.get('source', {}).get('userId')
        
        if not user_id:
            logger.error("Missing user_id in event")
            return
        
        # 清理用戶會話
        if self.session_manager:
            await self.session_manager.clear_session(user_id)
            logger.info(f"User {user_id} unfollowed, session cleared")


class ResearchService:
    """處理研究查詢和結果生成"""
    
    def __init__(self, researcher_graph):
        self.researcher_graph = researcher_graph
        self.active_researches = {}
    
    async def process_research_query(self, user_id: str, query: str, config: Dict[str, Any]) -> str:
        """處理研究查詢"""
        try:
            logger.info(f"Processing research query for user {user_id}: {query}")
            
            # 記錄活動研究
            self.active_researches[user_id] = {
                "query": query,
                "status": "processing",
                "start_time": datetime.now()
            }
            
            # 調用研究圖
            result = await self._invoke_researcher_graph(query, config)
            
            # 更新研究狀態
            self.active_researches[user_id]["status"] = "completed"
            self.active_researches[user_id]["end_time"] = datetime.now()
            
            return result
        except Exception as e:
            logger.error(f"Research query processing error: {e}")
            self.active_researches[user_id]["status"] = "failed"
            self.active_researches[user_id]["error"] = str(e)
            raise
    
    async def _invoke_researcher_graph(self, query: str, config: Dict[str, Any]) -> str:
        """調用研究圖生成結果"""
        try:
            # 準備輸入
            inputs = {
                "user_instructions": query
            }
            
            # 調用研究圖
            result = await self.researcher_graph.ainvoke(inputs, {"configurable": config})
            
            # 返回最終答案
            return result.get("final_answer", "無法生成研究結果。")
        except Exception as e:
            logger.error(f"Error invoking researcher graph: {e}")
            raise
    
    async def get_research_status(self, user_id: str) -> Dict[str, Any]:
        """獲取研究狀態"""
        if user_id in self.active_researches:
            return self.active_researches[user_id]
        return {"status": "not_found"}
    
    async def cancel_research(self, user_id: str) -> bool:
        """取消研究"""
        if user_id in self.active_researches and self.active_researches[user_id]["status"] == "processing":
            self.active_researches[user_id]["status"] = "cancelled"
            return True
        return False


class SessionManager:
    """管理用戶會話和狀態"""
    
    def __init__(self):
        self.sessions = {}
        self.session_expiry = timedelta(hours=24)
    
    async def get_session(self, user_id: str) -> UserSession:
        """獲取用戶會話，如果不存在則創建"""
        if user_id not in self.sessions:
            self.sessions[user_id] = UserSession(user_id=user_id)
        else:
            # 更新最後活動時間
            self.sessions[user_id].last_activity = datetime.now()
        
        return self.sessions[user_id]
    
    async def update_session(self, user_id: str, session: UserSession) -> None:
        """更新用戶會話"""
        session.last_activity = datetime.now()
        self.sessions[user_id] = session
    
    async def clear_session(self, user_id: str) -> None:
        """清除用戶會話"""
        if user_id in self.sessions:
            self.sessions[user_id] = UserSession(user_id=user_id)
    
    async def cleanup_expired_sessions(self) -> int:
        """清理過期會話"""
        now = datetime.now()
        expired_users = [
            user_id for user_id, session in self.sessions.items()
            if now - session.last_activity > self.session_expiry
        ]
        
        for user_id in expired_users:
            del self.sessions[user_id]
        
        return len(expired_users)


class FileHandler:
    """處理文件上傳和處理"""
    
    def __init__(self, line_bot_api: LineBotApi):
        self.line_bot_api = line_bot_api
        self.supported_formats = ['pdf', 'txt', 'docx', 'jpg', 'png']
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    async def process_message(self, message_id: str, message_type: str) -> bool:
        """處理訊息中的文件"""
        try:
            # 下載文件
            file_content = await self.download_file(message_id)
            
            # 根據訊息類型處理文件
            if message_type == 'file':
                # 處理一般文件
                return await self.process_file(file_content, message_id)
            elif message_type == 'image':
                # 處理圖片
                return await self.process_image(file_content, message_id)
            else:
                logger.warning(f"Unsupported message type: {message_type}")
                return False
        except Exception as e:
            logger.error(f"File processing error: {e}")
            return False
    
    async def download_file(self, message_id: str) -> bytes:
        """從 LINE 平台下載文件"""
        try:
            message_content = self.line_bot_api.get_message_content(message_id)
            file_content = bytes()
            for chunk in message_content.iter_content():
                file_content += chunk
            
            # 檢查文件大小
            if len(file_content) > self.max_file_size:
                raise ValueError(f"File size exceeds limit of {self.max_file_size / 1024 / 1024}MB")
            
            return file_content
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            raise
    
    async def process_file(self, file_content: bytes, filename: str) -> bool:
        """處理文件並加入向量資料庫"""
        # 這裡應該整合現有的文件處理和向量化功能
        # 目前僅返回成功，實際實現需要根據現有系統進行整合
        logger.info(f"Processing file: {filename}")
        return True
    
    async def process_image(self, file_content: bytes, filename: str) -> bool:
        """處理圖片並加入向量資料庫"""
        # 這裡應該整合現有的圖片處理和向量化功能
        # 目前僅返回成功，實際實現需要根據現有系統進行整合
        logger.info(f"Processing image: {filename}")
        return True
    
    def get_supported_formats(self) -> List[str]:
        """獲取支援的文件格式"""
        return self.supported_formats


class ConfigurationService:
    """管理用戶配置"""
    
    def __init__(self):
        self.user_configs = {}
    
    async def get_user_config(self, user_id: str) -> UserConfig:
        """獲取用戶配置，如果不存在則返回默認配置"""
        if user_id not in self.user_configs:
            self.user_configs[user_id] = UserConfig()
        return self.user_configs[user_id]
    
    async def update_user_config(self, user_id: str, config: UserConfig) -> None:
        """更新用戶配置"""
        self.user_configs[user_id] = config
    
    async def reset_user_config(self, user_id: str) -> None:
        """重置用戶配置為默認值"""
        self.user_configs[user_id] = UserConfig()
    
    def get_default_config(self) -> UserConfig:
        """獲取默認配置"""
        return UserConfig()
