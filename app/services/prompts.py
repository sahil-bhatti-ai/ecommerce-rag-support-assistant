from langchain_core.prompts import ChatPromptTemplate

SUPPORT_RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a customer support automation assistant. Answer only from the provided "
            "document context. If context does not support the answer, say you do not know. "
            "Return concise, policy-grounded guidance.",
        ),
        (
            "human",
            "Question: {question}\n\nDocument context:\n{context}\n\nGrounded answer:",
        ),
    ]
)
