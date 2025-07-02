"""
News Analyzer Module
Analyzes CSV data to identify location columns and generates relevant news queries
"""

import pandas as pd
import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


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
            context = {
                'data_shape': data.shape,
                'columns': list(data.columns),
                'column_types': column_info,
                'location_columns': self._identify_location_columns(data),
                'business_context': self._identify_business_context(data.columns),
                'date_range': self._get_date_range(data, column_info.get('date_columns', [])),
                'top_locations': self._get_top_locations(data)
            }
            
            print(f"[DEBUG] News context analysis: {context}")
            return context
            
        except Exception as e:
            print(f"[DEBUG] Error in context analysis: {str(e)}")
            return {}
    
    def _identify_location_columns(self, data: pd.DataFrame) -> List[str]:
        """Identify columns that contain location data"""
        location_columns = []
        
        for col in data.columns:
            col_lower = col.lower()
            
            # Check if column name contains location keywords
            if any(keyword in col_lower for keyword in self.location_keywords):
                location_columns.append(col)
                continue
            
            # Check sample values for location patterns
            if data[col].dtype == 'object':
                sample_values = data[col].dropna().head(10).astype(str)
                
                # Look for state abbreviations or common location patterns
                location_patterns = 0
                for value in sample_values:
                    value_clean = value.strip().replace('_', ' ')
                    
                    # Check for US state patterns
                    if len(value_clean) == 2 and value_clean.isupper():
                        location_patterns += 1
                    # Check for state/country names
                    elif any(word in value_clean.lower() for word in [
                        'california', 'texas', 'florida', 'new york', 'illinois',
                        'ohio', 'georgia', 'north carolina', 'michigan', 'virginia',
                        'washington', 'arizona', 'massachusetts', 'tennessee',
                        'indiana', 'missouri', 'maryland', 'wisconsin', 'minnesota',
                        'colorado', 'alabama', 'south carolina', 'louisiana',
                        'kentucky', 'oregon', 'oklahoma', 'connecticut', 'utah',
                        'nevada', 'arkansas', 'mississippi', 'kansas', 'new mexico',
                        'nebraska', 'west virginia', 'idaho', 'hawaii', 'new hampshire',
                        'maine', 'montana', 'rhode island', 'delaware', 'south dakota',
                        'north dakota', 'alaska', 'vermont', 'wyoming', 'united states',
                        'canada', 'uk', 'germany', 'france', 'italy', 'spain', 'japan'
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
        except Exception as e:
            print(f"[DEBUG] Error getting date range: {str(e)}")
        
        return {}
    
    def _get_top_locations(self, data: pd.DataFrame) -> List[str]:
        """Get the top locations from identified location columns"""
        location_columns = self._identify_location_columns(data)
        top_locations = []
        
        for col in location_columns[:2]:  # Limit to first 2 location columns
            try:
                top_values = data[col].value_counts().head(5).index.tolist()
                for value in top_values:
                    if value and str(value).strip():
                        clean_value = str(value).replace('_', ' ').title()
                        if clean_value not in top_locations:
                            top_locations.append(clean_value)
            except Exception as e:
                print(f"[DEBUG] Error getting top locations from {col}: {str(e)}")
        
        return top_locations[:8]  # Limit to 8 locations total
    
    def generate_news_query(self, context: Dict, llm_interpreter=None) -> str:
        """Generate a news search query based on data context using LLM"""
        if not llm_interpreter or not llm_interpreter.is_available:
            return self._generate_fallback_query(context)
        
        try:
            # Create prompt for LLM to generate news query
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
        """Fetch news articles using RSS feeds (free alternative to paid APIs)"""
        try:
            # Use RSS feeds for free news access
            import feedparser
            import urllib.parse
            
            # URL encode the query
            encoded_query = urllib.parse.quote(query)
            
            news_sources = [
                f'https://feeds.feedburner.com/oreilly/radar?q={encoded_query}',
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
                        
                        if relevance_score > 0:  # At least one query word matches
                            articles.append({
                                'title': entry.title,
                                'link': entry.link,
                                'published': getattr(entry, 'published', 'Unknown'),
                                'summary': getattr(entry, 'summary', '')[:200] + '...' if hasattr(entry, 'summary') else '',
                                'source': feed.feed.get('title', 'News Source'),
                                'relevance': relevance_score
                            })
                    
                    if len(articles) >= max_articles:
                        break
                        
                except Exception as e:
                    print(f"[DEBUG] Error fetching from {source_url}: {str(e)}")
                    continue
            
            # Sort by relevance and return top articles
            articles.sort(key=lambda x: x['relevance'], reverse=True)
            return articles[:max_articles]
            
        except ImportError:
            print("[DEBUG] feedparser not available, installing...")
            try:
                import subprocess
                subprocess.check_call(['pip', 'install', 'feedparser'])
                import feedparser
                return self.fetch_news(query, max_articles)  # Retry after install
            except Exception as e:
                print(f"[DEBUG] Could not install feedparser: {str(e)}")
                return []
        
        except Exception as e:
            print(f"[DEBUG] Error fetching news: {str(e)}")
            return []
    
    def format_news_for_chat(self, articles: List[Dict], query: str) -> str:
        """Format news articles for display in chat"""
        if not articles:
            return f"""
📰 **RELEVANT NEWS CONTEXT**

🔍 **Search Query**: {query}

ℹ️ No relevant news articles found at this time. The analysis below is based on your data trends and patterns.

---
"""
        
        formatted_parts = [
            "📰 **RELEVANT NEWS CONTEXT**",
            "",
            f"🔍 **Search Query**: {query}",
            "",
            "📈 **Recent Headlines That May Impact Your Data:**"
        ]
        
        for i, article in enumerate(articles[:3], 1):  # Limit to top 3
            formatted_parts.extend([
                f"",
                f"**{i}. {article['title']}**",
                f"📅 {article['published']}",
                f"🔗 [Read More]({article['link']})"
            ])
            
            if article['summary']:
                formatted_parts.append(f"📝 {article['summary']}")
        
        formatted_parts.extend([
            "",
            "💡 **Business Impact**: Consider how these trends might relate to your data patterns in the analysis below.",
            "",
            "---"
        ])
        
        return "\n".join(formatted_parts)
    
    def analyze(self, data: pd.DataFrame, column_info: Dict, llm_interpreter=None) -> Dict:
        """Main analysis method that returns news context"""
        try:
            print("[DEBUG] Starting news analysis...")
            
            # Analyze data context
            context = self.analyze_data_context(data, column_info, llm_interpreter)
            
            # Generate news query
            query = self.generate_news_query(context, llm_interpreter)
            
            # Fetch relevant news
            articles = self.fetch_news(query)
            
            # Store results
            self.last_analysis = {
                'context': context,
                'query': query,
                'articles': articles,
                'timestamp': datetime.now()
            }
            
            print(f"[DEBUG] News analysis complete. Found {len(articles)} articles.")
            
            return {
                'success': True,
                'context': context,
                'query': query,
                'articles': articles,
                'formatted_output': self.format_news_for_chat(articles, query)
            }
            
        except Exception as e:
            print(f"[DEBUG] Error in news analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'formatted_output': "📰 **NEWS CONTEXT**: Unable to fetch relevant news at this time."
            }
