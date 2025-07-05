"""
Strategy 1: LLM-Enhanced Pattern Matching
Uses LLM to understand intent and extract conditions, then builds SQL systematically
"""

from typing import Dict, Any, List, Optional, Tuple
import re
import pandas as pd
from dataclasses import dataclass
@dataclass
class SQLTranslationResult:
    """Result of NL-to-SQL translation"""
    success: bool
    sql_query: str
    explanation: str
    confidence: float
    error_message: Optional[str] = None
    extracted_conditions: Optional[List[Dict]] = None


class LLMEnhancedNLToSQL:
    """
    Strategy 1: LLM-Enhanced NL-to-SQL Translator
    
    Uses LLM to understand natural language intent and extract conditions,
    then systematically builds SQL with proper WHERE clauses
    """
    
    def __init__(self, llm_interpreter=None):
        """
        Initialize with LLM interpreter for intent understanding
        
        Args:
            llm_interpreter: LLM interpreter for natural language understanding
        """
        self.llm_interpreter = llm_interpreter
        self.schema_info = None
        self.table_name = "data"
        
        # Enhanced column mapping with business terms
        self.column_mappings = {
            # Financial terms
            'sales': ['sales', 'revenue', 'income'],
            'budget': ['budget', 'planned', 'target'],
            'actual': ['actual', 'real', 'achieved'],
            'variance': ['variance', 'difference', 'delta'],
            'region': ['region', 'area', 'territory', 'location'],
            'product': ['product', 'item', 'sku'],
            'date': ['date', 'time', 'when', 'period'],
            'quarter': ['quarter', 'q1', 'q2', 'q3', 'q4'],
            'month': ['month', 'january', 'february', 'march', 'april', 'may', 'june',
                     'july', 'august', 'september', 'october', 'november', 'december'],
            'year': ['year', '2023', '2024', '2025']
        }
        
        # Condition extraction patterns
        self.condition_patterns = [
            # Comparison operators
            r'(\w+)\s+(is|equals?|=)\s+(["\']?[^"\'\s]+["\']?)',
            r'(\w+)\s+(greater than|>|above)\s+(["\']?[^"\'\s]+["\']?)',
            r'(\w+)\s+(less than|<|below)\s+(["\']?[^"\'\s]+["\']?)',
            r'(\w+)\s+(>=|at least)\s+(["\']?[^"\'\s]+["\']?)',
            r'(\w+)\s+(<=|at most)\s+(["\']?[^"\'\s]+["\']?)',
            # Range patterns
            r'(\w+)\s+between\s+(["\']?[^"\'\s]+["\']?)\s+and\s+(["\']?[^"\'\s]+["\']?)',
            r'(\w+)\s+from\s+(["\']?[^"\'\s]+["\']?)\s+to\s+(["\']?[^"\'\s]+["\']?)',
            # List patterns
            r'(\w+)\s+in\s+\(([^)]+)\)',
            # Negation patterns
            r'(\w+)\s+not\s+(equals?|=)\s+(["\']?[^"\'\s]+["\']?)',
            r'(\w+)\s+is\s+not\s+(["\']?[^"\'\s]+["\']?)'
        ]
        
        # Aggregation function mapping
        self.aggregation_mapping = {
            'top': 'ORDER BY {} DESC LIMIT {}',
            'bottom': 'ORDER BY {} ASC LIMIT {}',
            'highest': 'ORDER BY {} DESC LIMIT 1',
            'lowest': 'ORDER BY {} ASC LIMIT 1',
            'sum': 'SUM({})',
            'total': 'SUM({})',
            'average': 'AVG({})',
            'count': 'COUNT({})',
            'maximum': 'MAX({})',
            'minimum': 'MIN({})'
        }
    
    def set_schema_context(self, schema_info: Dict[str, Any], table_name: str):
        """Set schema context for SQL generation"""
        self.schema_info = schema_info
        self.table_name = table_name
        
        # Update column mappings based on actual columns
        if 'columns' in schema_info:
            for col in schema_info['columns']:
                col_lower = col.lower()
                # Add actual column names to mappings
                for key, aliases in self.column_mappings.items():
                    if any(alias in col_lower for alias in aliases):
                        if col not in self.column_mappings[key]:
                            self.column_mappings[key].append(col)
    
    def translate_to_sql(self, natural_query: str) -> SQLTranslationResult:
        """
        Translate natural language query to SQL using LLM-enhanced approach
        
        Args:
            natural_query: Natural language query to translate
            
        Returns:
            SQLTranslationResult with translation details
        """
        try:
            # Step 1: Use LLM to understand intent if available
            intent_analysis = self._analyze_intent_with_llm(natural_query)
            
            # Step 2: Extract conditions using both LLM and patterns
            conditions = self._extract_conditions(natural_query, intent_analysis)
            
            # Step 3: Identify aggregations and sorting
            aggregations = self._identify_aggregations(natural_query)
            
            # Step 4: Build SQL query systematically
            sql_query = self._build_enhanced_sql(conditions, aggregations, natural_query)
            
            # Step 5: Calculate confidence based on extraction success
            confidence = self._calculate_confidence(conditions, aggregations, natural_query)
            
            # Step 6: Generate explanation
            explanation = self._generate_explanation(sql_query, conditions, aggregations)
            
            return SQLTranslationResult(
                success=True,
                sql_query=sql_query,
                explanation=explanation,
                confidence=confidence,
                extracted_conditions=conditions
            )
            
        except Exception as e:
            return SQLTranslationResult(
                success=False,
                sql_query="",
                explanation="",
                confidence=0.0,
                error_message=f"Translation failed: {str(e)}"
            )
    
    def _analyze_intent_with_llm(self, query: str) -> Dict[str, Any]:
        """
        Use LLM to analyze query intent and extract key information
        
        Args:
            query: Natural language query
            
        Returns:
            Dictionary with intent analysis
        """
        intent_analysis = {
            'conditions': [],
            'aggregations': [],
            'sorting': [],
            'limit': None,
            'columns': []
        }
        
        if not self.llm_interpreter:
            return intent_analysis
        
        # Create prompt for intent analysis
        schema_context = ""
        if self.schema_info:
            schema_context = f"Available columns: {', '.join(self.schema_info['columns'])}\n"
            if 'sample_values' in self.schema_info:
                sample_context = []
                for col, samples in self.schema_info['sample_values'].items():
                    sample_context.append(f"{col}: {samples[:3]}")
                schema_context += f"Sample values: {'; '.join(sample_context)}\n"
        
        prompt = f"""
Analyze this natural language query for database search intent:
Query: "{query}"

{schema_context}

Extract and identify:
1. Filtering conditions (column, operator, value)
2. Aggregation functions needed (sum, count, avg, max, min)
3. Sorting requirements (order by, top N)
4. Specific columns to select (or * for all)

Respond in this format:
CONDITIONS: [list each condition as "column operator value"]
AGGREGATIONS: [list aggregation functions needed]
SORTING: [list sorting requirements]
COLUMNS: [list specific columns or "all"]
LIMIT: [number if top N requested, or "none"]

Focus on extracting concrete filtering conditions that would create WHERE clauses.
"""
        
        try:
            # Get LLM response
            response = self.llm_interpreter.query_llm(prompt)
            
            # Parse LLM response
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('CONDITIONS:'):
                    conditions_text = line.replace('CONDITIONS:', '').strip()
                    if conditions_text and conditions_text != '[]':
                        # Parse conditions from LLM response
                        intent_analysis['conditions'] = self._parse_llm_conditions(conditions_text)
                
                elif line.startswith('AGGREGATIONS:'):
                    agg_text = line.replace('AGGREGATIONS:', '').strip()
                    if agg_text and agg_text != '[]':
                        intent_analysis['aggregations'] = [a.strip() for a in agg_text.split(',')]
                
                elif line.startswith('SORTING:'):
                    sort_text = line.replace('SORTING:', '').strip()
                    if sort_text and sort_text != '[]':
                        intent_analysis['sorting'] = [s.strip() for s in sort_text.split(',')]
                
                elif line.startswith('LIMIT:'):
                    limit_text = line.replace('LIMIT:', '').strip()
                    if limit_text and limit_text.lower() != 'none':
                        try:
                            intent_analysis['limit'] = int(limit_text)
                        except ValueError:
                            pass
                
                elif line.startswith('COLUMNS:'):
                    cols_text = line.replace('COLUMNS:', '').strip()
                    if cols_text and cols_text.lower() != 'all':
                        intent_analysis['columns'] = [c.strip() for c in cols_text.split(',')]
            
        except Exception as e:
            print(f"LLM intent analysis failed: {e}")
        
        return intent_analysis
    
    def _parse_llm_conditions(self, conditions_text: str) -> List[Dict]:
        """Parse conditions from LLM response"""
        conditions = []
        
        # Remove brackets and split by commas or semicolons
        clean_text = conditions_text.strip('[]').replace('"', '').replace("'", "")
        condition_strings = re.split(r'[,;]', clean_text)
        
        for cond_str in condition_strings:
            cond_str = cond_str.strip()
            if not cond_str:
                continue
            
            # Try to parse "column operator value" format
            parts = cond_str.split()
            if len(parts) >= 3:
                column = parts[0]
                operator = parts[1]
                value = ' '.join(parts[2:])
                
                # Map column names
                mapped_column = self._map_column_name(column)
                if mapped_column:
                    conditions.append({
                        'column': mapped_column,
                        'operator': operator,
                        'value': value,
                        'source': 'llm'
                    })
        
        return conditions
    
    def _extract_conditions(self, query: str, intent_analysis: Dict) -> List[Dict]:
        """
        Extract filtering conditions using both LLM and pattern matching
        
        Args:
            query: Natural language query
            intent_analysis: LLM intent analysis results
            
        Returns:
            List of condition dictionaries
        """
        conditions = []
        
        # Start with LLM-extracted conditions
        if intent_analysis.get('conditions'):
            conditions.extend(intent_analysis['conditions'])
        
        # Add pattern-based extraction for additional conditions
        query_lower = query.lower()
        
        for pattern in self.condition_patterns:
            matches = re.finditer(pattern, query_lower, re.IGNORECASE)
            for match in matches:
                if pattern.count('(') == 3:  # Standard condition pattern
                    column_term = match.group(1)
                    operator = match.group(2)
                    value = match.group(3).strip('"\'')
                    
                    # Map column name
                    mapped_column = self._map_column_name(column_term)
                    if mapped_column:
                        # Convert operator to SQL
                        sql_operator = self._convert_operator(operator)
                        
                        # Check if this condition already exists
                        existing = any(
                            c['column'] == mapped_column and c['value'] == value 
                            for c in conditions
                        )
                        
                        if not existing:
                            conditions.append({
                                'column': mapped_column,
                                'operator': sql_operator,
                                'value': value,
                                'source': 'pattern'
                            })
                
                elif 'between' in pattern or 'from' in pattern:  # Range pattern
                    column_term = match.group(1)
                    start_value = match.group(2).strip('"\'')
                    end_value = match.group(3).strip('"\'')
                    
                    mapped_column = self._map_column_name(column_term)
                    if mapped_column:
                        conditions.append({
                            'column': mapped_column,
                            'operator': 'BETWEEN',
                            'value': f"{start_value} AND {end_value}",
                            'source': 'pattern'
                        })
        
        return conditions
    
    def _map_column_name(self, term: str) -> Optional[str]:
        """
        Map business term to actual column name
        
        Args:
            term: Business term from query
            
        Returns:
            Actual column name or None if not found
        """
        if not self.schema_info or 'columns' not in self.schema_info:
            return term  # Return as-is if no schema info
        
        term_lower = term.lower()
        
        # First check exact match
        for col in self.schema_info['columns']:
            if col.lower() == term_lower:
                return col
        
        # Then check mappings
        for actual_col in self.schema_info['columns']:
            col_lower = actual_col.lower()
            for key, aliases in self.column_mappings.items():
                if term_lower in aliases:
                    # Check if this alias matches the column
                    for alias in aliases:
                        if alias in col_lower:
                            return actual_col
        
        # Check partial matches
        for col in self.schema_info['columns']:
            if term_lower in col.lower() or col.lower() in term_lower:
                return col
        
        return None
    
    def _convert_operator(self, operator: str) -> str:
        """Convert natural language operator to SQL operator"""
        operator_map = {
            'is': '=',
            'equals': '=',
            'equal': '=',
            '=': '=',
            'greater than': '>',
            'above': '>',
            '>': '>',
            'less than': '<',
            'below': '<',
            '<': '<',
            '>=': '>=',
            'at least': '>=',
            '<=': '<=',
            'at most': '<=',
            'not equals': '!=',
            'not equal': '!=',
            'is not': '!='
        }
        
        return operator_map.get(operator.lower(), '=')
    
    def _identify_aggregations(self, query: str) -> List[Dict]:
        """Identify aggregation functions and sorting requirements"""
        aggregations = []
        query_lower = query.lower()
        
        # Look for aggregation keywords
        for keyword, sql_pattern in self.aggregation_mapping.items():
            if keyword in query_lower:
                # Try to identify the column for aggregation
                column = self._extract_aggregation_column(query_lower, keyword)
                
                if keyword in ['top', 'bottom']:
                    # Extract number for LIMIT
                    limit_match = re.search(rf'{keyword}\s+(\d+)', query_lower)
                    if limit_match:
                        limit_num = limit_match.group(1)
                        aggregations.append({
                            'type': 'sort_limit',
                            'keyword': keyword,
                            'column': column,
                            'limit': int(limit_num),
                            'sql_pattern': sql_pattern
                        })
                else:
                    aggregations.append({
                        'type': 'function',
                        'keyword': keyword,
                        'column': column,
                        'sql_pattern': sql_pattern
                    })
        
        return aggregations
    
    def _extract_aggregation_column(self, query: str, keyword: str) -> Optional[str]:
        """Extract column for aggregation function"""
        # Look for column name after or before the keyword
        patterns = [
            rf'{keyword}\s+(\w+)',
            rf'(\w+)\s+{keyword}',
            rf'{keyword}\s+\w+\s+by\s+(\w+)',
            rf'(\w+)\s+\w+\s+{keyword}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                column_term = match.group(1)
                mapped_column = self._map_column_name(column_term)
                if mapped_column:
                    return mapped_column
        
        # Default to first numeric column if available
        if self.schema_info and 'column_types' in self.schema_info:
            for col, dtype in self.schema_info['column_types'].items():
                if 'int' in str(dtype).lower() or 'float' in str(dtype).lower():
                    return col
        
        return None
    
    def _build_enhanced_sql(self, conditions: List[Dict], aggregations: List[Dict], original_query: str) -> str:
        """
        Build SQL query with proper WHERE clauses and aggregations
        
        Args:
            conditions: Extracted filtering conditions
            aggregations: Extracted aggregation requirements
            original_query: Original natural language query
            
        Returns:
            SQL query string
        """
        # Determine SELECT clause
        select_clause = "SELECT *"
        
        # Check for specific column requests
        function_aggs = [a for a in aggregations if a['type'] == 'function']
        if function_aggs:
            # Build aggregation SELECT
            agg_selects = []
            for agg in function_aggs:
                if agg['column']:
                    func_sql = agg['sql_pattern'].format(agg['column'])
                    agg_selects.append(f"{func_sql} as {agg['keyword']}_{agg['column']}")
                else:
                    agg_selects.append(f"{agg['keyword']}(*)")
            
            if agg_selects:
                select_clause = f"SELECT {', '.join(agg_selects)}"
        
        # Build FROM clause
        from_clause = f"FROM {self.table_name}"
        
        # Build WHERE clause
        where_conditions = []
        for condition in conditions:
            column = condition['column']
            operator = condition['operator']
            value = condition['value']
            
            # Handle different value types
            if operator == 'BETWEEN':
                where_conditions.append(f"{column} {operator} {value}")
            else:
                # Try to determine if value should be quoted
                formatted_value = self._format_sql_value(value, column)
                where_conditions.append(f"{column} {operator} {formatted_value}")
        
        where_clause = ""
        if where_conditions:
            where_clause = f"WHERE {' AND '.join(where_conditions)}"
        
        # Build ORDER BY and LIMIT
        order_limit_clause = ""
        sort_aggs = [a for a in aggregations if a['type'] == 'sort_limit']
        if sort_aggs:
            agg = sort_aggs[0]  # Take first sort aggregation
            if agg['column']:
                direction = 'DESC' if agg['keyword'] == 'top' else 'ASC'
                order_limit_clause = f"ORDER BY {agg['column']} {direction} LIMIT {agg['limit']}"
        elif not function_aggs and not where_conditions:
            # If no specific conditions, add reasonable limit
            order_limit_clause = "LIMIT 100"
        
        # Combine all parts
        sql_parts = [select_clause, from_clause]
        if where_clause:
            sql_parts.append(where_clause)
        if order_limit_clause:
            sql_parts.append(order_limit_clause)
        
        return " ".join(sql_parts)
    
    def _format_sql_value(self, value: str, column: str) -> str:
        """Format value for SQL query based on column type"""
        # Remove quotes if already present
        value = value.strip('"\'')
        
        # Check if it's a number
        try:
            float(value)
            return value  # Numeric value, no quotes needed
        except ValueError:
            pass
        
        # Check column type if available
        if self.schema_info and 'column_types' in self.schema_info:
            column_type = self.schema_info['column_types'].get(column, '')
            if 'int' in str(column_type).lower() or 'float' in str(column_type).lower():
                try:
                    float(value)
                    return value
                except ValueError:
                    pass
        
        # Default to quoted string
        return f"'{value}'"
    
    def _calculate_confidence(self, conditions: List[Dict], aggregations: List[Dict], query: str) -> float:
        """Calculate confidence score for the translation"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for each extracted condition
        confidence += min(len(conditions) * 0.15, 0.3)
        
        # Boost confidence for aggregations
        confidence += min(len(aggregations) * 0.1, 0.2)
        
        # Check for common query patterns
        query_lower = query.lower()
        common_patterns = ['where', 'show', 'find', 'get', 'list', 'top', 'greater', 'less', 'equal']
        pattern_matches = sum(1 for pattern in common_patterns if pattern in query_lower)
        confidence += min(pattern_matches * 0.05, 0.15)
        
        # Penalty for very simple queries without conditions
        if not conditions and not aggregations:
            confidence *= 0.7
        
        return min(confidence, 1.0)
    
    def _generate_explanation(self, sql_query: str, conditions: List[Dict], aggregations: List[Dict]) -> str:
        """Generate human-readable explanation of the SQL query"""
        parts = []
        
        if 'SELECT *' in sql_query:
            parts.append("Selecting all columns")
        elif 'SELECT' in sql_query:
            parts.append("Selecting specific aggregated data")
        
        if conditions:
            condition_descriptions = []
            for condition in conditions:
                condition_descriptions.append(
                    f"{condition['column']} {condition['operator']} {condition['value']}"
                )
            parts.append(f"Filtering where: {', '.join(condition_descriptions)}")
        
        if aggregations:
            agg_descriptions = []
            for agg in aggregations:
                if agg['type'] == 'function':
                    agg_descriptions.append(f"Calculating {agg['keyword']} of {agg['column']}")
                elif agg['type'] == 'sort_limit':
                    agg_descriptions.append(f"Getting {agg['keyword']} {agg['limit']} by {agg['column']}")
            parts.append(f"Aggregations: {', '.join(agg_descriptions)}")
        
        if 'LIMIT' in sql_query and not any(a['type'] == 'sort_limit' for a in aggregations):
            parts.append("Limited to reasonable number of results")
        
        return ". ".join(parts) if parts else "Basic data retrieval query"
