from typing_extensions import TypedDict, Literal
from typing import Optional

from langgraph.graph import StateGraph, START, END

class Thread(TypedDict):
    id: str
    title: str
    content: str

# Single shared state for entire graph
class GraphState(TypedDict):
    # Input
    thread_id: str

    # Fetched data
    thread: Optional[Thread]

    # Sanitized data
    sanitized_content: Optional[str]

    # Narration output
    audio_path: Optional[str]
    narration_text: Optional[str]

    # Status/Error messages
    message: Optional[str]

threads = [
    {"id": "1", "title": "The Haunted House", "content": "Once upon a time..."},
    {"id": "2", "title": "The Lost Village", "content": "In a remote corner..."},
]

def fetch(state: GraphState) -> dict:
    """Fetch thread by ID from the threads list."""
    for thread in threads:
        if thread["id"] == state["thread_id"]:
            return {"thread": thread}
    return {"thread": None}

def is_valid_thread(state: GraphState) -> Literal["sanitize", "end"]:
    """Route to sanitize if thread exists, otherwise end."""
    if state["thread"] is None:
        return "end"
    return "sanitize"

def sanitize(state: GraphState) -> dict:
    """Sanitize thread content for narration."""
    assert state["thread"] is not None  # Guaranteed by routing
    thread: Thread = state["thread"]

    # TODO: Add your sanitization logic here
    sanitized = thread["content"].strip()

    return {"sanitized_content": sanitized}

def should_narrate(state: GraphState) -> Literal["narrate", "end"]:
    """Route to narrate if sanitization succeeded."""
    if not state.get("sanitized_content"):
        return "end"
    return "narrate"

def narrate(state: GraphState) -> dict:
    """Generate audio narration from sanitized content."""
    assert state["sanitized_content"] is not None

    # TODO: Add your narration logic here (TTS, etc.)
    audio_path = f"/path/to/{state['thread_id']}.mp3"

    return {
        "audio_path": audio_path,
        "narration_text": state["sanitized_content"],
        "message": "Narration complete"
    }

def end(state: GraphState) -> dict:
    """Handle end state with appropriate message."""
    if state["thread"] is None:
        return {"message": "Thread not found."}
    return {"message": state.get("message", "Processing complete.")}

def main():
    # Build the graph
    build = StateGraph(GraphState)

    # Add nodes
    build.add_node("fetch", fetch)
    build.add_node("sanitize", sanitize)
    build.add_node("narrate", narrate)
    build.add_node("end", end)

    # Add edges
    build.add_edge(START, "fetch")
    build.add_conditional_edges(
        "fetch",
        is_valid_thread,
        {"sanitize": "sanitize", "end": "end"}
    )
    build.add_conditional_edges(
        "sanitize",
        should_narrate,
        {"narrate": "narrate", "end": "end"}
    )
    build.add_edge("narrate", "end")
    build.add_edge("end", END)

    # Compile the graph
    graph = build.compile()

    mermaid_diagram = graph.get_graph().draw_mermaid()
    print("Mermaid diagram:")
    print(mermaid_diagram)

    # Test invocations
    print("=== Test 1: Valid thread ===")
    result1 = graph.invoke({"thread_id": "1"})
    print(f"Result: {result1}\n")

    print("=== Test 2: Invalid thread ===")
    result2 = graph.invoke({"thread_id": "999"})
    print(f"Result: {result2}\n")


if __name__ == "__main__":
    main()
