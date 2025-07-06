#!/usr/bin/env python3
"""
Sample CSV Data Generator for VariancePro
Generates realistic financial data with configurable parameters
"""

import pandas as pd
import numpy as np
import argparse
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import random

# Sample data definitions
STATES_CITIES = {
    'Alabama': ['Birmingham', 'Mobile', 'Montgomery'],
    'Alaska': ['Anchorage', 'Fairbanks', 'Juneau'],
    'Arizona': ['Phoenix', 'Tucson', 'Mesa'],
    'Arkansas': ['Little Rock', 'Fort Smith', 'Fayetteville'],
    'California': ['Los Angeles', 'San Diego', 'San Jose'],
    'Colorado': ['Denver', 'Colorado Springs', 'Aurora'],
    'Connecticut': ['Bridgeport', 'New Haven', 'Hartford'],
    'Delaware': ['Wilmington', 'Dover', 'Newark'],
    'Florida': ['Jacksonville', 'Miami', 'Tampa'],
    'Georgia': ['Atlanta', 'Columbus', 'Augusta'],
    'Hawaii': ['Honolulu', 'Pearl City', 'Hilo'],
    'Idaho': ['Boise', 'Meridian', 'Nampa'],
    'Illinois': ['Chicago', 'Aurora', 'Rockford'],
    'Indiana': ['Indianapolis', 'Fort Wayne', 'Evansville'],
    'Iowa': ['Des Moines', 'Cedar Rapids', 'Davenport'],
    'Kansas': ['Wichita', 'Overland Park', 'Kansas City'],
    'Kentucky': ['Louisville', 'Lexington', 'Bowling Green'],
    'Louisiana': ['New Orleans', 'Baton Rouge', 'Shreveport'],
    'Maine': ['Portland', 'Lewiston', 'Bangor'],
    'Maryland': ['Baltimore', 'Frederick', 'Rockville'],
    'Massachusetts': ['Boston', 'Worcester', 'Springfield'],
    'Michigan': ['Detroit', 'Grand Rapids', 'Warren'],
    'Minnesota': ['Minneapolis', 'Saint Paul', 'Rochester'],
    'Mississippi': ['Jackson', 'Gulfport', 'Southaven'],
    'Missouri': ['Kansas City', 'Saint Louis', 'Springfield'],
    'Montana': ['Billings', 'Missoula', 'Great Falls'],
    'Nebraska': ['Omaha', 'Lincoln', 'Bellevue'],
    'Nevada': ['Las Vegas', 'Henderson', 'Reno'],
    'New Hampshire': ['Manchester', 'Nashua', 'Concord'],
    'New Jersey': ['Newark', 'Jersey City', 'Paterson'],
    'New Mexico': ['Albuquerque', 'Las Cruces', 'Rio Rancho'],
    'New York': ['New York City', 'Buffalo', 'Rochester'],
    'North Carolina': ['Charlotte', 'Raleigh', 'Greensboro'],
    'North Dakota': ['Fargo', 'Bismarck', 'Grand Forks'],
    'Ohio': ['Columbus', 'Cleveland', 'Cincinnati'],
    'Oklahoma': ['Oklahoma City', 'Tulsa', 'Norman'],
    'Oregon': ['Portland', 'Eugene', 'Salem'],
    'Pennsylvania': ['Philadelphia', 'Pittsburgh', 'Allentown'],
    'Rhode Island': ['Providence', 'Warwick', 'Cranston'],
    'South Carolina': ['Charleston', 'Columbia', 'North Charleston'],
    'South Dakota': ['Sioux Falls', 'Rapid City', 'Aberdeen'],
    'Tennessee': ['Nashville', 'Memphis', 'Knoxville'],
    'Texas': ['Houston', 'San Antonio', 'Dallas'],
    'Utah': ['Salt Lake City', 'West Valley City', 'Provo'],
    'Vermont': ['Burlington', 'Essex', 'South Burlington'],
    'Virginia': ['Virginia Beach', 'Norfolk', 'Chesapeake'],
    'Washington': ['Seattle', 'Spokane', 'Tacoma'],
    'West Virginia': ['Charleston', 'Huntington', 'Parkersburg'],
    'Wisconsin': ['Milwaukee', 'Madison', 'Green Bay'],
    'Wyoming': ['Cheyenne', 'Casper', 'Laramie']
}

