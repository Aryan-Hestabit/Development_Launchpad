# Model Comparison Report - Day 3

## Summary

**Best Model:** LightGBM
**Best F1-Score:** 0.6965

## Models Trained

1. Logistic Regression (with L2 regularization)
2. Random Forest
3. XGBoost
4. LightGBM

All models use **class_weight='balanced'** (or equivalent) to handle 76:24 class imbalance.

## Cross-Validation Results (5-Fold)

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|-------|----------|-----------|--------|----------|---------|
| Logistic Regression | 0.8049 | 0.5624 | 0.8599 | 0.6799 | 0.9086 |
| Random Forest | 0.8442 | 0.6819 | 0.6624 | 0.6719 | 0.8967 |
| XGBoost | 0.8312 | 0.6053 | 0.8616 | 0.7110 | 0.9251 |
| LightGBM | 0.8278 | 0.5980 | 0.8699 | 0.7088 | 0.9263 |

## Test Set Results

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|-------|----------|-----------|--------|----------|---------|
| Logistic Regression | 0.8041 | 0.5618 | 0.8469 | 0.6755 | 0.9031 |
| Random Forest | 0.8399 | 0.6780 | 0.6378 | 0.6572 | 0.8868 |
| XGBoost | 0.8213 | 0.5911 | 0.8361 | 0.6926 | 0.9168 |
| LightGBM  | 0.8207 | 0.5877 | 0.8546 | 0.6965 | 0.9208 |

lightGBM = Best Model

## Confusion Matrices

### Logistic Regression

```
True Negative:   3909  |  False Positive:  1036
False Negative:   240  |  True Positive:   1328
```

### Random Forest

```
True Negative:   4470  |  False Positive:   475
False Negative:   568  |  True Positive:   1000
```

### XGBoost

```
True Negative:   4038  |  False Positive:   907
False Negative:   257  |  True Positive:   1311
```

### LightGBM

```
True Negative:   4005  |  False Positive:   940
False Negative:   228  |  True Positive:   1340
```

## Key Findings

- **Best performing model:** LightGBM
- **Class imbalance handled:** Using class weights for all models
- **Regularization:** L2 regularization applied to Logistic Regression
- **Cross-validation:** 5-fold CV used for robust evaluation
