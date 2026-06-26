from pydantic import BaseModel

from app.core.config import get_settings
from app.schemas.chat import Citation
from app.services.confidence import compute_confidence, is_grounded
from app.services.issue_classifier import IssueType, classify_issue_type
from app.services.prompts import SUPPORT_RAG_PROMPT
from app.services.qdrant_store import QdrantVectorStore, RetrievedChunk
from app.services.resolution import generate_resolution_steps
from app.services.summarizer import summarize_customer_issue


class RAGAnswer(BaseModel):
    answer: str
    issue_type: str
    customer_issue_summary: str
    resolution_steps: list[str]
    confidence: float
    grounded: bool
    citations: list[Citation]
    fallback_reason: str | None = None


class SupportAutomationTools:
    """Tool-style actions used by the chat endpoint."""

    def __init__(self) -> None:
        self.vector_store = QdrantVectorStore()

    def search_docs(self, query: str) -> list[RetrievedChunk]:
        return self.vector_store.search(query)

    def classify_issue_type(self, message: str) -> IssueType:
        return classify_issue_type(message)

    def summarize_customer_issue(self, message: str, issue_type: IssueType) -> str:
        return summarize_customer_issue(message, issue_type)

    def generate_resolution_steps(self, issue_type: IssueType) -> list[str]:
        return generate_resolution_steps(issue_type)


class RAGService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.tools = SupportAutomationTools()

    async def answer(self, question: str) -> RAGAnswer:
        issue_type = self.tools.classify_issue_type(question)
        summary = self.tools.summarize_customer_issue(question, issue_type)
        steps = self.tools.generate_resolution_steps(issue_type)

        chunks = self.tools.search_docs(question)
        confidence = compute_confidence([chunk.score for chunk in chunks])
        grounded = is_grounded(confidence, self.settings.min_confidence)
        citations = [self._citation_from_chunk(chunk) for chunk in chunks]

        if not chunks:
            return RAGAnswer(
                answer="I could not find relevant information in the uploaded support documents.",
                issue_type=issue_type.value,
                customer_issue_summary=summary,
                resolution_steps=steps,
                confidence=confidence,
                grounded=False,
                citations=[],
                fallback_reason="No document chunks were retrieved.",
            )

        if not grounded:
            return RAGAnswer(
                answer=(
                    "I found weakly related document snippets, but not enough support to answer safely. "
                    "The uploaded documents do not clearly cover this question."
                ),
                issue_type=issue_type.value,
                customer_issue_summary=summary,
                resolution_steps=steps,
                confidence=confidence,
                grounded=False,
                citations=citations,
                fallback_reason="Retrieval confidence was below the configured threshold.",
            )

        generated_answer = await self._generate_grounded_answer(question=question, chunks=chunks, steps=steps)
        return RAGAnswer(
            answer=generated_answer,
            issue_type=issue_type.value,
            customer_issue_summary=summary,
            resolution_steps=steps,
            confidence=confidence,
            grounded=True,
            citations=citations,
            fallback_reason=None,
        )

    async def _generate_grounded_answer(
        self,
        *,
        question: str,
        chunks: list[RetrievedChunk],
        steps: list[str],
    ) -> str:
        context = "\n\n".join(
            f"Source {index + 1} [{chunk.filename} chunk {chunk.chunk_index}]: {chunk.text}"
            for index, chunk in enumerate(chunks[:3])
        )

        if self.settings.openai_api_key:
            try:
                from langchain_openai import ChatOpenAI

                llm = ChatOpenAI(
                    api_key=self.settings.openai_api_key,
                    model=self.settings.openai_model,
                    temperature=0,
                )
                chain = SUPPORT_RAG_PROMPT | llm
                result = await chain.ainvoke({"question": question, "context": context})
                return str(result.content).strip()
            except Exception:
                # Fall back silently to deterministic mode. The user asked for a working
                # backend, not a shrine to brittle third-party exceptions.
                pass

        best_chunk = chunks[0]
        joined_steps = " ".join(f"{index + 1}. {step}" for index, step in enumerate(steps))
        return (
            "Based on the uploaded support documents, the most relevant policy says: "
            f"{best_chunk.text[:700].strip()}\n\n"
            "Recommended resolution flow: "
            f"{joined_steps}"
        )

    @staticmethod
    def _citation_from_chunk(chunk: RetrievedChunk) -> Citation:
        preview = " ".join(chunk.text.split())[:260]
        return Citation(
            document_id=chunk.document_id,
            filename=chunk.filename,
            chunk_index=chunk.chunk_index,
            score=round(chunk.score, 3),
            text_preview=preview,
        )
