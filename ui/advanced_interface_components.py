"""
Advanced Field Picker for Quant Commander
Provides dynamic field selection and query building capabilities
"""

import gradio as gr
from typing import List, Dict, Any, Optional


class FieldPicker:
    """Advanced field picker with query building capabilities"""
    
    def __init__(self, app):
        """Initialize field picker with app reference"""
        self.app = app
        self.selected_fields = []
        self.filter_conditions = []
        
    def get_available_fields(self) -> List[str]:
        """Get list of available fields from current data"""
        if self.app.current_data is None:
            return []
        return list(self.app.current_data.columns)
    
    def get_numeric_fields(self) -> List[str]:
        """Get list of numeric fields for aggregations"""
        if self.app.current_data is None:
            return []
        return list(self.app.current_data.select_dtypes(include=['number']).columns)
    
    def get_categorical_fields(self) -> List[str]:
        """Get list of categorical fields for grouping"""
        if self.app.current_data is None:
            return []
        return list(self.app.current_data.select_dtypes(include=['object', 'category']).columns)
    
    def build_query_from_selection(self, selected_fields: List[str], 
                                 aggregation: str, group_by: List[str],
                                 filters: List[Dict]) -> str:
        """Build natural language query from field selections"""
        query_parts = []
        
        # Start with action
        if aggregation and aggregation != "None":
            query_parts.append(f"{aggregation.lower()}")
            if selected_fields:
                query_parts.append(f"of {', '.join(selected_fields)}")
        else:
            if selected_fields:
                query_parts.append(f"show {', '.join(selected_fields)}")
            else:
                query_parts.append("show all data")
        
        # Add grouping
        if group_by:
            query_parts.append(f"by {', '.join(group_by)}")
        
        # Add filters
        if filters:
            filter_parts = []
            for filter_item in filters:
                field = filter_item.get('field', '')
                operator = filter_item.get('operator', '')
                value = filter_item.get('value', '')
                if field and operator and value:
                    filter_parts.append(f"{field} {operator} {value}")
            
            if filter_parts:
                query_parts.append(f"where {' and '.join(filter_parts)}")
        
        return " ".join(query_parts)
    
    def create_field_picker_interface(self) -> Dict[str, Any]:
        """Create the field picker Gradio interface components"""
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🎯 Field Selection")
                
                field_selector = gr.CheckboxGroup(
                    choices=[],
                    label="Select Fields",
                    info="Choose fields to include in analysis"
                )
                
                aggregation_dropdown = gr.Dropdown(
                    choices=["None", "Sum", "Average", "Count", "Max", "Min"],
                    value="None",
                    label="Aggregation",
                    info="How to aggregate numeric fields"
                )
                
                group_by_selector = gr.CheckboxGroup(
                    choices=[],
                    label="Group By",
                    info="Group results by these fields"
                )
                
            with gr.Column(scale=1):
                gr.Markdown("### 🔍 Filters")
                
                filter_field = gr.Dropdown(
                    choices=[],
                    label="Filter Field",
                    info="Field to filter on"
                )
                
                filter_operator = gr.Dropdown(
                    choices=["greater than", "less than", "equal to", "contains"],
                    label="Operator",
                    info="Filter condition"
                )
                
                filter_value = gr.Textbox(
                    label="Value",
                    info="Filter value"
                )
                
                add_filter_btn = gr.Button("Add Filter", size="sm")
                
                filters_display = gr.Textbox(
                    label="Active Filters",
                    value="No filters applied",
                    interactive=False,
                    lines=3
                )
        
        with gr.Row():
            query_preview = gr.Textbox(
                label="Generated Query",
                placeholder="Your query will appear here...",
                interactive=False,
                lines=2
            )
            
            execute_query_btn = gr.Button("Execute Query 🚀", variant="primary")
        
        return {
            'field_selector': field_selector,
            'aggregation_dropdown': aggregation_dropdown,
            'group_by_selector': group_by_selector,
            'filter_field': filter_field,
            'filter_operator': filter_operator,
            'filter_value': filter_value,
            'add_filter_btn': add_filter_btn,
            'filters_display': filters_display,
            'query_preview': query_preview,
            'execute_query_btn': execute_query_btn
        }
    
    def update_field_choices(self) -> tuple:
        """Update field choices when data is loaded"""
        all_fields = self.get_available_fields()
        numeric_fields = self.get_numeric_fields()
        categorical_fields = self.get_categorical_fields()
        
        return (
            gr.CheckboxGroup(choices=all_fields),  # field_selector
            gr.CheckboxGroup(choices=categorical_fields),  # group_by_selector
            gr.Dropdown(choices=all_fields)  # filter_field
        )
    
    def add_filter(self, field: str, operator: str, value: str, current_filters: str) -> str:
        """Add a new filter to the filter list"""
        if not field or not operator or not value:
            return current_filters
        
        new_filter = f"{field} {operator} {value}"
        
        if current_filters == "No filters applied":
            return new_filter
        else:
            return f"{current_filters}\n{new_filter}"
    
    def update_query_preview(self, selected_fields: List[str], aggregation: str, 
                           group_by: List[str], filters_text: str) -> str:
        """Update the query preview based on current selections"""
        try:
            # Parse filters from text
            filters = []
            if filters_text and filters_text != "No filters applied":
                for line in filters_text.split('\n'):
                    if line.strip():
                        parts = line.split(' ', 2)
                        if len(parts) >= 3:
                            filters.append({
                                'field': parts[0],
                                'operator': parts[1] + ' ' + parts[2].split(' ')[0],
                                'value': ' '.join(parts[2].split(' ')[1:])
                            })
            
            return self.build_query_from_selection(selected_fields, aggregation, group_by, filters)
        except Exception as e:
            return f"Error building query: {str(e)}"


