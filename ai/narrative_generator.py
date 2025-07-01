"""
Narrative Generator for VariancePro
Creates AI-powered financial narratives and summaries
"""

from typing import Dict, Any, List, Optional
from config.settings import Settings
from .llm_interpreter import LLMInterpreter, LLMResponse


class NarrativeGenerator:
    """
    Generate AI-powered financial narratives
    Creates professional summaries and insights from analysis results
    """
    
    def __init__(self, llm_interpreter: LLMInterpreter):
        """
        Initialize narrative generator
        
        Args:
            llm_interpreter: LLM interpreter instance
        """
        self.llm = llm_interpreter
        self.tone = "professional"
        self.persona = "Aria Sterling"
        
    def generate_summary(self, analysis_results: Dict[str, Any], dataset_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate comprehensive summary from analysis results
        
        Args:
            analysis_results: Dictionary with analysis results
            dataset_info: Optional dataset information
            
        Returns:
            Generated summary text
        """
        # Build context for LLM
        context = {
            'analysis_results': analysis_results
        }
        
        if dataset_info:
            context['dataset_info'] = dataset_info
        
        # Create summary prompt
        prompt = self._build_summary_prompt(analysis_results, dataset_info)
        
        # Get LLM response
        response = self.llm.query_llm(prompt, context)
        
        if response.success:
            return response.content
        else:
            return self._generate_fallback_summary(analysis_results)
    
    def generate_insights(self, data_summary: Dict[str, Any], analysis_type: str = "general") -> List[str]:
        """
        Generate actionable insights from data
        
        Args:
            data_summary: Summary of dataset
            analysis_type: Type of analysis performed
            
        Returns:
            List of insight strings
        """
        # Build context
        context = {
            'dataset_info': data_summary,
            'analysis_type': analysis_type
        }
        
        # Create insights prompt
        prompt = self._build_insights_prompt(data_summary, analysis_type)
        
        # Get LLM response
        response = self.llm.query_llm(prompt, context)
        
        if response.success:
            # Process response to extract insights
            processed = self.llm.process_response(response.content)
            return processed.get('key_insights', [response.content])
        else:
            return self._generate_fallback_insights(data_summary, analysis_type)
    
    def create_executive_summary(self, analysis_results: Dict[str, Any], dataset_info: Dict[str, Any]) -> str:
        """
        Create executive-level summary
        
        Args:
            analysis_results: Complete analysis results
            dataset_info: Dataset information
            
        Returns:
            Executive summary text
        """
        context = {
            'analysis_results': analysis_results,
            'dataset_info': dataset_info
        }
        
        prompt = (
            "Create a concise executive summary of this financial analysis. "
            "Focus on the most critical business insights, key performance indicators, "
            "and strategic recommendations. Keep it under 200 words and use bullet points "
            "for key findings. This will be presented to senior management."
        )
        
        response = self.llm.query_llm(prompt, context)
        
        if response.success:
            return response.content
        else:
            return self._generate_fallback_executive_summary(analysis_results, dataset_info)
    
    def explain_analysis(self, analysis_type: str, results: Dict[str, Any]) -> str:
        """
        Explain what an analysis means in business terms
        
        Args:
            analysis_type: Type of analysis (e.g., "contribution", "variance")
            results: Analysis results
            
        Returns:
            Explanation text
        """
        context = {
            'analysis_results': results,
            'analysis_type': analysis_type
        }
        
        prompt = (
            f"Explain what the {analysis_type} analysis results mean in simple business terms. "
            "Focus on what actions should be taken based on these findings. "
            "Avoid technical jargon and explain the business implications clearly."
        )
        
        response = self.llm.query_llm(prompt, context)
        
        if response.success:
            return response.content
        else:
            return self._generate_fallback_explanation(analysis_type, results)
    
    def _build_summary_prompt(self, analysis_results: Dict[str, Any], dataset_info: Optional[Dict[str, Any]]) -> str:
        """
        Build prompt for summary generation
        
        Args:
            analysis_results: Analysis results
            dataset_info: Optional dataset info
            
        Returns:
            Formatted prompt
        """
        prompt_parts = [
            "Generate a comprehensive financial analysis summary based on the provided data and analysis results.",
            "Structure your response with:",
            "1. Key Performance Overview",
            "2. Major Findings", 
            "3. Business Implications",
            "4. Recommended Actions",
            "",
            "Use specific numbers and percentages from the analysis results.",
            "Keep the tone professional but accessible to business stakeholders."
        ]
        
        return "\n".join(prompt_parts)
    
    def _build_insights_prompt(self, data_summary: Dict[str, Any], analysis_type: str) -> str:
        """
        Build prompt for insights generation
        
        Args:
            data_summary: Data summary
            analysis_type: Analysis type
            
        Returns:
            Formatted prompt
        """
        prompt_parts = [
            f"Based on this {analysis_type} analysis, identify 3-5 key business insights.",
            "Each insight should:",
            "• Be actionable and specific",
            "• Include relevant data points or percentages",
            "• Focus on business impact",
            "• Suggest next steps or implications",
            "",
            "Format as bullet points with clear, concise statements."
        ]
        
        return "\n".join(prompt_parts)
    
    def _generate_fallback_summary(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generate fallback summary when LLM is unavailable
        
        Args:
            analysis_results: Analysis results
            
        Returns:
            Fallback summary text
        """
        summary_parts = [
            "📊 **ANALYSIS SUMMARY**",
            "",
            "**Status**: Analysis completed successfully",
        ]
        
        # Extract key metrics if available
        if 'pareto_analysis' in analysis_results:
            pareto = analysis_results['pareto_analysis']
            top_contributors = pareto.get('top_contributors', {})
            
            summary_parts.extend([
                f"**Key Finding**: Top {top_contributors.get('count', 'N/A')} contributors generate "
                f"{top_contributors.get('value_percentage', 'N/A')}% of total value",
            ])
        
        if 'insights' in analysis_results:
            insights = analysis_results['insights']
            if 'summary' in insights:
                summary_parts.append(f"**Total Value**: {insights['summary'].get('total_value', 'N/A')}")
        
        summary_parts.extend([
            "",
            "**Note**: Detailed AI analysis unavailable - LLM service not accessible.",
            "The numerical analysis results above provide the core findings."
        ])
        
        return "\n".join(summary_parts)
    
    def _generate_fallback_insights(self, data_summary: Dict[str, Any], analysis_type: str) -> List[str]:
        """
        Generate fallback insights when LLM is unavailable
        
        Args:
            data_summary: Data summary
            analysis_type: Analysis type
            
        Returns:
            List of fallback insights
        """
        insights = [
            f"✅ {analysis_type.title()} analysis completed successfully",
            f"📊 Dataset contains {data_summary.get('total_rows', 'N/A')} rows of data",
            "🎯 Detailed insights require LLM service - please check Ollama connection",
            "📈 Numerical results are available in the analysis output above"
        ]
        
        return insights
    
    def _generate_fallback_executive_summary(self, analysis_results: Dict[str, Any], dataset_info: Dict[str, Any]) -> str:
        """
        Generate fallback executive summary
        
        Args:
            analysis_results: Analysis results
            dataset_info: Dataset info
            
        Returns:
            Fallback executive summary
        """
        return (
            "**EXECUTIVE SUMMARY**\n\n"
            f"• Analysis completed on dataset with {dataset_info.get('total_rows', 'N/A')} records\n"
            f"• {len(analysis_results)} analysis components processed\n"
            "• Detailed AI-generated insights unavailable (LLM service offline)\n"
            "• Raw analysis results provide core numerical findings\n"
            "• Recommend reviewing detailed analysis output for specific metrics"
        )
    
    def _generate_fallback_explanation(self, analysis_type: str, results: Dict[str, Any]) -> str:
        """
        Generate fallback explanation
        
        Args:
            analysis_type: Analysis type
            results: Results dictionary
            
        Returns:
            Fallback explanation
        """
        explanations = {
            'contribution': (
                "Contribution analysis identifies which categories (customers, products, regions) "
                "drive the most value using the 80/20 principle. This helps focus resources on "
                "the most important contributors to your business."
            ),
            'variance': (
                "Variance analysis compares actual performance against budgets or targets. "
                "It identifies areas of over/under-performance and helps understand what's "
                "driving differences from planned results."
            ),
            'financial': (
                "Financial analysis examines key metrics like revenue trends, profitability, "
                "and growth patterns. It provides insights into business performance and "
                "identifies opportunities for improvement."
            )
        }
        
        base_explanation = explanations.get(analysis_type, 
            f"{analysis_type.title()} analysis provides insights into your business data "
            "to help inform strategic decisions."
        )
        
        return f"{base_explanation}\n\nNote: Detailed AI explanation unavailable - LLM service not accessible."
    
    def format_for_chat(self, content: str, title: Optional[str] = None) -> str:
        """
        Format narrative content for chat display
        
        Args:
            content: Content to format
            title: Optional title
            
        Returns:
            Formatted content for chat
        """
        formatted_parts = []
        
        if title:
            formatted_parts.append(f"📋 **{title.upper()}**")
            formatted_parts.append("")
        
        # Clean and format content
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                formatted_parts.append("")
                continue
            
            # Format different types of content
            if line.startswith(('Key Finding', 'Finding', 'Insight')):
                formatted_parts.append(f"🎯 **{line}**")
            elif line.startswith(('Recommend', 'Action', 'Next Step')):
                formatted_parts.append(f"💡 **{line}**")
            elif line.startswith(('Note', 'Important', 'Warning')):
                formatted_parts.append(f"⚠️ **{line}**")
            elif line.startswith(('Summary', 'Overview')):
                formatted_parts.append(f"📊 **{line}**")
            else:
                formatted_parts.append(line)
        
        return "\n".join(formatted_parts)
    
    def set_tone(self, tone: str):
        """
        Set narrative tone
        
        Args:
            tone: Tone to use ("professional", "casual", "technical")
        """
        if tone in ["professional", "casual", "technical"]:
            self.tone = tone
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get narrative generator status
        
        Returns:
            Status dictionary
        """
        return {
            'llm_available': self.llm.is_available,
            'tone': self.tone,
            'persona': self.persona,
            'llm_status': self.llm.get_status()
        }
