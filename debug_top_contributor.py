#!/usr/bin/env python3
"""
Debug Top Contributor Analysis Display
Test your specific file to see where contribution analysis appears in chat
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_your_file():
    """Test your specific sample_financial_data.csv file"""
    
    print("🔍 DEBUGGING TOP CONTRIBUTOR ANALYSIS")
    print("="*60)
    
    try:
        from app import AriaFinancialChat, ContributionAnalyzer
        import pandas as pd
        
        # Load your specific file
        file_path = "sample_financial_data.csv"
        df = pd.read_csv(file_path)
        
        print(f"📁 File: {file_path}")
        print(f"📊 Rows: {len(df)}, Columns: {len(df.columns)}")
        print(f"🔢 Columns: {list(df.columns)}")
        
        # Test direct contribution analyzer first
        print("\n🧪 TESTING DIRECT CONTRIBUTION ANALYZER")
        print("-" * 40)
        
        analyzer = ContributionAnalyzer()
        
        # Try different column combinations
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        print(f"📈 Numeric columns: {numeric_cols}")
        print(f"📝 Text columns: {text_cols}")
        
        # Test with Revenue and Department (most likely combination)
        if 'Revenue' in numeric_cols and 'Department' in text_cols:
            print(f"\n🎯 Testing: Revenue by Department")
            
            analysis_df, summary, fig = analyzer.perform_contribution_analysis_pandas(
                df=df,
                category_col='Department',
                value_col='Revenue'
            )
            
            print(f"✅ Analysis completed")
            print(f"📊 Summary keys: {list(summary.keys())}")
            print(f"🏆 Top contributor: {summary.get('top_contributor', 'Not found')}")
            print(f"💰 Top contributor share: {summary.get('top_contributor_share', 'Not found'):.1%}")
            print(f"🎯 Key contributors: {summary.get('key_contributors_list', 'Not found')}")
            
            # Show the contribution breakdown
            dept_totals = df.groupby('Department')['Revenue'].sum().sort_values(ascending=False)
            print(f"\n📈 Revenue by Department:")
            for dept, revenue in dept_totals.items():
                pct = (revenue / dept_totals.sum()) * 100
                print(f"   {dept}: ${revenue:,.0f} ({pct:.1f}%)")
        
        # Test through chat system
        print(f"\n💬 TESTING THROUGH CHAT SYSTEM")
        print("-" * 40)
        
        chat = AriaFinancialChat()
        
        # Test contribution analysis request
        response, status = chat.analyze_data(file_path, "perform contribution analysis")
        
        print(f"📊 Status: {status}")
        print(f"📝 Response length: {len(response)} characters")
        
        # Search for key terms in response
        keywords = ['top contributor', 'pareto', '80/20', 'key contributors', 'contribution analysis']
        
        print(f"\n🔍 Searching for keywords in response:")
        for keyword in keywords:
            found = keyword.lower() in response.lower()
            print(f"   {keyword}: {'✅' if found else '❌'}")
        
        # Find and show the contribution analysis section
        lines = response.split('\n')
        contribution_lines = []
        in_contribution_section = False
        
        for i, line in enumerate(lines):
            if any(term in line.upper() for term in ['CONTRIBUTION ANALYSIS', 'PARETO', '80/20', 'KEY CONTRIBUTORS']):
                in_contribution_section = True
                contribution_lines.append(f"Line {i+1}: {line}")
            elif in_contribution_section and line.strip():
                contribution_lines.append(f"Line {i+1}: {line}")
            elif in_contribution_section and not line.strip():
                # End of section
                break
        
        if contribution_lines:
            print(f"\n🎯 FOUND CONTRIBUTION ANALYSIS SECTION:")
            print("-" * 40)
            for line in contribution_lines[:10]:  # Show first 10 lines
                print(line)
            if len(contribution_lines) > 10:
                print(f"... ({len(contribution_lines) - 10} more lines)")
        else:
            print(f"\n❌ NO CONTRIBUTION ANALYSIS SECTION FOUND")
            print(f"💡 Showing first 300 characters of response:")
            print("-" * 40)
            print(response[:300])
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_your_file()
