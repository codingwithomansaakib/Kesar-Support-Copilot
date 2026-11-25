# Submission notes and product-thinking answers

## 1. Auto-send vs draft
This implementation sends nothing automatically. Routine, verified order-status and FAQ answers can be drafted automatically when identity is confirmed and confidence is at least 0.80. Refunds, complaints, privacy mismatches, medical/safety questions, ambiguous data and low-confidence classifications stay with a human. The threshold is a starting point and should be tuned using reviewed outcomes.

## 2. Cost estimate
Actual cost depends on the chosen model and prompt size. Estimate with:
`cost/email = (input_tokens × input_price + output_tokens × output_price) / 1,000,000`.
At 1,000 emails/day, monthly volume is about 30,000 emails. Insert the current provider price and measured token counts from production logs; do not invent a fixed rupee estimate. This project currently does not persist token usage.

## 3. Week-one success metric
Track the percentage of drafts approved by a human without edits, segmented by intent. A rising approval-without-edit rate indicates usefulness while preserving review. Switch off automation if privacy leaks, unsupported policy claims, or a material increase in incorrect drafts occurs.

## 4. Failure experience
The customer receives no automatic email because all output is draft-only. The case is routed for human review and the audit log records the reason. This limits harm from a wrong refund promise, privacy disclosure or medical claim.

## 5. What should stay manual
Final refund approval and any exception to policy should stay manual. These decisions involve money, evidence and customer context not fully represented in the mock order database.
