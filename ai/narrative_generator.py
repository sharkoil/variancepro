"""
Narrative Generator for VariancePro
Creates AI-powered financial narratives and summaries with standardized formatting
"""

from typing import Dict, Any, List, Optional
from config.settings import Settings
from .llm_interpreter import LLMInterpreter, LLMResponse


class NarrativeGenerator:
    """
    Generate AI-powered financial narratives with consistent formatting
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
        Generate comprehensive summary from analysis results with standardized formatting
        
        Args:
            analysis_results: Dictionary with analysis results
            dataset_info: Optional dataset information
            
        Returns:
            Generated summary text with proper business formatting
        """
        # Build context for LLM
        context = {
            'analysis_results': analysis_results
        }
        
        if dataset_info:
            context['dataset_info'] = dataset_info
        
        # Create summary prompt that enforces formatting standards
        prompt = self._build_summary_prompt(analysis_results, dataset_info)
        
        # Get LLM response
        response = self.llm.query_llm(prompt, context)
        
        if response.success:
            # Clean and format the response
            return self._clean_and_format_response(response.content)
        else:
            return self._generate_fallback_summary(analysis_results)
    
    def generate_insights(self, data_summary: Dict[str, Any], analysis_type: str = "general") -> List[str]:
        """
        Generate actionable insights from data with proper formatting
        
        Args:
            data_summary: Summary of dataset
            analysis_type: Type of analysis performed
            
        Returns:
            List of clean, actionable insight strings
        """
        # Build context
        context = {
            'dataset_info': data_summary,
            'analysis_type': analysis_type
        }
        
        # Create insights prompt with formatting requirements
        prompt = self._build_insights_prompt(data_summary, analysis_type)
        
        # Get LLM response
        response = self.llm.query_llm(prompt, context)
        
        if response.success:
            # Process response to extract clean insights
            processed = self.llm.process_response(response.content)
            insights = processed.get('key_insights', [response.content])
            return [self._clean_insight_text(insight) for insight in insights]
        else:
            return self._generate_fallback_insights(data_summary, analysis_type)
    
    def create_executive_summary(self, analysis_results: Dict[str, Any], dataset_info: Dict[str, Any]) -> str:
        """
        Create executive-level summary with standardized business formatting
        
        Args:
            analysis_results: Complete analysis results
            dataset_info: Dataset information
            
        Returns:
            Executive summary text with proper business structure
        """
        context = {
            'analysis_results': analysis_results,
            'dataset_info': dataset_info
        }
        
        prompt = self._build_executive_prompt()
        
        response = self.llm.query_llm(prompt, context)
        
        if response.success:
            return self._clean_and_format_response(response.content)
        else:
            return self._generate_fallback_executive_summary(analysis_results, dataset_info)
    
    def explain_analysis(self, analysis_type: str, results: Dict[str, Any]) -> str:
        """
        Explain what an analysis means in business terms with proper formatting
        
        Args:
            analysis_type: Type of analysis (e.g., "contribution", "variance")
            results: Analysis results
            
        Returns:
            Clean business explanation without technical jargon
        """
        context = {
            'analysis_results': results,
            'analysis_type': analysis_type
        }
        
        prompt = self._build_explanation_prompt(analysis_type)
        
        response = self.llm.query_llm(prompt, context)
        
        if response.success:
            return self._clean_and_format_response(response.content)
        else:
            return self._generate_fallback_explanation(analysis_type, results)
    
    def _build_summary_prompt(self, analysis_results: Dict[str, Any], dataset_info: Optional[Dict[str, Any]]) -> str:
        """Build prompt for summary generation with formatting requirements"""
        prompt_parts = [
            "Generate a comprehensive financial analysis summary based on the provided data and analysis results.",
            "",
            "FORMATTING REQUIREMENTS:",
            "- Use clear, professional business language",
            "- NO code snippets, SQL queries, or technical syntax",
            "- State all assumptions clearly",
            "- Use bullet points for key findings",
            "- Include specific numbers and percentages from analysis",
            "- Structure with: Overview, Key Findings, Business Implications, Recommendations",
            "",
            "CONTENT REQUIREMENTS:",
            "- Focus on business impact and actionable insights",
            "- Explain what the numbers mean for business operations",
            "- Avoid technical jargon and statistical terms",
            "- State data assumptions and limitations clearly",
            "",
            "Create a professional summary suitable for business stakeholders."
        ]
        
        return "\n".join(prompt_parts)
    
    def _build_insights_prompt(self, data_summary: Dict[str, Any], analysis_type: str) -> str:
        """Build prompt for insights generation with formatting standards"""
        prompt_parts = [
            f"Based on this {analysis_type} analysis, identify 3-5 key business insights.",
            "",
            "REQUIREMENTS FOR EACH INSIGHT:",
            "• Must be actionable and specific to business operations",
            "• Include relevant data points or percentages",
            "• Focus on business impact and implications",
            "• Suggest concrete next steps or actions",
            "• NO technical jargon, code, or complex statistical terms",
            "",
            "FORMATTING:",
            "• Write in clear, simple business language",
            "• State any assumptions made",
            "• Keep each insight to 1-2 sentences maximum",
            "• Focus on 'what this means for the business'",
            "",
            "Provide actionable business insights, not technical analysis."
        ]
        
        return "\n".join(prompt_parts)
    
    def _build_executive_prompt(self) -> str:
        """Build prompt for executive summary with business focus"""
        return (
            "Create a concise executive summary of this financial analysis suitable for senior management.\n\n"
            "REQUIREMENTS:\n"
            "• Under 200 words total\n"
            "• Use bullet points for key findings\n"
            "• Focus on business implications and strategic insights\n"
            "• NO technical details, code, or complex statistical terms\n"
            "• State key assumptions clearly\n"
            "• Include recommended actions\n"
            "• Write in executive-level business language\n\n"
            "Structure: Executive Overview • Key Performance Indicators • Strategic Recommendations"
        )
    
    def _build_explanation_prompt(self, analysis_type: str) -> str:
        """Build prompt for analysis explanation"""
        return (
            f"Explain what the {analysis_type} analysis results mean in simple business terms.\n\n"
            "REQUIREMENTS:\n"
            "• Focus on business implications and actionable insights\n"
            "• Avoid technical jargon and statistical terminology\n"
            "• Explain what actions should be taken based on findings\n"
            "• State any assumptions clearly\n"
            "• NO code examples or technical syntax\n"
            "• Use clear, professional business language\n\n"
            "Answer: What do these results mean for business operations and decision-making?"
        )
    
    def _clean_and_format_response(self, content: str) -> str:
        """Clean and format LLM response to ensure no code snippets"""
        lines = content.split('\n')
        cleaned_lines = []
        skip_code_block = False
        
        for line in lines:
            line = line.strip()
            
            # Skip code blocks
            if line.startswith('```') or line.startswith('`'):
                skip_code_block = not skip_code_block
                continue
            
            if skip_code_block:
                continue
            
            # Remove other code-like patterns
            if any(pattern in line.lower() for pattern in ['select ', 'from ', 'where ', 'import ', 'def ', 'class ', '= pd.']):
                continue
            
            # Clean up formatting
            if line:
                cleaned_lines.append(line)
            elif cleaned_lines and cleaned_lines[-1]:  # Only add empty lines if previous line has content
                cleaned_lines.append("")
        
        return '\n'.join(cleaned_lines).strip()
    
    def _clean_insight_text(self, insight: str) -> str:
        """Clean individual insight text"""
        # Remove common formatting artifacts
        insight = insight.strip()
        insight = insight.replace('**', '').replace('•', '').replace('*', '')
        
        # Remove code-like patterns
        if any(pattern in insight.lower() for pattern in ['```', 'select', 'import', 'def ', '= pd.']):
            return ""
        
        return insight.strip()
    
    def _generate_fallback_summary(self, analysis_results: Dict[str, Any]) -> str:
        """Generate fallback summary when LLM is unavailable"""
        summary_parts = [
            "📊 **ANALYSIS SUMMARY**",
            "",
            "**Status**: Analysis completed successfully",
            "**Assumptions**: Standard financial analysis methodology applied",
            ""
        ]
        
        # Extract key metrics if available
        if 'pareto_analysis' in analysis_results:
            pareto = analysis_results['pareto_analysis']
            top_contributors = pareto.get('top_contributors', {})
            
            summary_parts.extend([
                "**Key Finding**: Business follows 80/20 principle",
                f"• Top {top_contributors.get('count', 'N/A')} contributors generate "
                f"{top_contributors.get('value_percentage', 'N/A')}% of total value",
                "• Concentration indicates opportunity for focused strategy"
            ])
        
        if 'insights' in analysis_results:
            insights = analysis_results['insights']
            if 'summary' in insights:
                summary_parts.append(f"**Total Value Analyzed**: {insights['summary'].get('total_value', 'N/A')}")
        
        summary_parts.extend([
            "",
            "**Note**: Detailed AI analysis unavailable - LLM service not accessible.",
            "**Recommendation**: Review numerical results above for specific findings."
        ])
        
        return "\n".join(summary_parts)
    
    def _generate_fallback_insights(self, data_summary: Dict[str, Any], analysis_type: str) -> List[str]:
        """Generate fallback insights when LLM is unavailable"""
        insights = [
            f"{analysis_type.title()} analysis completed successfully with standard business assumptions",
            f"Dataset contains {data_summary.get('total_rows', 'N/A')} rows suitable for analysis",
            "Detailed insights require LLM service - check Ollama connection for AI-powered insights",
            "Numerical results provide core business metrics for decision-making"
        ]
        
        return insights
    
    def _generate_fallback_executive_summary(self, analysis_results: Dict[str, Any], dataset_info: Dict[str, Any]) -> str:
        """Generate fallback executive summary"""
        return (
            "**EXECUTIVE SUMMARY**\n\n"
            f"• Financial analysis completed on {dataset_info.get('total_rows', 'N/A')} data records\n"
            f"• {len(analysis_results)} analysis components processed successfully\n"
            "• Key assumptions: Standard financial analysis methodology applied\n"
            "• Detailed AI insights unavailable (LLM service offline)\n"
            "• Recommendation: Review numerical analysis results for business metrics\n"
            "• Next steps: Ensure AI service connectivity for enhanced insights"
        )
    
    def _generate_fallback_explanation(self, analysis_type: str, results: Dict[str, Any]) -> str:
        """Generate fallback explanation"""
        explanations = {
            'contribution': (
                "Contribution analysis identifies which business categories drive the most value "
                "using the 80/20 principle. Key assumption: Top performers follow Pareto distribution. "
                "Business implication: Focus resources on high-impact contributors for maximum ROI."
            ),
            'variance': (
                "Variance analysis compares actual performance against budgets or targets. "
                "Key assumption: Budget represents expected performance baseline. "
                "Business implication: Identifies areas needing attention and resource reallocation."
            ),
            'financial': (
                "Financial analysis examines key business metrics and performance trends. "
                "Key assumption: Historical data predicts future patterns. "
                "Business implication: Provides insights for strategic planning and performance improvement."
            )
        }
        
        base_explanation = explanations.get(analysis_type, 
            f"{analysis_type.title()} analysis provides business insights from your data "
            "using standard financial analysis assumptions to inform strategic decisions."
        )
        
        return f"{base_explanation}\n\nNote: Enhanced AI explanation unavailable - LLM service not accessible."
    
    def format_for_chat(self, content: str, title: Optional[str] = None) -> str:
        """
        Format narrative content for chat display with standardized structure
        
        Args:
            content: Content to format
            title: Optional title
            
        Returns:
            Formatted content for chat with clean business presentation
        """
        formatted_parts = []
        
        if title:
            formatted_parts.append(f"📋 **{title.upper()}**")
            formatted_parts.append("")
        
        # Clean and format content - ensure no code snippets
        content = self._clean_and_format_response(content)
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted_parts.append("")
                continue
            
            # Format different types of content with business focus
            if line.startswith(('Key Finding', 'Finding', 'Insight')):
                formatted_parts.append(f"🎯 **{line}**")
            elif line.startswith(('Recommend', 'Action', 'Next Step')):
                formatted_parts.append(f"💡 **{line}**")
            elif line.startswith(('Assumption', 'Note', 'Important', 'Warning')):
                formatted_parts.append(f"⚠️ **{line}**")
            elif line.startswith(('Summary', 'Overview')):
                formatted_parts.append(f"📊 **{line}**")
            else:
                formatted_parts.append(line)
        
        return "\n".join(formatted_parts)
    
    def set_tone(self, tone: str):
        """Set narrative tone"""
        if tone in ["professional", "casual", "technical"]:
            self.tone = tone
    
    def get_status(self) -> Dict[str, Any]:
        """Get narrative generator status"""
        return {
            'llm_available': self.llm.is_available,
            'tone': self.tone,
            'persona': self.persona,
            'llm_status': self.llm.get_status(),
            'formatting_standards': 'Applied - no code snippets, clear assumptions, business focus'
        }
