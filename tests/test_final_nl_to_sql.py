"""
Final Test Script for Enhanced NL-to-SQL Translator
Tests 10 diverse examples using comprehensive_sales_data.csv with the final enhanced translator
"""

import pandas as pd
import os
import sys
import sqlite3
from typing import Dict, List, Tuple, Any
from tabulate import tabulate

# Add project root to path
sys.path.append(os.path.abspath("."))

# Import the final enhanced translator
from analyzers.enhanced_nl_to_sql_translator_final import EnhancedNLToSQLTranslator

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

def test_nl_query(translator: EnhancedNLToSQLTranslator, df: pd.DataFrame, query: str, expected_columns: List[str] = None) -> Dict[str, Any]:
    """Test a natural language query and return results"""
    print(f"\n🔍 TESTING QUERY: '{query}'")
    
    # Translate query to SQL
    result = translator.translate_to_sql(query)
    
    if not result.success:
        print(f"❌ Translation failed: {result.error_message}")
        return {
            'query': query,
            'success': False,
            'error': result.error_message,
            'sql': '',
            'results': pd.DataFrame()
        }
    
    print(f"✅ Translated to SQL: {result.sql_query}")
    print(f"📝 Explanation: {result.explanation}")
    print(f"🎯 Confidence: {result.confidence:.2f}")
    
    # Execute SQL query
    success, results_df, error = execute_sql_query(df, result.sql_query)
    
    if not success:
        print(f"❌ Execution failed: {error}")
        return {
            'query': query,
            'success': False,
            'error': error,
            'sql': result.sql_query,
            'results': pd.DataFrame()
        }
    
    # Print results
    print(f"✅ Query executed successfully, returned {len(results_df)} rows")
    
    # Verify expected columns
    if expected_columns:
        missing_cols = [col for col in expected_columns if col not in results_df.columns]
        if missing_cols:
            print(f"⚠️ Missing expected columns: {', '.join(missing_cols)}")
        else:
            print(f"✅ All expected columns found: {', '.join(expected_columns)}")
    
    if not results_df.empty:
        print("\nRESULTS PREVIEW:")
        print(tabulate(results_df.head(5), headers='keys', tablefmt='pretty', showindex=False))
    
    return {
        'query': query,
        'success': True,
        'sql': result.sql_query,
        'explanation': result.explanation,
        'confidence': result.confidence,
        'results': results_df
    }

def main():
    """Main test function"""
    # Load sample data
    filepath = "F:\\Projects\\QUANTCOMMANDER\\sample_data\\comprehensive_sales_data.csv"
    df = load_csv_to_dataframe(filepath)
    
    # Create schema info
    schema_info = get_schema_info(df)
    
    # Initialize translator
    translator = EnhancedNLToSQLTranslator()
    translator.set_schema_context(schema_info, "financial_data")
    
    # List of 10 diverse test queries with expected WHERE clauses
    test_queries = [
        {
            "query": "Show me sales greater than 60000",
            "expected_columns": ["actual_sales", "budget_sales"]
        },
        {
            "query": "Find transactions where actual sales is less than budget sales",
            "expected_columns": ["actual_sales", "budget_sales"]
        },
        {
            "query": "List products where discount percentage is greater than 2%",
            "expected_columns": ["product_line", "discount_pct"]
        },
        {
            "query": "Show regions with customer satisfaction above 3",
            "expected_columns": ["region", "customer_satisfaction"]
        },
        {
            "query": "Find transactions where sales variance is negative",
            "expected_columns": ["sales_variance"]
        },
        {
            "query": "Show me transactions with price variance greater than 3",
            "expected_columns": ["price_variance"]
        },
        {
            "query": "Total actual sales by region where budget sales is greater than 50000",
            "expected_columns": ["region", "sum_actual_sales"]
        },
        {
            "query": "Average discount percentage by product line",
            "expected_columns": ["product_line", "avg_discount_pct"]
        },
        {
            "query": "Top 5 regions by actual sales",
            "expected_columns": ["region", "sum_actual_sales"]
        },
        {
            "query": "Find products with highest customer satisfaction",
            "expected_columns": ["product_line", "customer_satisfaction"]
        }
    ]
    
    # Run tests
    results = []
    for test in test_queries:
        result = test_nl_query(translator, df, test["query"], test.get("expected_columns"))
        results.append(result)
    
    # Print summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    success_count = sum(1 for r in results if r['success'])
    print(f"✅ {success_count} of {len(results)} queries translated and executed successfully")
    
    # Print SQL queries generated
    print("\n📝 SQL QUERIES GENERATED:")
    for i, result in enumerate(results, 1):
        status = "✅" if result['success'] else "❌"
        print(f"{status} Query {i}: {result['query']}")
        print(f"   SQL: {result['sql']}")
        if 'explanation' in result:
            print(f"   Explanation: {result['explanation']}")
        print()
    
    print("="*80)
    print("🏁 TEST COMPLETED")
    print("="*80)

if __name__ == "__main__":
    main()
