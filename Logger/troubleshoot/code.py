import pandas as pd
import numpy as np

def duration_to_minutes(duration):
    h, m, s = map(int, duration.split(':'))
    return h * 60 + m + s / 60

def read_output_file(filename):
    df = pd.read_excel(filename)
    df['task'] = df['box_name'] + '_' + df['line']
    return df[['task', 'to']]

def parse_line(line, completed_tasks_df):
    try:
        box_line, area = line.strip().split(',')
        box, line = box_line.rsplit('_', 1)
        task = f'{box}_{line}'
        completion_date = completed_tasks_df.loc[completed_tasks_df['task'] == task, 'to']
        return box, line, area, 'y' if task in completed_tasks_df['task'].values else '', completion_date.iloc[0] if len(completion_date) > 0 else None
    except ValueError:
        return None, None, None, None, None

def process_file(filename, completed_tasks_df):
    with open(filename, 'r') as file:
        lines = file.readlines()
    parsed_lines = [parse_line(line, completed_tasks_df) for line in lines if parse_line(line, completed_tasks_df) != (None, None, None, None, None)]
    df = pd.DataFrame(parsed_lines, columns=['box', 'line', 'area', 'completed', 'completion_date'])
    return df

# Modify the below section of the code
completed_tasks_df = read_output_file('output.xlsx')
df1 = process_file('Boreholes_RunLines_20230617.txt', completed_tasks_df)
df2 = process_file('CPT_RunLines_20230617.txt', completed_tasks_df)

df_combined = pd.concat([df1, df2])

# Convert 'completion_date' to datetime and then to string
df_combined['completion_date'] = pd.to_datetime(df_combined['completion_date']).dt.strftime('%Y-%m-%d %H:%M:%S')


############################


############################

# Load the data
df = pd.read_excel('output.xlsx')

# Ensure 'distance' is a float
df['distance'] = df['distance'].str.replace(' km','').astype(float)

# Rename 'operator' to 'teams'
df.rename(columns={'operator': 'teams'}, inplace=True)

# Sort strings alphabetically within each teams
df['teams'] = df['teams'].apply(lambda x: '/'.join(sorted(x.split('/'))))

# Convert 'duration' and 'from', 'to' to minutes
df['duration_minutes'] = df['duration'].apply(duration_to_minutes)
df['from'] = pd.to_datetime(df['from'])
df['to'] = pd.to_datetime(df['to'])

# Sort DataFrame by 'from' in ascending order
df.sort_values('from', inplace=True)

# Initialize an empty DataFrame to hold box change data
box_changes = pd.DataFrame(columns=['box_name', 'log_off', 'next_box', 'log_on', 'time_diff'])

##################

##################

last_box = None
last_log_off = None

for _, row in df.iterrows():
    if row['box_name'] != last_box:
        if last_box is not None:
            next_log_on = df[(df['box_name'] == row['box_name']) & (df['from'] > last_log_off)]['from'].min()
            if pd.isnull(next_log_on):  
                continue
            time_diff = (next_log_on - last_log_off).total_seconds() / 60
            box_changes = pd.concat([box_changes, pd.DataFrame([{
                'box_name': last_box,
                'log_off': last_log_off.strftime('%Y-%m-%d %H:%M:%S'),
                'next_box': row['box_name'],
                'log_on': next_log_on.strftime('%Y-%m-%d %H:%M:%S'),
                'time_diff': time_diff
            }])])
        last_box = row['box_name']
    last_log_off = row['to']  

df['day'] = df['from'].dt.date

grouped = df.groupby(['box_name', 'day']).agg({'from': 'min', 'to': 'max'})

grouped['duration'] = (grouped['to'] - grouped['from']).dt.total_seconds() / 60

total_duration_per_box_with_relocation = grouped.groupby('box_name')['duration'].sum()

# fastest box
fastest_bh_box = total_duration_per_box_with_relocation[total_duration_per_box_with_relocation.index.str.startswith('BH_')].idxmin()
fastest_cpt_box = total_duration_per_box_with_relocation[total_duration_per_box_with_relocation.index.str.startswith('CPT_')].idxmin()
fastest_bh_box_time = total_duration_per_box_with_relocation.loc[fastest_bh_box]
fastest_cpt_box_time = total_duration_per_box_with_relocation.loc[fastest_cpt_box]


df['from'] = df['from'].dt.strftime('%Y-%m-%d %H:%M:%S')
df['to'] = df['to'].dt.strftime('%Y-%m-%d %H:%M:%S')

total_distance_surveyed = df['distance'].sum()

total_lines_by_team = df.groupby('teams')['line'].count()

total_boxes_by_team = df.groupby('teams')['box_name'].nunique()

team_efficiency = pd.concat([total_lines_by_team, total_boxes_by_team], axis=1)
team_efficiency.columns = ['Total Lines', 'Total Boxes']

total_distance_per_box = df.groupby('box_name')['distance'].sum()

survey_frequency_per_box = df['box_name'].value_counts()

retries_per_box = df[df['line'].str.contains('(_RR|_INF|_in)', case=False)]['box_name'].value_counts().reindex(df['box_name'].unique(), fill_value=0)

duration_per_line_in_box = df.groupby(['box_name', 'line'])['duration_minutes'].mean()

total_duration_per_box = df.groupby('box_name')['duration_minutes'].sum()

completed_tasks = read_output_file('output.xlsx')
df1 = process_file('Boreholes_RunLines_20230617.txt', completed_tasks)
df2 = process_file('CPT_RunLines_20230617.txt', completed_tasks)