class DataVisualizer:
    """Advanced data visualization components"""
    
    def __init__(self, app):
        """Initialize visualizer with app reference"""
        self.app = app
    
    def create_visualization_interface(self) -> Dict[str, Any]:
        """Create visualization interface components"""
        with gr.Row():
            with gr.Column(scale=2):
                chart_area = gr.Plot(
                    label="Data Visualization",
                    value=None
                )
            
            with gr.Column(scale=1):
                gr.Markdown("### 📊 Chart Options")
                
                chart_type = gr.Dropdown(
                    choices=["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart"],
                    value="Bar Chart",
                    label="Chart Type"
                )
                
                x_axis = gr.Dropdown(
                    choices=[],
                    label="X-Axis Field"
                )
                
                y_axis = gr.Dropdown(
                    choices=[],
                    label="Y-Axis Field"
                )
                
                create_chart_btn = gr.Button("Create Chart 📈", variant="primary")
        
        return {
            'chart_area': chart_area,
            'chart_type': chart_type,
            'x_axis': x_axis,
            'y_axis': y_axis,
            'create_chart_btn': create_chart_btn
        }
    
    def generate_chart(self, chart_type: str, x_field: str, y_field: str):
        """Generate chart based on selections"""
        if self.app.current_data is None:
            return None
        
        try:
            import matplotlib.pyplot as plt
            import pandas as pd
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if chart_type == "Bar Chart":
                # Group by x_field and sum y_field
                grouped_data = self.app.current_data.groupby(x_field)[y_field].sum()
                grouped_data.plot(kind='bar', ax=ax)
                
            elif chart_type == "Line Chart":
                grouped_data = self.app.current_data.groupby(x_field)[y_field].sum()
                grouped_data.plot(kind='line', ax=ax, marker='o')
                
            elif chart_type == "Scatter Plot":
                ax.scatter(self.app.current_data[x_field], self.app.current_data[y_field])
                
            elif chart_type == "Pie Chart":
                grouped_data = self.app.current_data.groupby(x_field)[y_field].sum()
                grouped_data.plot(kind='pie', ax=ax, autopct='%1.1f%%')
            
            ax.set_title(f"{chart_type}: {y_field} by {x_field}")
            plt.tight_layout()
            
            return fig
            
        except Exception as e:
            print(f"Error generating chart: {e}")
            return None


class ExportManager:
    """Advanced export functionality"""
    
    def __init__(self, app):
        """Initialize export manager with app reference"""
        self.app = app
    
    def create_export_interface(self) -> Dict[str, Any]:
        """Create export interface components"""
        gr.Markdown("### 💾 Export Options")
        
        with gr.Row():
            export_format = gr.Dropdown(
                choices=["CSV", "Excel", "JSON", "Analysis Report"],
                value="CSV",
                label="Export Format"
            )
            
            include_filters = gr.Checkbox(
                label="Include Current Filters",
                value=True
            )
        
        with gr.Row():
            export_btn = gr.Button("Export Data 📤", variant="primary")
            download_link = gr.File(
                label="Download",
                visible=False
            )
        
        export_status = gr.Textbox(
            label="Export Status",
            value="Ready to export",
            interactive=False,
            lines=2
        )
        
        return {
            'export_format': export_format,
            'include_filters': include_filters,
            'export_btn': export_btn,
            'download_link': download_link,
            'export_status': export_status
        }
    
    def export_data(self, export_format: str, include_filters: bool) -> tuple:
        """Export data in specified format"""
        if self.app.current_data is None:
            return "❌ No data to export", gr.File(visible=False)
        
        try:
            import tempfile
            import os
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if export_format == "CSV":
                filename = f"quantcommander_export_{timestamp}.csv"
                filepath = os.path.join(tempfile.gettempdir(), filename)
                self.app.current_data.to_csv(filepath, index=False)
                
            elif export_format == "Excel":
                filename = f"quantcommander_export_{timestamp}.xlsx"
                filepath = os.path.join(tempfile.gettempdir(), filename)
                self.app.current_data.to_excel(filepath, index=False)
                
            elif export_format == "JSON":
                filename = f"quantcommander_export_{timestamp}.json"
                filepath = os.path.join(tempfile.gettempdir(), filename)
                self.app.current_data.to_json(filepath, orient='records', indent=2)
                
            elif export_format == "Analysis Report":
                filename = f"quantcommander_report_{timestamp}.txt"
                filepath = os.path.join(tempfile.gettempdir(), filename)
                
                # Generate analysis report
                report_content = self._generate_analysis_report()
                with open(filepath, 'w') as f:
                    f.write(report_content)
            
            status = f"✅ Export successful: {filename}"
            return status, gr.File(value=filepath, visible=True)
            
        except Exception as e:
            return f"❌ Export failed: {str(e)}", gr.File(visible=False)
    
    def _generate_analysis_report(self) -> str:
        """Generate comprehensive analysis report"""
        report_parts = [
            "# Quant Commander Analysis Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Data Summary",
            f"Total Rows: {len(self.app.current_data):,}",
            f"Total Columns: {len(self.app.current_data.columns)}",
            "",
            "## Column Information",
        ]
        
        # Add column details
        for col in self.app.current_data.columns:
            dtype = str(self.app.current_data[col].dtype)
            null_count = self.app.current_data[col].isnull().sum()
            report_parts.append(f"- {col}: {dtype} ({null_count} nulls)")
        
        # Add basic statistics for numeric columns
        numeric_cols = self.app.current_data.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            report_parts.extend([
                "",
                "## Numeric Column Statistics",
                "",
                str(self.app.current_data[numeric_cols].describe())
            ])
        
        return "\n".join(report_parts)
