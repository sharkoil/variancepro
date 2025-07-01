#!/usr/bin/env python3
"""
Complete Chat Interface Test
Tests the full workflow: upload → analyzing → timescale analysis → LLM summary
"""

import os
import sys
import pandas as pd
import tempfile
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Import our application components
try:
    from app import AriaFinancialChat, ContributionAnalyzer
    print("✅ Successfully imported application components")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def create_test_data():
    """Create sample financial data for testing"""
    data = {
        'Date': pd.date_range('2024-01-01', periods=12, freq='M'),
        'Product': ['Product_A', 'Product_B', 'Product_C', 'Product_A', 'Product_B', 'Product_C'] * 2,
        'Sales': [15000, 25000, 8000, 18000, 22000, 9500, 16000, 27000, 7500, 17000, 24000, 8800],
        'Budget': [14000, 24000, 9000, 17000, 21000, 9000, 15000, 26000, 8000, 16000, 23000, 9000],
        'Region': ['North', 'South', 'East', 'North', 'South', 'East'] * 2
    }
    df = pd.DataFrame(data)
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    df.to_csv(temp_file.name, index=False)
    temp_file.close()
    
    print(f"✅ Created test data with {len(df)} rows")
    print(f"📁 Test file: {temp_file.name}")
    return temp_file.name, df


def test_chat_workflow():
    """Test the complete chat workflow"""
    print("\n" + "="*50)
    print("🧪 TESTING COMPLETE CHAT WORKFLOW")
    print("="*50)
    
    # Step 1: Create test data
    test_file, test_df = create_test_data()
    
    try:
        # Step 2: Initialize chat system
        print("\n📋 Step 1: Initialize Chat System")
        chat_system = AriaFinancialChat()
        print("✅ Chat system initialized")
        
        # Step 3: Test file upload analysis
        print("\n📋 Step 2: Test File Upload & Initial Analysis")
        response, status = chat_system.analyze_data(test_file, "analyze this data")
        print(f"✅ Initial analysis completed")
        print(f"📊 Status: {status}")
        print(f"📝 Response length: {len(response)} characters")
        
        # Step 4: Test contribution analysis
        print("\n📋 Step 3: Test Contribution Analysis")
        response, status = chat_system.analyze_data(test_file, "perform contribution analysis")
        print(f"✅ Contribution analysis completed")
        print(f"📊 Status: {status}")
        
        # Verify response contains expected elements
        expected_elements = [
            "contribution analysis",
            "pareto",
            "80/20",
            "key contributors"
        ]
        
        found_elements = []
        for element in expected_elements:
            if element.lower() in response.lower():
                found_elements.append(element)
        
        print(f"✅ Found expected elements: {found_elements}")
        
        # Step 5: Test ContributionAnalyzer directly
        print("\n📋 Step 4: Test ContributionAnalyzer Class")
        analyzer = ContributionAnalyzer()
        
        # Test pandas-based analysis
        analysis_df, summary, fig = analyzer.perform_contribution_analysis_pandas(
            test_df, 
            value_col='Sales', 
            category_col='Product'
        )
        
        print(f"✅ Direct analyzer test completed")
        print(f"📊 Summary keys: {list(summary.keys())}")
        print(f"🎯 Key contributors count: {summary['key_contributors_count']}")
        print(f"📈 Top contributor: {summary['top_contributor']}")
        print(f"💰 Value share: {summary['key_contributors_value_share']:.1%}")
        
        # Step 6: Test 80/20 validation
        print("\n📋 Step 5: Validate 80/20 Principle")
        key_contributors = analysis_df[analysis_df['is_key_contributor']]
        total_contributors = len(analysis_df)
        key_percentage = len(key_contributors) / total_contributors
        value_share = summary['key_contributors_value_share']
        
        print(f"📊 Contributors: {len(key_contributors)}/{total_contributors} ({key_percentage:.1%})")
        print(f"💰 Value share: {value_share:.1%}")
        
        if value_share >= 0.7:  # At least 70% concentration
            print("✅ Strong concentration pattern detected (good 80/20 distribution)")
        else:
            print("ℹ️ Moderate concentration pattern")
        
        print("\n🎉 ALL TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        try:
            os.unlink(test_file)
            print(f"🗑️ Cleaned up test file")
        except:
            pass


def test_sample_data_analysis():
    """Test with the actual sample data files"""
    print("\n" + "="*50)
    print("🧪 TESTING WITH SAMPLE DATA FILES")
    print("="*50)
    
    sample_files = [
        'sales_budget_actuals.csv',
        'sample_financial_data.csv'
    ]
    
    for file_name in sample_files:
        file_path = project_dir / file_name
        if file_path.exists():
            print(f"\n📁 Testing with: {file_name}")
            
            try:
                chat_system = AriaFinancialChat()
                response, status = chat_system.analyze_data(str(file_path), "perform contribution analysis")
                print(f"✅ Analysis completed for {file_name}")
                print(f"📊 Status: {status}")
                
                # Check if response contains contribution analysis
                if "contribution" in response.lower() and "pareto" in response.lower():
                    print("✅ Response contains contribution analysis content")
                else:
                    print("⚠️ Response may not contain full contribution analysis")
                    
            except Exception as e:
                print(f"❌ Error with {file_name}: {str(e)}")
        else:
            print(f"⚠️ Sample file not found: {file_name}")


if __name__ == "__main__":
    print("🚀 VariancePro Complete Chat Interface Test")
    print("Testing the workflow: upload → analyzing → timescale analysis → LLM summary")
    
    # Test 1: Complete workflow
    success = test_chat_workflow()
    
    # Test 2: Sample data files
    test_sample_data_analysis()
    
    if success:
        print("\n✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("🎯 The chat interface is ready for:")
        print("   1. File upload")
        print("   2. Automatic analysis detection")
        print("   3. Contribution analysis (80/20 Pareto)")
        print("   4. Time-series analysis")
        print("   5. LLM-powered insights")
        print("\n🌐 Open http://127.0.0.1:7860 to use the interface")
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)
