#!/usr/bin/env python3
"""
Generate PNG figures for Extortion analysis.
"""

import openpyxl
from openpyxl import load_workbook
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import json

# Set matplotlib to use grayscale/black and white
plt.style.use('grayscale')

def generate_discrete_count_chart(results, output_path):
    """Generate discrete distribution bar chart for event counts."""
    
    dist_info = results['distribution']
    lower_bound = dist_info['lower_bound']
    upper_bound = dist_info['upper_bound']
    num_events = dist_info['range']
    
    # Generate Monte Carlo data directly using discrete uniform distribution
    np.random.seed(42)
    values = np.random.randint(lower_bound, upper_bound + 1, size=10000).tolist()
    
    print(f'Generated {len(values)} Monte Carlo values')
    
    # Count occurrences of each value
    event_range = list(range(lower_bound, upper_bound + 1))
    counts = [values.count(v) for v in event_range]
    percentages = [c / len(values) * 100 for c in counts]
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(event_range, counts, color='gray', edgecolor='black', linewidth=1.5)
    
    ax.set_xlabel('Number of Extortion Events', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency (out of 10,000)', fontsize=12, fontweight='bold')
    ax.set_title('Monte Carlo Discrete Simulation: Extortion Event Counts', fontsize=14, fontweight='bold')
    
    # Set x-axis to show all values
    ax.set_xticks(event_range)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add percentage labels on top of bars
    for i, (bar, pct) in enumerate(zip(bars, percentages)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{pct:.1f}%',
                ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f'Saved discrete count chart to {output_path}')
    plt.close()
    
    return percentages

def generate_impact_histogram(results, output_path):
    """Generate histogram for impact distribution."""
    
    as_mean = results['american_samoa']['mean_scaled_impact']
    ca_mean = results['california']['mean_scaled_impact']
    
    # Generate normal distribution for impact
    np.random.seed(42)
    mean = (as_mean + ca_mean) / 2
    std = (ca_mean - as_mean) / 4  # Approximate std dev
    
    # Generate 10,000 samples
    samples = np.random.normal(mean, std, 10000)
    # Clip to reasonable bounds
    samples = np.clip(samples, as_mean, ca_mean)
    
    # Create histogram
    fig, ax = plt.subplots(figsize=(12, 6))
    n, bins, patches = ax.hist(samples, bins=50, color='gray', edgecolor='black', linewidth=1)
    
    ax.set_xlabel('Impact Cost ($)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax.set_title('Monte Carlo Normal Distribution: Extortion Impact', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Format x-axis as currency
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f'Saved impact histogram to {output_path}')
    plt.close()
    
    return samples

def generate_impact_percentile_chart(samples, output_path):
    """Generate percentile/exceedance curve for impact."""
    
    # Sort samples
    sorted_samples = np.sort(samples)
    
    # Calculate percentiles
    percentiles = np.arange(0, 100, 0.1)
    values = np.percentile(sorted_samples, percentiles)
    
    # Create the exceedance curve (100 - percentile)
    exceedance = 100 - percentiles
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(values, exceedance, color='black', linewidth=2)
    
    # Mark key percentiles
    p10 = np.percentile(sorted_samples, 10)
    p50 = np.percentile(sorted_samples, 50)
    p90 = np.percentile(sorted_samples, 90)
    
    ax.axvline(p10, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax.axvline(p50, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax.axvline(p90, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    
    ax.text(p10, 95, f'P10: ${p10:,.0f}', rotation=0, fontsize=9)
    ax.text(p50, 95, f'P50: ${p50:,.0f}', rotation=0, fontsize=9)
    ax.text(p90, 95, f'P90: ${p90:,.0f}', rotation=0, fontsize=9)
    
    ax.set_xlabel('Impact Cost ($)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Probability of Exceedance (%)', fontsize=12, fontweight='bold')
    ax.set_title('Exceedance Curve: Extortion Impact', fontsize=14, fontweight='bold')
    ax.grid(alpha=0.3, linestyle='--')
    
    # Format x-axis as currency
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f'Saved impact percentile chart to {output_path}')
    plt.close()
    
    # Return key percentiles for LaTeX
    return {
        'p10': p10,
        'p50': p50,
        'p90': p90,
        'ci_lower': p10,
        'ci_upper': p90
    }

def main():
    # Load results
    with open('extortion_analysis_results.json', 'r') as f:
        results = json.load(f)
    
    print('Generating PNG figures for Extortion...')
    
    # Generate discrete count chart
    percentages = generate_discrete_count_chart(
        results,
        '../../figures/discrete_extortion_count.png'
    )
    
    # Generate impact histogram
    samples = generate_impact_histogram(
        results,
        '../../figures/histogram_extortion_impact.png'
    )
    
    # Generate impact percentile chart
    percentiles = generate_impact_percentile_chart(
        samples,
        '../../figures/percent_extortion_impact.png'
    )
    
    # Update results with percentages and percentiles
    results['monte_carlo'] = {
        'discrete_percentages': percentages,
        'impact_percentiles': percentiles
    }
    
    # Save updated results
    with open('extortion_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print('\nAll figures generated successfully!')
    print(f'\nKey impact percentiles:')
    print(f'  P10 (90% probability): ${percentiles["p10"]:,.2f}')
    print(f'  P50 (50% probability): ${percentiles["p50"]:,.2f}')
    print(f'  P90 (10% probability): ${percentiles["p90"]:,.2f}')
    print(f'  80% CI: [${percentiles["ci_lower"]:,.2f}, ${percentiles["ci_upper"]:,.2f}]')

if __name__ == '__main__':
    main()
