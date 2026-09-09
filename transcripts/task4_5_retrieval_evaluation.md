# Tasks 4–5 manual transcript

## Task 4 calibration

```text
In-scope top-1 similarities: [0.7473, 0.7327, 0.656, 0.7177, 0.6763]
Out-of-scope top-1 similarities: [0.0479, 0.0766]
Calibrated fallback threshold: 0.3663
```

The in-scope KYC query returned policy context and the out-of-scope weather query returned:

```text
I don't know based on the available policy documents.
```

## Task 5 comparison

```text
Fixed strategy
KYC: Precision@3=0.333, Recall@3=1.000
EMI: Precision@3=0.333, Recall@3=1.000
Fraud dispute: Precision@3=0.333, Recall@3=1.000
Credit score: Precision@3=0.333, Recall@3=1.000
NRI account: Precision@3=0.333, Recall@3=1.000
Mean Precision@3: 0.333
Mean Recall@3: 1.000

Sentence strategy
KYC: Precision@3=0.333, Recall@3=1.000
EMI: Precision@3=0.333, Recall@3=1.000
Fraud dispute: Precision@3=0.333, Recall@3=1.000
Credit score: Precision@3=0.333, Recall@3=1.000
NRI account: Precision@3=0.333, Recall@3=1.000
Mean Precision@3: 0.333
Mean Recall@3: 1.000
```

Both strategies tied on the measured metrics. Sentence-based chunks were selected because their policy boundaries are easier to interpret and maintain.
