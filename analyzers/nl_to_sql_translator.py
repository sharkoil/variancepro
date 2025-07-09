"""
Natural Language to SQL Translator for Quant Commander
Converts natural language queries to SQL using financial domain knowledge
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TranslationResult:
    """Result object for NL-to-SQL translation"""
    success: bool
    sql_query: Optional[str] = None
    error_message: Optional[str] = None
    confidence: float = 0.0
    method_used: str = "unknown"  # "pattern" or "llm"


class NLToSQLTranslator:
    """Translate natural language queries to SQL using financial domain knowledge"""
    
    def __init__(self, settings: Dict = None):
        self.settings = settings or {}
        self.table_name = "financial_data"
        self.schema_info = {}
        self.llm_interpreter = None
        self.column_mapping = {}  # Maps original to cleaned column names
        
    def set_schema_context(self, schema_info: Dict, table_name: str = "financial_data", column_mapping: Dict = None):
        """Set the schema context for SQL generation"""
        self.schema_info = schema_info
        self.table_name = table_name
        self.column_mapping = column_mapping or {}
    
    def set_llm_interpreter(self, llm_interpreter):
        """Set LLM interpreter for advanced NL-to-SQL"""
        self.llm_interpreter = llm_interpreter
    
    def translate_to_sql(self, natural_query: str, schema_context: Dict = None) -> TranslationResult:
        """Convert natural language to SQL query"""
        try:
            print(f"[NL-to-SQL] Translating query: {natural_query}")
            
            # Set schema context if provided
            if schema_context:
                table_name = schema_context.get('table_name', 'data')
                self.set_schema_context(schema_context, table_name)
            
            # First try pattern-based translation (fast)
            success, sql_query = self._pattern_based_translation(natural_query)
            
            if success:
                print(f"[NL-to-SQL] Pattern-based translation successful: {sql_query}")
                return TranslationResult(
                    success=True,
                    sql_query=sql_query,
                    confidence=0.8,
                    method_used="pattern"
                )
            
            # Fall back to LLM-based translation (more flexible)
            if self.llm_interpreter and self.llm_interpreter.is_available:
                print("[NL-to-SQL] Using LLM-based translation")
                success, sql_query = self._llm_based_translation(natural_query)
                if success:
                    return TranslationResult(
                        success=True,
                        sql_query=sql_query,
                        confidence=0.9,
                        method_used="llm"
                    )
                else:
                    return TranslationResult(
                        success=False,
                        error_message=sql_query,  # Error message in this case
                        method_used="llm"
                    )
            
            # Fall back to basic template matching
            print("[NL-to-SQL] Using template-based translation")
            success, sql_query = self._template_based_translation(natural_query)
            
            if success:
                return TranslationResult(
                    success=True,
                    sql_query=sql_query,
                    confidence=0.6,
                    method_used="template"
                )
            else:
                return TranslationResult(
                    success=False,
                    error_message=sql_query,  # Error message in this case
                    method_used="template"
                )
            
        except Exception as e:
            print(f"[NL-to-SQL ERROR] Translation failed: {str(e)}")
            return TranslationResult(
                success=False,
                error_message=f"Translation error: {str(e)}"
            )
    
    def _pattern_based_translation(self, query: str) -> Tuple[bool, str]:
        """Fast pattern-based SQL generation for common queries"""
        query_lower = query.lower().strip()
        
        # Common financial analysis patterns
        patterns = [
            {
                'pattern': r'(?:show|give|list|find)\s+(?:me\s+)?(?:the\s+)?top\s+(\d+)\s+(.+?)\s+by\s+(.+)',
                'handler': self._handle_top_pattern
            },
            {
                'pattern': r'(?:show|give|list|find)\s+(?:me\s+)?(?:the\s+)?bottom\s+(\d+)\s+(.+?)\s+by\s+(.+)',
                'handler': self._handle_bottom_pattern
            },
            {
                'pattern': r'(?:what|show)\s+(?:is\s+)?(?:the\s+)?total\s+(.+?)(?:\s+for\s+(.+))?',
                'handler': self._handle_total_pattern
            },
            {
                'pattern': r'(?:what|show)\s+(?:is\s+)?(?:the\s+)?average\s+(.+?)\s+(?:by\s+(.+))?',
                'handler': self._handle_average_pattern
            },
            {
                'pattern': r'how\s+many\s+(.+?)(?:\s+(?:are|where)\s+(.+))?',
                'handler': self._handle_count_pattern
            },
            {
                'pattern': r'(?:show|list|find)\s+(?:all\s+)?(.+?)\s+where\s+(.+)',
                'handler': self._handle_where_pattern
            }
        ]
        
        for pattern_info in patterns:
            match = re.search(pattern_info['pattern'], query_lower)
            if match:
                try:
                    return pattern_info['handler'](match, query_lower)
                except Exception as e:
                    print(f"[NL-to-SQL] Pattern handler failed: {str(e)}")
                    continue
        
        return False, "No matching pattern found"
    
    def _handle_top_pattern(self, match, query: str) -> Tuple[bool, str]:
        """Handle top N queries"""
        n = int(match.group(1))
        group_entity = match.group(2).strip()
        value_entity = match.group(3).strip()
        
        group_col = self._find_column(group_entity)
        value_col = self._find_column(value_entity)
        
        if not group_col or not value_col:
            return False, f"Could not identify columns for '{group_entity}' or '{value_entity}'"
        
        sql = f"SELECT {group_col}, SUM({value_col}) as total FROM {self.table_name} GROUP BY {group_col} ORDER BY total DESC LIMIT {n}"
        return True, sql
    
    def _handle_bottom_pattern(self, match, query: str) -> Tuple[bool, str]:
        """Handle bottom N queries"""
        n = int(match.group(1))
        group_entity = match.group(2).strip()
        value_entity = match.group(3).strip()
        
        group_col = self._find_column(group_entity)
        value_col = self._find_column(value_entity)
        
        if not group_col or not value_col:
            return False, f"Could not identify columns for '{group_entity}' or '{value_entity}'"
        
        sql = f"SELECT {group_col}, SUM({value_col}) as total FROM {self.table_name} GROUP BY {group_col} ORDER BY total ASC LIMIT {n}"
        return True, sql
    
    def _handle_total_pattern(self, match, query: str) -> Tuple[bool, str]:
        """Handle total/sum queries"""
        value_entity = match.group(1).strip()
        filter_entity = match.group(2).strip() if match.group(2) else None
        
        value_col = self._find_column(value_entity)
        if not value_col:
            return False, f"Could not identify column for '{value_entity}'"
        
        if filter_entity:
            filter_col = self._find_column(filter_entity)
            if filter_col:
                sql = f"SELECT {filter_col}, SUM({value_col}) as total FROM {self.table_name} GROUP BY {filter_col}"
            else:
                sql = f"SELECT SUM({value_col}) as total FROM {self.table_name}"
        else:
            sql = f"SELECT SUM({value_col}) as total FROM {self.table_name}"
        
        return True, sql
    
    def _handle_average_pattern(self, match, query: str) -> Tuple[bool, str]:
        """Handle average queries"""
        value_entity = match.group(1).strip()
        group_entity = match.group(2).strip() if match.group(2) else None
        
        value_col = self._find_column(value_entity)
        if not value_col:
            return False, f"Could not identify column for '{value_entity}'"
        
        if group_entity:
            group_col = self._find_column(group_entity)
            if group_col:
                sql = f"SELECT {group_col}, AVG({value_col}) as average FROM {self.table_name} GROUP BY {group_col}"
            else:
                sql = f"SELECT AVG({value_col}) as average FROM {self.table_name}"
        else:
            sql = f"SELECT AVG({value_col}) as average FROM {self.table_name}"
        
        return True, sql
    
    def _handle_count_pattern(self, match, query: str) -> Tuple[bool, str]:
        """Handle count queries"""
        entity = match.group(1).strip()
        condition = match.group(2).strip() if match.group(2) else None
        
        if condition:
            # Try to parse simple conditions
            where_clause = self._parse_simple_condition(condition)
            if where_clause:
                sql = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE {where_clause}"
            else:
                sql = f"SELECT COUNT(*) as count FROM {self.table_name}"
        else:
            sql = f"SELECT COUNT(*) as count FROM {self.table_name}"
        
        return True, sql
    
    def _handle_where_pattern(self, match, query: str) -> Tuple[bool, str]:
        """Handle queries with WHERE conditions"""
        entity = match.group(1).strip()
        condition = match.group(2).strip()
        
        where_clause = self._parse_simple_condition(condition)
        if where_clause:
            sql = f"SELECT * FROM {self.table_name} WHERE {where_clause} LIMIT 100"
        else:
            sql = f"SELECT * FROM {self.table_name} LIMIT 100"
        
        return True, sql
    
    def _find_column(self, entity: str) -> Optional[str]:
        """Find the best matching column for an entity"""
        entity_lower = entity.lower()
        
        # Direct match with cleaned column names
        for col in self.schema_info.get('columns', []):
            if col.lower() == entity_lower:
                return col
        
        # Partial match
        for col in self.schema_info.get('columns', []):
            if entity_lower in col.lower() or col.lower() in entity_lower:
                return col
        
        # Financial keyword matching
        financial_mappings = {
            'sales': ['sales', 'revenue', 'amount'],
            'revenue': ['revenue', 'sales', 'income'],
            'amount': ['amount', 'value', 'total'],
            'products': ['product', 'item', 'sku'],
            'customers': ['customer', 'client', 'account'],
            'regions': ['region', 'state', 'location', 'territory'],
            'dates': ['date', 'time', 'period'],
            'budget': ['budget', 'plan', 'target'],
            'actual': ['actual', 'real', 'current']
        }
        
        for keyword, alternatives in financial_mappings.items():
            if any(alt in entity_lower for alt in alternatives):
                for col in self.schema_info.get('columns', []):
                    if any(alt in col.lower() for alt in alternatives):
                        return col
        
        # Default to first numeric column for values, first categorical for groups
        if any(word in entity_lower for word in ['sales', 'revenue', 'amount', 'value', 'total', 'budget', 'actual']):
            numeric_cols = self.schema_info.get('numeric_columns', [])
            return numeric_cols[0] if numeric_cols else None
        else:
            categorical_cols = self.schema_info.get('categorical_columns', [])
            return categorical_cols[0] if categorical_cols else None
    
    def _parse_simple_condition(self, condition: str) -> Optional[str]:
        """Parse simple WHERE conditions"""
        condition = condition.strip()
        
        # Simple equality conditions
        equality_patterns = [
            r'(.+?)\s+(?:is|equals?)\s+(.+)',
            r'(.+?)\s*=\s*(.+)',
        ]
        
        for pattern in equality_patterns:
            match = re.search(pattern, condition, re.IGNORECASE)
            if match:
                col_entity = match.group(1).strip()
                value = match.group(2).strip().strip("'\"")
                
                col = self._find_column(col_entity)
                if col:
                    return f"{col} = '{value}'"
        
        # Numeric comparison conditions
        comparison_patterns = [
            r'(.+?)\s+(>|<|>=|<=)\s+(\d+(?:\.\d+)?)',
            r'(.+?)\s+(?:greater than|more than|above)\s+(\d+(?:\.\d+)?)',
            r'(.+?)\s+(?:less than|below)\s+(\d+(?:\.\d+)?)',
        ]
        
        for pattern in comparison_patterns:
            match = re.search(pattern, condition, re.IGNORECASE)
            if match:
                col_entity = match.group(1).strip()
                operator = match.group(2) if len(match.groups()) == 3 else '>' if 'greater' in condition else '<'
                value = match.group(-1)  # Last group is always the number
                
                col = self._find_column(col_entity)
                if col:
                    return f"{col} {operator} {value}"
        
        return None
    
    def _llm_based_translation(self, query: str) -> Tuple[bool, str]:
        """Use LLM to generate SQL from natural language"""
        try:
            schema_context = self._format_schema_for_llm()
            
            # Enhanced prompt with function calling support for Gemma3
            prompt = f"""
