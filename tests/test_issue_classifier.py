from app.services.issue_classifier import IssueType, classify_issue_type


def test_classifies_refund_issue() -> None:
    assert classify_issue_type("I want a refund for my returned product") == IssueType.refund


def test_classifies_delivery_issue() -> None:
    assert classify_issue_type("My shipment tracking has not updated and delivery is late") == IssueType.delivery


def test_classifies_unknown_issue() -> None:
    assert classify_issue_type("Tell me something philosophical about bananas") == IssueType.unknown
