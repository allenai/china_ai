'''
This script is the source code for a project that
Field Cady and Oren Etzioni are working on.
'''

import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
from scipy import stats
import pys2  # library internal to Allen Institute

# The field we use to tell rank paper importance
CITATION_COUNT_FIELD = "estimated citation count"

# Pull down table of AI papers from Redshift, and add on columns for
# the final US/China heuristics and the cutoffs for levels of how much
# a paper is cited.
df = pys2._evaluate_redshift_query('select * from ai_papers_any_author_table where yr<2019 and yr>1980')
df["citation_count"] = df[CITATION_COUNT_FIELD].astype(int)
df['china'] = df.dotcn.astype(bool) | df.dothk.astype(bool) \
    | df.china_name.astype(bool) | df.china_language.astype(bool) \
    | df.china_city.astype(bool)
df['us'] = df.dotedu.astype(bool) | df.dotedu.astype(bool)
df['top_half_cutoff'] = df.groupby('yr').citation_count.transform(lambda x: (x-x)+x.quantile(0.5))
df['top_tenth_cutoff'] = df.groupby('yr').citation_count.transform(lambda x: (x-x)+x.quantile(0.9))
df['top_twentieth_cutoff'] = df.groupby('yr').citation_count.transform(lambda x: (x-x)+x.quantile(0.95))
df['top_hundredth_cutoff'] = df.groupby('yr').citation_count.transform(lambda x: (x-x)+x.quantile(0.99))
df['top_halfpercent_cutoff'] = df.groupby('yr').citation_count.transform(lambda x: (x-x)+x.quantile(0.995))

#
# Plot all figures
#

# Number of China papers vs their market share in the bottom 50% and top 10%
plt.close()
sums = df.groupby('yr').china.sum()
ax1 = sums.plot(label="# Papers", color='b')
ax1.set_xlabel(''); ax1.set_ylabel('# Papers')
ax2 = ax1.twinx()
df[df.citation_count>df.top_tenth_cutoff].groupby('yr').china.mean().plot(
    label='Top 10%', ax=ax2, color='g', style='--')
df[df.citation_count<=df.top_half_cutoff].groupby('yr').china.mean().plot(
    label='Bottom Half', ax=ax2, color='r', style='--')
ax2.set_xlabel(''); ax2.set_ylabel('Market Shares')
plt.title("Chinas Drop was in Bad Papers")
plt.minorticks_on()
plt.legend()
plt.savefig('chinas_drop_vs_market_share.jpg')

# Raw number of papers
plt.close()
df.groupby('yr').china.sum().plot(label='China')
df.groupby('yr').us.sum().plot(label='US')
plt.title('All AI Papers')
plt.legend(); plt.xlabel(''); plt.ylabel('# Papers')
plt.minorticks_on()
plt.savefig('all_papers.jpg')

# Market share for different levels of citation
cutoffcol_title_pairs = [
    ('top_half_cutoff', 'Top 50% of AI Papers'),
    ('top_twentieth_cutoff', 'Share of Papers in the Top 10% '),
    ('top_halfpercent_cutoff', 'Share of Papers in the Top 1%')
]
for cutoffcol, title in cutoffcol_title_pairs:
    print(title)
    # Create time series for each country
    china_ts = df[df.citation_count>df[cutoffcol]].groupby('yr').china.mean()
    us_ts = df[df.citation_count>df[cutoffcol]].groupby('yr').us.mean()
    # fit lines to last 4 years
    china_slope, china_intercept, r_value, p_value, std_err = stats.linregress([2015, 2016, 2017, 2018],china_ts[-4:])
    us_slope, us_intercept, r_value, p_value, std_err = stats.linregress([2015, 2016, 2017, 2018],us_ts[-4:])
    intercept_year = (china_intercept-us_intercept) / (us_slope-china_slope)
    # Compute interpolations to plot
    fit_years = pd.Series(range(2014, 2026), index=range(2014, 2026))
    china_fit = fit_years*china_slope+china_intercept
    us_fit = fit_years*us_slope+us_intercept
    # Save a CSV
    pd.DataFrame({'China': china_ts, 'US':us_ts,
        'China Fit': china_fit, 'US Fit': us_fit}).to_csv(title+'.csv')
    # Plot
    plt.close()
    china_ts.plot(label='China')
    us_ts.plot(label='US')
    china_fit.plot(style='--', label='China Fit')
    us_fit.plot(style='--', label='US Fit')
    plt.title(title + ' : Intercept in ' + str(int(intercept_year)))
    plt.legend(); plt.xlabel(''); plt.ylabel('Market Share')
    plt.minorticks_on()
    plt.savefig(title + '.jpg')
