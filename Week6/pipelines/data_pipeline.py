import pandas as pd
import numpy as np

def load_data(filepath):
    """Load raw dataset"""
    df = pd.read_csv(filepath)
    print(f"✅ Data loaded: {df.shape}")
    return df

def handle_missing_values(df):
    """Handle missing values marked as '?'"""
    print("\n" + "="*60)
    print("HANDLING MISSING VALUES")
    print("="*60)
    
    # Replace '?' with 'Unknown' for workclass and occupation
    df['workclass'] = df['workclass'].replace('?', 'Unknown')
    df['occupation'] = df['occupation'].replace('?', 'Unknown')
    print("✅ Replaced '?' with 'Unknown' in workclass and occupation")
    
    # Remove rows where native.country is '?'
    rows_before = len(df)
    df = df[df['native.country'] != '?'].copy()
    rows_removed = rows_before - len(df)
    print(f"✅ Removed {rows_removed} rows with native.country='?' ({rows_removed/rows_before*100:.2f}%)")
    
    return df

def remove_duplicates(df):
    """Remove duplicate rows"""
    print("\n" + "="*60)
    print("REMOVING DUPLICATES")
    print("="*60)
    
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        df = df.drop_duplicates().copy()
        print(f"✅ Removed {duplicates} duplicate rows")
    else:
        print("✅ No duplicates found")
    
    return df

def handle_outliers(df):
    """Handle outliers in numerical features"""
    print("\n" + "="*60)
    print("HANDLING OUTLIERS")
    print("="*60)
    
    # Features to handle outliers
    outlier_features = ['age', 'hours.per.week']
    
    for col in outlier_features:
        # Calculate IQR
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        print(f"\nlower_bound (before domain constraints) for {col}: {lower_bound:.1f}")
        print(f"\nupper_bound (before domain constraints) for {col}: {upper_bound:.1f}")
        
        # Apply domain constraints
        if col == 'age':
            lower_bound = max(17, lower_bound)  # Min working age
            upper_bound = min(90, upper_bound)  # Max reasonable age
        elif col == 'hours.per.week':
            lower_bound = max(1, lower_bound)   # Min 1 hour
            upper_bound = min(99, upper_bound)  # Max 99 hours
        
        # Count outliers before capping
        outliers_lower = (df[col] < lower_bound).sum()
        outliers_upper = (df[col] > upper_bound).sum()
        total_outliers = outliers_lower + outliers_upper
        
        # Cap outliers
        df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
        
        print(f"✅ {col}: Capped {total_outliers} outliers (bounds: [{lower_bound:.1f}, {upper_bound:.1f}])")
    return df

def save_cleaned_data(df, output_path):
    """Save cleaned dataset"""
    df.to_csv(output_path, index=False)
    print(f"\n✅ Cleaned data saved to: {output_path}")
    print(f"   Final shape: {df.shape}")

def run_pipeline(input_path, output_path):
    """Run complete data pipeline"""
    print("=" * 70)
    print("DATA CLEANING PIPELINE")
    print("=" * 70)
    
    # Load data
    df = load_data(input_path)
    
    # Handle missing values
    df = handle_missing_values(df)
    
    # Remove duplicates
    df = remove_duplicates(df)
    
    # Save cleaned data
    save_cleaned_data(df, output_path)
    
    print("\n" + "=" * 70)
    print("✅ DATA PIPELINE COMPLETED!")
    print("=" * 70)
    
    return df

if __name__ == "__main__":
    # File paths
    input_file = "../data/raw/adult.csv"
    output_file = "../data/processed/processed_adult.csv"
    
    # Run pipeline
    cleaned_df = run_pipeline(input_file, output_file)