df_combined = pd.concat([df1, df2])

completed_lines = df_combined[df_combined['completed'] == 'y'].shape[0]
total_lines = df_combined.shape[0]
completion_percentage = completed_lines / total_lines * 100

retries = df[df['line'].str.contains('(_RR|_INF|_in)', case=False)].shape[0]
retries_percentage = retries / completed_lines * 100

median_BH_box_time = total_duration_per_box_with_relocation[total_duration_per_box_with_relocation.index.str.startswith('BH_')].median()
median_CPT_box_time = total_duration_per_box_with_relocation[total_duration_per_box_with_relocation.index.str.startswith('CPT_')].median()
median_time_between_boxes = box_changes['time_diff'].median()

############


# Load box location data from csv
box_location_df = pd.read_csv('box_locations.csv', names=['Box Name', 'X', 'Y'])

# Define the completed boxes from the box_changes DataFrame
completed_boxes = box_changes['box_name'].unique()

# Add a new column to the box_location_df DataFrame, checking if the box has been completed
box_location_df['Completed'] = box_location_df['Box Name'].apply(lambda x: 'y' if x in completed_boxes else '')

###########################################


# Convert 'from' and 'to' to datetime
df['from'] = pd.to_datetime(df['from'])
df['to'] = pd.to_datetime(df['to'])

# Split the 'teams' column into individual operators and explode
df['operators'] = df['teams'].str.split('/')
df_exploded = df.explode('operators')

# Calculate the first log on and last log off for each operator
log_on_off_times = df_exploded.groupby('operators').agg({'from': 'min', 'to': 'max'})

# Rename the columns for clarity
log_on_off_times.columns = ['First Log On', 'Last Log Off']

# Convert datetime to string
log_on_off_times['First Log On'] = log_on_off_times['First Log On'].dt.strftime('%Y-%m-%d %H:%M:%S')
log_on_off_times['Last Log Off'] = log_on_off_times['Last Log Off'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Merge team_efficiency with log_on_off_times
team_efficiency_exploded = df_exploded.groupby('operators').agg({'line': 'count', 'box_name': 'nunique'})
team_efficiency_exploded.columns = ['Total Lines', 'Total Boxes']

team_efficiency_exploded = team_efficiency_exploded.merge(log_on_off_times, left_index=True, right_index=True)


# ...
# ...



########################################


# Function to calculate distance between two points in a Cartesian coordinate system
def calculate_distance(x1, y1, x2, y2):
    distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2) / 1000  # Convert to km
    return distance

# Merge box locations to the 'Time Between Boxes' dataframe
df_box_changes_with_location = box_changes.merge(box_location_df, 
                                        left_on='box_name', 
                                        right_on='Box Name', 
                                        how='left')

df_box_changes_with_location = df_box_changes_with_location.merge(box_location_df, 
                            left_on='next_box', 
                            right_on='Box Name', 
                            how='left', 
                            suffixes=('_current', '_next'))

# Calculate distance
df_box_changes_with_location['distance'] = df_box_changes_with_location.apply(lambda row: calculate_distance(row['X_current'], row['Y_current'], row['X_next'], row['Y_next']), axis=1)

# Create 'Travel Box to Box' dataframe
df_travel_box_to_box = df_box_changes_with_location[['box_name', 'next_box', 'distance']]

totaldistance = df_travel_box_to_box['distance'].sum()

summary_df = pd.DataFrame(
    data=np.array([completion_percentage, completed_lines, retries_percentage, total_distance_surveyed,  totaldistance, median_BH_box_time, median_CPT_box_time, median_time_between_boxes, fastest_bh_box_time, fastest_cpt_box_time]).reshape(1, -1),
    columns=['Completion Percentage', 'Completed Lines', 'Infill Percentage', 'Total Distance Surveyed (Km)', 'Total Distance Box-to-Box', 'Median BH Box Time (Minutes)', 'Median CPT Box Time (Minutes)', 'Median Time Between Boxes (Minutes)', 'Fastest BH Box Time (Minutes)', 'Fastest CPT Box Time (Minutes)']
)


summary_df = summary_df.T


##################################################

with pd.ExcelWriter('marine_survey_analysis.xlsx') as writer:
    summary_df.to_excel(writer, sheet_name='Summary', header=False)
    team_efficiency.to_excel(writer, sheet_name='Teams')
    team_efficiency_exploded.to_excel(writer, sheet_name='Operator Schedule')
    total_distance_per_box.to_excel(writer, sheet_name='Total Distance logged per Box')
    df_travel_box_to_box.to_excel(writer, sheet_name='Travel Box to Box', index=False)
    survey_frequency_per_box.to_excel(writer, sheet_name='Survey Frequency per Box')
    retries_per_box.to_excel(writer, sheet_name='Retries per Box')
    duration_per_line_in_box.to_excel(writer, sheet_name='Duration per Line in Box')
    total_duration_per_box.to_excel(writer, sheet_name='Logged Duration per Box')
    box_changes.to_excel(writer, sheet_name='Time Between Boxes', index=False)
    total_duration_per_box_with_relocation.to_excel(writer, sheet_name='Total Duration per Box with Line Relocation')
    box_location_df.to_excel(writer, sheet_name='Box Locations', index=False)
    df_combined.to_excel(writer, sheet_name='Progress', index=False)
    last_box_change_date = box_changes['log_off'].max()
    history_df = pd.DataFrame([last_box_change_date], columns=['Latest Date'])
    history_df.to_excel(writer, sheet_name='History', index=False)
    
