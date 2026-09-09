# Cred Domain Support Agent

## Task 4 calibration

The SentenceTransformer model is `all-MiniLM-L6-v2`. Five in-scope queries produced top-1 cosine similarities of 0.7473, 0.7327, 0.6560, 0.7177, and 0.6763. Two deliberately out-of-scope queries produced 0.0479 and 0.0766, so the tested fallback threshold is 0.3663, the midpoint between the lowest in-scope and highest out-of-scope scores.

Queries below 0.3663 return an explicit “I don't know based on the available policy documents” fallback.

## Task 5 evaluation

`evaluate_rag.py` evaluates the same five in-scope queries for both chunking strategies at the document level. Retrieved chunks are deduplicated by parent document before calculating Precision@3 and Recall@3.
