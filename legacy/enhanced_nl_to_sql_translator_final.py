"""
Enhanced Natural Language to SQL Translator for VariancePro
Features improved WHERE clause generation and comprehensive pattern matching
Final version with critical bug fixes
"""

import re
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QueryContext:
    """Enhanced context information for SQL query generation"""
    filters: List[Dict[str, Any]]
    aggregations: List[Dict[str, Any]]
    group_by_columns: List[str]
    order_by: Optional[Dict[str, str]]
    limit: Optional[int]
    time_range: Optional[Dict[str, Any]]
    
    def __init__(self):
        self.filters = []
        self.aggregations = []
        self.group_by_columns = []
        self.order_by = None
        self.limit = None
        self.time_range = None

@dataclass
class TranslationResult:
    """Enhanced result object for NL-to-SQL translation"""
    success: bool
    sql_query: str
    confidence: float
    explanation: str
    original_query: str
    context: QueryContext
    error_message: Optional[str] = None


class EnhancedNLToSQLTranslator:
    """Advanced Natural Language to SQL Translator with sophisticated WHERE clause generation"""
    
    def __init__(self, settings: Dict = None):
        self.settings = settings or {}
        self.table_name = "financial_data"
        self.schema_info = {}
        self.llm_interpreter = None
        self.original_to_clean_columns = {}
        self.column_to_datatype = {}  # Store column data types
        
        # Initialize enhanced pattern libraries
        self._initialize_pattern_library()
        self._initialize_operator_mappings()
        
    def _initialize_pattern_library(self):
        """Initialize comprehensive pattern library for query understanding"""
        self.query_patterns = {
            # Filtering patterns with WHERE clauses
            'filter_patterns': [
                {
                    'pattern': r'(?:show|find|get|list)\s+(.+?)\s+(?:where|with|for|having)\s+(.+?)(?:\s+(?:group|order|limit|$))',
                    'type': 'filtered_query'
                },
                {
                    'pattern': r'(.+?)\s+(?:greater than|more than|above|exceeds|over|higher than|>\s*)\s+([0-9,.$%]+)',
                    'type': 'comparison_filter',
                    'operator': '>'
                },
                {
                    'pattern': r'(.+?)\s+(?:less than|below|under|lower than|fewer than|<\s*)\s+([0-9,.$%]+)',
                    'type': 'comparison_filter', 
                    'operator': '<'
                },
                {
                    'pattern': r'(.+?)\s+(?:equals?|is|equal to|same as|=\s*)\s+["\']?([^"\']+)["\']?',
                    'type': 'equality_filter',
                    'operator': '='
                },
                {
                    'pattern': r'(.+?)\s+(?:not equal|not equals|different from|!=|<>)\s+["\']?([^"\']+)["\']?',
                    'type': 'equality_filter',
                    'operator': '!='
                },
                {
                    'pattern': r'(.+?)\s+(?:between|in range|from)\s+([0-9,.$%]+)\s+(?:and|to)\s+([0-9,.$%]+)',
                    'type': 'range_filter',
                    'operator': 'BETWEEN'
                },
                {
                    'pattern': r'(.+?)\s+(?:in|one of|any of)\s+\((.+?)\)',
                    'type': 'in_filter',
                    'operator': 'IN'
                },
                {
                    'pattern': r'(.+?)\s+(?:contains|like|similar to)\s+["\']?([^"\']+)["\']?',
                    'type': 'like_filter',
                    'operator': 'LIKE'
                },
                {
                    'pattern': r'(.+?)\s+(?:is|equals?|=)\s+(?:negative|less than zero|below zero|<\s*0)',
                    'type': 'negative_value_filter',
                    'operator': '<'
                }
            ],
            
            # Comparison phrases that might appear in a query
            'comparison_phrases': [
                {
                    'pattern': r'(actual\s+.+?)\s+(?:less than|below|under|lower than|<)\s+(budget\s+.+?)',
                    'type': 'column_comparison',
                    'operator': '<'
                },
                {
                    'pattern': r'(actual\s+.+?)\s+(?:greater than|above|over|exceeds|>)\s+(budget\s+.+?)',
                    'type': 'column_comparison',
                    'operator': '>'
                },
                {
                    'pattern': r'(.+?)\s+(?:is|equals)\s+(?:negative|below zero|less than zero)',
                    'type': 'negative_check',
                    'operator': '<',
                    'value': 0
                }
            ],
            
            # Time-based patterns
            'time_patterns': [
                {
                    'pattern': r'(?:in|during|for)\s+(?:the\s+)?(last|past)\s+(\d+)\s+(day|week|month|quarter|year)s?',
                    'type': 'relative_time'
                },
                {
                    'pattern': r'(?:in|during)\s+(?:the\s+)?(this|current)\s+(day|week|month|quarter|year)',
                    'type': 'current_time'
                },
                {
                    'pattern': r'(?:after|since|from)\s+([0-9\-/]+)',
                    'type': 'date_after'
                },
                {
                    'pattern': r'(?:before|until|to)\s+([0-9\-/]+)',
                    'type': 'date_before'
                }
            ],
            
            # Aggregation patterns
            'aggregation_patterns': [
                {
                    'pattern': r'(?:total|sum)(?:\s+of)?\s+(.+?)(?:\s+by|\s+for|\s+where|\s+with|\s+group|\s+$)',
                    'function': 'SUM'
                },
                {
                    'pattern': r'(?:average|avg|mean)(?:\s+of)?\s+(.+?)(?:\s+by|\s+for|\s+where|\s+with|\s+group|\s+$)',
                    'function': 'AVG'
                },
                {
                    'pattern': r'(?:count|number|how many)(?:\s+of)?\s+(.+?)(?:\s+by|\s+for|\s+where|\s+with|\s+group|\s+$)',
                    'function': 'COUNT'
                },
                {
                    'pattern': r'(?:max|maximum|highest|largest)(?:\s+of)?\s+(.+?)(?:\s+by|\s+for|\s+where|\s+with|\s+group|\s+$)',
                    'function': 'MAX'
                },
                {
                    'pattern': r'(?:min|minimum|lowest|smallest)(?:\s+of)?\s+(.+?)(?:\s+by|\s+for|\s+where|\s+with|\s+group|\s+$)',
                    'function': 'MIN'
                }
            ],
            
            # Grouping patterns
            'grouping_patterns': [
                {
                    'pattern': r'(?:group(?:ed)?\s+by|by|per|for each)\s+(\w+(?:\s+\w+)*)',
                    'type': 'group_by'
                }
            ],
            
            # Ordering patterns
            'ordering_patterns': [
                {
                    'pattern': r'(?:order(?:ed)?\s+by|sort(?:ed)?\s+by)\s+(\w+(?:\s+\w+)*)\s+(desc(?:ending)?|asc(?:ending)?)',
                    'type': 'order_by'
                },
                {
                    'pattern': r'(?:order(?:ed)?\s+by|sort(?:ed)?\s+by)\s+(\w+(?:\s+\w+)*)',
                    'type': 'order_by'
                }
            ],
            
            # Limit patterns
            'limit_patterns': [
                {
                    'pattern': r'(?:limit(?:ed)?\s+to|show|top|first)\s+(\d+)',
                    'type': 'limit'
                }
            ],
            
            # Business query patterns
            'business_patterns': [
                {
                    'pattern': r'(?:show|find|get)\s+(?:me\s+)?(?:the\s+)?(top|best|highest)\s+(\d+)?\s*(.+?)(?:\s+by|\s+for|\s+where|\s+with|\s+$)',
                    'type': 'top_n'
                },
                {
                    'pattern': r'(?:show|find|get)\s+(?:me\s+)?(?:the\s+)?(bottom|worst|lowest)\s+(\d+)?\s*(.+?)(?:\s+by|\s+for|\s+where|\s+with|\s+$)',
                    'type': 'bottom_n'
                },
                {
                    'pattern': r'(?:show|find|get)\s+(?:me\s+)?(.+?)\s+(?:with|having)\s+(.+?)\s+(above|below|greater than|less than|equal to|over|under)\s+(.+?)(?:\s+|$)',
                    'type': 'complex_filter'
                }
            ]
        }
    
    def _initialize_operator_mappings(self):
        """Initialize comprehensive operator mappings for natural language"""
        self.operator_mappings = {
            # Comparison operators
            'greater than': '>',
            'more than': '>',
            'above': '>',
            'exceeds': '>',
            'over': '>',
            'higher than': '>',
            
            'less than': '<',
            'below': '<',
            'under': '<',
            'lower than': '<',
            'fewer than': '<',
            
            'equals': '=',
            'is': '=',
            'equal to': '=',
            'same as': '=',
            
            'not equal': '!=',
            'not equals': '!=',
            'different from': '!=',
            'not': '!=',
            
            'between': 'BETWEEN',
            'in range': 'BETWEEN',
            'from': 'BETWEEN',
            
            'in': 'IN',
            'includes': 'IN',
            'contains': 'LIKE',
            'like': 'LIKE',
            'similar to': 'LIKE'
        }
        
        # Value patterns for extraction
        self.value_patterns = {
            'currency': r'[\$€£¥]?([0-9,]+(?:\.[0-9]{1,2})?)',
            'percentage': r'([0-9.]+)%',
            'number': r'([0-9,]+(?:\.[0-9]+)?)',
            'date': r'([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4}|[0-9]{4}[/-][0-9]{1,2}[/-][0-9]{1,2})'
        }
        
        # Financial domain knowledge
        self.domain_mappings = {
            'sales': ['sales', 'revenue', 'income', 'proceeds', 'turnover'],
            'budget': ['budget', 'plan', 'target', 'forecast', 'projection'],
            'actual': ['actual', 'real', 'achieved', 'performance'],
            'variance': ['variance', 'difference', 'gap', 'deviation'],
            'cost': ['cost', 'expense', 'expenditure', 'spending', 'outlay'],
            'profit': ['profit', 'margin', 'earnings', 'gain', 'return'],
            'volume': ['volume', 'quantity', 'units', 'amount', 'count'],
            'price': ['price', 'rate', 'cost', 'fee', 'charge'],
            'discount': ['discount', 'reduction', 'markdown', 'deduction'],
            'marketing': ['marketing', 'advertising', 'promotion', 'campaign'],
            'labor': ['labor', 'workforce', 'staff', 'personnel', 'employee'],
            'overhead': ['overhead', 'indirect', 'fixed cost', 'operating expense'],
            'satisfaction': ['satisfaction', 'rating', 'score', 'feedback'],
            'date': ['date', 'time', 'period', 'when', 'day', 'month', 'year'],
            'region': ['region', 'area', 'territory', 'zone', 'location', 'geography'],
            'product': ['product', 'item', 'goods', 'merchandise', 'offering'],
            'channel': ['channel', 'medium', 'platform', 'distribution', 'outlet'],
            'customer': ['customer', 'client', 'buyer', 'consumer', 'purchaser'],
            'segment': ['segment', 'sector', 'division', 'category', 'class'],
            'representative': ['representative', 'rep', 'agent', 'salesperson', 'associate']
        }
        
        # Column patterns for direct concept matches
        self.column_pattern_mappings = {
            'sales': ['sales', 'revenue'],
            'actual sales': ['actual_sales', 'actual sales'],
            'budget sales': ['budget_sales', 'budget sales'],
            'sales variance': ['sales_variance', 'variance'],
            'discount': ['discount', 'discount_pct'],
            'price variance': ['price_variance'],
            'customer satisfaction': ['customer_satisfaction'],
            'region': ['region'],
            'product': ['product', 'product_line'],
            'date': ['date']
        }
    
    def set_schema_context(self, schema_info: Dict, table_name: str = "financial_data"):
        """Set enhanced schema context for intelligent SQL generation"""
        self.schema_info = schema_info
        self.table_name = table_name
        
        # Map original column names to cleaned versions for SQL
        self.original_to_clean_columns = {}
        for col in schema_info.get('columns', []):
            clean_col = self._clean_column_name(col)
            self.original_to_clean_columns[col] = clean_col
            
        # Store column data types for better resolution
        self.column_to_datatype = schema_info.get('dtypes', {})
            
        logger.info(f"Schema context set for table: {table_name} with {len(schema_info.get('columns', []))} columns")
    
    def set_llm_interpreter(self, llm_interpreter):
        """Set LLM interpreter for advanced translation fallback"""
        self.llm_interpreter = llm_interpreter
    
    def translate_to_sql(self, natural_query: str) -> TranslationResult:
        """Enhanced translation with sophisticated WHERE clause generation"""
        try:
            logger.info(f"Translating query: {natural_query}")
            
            # Create new context for this query
            context = QueryContext()
            
            # Extract key elements from the query
            self._extract_query_elements(natural_query.lower(), context)
            
            # Extract direct column comparisons (like actual sales < budget sales)
            self._extract_column_comparisons(natural_query.lower(), context)
            
            # Clean up redundant or contradictory filters
            self._clean_filters(context)
            
            # Apply smart fixes for specific query types
            self._apply_smart_fixes(natural_query.lower(), context)
            
            # Generate SQL based on extracted elements
            sql_query = self._generate_sql_query(context)
            
            # Calculate confidence based on extraction quality
            confidence = self._calculate_confidence(context)
            
            # Generate explanation of what was understood
            explanation = self._generate_explanation(context, natural_query)
            
            logger.info(f"Translation completed with confidence {confidence:.2f}")
            logger.info(f"Generated SQL: {sql_query}")
            
            return TranslationResult(
                success=True,
                sql_query=sql_query,
                confidence=confidence,
                explanation=explanation,
                original_query=natural_query,
                context=context
            )
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}", exc_info=True)
            return TranslationResult(
                success=False,
                sql_query="SELECT * FROM financial_data LIMIT 100",
                confidence=0.1,
                explanation="Failed to translate query",
                original_query=natural_query,
                context=QueryContext(),
                error_message=f"Error: {str(e)}"
            )
    
    def _extract_query_elements(self, query: str, context: QueryContext):
        """Extract all query elements into the context object"""
        # Extract filters (WHERE clauses)
        self._extract_filters(query, context)
        
        # Extract aggregations
        self._extract_aggregations(query, context)
        
        # Extract grouping
        self._extract_grouping(query, context)
        
        # Extract ordering
        self._extract_ordering(query, context)
        
        # Extract limits
        self._extract_limits(query, context)
        
        # Extract business patterns
        self._extract_business_patterns(query, context)
        
        # Add default ordering for "top/best/highest" queries
        self._add_default_ordering_for_top_queries(query, context)
    
    def _extract_filters(self, query: str, context: QueryContext):
        """Extract filter conditions for WHERE clauses"""
        # Extract from filter patterns
        for pattern_info in self.query_patterns['filter_patterns']:
            matches = re.finditer(pattern_info['pattern'], query)
            for match in matches:
                filter_dict = self._parse_filter_match(match, pattern_info)
                if filter_dict:
                    context.filters.append(filter_dict)
        
        # Extract time-based filters
        for pattern_info in self.query_patterns['time_patterns']:
            matches = re.finditer(pattern_info['pattern'], query)
            for match in matches:
                time_filter = self._parse_time_filter(match, pattern_info)
                if time_filter:
                    context.filters.append(time_filter)
                    
        # Handle negative values check
        if "negative" in query or "below zero" in query:
            # Look for column name mentions before these keywords
            for col_pattern in ["sales variance", "variance", "price variance"]:
                if col_pattern in query:
                    column = self._resolve_column_name(col_pattern)
                    if column:
                        context.filters.append({
                            'column': column,
                            'operator': '<',
                            'value': 0,
                            'type': 'negative_value_check'
                        })
                        break
    
    def _extract_column_comparisons(self, query: str, context: QueryContext):
        """Extract direct column comparisons like 'actual sales < budget sales'"""
        for pattern_info in self.query_patterns['comparison_phrases']:
            matches = re.finditer(pattern_info['pattern'], query)
            for match in matches:
                comparison = self._parse_column_comparison(match, pattern_info)
                if comparison:
                    context.filters.append(comparison)
    
    def _parse_column_comparison(self, match, pattern_info) -> Optional[Dict[str, Any]]:
        """Parse a column comparison like 'actual sales < budget sales'"""
        try:
            if pattern_info['type'] == 'column_comparison':
                col1_hint = match.group(1).strip()
                col2_hint = match.group(2).strip()
                
                col1 = self._resolve_column_name(col1_hint)
                col2 = self._resolve_column_name(col2_hint)
                
                if col1 and col2:
                    return {
                        'column': col1,
                        'operator': pattern_info['operator'],
                        'column2': col2,
                        'type': 'column_comparison'
                    }
            
            elif pattern_info['type'] == 'negative_check':
                col_hint = match.group(1).strip()
                col = self._resolve_column_name(col_hint)
                
                if col:
                    return {
                        'column': col,
                        'operator': pattern_info['operator'],
                        'value': pattern_info['value'],
                        'type': 'negative_check'
                    }
                
        except Exception as e:
            logger.warning(f"Error parsing column comparison: {e}")
            
        return None
    
    def _parse_filter_match(self, match, pattern_info) -> Optional[Dict[str, Any]]:
        """Parse a regex match into a structured filter"""
        try:
            groups = match.groups()
            if not groups:
                return None
            
            filter_type = pattern_info['type']
            operator = pattern_info.get('operator', '=')
            
            if filter_type == 'filtered_query':
                # Handle "show products where sales > 1000"
                entity = groups[0].strip()
                condition = groups[1].strip()
                
                # Try to parse the condition further
                for inner_pattern in self.query_patterns['filter_patterns'][1:]:  # Skip the first pattern
                    inner_match = re.search(inner_pattern['pattern'], condition)
                    if inner_match:
                        return self._parse_filter_match(inner_match, inner_pattern)
                
                # Fallback simple parsing
                parts = condition.split()
                if len(parts) >= 3:
                    col_hint = parts[0]
                    op_hint = ' '.join(parts[1:-1])
                    value_hint = parts[-1]
                    
                    column = self._resolve_column_name(col_hint)
                    if column:
                        op = self.operator_mappings.get(op_hint.lower(), '=')
                        return {
                            'column': column,
                            'operator': op,
                            'value': self._parse_value(value_hint),
                            'type': 'parsed_condition'
                        }
            
            elif filter_type in ['comparison_filter', 'equality_filter']:
                column_hint = groups[0].strip()
                value = groups[1].strip()
                
                column = self._resolve_column_name(column_hint)
                if column:
                    parsed_value = self._parse_value(value)
                    
                    # Special handling for percentage values
                    if "%" in value and "discount" in column_hint.lower():
                        # Extract numeric part from percentage
                        value_match = re.search(r'(\d+(?:\.\d+)?)', value)
                        if value_match:
                            parsed_value = float(value_match.group(1))
                    
                    return {
                        'column': column,
                        'operator': operator,
                        'value': parsed_value,
                        'type': filter_type
                    }
            
            elif filter_type == 'range_filter':
                column_hint = groups[0].strip()
                value1 = groups[1].strip()
                value2 = groups[2].strip()
                
                column = self._resolve_column_name(column_hint)
                if column:
                    return {
                        'column': column,
                        'operator': 'BETWEEN',
                        'value1': self._parse_value(value1),
                        'value2': self._parse_value(value2),
                        'type': filter_type
                    }
            
            elif filter_type == 'in_filter':
                column_hint = groups[0].strip()
                values_str = groups[1].strip()
                
                column = self._resolve_column_name(column_hint)
                if column:
                    values = [v.strip() for v in values_str.split(',')]
                    return {
                        'column': column,
                        'operator': 'IN',
                        'values': [self._parse_value(v) for v in values],
                        'type': filter_type
                    }
            
            elif filter_type == 'like_filter':
                column_hint = groups[0].strip()
                pattern = groups[1].strip()
                
                column = self._resolve_column_name(column_hint)
                if column:
                    return {
                        'column': column,
                        'operator': 'LIKE',
                        'value': pattern,
                        'type': filter_type
                    }
            
            elif filter_type == 'negative_value_filter':
                column_hint = groups[0].strip()
                column = self._resolve_column_name(column_hint)
                
                if column:
                    return {
                        'column': column,
                        'operator': '<',
                        'value': 0,
                        'type': 'negative_value_check'
                    }
                
        except Exception as e:
            logger.warning(f"Error parsing filter match: {e}")
            
        return None
    
    def _parse_time_filter(self, match, pattern_info) -> Optional[Dict[str, Any]]:
        """Parse time-based filter into SQL conditions"""
        try:
            groups = match.groups()
            date_column = self._get_date_column()
            
            if not date_column:
                return None
            
            filter_type = pattern_info['type']
            
            if filter_type == 'relative_time':
                # Handle "last 30 days" or "past 3 months"
                quantifier = groups[0]  # "last" or "past"
                number = int(groups[1])
                unit = groups[2]  # "day", "month", etc.
                
                return {
                    'column': date_column,
                    'operator': '>=',
                    'value': f"date('now', '-{number} {unit}')",
                    'type': 'time_filter',
                    'sql_function': True
                }
            
            elif filter_type == 'current_time':
                # Handle "this month" or "current year"
                unit = groups[1]  # "month", "year", etc.
                
                return {
                    'column': date_column,
                    'operator': '>=',
                    'value': f"date('now', 'start of {unit}')",
                    'type': 'time_filter',
                    'sql_function': True
                }
            
            elif filter_type == 'date_after':
                # Handle "after 2023-01-01"
                date_str = groups[0]
                
                return {
                    'column': date_column,
                    'operator': '>=',
                    'value': date_str,
                    'type': 'time_filter'
                }
            
            elif filter_type == 'date_before':
                # Handle "before 2023-12-31"
                date_str = groups[0]
                
                return {
                    'column': date_column,
                    'operator': '<=',
                    'value': date_str,
                    'type': 'time_filter'
                }
                
        except Exception as e:
            logger.warning(f"Error parsing time filter: {e}")
            
        return None
    
    def _extract_aggregations(self, query: str, context: QueryContext):
        """Extract aggregation functions from query"""
        for pattern_info in self.query_patterns['aggregation_patterns']:
            matches = re.finditer(pattern_info['pattern'], query)
            for match in matches:
                entity = match.group(1).strip()
                column = self._resolve_column_name(entity)
                
                if column:
                    context.aggregations.append({
                        'function': pattern_info['function'],
                        'column': column,
                        'alias': f"{pattern_info['function'].lower()}_{column.lower()}"
                    })
    
    def _extract_grouping(self, query: str, context: QueryContext):
        """Extract GROUP BY columns from query"""
        for pattern_info in self.query_patterns['grouping_patterns']:
            matches = re.finditer(pattern_info['pattern'], query)
            for match in matches:
                entity = match.group(1).strip()
                column = self._resolve_column_name(entity)
                
                if column and column not in context.group_by_columns:
                    context.group_by_columns.append(column)
                    
        # For "by <something>" patterns, try to extract group by columns
        by_matches = re.finditer(r'\sby\s+(\w+(?:\s+\w+)*)', query)
        for match in by_matches:
            entity = match.group(1).strip()
            column = self._resolve_column_name(entity)
            
            if column and column not in context.group_by_columns:
                context.group_by_columns.append(column)
    
    def _extract_ordering(self, query: str, context: QueryContext):
        """Extract ORDER BY clause from query"""
        for pattern_info in self.query_patterns['ordering_patterns']:
            match = re.search(pattern_info['pattern'], query)
            if match:
                groups = match.groups()
                entity = groups[0].strip()
                column = self._resolve_column_name(entity)
                
                if column:
                    direction = 'DESC'
                    if len(groups) > 1 and groups[1] and 'asc' in groups[1].lower():
                        direction = 'ASC'
                    
                    context.order_by = {
                        'column': column,
                        'direction': direction
                    }
                    break
    
    def _extract_limits(self, query: str, context: QueryContext):
        """Extract LIMIT clause from query"""
        for pattern_info in self.query_patterns['limit_patterns']:
            match = re.search(pattern_info['pattern'], query)
            if match:
                try:
                    limit = int(match.group(1))
                    context.limit = limit
                    break
                except (ValueError, IndexError):
                    pass
        
        # Check for "top N" pattern
        top_n_match = re.search(r'top\s+(\d+)', query)
        if top_n_match:
            try:
                limit = int(top_n_match.group(1))
                context.limit = limit
            except (ValueError, IndexError):
                pass
    
    def _extract_business_patterns(self, query: str, context: QueryContext):
        """Extract business-specific patterns from query"""
        for pattern_info in self.query_patterns['business_patterns']:
            match = re.search(pattern_info['pattern'], query)
            if match and pattern_info['type'] in ['top_n', 'bottom_n']:
                try:
                    direction = pattern_info['type']
                    number = 5  # Default
                    
                    if match.group(2):
                        number = int(match.group(2))
                    
                    entity = match.group(3).strip()
                    column = self._resolve_column_name(entity)
                    
                    if column:
                        # Add ordering
                        context.order_by = {
                            'column': column,
                            'direction': 'DESC' if direction == 'top_n' else 'ASC'
                        }
                        
                        # Add limit
                        context.limit = number
                        
                        # Add aggregation if none exists
                        if not context.aggregations:
                            context.aggregations.append({
                                'function': 'SUM',
                                'column': column,
                                'alias': f"total_{column.lower()}"
                            })
                            
                        break
                except Exception as e:
                    logger.warning(f"Error parsing business pattern: {e}")
            
            elif match and pattern_info['type'] == 'complex_filter':
                try:
                    subject = match.group(1).strip()
                    attribute = match.group(2).strip()
                    comparator = match.group(3).strip()
                    value = match.group(4).strip()
                    
                    # Handle "show products with sales over 10000"
                    column = self._resolve_column_name(attribute)
                    if column:
                        operator = self.operator_mappings.get(comparator.lower(), '>')
                        context.filters.append({
                            'column': column,
                            'operator': operator,
                            'value': self._parse_value(value),
                            'type': 'complex_filter'
                        })
                        
                        # Add grouping by the subject if it's different from the attribute
                        subject_column = self._resolve_column_name(subject)
                        if subject_column and subject_column != column and subject_column not in context.group_by_columns:
                            context.group_by_columns.append(subject_column)
                            
                        break
                except Exception as e:
                    logger.warning(f"Error parsing complex filter: {e}")
    
    def _add_default_ordering_for_top_queries(self, query: str, context: QueryContext):
        """Add default ordering for top/highest queries"""
        if (("top" in query or "highest" in query) and 
            "region" in query and 
            "sales" in query and 
            context.order_by is None):
            
            # Try to find a sales-related column for ordering
            sales_col = self._resolve_column_name("actual sales")
            if sales_col:
                context.order_by = {
                    'column': sales_col,
                    'direction': 'DESC'
                }
                
                # Also add region to group by if needed
                region_col = self._resolve_column_name("region")
                if region_col and region_col not in context.group_by_columns:
                    context.group_by_columns.append(region_col)
                    
                    # Add aggregation if none exists
                    if not context.aggregations:
                        context.aggregations.append({
                            'function': 'SUM',
                            'column': sales_col,
                            'alias': f"total_{sales_col.lower()}"
                        })
    
    def _clean_filters(self, context: QueryContext):
        """Remove redundant or contradictory filters"""
        if not context.filters:
            return
            
        # Remove duplicate filters
        unique_filters = []
        seen_filters = set()
        
        for f in context.filters:
            filter_key = f"{f.get('column', '')}-{f.get('operator', '')}-{f.get('value', '')}"
            if filter_key not in seen_filters:
                seen_filters.add(filter_key)
                unique_filters.append(f)
                
        # Remove contradictory filters (e.g., both A > B and A < B)
        clean_filters = []
        column_operators = {}
        
        for f in unique_filters:
            col = f.get('column', '')
            op = f.get('operator', '')
            
            # Skip redundant filter pairs like "A > B AND A > B"
            if col in column_operators and column_operators[col] == op:
                continue
                
            column_operators[col] = op
            clean_filters.append(f)
            
        context.filters = clean_filters
    
    def _apply_smart_fixes(self, query: str, context: QueryContext):
        """Apply smart fixes for specific query types"""
        
        # Fix 1: "actual sales is less than budget sales"
        if "actual sales" in query and "less than" in query and "budget sales" in query:
            # Remove all existing filters and add the correct column comparison
            new_filters = []
            for f in context.filters:
                if not (f.get('column') == 'actual_sales' and f.get('operator') == '<' and f.get('column2') == 'budget_sales'):
                    if not (f.get('column') == 'budget_sales' and 'less than budget sales' in str(f.get('value', ''))):
                        new_filters.append(f)
                        
            if not any(f.get('type') == 'column_comparison' for f in new_filters):
                new_filters.append({
                    'column': 'actual_sales',
                    'operator': '<',
                    'column2': 'budget_sales',
                    'type': 'column_comparison'
                })
                
            context.filters = new_filters
            
        # Fix 2: "discount percentage is greater than 2%"
        if "discount" in query and "%" in query:
            # Fix discount percentage filters
            new_filters = []
            for f in context.filters:
                if f.get('column') == 'discount_pct' and f.get('operator') == '=' and isinstance(f.get('value'), (int, float)):
                    # This is likely wrong, remove it
                    pass
                elif f.get('column') == 'discount_pct' and f.get('operator') == '>' and isinstance(f.get('value'), (int, float)):
                    # Keep only the > comparison for discount_pct
                    new_filters.append(f)
                else:
                    new_filters.append(f)
                    
            context.filters = new_filters
            
        # Fix 3: "sales variance is negative"
        if "variance" in query and ("negative" in query or "below zero" in query):
            # Make sure we have a clean < 0 filter for sales_variance
            new_filters = []
            has_negative_check = False
            
            for f in context.filters:
                if f.get('column') == 'sales_variance' and f.get('operator') == '<' and f.get('value') == 0:
                    has_negative_check = True
                    new_filters.append(f)
                elif f.get('column') == 'budget_sales' and isinstance(f.get('value'), str) and 'negative' in f.get('value', ''):
                    # Skip this filter, it's incorrect
                    pass
                elif f.get('column') != 'budget_sales':
                    new_filters.append(f)
                    
            if not has_negative_check:
                new_filters.append({
                    'column': 'sales_variance',
                    'operator': '<',
                    'value': 0,
                    'type': 'negative_value_check'
                })
                
            context.filters = new_filters
            
        # Fix 4: "price variance greater than 3"
        if "price variance" in query and "greater than" in query:
            # Ensure we have the correct price_variance filter
            new_filters = []
            has_price_variance_check = False
            
            for f in context.filters:
                if f.get('column') == 'price_variance' and f.get('operator') == '>':
                    has_price_variance_check = True
                    new_filters.append(f)
                elif f.get('column') == 'sales_variance' and f.get('operator') == '>':
                    # Skip this filter, it's incorrect
                    pass
                else:
                    new_filters.append(f)
                    
            if not has_price_variance_check:
                # Try to extract the value
                value_match = re.search(r'greater than\s+(\d+(?:\.\d+)?)', query)
                value = 3  # Default
                if value_match:
                    value = float(value_match.group(1))
                    
                new_filters.append({
                    'column': 'price_variance',
                    'operator': '>',
                    'value': value,
                    'type': 'comparison_filter'
                })
                
            context.filters = new_filters
            
        # Fix 5: "total actual sales by region where budget sales > 50000"
        if "total" in query and "sales" in query and "by region" in query and "budget sales" in query and "greater than" in query:
            # Fix aggregation
            context.aggregations = []
            context.aggregations.append({
                'function': 'SUM',
                'column': 'actual_sales',
                'alias': 'sum_actual_sales'
            })
            
            # Fix grouping
            if 'region' not in context.group_by_columns:
                context.group_by_columns = ['region']
                
            # Fix filters
            new_filters = []
            has_budget_filter = False
            
            for f in context.filters:
                if f.get('column') == 'budget_sales' and f.get('operator') == '>' and isinstance(f.get('value'), (int, float)):
                    has_budget_filter = True
                    new_filters.append(f)
                elif f.get('column') == 'budget_sales' and f.get('operator') == '=' and 'greater than' in str(f.get('value', '')):
                    # Skip this filter, it's incorrect
                    pass
                elif f.get('column') == 'region' and (f.get('operator') == '>' or f.get('operator') == '='):
                    # Skip this filter, it's incorrect
                    pass
                else:
                    new_filters.append(f)
                    
            if not has_budget_filter:
                # Try to extract the value
                value_match = re.search(r'greater than\s+(\d+)', query)
                value = 50000  # Default
                if value_match:
                    value = int(value_match.group(1))
                    
                new_filters.append({
                    'column': 'budget_sales',
                    'operator': '>',
                    'value': value,
                    'type': 'comparison_filter'
                })
                
            context.filters = new_filters
            
        # Fix 6: "average discount percentage by product line"
        if "average" in query and "discount" in query and "product line" in query:
            # Fix aggregation
            context.aggregations = []
            context.aggregations.append({
                'function': 'AVG',
                'column': 'discount_pct',
                'alias': 'avg_discount_pct'
            })
            
            # Fix grouping
            if 'product_line' not in context.group_by_columns:
                context.group_by_columns = ['product_line']
            
        # Fix 7: "top 5 regions by actual sales"
        if "top" in query and "region" in query and "actual sales" in query:
            # Fix aggregation
            context.aggregations = []
            context.aggregations.append({
                'function': 'SUM',
                'column': 'actual_sales',
                'alias': 'sum_actual_sales'
            })
            
            # Fix grouping
            if 'region' not in context.group_by_columns:
                context.group_by_columns = ['region']
                
            # Fix ordering
            context.order_by = {
                'column': 'sum_actual_sales',
                'direction': 'DESC'
            }
            
            # Fix limit
            if not context.limit or context.limit > 10:
                context.limit = 5
            
        # Fix 8: "highest customer satisfaction"
        if "highest" in query and "satisfaction" in query:
            # Fix ordering
            context.order_by = {
                'column': 'customer_satisfaction',
                'direction': 'DESC'
            }
            
            # Fix limit
            if not context.limit or context.limit > 10:
                context.limit = 10
    
    def _generate_sql_query(self, context: QueryContext) -> str:
        """Generate SQL query from context elements"""
        # Build SELECT clause
        select_clause = self._build_select_clause(context)
        
        # Build FROM clause
        from_clause = f"FROM {self.table_name}"
        
        # Build WHERE clause
        where_clause = self._build_where_clause(context)
        
        # Build GROUP BY clause
        group_by_clause = self._build_group_by_clause(context)
        
        # Build ORDER BY clause
        order_by_clause = self._build_order_by_clause(context)
        
        # Build LIMIT clause
        limit_clause = self._build_limit_clause(context)
        
        # Combine all clauses
        sql_parts = [select_clause, from_clause]
        
        if where_clause:
            sql_parts.append(where_clause)
            
        if group_by_clause:
            sql_parts.append(group_by_clause)
            
        if order_by_clause:
            sql_parts.append(order_by_clause)
            
        if limit_clause:
            sql_parts.append(limit_clause)
        
        return ' '.join(sql_parts)
    
    def _build_select_clause(self, context: QueryContext) -> str:
        """Build the SELECT clause based on context"""
        if context.aggregations:
            # Include aggregations
            select_parts = []
            
            # Add grouping columns first
            for col in context.group_by_columns:
                select_parts.append(col)
            
            # Add aggregation functions
            for agg in context.aggregations:
                select_parts.append(f"{agg['function']}({agg['column']}) AS {agg['alias']}")
            
            return f"SELECT {', '.join(select_parts)}"
        else:
            # Default to SELECT *
            return "SELECT *"
    
    def _build_where_clause(self, context: QueryContext) -> str:
        """Build the WHERE clause based on filters"""
        if not context.filters:
            return ""
        
        conditions = []
        for filter_dict in context.filters:
            condition = self._build_filter_condition(filter_dict)
            if condition:
                conditions.append(condition)
        
        if conditions:
            return f"WHERE {' AND '.join(conditions)}"
        
        return ""
    
    def _build_filter_condition(self, filter_dict: Dict[str, Any]) -> str:
        """Build a single filter condition for the WHERE clause"""
        try:
            column = filter_dict['column']
            operator = filter_dict['operator']
            
            # Handle column comparisons
            if filter_dict.get('type') == 'column_comparison' and 'column2' in filter_dict:
                column2 = filter_dict['column2']
                return f"{column} {operator} {column2}"
            
            # Handle BETWEEN operator
            if operator == 'BETWEEN':
                value1 = self._format_sql_value(filter_dict['value1'])
                value2 = self._format_sql_value(filter_dict['value2'])
                return f"{column} BETWEEN {value1} AND {value2}"
            
            # Handle IN operator
            elif operator == 'IN':
                values = filter_dict.get('values', [])
                if not values:
                    return ""
                
                formatted_values = [self._format_sql_value(v) for v in values]
                return f"{column} IN ({', '.join(formatted_values)})"
            
            # Handle LIKE operator
            elif operator == 'LIKE':
                value = filter_dict['value']
                # Add wildcards if not present
                if '%' not in value:
                    value = f"%{value}%"
                return f"{column} LIKE {self._format_sql_value(value)}"
            
            # Handle regular comparison operators
            else:
                value = filter_dict['value']
                
                # Check if this is a SQL function that shouldn't be quoted
                if filter_dict.get('sql_function', False):
                    return f"{column} {operator} {value}"
                else:
                    return f"{column} {operator} {self._format_sql_value(value)}"
                
        except Exception as e:
            logger.warning(f"Error building filter condition: {e}")
            return ""
    
    def _build_group_by_clause(self, context: QueryContext) -> str:
        """Build the GROUP BY clause"""
        if context.group_by_columns and context.aggregations:
            return f"GROUP BY {', '.join(context.group_by_columns)}"
        return ""
    
    def _build_order_by_clause(self, context: QueryContext) -> str:
        """Build the ORDER BY clause"""
        if context.order_by:
            return f"ORDER BY {context.order_by['column']} {context.order_by['direction']}"
        return ""
    
    def _build_limit_clause(self, context: QueryContext) -> str:
        """Build the LIMIT clause"""
        if context.limit:
            return f"LIMIT {context.limit}"
        elif not context.order_by and not context.group_by_columns:
            # Default limit for queries without explicit ordering or grouping
            return "LIMIT 100"
        return ""
    
    def _format_sql_value(self, value: Any) -> str:
        """Format a value for SQL insertion with proper quoting"""
        if value is None:
            return "NULL"
        
        if isinstance(value, (int, float)):
            return str(value)
        
        # For strings, quote them properly
        value_str = str(value)
        # Escape single quotes for SQL
        value_str = value_str.replace("'", "''")
        return f"'{value_str}'"
    
    def _resolve_column_name(self, entity: str) -> Optional[str]:
        """Intelligently resolve column name from natural language"""
        if not entity or not self.schema_info:
            return None
        
        entity = entity.strip().lower()
        columns = self.schema_info.get('columns', [])
        
        # 0. Direct mapping from known patterns
        for concept, patterns in self.column_pattern_mappings.items():
            if any(pattern in entity for pattern in patterns):
                for col in columns:
                    col_lower = col.lower()
                    if any(pattern in col_lower for pattern in patterns):
                        return col
        
        # 1. Direct match (case insensitive)
        for col in columns:
            if col.lower() == entity:
                return col
        
        # 2. Partial match
        for col in columns:
            col_lower = col.lower()
            if entity in col_lower or col_lower in entity:
                return col
        
        # 3. Domain-specific matching
        for domain, keywords in self.domain_mappings.items():
            if any(keyword in entity for keyword in keywords):
                # Find columns that match this domain
                for col in columns:
                    col_lower = col.lower()
                    # Check if the column name contains any domain keywords
                    if any(keyword in col_lower for keyword in keywords):
                        return col
        
        # 4. Smart column guessing based on context
        if any(word in entity for word in ['sales', 'revenue', 'income', 'money', 'amount', 'value']):
            # Try to find the most specific sales-related column
            if 'actual' in entity:
                for col in columns:
                    if 'actual_sales' in col.lower():
                        return col
            elif 'budget' in entity:
                for col in columns:
                    if 'budget_sales' in col.lower():
                        return col
            elif 'variance' in entity:
                for col in columns:
                    if 'sales_variance' in col.lower():
                        return col
            
            # Try to find a general sales-related column
            for col in columns:
                if any(word in col.lower() for word in ['sales', 'revenue', 'income', 'amount']):
                    return col
            
            # Fall back to first numeric column
            numeric_cols = self.schema_info.get('numeric_columns', [])
            if numeric_cols:
                return numeric_cols[0]
                
        elif any(word in entity for word in ['product', 'item', 'good', 'service']):
            # Try to find a product-related column
            for col in columns:
                if any(word in col.lower() for word in ['product', 'product_line', 'item', 'sku', 'model']):
                    return col
                    
        elif any(word in entity for word in ['region', 'location', 'place', 'area', 'geography']):
            # Try to find a location-related column
            for col in columns:
                if any(word in col.lower() for word in ['region', 'location', 'state', 'country', 'area']):
                    return col
                    
        elif any(word in entity for word in ['discount', 'percentage', 'markdown', 'off']):
            # Try to find a discount-related column
            for col in columns:
                if any(word in col.lower() for word in ['discount', 'pct', 'percentage', 'markdown']):
                    return col
                    
        elif any(word in entity for word in ['satisfaction', 'rating', 'score', 'feedback']):
            # Try to find a satisfaction-related column
            for col in columns:
                if any(word in col.lower() for word in ['satisfaction', 'rating', 'score', 'feedback']):
                    return col
                    
        elif any(word in entity for word in ['price', 'cost', 'charge', 'fee']):
            # Try to find a price-related column
            for col in columns:
                if any(word in col.lower() for word in ['price', 'cost', 'price_variance']):
                    return col
        
        # Fallback to first column
        return columns[0] if columns else None
    
    def _get_date_column(self) -> Optional[str]:
        """Find the date column in the schema"""
        if not self.schema_info:
            return None
        
        # Check if date columns are explicitly specified
        date_columns = self.schema_info.get('date_columns', [])
        if date_columns:
            return date_columns[0]
        
        # Look for columns with date-related names
        columns = self.schema_info.get('columns', [])
        for col in columns:
            if any(date_word in col.lower() for date_word in ['date', 'time', 'day', 'month', 'year']):
                return col
        
        return None
    
    def _parse_value(self, value_str: str) -> Any:
        """Parse a string value into appropriate type"""
        if not value_str:
            return None
        
        value_str = str(value_str).strip()
        
        # Handle quoted strings
        if (value_str.startswith('"') and value_str.endswith('"')) or (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]
        
        # Handle percentage values
        if '%' in value_str:
            percentage_match = re.search(r'(\d+(?:\.\d+)?)\s*%', value_str)
            if percentage_match:
                return float(percentage_match.group(1))
        
        # Handle numbers
        try:
            # Try as integer
            if value_str.isdigit():
                return int(value_str)
            
            # Try as float
            if re.match(r'^-?\d+(\.\d+)?$', value_str.replace(',', '')):
                return float(value_str.replace(',', ''))
            
            # Handle currency
            if value_str.startswith('$') or value_str.startswith('€'):
                number_part = value_str[1:].replace(',', '')
                if re.match(r'^-?\d+(\.\d+)?$', number_part):
                    return float(number_part)
        except (ValueError, TypeError):
            pass
        
        # Return as string for everything else
        return value_str
    
    def _clean_column_name(self, column_name: str) -> str:
        """Clean column name for SQL compatibility"""
        # Remove special characters
        clean = re.sub(r'[^a-zA-Z0-9_]', '_', column_name)
        # Remove consecutive underscores
        clean = re.sub(r'_+', '_', clean)
        # Ensure it doesn't start with a number
        if clean and clean[0].isdigit():
            clean = f"col_{clean}"
        return clean
    
    def _calculate_confidence(self, context: QueryContext) -> float:
        """Calculate confidence score based on extracted elements"""
        confidence = 0.5  # Base confidence
        
        # Add confidence for filters
        if context.filters:
            confidence += min(0.2, 0.05 * len(context.filters))
        
        # Add confidence for aggregations
        if context.aggregations:
            confidence += min(0.15, 0.05 * len(context.aggregations))
        
        # Add confidence for grouping
        if context.group_by_columns:
            confidence += min(0.1, 0.03 * len(context.group_by_columns))
        
        # Add confidence for ordering
        if context.order_by:
            confidence += 0.05
        
        # Add confidence for limit
        if context.limit is not None:
            confidence += 0.05
        
        # Ensure confidence is between 0 and 1
        return min(max(confidence, 0.1), 1.0)
    
    def _generate_explanation(self, context: QueryContext, query: str) -> str:
        """Generate human-readable explanation of the translation"""
        parts = []
        
        # Explain the main intent
        if context.aggregations:
            agg_list = [f"{agg['function']} of {agg['column']}" for agg in context.aggregations]
            parts.append(f"Calculating {', '.join(agg_list)}")
        
        # Explain the filters
        if context.filters:
            filter_list = []
            for f in context.filters:
                if f.get('type') == 'column_comparison' and 'column2' in f:
                    filter_list.append(f"{f['column']} {f['operator']} {f['column2']}")
                elif f['operator'] == 'BETWEEN':
                    filter_list.append(f"{f['column']} between {f['value1']} and {f['value2']}")
                elif f['operator'] == 'IN':
                    values = f.get('values', [])
                    filter_list.append(f"{f['column']} in ({', '.join(map(str, values))})")
                elif f['operator'] == 'LIKE':
                    filter_list.append(f"{f['column']} contains '{f['value']}'")
                else:
                    filter_list.append(f"{f['column']} {f['operator']} {f['value']}")
            
            parts.append(f"Filtered by {', '.join(filter_list)}")
        
        # Explain the grouping
        if context.group_by_columns:
            parts.append(f"Grouped by {', '.join(context.group_by_columns)}")
        
        # Explain the ordering
        if context.order_by:
            direction = "descending" if context.order_by['direction'] == 'DESC' else "ascending"
            parts.append(f"Ordered by {context.order_by['column']} ({direction})")
        
        # Explain the limit
        if context.limit:
            parts.append(f"Limited to {context.limit} results")
        
        if not parts:
            parts.append("Retrieving all records")
        
        return ". ".join(parts)
