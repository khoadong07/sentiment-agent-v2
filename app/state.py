from typing import TypedDict, Optional, Dict, List

class AgentState(TypedDict):
    input_data: dict
    topic: Optional[dict]
    merged_text: Optional[str]
    llm_analysis: Optional[Dict]
    final_result: Optional[dict]