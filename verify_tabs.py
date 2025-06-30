#!/usr/bin/env python3
"""
Quick verification script to check the tabs in the VariancePro app
Using BeautifulSoup for more reliable parsing
"""

import requests
import re
import time
from bs4 import BeautifulSoup

def check_tabs(url="http://127.0.0.1:7864", wait_time=3):
    """Check the tabs present in the app"""
    print(f"Checking tabs at {url}...")
    # Wait for the app to fully load
    time.sleep(wait_time)
    
    try:
        # Get the HTML from the running app
        response = requests.get(url)
        html_content = response.text
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all tab buttons
        tab_buttons = soup.find_all('button', {'role': 'tab'})
        
        # Extract tab names
        tabs = [button.text.strip() for button in tab_buttons if button.text.strip()]
        
        print(f"Found {len(tabs)} tabs:")
        for i, tab in enumerate(tabs, 1):
            print(f"  {i}. {tab}")
        
        # Check if there are exactly 2 tabs
        if len(tabs) == 2:
            print("\n✅ SUCCESS: App has exactly 2 tabs")
            
            # Check if they're the correct tabs
            expected_tabs = ["💬 Chat Analysis", "📊 Data View"]
            if sorted([tab.strip() for tab in tabs]) == sorted(expected_tabs):
                print("✅ SUCCESS: Found the correct tabs: 'Chat Analysis' and 'Data View'")
            else:
                print("❌ ERROR: Incorrect tab names")
                print(f"Expected: {expected_tabs}")
                print(f"Found: {tabs}")
        else:
            print(f"\n❌ ERROR: Found {len(tabs)} tabs instead of 2")
            print("Make sure the visualization tab has been removed")
        
        # Also check for visualization-related content
        viz_keywords = ['visualization', 'chart', 'plot', 'graph', 'visualiz']
        found_viz = []
        
        for keyword in viz_keywords:
            if keyword.lower() in html_content.lower():
                found_viz.append(keyword)
        
        if found_viz:
            print(f"\n⚠️  WARNING: Found visualization-related content: {found_viz}")
        else:
            print("\n✅ No visualization-related content found!")
            
    except Exception as e:
        print(f"Error checking tabs: {e}")

if __name__ == "__main__":
    # Try different common ports for Gradio apps
    for port in [7866, 7864, 7863, 7861, 7860]:
        url = f"http://127.0.0.1:{port}"
        print(f"\nTrying port {port}...")
        check_tabs(url)
