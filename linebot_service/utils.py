"""
LineBot 工具模組 - 提供輔助功能和工具類
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ErrorResponse:
    """錯誤回應格式"""
    error_code: str
    error_message: str
    user_message: str
    suggested_actions: list[str]
    retry_after: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "error": {
                "code": self.error_code,
                "message": self.error_message,
                "user_message": self.user_message,
                "suggested_actions": self.suggested_actions,
                "retry_after": self.retry_after
            }
        }


class ErrorResponseFactory:
    """錯誤回應工廠，用於生成標準化錯誤回應"""
    
    @staticmethod
    def invalid_signature() -> ErrorResponse:
        """生成簽名無效的錯誤回應"""
        return ErrorResponse(
            error_code="INVALID_SIGNATURE",
            error_message="Invalid LINE signature",
            user_message="無法驗證請求來源",
            suggested_actions=["檢查 Channel Secret 設定"]
        )
    
    @staticmethod
    def invalid_request() -> ErrorResponse:
        """生成請求無效的錯誤回應"""
        return ErrorResponse(
            error_code="INVALID_REQUEST",
            error_message="Invalid request format",
            user_message="請求格式無效",
            suggested_actions=["檢查請求格式"]
        )
    
    @staticmethod
    def service_unavailable() -> ErrorResponse:
        """生成服務不可用的錯誤回應"""
        return ErrorResponse(
            error_code="SERVICE_UNAVAILABLE",
            error_message="Service temporarily unavailable",
            user_message="服務暫時不可用，請稍後再試",
            suggested_actions=["稍後重試"],
            retry_after=60
        )
    
    @staticmethod
    def file_too_large() -> ErrorResponse:
        """生成文件過大的錯誤回應"""
        return ErrorResponse(
            error_code="FILE_TOO_LARGE",
            error_message="File size exceeds limit",
            user_message="文件大小超過限制",
            suggested_actions=["減小文件大小", "分割文件"]
        )
    
    @staticmethod
    def unsupported_file_format() -> ErrorResponse:
        """生成不支援的文件格式錯誤回應"""
        return ErrorResponse(
            error_code="UNSUPPORTED_FORMAT",
            error_message="Unsupported file format",
            user_message="不支援的文件格式",
            suggested_actions=["使用支援的文件格式"]
        )
    
    @staticmethod
    def research_error() -> ErrorResponse:
        """生成研究錯誤的錯誤回應"""
        return ErrorResponse(
            error_code="RESEARCH_ERROR",
            error_message="Error processing research query",
            user_message="處理研究查詢時發生錯誤",
            suggested_actions=["簡化查詢", "稍後重試"]
        )


class MessageFormatter:
    """訊息格式化工具，用於將不同格式的訊息轉換為 LINE 訊息格式"""
    
    @staticmethod
    def format_research_result(result: str, max_length: int = 5000) -> list[str]:
        """格式化研究結果，分割長文本"""
        if len(result) <= max_length:
            return [f"研究結果:\n\n{result}"]
        
        # 分割長文本
        chunks = []
        for i in range(0, len(result), max_length):
            chunk = result[i:i+max_length]
            prefix = "研究結果 (續):\n\n" if i > 0 else "研究結果:\n\n"
            chunks.append(f"{prefix}{chunk}")
        
        return chunks
    
    @staticmethod
    def markdown_to_line(markdown_text: str) -> str:
        """將 Markdown 格式轉換為 LINE 支援的格式"""
        # 簡單的 Markdown 轉換，可以根據需要擴展
        text = markdown_text
        
        # 粗體
        import re
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'__(.*?)__', r'\1', text)
        
        # 斜體
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'_(.*?)_', r'\1', text)
        
        # 標題
        text = re.sub(r'^# (.*?)$', r'\1\n', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.*?)$', r'\1\n', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.*?)$', r'\1\n', text, flags=re.MULTILINE)
        
        # 列表
        text = re.sub(r'^\* (.*?)$', r'• \1', text, flags=re.MULTILINE)
        text = re.sub(r'^- (.*?)$', r'• \1', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+\. (.*?)$', r'• \1', text, flags=re.MULTILINE)
        
        return text


class FlexMessageTemplates:
    """Flex Message 模板，用於生成各種 LINE Flex Message"""
    
    @staticmethod
    def welcome_message() -> Dict[str, Any]:
        """歡迎訊息模板"""
        return {
            "type": "flex",
            "altText": "歡迎使用 RAG 研究助手",
            "contents": {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://via.placeholder.com/1000x400?text=RAG+Research+Assistant",
                    "size": "full",
                    "aspectRatio": "20:8",
                    "aspectMode": "cover"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": "歡迎使用 RAG 研究助手",
                            "size": "xl",
                            "weight": "bold"
                        },
                        {
                            "type": "text",
                            "text": "我可以幫助您進行深入的研究和分析。您可以發送問題進行研究查詢，上傳文件進行分析，獲得詳細的研究報告。",
                            "wrap": True
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "開始使用",
                                "text": "/help"
                            },
                            "style": "primary"
                        }
                    ]
                }
            }
        }
    
    @staticmethod
    def help_message() -> Dict[str, Any]:
        """幫助訊息模板"""
        return {
            "type": "flex",
            "altText": "RAG 研究助手使用說明",
            "contents": {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": "RAG 研究助手使用說明",
                            "size": "xl",
                            "weight": "bold"
                        },
                        {
                            "type": "text",
                            "text": "功能:",
                            "weight": "bold"
                        },
                        {
                            "type": "text",
                            "text": "• 發送問題進行研究查詢\n• 上傳文件進行分析\n• 獲得詳細的研究報告",
                            "wrap": True
                        },
                        {
                            "type": "text",
                            "text": "命令:",
                            "weight": "bold"
                        },
                        {
                            "type": "text",
                            "text": "/help - 顯示此幫助訊息\n/config - 顯示配置選項\n/reset - 重置當前會話\n/status - 顯示當前研究狀態",
                            "wrap": True
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "查看配置",
                                "text": "/config"
                            }
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "試試範例",
                                "text": "台灣AI發展趨勢"
                            },
                            "style": "primary",
                            "margin": "md"
                        }
                    ]
                }
            }
        }
    
    @staticmethod
    def config_menu() -> Dict[str, Any]:
        """配置選單模板"""
        return {
            "type": "flex",
            "altText": "配置選單",
            "contents": {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": "配置選單",
                            "size": "xl",
                            "weight": "bold"
                        },
                        {
                            "type": "separator"
                        },
                        {
                            "type": "text",
                            "text": "網絡搜索",
                            "weight": "bold"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "postback",
                                        "label": "開啟",
                                        "data": "action=config&option=web_search&value=true"
                                    },
                                    "height": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "postback",
                                        "label": "關閉",
                                        "data": "action=config&option=web_search&value=false"
                                    },
                                    "height": "sm"
                                }
                            ]
                        },
                        {
                            "type": "separator"
                        },
                        {
                            "type": "text",
                            "text": "最大搜索查詢數",
                            "weight": "bold"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "postback",
                                        "label": "2",
                                        "data": "action=config&option=max_queries&value=2"
                                    },
                                    "height": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "postback",
                                        "label": "3",
                                        "data": "action=config&option=max_queries&value=3"
                                    },
                                    "height": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "postback",
                                        "label": "5",
                                        "data": "action=config&option=max_queries&value=5"
                                    },
                                    "height": "sm"
                                }
                            ]
                        },
                        {
                            "type": "separator"
                        },
                        {
                            "type": "text",
                            "text": "報告格式",
                            "weight": "bold"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "postback",
                                        "label": "標準",
                                        "data": "action=config&option=report_format&value=standard"
                                    },
                                    "height": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "postback",
                                        "label": "學術",
                                        "data": "action=config&option=report_format&value=academic"
                                    },
                                    "height": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "postback",
                                        "label": "簡潔",
                                        "data": "action=config&option=report_format&value=concise"
                                    },
                                    "height": "sm"
                                }
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "重置配置",
                                "text": "/config reset"
                            }
                        }
                    ]
                }
            }
        }
    
    @staticmethod
    def research_progress(progress: int) -> Dict[str, Any]:
        """研究進度模板"""
        return {
            "type": "flex",
            "altText": f"研究進度: {progress}%",
            "contents": {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": "研究進度",
                            "size": "xl",
                            "weight": "bold"
                        },
                        {
                            "type": "text",
                            "text": f"{progress}% 完成"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "filler"
                                        }
                                    ],
                                    "width": f"{progress}%",
                                    "backgroundColor": "#0D8186",
                                    "height": "6px"
                                }
                            ],
                            "backgroundColor": "#9FD8E36E",
                            "height": "6px"
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "postback",
                                "label": "取消研究",
                                "data": "action=cancel_research"
                            }
                        }
                    ]
                }
            }
        }
