# Sample Data Generator for VariancePro

## Overview
The `generate_sample_data.py` script creates realistic financial CSV data for testing VariancePro's analysis capabilities. It generates data with the exact column structure needed: Date, Product, Category, State, City, Budget, Actuals, Channel.

## Features

### ✅ **Data Structure**
- **Date**: Random dates within specified range
- **Product**: 10 predefined realistic products
- **Category**: 4 business categories (Electronics, Home & Garden, Health & Fitness, Office & Business)
- **State**: All 50 US states
- **City**: 3 largest cities per state (150 cities total)
- **Budget**: Realistic budget amounts based on product category and location
- **Actuals**: Realistic actual amounts with variance from budget (-20% to +30%)
- **Channel**: 4 sales channels (Online, Retail, Direct Sales, Partner)

### 🎯 **Configurable Parameters**
- **Date Range**: Specify start and end dates
- **Row Count**: Generate any number of records
- **Product Selection**: Choose 1-10 products to include
- **Output File**: Custom CSV filename

### 📊 **Realistic Data Generation**
- **Location-based pricing**: Coastal states have higher budgets
- **Channel multipliers**: Different channels affect budget amounts
- **Category-based ranges**: Electronics highest, Health & Fitness lowest
- **Realistic variance**: Actuals vary realistically from budget

## Usage

### Basic Usage
```bash
# Generate 200 rows for 2024 with 5 products
python generate_sample_data.py --start 2024-01-01 --end 2024-12-31 --rows 200 --products 5
```

### Advanced Examples
```bash
# Generate large dataset for Q1 2025 with all products
python generate_sample_data.py --start 2025-01-01 --end 2025-03-31 --rows 1000 --products 10 --output q1_2025_data.csv

# Generate small test dataset for June 2024
python generate_sample_data.py --start 2024-06-01 --end 2024-06-30 --rows 50 --products 3 --output test_data.csv

# Generate large annual dataset
python generate_sample_data.py --start 2024-01-01 --end 2024-12-31 --rows 2000 --products 8 --output annual_2024.csv
```

### Information Commands
```bash
# List all available products and categories
python generate_sample_data.py --list-products

# Show help and examples
python generate_sample_data.py --help
```

## Command Line Options

| Option | Short | Required | Description |
|--------|-------|----------|-------------|
| `--start` | `-s` | Yes* | Start date (YYYY-MM-DD) |
| `--end` | `-e` | Yes* | End date (YYYY-MM-DD) |
| `--rows` | `-r` | Yes* | Number of rows to generate |
| `--products` | `-p` | No | Number of products (1-10, default: 5) |
| `--output` | `-o` | No | Output file (default: sample_financial_data.csv) |
| `--list-products` | | No | List products and exit |

*Not required when using `--list-products`

## Sample Output

### Console Output
```
🔧 Generating 200 rows of data...
📅 Date range: 2024-01-01 to 2024-12-31
📦 Products: 5 (Premium Laptop Pro, Smart Home Security System, ...)
📊 Progress: 200/200 (100.0%)

✅ Data generation complete!
📁 Output file: test_data_200.csv
📊 Total rows: 200
📅 Date range: 2024-01-01 to 2024-12-29
🏢 States: 50
🏙️ Cities: 106
📦 Products: 5
🏷️ Categories: 3
📺 Channels: 4
💰 Budget range: $25,445 - $271,381
💸 Actuals range: $24,764 - $320,137
```

### CSV Structure
```csv
Date,Product,Category,State,City,Budget,Actuals,Channel
2024-01-01,Professional Coffee Machine,Home & Garden,Texas,Dallas,32934,38861,Partner
2024-01-02,Wireless Gaming Headset,Electronics,Maine,Bangor,82625,81683,Partner
2024-01-04,Premium Laptop Pro,Electronics,California,San Jose,79247,71886,Retail
```

## Data Quality Features

### 🎯 **Realistic Patterns**
- Budget amounts vary by product category and geographic location
- Coastal states (CA, FL, NY, WA, MA) have 10-30% higher budgets
- Electronics products have highest budget ranges ($50K-$200K)
- Home & Garden products have mid-range budgets ($30K-$150K)
- Health & Fitness has lowest ranges ($20K-$100K)

### 📈 **Variance Analysis Ready**
- Actuals vary from budget with realistic patterns
- Some records over-perform (up to +30%)
- Some records under-perform (down to -20%)
- Perfect for variance analysis testing

### 🌐 **Geographic Distribution**
- All 50 US states represented
- 3 major cities per state (150 total cities)
- Realistic state/city combinations
- Geographic pricing patterns

## Integration with VariancePro

### ✅ **Perfect for Testing**
- Generate test data matching VariancePro's expected format
- Test CSV upload and validation features
- Test quantified metrics display
- Test LLM analysis capabilities

### 📊 **Analysis Ready**
- Ready for contribution analysis
- Budget vs Actuals variance analysis
- Geographic performance analysis
- Product category analysis
- Channel performance analysis

## Next Steps

1. **Generate Test Data**: Use the script to create CSV files for testing
2. **Upload to VariancePro**: Test the upload functionality in app_v2.py
3. **Verify Chat Integration**: Confirm metrics appear in chat
4. **Test Analysis**: Use for developing NL2SQL capabilities

---

**Generated by**: VariancePro Sample Data Generator  
**Compatible with**: VariancePro v2.0 and later  
**Last Updated**: July 6, 2025
