#!/usr/bin/env python3
"""
Generate LaTeX content for Extortion section based on extracted data.
"""

import json
import sys

def format_number_with_commas(num):
    """Format number with thousands separators for LaTeX."""
    if num == 0:
        return '0'
    if isinstance(num, int) or (isinstance(num, float) and num == int(num)):
        return f'{int(num):,}'.replace(',', '{,}')
    else:
        # For floats, format with 2 decimal places
        return f'{num:,.2f}'.replace(',', '{,}')

def format_dollar_amount(amount):
    """Format dollar amount for LaTeX."""
    if amount == 0:
        return '\\$0'
    if isinstance(amount, int) or (isinstance(amount, float) and amount == int(amount)):
        return '\\$' + format_number_with_commas(amount)
    else:
        return '\\$' + format_number_with_commas(amount)

def generate_latex_section(results):
    """Generate the full LaTeX section for Extortion."""
    
    # Extract data
    as_data = results['american_samoa']
    ca_data = results['california']
    dist_info = results['distribution']
    years = results['years']
    
    # Select three years: 2016, 2017, 2022
    selected_indices = [0, 1, 6]  # 2016, 2017, 2022
    selected_years = [years[i] for i in selected_indices]
    
    # American Samoa selected data
    as_selected_counts = [as_data['raw_counts'][i] for i in selected_indices]
    as_selected_impacts = [as_data['raw_impacts'][i] for i in selected_indices]
    as_selected_scaled_counts = [as_data['scaled_counts'][i] for i in selected_indices]
    as_selected_scaled_impacts = [as_data['scaled_impacts'][i] for i in selected_indices]
    
    # California selected data
    ca_selected_counts = [ca_data['raw_counts'][i] for i in selected_indices]
    ca_selected_impacts = [ca_data['raw_impacts'][i] for i in selected_indices]
    ca_selected_scaled_counts = [ca_data['scaled_counts'][i] for i in selected_indices]
    ca_selected_scaled_impacts = [ca_data['scaled_impacts'][i] for i in selected_indices]
    
    latex = f"""%%%%%%%%%%%%%%%%%%%%  EXTORTION %%%%%%%%%%%%%%%%%%%%%%%%
\\newpage
\\subsection{{Extortion}}
\\subsubsection{{Lower Bound Computation}}
\\[
\\begin{{bmatrix}}
\\mathbf{{x}}_{{\\text{{American Samoa}}}}^{{(\\text{{count}})}}\\\\
\\mathbf{{x}}_{{\\text{{American Samoa}}}}^{{(\\text{{dollars}})}}
\\end{{bmatrix}}
=
\\begin{{bmatrix}}
{as_selected_counts[0]} & {as_selected_counts[1]} & \\cdots & {as_selected_counts[2]}\\\\
{format_dollar_amount(as_selected_impacts[0])} & {format_dollar_amount(as_selected_impacts[1])} & \\cdots & {format_dollar_amount(as_selected_impacts[2])}
\\end{{bmatrix}}.
\\]
\\[
\\begin{{bmatrix}}
\\mathbf{{x}}_{{\\text{{American Samoa}}}}^{{(\\text{{count scaled to sample population}})}}\\\\
\\mathbf{{x}}_{{\\text{{American Samoa}}}}^{{(\\text{{dollars scaled to sample population}})}}
\\end{{bmatrix}}
=
\\begin{{bmatrix}}
{format_number_with_commas(as_selected_scaled_counts[0])} & \\cdots & {format_number_with_commas(as_selected_scaled_counts[2])}\\\\
{format_dollar_amount(as_selected_scaled_impacts[0])} & \\cdots & {format_dollar_amount(as_selected_scaled_impacts[2])}
\\end{{bmatrix}}.
\\]
  \\[
\\bar{{X}}_{{\\text{{American Samoa}}}}^{{(m)}}
= \\frac{{1}}{{N}}\\sum_{{i=1}}^{{N}} X_{{\\text{{American Samoa}},i}}^{{(m)}},
\\]
\\\\
\\[
\\qquad
m \\in \\{{\\text{{scaled count}},\\text{{scaled dollars}}\\}}
\\]
\\[
\\begin{{bmatrix}}
\\bar{{X}}_{{\\text{{American Samoa}}}}^{{(\\text{{scaled count}})}}\\\\
\\bar{{X}}_{{\\text{{American Samoa}}}}^{{(\\text{{scaled dollars}})}}
\\end{{bmatrix}}
=
\\begin{{bmatrix}}
{format_number_with_commas(as_data['mean_scaled_count'])}\\\\
{format_dollar_amount(as_data['mean_scaled_impact'])}
\\end{{bmatrix}}.
\\]
\\subsubsection{{Upper Bound Computation}}
\\[
\\begin{{bmatrix}}
\\mathbf{{x}}_{{\\text{{California}}}}^{{(\\text{{count}})}}\\\\
\\mathbf{{x}}_{{\\text{{California}}}}^{{(\\text{{dollars}})}}
\\end{{bmatrix}}
=
\\begin{{bmatrix}}
{format_number_with_commas(ca_selected_counts[0])} & {format_number_with_commas(ca_selected_counts[1])} & \\cdots & {format_number_with_commas(ca_selected_counts[2])}\\\\
{format_dollar_amount(ca_selected_impacts[0])} & {format_dollar_amount(ca_selected_impacts[1])} & \\cdots & {format_dollar_amount(ca_selected_impacts[2])}
\\end{{bmatrix}}.
\\]
\\[
\\begin{{bmatrix}}
\\mathbf{{x}}_{{\\text{{California}}}}^{{(\\text{{count scaled to sample population}})}}\\\\
\\mathbf{{x}}_{{\\text{{California}}}}^{{(\\text{{dollars scaled to sample population}})}}
\\end{{bmatrix}}
=
\\begin{{bmatrix}}
{format_number_with_commas(ca_selected_scaled_counts[0])} & {format_number_with_commas(ca_selected_scaled_counts[1])} & \\cdots & {format_number_with_commas(ca_selected_scaled_counts[2])}\\\\
{format_dollar_amount(ca_selected_scaled_impacts[0])} & {format_dollar_amount(ca_selected_scaled_impacts[1])} & \\cdots & {format_dollar_amount(ca_selected_scaled_impacts[2])}
\\end{{bmatrix}}.
\\]
\\[
\\bar{{X}}_{{\\text{{California}}}}^{{(m)}}
= \\frac{{1}}{{N}}\\sum_{{i=1}}^{{N}} X_{{\\text{{California}},i}}^{{(m)}},
\\]
\\\\
\\[
\\qquad
m \\in \\{{\\text{{scaled count}},\\text{{scaled dollars}}\\}}
\\]
\\[
\\begin{{bmatrix}}
\\bar{{X}}_{{\\text{{California}}}}^{{(\\text{{scaled count}})}}\\\\
\\bar{{X}}_{{\\text{{California}}}}^{{(\\text{{scaled dollars}})}}
\\end{{bmatrix}}
=
\\begin{{bmatrix}}
{format_number_with_commas(ca_data['mean_scaled_count'])}\\\\
{format_dollar_amount(ca_data['mean_scaled_impact'])}
\\end{{bmatrix}}.
\\]
\\subsubsection{{Monte Carlo Simulations for Likelihood and Impact}}
\\begin{{figure}}[H]
  \\centering
  \\rotatebox{{0}}{{\\scalebox{{1}}{{\\includegraphics[scale=0.25]{{figures/discrete_extortion_count.png}}}}}}
  \\caption{{We ran a\\index{{Monte Carlo simulation}} Monte Carlo simulation of 10,000 iterations with a discrete distribution to spread random instances between upper and lower bounds taken from the means of seven year samples. We bounded between {dist_info['lower_bound']} and {dist_info['upper_bound']} possible \\index{{extortion}}extortion events over a year.\\protect\\endnote{{\\index{{sample}} Sample size was set equivalent to the City of\\index{{Chattanooga}} Chattanooga to determine the per capita rates for each year over data from \\index{{American Samoa}} American Samoa and\\index{{California}} California.  The means of those rates were used to set upper and lower bounds with \\index{{American Samoa}} American Samoa and\\index{{California}} California representing low and high \\index{{cybercrime}} cybercrime counts respectively.}}
  \\protect\\endnote{{Monte Carlo Modeling Toolkit authored by Derek E. Brink, CISSP, \\url{{www.linkedin.com/in/derekbrink}}. March 2023.}}
  }}
  \\label{{fig:screenshot-montecarlo-extortion-count-discrete}}
\\end{{figure}}
When we computed the upper and lower bounds, we recognized that a normal distribution would not fit well for forecasting likelihood.  We took the mean of the sample from American Samoa for the lower bound ({format_number_with_commas(as_data['mean_scaled_count'])}, rounded to {dist_info['lower_bound']}); we took the mean from the sample from California for the upper bound ({format_number_with_commas(ca_data['mean_scaled_count'])}, rounded to {dist_info['upper_bound']}); we had a separation of {dist_info['upper_bound'] - dist_info['lower_bound']} units.  Therefore, we switched to a discrete model with all {dist_info['range']} options sharing an equal likelihood.
\\begin{{table}}[H]
  \\centering
  \\caption{{Monte Carlo Discrete Simulation Values for Extortion}}
  \\label{{tab:discrete_extortion_montecarlo}}
  \\begin{{center}}
"""
    
    # Generate the event tables
    # We need to create tables similar to the phishing example
    # For 21 events (6-26), we'll create multiple tables with 6 columns each
    events = list(range(dist_info['lower_bound'], dist_info['upper_bound'] + 1))
    
    # Placeholder percentages (will be filled from Monte Carlo simulation)
    # For now, use equal probability
    equal_prob = 100.0 / len(events)
    
    # Split into groups of 5 for table layout
    event_groups = [events[i:i+5] for i in range(0, len(events), 5)]
    
    for group in event_groups:
        latex += "  \\begin{tabular}{@{}>{\centering\\arraybackslash}\n"
        latex += "  p{0.20\\linewidth} >{\centering\\arraybackslash}\n"
        for _ in range(len(group)):
            latex += "  p{0.10\\linewidth}>{\\centering\\arraybackslash}\n"
        latex = latex.rstrip(">{\centering\\arraybackslash}\n")
        latex += "}\n"
        
        latex += "    \\toprule\n"
        latex += "Events\n"
        for event in group:
            latex += f"    &{event}\n"
        latex = latex.rstrip("\n")
        latex += "\\\\\n"
        
        latex += "    \\midrule\n"
        latex += "Likelihood\n"
        for _ in group:
            latex += f"    &{equal_prob:.1f}\\%\n"
        latex = latex.rstrip("\n")
        latex += "\\\\\n"
        
        latex += "    \\bottomrule \\end{tabular}\n"
    
    latex += f"""    \\end{{center}}
  \\raggedright{{A\\index{{Monte Carlo simulation}} Monte Carlo simulation was run using a discrete distribution.  We bounded the simulation between {dist_info['lower_bound']} and {dist_info['upper_bound']} events.  We assigned an approximately {equal_prob:.1f}\\% likelihood to each bin.  The resulting distribution showed the effect of randomness on each possible outcome.}}
\\end{{table}}

\\begin{{figure}}[H]
  \\centering
  \\rotatebox{{0}}{{\\scalebox{{1}}{{\\includegraphics[width=\\linewidth]{{figures/histogram_extortion_impact.png}}}}}}
  \\caption{{We ran a\\index{{Monte Carlo simulation}} Monte Carlo simulation of 10,000 iterations with a normal distribution to spread random instances between bounds taken from means of seven year samples. We set a lower bound that the events would cost at {format_dollar_amount(as_data['mean_scaled_impact'])}.  We set an upper bound that the events would cost {format_dollar_amount(ca_data['mean_scaled_impact'])}.  \\protect\\endnote{{\\index{{sample}} Sample size was set equivalent to the City of\\index{{Chattanooga}} Chattanooga to determine the per capita rates for each year over data from \\index{{American Samoa}} American Samoa and\\index{{California}} California.  The means of those rates were used to set upper and lower bounds with \\index{{American Samoa}} American Samoa and\\index{{California}} California representing low and high \\index{{extortion}} extortion impact values respectively.}}
  \\protect\\endnote{{Monte Carlo Modeling Toolkit authored by Derek E. Brink, CISSP, \\url{{www.linkedin.com/in/derekbrink}}. March 2023.}}
  }}
  \\label{{fig:screenshot-montecarlo-extortion-impact-histo}}
\\end{{figure}}
\\begin{{figure}}[H]
  \\centering
  \\rotatebox{{0}}{{\\scalebox{{1}}{{\\includegraphics[width=\\linewidth]{{figures/percent_extortion_impact.png}}}}}}
  \\[
\\mathrm{{CI}}_{{80\\%}}(\\theta) = [\\${{P10}}, \\${{P90}}]
\\]
  \\caption{{A\\index{{Monte Carlo simulation}} Monte Carlo simulation with a normal distribution suggests that there is a 90\\% probability that\\index{{extortion}} extortion events will cost \\${{P10}} or more in a year.  There is a 50\\% likelihood that they will cost \\${{P50}} or more in a year.  There is a 10\\% chance that they will cost \\${{P90}} or more in a year. \\protect\\endnote{{\\index{{sample}} sample size was set equivalent to the City of\\index{{Chattanooga}} Chattanooga to determine the per capita rates for each year over data from \\index{{American Samoa}} American Samoa and\\index{{California}} California.  The means of those rates were used to set upper and lower bounds with \\index{{American Samoa}} American Samoa and\\index{{California}} California representing low and high \\index{{extortion}} extortion impact values respectively.}}
  \\protect\\endnote{{Monte Carlo Modeling Toolkit authored by Derek E. Brink, CISSP, \\url{{www.linkedin.com/in/derekbrink}}. March 2023.}}
  }}
  \\label{{fig:screenshot-montecarlo-extortion-impact-percent}}
\\end{{figure}}
"""
    
    return latex

def main():
    # Load results
    with open('extortion_analysis_results.json', 'r') as f:
        results = json.load(f)
    
    # Generate LaTeX
    latex_content = generate_latex_section(results)
    
    # Save to file
    with open('../../excerpts/extortion_latex_output.txt', 'w') as f:
        f.write(latex_content)
    
    print('LaTeX content generated and saved to excerpts/extortion_latex_output.txt')
    print('\nPreview:')
    print(latex_content[:1000])
    print('\n... (truncated)')

if __name__ == '__main__':
    main()
