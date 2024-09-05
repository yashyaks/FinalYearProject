import pandas as pd
import numpy as np
import random

demand_df = pd.read_csv('demand.csv')
vehicles_df = pd.read_csv('vehicles.csv')
vehicles_fuels_df = pd.read_csv('vehicles_fuels.csv')
fuels_df = pd.read_csv('fuels.csv')
carbon_emissions_df = pd.read_csv('carbon_emissions.csv')

vehicles_full_df = pd.merge(vehicles_df, vehicles_fuels_df, on='ID')
vehicles_full_df = pd.merge(vehicles_full_df, fuels_df, left_on='Fuel', right_on='Fuel')
combined_df = pd.merge(demand_df, vehicles_full_df, left_on=['Size', 'Distance'], right_on=['Size', 'Distance'])
combined_df.rename(columns={'Year_x': 'Year'}, inplace=True)
combined_df = pd.merge(combined_df, carbon_emissions_df, left_on='Year', right_on='Year')
# print(combined_df)
combined_df.to_csv('Combined_CSV_1.csv', index=False)

np.random.seed(0)  
combined_df['Num_Vehicles'] = np.random.randint(1, 51, size=len(combined_df))

def generate_random_distance(row):
    distance = np.random.uniform(0, row['Yearly range (km)'])
    if np.random.rand() < 0.5:
        return round(distance, 0)
    else:
        return round(distance, 2)

combined_df['Distance_per_vehicle(km)'] = combined_df.apply(generate_random_distance, axis=1)

def set_type(row):
    if row['Year'] == row['Year_y']:
        return 'Buy'
    elif row['Year'] > row['Year_y']:
        return random.choice(['Sell', 'Use'])
combined_df['Type'] = combined_df.apply(set_type, axis=1)

final_df = combined_df[['Year', 'ID', 'Num_Vehicles', 'Type', 'Fuel', 'Distance', 'Distance_per_vehicle(km)', 'Yearly range (km)', 'Year_y']]

final_df = final_df.rename(columns={
    'Year': 'Operating Year',
    'Distance': 'Distance_bucket',
    'Distance_per_vehicle(km)': 'Distance_per_vehicle(km)',
    'Year_y': 'Vehicle_Year'
})

final_df = final_df[(final_df['Type'].isin(['Buy', 'Use', 'Sell'])) &
                    (final_df['Num_Vehicles'] >= 1) &
                    (final_df['Distance_per_vehicle(km)'] > 0) &
                    (final_df['Distance_per_vehicle(km)'] <= final_df['Yearly range (km)'])]

final_df = final_df[~((final_df['Type'] == 'Buy') & (final_df['Operating Year'] != final_df['Vehicle_Year'])) & 
                     ~((final_df['Type'] == 'Sell') & (final_df['Operating Year'] <= final_df['Vehicle_Year']))]

final_df.to_csv('Integrated_Fleet_Data_Cleaned_3.csv', index=False)
