"""
Strategy 2: Advanced Semantic Parsing with Context Learning
Builds a smarter pattern recognition system that learns from user data patterns
"""

from typing import Dict, Any, List, Optional, Tuple, Set
import re
import pandas as pd
from dataclasses import dataclass
from collections import defaultdict
import json
@dataclass
class SQLTranslationResult:
    """Result of NL-to-SQL translation"""
    success: bool
    sql_query: str
    explanation: str
    confidence: float
    error_message: Optional[str] = None
    extracted_conditions: Optional[List[Dict]] = None


class SemanticNLToSQL:
    """
    Strategy 2: Advanced Semantic Parsing with Context Learning
    
    Uses sophisticated pattern recognition and context learning to understand
    natural language queries and generate accurate SQL with proper WHERE clauses
    """
    
    def __init__(self):
        """Initialize the semantic parser"""
        self.schema_info = None
        self.table_name = "data"
        
        # Advanced semantic patterns for better understanding
        self.semantic_patterns = {
            # Comparison patterns with better context
            'exact_match': [
                r'(?:where|find|show|get|list)\s+.*?(\w+)\s+(?:is|equals?|=)\s+["\']?([^"\'\s,]+)["\']?',
                r'(\w+)\s+(?:is|equals?|=)\s+["\']?([^"\'\s,]+)["\']?',
                r'(?:with|having)\s+(\w+)\s+["\']?([^"\'\s,]+)["\']?'
            ],
            'greater_than': [
                r'(\w+)\s+(?:greater than|>|above|more than|over|exceeds?)\s+(["\']?[^"\'\s,]+["\']?)',
                r'(?:where|with|having)\s+(\w+)\s+(?:>|above|greater than)\s+(["\']?[^"\'\s,]+["\']?)',
                r'(\w+)\s+(?:above|over)\s+(["\']?[^"\'\s,]+["\']?)'
            ],
            'less_than': [
                r'(\w+)\s+(?:less than|<|below|under|fewer than)\s+(["\']?[^"\'\s,]+["\']?)',
                r'(?:where|with|having)\s+(\w+)\s+(?:<|below|less than)\s+(["\']?[^"\'\s,]+["\']?)',
                r'(\w+)\s+(?:below|under)\s+(["\']?[^"\'\s,]+["\']?)'
            ],
            'range': [
                r'(\w+)\s+between\s+(["\']?[^"\'\s,]+["\']?)\s+and\s+(["\']?[^"\'\s,]+["\']?)',
                r'(\w+)\s+from\s+(["\']?[^"\'\s,]+["\']?)\s+to\s+(["\']?[^"\'\s,]+["\']?)',
                r'(\w+)\s+in\s+(?:the\s+)?range\s+(["\']?[^"\'\s,]+["\']?)\s+(?:to|through|\-)\s+(["\']?[^"\'\s,]+["\']?)'
            ],
            'contains': [
                r'(\w+)\s+(?:contains|includes|has)\s+["\']?([^"\'\s,]+)["\']?',
                r'(?:with|having)\s+(\w+)\s+(?:containing|including)\s+["\']?([^"\'\s,]+)["\']?'
            ],
            'negation': [
                r'(\w+)\s+(?:is\s+)?not\s+(?:equal\s+to|=)\s+["\']?([^"\'\s,]+)["\']?',
                r'(\w+)\s+!=\s+["\']?([^"\'\s,]+)["\']?',
                r'(?:exclude|without|except)\s+(\w+)\s+["\']?([^"\'\s,]+)["\']?'
            ]
        }
        
        # Enhanced business domain vocabulary
        self.domain_vocabulary = {
            'financial_terms': {
                'sales': ['sales', 'revenue', 'income', 'earnings', 'turnover'],
                'profit': ['profit', 'margin', 'gain', 'net', 'gross'],
                'budget': ['budget', 'planned', 'target', 'forecast', 'projected'],
                'actual': ['actual', 'real', 'achieved', 'realized', 'current'],
                'variance': ['variance', 'difference', 'delta', 'deviation', 'gap'],
                'cost': ['cost', 'expense', 'expenditure', 'outlay', 'spending']
            },
            'temporal_terms': {
                'year': ['year', 'yearly', 'annual', 'annually', '2023', '2024', '2025'],
                'quarter': ['quarter', 'quarterly', 'q1', 'q2', 'q3', 'q4', 'first quarter', 'second quarter'],
                'month': ['month', 'monthly', 'january', 'february', 'march', 'april', 'may', 'june',
                         'july', 'august', 'september', 'october', 'november', 'december',
                         'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'],
                'date': ['date', 'day', 'time', 'when', 'period', 'during']
            },
            'location_terms': {
                'region': ['region', 'area', 'territory', 'zone', 'district', 'location'],
                'country': ['country', 'nation', 'state', 'province'],
                'city': ['city', 'town', 'urban', 'metropolitan']
            },
            'product_terms': {
                'product': ['product', 'item', 'sku', 'good', 'service', 'offering'],
                'category': ['category', 'type', 'class', 'group', 'segment'],
                'brand': ['brand', 'make', 'manufacturer', 'label']
            }
        }
        
        # Context learning for better column mapping
        self.learned_mappings = defaultdict(set)
        self.query_patterns = defaultdict(int)
        
        # Advanced aggregation patterns
        self.aggregation_patterns = {
            'top_n': [
                r'(?:top|best|highest|largest)\s+(\d+)',
                r'(\d+)\s+(?:highest|largest|best|top)',
                r'show\s+me\s+(?:the\s+)?(\d+)\s+(?:highest|top|best)'
            ],
            'bottom_n': [
                r'(?:bottom|worst|lowest|smallest)\s+(\d+)',
                r'(\d+)\s+(?:lowest|smallest|worst|bottom)',
                r'show\s+me\s+(?:the\s+)?(\d+)\s+(?:lowest|worst|bottom)'
            ],
            'sum_total': [
                r'(?:sum|total|add up|aggregate)',
                r'(?:what|how much)\s+(?:is\s+)?(?:the\s+)?(?:total|sum)',
                r'calculate\s+(?:the\s+)?(?:total|sum)'
            ],
            'average': [
                r'(?:average|mean|avg)',
                r'(?:what|how much)\s+(?:is\s+)?(?:the\s+)?(?:average|mean)',
                r'calculate\s+(?:the\s+)?(?:average|mean)'
            ],
            'count': [
                r'(?:count|number of|how many)',
                r'(?:what|how many)\s+(?:is\s+)?(?:the\s+)?(?:number|count)',
                r'calculate\s+(?:the\s+)?(?:count|number)'
            ],
            'max_min': [
                r'(?:maximum|max|highest|largest)',
                r'(?:minimum|min|lowest|smallest)',
                r'(?:what|how much)\s+(?:is\s+)?(?:the\s+)?(?:max|min|maximum|minimum)'
            ]
        }
        
        # Value type detection patterns
        self.value_type_patterns = {
            'integer': r'^\d+$',
            'float': r'^\d*\.\d+$',
            'percentage': r'^\d+(?:\.\d+)?%$',
            'date': r'^\d{4}-\d{2}-\d{2}$|^\d{1,2}/\d{1,2}/\d{4}$',
            'currency': r'^\$?\d+(?:,\d{3})*(?:\.\d{2})?$'
        }
    
    def set_schema_context(self, schema_info: Dict[str, Any], table_name: str):
        """
        Set schema context and learn from data patterns
        
        Args:
            schema_info: Schema information including columns and sample values
            table_name: Name of the table
        """
        self.schema_info = schema_info
        self.table_name = table_name
        
        # Learn from schema context
        self._learn_from_schema()
    
    def _learn_from_schema(self):
        """Learn patterns from schema information to improve mapping"""
        if not self.schema_info:
            return
        
        columns = self.schema_info.get('columns', [])
        sample_values = self.schema_info.get('sample_values', {})
        
        # Learn column name patterns
        for column in columns:
            column_lower = column.lower()
            
            # Map to domain vocabulary
            for domain, terms_dict in self.domain_vocabulary.items():
                for concept, aliases in terms_dict.items():
                    for alias in aliases:
                        if alias in column_lower or column_lower in alias:
                            self.learned_mappings[concept].add(column)
                            self.learned_mappings[alias].add(column)
        
        # Learn from sample values to understand data patterns
        for column, values in sample_values.items():
            for value in values:
                if pd.notna(value):
                    value_str = str(value).lower()
                    
                    # Learn common value patterns
                    for pattern_name, pattern in self.value_type_patterns.items():
                        if re.match(pattern, str(value).strip()):
                            self.learned_mappings[f"{column}_type"].add(pattern_name)
                            break
    
    def translate_to_sql(self, natural_query: str) -> SQLTranslationResult:
        """
        Translate natural language to SQL using advanced semantic parsing
        
        Args:
            natural_query: Natural language query to translate
            
        Returns:
            SQLTranslationResult with detailed translation information
        """
        try:
            # Clean and normalize query
            normalized_query = self._normalize_query(natural_query)
            
            # Extract semantic components
            conditions = self._extract_semantic_conditions(normalized_query)
            aggregations = self._extract_aggregations(normalized_query)
            columns = self._identify_target_columns(normalized_query)
            
            # Build sophisticated SQL
            sql_query = self._build_semantic_sql(conditions, aggregations, columns, normalized_query)
            
            # Calculate confidence with advanced metrics
            confidence = self._calculate_semantic_confidence(conditions, aggregations, normalized_query)
            
            # Generate detailed explanation
            explanation = self._generate_semantic_explanation(sql_query, conditions, aggregations, columns)
            
            # Learn from this query for future improvements
            self._learn_from_query(natural_query, conditions, aggregations)
            
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
                error_message=f"Semantic parsing failed: {str(e)}"
            )
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for better parsing"""
        # Convert to lowercase
        normalized = query.lower().strip()
        
        # Handle common abbreviations
        abbreviations = {
            'q1': 'first quarter',
            'q2': 'second quarter',
            'q3': 'third quarter',
            'q4': 'fourth quarter',
            'ytd': 'year to date',
            'mtd': 'month to date',
            'yoy': 'year over year'
        }
        
        for abbrev, full_form in abbreviations.items():
            normalized = re.sub(rf'\b{abbrev}\b', full_form, normalized)
        
        # Standardize operators
        operator_replacements = {
            ' greater than ': ' > ',
            ' less than ': ' < ',
            ' equals ': ' = ',
            ' is equal to ': ' = ',
            ' not equal to ': ' != ',
            ' is not ': ' != '
        }
        
        for old_op, new_op in operator_replacements.items():
            normalized = normalized.replace(old_op, new_op)
        
        return normalized
    
    def _extract_semantic_conditions(self, query: str) -> List[Dict]:
        """
        Extract conditions using advanced semantic patterns
        
        Args:
            query: Normalized query string
            
        Returns:
            List of condition dictionaries
        """
        conditions = []
        
        # Process each semantic pattern type
        for pattern_type, patterns in self.semantic_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, query, re.IGNORECASE)
                
                for match in matches:
                    if pattern_type == 'range':
                        # Handle range patterns (3 groups)
                        column_term = match.group(1)
                        start_value = match.group(2).strip('"\'')
                        end_value = match.group(3).strip('"\'')
                        
                        mapped_column = self._map_semantic_column(column_term)
                        if mapped_column:
                            conditions.append({
                                'column': mapped_column,
                                'operator': 'BETWEEN',
                                'value': f"{self._format_value(start_value, mapped_column)} AND {self._format_value(end_value, mapped_column)}",
                                'type': pattern_type,
                                'confidence': 0.8
                            })
                    
                    else:
                        # Handle standard patterns (2 groups)
                        if len(match.groups()) >= 2:
                            column_term = match.group(1)
                            value = match.group(2).strip('"\'')
                            
                            mapped_column = self._map_semantic_column(column_term)
                            if mapped_column:
                                sql_operator = self._get_sql_operator(pattern_type)
                                formatted_value = self._format_value(value, mapped_column)
                                
                                # Check for duplicates
                                existing = any(
                                    c['column'] == mapped_column and c['value'] == formatted_value
                                    for c in conditions
                                )
                                
                                if not existing:
                                    conditions.append({
                                        'column': mapped_column,
                                        'operator': sql_operator,
                                        'value': formatted_value,
                                        'type': pattern_type,
                                        'confidence': self._calculate_condition_confidence(column_term, value, pattern_type)
                                    })
        
        # Post-process to resolve conflicts and improve conditions
        conditions = self._resolve_condition_conflicts(conditions)
        
        return conditions
    
    def _map_semantic_column(self, term: str) -> Optional[str]:
        """
        Map business term to actual column using semantic understanding
        
        Args:
            term: Business term from query
            
        Returns:
            Best matching column name or None
        """
        if not self.schema_info or 'columns' not in self.schema_info:
            return term
        
        available_columns = self.schema_info['columns']
        term_lower = term.lower().strip()
        
        # 1. Exact match
        for col in available_columns:
            if col.lower() == term_lower:
                return col
        
        # 2. Check learned mappings
        if term_lower in self.learned_mappings:
            potential_columns = self.learned_mappings[term_lower]
            for col in potential_columns:
                if col in available_columns:
                    return col
        
        # 3. Semantic similarity with domain vocabulary
        best_match = None
        best_score = 0
        
        for col in available_columns:
            col_lower = col.lower()
            score = 0
            
            # Direct substring match
            if term_lower in col_lower or col_lower in term_lower:
                score += 0.8
            
            # Domain vocabulary matching
            for domain, terms_dict in self.domain_vocabulary.items():
                for concept, aliases in terms_dict.items():
                    if term_lower in aliases:
                        for alias in aliases:
                            if alias in col_lower:
                                score += 0.6
                    if concept in col_lower and term_lower in aliases:
                        score += 0.7
            
            # Fuzzy matching for similar words
            if self._calculate_similarity(term_lower, col_lower) > 0.7:
                score += 0.5
            
            if score > best_score:
                best_score = score
                best_match = col
        
        # Return best match if confidence is high enough
        if best_score > 0.5:
            # Learn this mapping for future use
            self.learned_mappings[term_lower].add(best_match)
            return best_match
        
        return None
    
    def _calculate_similarity(self, term1: str, term2: str) -> float:
        """Calculate similarity between two terms using simple algorithm"""
        # Simple similarity based on character overlap
        set1 = set(term1.lower())
        set2 = set(term2.lower())
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _get_sql_operator(self, pattern_type: str) -> str:
        """Get SQL operator for pattern type"""
        operator_map = {
            'exact_match': '=',
            'greater_than': '>',
            'less_than': '<',
            'range': 'BETWEEN',
            'contains': 'LIKE',
            'negation': '!='
        }
        return operator_map.get(pattern_type, '=')
    
    def _format_value(self, value: str, column: str) -> str:
        """Format value based on detected type and column context"""
        value = value.strip('"\'')
        
        # Check if it's a number
        try:
            float(value)
            return value
        except ValueError:
            pass
        
        # Check for percentage
        if value.endswith('%'):
            try:
                num_value = float(value[:-1])
                return str(num_value / 100)  # Convert percentage to decimal
            except ValueError:
                pass
        
        # Check for currency
        currency_match = re.match(r'^\$?([0-9,]+(?:\.\d{2})?)$', value)
        if currency_match:
            clean_value = currency_match.group(1).replace(',', '')
            try:
                float(clean_value)
                return clean_value
            except ValueError:
                pass
        
        # Check column type if available
        if self.schema_info and 'column_types' in self.schema_info:
            column_type = str(self.schema_info['column_types'].get(column, '')).lower()
            if 'int' in column_type or 'float' in column_type:
                try:
                    float(value)
                    return value
                except ValueError:
                    pass
        
        # For LIKE operations, add wildcards
        if '%' not in value and 'contains' in str(value):
            value = f'%{value}%'
        
        # Default to quoted string
        return f"'{value}'"
    
    def _calculate_condition_confidence(self, column_term: str, value: str, pattern_type: str) -> float:
        """Calculate confidence for a specific condition"""
        confidence = 0.5  # Base confidence
        
        # Boost for exact column matches
        if self.schema_info and 'columns' in self.schema_info:
            if column_term.lower() in [col.lower() for col in self.schema_info['columns']]:
                confidence += 0.3
        
        # Boost for learned mappings
        if column_term.lower() in self.learned_mappings:
            confidence += 0.2
        
        # Boost for clear value types
        for pattern_name, pattern in self.value_type_patterns.items():
            if re.match(pattern, value.strip()):
                confidence += 0.1
                break
        
        # Boost for specific pattern types
        pattern_confidence = {
            'exact_match': 0.9,
            'greater_than': 0.8,
            'less_than': 0.8,
            'range': 0.9,
            'contains': 0.7,
            'negation': 0.8
        }
        
        base_confidence = pattern_confidence.get(pattern_type, 0.5)
        confidence = (confidence + base_confidence) / 2
        
        return min(confidence, 1.0)
    
    def _resolve_condition_conflicts(self, conditions: List[Dict]) -> List[Dict]:
        """Resolve conflicts between conditions and improve quality"""
        if not conditions:
            return conditions
        
        # Group conditions by column
        column_conditions = defaultdict(list)
        for condition in conditions:
            column_conditions[condition['column']].append(condition)
        
        resolved_conditions = []
        
        for column, conds in column_conditions.items():
            if len(conds) == 1:
                resolved_conditions.extend(conds)
            else:
                # Resolve conflicts by taking highest confidence condition
                # unless they can be combined (e.g., range conditions)
                conds.sort(key=lambda x: x['confidence'], reverse=True)
                
                # Check if we can combine conditions
                if len(conds) == 2:
                    cond1, cond2 = conds
                    if (cond1['operator'] == '>' and cond2['operator'] == '<') or \
                       (cond1['operator'] == '<' and cond2['operator'] == '>'):
                        # Combine into BETWEEN condition
                        if cond1['operator'] == '>':
                            start_val = cond1['value']
                            end_val = cond2['value']
                        else:
                            start_val = cond2['value']
                            end_val = cond1['value']
                        
                        combined_condition = {
                            'column': column,
                            'operator': 'BETWEEN',
                            'value': f"{start_val} AND {end_val}",
                            'type': 'range',
                            'confidence': (cond1['confidence'] + cond2['confidence']) / 2
                        }
                        resolved_conditions.append(combined_condition)
                        continue
                
                # Take highest confidence condition
                resolved_conditions.append(conds[0])
        
        return resolved_conditions
    
    def _extract_aggregations(self, query: str) -> List[Dict]:
        """Extract aggregation requirements using advanced patterns"""
        aggregations = []
        
        for agg_type, patterns in self.aggregation_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, query, re.IGNORECASE)
                
                for match in matches:
                    if agg_type in ['top_n', 'bottom_n']:
                        try:
                            limit = int(match.group(1))
                            
                            # Try to find the column for sorting
                            sort_column = self._find_sort_column(query, agg_type)
                            
                            aggregations.append({
                                'type': 'sort_limit',
                                'function': agg_type.split('_')[0],  # 'top' or 'bottom'
                                'limit': limit,
                                'column': sort_column,
                                'confidence': 0.8
                            })
                        except (ValueError, IndexError):
                            pass
                    
                    else:
                        # Find target column for aggregation
                        target_column = self._find_aggregation_column(query, agg_type)
                        
                        sql_function = self._get_aggregation_function(agg_type)
                        
                        aggregations.append({
                            'type': 'function',
                            'function': sql_function,
                            'column': target_column,
                            'confidence': 0.7
                        })
        
        return aggregations
    
    def _find_sort_column(self, query: str, sort_type: str) -> Optional[str]:
        """Find column for sorting in top/bottom queries"""
        # Look for patterns like "top 5 sales", "highest revenue", etc.
        patterns = [
            rf'{sort_type.split("_")[0]}\s+\d+\s+(\w+)',
            rf'(\w+)\s+{sort_type.split("_")[0]}\s+\d+',
            rf'{sort_type.split("_")[0]}\s+\d+\s+by\s+(\w+)',
            rf'(\w+)\s+(?:highest|lowest|best|worst)',
            rf'(?:highest|lowest|best|worst)\s+(\w+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                column_term = match.group(1)
                mapped_column = self._map_semantic_column(column_term)
                if mapped_column:
                    return mapped_column
        
        # Default to first numeric column
        return self._get_default_numeric_column()
    
    def _find_aggregation_column(self, query: str, agg_type: str) -> Optional[str]:
        """Find column for aggregation function"""
        # Look for patterns around aggregation keywords
        agg_keywords = {
            'sum_total': ['sum', 'total'],
            'average': ['average', 'mean', 'avg'],
            'count': ['count', 'number'],
            'max_min': ['max', 'min', 'maximum', 'minimum', 'highest', 'lowest']
        }
        
        keywords = agg_keywords.get(agg_type, [])
        
        for keyword in keywords:
            patterns = [
                rf'{keyword}\s+of\s+(\w+)',
                rf'(\w+)\s+{keyword}',
                rf'{keyword}\s+(\w+)',
                rf'total\s+(\w+)',
                rf'(\w+)\s+total'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    column_term = match.group(1)
                    if column_term.lower() not in ['of', 'the', 'a', 'an']:
                        mapped_column = self._map_semantic_column(column_term)
                        if mapped_column:
                            return mapped_column
        
        return self._get_default_numeric_column()
    
    def _get_default_numeric_column(self) -> Optional[str]:
        """Get default numeric column for aggregations"""
        if not self.schema_info or 'column_types' not in self.schema_info:
            return None
        
        # Look for numeric columns
        numeric_columns = []
        for col, dtype in self.schema_info['column_types'].items():
            if 'int' in str(dtype).lower() or 'float' in str(dtype).lower():
                numeric_columns.append(col)
        
        # Prefer columns with financial terms
        financial_terms = ['sales', 'revenue', 'amount', 'value', 'price', 'cost']
        for term in financial_terms:
            for col in numeric_columns:
                if term in col.lower():
                    return col
        
        # Return first numeric column
        return numeric_columns[0] if numeric_columns else None
    
    def _get_aggregation_function(self, agg_type: str) -> str:
        """Get SQL aggregation function for type"""
        function_map = {
            'sum_total': 'SUM',
            'average': 'AVG',
            'count': 'COUNT',
            'max_min': 'MAX'  # Default to MAX, could be improved
        }
        return function_map.get(agg_type, 'COUNT')
    
    def _identify_target_columns(self, query: str) -> List[str]:
        """Identify specific columns mentioned in query"""
        if not self.schema_info or 'columns' not in self.schema_info:
            return []
        
        mentioned_columns = []
        available_columns = self.schema_info['columns']
        
        # Look for column names or their aliases in the query
        words = re.findall(r'\b\w+\b', query.lower())
        
        for word in words:
            # Check direct matches
            for col in available_columns:
                if word == col.lower():
                    mentioned_columns.append(col)
            
            # Check semantic mappings
            mapped_col = self._map_semantic_column(word)
            if mapped_col and mapped_col not in mentioned_columns:
                mentioned_columns.append(mapped_col)
        
        return mentioned_columns
    
    def _build_semantic_sql(self, conditions: List[Dict], aggregations: List[Dict], 
                           columns: List[str], query: str) -> str:
        """Build SQL using semantic understanding"""
        
        # Determine SELECT clause
        if aggregations:
            select_parts = []
            for agg in aggregations:
                if agg['type'] == 'function' and agg['column']:
                    select_parts.append(f"{agg['function']}({agg['column']}) as {agg['function'].lower()}_{agg['column']}")
                elif agg['type'] == 'function':
                    select_parts.append(f"{agg['function']}(*)")
            
            if select_parts:
                select_clause = f"SELECT {', '.join(select_parts)}"
            else:
                select_clause = "SELECT *"
        elif columns:
            select_clause = f"SELECT {', '.join(columns)}"
        else:
            select_clause = "SELECT *"
        
        # Build FROM clause
        from_clause = f"FROM {self.table_name}"
        
        # Build WHERE clause
        where_conditions = []
        for condition in conditions:
            column = condition['column']
            operator = condition['operator']
            value = condition['value']
            
            if operator == 'LIKE':
                where_conditions.append(f"{column} {operator} {value}")
            elif operator == 'BETWEEN':
                where_conditions.append(f"{column} {operator} {value}")
            else:
                where_conditions.append(f"{column} {operator} {value}")
        
        where_clause = ""
        if where_conditions:
            where_clause = f"WHERE {' AND '.join(where_conditions)}"
        
        # Build ORDER BY and LIMIT
        order_limit_clause = ""
        sort_aggs = [a for a in aggregations if a['type'] == 'sort_limit']
        if sort_aggs:
            agg = sort_aggs[0]
            if agg['column']:
                direction = 'DESC' if agg['function'] == 'top' else 'ASC'
                order_limit_clause = f"ORDER BY {agg['column']} {direction} LIMIT {agg['limit']}"
        elif not aggregations and not where_conditions:
            # Add reasonable limit for exploratory queries
            order_limit_clause = "LIMIT 100"
        
        # Combine all parts
        sql_parts = [select_clause, from_clause]
        if where_clause:
            sql_parts.append(where_clause)
        if order_limit_clause:
            sql_parts.append(order_limit_clause)
        
        return " ".join(sql_parts)
    
    def _calculate_semantic_confidence(self, conditions: List[Dict], aggregations: List[Dict], query: str) -> float:
        """Calculate confidence using semantic analysis"""
        base_confidence = 0.6
        
        # Condition confidence
        if conditions:
            avg_condition_confidence = sum(c['confidence'] for c in conditions) / len(conditions)
            base_confidence += avg_condition_confidence * 0.3
        
        # Aggregation confidence
        if aggregations:
            avg_agg_confidence = sum(a['confidence'] for a in aggregations) / len(aggregations)
            base_confidence += avg_agg_confidence * 0.2
        
        # Query complexity analysis
        complexity_indicators = ['where', 'and', 'or', 'between', 'greater', 'less', 'top', 'sum', 'average']
        complexity_score = sum(1 for indicator in complexity_indicators if indicator in query.lower())
        base_confidence += min(complexity_score * 0.05, 0.15)
        
        # Penalty for no conditions in complex queries
        if len(query.split()) > 5 and not conditions and not aggregations:
            base_confidence *= 0.7
        
        return min(base_confidence, 1.0)
    
    def _generate_semantic_explanation(self, sql_query: str, conditions: List[Dict], 
                                     aggregations: List[Dict], columns: List[str]) -> str:
        """Generate detailed explanation of the semantic translation"""
        parts = []
        
        # Explain selection
        if aggregations:
            agg_descriptions = []
            for agg in aggregations:
                if agg['type'] == 'function':
                    agg_descriptions.append(f"calculating {agg['function']} of {agg['column'] or 'all records'}")
                elif agg['type'] == 'sort_limit':
                    agg_descriptions.append(f"finding {agg['function']} {agg['limit']} records by {agg['column'] or 'default order'}")
            parts.append(f"Aggregating data: {', '.join(agg_descriptions)}")
        elif columns:
            parts.append(f"Selecting columns: {', '.join(columns)}")
        else:
            parts.append("Selecting all available data")
        
        # Explain filtering
        if conditions:
            condition_descriptions = []
            for condition in conditions:
                if condition['operator'] == 'BETWEEN':
                    condition_descriptions.append(f"{condition['column']} {condition['operator']} {condition['value']}")
                else:
                    condition_descriptions.append(f"{condition['column']} {condition['operator']} {condition['value']}")
            parts.append(f"Filtering where: {', '.join(condition_descriptions)}")
        
        # Explain sorting/limiting
        sort_aggs = [a for a in aggregations if a['type'] == 'sort_limit']
        if sort_aggs:
            agg = sort_aggs[0]
            parts.append(f"Sorted by {agg['column']} ({'descending' if agg['function'] == 'top' else 'ascending'}) with limit {agg['limit']}")
        elif 'LIMIT' in sql_query and not sort_aggs:
            parts.append("Limited to reasonable number of results for exploration")
        
        return ". ".join(parts) if parts else "Comprehensive data retrieval with semantic understanding"
    
    def _learn_from_query(self, query: str, conditions: List[Dict], aggregations: List[Dict]):
        """Learn from successful query translation for future improvements"""
        # Track successful pattern usage
        for condition in conditions:
            pattern_key = f"{condition['type']}_{condition['column']}"
            self.query_patterns[pattern_key] += 1
        
        # Learn new column mappings
        query_words = re.findall(r'\b\w+\b', query.lower())
        for condition in conditions:
            for word in query_words:
                if word != condition['column'].lower():
                    self.learned_mappings[word].add(condition['column'])
        
        # This learning data could be persisted for long-term improvement
