"""
News Analyzer Module - Version 2
Analyzes CSV data to identify location columns and generates relevant news queries
"""

import pandas as pd
import requests
import json
import time
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import urllib.parse

class NewsAnalyzer:
    """Analyzes data context and fetches relevant news for business insights"""
    
    def __init__(self, settings):
        """Initialize the News Analyzer"""
        self.settings = settings
        self.news_api_key = getattr(settings, 'news_api_key', None)
        self.last_analysis = None
        self.location_keywords = [
            'state', 'country', 'region', 'city', 'location', 'territory',
            'province', 'county', 'district', 'area', 'zone', 'market',
            'geography', 'locale', 'place'
        ]
    
    def analyze_data_context(self, data: pd.DataFrame, column_info: Dict, llm_interpreter=None) -> Dict:
        """Analyze CSV data to understand business context and identify location data"""
        try:
            # First, identify location columns
            location_columns = self._identify_location_columns(data)
            print(f"[DEBUG] Identified location columns: {location_columns}")
            
            if not location_columns:
                print("[DEBUG] No location columns found")
                return {}
            
            # Get business context
            business_context = self._identify_business_context(data.columns)
            
            # Get date range
            date_range = self._get_date_range(data, column_info.get('date_columns', []))
            
            # Get top locations from data
            top_locations = self._get_top_locations(data, location_columns)
            
            # Create full context
            context = {
                'data_shape': data.shape,
                'columns': list(data.columns),
                'column_types': column_info,
                'location_columns': location_columns,
                'business_context': business_context,
                'date_range': date_range,
                'top_locations': top_locations
            }
            
            print(f"[DEBUG] News context analysis: {context}")
            
            # Generate news query based on context
            search_queries = []
            if llm_interpreter is None:
                from ai.llm_interpreter import LLMInterpreter
                llm_interpreter = LLMInterpreter(self.settings)
                
            # Generate query for top locations
            for location in top_locations[:2]:  # Limit to top 2 locations for diversity
                query_context = context.copy()
                query_context['top_locations'] = [location]
                query = self.generate_news_query(query_context, llm_interpreter)
                if query:
                    search_queries.append(query)
                    print(f"[DEBUG] Generated query for {location}: {query}")
            
            # If no location-specific queries worked, try a general query
            if not search_queries:
                query = self.generate_news_query(context, llm_interpreter)
                if query:
                    search_queries.append(query)
                    print(f"[DEBUG] Generated general query: {query}")
            
            # Fetch news for each query
            all_news_items = []
            for query in search_queries:
                news_items = self.fetch_news(query, max_articles=3)
                all_news_items.extend(news_items)
                print(f"[DEBUG] Found {len(news_items)} news items for query: {query}")
            
            # Create result dictionary
            result = {
                'location_columns': location_columns,
                'business_context': business_context,
                'top_locations': top_locations,
                'search_queries': search_queries,
                'news_items': all_news_items
            }
            
            return result
            
        except Exception as e:
            print(f"[DEBUG] Error in analyze_data_context: {e}")
            return {}

    def _identify_location_columns(self, data: pd.DataFrame) -> List[str]:
        """Identify columns that contain location information"""
        location_columns = []
        
        for col in data.columns:
            # Check if column name suggests location
            if any(keyword in col.lower() for keyword in self.location_keywords):
                location_columns.append(col)
                continue
            
            # Check data patterns (sample values) for common location patterns
            if col in data.select_dtypes(include=['object']).columns:
                sample_values = data[col].dropna().unique()[:10]  # Check first 10 unique values
                
                if len(sample_values) == 0:
                    continue
                
                location_patterns = 0
                for val in sample_values:
                    if not isinstance(val, str):
                        continue
                        
                    val_lower = val.lower().replace('_', ' ')
                    
                    # Check for common US states, countries, or cities
                    if val_lower in set([
                        'alabama', 'alaska', 'arizona', 'arkansas', 'california', 
                        'colorado', 'connecticut', 'delaware', 'florida', 'georgia',
                        'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 'kansas',
                        'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts',
                        'michigan', 'minnesota', 'mississippi', 'missouri', 'montana',
                        'nebraska', 'nevada', 'new hampshire', 'new jersey', 'new mexico',
                        'new york', 'north carolina', 'north dakota', 'ohio', 'oklahoma',
                        'oregon', 'pennsylvania', 'rhode island', 'south carolina', 
                        'south dakota', 'tennessee', 'texas', 'utah', 'vermont', 
                        'virginia', 'washington', 'west virginia', 'wisconsin', 'wyoming',
                        'canada', 'mexico', 'germany', 'france', 'uk', 'china', 'japan',
                        'australia', 'new zealand', 'brazil', 'india'
                    ]):
                        location_patterns += 1
                
                # If majority of sample values look like locations
                if location_patterns >= len(sample_values) * 0.6:
                    location_columns.append(col)
        
        print(f"[DEBUG] Identified location columns: {location_columns}")
        return location_columns
    
    def _identify_business_context(self, columns: List[str]) -> Dict:
        """Identify the type of business data based on column names"""
        context = {
            'industry': 'general',
            'data_type': 'business',
            'key_metrics': []
        }
        
        column_text = ' '.join([col.lower() for col in columns])
        
        # Industry identification
        if any(word in column_text for word in ['sales', 'revenue', 'profit', 'margin']):
            context['industry'] = 'sales'
        elif any(word in column_text for word in ['budget', 'actual', 'forecast', 'variance']):
            context['industry'] = 'finance'
        elif any(word in column_text for word in ['customer', 'client', 'account']):
            context['industry'] = 'customer_service'
        elif any(word in column_text for word in ['product', 'inventory', 'stock']):
            context['industry'] = 'retail'
        elif any(word in column_text for word in ['employee', 'hr', 'payroll']):
            context['industry'] = 'human_resources'
        
        # Key metrics identification
        for col in columns:
            col_lower = col.lower()
            if any(word in col_lower for word in ['revenue', 'sales', 'profit', 'income']):
                context['key_metrics'].append('financial_performance')
            elif any(word in col_lower for word in ['budget', 'actual', 'target']):
                context['key_metrics'].append('budget_performance')
            elif any(word in col_lower for word in ['margin', 'cost', 'expense']):
                context['key_metrics'].append('cost_management')
        
        return context
    
    def _get_date_range(self, data: pd.DataFrame, date_columns: List[str]) -> Dict:
        """Get the date range of the data"""
        if not date_columns:
            return {}
        
        try:
            date_col = date_columns[0]
            dates = pd.to_datetime(data[date_col], errors='coerce').dropna()
            
            if len(dates) > 0:
                return {
                    'start_date': dates.min().strftime('%Y-%m-%d'),
                    'end_date': dates.max().strftime('%Y-%m-%d'),
                    'date_column': date_col
                }
        except:
            pass
            
        return {}
    
    def _get_top_locations(self, data: pd.DataFrame, location_columns: List[str], top_n: int = 5) -> List[str]:
        """Get the top N most frequently occurring locations"""
        if not location_columns:
            return []
            
        top_locations = []
        for col in location_columns:
            if col in data.columns:
                value_counts = data[col].value_counts().head(top_n)
                for loc in value_counts.index:
                    if isinstance(loc, str) and loc.strip():
                        top_locations.append(loc.replace('_', ' '))
                        if len(top_locations) >= top_n:
                            return top_locations
        
        return top_locations
    
    def generate_news_query(self, context: Dict, llm_interpreter=None) -> str:
        """Generate a news search query based on data context"""
        try:
            if llm_interpreter is None:
                from ai.llm_interpreter import LLMInterpreter
                llm_interpreter = LLMInterpreter(self.settings)
            
            # Create prompt for LLM to generate search query
            prompt = f"""
You are a business analyst creating a news search query to find relevant headlines for data analysis.

DATA CONTEXT:
- Business Type: {context.get('business_context', {}).get('industry', 'business')}
- Key Metrics: {context.get('business_context', {}).get('key_metrics', [])}
- Top Locations: {context.get('top_locations', [])}
- Date Range: {context.get('date_range', {})}
- Data Columns: {context.get('columns', [])}

TASK: Create a focused news search query (2-4 keywords) that would find headlines relevant to:
1. The business/industry context
2. The geographic locations in the data
3. Economic or business trends that could impact the metrics being analyzed

GUIDELINES:
- Use specific industry terms if identified
- Include 1-2 location terms if available
- Focus on business/economic keywords
- Keep it concise (2-4 keywords maximum)
- Avoid generic terms like "data" or "analysis"

EXAMPLES:
- For sales data with states: "retail sales performance [state]"
- For budget data with regions: "economic forecast budget [region]"
- For financial data: "business earnings financial [location]"

RESPOND WITH ONLY THE SEARCH QUERY (no quotes, no explanation):
"""
            
            print(f"[DEBUG] Generating news query with LLM")
            response = llm_interpreter.query_llm(prompt, context)
            
            if response.success and response.content:
                query = response.content.strip().strip('"\'')
                print(f"[DEBUG] LLM generated news query: {query}")
                return query
                
        except Exception as e:
            print(f"[DEBUG] Error generating LLM news query: {str(e)}")
        
        return self._generate_fallback_query(context)
    
    def _generate_fallback_query(self, context: Dict) -> str:
        """Generate a fallback news query without LLM"""
        query_parts = []
        
        # Add business context
        business_type = context.get('business_context', {}).get('industry', '')
        if business_type and business_type != 'general':
            query_parts.append(business_type)
        else:
            query_parts.append('business')
        
        # Add location if available
        locations = context.get('top_locations', [])
        if locations:
            # Use the first location
            location = locations[0]
            if len(location.split()) == 1:  # Single word location
                query_parts.append(location)
        
        # Add economic context
        if any(metric in context.get('business_context', {}).get('key_metrics', []) 
               for metric in ['financial_performance', 'budget_performance']):
            query_parts.append('economic')
        else:
            query_parts.append('market')
        
        query = ' '.join(query_parts)
        print(f"[DEBUG] Fallback news query: {query}")
        return query
    
    def fetch_news(self, query: str, max_articles: int = 5) -> List[Dict]:
        """Fetch news articles using RSS feeds and try to get article content"""
        try:
            # Use RSS feeds for free news access
            import feedparser
            
            # URL encode the query
            encoded_query = urllib.parse.quote(query)
            
            news_sources = [
                f'https://news.google.com/rss/search?q={encoded_query}',
                f'https://rss.cnn.com/rss/money_news_companies.rss',
                f'http://feeds.reuters.com/reuters/businessNews',
                f'https://feeds.finance.yahoo.com/rss/2.0/headline'
            ]
            
            articles = []
            
            for source_url in news_sources:
                try:
                    feed = feedparser.parse(source_url)
                    
                    for entry in feed.entries[:2]:  # Limit to 2 articles per source
                        if len(articles) >= max_articles:
                            break
                            
                        # Filter articles by query relevance
                        title_text = entry.title.lower()
                        query_words = query.lower().split()
                        
                        relevance_score = sum(1 for word in query_words if word in title_text)
                        
                        if relevance_score > 0 or 'q=' in source_url:  # At least one query word matches or it's a search URL
                            # Try to get article content
                            article_content = self._extract_article_content(entry)
                            
                            articles.append({
                                'title': entry.title,
                                'link': entry.link,
                                'published': getattr(entry, 'published', ''),
                                'source': source_url.split('/')[2],
                                'summary': article_content if article_content else getattr(entry, 'summary', '')[:200] + '...' if hasattr(entry, 'summary') and len(getattr(entry, 'summary', '')) > 200 else getattr(entry, 'summary', '')
                            })
                except Exception as e:
                    print(f"[DEBUG] Error fetching from {source_url}: {str(e)}")
            
            return articles
                
        except ImportError:
            # If feedparser is not installed, try to install it
            try:
                print("[DEBUG] Feedparser not installed, attempting to install...")
                import subprocess
                subprocess.check_call(['pip', 'install', 'feedparser'])
                
                # Try again after installation
                import feedparser
                return self.fetch_news(query, max_articles)  # Retry after install
                
            except Exception as e:
                print(f"[DEBUG] Could not install feedparser: {str(e)}")
                return []
                
        except Exception as e:
            print(f"[DEBUG] Error fetching news: {str(e)}")
            return []
    
    def _extract_article_content(self, entry) -> str:
        """Try to extract meaningful content from article entry"""
        try:
            # First try the summary field
            if hasattr(entry, 'summary') and entry.summary:
                content = entry.summary
                # Clean HTML tags if present
                import re
                content = re.sub(r'<[^>]+>', '', content)
                if len(content) > 50:  # If we got meaningful content
                    return content[:300] + '...' if len(content) > 300 else content
            
            # Try content field
            if hasattr(entry, 'content') and entry.content:
                for content_item in entry.content:
                    if hasattr(content_item, 'value'):
                        content = content_item.value
                        import re
                        content = re.sub(r'<[^>]+>', '', content)
                        if len(content) > 50:
                            return content[:300] + '...' if len(content) > 300 else content
            
            # Fallback to description
            if hasattr(entry, 'description') and entry.description:
                content = entry.description
                import re
                content = re.sub(r'<[^>]+>', '', content)
                return content[:300] + '...' if len(content) > 300 else content
                
        except Exception as e:
            print(f"[DEBUG] Error extracting article content: {str(e)}")
        
        return ""
    
    def format_news_for_chat(self, results: Dict) -> str:
        """Format news results for chat display with useful business insights"""
        if not results or not isinstance(results, dict):
            return "📰 **BUSINESS CONTEXT ANALYSIS**\n\nUnable to generate business context analysis."
        
        news_items = results.get('news_items', [])
        if not news_items:
            return "📰 **BUSINESS CONTEXT ANALYSIS**\n\nNo relevant business news found for this dataset."
        
        # Generate AI summary based on headlines and any available content
        ai_summary = self._generate_actionable_news_summary(news_items, results)
        
        # Create simple table of news sources
        news_table = self._create_simple_news_table(news_items)
        
        # Create output with summary first, then table
        output = []
        output.append("📰 **BUSINESS CONTEXT ANALYSIS**")
        output.append("")
        output.append("🎯 **Market Intelligence Summary:**")
        output.append(ai_summary)
        output.append("")
        output.append("---")
        output.append("📊 **RELEVANT NEWS SOURCES** *(See details below)*")
        output.append("")
        output.append(news_table)
        
        return "\n".join(output)
    
    def _generate_actionable_news_summary(self, news_items: List[Dict], context: Dict) -> str:
        """Generate a meaningful summary that helps understand data influences"""
        try:
            # Import LLM interpreter
            from ai.llm_interpreter import LLMInterpreter
            from config.settings import Settings
            
            # Create LLM interpreter instance
            settings = Settings()
            llm = LLMInterpreter(settings)
            
            # Prepare headlines and any content for analysis
            news_content = []
            for item in news_items[:5]:  # Focus on top 5 articles
                title = item.get('title', 'No title')
                summary = item.get('summary', '')
                date = item.get('published', 'Recent')
                
                article_info = f"HEADLINE: {title}"
                if summary and len(summary) > 10:
                    article_info += f"\nSUMMARY: {summary}"
                article_info += f"\nDATE: {date}"
                news_content.append(article_info)
            
            # Get business context
            business_context = context.get('business_context', {})
            industry = business_context.get('industry', 'business')
            locations = context.get('top_locations', [])
            
            # Create focused prompt for actionable insights
            summary_prompt = f"""
            You are a business analyst helping interpret how current news might influence financial data patterns.

            BUSINESS CONTEXT:
            - Industry: {industry}
            - Key Locations: {', '.join(locations[:3]) if locations else 'General'}
            - Data Analysis Focus: Understanding external factors affecting business performance

            NEWS HEADLINES AND CONTENT:
            {chr(10).join(news_content)}

            TASK: Write a concise paragraph (3-4 sentences) that explains:
            1. What key market/economic trends these headlines reveal
            2. How these trends could specifically impact {industry} business performance
            3. What data patterns an analyst should look for based on this news context

            Focus on actionable insights that help explain data variations, not generic business advice.
            Be specific about potential impacts on metrics like revenue, costs, regional performance, etc.

            Market Intelligence Summary:
            """
            
            # Query the LLM for summary
            response = llm.query_llm(summary_prompt)
            
            if response.success and response.content:
                summary = response.content.strip()
                # Clean up any unwanted prefixes
                prefixes = ['market intelligence summary:', 'summary:', 'analysis:']
                for prefix in prefixes:
                    if summary.lower().startswith(prefix):
                        summary = summary[len(prefix):].strip()
                return summary
            else:
                return self._generate_headline_based_summary(news_items, industry, locations)
                
        except Exception as e:
            print(f"[NEWS] AI summary generation failed: {str(e)}")
            return self._generate_headline_based_summary(news_items, industry, locations)
    
    def _generate_headline_based_summary(self, news_items: List[Dict], industry: str, locations: List[str]) -> str:
        """Generate summary based on headlines when AI fails"""
        if not news_items:
            return f"No relevant news trends identified for {industry} sector analysis."
        
        # Extract key themes from headlines
        headlines = [item.get('title', '') for item in news_items[:3]]
        
        # Look for common business themes
        themes = []
        all_text = ' '.join(headlines).lower()
        
        if 'growth' in all_text or 'increase' in all_text:
            themes.append('growth trends')
        if 'decline' in all_text or 'drop' in all_text or 'fall' in all_text:
            themes.append('market challenges')
        if 'economic' in all_text or 'economy' in all_text:
            themes.append('economic factors')
        if 'earnings' in all_text or 'revenue' in all_text or 'profit' in all_text:
            themes.append('financial performance')
        
        location_text = ', '.join(locations[:2]) if locations else 'regional markets'
        theme_text = ', '.join(themes) if themes else 'business developments'
        
        return f"Recent headlines indicate {theme_text} affecting {industry} sector performance in {location_text}. Analysts should examine data patterns around these external market factors to identify correlations with performance metrics and regional variations."
    
    def _create_simple_news_table(self, news_items: List[Dict]) -> str:
        """Create a simple table of news sources without complex formatting"""
        if not news_items:
            return "No news articles found."
        
        table_lines = []
        table_lines.append("| # | Headline | Source | Date |")
        table_lines.append("|---|----------|--------|------|")
        
        for i, item in enumerate(news_items[:8], 1):  # Top 8 articles
            title = item.get('title', 'No title').strip()
            source = item.get('source', 'Unknown').replace('.com', '').replace('www.', '').title()
            
            # Clean up title length
            if len(title) > 60:
                title = title[:57] + "..."
            
            # Format date
            date_str = "Recent"
            published = item.get('published', '')
            if published:
                try:
                    import pandas as pd
                    date_obj = pd.to_datetime(published)
                    date_str = date_obj.strftime("%b %d")
                except:
                    pass
            
            # Create table row
            link = item.get('link', '')
            if link:
                title_with_link = f"[{title}]({link})"
            else:
                title_with_link = title
                
            table_lines.append(f"| {i} | {title_with_link} | {source} | {date_str} |")
        
        return "\n".join(table_lines)
    
    def analyze(self, data: pd.DataFrame, column_info: Dict, llm_interpreter=None) -> Dict:
        """Main analysis method that returns news context"""
        try:
            print("[DEBUG] Starting news analysis...")
            
            # Analyze data context
            context = self.analyze_data_context(data, column_info, llm_interpreter)
            
            # Store results
            self.last_analysis = {
                'context': context,
                'timestamp': datetime.now()
            }
            
            return context
            
        except Exception as e:
            print(f"[DEBUG] News analysis error: {str(e)}")
            return {}
