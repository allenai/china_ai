'''
This script is the source code for a project that Field Cady
and Oren Etzioni are working on.
'''

import pandas as pd
import pys2
from matplotlib import pyplot as plt
from scipy import stats
import matplotlib


# The field we use to tell rank paper importance
CITATION_COUNT_FIELD = "estimated citation count"

# Pull down table of AI papers from Redshift, and add on columns for
# the final US/China heuristics and the cutoffs for levels of how much
# a paper is cited.
df = pys2._evaluate_redshift_query('select * from ai_papers_any_author_table where yr<2019 and yr>1980')
df["citation_count"] = df[CITATION_COUNT_FIELD].astype(int)
df['china'] = df.dotcn.astype(bool) | df.dothk.astype(bool) | df.china_name.astype(bool) | df.china_language.astype(bool) | df.china_city.astype(bool)
df['usa'] = df.dotedu.astype(bool) | df.dotedu.astype(bool)
df['top_half_cutoff'] = df.groupby('yr').citation_count.transform(lambda x: (x-x)+x.quantile(0.5))
df['top_tenth_cutoff'] = df.groupby('yr').citation_count.transform(lambda x: (x-x)+x.quantile(0.9))
df['top_twentieth_cutoff'] = df.groupby('yr').citation_count.transform(lambda x: (x-x)+x.quantile(0.95))
df['top_hundredth_cutoff'] = df.groupby('yr').citation_count.transform(lambda x: (x-x)+x.quantile(0.99))
df['top_halfpercent_cutoff'] = df.groupby('yr').citation_count.transform(lambda x: (x-x)+x.quantile(0.995))

#
# Plot all figures
#

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

plt.close()
df.groupby('yr').china.sum().plot(label='China')
df.groupby('yr').usa.sum().plot(label='US')
plt.title('All AI Papers')
plt.legend(); plt.xlabel(''); plt.ylabel('# Papers')
plt.minorticks_on()
plt.savefig('all_papers.jpg')

plt.close()
df[df.citation_count>df.top_tenth_cutoff].groupby('yr').china.sum().plot(label='China')
df[df.citation_count>df.top_tenth_cutoff].groupby('yr').usa.sum().plot(label='US')
plt.title('Top Half AI Papers')
plt.legend(); plt.xlabel(''); plt.ylabel('# Papers')
plt.minorticks_on()
plt.savefig('top_half_papers.jpg')

plt.close()
(100*df[df.citation_count>-1].groupby('yr').china.mean()).plot(label='China')
(100*df[df.citation_count>-1].groupby('yr').usa.mean()).plot(label='US')
plt.title('All AI Papers')
plt.legend(); plt.xlabel(''); plt.ylabel('% Papers')
plt.minorticks_on()
plt.savefig('top_100_percent.jpg')

plt.close()
(100*df[df.citation_count>df.top_tenth_cutoff].groupby('yr').china.mean()).plot(label='China')
(100*df[df.citation_count>df.top_tenth_cutoff].groupby('yr').usa.mean()).plot(label='US')
plt.title('Top Half of AI Papers')
plt.legend(); plt.xlabel(''); plt.ylabel('% Papers')
plt.minorticks_on()
plt.savefig('top_half_market_share.jpg')


plt.close()
(100*df[df.citation_count>df.top_tenth_cutoff].groupby('yr').china.mean()).plot(label='China')
(100*df[df.citation_count>df.top_tenth_cutoff].groupby('yr').usa.mean()).plot(label='US')
plt.title('Top 10% AI Papers (for each year, by # citations)')
plt.legend(); plt.xlabel(''); plt.ylabel('% Papers')
plt.minorticks_on()
plt.savefig('top_10_percent.jpg')


plt.close()
(100*df[df.citation_count>df.top_twentieth_cutoff].groupby('yr').china.mean()).plot(label='China')
(100*df[df.citation_count>df.top_twentieth_cutoff].groupby('yr').usa.mean()).plot(label='US')
plt.title('Top 5% AI Papers (for each year, by # citations)')
plt.legend(); plt.xlabel(''); plt.ylabel('% Papers')
plt.minorticks_on()
plt.savefig('top_5_percent.jpg')


plt.close()
(100*df[df.citation_count>df.top_hundredth_cutoff].groupby('yr').china.mean()).plot(label='China')
(100*df[df.citation_count>df.top_hundredth_cutoff].groupby('yr').usa.mean()).plot(label='US')
plt.title('Top 1% AI Papers (for each year, by # citations)')
plt.legend(); plt.xlabel(''); plt.ylabel('% Papers')
plt.minorticks_on()
plt.savefig('top_1_percent.jpg')

plt.close()
(100*df[df.citation_count>df.top_halfpercent_cutoff].groupby('yr').china.mean()).plot(label='China')
(100*df[df.citation_count>df.top_halfpercent_cutoff].groupby('yr').usa.mean()).plot(label='US')
plt.title('Top 0.5% AI Papers (for each year, by # citations)')
plt.legend(); plt.xlabel(''); plt.ylabel('% Papers')
plt.minorticks_on()
plt.savefig('top_halfpercent.jpg')


####

