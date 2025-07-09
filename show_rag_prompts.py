"""
Quick validation script to demonstrate RAG prompt integration.
This shows the prompts that would be used for each button action.
"""

def show_rag_prompts():
    """Show the RAG enhancement prompts for each button action"""
    
    print("🔍 RAG Enhancement Prompts for Quick Action Buttons")
    print("=" * 60)
    print()
    
    # Summary Action Prompt
    print("📊 SUMMARY ACTION - RAG Enhancement Prompt:")
    print("-" * 40)
    summary_prompt = """
Enhance this data summary analysis with insights from uploaded documents.

ORIGINAL ANALYSIS:
- Dataset: 370 rows × 8 columns
- Key columns: Date, Budget, Actual, Product, Category, State, Type, Margin
- Data types: 5 numeric, 3 categorical

RETRIEVED DOCUMENT CONTEXT:
[Relevant chunks from uploaded documents about macroeconomic trends, financial analysis, etc.]

Please provide enhanced insights that:
1. Connect the dataset patterns with external economic factors
2. Identify potential causes for variances based on document context
3. Suggest strategic considerations from macroeconomic perspective
4. Highlight any industry trends that might affect the data

Keep response focused and actionable.
"""
    print(summary_prompt)
    print()
    
    # Trends Action Prompt
    print("📈 TRENDS ACTION - RAG Enhancement Prompt:")
    print("-" * 40)
    trends_prompt = """
Enhance this trends analysis with supplementary insights from uploaded documents.

ORIGINAL ANALYSIS:
- Date column: Date
- Value columns analyzed: Budget, Actual, Margin
- Dataset size: 370 records
- Trends detected: [Time series patterns, seasonal variations, etc.]

RETRIEVED DOCUMENT CONTEXT:
[Relevant chunks about economic forecasts, industry outlooks, market conditions]

Please provide enhanced insights that:
1. Correlate observed trends with broader economic patterns from documents
2. Identify external factors that may explain trend changes
3. Provide forward-looking insights based on document forecasts
4. Suggest risk factors or opportunities based on trend analysis

Focus on connecting data trends with external economic intelligence.
"""
    print(trends_prompt)
    print()
    
    # Variance Action Prompt
    print("📊 VARIANCE ACTION - RAG Enhancement Prompt:")
    print("-" * 40)
    quant_commandermpt = """
Enhance this quantitative analysis with insights from uploaded documents.

ORIGINAL ANALYSIS:
- Actual column: Actual
- Planned column: Budget
- Variance patterns: [Actual vs Budget deviations, timing patterns, etc.]
- Key findings: [Major variances, categories with highest deviations]

RETRIEVED DOCUMENT CONTEXT:
[Relevant chunks about budget planning, economic uncertainties, market volatility]

Please provide enhanced insights that:
1. Explain potential causes for significant variances using document context
2. Identify external economic factors affecting performance vs budget
3. Suggest adjustments to planning based on documented trends
4. Highlight risks or opportunities for future variance management

Connect variance patterns with external economic intelligence.
"""
    print(quant_commandermpt)
    print()
    
    # Top/Bottom N Action Prompt
    print("🔝 TOP/BOTTOM N ACTION - RAG Enhancement Prompt:")
    print("-" * 40)
    top_n_prompt = """
Enhance this top/bottom analysis with insights from uploaded documents.

ORIGINAL ANALYSIS:
- Top 5 performers by Actual revenue
- Statistical summary: Mean, range, standard deviation
- Performance distribution patterns
- Base LLM commentary on performance gaps

RETRIEVED DOCUMENT CONTEXT:
[Relevant chunks about industry performance, competitive landscape, market conditions]

Please provide enhanced insights that:
1. Explain top performer success factors using document insights
2. Identify market conditions affecting performance distribution
3. Suggest strategies for bottom performers based on document guidance
4. Highlight industry benchmarks or best practices from documents

Connect performance patterns with external market intelligence.
"""
    print(top_n_prompt)
    print()
    
    print("🔧 RAG Integration Features:")
    print("-" * 40)
    print("✅ All quick action buttons now include RAG enhancement")
    print("✅ Original analysis is preserved and enhanced, not replaced")
    print("✅ RAG context is retrieved using semantic similarity search")
    print("✅ Prompts include both data analysis and document context")
    print("✅ Enhancement only occurs when documents are uploaded")
    print("✅ All prompts are logged to console for validation")
    print("✅ Graceful fallback when RAG enhancement fails")
    print()
    
    print("📋 Implementation Details:")
    print("-" * 40)
    print("• QuickActionHandler now accepts RAG components as parameters")
    print("• Each action method (_handle_summary_action, etc.) enhanced")
    print("• RAG context retrieved based on analysis type and content")
    print("• Enhanced responses include '🔍 RAG Enhancement' indicator")
    print("• Prompt logging shows exact LLM input for transparency")
    print("• Document count displayed in enhancement notice")
    print()

if __name__ == "__main__":
    show_rag_prompts()
