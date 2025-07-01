"""
Demo of the ContributionAnalyzer implementation
"""

import pandas as pd
import numpy as np
from app import ContributionAnalyzer

def main():
    print('=== Contribution Analysis Demo ===')
    print()

    # Create sample data following the Medium article approach
    np.random.seed(42)
    data = pd.DataFrame(np.random.rand(10) * 3500 + 3000, 
                        index=['Product_A', 'Product_B', 'Product_C', 'Product_D', 'Product_E', 
                               'Product_F', 'Product_G', 'Product_H', 'Product_I', 'Product_J'], 
                        columns=['sales'])

    # Round the sales data to two decimal places
    data['sales'] = data['sales'].round(2)
    data = data.reset_index()
    data.columns = ['Product', 'Sales']

    print('Generated Sales Data:')
    print(data)
    print()

    # Initialize analyzer
    analyzer = ContributionAnalyzer()

    # Perform contribution analysis using the pandas approach
    result_df, summary, fig = analyzer.perform_contribution_analysis_pandas(
        data, 'Product', 'Sales'
    )

    print('=== Contribution Analysis Results ===')
    print()
    print('Sorted data with cumulative contributions:')
    print(result_df[['Product', 'Sales', 'individual_contribution', 'contribution', 'is_key_contributor']].round(3))
    print()

    print('=== Summary Statistics ===')
    print(f'Total products: {summary["total_categories"]}')
    print(f'Key contributors: {summary["key_contributors_count"]} ({summary["key_contributors_percentage"]:.1f}%)')
    print(f'Value share of key contributors: {summary["key_contributors_value_share"]:.1f}%')
    print(f'Top contributor: {summary["top_contributor"]["name"]} ({summary["top_contributor"]["percentage"]:.1f}%)')
    print()

    print('=== Key Insights ===')
    for insight in summary['insights']:
        print(f'- {insight}')
    print()

    # Find the key contributors (those contributing to 80% threshold)
    key_contributors = result_df[result_df['is_key_contributor']]
    print('=== Core Products (Key Contributors) ===')
    print(key_contributors[['Product', 'Sales', 'individual_contribution']].round(3))
    print()

    print('✅ Analysis completed successfully!')
    print()
    print('This follows the 80/20 Pareto principle approach from the Medium article.')
    print('The implementation includes:')
    print('- Sorting products by sales in descending order')
    print('- Calculating cumulative percentages using pandas cumsum()')
    print('- Identifying key contributors at the 80% threshold')
    print('- Generating comprehensive Pareto charts with Plotly')
    print('- Time-based analysis capabilities')

if __name__ == '__main__':
    main()
