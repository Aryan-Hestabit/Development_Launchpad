import pandas as pd
import numpy as np

def load_data(filepath):
    """Load raw dataset"""
    df = pd.read_csv(filepath)
    print(f" Data loaded: {df.shape}")
    return df

def handle_missing_values(df):
    """Handle missing values marked as '?'"""
    print("\n" + "="*60)
    print("HANDLING MISSING VALUES")
    print("="*60)
    
    # Replace '?' with 'Unknown' for workclass and occupation
    df['workclass'] = df['workclass'].replace('?', 'Unknown')
    df['occupation'] = df['occupation'].replace('?', 'Unknown')
    print(" Replaced '?' with 'Unknown' in workclass and occupation")
    
    # Remove rows where native.country is '?'
    rows_before = len(df)
    df = df[df['native.country'] != '?'].copy()
    rows_removed = rows_before - len(df)
    print(f" Removed {rows_removed} rows with native.country='?' ({rows_removed/rows_before*100:.2f}%)")
    
    return df

def remove_duplicates(df):
    """Remove duplicate rows"""
    print("\n" + "="*60)
    print("REMOVING DUPLICATES")
    print("="*60)
    
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        df = df.drop_duplicates().copy()
        print(f" Removed {duplicates} duplicate rows")
    else:
        print(" Removed no duplicates")
    
    return df


def save_cleaned_data(df, output_path):
    """Save cleaned dataset"""
    df.to_csv(output_path, index=False)
    print(f"\n Cleaned data saved to: {output_path}")
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
    print(" DATA PIPELINE COMPLETED!")
    print("=" * 70)
    
    return df

if __name__ == "__main__":
    # File paths
    input_file = "../data/raw/adult.csv"
    output_file = "../data/processed/processed_adult.csv"
    
    # Run pipeline
    cleaned_df = run_pipeline(input_file, output_file)