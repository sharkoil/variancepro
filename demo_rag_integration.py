"""
RAG Integration Demo
Shows how the new RAG functionality enhances analysis
"""

import sys
import os
import tempfile

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_rag_functionality():
    """Demonstrate RAG functionality with sample data"""
    print("🚀 RAG Integration Demo")
    print("=" * 50)
    
    try:
        # Import RAG components
        from analyzers.rag_document_manager import RAGDocumentManager
        from analyzers.rag_enhanced_analyzer import RAGEnhancedAnalyzer
        print("✅ RAG modules imported successfully")
        
        # Initialize components
        rag_manager = RAGDocumentManager()
        rag_analyzer = RAGEnhancedAnalyzer(rag_manager)
        print("✅ RAG components initialized")
        
        # Create sample document
        sample_document = """
        Financial Performance Report Q3 2024
        
        Executive Summary:
        Our quarterly analysis reveals significant insights into company performance.
        
        Variance Analysis:
        - Budget variance in sales: +15% above target
        - Marketing spend variance: -8% below budget (cost savings)
        - Regional performance: North region exceeded targets by 20%
        
        Trend Analysis:
        - Digital channel growth: 25% YoY increase
        - Customer acquisition costs: Stable at $45 per customer
        - Revenue per customer: Increased 12% from last quarter
        
        Key Recommendations:
        1. Increase investment in North region
        2. Expand digital marketing initiatives
        3. Monitor cost savings sustainability
        """
        
        # Save to temporary file and upload
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(sample_document)
            temp_file_path = temp_file.name
        
        print(f"📄 Created sample document: {os.path.basename(temp_file_path)}")
        
        try:
            # Upload document
            upload_result = rag_manager.upload_document(temp_file_path)
            if upload_result.get('success'):
                print(f"✅ Document uploaded: {upload_result['chunks_created']} chunks created")
            else:
                print(f"❌ Upload failed: {upload_result.get('error', 'Unknown error')}")
                return
            
            # Test document retrieval
            print("\n🔍 Testing document search...")
            search_results = rag_manager.retrieve_relevant_chunks("quantitative analysis", max_chunks=2)
            print(f"Found {len(search_results)} relevant chunks")
            
            if search_results:
                print("Sample retrieved content:")
                print(f"  '{search_results[0]['content'][:100]}...'")
            
            # Test enhanced analysis (without actual LLM call)
            print("\n🤖 Testing analysis enhancement...")
            
            # Mock trading data
            mock_variance_data = {
                'total_variance': 50000,
                'budget_total': 1000000,
                'actual_total': 1050000,
                'variance_percentage': 5.0
            }
            
            # Test variance enhancement
            print("📊 Testing quantitative analysis enhancement...")
            variance_result = rag_analyzer.enhance_variance_analysis(
                variance_data=mock_variance_data,
                analysis_context="Standard quantitative analysis showing 5% positive variance"
            )
            
            print(f"Enhancement result: {type(variance_result)} with {len(variance_result)} keys")
            
            # Test trend enhancement
            print("📈 Testing trend analysis enhancement...")
            mock_trend_data = {
                'trends': ['increasing', 'stable', 'growing'],
                'growth_rate': 15.5
            }
            
            trend_result = rag_analyzer.enhance_trend_analysis(
                trend_data=mock_trend_data,
                analysis_context="Trend analysis shows steady growth"
            )
            
            print(f"Trend enhancement result: {type(trend_result)} with {len(trend_result)} keys")
            
            # Summary
            print("\n📋 Document Summary:")
            doc_summary = rag_manager.get_document_summary()
            for doc_id, info in doc_summary.items():
                print(f"  📄 {info.get('filename', 'Unknown')}: {info.get('chunks', 0)} chunks")
            
            print("\n🎉 RAG Demo completed successfully!")
            print("✅ RAG functionality is working and ready for integration")
            
        finally:
            # Clean up
            os.unlink(temp_file_path)
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required modules are available")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_rag_functionality()
