from src.assistant.graph import researcher
from src.assistant.vector_db import get_or_create_vector_db
from dotenv import load_dotenv

load_dotenv()

report_structure = """
1. 引言
- 研究主題或問題的簡要概述。
- 報告的目的和範圍。

2. 主體內容
- 對於每個部分（例如，第1節，第2節，第3節等）：
  - 提供與研究關鍵方面相關的小標題。
  - 包含解釋、發現和支持細節。

3. 關鍵要點
- 總結最重要的見解或發現的要點。

4. 結論
- 研究的最終總結。
- 發現的意義或相關性。
"""

# 定義初始狀態
initial_state = {
    "user_instructions": "你能幫我了解 AI 推理模型的當前狀態，特別是 DeepSeek R-1 嗎？我一直聽說數學推理和問題解決能力的突破，但我想知道這些模型實際上是如何在真實應用中實現和使用的。我非常有興趣了解它與其他 LLM 相比的性能，其訓練方法的獨特之處，以及是否有任何關於可靠性或限制的擔憂。我尋找的是最新的基準測試和真實世界的應用，而不僅僅是理論上的能力。",
}

# Langgraph researcher config
config = {
  "configurable": {
    "enable_web_search": False,
    "report_structure": report_structure,
    "max_search_queries": 5
}}

# Init vector store
# Must add your own documents in the /files directory before running this script
vector_db = get_or_create_vector_db()

# Run the researcher graph
for output in researcher.stream(initial_state, config=config):
    for key, value in output.items():
        print(f"Finished running: **{key}**")
        print(value)