# Predict convergence of top 10% share and plot line
china_ts = 100*df[df.citation_count>df.top_tenth_cutoff].groupby('yr').china.mean()
usa_ts = 100*df[df.citation_count>df.top_tenth_cutoff].groupby('yr').usa.mean()
china_slope, china_intercept, r_value, p_value, std_err = stats.linregress([2015, 2016, 2017, 2018],china_ts[-4:])
usa_slope, usa_intercept, r_value, p_value, std_err = stats.linregress([2015, 2016, 2017, 2018],usa_ts[-4:])
intercept_year = (china_intercept-usa_intercept) / (usa_slope-china_slope)

plt.close()
plt.ion()
china_ts.plot(label='China', linewidth=4, alpha=0.5)
usa_ts.plot(label='US', linewidth=4, alpha=0.5)
fit_years = pd.Series(range(2014, 2023), index=range(2014, 2023))
china_fit = fit_years*china_slope+china_intercept
usa_fit = fit_years*usa_slope+usa_intercept
china_fit.plot(style='--', label='China Fit')
usa_fit.plot(style='--', label='US Fit')
plt.legend(); plt.xlabel(''); plt.ylabel('% of Top Papers')
plt.title('Share of Papers in the Top 10%')
plt.minorticks_on()
plt.savefig('top_tenth_convergence.jpg')

# Predict convergence of top 5% share and plot line
china_ts = 100*df[df.citation_count>df.top_twentieth_cutoff].groupby('yr').china.mean()
usa_ts = 100*df[df.citation_count>df.top_twentieth_cutoff].groupby('yr').usa.mean()
china_slope, china_intercept, r_value, p_value, std_err = stats.linregress([2015, 2016, 2017, 2018],china_ts[-4:])
usa_slope, usa_intercept, r_value, p_value, std_err = stats.linregress([2015, 2016, 2017, 2018],usa_ts[-4:])
intercept_year = (china_intercept-usa_intercept) / (usa_slope-china_slope)

plt.close()
plt.ion()
china_ts.plot(label='China', linewidth=4, alpha=0.5)
usa_ts.plot(label='US', linewidth=4, alpha=0.5)
fit_years = pd.Series(range(2014, 2026), index=range(2014, 2026))
china_fit = fit_years*china_slope+china_intercept
usa_fit = fit_years*usa_slope+usa_intercept
china_fit.plot(style='--', label='China Fit')
usa_fit.plot(style='--', label='US Fit')
plt.legend(); plt.xlabel(''); plt.ylabel('% of Top Papers')
plt.title('Share of Papers in the Top 5%')
plt.minorticks_on()
plt.savefig('top_twentieth_convergence.jpg')



# Predict convergence of top 1% share and plot line
china_ts = 100*df[df.citation_count>df.top_hundredth_cutoff].groupby('yr').china.mean()
usa_ts = 100*df[df.citation_count>df.top_hundredth_cutoff].groupby('yr').usa.mean()
china_slope, china_intercept, r_value, p_value, std_err = stats.linregress([2015, 2016, 2017, 2018],china_ts[-4:])
usa_slope, usa_intercept, r_value, p_value, std_err = stats.linregress([2015, 2016, 2017, 2018],usa_ts[-4:])
intercept_year = (china_intercept-usa_intercept) / (usa_slope-china_slope)

plt.close()
plt.ion()
china_ts.plot(label='China', linewidth=4, alpha=0.5)
usa_ts.plot(label='US', linewidth=4, alpha=0.5)
fit_years = pd.Series(range(2014, 2025), index=range(2014, 2025))
china_fit = fit_years*china_slope+china_intercept
usa_fit = fit_years*usa_slope+usa_intercept
china_fit.plot(style='--', label='China Fit')
usa_fit.plot(style='--', label='US Fit')
plt.legend(); plt.xlabel(''); plt.ylabel('% of Top Papers')
plt.title('Share of Papers in the Top 1%')
plt.minorticks_on()
plt.savefig('top_hundredth_convergence.jpg')

# Predict convergence of top 1% share and plot line
china_ts = 100*df[df.citation_count>df.top_halfpercent_cutoff].groupby('yr').china.mean()
usa_ts = 100*df[df.citation_count>df.top_halfpercent_cutoff].groupby('yr').usa.mean()
china_slope, china_intercept, r_value, p_value, std_err = stats.linregress([2015, 2016, 2017, 2018],china_ts[-4:])
usa_slope, usa_intercept, r_value, p_value, std_err = stats.linregress([2015, 2016, 2017, 2018],usa_ts[-4:])
intercept_year = (china_intercept-usa_intercept) / (usa_slope-china_slope)

plt.close()
plt.ion()
china_ts.plot(label='China', linewidth=4, alpha=0.5)
usa_ts.plot(label='US', linewidth=4, alpha=0.5)
fit_years = pd.Series(range(2014, 2024), index=range(2014, 2024))
china_fit = fit_years*china_slope+china_intercept
usa_fit = fit_years*usa_slope+usa_intercept
china_fit.plot(style='--', label='China Fit')
usa_fit.plot(style='--', label='US Fit')
plt.legend(); plt.xlabel(''); plt.ylabel('% of Top Papers')
plt.title('Share of Papers in the Top 0.5%')
plt.minorticks_on()
plt.savefig('top_halfpercent_convergence.jpg')



#
#
#


adf = pys2._evaluate_redshift_query('''
    select "paper id" as pid, "author id" as authorid, "estimated citation count" as ct, displayname
    from paper_author_institution_table''')
