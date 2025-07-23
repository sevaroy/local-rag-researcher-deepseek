# 🚀 **本地 RAG 研究助手 ft. DeepSeek R1 & LangGraph**

### 👉 **[完整教學指南看這裡！從零開始打造你專屬的本地 RAG 研究助手](https://dev.to/kaymen99/build-your-own-local-rag-researcher-with-deepseek-r1-11m) 🚀**

我們打造了一個超強的**本地自適應 RAG 研究智慧體**，使用 **LangGraph** 搭配在 **Ollama** 上運行的 **DeepSeek R1** 模型。這個 AI 助手就像個專業研究員，能根據你的需求收集、分析並總結資訊，現在還加上了 **LINE Bot 整合**！

<div align="center">
  <img src="https://github.com/user-attachments/assets/5dc34341-3a2f-461c-b66d-46b134fe5bd9" alt="本地 RAG 研究助手 with LangGraph & DeepSeek 展示">
</div>

## **🤖 怎麼運作的？** 

這套系統的工作流程超級聰明：

1. **📝 生成研究查詢** – AI 會把你的問題拆解成好幾個具體的研究方向，確保能找到最有用的資訊

2. **🔍 檢索相關文件** – 從本地的 **Chroma 向量資料庫**搜尋跟你問題相關的文件

3. **✅ 評估相關性** – 每份找到的文件都會被仔細檢查，確保內容真的對你有幫助

4. **🌐 擴展搜尋範圍** – 如果本地文件不夠豐富，系統會自動**上網搜尋**更多資料來源

5. **📊 整理重點發現** – 把收集到的所有資料進行分析，萃取出關鍵洞察

6. **📋 產出最終報告** – 由專門的**寫作智慧體**把所有發現整理成**結構完整、格式漂亮的研究報告**

這個系統讓研究過程變得**高效又聰明**，確保產出高品質且相關的內容，同時避免無用資訊的干擾。

## **✨ 主要特色功能**  

