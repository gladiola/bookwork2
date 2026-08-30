#!/usr/bin/env python3
"""
Regenerate cybercrime analysis plots in black and white with larger text and taller aspect ratio.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# Define category order (same as in R script)
category_levels = [
    "Data Breach",
    "Personal Data Breach",
    "Malware",
    "Phishing",
    "Ransomware",
    "Crimes Against Children",
    "Extortion",
    "Threats/Stalking/Harassment/Terrorism",
    "IPR/Counterfeit",
    "Identity Theft",
    "BEC"
]

# Reverse for plotting (bottom to top)
category_levels_reversed = list(reversed(category_levels))

def make_emm_plot(csv_file, output_file):
    """Create estimated marginal means plot in black and white."""
    # Read data
    df = pd.read_csv(csv_file)
    
    # Convert Category to categorical with proper order
    df['Category'] = pd.Categorical(df['Category'], categories=category_levels_reversed, ordered=True)
    
    # Sort by category
    df = df.sort_values('Category')
    
    # Define shapes and styles for each state
    state_markers = {'AS': 'o', 'TN': 's', 'CA': '^'}
    state_linestyles = {'AS': '-', 'TN': '--', 'CA': ':'}
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 12))
    
    # Add vertical line at x=0
    ax.axvline(x=0, linewidth=0.5, color='gray', alpha=0.7)
    
    # Define offsets for dodging
    offsets = {'AS': -0.25, 'TN': 0, 'CA': 0.25}
    
    # Plot each state
    for state in ['AS', 'TN', 'CA']:
        state_data = df[df['State'] == state].copy()
        
        # Get y positions with offset
        y_positions = range(len(state_data))
        y_positions_offset = [y + offsets[state] for y in y_positions]
        
        # Plot error bars
        ax.errorbar(
            state_data['emmean'], y_positions_offset,
            xerr=[state_data['emmean'] - state_data['lower.CL'], 
                  state_data['upper.CL'] - state_data['emmean']],
            fmt=state_markers[state],
            markersize=10,
            markerfacecolor='white',
            markeredgewidth=2,
            markeredgecolor='black',
            linestyle='none',
            elinewidth=2,
            capsize=4,
            capthick=2,
            color='black',
            label=state
        )
    
    # Set labels and title
    ax.set_yticks(range(len(category_levels_reversed)))
    ax.set_yticklabels(category_levels_reversed)
    ax.set_xlabel('Adjusted per-capita rate', fontsize=16, fontweight='bold')
    ax.set_title('Estimated marginal means with 95% confidence intervals', 
                 fontsize=18, fontweight='bold', pad=20)
    
    # Customize legend
    legend_elements = [
        mpatches.Patch(facecolor='none', edgecolor='black', label='AS', 
                      linestyle='-', linewidth=2),
        mpatches.Patch(facecolor='none', edgecolor='black', label='TN', 
                      linestyle='--', linewidth=2),
        mpatches.Patch(facecolor='none', edgecolor='black', label='CA', 
                      linestyle=':', linewidth=2)
    ]
    
    # Create custom legend with markers
    handles = []
    for state in ['AS', 'TN', 'CA']:
        handle = plt.Line2D([0], [0], marker=state_markers[state], 
                           color='black', linewidth=0,
                           markersize=10, markerfacecolor='white',
                           markeredgewidth=2, label=state)
        handles.append(handle)
    
    ax.legend(handles=handles, loc='upper right', fontsize=15, 
             title='State', title_fontsize=16, frameon=True)
    
    # Grid
    ax.grid(True, axis='x', alpha=0.3, linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Tick sizes
    ax.tick_params(axis='both', which='major', labelsize=14)
    
    # Tight layout
    plt.tight_layout()
    
    # Save
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()

def make_contrast_plot(csv_file, output_file):
    """Create planned contrasts plot in black and white."""
    # Read data
    df = pd.read_csv(csv_file)
    
    # Convert Category to categorical with proper order
    df['Category'] = pd.Categorical(df['Category'], categories=category_levels_reversed, ordered=True)
    
    # Sort by category
    df = df.sort_values('Category')
    
    # Define shapes and styles for each contrast
    contrast_markers = {'TN vs AS': 's', 'TN vs CA': '^'}
    contrast_linestyles = {'TN vs AS': '--', 'TN vs CA': ':'}
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 12))
    
    # Add vertical line at x=0
    ax.axvline(x=0, linewidth=0.5, color='gray', alpha=0.7)
    
    # Define offsets for dodging
    offsets = {'TN vs AS': -0.15, 'TN vs CA': 0.15}
    
    # Plot each contrast
    for contrast in ['TN vs AS', 'TN vs CA']:
        contrast_data = df[df['contrast'] == contrast].copy()
        
        # Get y positions with offset
        y_positions = range(len(contrast_data))
        y_positions_offset = [y + offsets[contrast] for y in y_positions]
        
        # Plot error bars
        ax.errorbar(
            contrast_data['estimate'], y_positions_offset,
            xerr=[contrast_data['estimate'] - contrast_data['lower.CL'], 
                  contrast_data['upper.CL'] - contrast_data['estimate']],
            fmt=contrast_markers[contrast],
            markersize=10,
            markerfacecolor='white',
            markeredgewidth=2,
            markeredgecolor='black',
            linestyle='none',
            elinewidth=2,
            capsize=4,
            capthick=2,
            color='black',
            label=contrast
        )
    
    # Set labels and title
    ax.set_yticks(range(len(category_levels_reversed)))
    ax.set_yticklabels(category_levels_reversed)
    ax.set_xlabel('Contrast estimate', fontsize=16, fontweight='bold')
    ax.set_title('Planned contrasts with 95% confidence intervals', 
                 fontsize=18, fontweight='bold', pad=20)
    
    # Create custom legend with markers
    handles = []
    for contrast in ['TN vs AS', 'TN vs CA']:
        handle = plt.Line2D([0], [0], marker=contrast_markers[contrast], 
                           color='black', linewidth=0,
                           markersize=10, markerfacecolor='white',
                           markeredgewidth=2, label=contrast)
        handles.append(handle)
    
    ax.legend(handles=handles, loc='upper right', fontsize=15, 
             title='Contrast', title_fontsize=16, frameon=True)
    
    # Grid
    ax.grid(True, axis='x', alpha=0.3, linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Tick sizes
    ax.tick_params(axis='both', which='major', labelsize=14)
    
    # Tight layout
    plt.tight_layout()
    
    # Save
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()

if __name__ == "__main__":
    # Get script directory
    script_dir = Path(__file__).parent
    
    # Input CSV files
    emm_csv = script_dir / "cybercrime_emmeans.csv"
    contrast_csv = script_dir / "cybercrime_planned_contrasts.csv"
    
    # Output PNG files
    emm_png = script_dir / "cybercrime_emmeans_ci.png"
    contrast_png = script_dir / "cybercrime_contrasts_ci.png"
    
    # Generate plots
    print("Generating plots...")
    make_emm_plot(emm_csv, emm_png)
    make_contrast_plot(contrast_csv, contrast_png)
    print("Done!")