You are a SQL expert assistant. Convert the natural language query to a valid SQL query.

SCHEMA INFORMATION:
{schema_context}

TABLE NAME: {self.table_name}

NATURAL LANGUAGE QUERY: "{query}"

CONVERSION RULES:
1. Only generate SELECT queries (no INSERT, UPDATE, DELETE, DROP)
2. Use the exact column names from the schema above
3. Use appropriate aggregations (SUM, AVG, COUNT, MIN, MAX)
4. Add proper GROUP BY clauses when aggregating
5. Add ORDER BY clauses for top/bottom queries
6. Use LIMIT for top/bottom queries (default 10 if not specified)
7. Handle date filtering appropriately
8. Use single quotes for string literals
9. Be case-insensitive for column matching

EXAMPLES:
- "top 5 products by sales" → SELECT product, SUM(sales) as total FROM {self.table_name} GROUP BY product ORDER BY total DESC LIMIT 5
- "average revenue by region" → SELECT region, AVG(revenue) as average FROM {self.table_name} GROUP BY region
- "total sales" → SELECT SUM(sales) as total FROM {self.table_name}

RESPOND WITH ONLY THE SQL QUERY (no explanation, no markdown):
"""
            
            response = self.llm_interpreter.query_llm(prompt, {})
            if response.success:
                sql_query = self._clean_sql_response(response.content)
                return True, sql_query
            else:
                return False, f"LLM translation failed: {response.error}"
                
        except Exception as e:
            return False, f"LLM translation error: {str(e)}"
    
    def _template_based_translation(self, query: str) -> Tuple[bool, str]:
        """Basic template-based SQL generation"""
        query_lower = query.lower().strip()
        
        # Simple keyword-based templates
        if 'top' in query_lower and any(word in query_lower for word in ['5', '10', '20']):
            n = 10  # default
            for num in ['5', '10', '20']:
                if num in query_lower:
                    n = int(num)
                    break
            
            value_col = self._guess_value_column()
            group_col = self._guess_group_column()
            return True, f"SELECT {group_col}, SUM({value_col}) as total FROM {self.table_name} GROUP BY {group_col} ORDER BY total DESC LIMIT {n}"
        
        elif 'bottom' in query_lower:
            value_col = self._guess_value_column()
            group_col = self._guess_group_column()
            return True, f"SELECT {group_col}, SUM({value_col}) as total FROM {self.table_name} GROUP BY {group_col} ORDER BY total ASC LIMIT 10"
        
        elif 'total' in query_lower or 'sum' in query_lower:
            value_col = self._guess_value_column()
            return True, f"SELECT SUM({value_col}) as total FROM {self.table_name}"
        
        elif 'average' in query_lower or 'avg' in query_lower:
            value_col = self._guess_value_column()
            group_col = self._guess_group_column()
            return True, f"SELECT {group_col}, AVG({value_col}) as average FROM {self.table_name} GROUP BY {group_col}"
        
        elif 'count' in query_lower:
            return True, f"SELECT COUNT(*) as count FROM {self.table_name}"
        
        else:
            return True, f"SELECT * FROM {self.table_name} LIMIT 100"
    
    def _format_schema_for_llm(self) -> str:
        """Format schema information for LLM context"""
        if not self.schema_info:
            return "Schema information not available"
        
        schema_text = f"Table: {self.table_name}\n"
        schema_text += "Columns:\n"
        
        for col in self.schema_info.get('columns', []):
            col_type = self.schema_info.get('dtypes', {}).get(col, 'unknown')
            schema_text += f"  - {col} ({col_type})\n"
        
        # Add column categories
        numeric_cols = self.schema_info.get('numeric_columns', [])
        categorical_cols = self.schema_info.get('categorical_columns', [])
        date_cols = self.schema_info.get('date_columns', [])
        
        if numeric_cols:
            schema_text += f"\nNumeric columns (for aggregation): {', '.join(numeric_cols)}\n"
        if categorical_cols:
            schema_text += f"Categorical columns (for grouping): {', '.join(categorical_cols)}\n"
        if date_cols:
            schema_text += f"Date columns: {', '.join(date_cols)}\n"
        
        return schema_text
    
    def _clean_sql_response(self, response: str) -> str:
        """Clean and validate SQL response from LLM"""
        # Remove markdown formatting
        response = response.strip()
        if response.startswith('```'):
            lines = response.split('\n')
            # Find the SQL content between markdown blocks
            sql_lines = []
            in_code_block = False
            for line in lines:
                if line.startswith('```'):
                    in_code_block = not in_code_block
                    continue
                if in_code_block or line.strip().lower().startswith('select'):
                    sql_lines.append(line)
            response = '\n'.join(sql_lines)
        
        # Remove any non-SQL text
        response = response.strip()
        if not response.lower().startswith('select'):
            # Try to find SELECT statement in response
            select_match = re.search(r'(SELECT.*?(?:;|$))', response, re.IGNORECASE | re.DOTALL)
            if select_match:
                response = select_match.group(1)
        
        return response.rstrip(';').strip()
    
    def _guess_value_column(self) -> str:
        """Guess the most likely value column for aggregation"""
        numeric_cols = self.schema_info.get('numeric_columns', [])
        
        # Prefer financial columns
        financial_keywords = ['sales', 'revenue', 'amount', 'value', 'total', 'actual', 'budget']
        for keyword in financial_keywords:
            for col in numeric_cols:
                if keyword.lower() in col.lower():
                    return col
        
        # Return first numeric column as fallback
        return numeric_cols[0] if numeric_cols else 'value'
    
    def _guess_group_column(self) -> str:
        """Guess the most likely grouping column"""
        categorical_cols = self.schema_info.get('categorical_columns', [])
        
        # Prefer common business dimensions
        business_keywords = ['product', 'category', 'region', 'state', 'department', 'customer']
        for keyword in business_keywords:
            for col in categorical_cols:
                if keyword.lower() in col.lower():
                    return col
        
        # Return first categorical column as fallback
        return categorical_cols[0] if categorical_cols else 'category'
