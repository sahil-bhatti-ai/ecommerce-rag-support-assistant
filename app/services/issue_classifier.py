from enum import StrEnum


class IssueType(StrEnum):
    billing = "billing"
    refund = "refund"
    delivery = "delivery"
    product_defect = "product_defect"
    account_issue = "account_issue"
    unknown = "unknown"


KEYWORDS: dict[IssueType, set[str]] = {
    IssueType.billing: {"invoice", "charged", "charge", "payment", "billing", "card", "paid"},
    IssueType.refund: {"refund", "return", "cancel", "replacement", "money back"},
    IssueType.delivery: {"delivery", "shipping", "shipment", "late", "delayed", "courier", "tracking"},
    IssueType.product_defect: {"damaged", "broken", "defective", "missing", "wrong item", "quality"},
    IssueType.account_issue: {"login", "password", "account", "email", "otp", "profile"},
}


def classify_issue_type(message: str) -> IssueType:
    normalized = message.lower()
    scores: dict[IssueType, int] = {}
    for issue_type, keywords in KEYWORDS.items():
        scores[issue_type] = sum(1 for keyword in keywords if keyword in normalized)

    best_issue, best_score = max(scores.items(), key=lambda item: item[1])
    return best_issue if best_score > 0 else IssueType.unknown