- **📁 智慧本地文件搜尋** – 快速從你的內部資料庫找到相關資訊
- **🧠 深度洞察萃取** – 運用 **DeepSeek R1** 的強大推理能力來評估、分析並提取最有價值的見解
- **🔗 即時網路搜尋** – 透過 **[Tavily API](https://tavily.com/)** 擴展搜尋範圍，當本地資料不足時自動上網找資料
- **📄 結構化報告生成** – 根據你預設的報告模板產生格式完整的專業報告
- **💬 LINE Bot 整合** – 透過 LINE 聊天介面輕鬆使用，隨時隨地進行研究查詢
- **🔧 彈性配置** – 支援多種報告格式和研究參數客製化

## **🎯 LINE Bot 新功能**

現在你可以直接透過 LINE 使用這個研究助手！

### 📱 支援功能
- **文字查詢** - 直接發送問題就能獲得詳細研究報告
- **文件上傳** - 支援 PDF、圖片、文字檔案上傳分析
- **智慧設定** - 可調整查詢數量、報告格式等參數
- **會話記憶** - 保持對話上下文，支援多輪互動
- **即時回饋** - 顯示研究進度和狀態更新

### 🎮 LINE 指令清單
| 指令 | 功能說明 |
|------|----------|
| `你好`、`hi`、`hello` | 歡迎訊息和使用說明 |
| `說明`、`help`、`幫助` | 詳細功能介紹 |
| `設定`、`config` | 開啟參數設定選單 |
| `清除`、`重置` | 清空對話記錄 |
| `狀態`、`status` | 查看目前研究狀態 |
| 其他文字訊息 | 當作研究查詢處理 |

## **🔄 系統架構圖**

整個系統的詳細運作流程：

<div align="center">
  <img src="https://github.com/user-attachments/assets/5e06e948-c853-47d1-b25e-e3c5ca96b60d" alt="LangGraph 本地 DeepSeek RAG 研究助手架構">
</div>

## **🛠 技術堆疊**

- **[Ollama](https://ollama.com/)** - 本地運行 DeepSeek R1 模型的平台
- **[LangGraph](https://www.langchain.com/langgraph)** - 建構 AI 智慧體和定義研究工作流程
- **[ChromaDB](https://docs.trychroma.com/)** - 本地向量資料庫，支援 RAG 檢索
- **[Streamlit](https://docs.streamlit.io/)** - 提供 Web 介面互動
- **[FastAPI](https://fastapi.tiangolo.com/)** - LINE Bot 後端 API 框架
- **[LINE Bot SDK](https://github.com/line/line-bot-sdk-python)** - LINE 平台整合
- **[Tavily](https://tavily.com/)** - 網路搜尋 API

## **🚀 安裝與執行**

### 📋 前置需求

確保你的環境有這些東西：
- Python 3.9 以上版本
- Ollama (用來跑本地模型)
- Tavily API Key (網路搜尋功能)
- LINE Bot 憑證 (如果要用 LINE Bot 功能)

### ⚙️ 環境設定

#### 📥 複製專案
```bash
git clone https://github.com/kaymen99/local-rag-researcher-deepseek
cd local-rag-researcher-deepseek
```

#### 🐍 建立虛擬環境
```bash
python3 -m venv venv
source venv/bin/activate  # Windows 用戶請用 `venv\Scripts\activate`
```

#### 📦 安裝套件
```bash
pip install -r requirements.txt
```

#### 🔑 設定環境變數

複製 `.env.example` 並改名為 `.env`，然後填入你的 API 金鑰：

```env
# RAG 系統基本設定
TAVILY_API_KEY="your_tavily_api_key"
OPENROUTER_API_KEY="your_openrouter_api_key"  # 如果要用外部 LLM

# LangChain 監控設定 (可選)
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_API_KEY="your_langsmith_api_key"
LANGCHAIN_PROJECT="Deepseek researcher"

# LINE Bot 設定 (如果要用 LINE Bot)
LINE_CHANNEL_SECRET="your_line_channel_secret"
LINE_CHANNEL_ACCESS_TOKEN="your_line_channel_access_token"
```

## **🎮 開始使用**

### 🤖 步驟 1：安裝並執行 Ollama

先按照[官方指南](https://ollama.com/download)安裝 Ollama，然後下載 DeepSeek R1 模型（這個專案使用 7B 版本，不過你也可以選其他[可用的模型](https://ollama.com/library/deepseek-r1)）：

```bash
ollama pull deepseek-r1:7b
```

### 🌐 步驟 2A：啟動 Streamlit Web 介面

如果你想用網頁版：

```bash
streamlit run app.py
```

### 💬 步驟 2B：啟動 LINE Bot 服務

如果你想用 LINE Bot（記得先設定好 LINE Bot 憑證）：

```bash
# 簡化版測試
python3 simple_linebot.py

# 或是完整版功能
python3 main.py
```

服務會在 `http://localhost:8000` 啟動，webhook 端點是 `/webhook`

### 🔍 步驟 3：LangGraph Studio 視覺化（可選）

想要深入了解 AI 智慧體的工作流程嗎？可以用 **LangGraph Studio**：

```bash
pip install -U "langgraph-cli[inmem]"
langgraph dev
```

## **🎨 客製化設定**

### 📄 修改報告結構

- 在 `report_structures` 資料夾裡新增你自己的報告模板
- 在使用介面中選擇偏好的報告格式
- 支援 Markdown 格式的自訂模板

### 🌐 使用外部 LLM 提供商

預設情況下，研究助手使用本地的 **DeepSeek R1** 模型。如果你想用雲端 LLM（像是 **OpenAI GPT-4o**、**Claude** 或雲端版 **DeepSeek R1**），這樣做：

1. **修改程式碼**：
   - 打開 `src/assistant/graph.py`
   - 把呼叫 Ollama 的程式碼註解掉
   - 取消註解外部 LLM 調用的部分
   - `invoke_llm` 使用 **[OpenRouter](https://openrouter.ai)**，你可以從他們的[模型清單](https://openrouter.ai/models)選擇喜歡的模型 🚀
   - 你也可以修改 `invoke_llm` 函數來使用單一 LLM 提供商

2. **設定 API 金鑰**：
   - 從[這裡](https://openrouter.ai/settings/keys)取得 OpenRouter API 金鑰
   - 加到 `.env` 檔案裡：

     ```env
     OPENROUTER_API_KEY=your_api_key
     ```

### 🤖 LINE Bot 進階設定

#### Webhook 設定
- **本地測試**：使用 ngrok 等工具建立公開隧道
- **正式環境**：設定 `https://your-domain.com/webhook`

#### 支援的文件格式
- PDF 文件 (.pdf)
- 圖片檔案 (.jpg, .png, .gif)  
- 文字檔案 (.txt)

#### 用戶設定選項
- **查詢數量**：1, 3, 5 次（預設 3 次）
- **網路搜尋**：開啟/關閉（預設關閉）
- **報告格式**：標準報告/財務報告（預設標準）

## **🎯 使用建議**

### 💡 最佳實務
1. **開發階段**：啟用 LangSmith 監控來除錯
2. **文件上傳**：先上傳相關文件再提問，效果更好
3. **查詢技巧**：問題越具體，得到的答案越精準
4. **報告格式**：根據需求選擇適合的報告模板

### ⚡ 效能調優
- **本地模型**：DeepSeek R1 7B 平衡了效能和資源使用
- **上下文長度**：建議設定 8K-16K tokens
- **並發處理**：可調整 BATCH_SIZE 參數

## **📚 延伸閱讀**

想了解更多技術細節？

* [Langchain: 用 DeepSeek-R1 建構完全本地化的「深度研究員」](https://www.youtube.com/watch?v=sGUjmyfof4Q) 
* [Langchain: 從零開始用 Ollama 建構本地研究助手](https://www.youtube.com/watch?v=XGuTzHoqlj8) 
* [LangGraph 模板: 多智慧體 RAG 研究系統](https://www.youtube.com/watch?v=JLDLANs_m_w) 
* [LangGraph 自適應 RAG 實作範例](https://github.com/langchain-ai/langgraph/blob/main/examples/rag/langgraph_adaptive_rag_local.ipynb)

## **🤝 貢獻指南**

歡迎大家一起讓這個專案變得更好！有任何想法或發現問題，請開 issue 或送 pull request。

## **📞 聯絡方式**

有問題或建議嗎？歡迎寄信給我：aymenMir1001@gmail.com

---

**🎉 現在就開始體驗你專屬的 AI 研究助手吧！無論是透過網頁還是 LINE，都能享受到強大的本地 RAG 研究能力！**