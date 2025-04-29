import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import itertools
from sklearn.linear_model import LinearRegression

# Set font to Computer Modern
plt.rcParams.update({"font.family": "serif", "mathtext.fontset": "cm"})

# Load the CSV file
file_path = 'int_data.csv'
df = pd.read_csv(file_path)

# Parse the Date column to datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Sort by Date just to ensure correct plotting
df = df.sort_values('Date')

# Filter CPUs with 20 or more data points
cpu_counts = df['CPU Name'].value_counts()
valid_cpus = cpu_counts[cpu_counts >= 20].index
df = df[df['CPU Name'].isin(valid_cpus)]

# Create Year-Month column for grouping
df['YearMonth'] = df['Date'].dt.to_period('M')

# First Plot: Score over Time with log2 scale on Y-axis
plt.figure(figsize=(12, 6))
colors = itertools.cycle(plt.cm.tab20.colors)
all_dates = []
all_scores = []
for cpu_name, group in df.groupby('CPU Name'):
    group_mean = group.groupby('YearMonth').agg({'Score': 'mean', 'MHz': 'mean'}).reset_index()
    group_mean['Date'] = group_mean['YearMonth'].dt.to_timestamp()
    plt.scatter(group_mean['Date'], group_mean['Score'], label=f"{cpu_name} ({len(group)})", color=next(colors))
    all_dates.append(group_mean['Date'])
    all_scores.append(group_mean['Score'])

# Prepare data for regression
all_dates = pd.concat(all_dates)
all_scores = pd.concat(all_scores)
all_timestamps = all_dates.map(pd.Timestamp.timestamp).values.reshape(-1, 1)
log_scores = np.log2(all_scores.values).reshape(-1, 1)

# Split data around 2005
cutoff = pd.Timestamp('2005-01-01').timestamp()
before_2005 = all_timestamps.flatten() < cutoff

# Fit and plot linear regression in log-space for data before 2005
model_before = LinearRegression()
model_before.fit(all_timestamps[before_2005].reshape(-1, 1), log_scores[before_2005])
r2_before = model_before.score(all_timestamps[before_2005].reshape(-1, 1), log_scores[before_2005])
x_range = np.linspace(all_timestamps[before_2005].min(), cutoff, 100).reshape(-1, 1)
y_pred_before = model_before.predict(x_range)
plt.plot(pd.to_datetime(x_range.flatten(), unit='s'), 2 ** y_pred_before.flatten(), color='black', linestyle='--', label=f'Log-Linear Trend before 2005 (R2={r2_before:.2f})')

plt.yscale('log', base=2)
plt.xlabel('Date')
plt.ylabel('Normalized SPECIntSpeed Score (log2 scale)')
plt.title('Normalized SPECIntSpeed Score over Time')
plt.legend(title='Results by CPU (# data points)')
plt.grid(True, which="both", ls="--", lw=0.5)
plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.gcf().autofmt_xdate()
plt.tight_layout()
plt.savefig('plot1_score_over_time.png')
plt.close()

# Second Plot: Date vs log(Score/MHz) by CPU Name
plt.figure(figsize=(12, 6))
colors = itertools.cycle(plt.cm.tab20.colors)
for cpu_name, group in df.groupby('CPU Name'):
    group_mean = group.groupby('YearMonth').agg({'Score/MHz': 'mean'}).reset_index()
    group_mean['Date'] = group_mean['YearMonth'].dt.to_timestamp()
    log_score_per_mhz = np.log(group_mean['Score/MHz'])
    plt.scatter(group_mean['Date'], log_score_per_mhz, label=f"{cpu_name} ({len(group)})", color=next(colors))

plt.xlabel('Date')
plt.ylabel('Normalized SPECIntSpeed Score/MHz (log scale)')
plt.title('Normalized SPECIntSpeed Score/MHz over Time (by CPU Name)')
plt.legend(title='Results by CPU (# data points)')
plt.grid(True, which="both", ls="--", lw=0.5)
plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.gcf().autofmt_xdate()
plt.tight_layout()
plt.savefig('plot2_score_per_mhz_cpu.png')
plt.close()

# Third Plot: Date vs log(Score/MHz) by Bench
plt.figure(figsize=(12, 6))
colors = itertools.cycle(plt.cm.tab20.colors)
for bench_name, group in df.groupby('bench'):
    group_mean = group.groupby('YearMonth').agg({'Score/MHz': 'mean'}).reset_index()
    group_mean['Date'] = group_mean['YearMonth'].dt.to_timestamp()
    log_score_per_mhz = np.log(group_mean['Score/MHz'])
    plt.scatter(group_mean['Date'], log_score_per_mhz, label=f"{bench_name} ({len(group)})", color=next(colors))

plt.xlabel('Date')
plt.ylabel('Normalized SPECIntSpeed Score/MHz (log scale)')
plt.title('Normalized SPECIntSpeed Score/MHz over Time (by Bench)')
plt.legend(title='Results by Benchmark (# data points)')
plt.grid(True, which="both", ls="--", lw=0.5)
plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.gcf().autofmt_xdate()
plt.tight_layout()
plt.savefig('plot3_score_per_mhz_bench.png')
plt.close()

# Fourth Plot: Date vs MHz by CPU Name
plt.figure(figsize=(12, 6))
colors = itertools.cycle(plt.cm.tab20.colors)
for cpu_name, group in df.groupby('CPU Name'):
    group_mean = group.groupby('YearMonth').agg({'MHz': 'mean'}).reset_index()
    group_mean['Date'] = group_mean['YearMonth'].dt.to_timestamp()
    plt.scatter(group_mean['Date'], group_mean['MHz'], label=f"{cpu_name} ({len(group)})", color=next(colors))

plt.xlabel('Date')
plt.ylabel('Clock Speed (MHz)')
plt.title('Clock Speed over Time (by CPU Name)')
plt.legend(title='Results by CPU (# data points)')
plt.grid(True, which="both", ls="--", lw=0.5)
plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.gcf().autofmt_xdate()
plt.tight_layout()
plt.savefig('plot4_mhz_over_time.png')
plt.close()

# Fifth Plot: Date vs log10(MHz) by CPU Name
plt.figure(figsize=(12, 6))
colors = itertools.cycle(plt.cm.tab20.colors)
for cpu_name, group in df.groupby('CPU Name'):
    group_mean = group.groupby('YearMonth').agg({'MHz': 'mean'}).reset_index()
    group_mean['Date'] = group_mean['YearMonth'].dt.to_timestamp()
    log10_mhz = np.log10(group_mean['MHz'])
    plt.scatter(group_mean['Date'], log10_mhz, label=f"{cpu_name} ({len(group)})", color=next(colors))

plt.xlabel('Date')
plt.ylabel('Log10 Clock Speed (MHz)')
plt.title('Log10 Clock Speed over Time (by CPU Name)')
plt.legend(title='Results by CPU (# data points)')
plt.grid(True, which="both", ls="--", lw=0.5)
plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.gcf().autofmt_xdate()
plt.tight_layout()
plt.savefig('plot5_log10_mhz_over_time.png')
plt.close()
