"""Demonstrate SQLite checkpointing and resume for a LangGraph thread."""

from typing import TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph


class CheckpointState(TypedDict, total=False):
    completed: list[str]


def build_checkpoint_graph(checkpointer):
    """Build a three-node graph whose first two results can be checkpointed."""
    def node_a(state: CheckpointState) -> CheckpointState:
        return {"completed": state.get("completed", []) + ["node_a"]}

    def node_b(state: CheckpointState) -> CheckpointState:
        return {"completed": state.get("completed", []) + ["node_b"]}

    def node_c(state: CheckpointState) -> CheckpointState:
        return {"completed": state.get("completed", []) + ["node_c"]}

    def node_d(state: CheckpointState) -> CheckpointState:
        return {"completed": state.get("completed", []) + ["node_d"]}

    graph = StateGraph(CheckpointState)
    graph.add_node("node_a", node_a)
    graph.add_node("node_b", node_b)
    graph.add_node("node_c", node_c)
    graph.add_node("node_d", node_d)
    graph.add_edge(START, "node_a")
    graph.add_edge("node_a", "node_b")
    graph.add_edge("node_b", "node_c")
    graph.add_edge("node_c", "node_d")
    graph.add_edge("node_d", END)
    return graph.compile(checkpointer=checkpointer, interrupt_before=["node_c"])


def run_checkpoint_demo(database: str = "checkpoints.sqlite") -> tuple[dict, dict]:
    """Pause and resume one thread, returning paused and completed states."""
    config = {"configurable": {"thread_id": "task15-demo-thread"}}
    with SqliteSaver.from_conn_string(database) as saver:
        graph = build_checkpoint_graph(saver)
        paused = graph.invoke({"completed": []}, config)
        resumed = graph.invoke(None, config)
    return paused, resumed


if __name__ == "__main__":
    paused, resumed = run_checkpoint_demo()
    print("Paused checkpoint state:", paused)
    print("Resumed completed state:", resumed)
    print("Checkpoint reused node_a and node_b:", resumed["completed"].count("node_a") == 1 and resumed["completed"].count("node_b") == 1)