PRODUCTS = [
    'Premium Laptop Pro',
    'Smart Home Security System',
    'Wireless Gaming Headset',
    'Professional Coffee Machine',
    'Fitness Tracker Elite',
    '4K Ultra HD TV',
    'Electric Standing Desk',
    'Bluetooth Speaker Max',
    'Digital Camera Pro',
    'Smart Watch Series X'
]

CATEGORIES = [
    'Electronics',
    'Home & Garden', 
    'Health & Fitness',
    'Office & Business'
]

PRODUCT_CATEGORIES = {
    'Premium Laptop Pro': 'Electronics',
    'Smart Home Security System': 'Home & Garden',
    'Wireless Gaming Headset': 'Electronics',
    'Professional Coffee Machine': 'Home & Garden',
    'Fitness Tracker Elite': 'Health & Fitness',
    '4K Ultra HD TV': 'Electronics',
    'Electric Standing Desk': 'Office & Business',
    'Bluetooth Speaker Max': 'Electronics',
    'Digital Camera Pro': 'Electronics',
    'Smart Watch Series X': 'Health & Fitness'
}

CHANNELS = ['Online', 'Retail', 'Direct Sales', 'Partner']

class SampleDataGenerator:
    """Generate realistic sample CSV data for financial analysis"""
    
    def __init__(self):
        """Initialize the generator with random seed for reproducibility"""
        random.seed(42)
        np.random.seed(42)
    
    def generate_data(self, 
                     start_date: str,
                     end_date: str,
                     row_count: int,
                     num_products: int,
                     output_file: str) -> None:
        """
        Generate sample data with specified parameters
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            row_count: Number of rows to generate
            num_products: Number of products to include (1-10)
            output_file: Output CSV file path
        """
        
        # Validate inputs
        if num_products < 1 or num_products > 10:
            raise ValueError("Number of products must be between 1 and 10")
        
        # Parse dates
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start_dt >= end_dt:
            raise ValueError("Start date must be before end date")
        
        # Select products
        selected_products = PRODUCTS[:num_products]
        
        print(f"🔧 Generating {row_count:,} rows of data...")
        print(f"📅 Date range: {start_date} to {end_date}")
        print(f"📦 Products: {num_products} ({', '.join(selected_products)})")
        
        # Generate data
        data = []
        
        for i in range(row_count):
            # Generate random date in range
            days_diff = (end_dt - start_dt).days
            random_days = random.randint(0, days_diff)
            record_date = start_dt + timedelta(days=random_days)
            
            # Select random location
            state = random.choice(list(STATES_CITIES.keys()))
            city = random.choice(STATES_CITIES[state])
            
            # Select random product
            product = random.choice(selected_products)
            category = PRODUCT_CATEGORIES[product]
            
            # Select random channel
            channel = random.choice(CHANNELS)
            
            # Generate realistic budget and actuals
            # Base budget varies by product category
            if category == 'Electronics':
                base_budget = random.randint(50000, 200000)
            elif category == 'Home & Garden':
                base_budget = random.randint(30000, 150000)
            elif category == 'Health & Fitness':
                base_budget = random.randint(20000, 100000)
            else:  # Office & Business
                base_budget = random.randint(40000, 180000)
            
            # Add some variance based on location (coastal states tend higher)
            coastal_states = ['California', 'Florida', 'New York', 'Washington', 'Massachusetts']
            if state in coastal_states:
                base_budget = int(base_budget * random.uniform(1.1, 1.3))
            
            # Add channel multiplier
            channel_multipliers = {
                'Online': random.uniform(0.8, 1.2),
                'Retail': random.uniform(0.9, 1.1),
                'Direct Sales': random.uniform(1.1, 1.4),
                'Partner': random.uniform(0.7, 1.0)
            }
            
            budget = int(base_budget * channel_multipliers[channel])
            
            # Generate actuals with realistic variance (-20% to +30%)
            variance_factor = random.uniform(0.8, 1.3)
            actuals = int(budget * variance_factor)
            
            # Create record
            record = {
                'Date': record_date.strftime('%Y-%m-%d'),
                'Product': product,
                'Category': category,
                'State': state,
                'City': city,
                'Budget': budget,
                'Actuals': actuals,
                'Channel': channel
            }
            
            data.append(record)
            
            # Progress indicator
            if (i + 1) % 50 == 0 or i == row_count - 1:
                progress = ((i + 1) / row_count) * 100
                print(f"📊 Progress: {i + 1:,}/{row_count:,} ({progress:.1f}%)")
        
        # Create DataFrame and save
        df = pd.DataFrame(data)
        
        # Sort by date for better readability
        df = df.sort_values('Date').reset_index(drop=True)
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        
        # Generate summary
        print(f"\n✅ Data generation complete!")
        print(f"📁 Output file: {output_file}")
        print(f"📊 Total rows: {len(df):,}")
        print(f"📅 Date range: {df['Date'].min()} to {df['Date'].max()}")
        print(f"🏢 States: {df['State'].nunique()}")
        print(f"🏙️ Cities: {df['City'].nunique()}")
        print(f"📦 Products: {df['Product'].nunique()}")
        print(f"🏷️ Categories: {df['Category'].nunique()}")
        print(f"📺 Channels: {df['Channel'].nunique()}")
        print(f"💰 Budget range: ${df['Budget'].min():,} - ${df['Budget'].max():,}")
        print(f"💸 Actuals range: ${df['Actuals'].min():,} - ${df['Actuals'].max():,}")
        
        # Show sample data
        print(f"\n📄 Sample data:")
        print(df.head(3).to_string(index=False))

