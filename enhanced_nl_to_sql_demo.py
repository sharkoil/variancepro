"""
VariancePro Enhanced NL-to-SQL Demo Script
This script demonstrates the enhanced natural language to SQL translator
with example queries on the comprehensive_sales_data.csv dataset.
"""

import pandas as pd
import os
import sys
import sqlite3
from typing import Dict, List, Tuple, Any
from tabulate import tabulate

# Add project root to path
sys.path.append(os.path.abspath("."))

# Import the enhanced translator
from analyzers.enhanced_nl_to_sql_translator_final_complete import EnhancedNLToSQLTranslator

def load_csv_to_dataframe(filepath: str) -> pd.DataFrame:
    """Load CSV file to pandas DataFrame"""
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} rows with {len(df.columns)} columns")
    return df

def get_schema_info(df: pd.DataFrame) -> Dict[str, Any]:
    """Extract schema information from DataFrame"""
    schema = {
        'columns': list(df.columns),
        'dtypes': {str(k): str(v) for k, v in df.dtypes.to_dict().items()},
        'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
        'date_columns': df.select_dtypes(include=['datetime64']).columns.tolist(),
        'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
        'row_count': len(df),
        'null_counts': df.isnull().sum().to_dict()
    }
    
    # If date columns weren't detected by dtype, try to find them by name
    if not schema['date_columns']:
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        schema['date_columns'] = date_columns
    
    return schema

def execute_sql_query(df: pd.DataFrame, sql_query: str) -> Tuple[bool, pd.DataFrame, str]:
    """Execute SQL query on DataFrame using SQLite"""
    try:
        # Create in-memory SQLite database
        conn = sqlite3.connect(':memory:')
        
        # Load DataFrame into SQLite
        df.to_sql('financial_data', conn, index=False, if_exists='replace')
        
        # Execute query
        result_df = pd.read_sql_query(sql_query, conn)
        
        # Close connection
        conn.close()
        
        return True, result_df, ""
    except Exception as e:
        return False, pd.DataFrame(), str(e)

def process_nl_query(translator: EnhancedNLToSQLTranslator, df: pd.DataFrame, query: str) -> None:
    """Process a natural language query and display results"""
    print(f"\n{'='*80}")
    print(f"🔍 QUERY: '{query}'")
    print(f"{'='*80}")
    
    # Translate query to SQL
    result = translator.translate_to_sql(query)
    
    if not result.success:
        if "Exit command detected" in result.error_message:
            return False  # Signal to exit
        print(f"❌ Translation failed: {result.error_message}")
        return True
    
    print(f"✅ Translated to SQL: {result.sql_query}")
    print(f"📝 Explanation: {result.explanation}")
    print(f"🎯 Confidence: {result.confidence:.2f}")
    
    # Execute SQL query
    success, results_df, error = execute_sql_query(df, result.sql_query)
    
    if not success:
        print(f"❌ Execution failed: {error}")
        return
    
    # Print results
    print(f"\n✅ Query executed successfully, returned {len(results_df)} rows")
    
    if not results_df.empty:
        print("\nRESULTS:")
        print(tabulate(results_df.head(10), headers='keys', tablefmt='pretty', showindex=False))
        
        if len(results_df) > 10:
            print(f"\n... and {len(results_df) - 10} more rows")

def main():
    """Main demo function"""
    # Load sample data
    filepath = os.path.join("sample_data", "comprehensive_sales_data.csv")
    df = load_csv_to_dataframe(filepath)
    
    # Create schema info
    schema_info = get_schema_info(df)
    
    # Initialize translator
    translator = EnhancedNLToSQLTranslator()
    translator.set_schema_context(schema_info, "financial_data")
    
    print("\n" + "="*80)
    print("🚀 ENHANCED NL-TO-SQL TRANSLATOR DEMO")
    print("="*80)
    print("\nThis demo showcases the enhanced natural language to SQL translator.")
    print("Enter natural language queries about the financial data, or type 'exit' to quit.")
    print("Type 'examples' to see sample queries you can try.")
    
    # Example queries
    examples = [
        "Show me sales greater than 60000",
        "Find transactions where actual sales is less than budget sales",
        "List products where discount percentage is greater than 2%",
        "Show regions with customer satisfaction above 3",
        "Find transactions where sales variance is negative",
        "Show me transactions with price variance greater than 3",
        "Total actual sales by region where budget sales is greater than 50000",
        "Average discount percentage by product line",
        "Top 5 regions by actual sales",
        "Find products with highest customer satisfaction"
    ]
    
    # Interactive loop
    while True:
        print("\n" + "-"*80)
        user_query = input("Enter your query (or 'examples' or 'exit'): ")
        
        if user_query.lower() == 'exit':
            print("\nExiting demo. Thank you!")
            break
        elif user_query.lower() == 'examples':
            print("\n📋 EXAMPLE QUERIES:")
            for i, example in enumerate(examples, 1):
                print(f"{i}. {example}")
            continue
        elif user_query.strip() == '':
            continue
        
        # Process the query
        continue_loop = process_nl_query(translator, df, user_query)
        if not continue_loop:
            print("\nExiting demo. Thank you!")
            break

if __name__ == "__main__":
    main()
