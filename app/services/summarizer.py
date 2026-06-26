from app.services.issue_classifier import IssueType


def summarize_customer_issue(message: str, issue_type: IssueType) -> str:
    cleaned = " ".join(message.strip().split())
    if len(cleaned) > 180:
        cleaned = cleaned[:177] + "..."
    if issue_type == IssueType.unknown:
        return f"Customer asks: {cleaned}"
    return f"Customer has a {issue_type.value.replace('_', ' ')} issue: {cleaned}"