def main():
    """Main command line interface"""
    parser = argparse.ArgumentParser(
        description='Generate sample CSV data for VariancePro financial analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 200 rows for 2024 with 5 products
  python generate_sample_data.py --start 2024-01-01 --end 2024-12-31 --rows 200 --products 5
  
  # Generate 1000 rows for Q1 2025 with all products
  python generate_sample_data.py --start 2025-01-01 --end 2025-03-31 --rows 1000 --products 10 --output q1_2025_data.csv
  
  # Generate small test dataset
  python generate_sample_data.py --start 2024-06-01 --end 2024-06-30 --rows 50 --products 3 --output test_data.csv
        """
    )
    
    parser.add_argument('--start', '-s', 
                       help='Start date (YYYY-MM-DD)')
    
    parser.add_argument('--end', '-e',
                       help='End date (YYYY-MM-DD)')
    
    parser.add_argument('--rows', '-r',
                       type=int,
                       help='Number of rows to generate')
    
    parser.add_argument('--products', '-p',
                       type=int,
                       default=5,
                       help='Number of products to include (1-10, default: 5)')
    
    parser.add_argument('--output', '-o',
                       default='sample_financial_data.csv',
                       help='Output CSV file name (default: sample_financial_data.csv)')
    
    parser.add_argument('--list-products',
                       action='store_true',
                       help='List available products and exit')
    
    args = parser.parse_args()
    
    # Handle list products command
    if args.list_products:
        print("📦 Available Products:")
        for i, product in enumerate(PRODUCTS, 1):
            category = PRODUCT_CATEGORIES[product]
            print(f"  {i:2d}. {product} ({category})")
        print(f"\n🏷️ Categories: {', '.join(CATEGORIES)}")
        print(f"📺 Channels: {', '.join(CHANNELS)}")
        print(f"🏢 States: {len(STATES_CITIES)} states with 3 cities each")
        return
    
    # Validate required arguments when not listing products
    if not args.start or not args.end or args.rows is None:
        parser.error("--start, --end, and --rows are required when not using --list-products")
    
    try:
        # Create generator and generate data
        generator = SampleDataGenerator()
        generator.generate_data(
            start_date=args.start,
            end_date=args.end,
            row_count=args.rows,
            num_products=args.products,
            output_file=args.output
        )
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
