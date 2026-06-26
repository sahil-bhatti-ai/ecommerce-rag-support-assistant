from app.services.issue_classifier import IssueType


BASE_STEPS: dict[IssueType, list[str]] = {
    IssueType.billing: [
        "Verify customer identity and order ID.",
        "Check invoice, payment status, duplicate charges, and payment method.",
        "Explain the billing policy and escalate to finance if the charge cannot be reconciled.",
    ],
    IssueType.refund: [
        "Verify order ID, delivery date, and return/refund eligibility window.",
        "Ask for required evidence such as images, invoice, or pickup status when needed.",
        "Offer refund, replacement, or store credit according to the uploaded policy.",
    ],
    IssueType.delivery: [
        "Check tracking status, courier updates, and expected delivery window.",
        "Confirm customer address and contact details.",
        "Escalate to logistics if the package is delayed beyond the stated policy window.",
    ],
    IssueType.product_defect: [
        "Ask for order ID, photos/videos, and description of the defect.",
        "Verify whether the defect was reported within the uploaded policy window.",
        "Offer replacement, refund, or troubleshooting according to policy.",
    ],
    IssueType.account_issue: [
        "Verify customer identity using safe account recovery steps.",
        "Guide the customer through password, email, or OTP troubleshooting.",
        "Escalate to account security if login recovery fails or suspicious activity is reported.",
    ],
    IssueType.unknown: [
        "Ask a clarifying question about the order, product, account, or policy area.",
        "Search uploaded support documents for exact policy coverage.",
        "Escalate to a human support agent if the issue is outside available documents.",
    ],
}


def generate_resolution_steps(issue_type: IssueType) -> list[str]:
    return BASE_STEPS[issue_type]
