import logging
from langgraph.graph import StateGraph
from app.state import AgentState
from app.nodes.merge_text import merge_text
from app.nodes.analyze_with_llm import analyze_with_llm
from app.nodes.format_output import format_output

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_sentiment_analysis_graph():
    """
    Tạo graph để phân tích sentiment và keyword matching
    """
    graph = StateGraph(AgentState)
    
    # Thêm các nodes
    graph.add_node("merge_text", merge_text)
    graph.add_node("analyze_with_llm", analyze_with_llm)
    graph.add_node("format_output", format_output)
    
    # Thiết lập flow
    graph.set_entry_point("merge_text")
    graph.add_edge("merge_text", "analyze_with_llm")
    graph.add_edge("analyze_with_llm", "format_output")
    graph.set_finish_point("format_output")
    
    return graph.compile()

# Tạo agent instance
agent = create_sentiment_analysis_graph()

logger.info("Sentiment analysis agent đã được khởi tạo thành công")