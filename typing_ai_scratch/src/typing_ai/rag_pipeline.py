from __future__ import annotations

from pathlib import Path

try:
    from chromadb import PersistentClient
    from langgraph.graph import END, StateGraph
    from llama_index.core import Document, VectorStoreIndex
except Exception:  # pragma: no cover
    PersistentClient = None
    StateGraph = None
    END = None
    Document = None
    VectorStoreIndex = None


class AdaptiveMemoryPipeline:
    """
    Stores recommendation memories in ChromaDB and provides
    a minimal LangGraph workflow around retrieval + recommendation.
    """

    def __init__(self, persist_dir: str | Path) -> None:
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.client = PersistentClient(path=str(self.persist_dir)) if PersistentClient else None
        self.collection = self.client.get_or_create_collection("typing_memories") if self.client else None

    def add_memory(self, user_id: int, summary: str) -> None:
        if not self.collection:
            return
        doc_id = f"user-{user_id}-{abs(hash(summary))}"
        self.collection.upsert(
            ids=[doc_id],
            documents=[summary],
            metadatas=[{"user_id": user_id}],
        )

    def retrieve_memories(self, user_id: int, query: str, limit: int = 3) -> list[str]:
        if not self.collection:
            return []
        result = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where={"user_id": user_id},
        )
        return result.get("documents", [[]])[0]

    def build_llamaindex(self, texts: list[str]):
        if not VectorStoreIndex or not Document or not texts:
            return None
        docs = [Document(text=t) for t in texts]
        return VectorStoreIndex.from_documents(docs)

    def build_langgraph(self):
        if not StateGraph:
            return None

        class State(dict):
            pass

        def retrieve_node(state: State) -> State:
            user_id = int(state.get("user_id", 0))
            query = str(state.get("query", "typing weaknesses"))
            state["memories"] = self.retrieve_memories(user_id=user_id, query=query)
            return state

        def recommend_node(state: State) -> State:
            memories = state.get("memories", [])
            if memories:
                state["recommendation_context"] = " | ".join(memories)
            else:
                state["recommendation_context"] = "No prior memory found."
            return state

        graph = StateGraph(State)
        graph.add_node("retrieve", retrieve_node)
        graph.add_node("recommend", recommend_node)
        graph.set_entry_point("retrieve")
        graph.add_edge("retrieve", "recommend")
        graph.add_edge("recommend", END)
        return graph.compile()
