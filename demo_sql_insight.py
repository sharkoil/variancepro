"""
SQL Insight Engine Demo Script
Demonstrates AI-powered field detection and insight generation
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzers.sql_insight_engine import SQLInsightEngine

def create_sample_data():
    """Create sample financial data for testing"""
    data = {
        'transaction_id': range(1, 101),
        'date': pd.date_range('2024-01-01', periods=100, freq='D'),
        'customer_name': [f'Customer_{i}' for i in range(1, 101)],
        'product_category': ['Electronics', 'Clothing', 'Books', 'Food'] * 25,
        'sales_amount': [100.50 + (i * 10.25) for i in range(100)],
        'profit_margin': [0.15 + (i * 0.002) for i in range(100)],
        'region': ['North', 'South', 'East', 'West'] * 25,
        'customer_type': ['Premium', 'Standard'] * 50
    }
    return pd.DataFrame(data)

def demo_field_detection():
    """Demonstrate AI-powered field detection"""
    print("🧠 SQL Insight Engine Demo")
    print("=" * 50)
    
    # Initialize engine
    engine = SQLInsightEngine()
    
    # Create sample data
    print("📊 Creating sample financial dataset...")
    df = create_sample_data()
    print(f"   • {len(df)} rows, {len(df.columns)} columns")
    
    # Load dataset with AI analysis
    print("\n🔍 Analyzing fields with AI...")
    result = engine.load_dataset(df, "sales_data")
    
    if result["status"] == "success":
        print("✅ Dataset loaded successfully!")
        print(f"   • Table: {result['table_name']}")
        print(f"   • Rows: {result['row_count']}")
        print(f"   • Columns: {result['column_count']}")
        
        print("\n🎯 AI-Detected Field Types:")
        for field_name, field_type in result["schema"].items():
            print(f"   • {field_name:20} → {field_type}")
        
        print("\n📋 Field Picker Data:")
        for field in result["field_picker_data"]:
            print(f"   • {field['name']:20} | {field['type']:12} | {field['description']}")
        
        return engine
    else:
        print(f"❌ Error: {result['message']}")
        return None

def demo_query_execution(engine):
    """Demonstrate SQL query execution with insights"""
    if not engine:
        return
    
    print("\n" + "=" * 50)
    print("📊 Query Execution Demo")
    
    # Test queries
    queries = [
        {
            "name": "Sales Summary",
            "query": "SELECT product_category, COUNT(*) as transactions, AVG(sales_amount) as avg_sales FROM sales_data GROUP BY product_category ORDER BY avg_sales DESC"
        },
        {
            "name": "Top Customers",
            "query": "SELECT customer_name, SUM(sales_amount) as total_sales FROM sales_data GROUP BY customer_name ORDER BY total_sales DESC LIMIT 5"
        },
        {
            "name": "Regional Performance",
            "query": "SELECT region, AVG(sales_amount) as avg_sales, AVG(profit_margin) as avg_margin FROM sales_data GROUP BY region"
        }
    ]
    
    for i, query_info in enumerate(queries, 1):
        print(f"\n🔍 Query {i}: {query_info['name']}")
        print(f"SQL: {query_info['query']}")
        
        # Execute query with insights
        result = engine.execute_sql_query(query_info['query'], generate_insights=True)
        
        if result["status"] == "success":
            print(f"✅ Success! {result['row_count']} rows returned")
            
            # Show sample results
            if result["data"]:
                print("\n📊 Sample Results:")
                for row in result["data"][:3]:
                    print(f"   {row}")
            
            # Show AI insights
            if "insights" in result:
                insights = result["insights"]
                print(f"\n🧠 AI Insights Status: {insights['status']}")
                if insights["status"] in ["success", "fallback"]:
                    print("💡 Analysis:")
                    # Show first few lines of insights
                    insights_text = insights["insights_text"]
                    lines = insights_text.split('\n')[:5]
                    for line in lines:
                        if line.strip():
                            print(f"   {line.strip()}")
                    if len(insights_text.split('\n')) > 5:
                        print("   ... (truncated)")
        else:
            print(f"❌ Query failed: {result['message']}")
        
        print("-" * 30)

def demo_suggestions(engine):
    """Demonstrate query suggestions"""
    if not engine:
        return
        
    print("\n" + "=" * 50)
    print("💡 Smart Query Suggestions")
    
    suggestions = engine.get_query_suggestions()
    
    print(f"\n📋 Generated {len(suggestions)} suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n{i}. {suggestion['title']}")
        print(f"   Category: {suggestion['category']}")
        print(f"   Description: {suggestion['description']}")
        print(f"   SQL: {suggestion['query']}")

def demo_template_management(engine):
    """Demonstrate template management"""
    if not engine:
        return
        
    print("\n" + "=" * 50)
    print("💾 Template Management Demo")
    
    # Save a template
    template_result = engine.save_query_template(
        name="Sales Analysis Template",
        query="SELECT product_category, SUM(sales_amount) as total_sales FROM sales_data GROUP BY product_category",
        description="Analyze total sales by product category"
    )
    
    if template_result["status"] == "success":
        print("✅ Template saved successfully!")
        print(f"   Template ID: {template_result['template_id']}")
        
        # Show saved templates
        templates = engine.get_saved_templates()
        print(f"\n📚 Saved Templates ({len(templates)}):")
        for template in templates:
            print(f"   • {template['name']} (ID: {template['id']})")
            print(f"     Query: {template['query'][:50]}...")
    else:
        print(f"❌ Failed to save template: {template_result['message']}")

def main():
    """Run the complete demo"""
    print("🚀 Starting SQL Insight Engine Demo...")
    print("This demo shows the prototype features:")
    print("• AI-powered field type detection")
    print("• SQL query execution with safety validation") 
    print("• LLM-generated insights from query results")
    print("• Smart query suggestions")
    print("• Template management")
    
    try:
        # Demo field detection
        engine = demo_field_detection()
        
        if engine:
            # Demo query execution
            demo_query_execution(engine)
            
            # Demo suggestions
            demo_suggestions(engine)
            
            # Demo template management
            demo_template_management(engine)
            
            # Show query history
            print("\n" + "=" * 50)
            print("📝 Query History")
            history = engine.get_query_history()
            print(f"\nExecuted {len(history)} queries:")
            for record in history:
                status_icon = "✅" if record["status"] == "success" else "❌"
                print(f"   {status_icon} {record['timestamp'][:19]} | {record['query'][:40]}...")
        
        print("\n🎉 Demo completed successfully!")
        print("\nTo launch the full UI prototype, run:")
        print("   python sql_insight_prototype.py")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
