"""
Session Manager for VariancePro
Handles session IDs, timestamps, and session-related functionality
"""

import uuid
from datetime import datetime
from typing import Dict, Any


class SessionManager:
    """
    Manages user sessions with unique IDs and timestamps
    Provides utilities for tracking session duration and formatting timestamps
    """
    
    def __init__(self):
        """Initialize a new session with unique ID and start time"""
        self.session_id = str(uuid.uuid4())[:8]  # Short UUID for display
        self.session_start_time = datetime.now()
        
        print(f"🆔 New Session ID: {self.session_id}")
        print(f"⏰ Session started at: {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def get_session_id(self) -> str:
        """Get the current session ID"""
        return self.session_id
    
    def get_session_start_time(self) -> datetime:
        """Get the session start time"""
        return self.session_start_time
    
    def get_session_duration(self) -> str:
        """Get formatted session duration"""
        current_time = datetime.now()
        duration = current_time - self.session_start_time
        return str(duration).split('.')[0]  # Remove microseconds
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp formatted for display"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def format_chat_timestamp(self, include_session: bool = True) -> str:
        """
        Format timestamp for chat messages with optional session info
        
        Args:
            include_session: Whether to include session ID in the timestamp
            
        Returns:
            Formatted timestamp string for chat messages
        """
        timestamp = self.get_current_timestamp()
        if include_session:
            return f"⏰ **Time**: {timestamp} | 🆔 **Session**: {self.session_id}"
        else:
            return f"⏰ **Time**: {timestamp}"
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get comprehensive session information
        
        Returns:
            Dictionary containing all session details
        """
        current_time = datetime.now()
        session_duration = current_time - self.session_start_time
        
        return {
            'session_id': self.session_id,
            'start_time': self.session_start_time,
            'current_time': current_time,
            'duration': session_duration,
            'formatted_start': self.session_start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'formatted_current': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'formatted_duration': str(session_duration).split('.')[0]
        }
    
    def format_status_session_info(self) -> str:
        """
        Format session information for status display
        
        Returns:
            Formatted session info string for status panels
        """
        info = self.get_session_info()
        
        return f"""🆔 **Session Information:**
• Session ID: {info['session_id']}
• Started: {info['formatted_start']}
• Duration: {info['formatted_duration']}
• Current Time: {info['formatted_current']}
"""
    
    def add_timestamp_to_message(self, message: str, include_session: bool = True) -> str:
        """
        Add timestamp to a message
        
        Args:
            message: The original message content
            include_session: Whether to include session info
            
        Returns:
            Message with timestamp appended
        """
        timestamp_info = self.format_chat_timestamp(include_session)
        return f"{message}\n\n---\n{timestamp_info}"
    
    def create_welcome_message(self) -> str:
        """
        Create a welcome message with session information and expandable content
        
        Returns:
            Formatted welcome message with read more/less functionality
        """
        info = self.get_session_info()
        
        return f"""👋 **Welcome to VariancePro!** I'm Aria Sterling, your AI financial analyst.

📊 Upload your financial data and chat with me for comprehensive insights and analysis!

<div class="expandable-content" id="welcome-details">
🆔 **Session ID**: {info['session_id']}<span class="dots">...</span><span class="more-text">
⏰ **Started**: {info['formatted_start']}

## 🚀 What I Can Do For You:

### 📈 **Analysis Types**
• **Contribution Analysis**: 80/20 Pareto analysis to identify top performers
• **Variance Analysis**: Budget vs Actual performance tracking
• **Trend Analysis**: Time series patterns and trailing twelve months (TTM)
• **Top/Bottom N**: Rankings and performance comparisons
• **Custom SQL Queries**: Natural language to SQL translation

### 🎯 **Smart Features**
• **Auto-detect data patterns** in your CSV files
• **Context-aware responses** based on your specific data
• **Interactive field picker** for building queries
• **Real-time insights** with AI-powered analysis
• **Professional reporting** with charts and tables

### 💡 **How to Get Started**
1. **Upload** your CSV file using the upload button
2. **Explore** the auto-generated data summary
3. **Ask questions** like "analyze contribution" or "show trends"
4. **Use quick buttons** for instant analysis
5. **Click field names** to build custom queries

### 🔧 **Advanced Capabilities**
• Multi-threaded SQL processing for large datasets
• Intelligent column detection (dates, categories, financials)
• Business context integration with news analysis
• Session management with full history tracking
• Export-ready formatted reports

💼✨ Ready to transform your data into strategic intelligence!</span>
</div>

<script>
function toggleWelcomeContent() {{
    const container = document.getElementById('welcome-details');
    const btn = document.getElementById('welcome-toggle-btn');
    
    if (container && btn) {{
        if (container.classList.contains('expanded')) {{
            container.classList.remove('expanded');
            btn.textContent = 'Read More';
        }} else {{
            container.classList.add('expanded');
            btn.textContent = 'Read Less';
        }}
    }}
}}

// Auto-run when content loads
setTimeout(() => {{
    const container = document.getElementById('welcome-details');
    if (container && !document.getElementById('welcome-toggle-btn')) {{
        const toggleBtn = document.createElement('span');
        toggleBtn.id = 'welcome-toggle-btn';
        toggleBtn.className = 'read-more-btn';
        toggleBtn.textContent = 'Read More';
        toggleBtn.onclick = toggleWelcomeContent;
        container.parentNode.appendChild(toggleBtn);
    }}
}}, 500);
</script>"""
