# Feature Engineering Documentation - Day 2

## Overview

This document describes all feature engineering steps applied to the Adult Census Income dataset for binary income classification (<=50K vs >50K).

---

## Dataset Summary

- **Original Dataset**: 32,561 rows, 15 columns
- **After Cleaning (Day 1)**: 31,978 rows, 15 columns
- **After Feature Engineering**: 31,978 rows, 60 features
- **After Feature Selection**: 31,978 rows, 30 features
- **Train/Test Split**: 80/20 (25,582 / 6,396 samples)

---

## 1. Feature Building

### Dropped Features

**fnlwgt** - Census sampling weight (metadata, not predictive)  
**education** - Redundant with education.num (text version dropped, kept numeric ordinal)

### New Features Created (10 total)

#### Capital-Related Features (3)

1. **capital_net**
   - Formula: `capital.gain - capital.loss`
   - Type: Numerical
   - Purpose: Net capital from investments

2. **has_capital_activity**
   - Formula: `(capital.gain > 0) OR (capital.loss > 0)`
   - Type: Binary (0/1)
   - Purpose: Indicates any investment/trading activity

3. **capital_gain_log**
   - Formula: `log(1 + capital.gain)`
   - Type: Numerical
   - Purpose: Handles extreme skewness (original skewness = 11.95)

#### Age-Related Features (2)

4. **age_group**
   - Bins: [0-25, 25-35, 35-50, 50-65, 65-100]
   - Labels: Young, Early-Career, Mid-Career, Senior, Retirement
   - Type: Categorical
   - Purpose: Captures life/career stage patterns

5. **is_prime_age**
   - Formula: `(age >= 35) AND (age <= 55)`
   - Type: Binary (0/1)
   - Purpose: Peak earning years indicator

#### Work Hours Features (2)

6. **hours_category**
   - Bins: [0-35, 35-40, 40-50, 50-100]
   - Labels: Part-time, Standard, Overtime, Extreme
   - Type: Categorical
   - Purpose: Work commitment level

7. **is_overworker**
   - Formula: `hours.per.week > 50`
   - Type: Binary (0/1)
   - Purpose: Identifies high work commitment

#### Education Feature (1)

8. **has_higher_education**
   - Formula: `education.num >= 13`
   - Type: Binary (0/1)
   - Purpose: College degree or higher (13=Bachelors, 14=Masters, 15=Prof-school, 16=Doctorate)

#### Marital Status Feature (1)

9. **is_married**
   - Formula: `marital.status contains 'Married'`
   - Type: Binary (0/1)
   - Purpose: Married status indicator

#### Country Feature (1)

10. **is_us_native**
    - Formula: `native.country == 'United-States'`
    - Type: Binary (0/1)
    - Purpose: US citizenship indicator

---

## 2. Feature Encoding

### Target Variable Encoding

**income**: Simple binary mapping
- `<=50K` → 0
- `>50K` → 1

### Categorical Feature Encoding Strategy

#### One-Hot Encoding (Low Cardinality ≤10)

Applied to features with 10 or fewer unique values:

- **workclass** (9 categories) → 8 binary columns
- **marital.status** (7 categories) → 6 binary columns
- **occupation** (15 categories) → 14 binary columns
- **relationship** (6 categories) → 5 binary columns
- **race** (5 categories) → 4 binary columns
- **sex** (2 categories) → 1 binary column
- **age_group** (5 categories) → 4 binary columns
- **hours_category** (4 categories) → 3 binary columns

**Total one-hot encoded columns**: 45

**Method**: `sklearn.preprocessing.OneHotEncoder(drop_first=True)`
- `drop_first=True` to avoid multicollinearity

#### Target Encoding (High Cardinality >10)

Applied to features with more than 10 unique values:

- **native.country** (42 unique countries)
  - Each country replaced with mean income (0 or 1) for that country
  - Example: If 30% of people from Mexico earn >50K, Mexico → 0.30
  - Handles unknown countries with global mean

**Method**: `category_encoders.TargetEncoder`
- Better than Label Encoding (no false ordinal relationships)
- Captures actual relationship with target variable

---

## 3. Feature Scaling

### Method: RobustScaler

**Why RobustScaler?**
- Uses median and IQR (Interquartile Range) instead of mean and std
- Robust to extreme values in data
- Better for data with valid outliers (e.g., 99 hours/week is valid but extreme)

**Formula**: `(X - median) / IQR`

### Features Scaled

Applied to all continuous numerical features:
- age
- education.num
- capital.gain
- capital.loss
- hours.per.week
- capital_net
- capital_gain_log
- native.country (after target encoding)

