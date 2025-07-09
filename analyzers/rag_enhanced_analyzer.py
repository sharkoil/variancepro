"""
RAG Enhanced Analyzer - Integrates document context with data analysis
Enhances variance, trends, and Top N analysis with supplementary document insights
"""

import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from analyzers.rag_document_manager import RAGDocumentManager

class RAGEnhancedAnalyzer:
    """
    Enhances data analysis with RAG (Retrieval-Augmented Generation) pattern
    
    This class:
    1. Integrates with existing analyzers (variance, contributor, timescale)
    2. Enhances LLM responses with document context
    3. Provides domain-specific insights from uploaded materials
    4. Maintains analysis quality with or without supplementary documents
    """
    
    def __init__(self, rag_manager: RAGDocumentManager):
        """
        Initialize RAG Enhanced Analyzer
        
        Args:
            rag_manager: Initialized RAG Document Manager instance
        """
        self.rag_manager = rag_manager
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "gemma3:latest"  # Updated to available model
        print("🤖 RAG Enhanced Analyzer initialized")
    
    def enhance_variance_analysis(
        self, 
        variance_data: Dict[str, Any], 
        analysis_context: str
    ) -> Dict[str, Any]:
        """
        Enhance quantitative analysis with RAG context
        
        Args:
            variance_data: Original quantitative analysis results
            analysis_context: Context about the quantitative analysis
            
        Returns:
            Enhanced analysis with supplementary insights
        """
        try:
            # Get enhanced context from uploaded documents
            enhanced_context = self.rag_manager.get_enhanced_context_for_llm(
                analysis_type="variance",
                data_context=analysis_context
            )
            
            # Create enhanced prompt for LLM
            prompt = self._create_variance_analysis_prompt(
                variance_data, 
                analysis_context, 
                enhanced_context
            )
            
            # Get enhanced analysis from LLM
            enhanced_insights = self._query_ollama(prompt)
            
            # Combine original and enhanced analysis
            result = {
                "status": "success",
                "original_analysis": variance_data,
                "enhanced_insights": enhanced_insights,
                "rag_context_used": bool(enhanced_context.strip()),
                "generated_at": datetime.now().isoformat(),
                "analysis_type": "variance_with_rag"
            }
            
            print("📊 Quantitative analysis enhanced with RAG context")
            return result
            
        except Exception as e:
            print(f"⚠️ RAG enhancement failed, returning original analysis: {e}")
            
            # Fallback to original analysis
            return {
                "status": "fallback",
                "original_analysis": variance_data,
                "enhanced_insights": "RAG enhancement unavailable. Analysis based on data patterns only.",
                "rag_context_used": False,
                "error": str(e),
                "generated_at": datetime.now().isoformat(),
                "analysis_type": "variance_fallback"
            }
    
    def enhance_trend_analysis(
        self, 
        trend_data: Dict[str, Any], 
        analysis_context: str
    ) -> Dict[str, Any]:
        """
        Enhance trend analysis with RAG context
        
        Args:
            trend_data: Original trend analysis results
            analysis_context: Context about the trend analysis
            
        Returns:
            Enhanced analysis with supplementary insights
        """
        try:
            # Get enhanced context from uploaded documents
            enhanced_context = self.rag_manager.get_enhanced_context_for_llm(
                analysis_type="trends",
                data_context=analysis_context
            )
            
            # Create enhanced prompt for LLM
            prompt = self._create_trend_analysis_prompt(
                trend_data, 
                analysis_context, 
                enhanced_context
            )
            
            # Get enhanced analysis from LLM
            enhanced_insights = self._query_ollama(prompt)
            
            # Combine original and enhanced analysis
            result = {
                "status": "success",
                "original_analysis": trend_data,
                "enhanced_insights": enhanced_insights,
                "rag_context_used": bool(enhanced_context.strip()),
                "generated_at": datetime.now().isoformat(),
                "analysis_type": "trends_with_rag"
            }
            
            print("📈 Trend analysis enhanced with RAG context")
            return result
            
        except Exception as e:
            print(f"⚠️ RAG enhancement failed, returning original analysis: {e}")
            
            # Fallback to original analysis
            return {
                "status": "fallback",
                "original_analysis": trend_data,
                "enhanced_insights": "RAG enhancement unavailable. Analysis based on data patterns only.",
                "rag_context_used": False,
                "error": str(e),
                "generated_at": datetime.now().isoformat(),
                "analysis_type": "trends_fallback"
            }
    
    def enhance_top_n_analysis(
        self, 
        top_n_data: Dict[str, Any], 
        analysis_context: str
    ) -> Dict[str, Any]:
        """
        Enhance Top N analysis with RAG context
        
        Args:
            top_n_data: Original Top N analysis results
            analysis_context: Context about the Top N analysis
            
        Returns:
            Enhanced analysis with supplementary insights
        """
        try:
            # Get enhanced context from uploaded documents
            enhanced_context = self.rag_manager.get_enhanced_context_for_llm(
                analysis_type="top_n",
                data_context=analysis_context
            )
            
            # Create enhanced prompt for LLM
            prompt = self._create_top_n_analysis_prompt(
                top_n_data, 
                analysis_context, 
                enhanced_context
            )
            
            # Get enhanced analysis from LLM
            enhanced_insights = self._query_ollama(prompt)
            
            # Combine original and enhanced analysis
            result = {
                "status": "success",
                "original_analysis": top_n_data,
                "enhanced_insights": enhanced_insights,
                "rag_context_used": bool(enhanced_context.strip()),
                "generated_at": datetime.now().isoformat(),
                "analysis_type": "top_n_with_rag"
            }
            
            print("🔝 Top N analysis enhanced with RAG context")
            return result
            
        except Exception as e:
            print(f"⚠️ RAG enhancement failed, returning original analysis: {e}")
            
            # Fallback to original analysis
            return {
                "status": "fallback",
                "original_analysis": top_n_data,
                "enhanced_insights": "RAG enhancement unavailable. Analysis based on data patterns only.",
                "rag_context_used": False,
                "error": str(e),
                "generated_at": datetime.now().isoformat(),
                "analysis_type": "top_n_fallback"
            }
    
    def enhance_general_analysis(
        self, 
        analysis_data: Dict[str, Any], 
        analysis_context: str,
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Enhance any general analysis with RAG context
        
        Args:
            analysis_data: Original analysis results
            analysis_context: Context about the analysis
            analysis_type: Type of analysis being performed
            
        Returns:
            Enhanced analysis with supplementary insights
        """
        try:
            # Get enhanced context from uploaded documents
            enhanced_context = self.rag_manager.get_enhanced_context_for_llm(
                analysis_type=analysis_type,
                data_context=analysis_context
            )
            
            # Create enhanced prompt for LLM
            prompt = self._create_general_analysis_prompt(
                analysis_data, 
                analysis_context, 
                enhanced_context,
                analysis_type
            )
            
            # Get enhanced analysis from LLM
            enhanced_insights = self._query_ollama(prompt)
            
            # Combine original and enhanced analysis
            result = {
                "status": "success",
                "original_analysis": analysis_data,
                "enhanced_insights": enhanced_insights,
                "rag_context_used": bool(enhanced_context.strip()),
                "generated_at": datetime.now().isoformat(),
                "analysis_type": f"{analysis_type}_with_rag"
            }
            
            print(f"🔍 {analysis_type.title()} analysis enhanced with RAG context")
            return result
            
        except Exception as e:
            print(f"⚠️ RAG enhancement failed, returning original analysis: {e}")
            
            # Fallback to original analysis
            return {
                "status": "fallback",
                "original_analysis": analysis_data,
                "enhanced_insights": "RAG enhancement unavailable. Analysis based on data patterns only.",
                "rag_context_used": False,
                "error": str(e),
                "generated_at": datetime.now().isoformat(),
                "analysis_type": f"{analysis_type}_fallback"
            }
    
    def _create_variance_analysis_prompt(
        self, 
        variance_data: Dict[str, Any], 
        context: str, 
        enhanced_context: str
    ) -> str:
        """
        Create enhanced prompt for quantitative analysis
        
        Args:
            variance_data: Quantitative analysis data
            context: Analysis context
            enhanced_context: RAG-enhanced context
            
        Returns:
            Formatted prompt for LLM
        """
        prompt = f"""
You are a financial analyst providing quantitative analysis insights. 

DATA ANALYSIS CONTEXT:
{context}

QUANTITATIVE ANALYSIS DATA:
{json.dumps(variance_data, indent=2, default=str)}

{enhanced_context}

Please provide a comprehensive quantitative analysis that includes:

1. **EXECUTIVE SUMMARY**: Key variance findings and their significance

2. **VARIANCE BREAKDOWN**: 
   - Favorable vs unfavorable variances
   - Magnitude and percentage analysis
   - Root cause identification

3. **BUSINESS IMPACT ASSESSMENT**:
   - Financial implications of variances
   - Operational impact analysis
   - Risk assessment

4. **SUPPLEMENTARY INSIGHTS** (if context available):
   - Industry benchmark comparisons
   - Best practice recommendations
   - Historical context and precedents

5. **ACTIONABLE RECOMMENDATIONS**:
   - Immediate corrective actions
   - Process improvements
   - Monitoring recommendations

Format your response for business stakeholders with clear, actionable insights.
Use bullet points for key findings and maintain professional tone.
"""
        return prompt
    
    def _create_trend_analysis_prompt(
        self, 
        trend_data: Dict[str, Any], 
        context: str, 
        enhanced_context: str
    ) -> str:
        """
        Create enhanced prompt for trend analysis
        
        Args:
            trend_data: Trend analysis data
            context: Analysis context
            enhanced_context: RAG-enhanced context
            
        Returns:
            Formatted prompt for LLM
        """
        prompt = f"""
You are a financial analyst providing trend analysis insights.

DATA ANALYSIS CONTEXT:
{context}

TREND ANALYSIS DATA:
{json.dumps(trend_data, indent=2, default=str)}

{enhanced_context}

Please provide a comprehensive trend analysis that includes:

1. **TREND OVERVIEW**: Summary of identified patterns and directions

2. **TREND ANALYSIS**:
   - Growth/decline patterns
   - Seasonality and cyclical patterns
   - Trend strength and sustainability

3. **FORECASTING INSIGHTS**:
   - Projected future performance
   - Confidence levels and assumptions
   - Risk factors and scenarios

4. **SUPPLEMENTARY CONTEXT** (if available):
   - Industry trend comparisons
   - Market condition influences
   - Historical precedents

5. **STRATEGIC RECOMMENDATIONS**:
   - Opportunity identification
   - Risk mitigation strategies
   - Investment and resource allocation guidance

Focus on actionable insights that support strategic decision-making.
Highlight both opportunities and risks identified in the trends.
"""
        return prompt
    
    def _create_top_n_analysis_prompt(
        self, 
        top_n_data: Dict[str, Any], 
        context: str, 
        enhanced_context: str
    ) -> str:
        """
        Create enhanced prompt for Top N analysis
        
        Args:
            top_n_data: Top N analysis data
            context: Analysis context
            enhanced_context: RAG-enhanced context
            
        Returns:
            Formatted prompt for LLM
        """
        prompt = f"""
You are a financial analyst providing Top N performance analysis insights.

DATA ANALYSIS CONTEXT:
{context}

TOP N ANALYSIS DATA:
{json.dumps(top_n_data, indent=2, default=str)}

{enhanced_context}

Please provide a comprehensive Top N analysis that includes:

1. **PERFORMANCE OVERVIEW**: Summary of top and bottom performers

2. **PERFORMANCE ANALYSIS**:
   - Key differentiators between top and bottom performers
   - Performance gaps and distribution
   - Consistency and volatility assessment

3. **SUCCESS FACTOR IDENTIFICATION**:
   - Common characteristics of top performers
   - Failure patterns in bottom performers
   - Performance drivers analysis

4. **SUPPLEMENTARY INSIGHTS** (if available):
   - Industry benchmarking
   - Best practice identification
   - Competitive positioning

5. **OPTIMIZATION RECOMMENDATIONS**:
   - Strategies to improve bottom performers
   - Methods to sustain top performance
   - Resource reallocation opportunities

Provide specific, actionable recommendations for performance improvement.
Focus on scalable insights that can be applied across the organization.
"""
        return prompt
    
    def _create_general_analysis_prompt(
        self, 
        analysis_data: Dict[str, Any], 
        context: str, 
        enhanced_context: str,
        analysis_type: str
    ) -> str:
        """
        Create enhanced prompt for general analysis
        
        Args:
            analysis_data: Analysis data
            context: Analysis context
            enhanced_context: RAG-enhanced context
            analysis_type: Type of analysis
            
        Returns:
            Formatted prompt for LLM
        """
        prompt = f"""
You are a financial analyst providing {analysis_type} analysis insights.

DATA ANALYSIS CONTEXT:
{context}

ANALYSIS DATA:
{json.dumps(analysis_data, indent=2, default=str)}

{enhanced_context}

Please provide a comprehensive analysis that includes:

1. **KEY FINDINGS**: Most important insights from the data

2. **DATA INTERPRETATION**: 
   - Pattern identification
   - Significance assessment
   - Context and implications

3. **BUSINESS IMPACT**:
   - Financial implications
   - Operational considerations
   - Strategic relevance

4. **SUPPLEMENTARY INSIGHTS** (if context available):
   - Industry context and benchmarks
   - Best practice applications
   - Relevant precedents and examples

5. **RECOMMENDATIONS**:
   - Actionable next steps
   - Monitoring and tracking suggestions
   - Risk mitigation strategies

Provide clear, business-focused insights that support decision-making.
Use professional language appropriate for executive stakeholders.
"""
        return prompt
    
    def _query_ollama(self, prompt: str) -> str:
        """
        Query Ollama for enhanced analysis
        
        Args:
            prompt: Formatted prompt for LLM
            
        Returns:
            LLM response text
        """
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60  # Longer timeout for comprehensive analysis
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No analysis generated')
            else:
                raise Exception(f"Ollama API returned status {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Failed to get enhanced analysis from LLM: {str(e)}")
    
    def get_rag_status(self) -> Dict[str, Any]:
        """
        Get current RAG system status
        
        Returns:
            Status information about RAG system
        """
        document_summary = self.rag_manager.get_document_summary()
        
        return {
            "rag_enabled": document_summary["total_documents"] > 0,
            "documents_loaded": document_summary["total_documents"],
            "total_chunks": document_summary["total_chunks"],
            "context_size": document_summary["context_size"],
            "ollama_model": self.model_name,
            "last_updated": datetime.now().isoformat()
        }
