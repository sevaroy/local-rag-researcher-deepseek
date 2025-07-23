# Local RAG Researcher with DeepSeek R1 & LangGraph - 系統架構

## 1. 系統概述

這個專案是一個本地自適應RAG（檢索增強生成）研究助手系統，使用LangGraph和DeepSeek R1模型構建。系統能夠根據用戶指令自動生成研究問題，檢索相關文檔，評估文檔相關性，必要時進行網絡搜索，並最終生成結構化的研究報告。

## 2. 架構設計

### 2.1 整體架構

該系統採用單體應用架構，使用Streamlit作為前端界面和應用程序框架，所有組件在同一個Python環境中運行。

```
+----------------------------------+
|           Streamlit UI           |
+----------------------------------+
               |
+----------------------------------+
|         LangGraph Engine         |
|                                  |
|  +-------------+  +------------+ |
|  | Researcher  |  | Query      | |
|  | Graph       |  | Subgraph   | |
|  +-------------+  +------------+ |
+----------------------------------+
               |
+----------------------------------+
|        Service Components        |
|                                  |
| +----------+  +----------------+ |
| | ChromaDB |  | Ollama/DeepSeek| |
| +----------+  +----------------+ |
|                                  |
| +----------+  +----------------+ |
| | HuggingFace| | Tavily API    | |
| | Embeddings|  | (可選)        | |
| +----------+  +----------------+ |
+----------------------------------+
```

### 2.2 主要組件

#### 2.2.1 用戶界面層 (Streamlit)
- 提供研究設置配置界面
- 文件上傳和處理功能
- 聊天式交互界面
- 研究過程可視化和結果展示

#### 2.2.2 核心處理層 (LangGraph)
- **主研究者圖 (Researcher Graph)**：控制整體研究流程
- **查詢子圖 (Query Subgraph)**：處理單個研究查詢的檢索和評估
- **狀態管理**：使用ResearcherState和QuerySearchState管理流程狀態

#### 2.2.3 服務組件層
- **向量數據庫 (ChromaDB)**：存儲和檢索文檔向量
- **本地LLM (Ollama/DeepSeek R1)**：處理自然語言理解和生成
- **嵌入模型 (HuggingFace Embeddings)**：生成文本嵌入向量
- **網絡搜索 (Tavily API)**：提供網絡搜索功能（可選）

## 3. 數據流程

### 3.1 研究流程
1. 用戶輸入研究指令
2. 系統生成研究查詢集
3. 對每個查詢批次進行處理：
   - 從向量數據庫檢索相關文檔
   - 評估文檔相關性
   - 如果相關，總結文檔內容
   - 如果不相關且啟用網絡搜索，進行網絡搜索並總結結果
4. 收集所有查詢的總結
5. 生成最終研究報告

### 3.2 文檔處理流程
1. 用戶上傳文檔
2. 系統處理文檔（根據文件類型選擇適當的加載器）
3. 使用語義分塊器將文檔分割成塊
4. 使用遞歸字符分割器進一步優化塊大小
5. 生成文本嵌入向量
6. 存儲到ChromaDB向量數據庫

## 4. 模塊結構

### 4.1 主要文件和模塊
- **app.py**: 應用程序入口點和Streamlit UI定義
- **run_researcher.py**: 命令行研究者執行腳本
- **src/assistant/graph.py**: LangGraph研究者圖定義
- **src/assistant/prompts.py**: 系統提示詞模板
- **src/assistant/vector_db.py**: 向量數據庫操作
- **src/assistant/utils.py**: 工具函數和輔助方法
- **src/assistant/state.py**: 狀態類型定義
- **report_structures/**: 報告模板目錄

### 4.2 關鍵類和函數
- **researcher**: 編譯後的LangGraph研究者圖
- **query_search_subgraph**: 處理單個查詢的子圖
- **generate_research_queries**: 生成研究查詢
- **retrieve_rag_documents**: 檢索相關文檔
- **evaluate_retrieved_documents**: 評估文檔相關性
- **summarize_query_research**: 總結查詢研究結果
- **generate_final_answer**: 生成最終報告

## 5. 技術棧

- **Python**: 主要編程語言
- **Streamlit**: UI框架
- **LangGraph**: AI代理和工作流定義
- **ChromaDB**: 向量數據庫
- **Ollama**: 本地LLM運行環境
- **DeepSeek R1**: 大型語言模型
- **HuggingFace Embeddings**: 文本嵌入模型
- **Tavily API**: 網絡搜索服務（可選）

## 6. 擴展性和自定義

### 6.1 報告結構自定義
- 通過修改report_structures目錄中的Markdown文件自定義報告格式
- 在UI中選擇不同的報告結構

### 6.2 LLM提供者切換
- 可以在graph.py中切換使用本地Ollama模型或外部LLM提供者
- 支持通過OpenRouter使用多種雲端LLM（如GPT-4o、Claude等）

### 6.3 搜索配置
- 可配置最大搜索查詢數量
- 可啟用或禁用網絡搜索功能

## 7. 部署要求

- Python 3.9+
- Ollama（用於運行本地DeepSeek R1模型）
- Tavily API密鑰（可選，用於網絡搜索）
- 足夠的系統資源運行本地LLM（取決於所選模型大小）