### Features NOT Scaled

Binary features (already 0/1):
- has_capital_activity
- is_prime_age
- is_overworker
- has_higher_education
- is_married
- is_us_native
- All one-hot encoded features

**Total features after encoding**: 60

---

## 4. Feature Selection

### Method: Mutual Information

**Why Mutual Information?**
- Measures dependency between feature and target
- Works with both linear and non-linear relationships
- Fast and accurate
- No model training required

**Process**:
1. Calculate MI score for each of 60 features
2. Rank features by MI score
3. Select top 30 features

### Selected Features: 30

Top features by Mutual Information score will be determined after running the pipeline.

**Parameters**:
- Number of features: k=30
- Random state: 42
- Scoring function: `mutual_info_classif`

**Reasoning for k=30**:
- 50% reduction from 60 features
- Sample-to-feature ratio: 853:1 (excellent)
- Industry standard for datasets this size
- Works well with all model types

---

## 5. Train/Test Split

**Split Ratio**: 80/20
- Training set: 25,582 samples
- Test set: 6,396 samples

**Strategy**: Stratified split
- Maintains 76:24 class distribution in both sets
- Random state: 42

**Important**: Split performed AFTER feature engineering and encoding, but BEFORE using transformers to avoid data leakage.

---

## 6. Class Imbalance Handling

**Original Distribution**:
- Class 0 (<=50K): 24,720 samples (75.92%)
- Class 1 (>50K): 7,841 samples (24.08%)
- Imbalance ratio: 3.15:1

**Strategy**: Use `class_weight='balanced'` in models (Day 3)

**Decision**: NOT using SMOTE
- Imbalance ratio (3.15:1) is moderate, not extreme
- SMOTE creates synthetic data which can introduce noise
- class_weight is simpler and more interpretable
- 7,841 minority samples is sufficient for training

---

## 7. Files Generated

### Data Files
- `features_engineered.csv` - Full dataset with 60 engineered features
- `X_train.csv` - Training features (30 selected features)
- `X_test.csv` - Test features (30 selected features)
- `y_train.csv` - Training labels
- `y_test.csv` - Test labels

### Metadata Files
- `transformers.pkl` - Saved OneHotEncoder, TargetEncoder, RobustScaler
- `feature_list.json` - List of all features and metadata
- `selected_features.json` - Selected features and MI scores

### Visualizations
- `feature_importance.png` - Top 20 features by MI score

---

## 8. Key Decisions & Rationale

### Why drop fnlwgt?
Census sampling weight is statistical metadata, not a predictive feature. It represents how many people in the population a record represents, not characteristics of the individual.

### Why log transform capital.gain?
Original skewness of 11.95 is extreme. Log transformation (log1p) makes the distribution more normal while preserving the information that high capital gains predict high income.

### Why keep education.num instead of education text?
education.num is already ordinal (1=Preschool to 16=Doctorate) and numerical, making it ready for models. The text version is redundant.

### Why RobustScaler over StandardScaler?
Even though we handled skewness with log transformation, features like hours.per.week still have valid extreme values (1 hour, 99 hours). RobustScaler's use of median and IQR makes it more stable.

### Why Target Encoding for native.country?
With 42 unique countries, one-hot encoding would create 41 new columns (feature explosion). Target encoding captures the actual income relationship per country in a single numerical column.

### Why Mutual Information over other methods?
- Correlation method: Only removes redundancy, doesn't select best features
- RFE: Slower, requires model training
- Mutual Information: Fast, captures non-linear relationships, model-agnostic

---

## 9. Pipeline Workflow

```
Raw Data (final.csv)
    ↓
Feature Building
    ↓ (23 features)
Encoding (One-Hot + Target)
    ↓ (60 features)
Scaling (RobustScaler)
    ↓ (60 features, scaled)
Train/Test Split (80/20)
    ↓
Feature Selection (Mutual Information)
    ↓ (30 features)
Output: X_train, X_test, y_train, y_test
```

---

## 10. Code Files

- `build_features.py` - Feature engineering pipeline
- `feature_selector.py` - Feature selection and train/test split

---

## Summary Statistics

| Stage | Features | Samples |
|-------|----------|---------|
| Raw data | 15 | 32,561 |
| After cleaning | 15 | 31,978 |
| After feature building | 23 | 31,978 |
| After encoding | 60 | 31,978 |
| After selection (train) | 30 | 25,582 |
| After selection (test) | 30 | 6,396 |

**Final train/test datasets ready for Day 3 model training.**