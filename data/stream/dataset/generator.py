import math
import random

from datetime import (
    datetime, 
    timedelta
)


import numpy as np
import pandas as pd

# from config.logging import Logger


class Generator:
    """
    Synthetic data generator with defined parameters.
    """
    def __init__(
        self, 
        n_records: int = 10000, 
        n_machines: int = 10, 
        n_operators: int = 5, 
        start_time: str = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S"), 
        combined_prob: float = 0.05,
        conditional_prob: float = 0.05,
        missing_rate: float = 0.02,
        delay_rate: float = 0.01,
        csv_path: str = './dataset.csv',
        # logger: Logger = None
    ) -> None:
        self.n_records = n_records
        self.n_machines = n_machines
        self.n_operators = n_operators
        self.start_time = start_time
        self.combined_prob = combined_prob
        self.conditional_prob = conditional_prob
        self.missing_rate = missing_rate
        self.delay_rate = delay_rate
        self.csv_path = csv_path
        # self.logger = Logger().setup_logger('dataset')

    def generate_data_point(self) -> pd.DataFrame:
        try:
            data = self.generate_base_data(1, self.n_machines, self.start_time)
            data = self.add_shift_effects(data)
            data = self.add_machine_effects(data, self.n_machines)
            data = self.add_context_metadata(data, self.n_operators, material_types=None)

            return data
        except Exception as e:
            pass
            # self.logger.error(f' [X] Error while generating dataset: {e}')


    def generate_csv(self) -> None:
        """
        Generates synthetic data then dumps to .csv file.
        """
        # self.logger.info(f' [*] Generating dataset...')
        try:
            data = self.generate_base_data(self.n_records, self.n_machines, self.start_time)
            data = self.add_shift_effects(data)
            data = self.add_machine_effects(data, self.n_machines)
            data = self.add_context_metadata(data, self.n_operators, material_types=None)
            data = self.add_anomalies(data)
            data = self.add_data_delays(data)

            data.to_csv(self.csv_path, index=False)
            # self.logger.info(f' [*] Generated dataset to {self.csv_path}')
        except Exception as e:
            pass
            # self.logger.error(f' [X] Error while generating dataset: {e}')

    def generate1(
        self, 
        iter: int, 
        interval_seconds: int = 30, 
        start_time: datetime = datetime.now() - timedelta(hours=24),
        anomaly_rate: int = 5
    ) -> dict:
        """
        # ! DEPRECATED !
        Original prototype data generator.
            - `num_entries`: Number of data entries that will be generated. 
            - `interval_seconds`: Interval between each entry. 
            - `start_time`: Dataset start time. 
            - `anomaly_rate`: Chance of data to generate an anomaly for each entry, from 0% to 100%. 
        """
        def temperature(hour):
            return 15 + 10 * math.sin((hour / 24) * 2 * math.pi) + random.uniform(-3, 3)

        def humidity(hour):
            return 55 + 10 * math.cos((hour / 24) * 2 * math.pi) + random.uniform(-5, 5)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hour = (start_time + timedelta(seconds=iter * interval_seconds)).hour

        temp = temperature(hour)
        hum = humidity(hour)
        
        gyro = [round(random.uniform(0, 10), 2) for _ in range(3)]
        accel = [round(random.uniform(0, 5), 2) for _ in range(3)]

        sensor_data = {
            "sensor": str(random.randint(1, 4)),
            "time": current_time,
            "temp": str(round(temp, 2)),
            "hum": str(round(hum, 2)),
            "gyro": gyro,
            "accel": accel
        }

        if random.randint(0, 100) < anomaly_rate:
            anomaly_type = random.choice(["temp_spike", "high_gyro", "high_accel", "combo"])
            if anomaly_type == "temp_spike":
                sensor_data["temp"] = str(round(random.uniform(100, 150), 2))  # Extreme temperature
            elif anomaly_type == "high_gyro":
                sensor_data["gyro"] = [round(random.uniform(100, 200), 2) for _ in range(3)]  # High gyro
            elif anomaly_type == "high_accel":
                sensor_data["accel"] = [round(random.uniform(10, 20), 2) for _ in range(3)]  # High accel
            elif anomaly_type == "combo":
                sensor_data["temp"] = str(round(random.uniform(80, 120), 2))
                sensor_data["hum"] = str(round(random.uniform(60, 80), 2))
                sensor_data["gyro"] = [round(random.uniform(50, 100), 2) for _ in range(3)]

        return 
    
    # function to generate base dataset
    def generate_base_data(self, n_records: int = 10000, n_machines: int = 10, start_time: str = str(datetime.now() - timedelta(hours=24))) -> pd.DataFrame:
        """
        Generates base dataset that consists of the following fields:
        - `timestamp`
        - `machine_id`
        - `temperature`
        - `humidity`
        - `vibration`
        - `gyro_x`
        - `gyro_y`
        - `gyro_z`
        - `accel_x`
        - `accel_y`
        - `accel_z`

        For generating data in real-time, call this function in a loop and set `n_records` to 1.

        args:
            `n_records`: Number of records that will be generated to dataset.
            `n_machines`: Number of machines in dataset.
            `start_time`: Dataset start time.

        return:
            `data`: Augmented Pandas DataFrame containing the dataset.
        """
        # create timestamps
        start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        # generate data with intervals ranging around 0.01s to 3s
        timestamps = [start_time + timedelta(seconds=i * random.uniform(0.01, 3)) for i in range(n_records)]
        
        # simulate machine IDs
        machine_ids = np.random.randint(0, n_machines, n_records)
        
        # generate random sensor data
        temperature = np.random.normal(20, 5, n_records)
        humidity = np.random.normal(50, 10, n_records)
        vibration = np.random.normal(0.1, 0.02, n_records)
        gyro_x = np.random.normal(0, 50, n_records)
        gyro_y = np.random.normal(0, 50, n_records)
        gyro_z = np.random.normal(0, 50, n_records)
        accel_x = np.random.normal(0, 5, n_records)
        accel_y = np.random.normal(0, 5, n_records)
        accel_z = np.random.normal(0, 5, n_records)
        
        return pd.DataFrame({
            "timestamp": timestamps,
            "machine_id": machine_ids,
            "temperature": temperature,
            "humidity": humidity,
            "vibration": vibration,
            "gyro_x": gyro_x,
            "gyro_y": gyro_y,
            "gyro_z": gyro_z,
            "accel_x": accel_x,
            "accel_y": accel_y,
            "accel_z": accel_z
        })
    
    # add shift based modifiers
    def add_shift_effects(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Helper function to incorporate temporal patterns. 
        
        Adds shift-based effects to dataset as manufacturing processes 
        often vary based on time of day, shifts, or maintenance schedules.
        
        ### Shift effects:
        Assigns a `shift` based on the hour of the day, then applies a `shift_modifiers` dictionary to influence temperature based on the shift type.
            - Morning shifts might have higher efficiency.
            - Night shifts might show increased wear-and-tear or anomalies due to reduced oversight.
        ### Weekly Trends:
        Uses the day_of_week feature (0 for Monday, 6 for Sunday) to modify temperature and vibration values.
            - Mondays might show startup issues.
            - Fridays might have shutdown-related anomalies.
        ### Seasonal Trends:
        Uses the `month` feature to modify temperature values.
            - Uses the month feature to modify temperature values.
            - Lower temperatures during winter months (December-February).

        args:
            `data`: Pandas DataFrame containing the dataset.

        return:
            `data`: Augmented Pandas DataFrame containing the dataset.
        """    
        # extract time-based features
        data['hour'] = data['timestamp'].dt.hour
        data['day_of_week'] = data['timestamp'].dt.dayofweek
        data['month'] = data['timestamp'].dt.month

        # add shift-based effects
        data['shift'] = np.where(
            data['hour'] < 8, 
            "Night", 
            np.where(data['hour'] < 16, "Day", "Evening")
        )
        shift_modifiers = {
            "Night": -3, 
            "Day": 0, 
            "Evening": 2
        }
        data['temperature'] += data['shift'].map(shift_modifiers)

        # add weekly trends
        # ex: Monday (day_of_week=0) has startup issues (higher temp/vibration)
        # Friday (day_of_week=4) has shutdown anomalies (increased vibration)
        weekly_modifiers_temp = {
            0: 2, 
            1: 0, 
            2: -1, 
            3: -1, 
            4: 1, 
            5: 0, 
            6: 1
        }
        weekly_modifiers_vibration = {
            0: 0.01, 
            1: 0.0, 
            2: -0.005, 
            3: -0.005, 
            4: 0.02, 
            5: 0.0, 
            6: 0.01
        }
        data['temperature'] += data['day_of_week'].map(weekly_modifiers_temp)
        data['vibration'] += data['day_of_week'].map(weekly_modifiers_vibration)

        # add seasonal trends
        # ex: Summer months (June, July, August) have higher temperatures
        # Winter months (December, January, February) have lower temperatures
        seasonal_modifiers_temp = {
            1: -5, 
            2: -4, 
            3: -2, 
            4: 0, 
            5: 2, 
            6: 5, 
            7: 7, 
            8: 6, 
            9: 3, 
            10: 1, 
            11: -2, 
            12: -4
        }
        data['temperature'] += data['month'].map(seasonal_modifiers_temp)

        return data
    
    # simulate machine-specific baseline adjustments
    def add_machine_effects(self, data: pd.DataFrame, n_machines: int = 10) -> pd.DataFrame:
        """
        Introduces machine variability.
        
        Different machines may have unique characteristics or failure patterns.

        - Older machines may have higher vibration baselines.
        - Specific machine types may operate within distinct temperature ranges.

        args:
            `data`: Pandas DataFrame containing the dataset.
            `n_machines`: Number of machines in dataset.

        return:
            `data`: Augmented Pandas DataFrame containing the dataset.
        """
        machine_types = ["TypeA", "TypeB", "TypeC"]
        machine_ages = np.random.randint(1, 15, n_machines)
        
        machine_data = pd.DataFrame({
            "machine_id": range(n_machines),
            "machine_type": np.random.choice(machine_types, n_machines),
            "machine_age": machine_ages
        })
        
        data = data.merge(machine_data, on="machine_id")
        data['temperature'] += data['machine_age'] * 0.5  # Older machines run hotter
        data['vibration'] += data['machine_type'].map({
            "TypeA": 0.01, 
            "TypeB": 0.02, 
            "TypeC": -0.01
        })
        
        return data


    # simulate metadata
    def add_context_metadata(self, data: pd.DataFrame, n_operators: int = 5, material_types: str = None) -> pd.DataFrame:
        """
        Include contextual data for each record, such as:
        - Operator ID: Simulate variability based on operators.
        - Material Type: Different materials may affect vibration or cycle time.
        - Maintenance Logs: Add fields indicating recent maintenance.

        args:
            `data`: Pandas DataFrame containing the dataset.
            `n_operators`: Number of machine operators in dataset (different to `n_machines`).
            `material_types`: Machine material type in dataset.

        return:
            `data`: Augmented Pandas DataFrame containing the dataset.
        """
        if material_types is None:
            material_types = ["Steel", "Aluminum", "Plastic", "Copper", "Composite"]

        # add operator ID
        data['operator_id'] = np.random.choice(
            [f"OP_{i}" for i in range(1, n_operators + 1)], 
            size=len(data)
        )

        # add material type
        data['material_type'] = np.random.choice(material_types, size=len(data))

        # add cycle time (in seconds)
        # assuming a normal operation range between 30 and 300 seconds, with some variability
        data['cycle_time'] = np.random.normal(loc=120, scale=30, size=len(data)).clip(min=30, max=300)

        # add maintenance logs
        # simulate the time since the last maintenance in days
        data['days_since_last_maintenance'] = np.random.randint(0, 30, size=len(data))

        # add maintenance-related effects
        # machines with recent maintenance (less than 3 days) operate more efficiently
        # machines without recent maintenance (>25 days) show slight performance degradation
        data['temperature'] -= np.where(data['days_since_last_maintenance'] < 3, 2, 0)
        data['vibration'] += np.where(data['days_since_last_maintenance'] > 25, 0.02, 0)
        # adjust cycle time based on maintenance:
        # machines with overdue maintenance (>25 days) have slightly longer cycles
        data['cycle_time'] += np.where(data['days_since_last_maintenance'] > 25, 5, 0)

        return data

    def add_anomalies(self, data: pd.DataFrame, combined_prob: float = 0.05, conditional_prob: float = 0.05) -> pd.DataFrame:
        """
        Add gradual, combined, and conditional anomalies to the dataset.
        
        ### Combined Anomalies:
        - Randomly selects rows and adds deviations to multiple metrics simultaneously.
        - Increases `temperature`, `vibration`, and `cycle_time`.

        ### Conditional Anomalies:
        - Filters rows where specific conditions (e.g., overdue maintenance and specific material type) are met.
        - Introduces anomalies only in those rows.

        ### Gradual Failures:
        - Gradually shifts the values of temperature and vibration over multiple rows.
        
        args:
            `data`: Pandas DataFrame containing the dataset.
            `combined_prob`: Probability of combined anomalies.
            `conditional_prob`: Probability of conditional anomalies.

        return:
            `data`: Augmented Pandas DataFrame containing the dataset.
        """
        # create a copy of the data to modify
        data = data.copy()

        # combined anomalies
        combined_anomaly_indices = data.sample(frac=combined_prob).index
        data.loc[combined_anomaly_indices, "temperature"] += np.random.uniform(5, 10, size=len(combined_anomaly_indices))
        data.loc[combined_anomaly_indices, "vibration"] += np.random.uniform(0.1, 0.3, size=len(combined_anomaly_indices))
        data.loc[combined_anomaly_indices, "cycle_time"] += np.random.uniform(10, 20, size=len(combined_anomaly_indices))

        # conditional anomalies
        conditional_anomaly_indices = data[
            (data['days_since_last_maintenance'] > 25) &    # overdue maintenance
            (data['material_type'] == "Steel")              # high-stress material
        ].sample(frac=conditional_prob, random_state=42).index

        data.loc[conditional_anomaly_indices, "temperature"] += np.random.uniform(10, 20, size=len(conditional_anomaly_indices))
        data.loc[conditional_anomaly_indices, "vibration"] += np.random.uniform(0.3, 0.5, size=len(conditional_anomaly_indices))
        data.loc[conditional_anomaly_indices, "cycle_time"] += np.random.uniform(20, 30, size=len(conditional_anomaly_indices))

        # gradual failures
        gradual_failure_indices = np.random.choice(data.index, size=int(0.02 * len(data)), replace=False)
        for idx in gradual_failure_indices:
            failure_duration = np.random.randint(5, 20)  # gradual failure over 5–20 rows
            drift = np.linspace(0, np.random.uniform(10, 30), failure_duration)
            # ensure exact slice matching
            end_idx = min(idx + len(drift) - 1, len(data) - 1)
            # use precise slicing
            temp_slice = data.loc[idx:end_idx, "temperature"]
            vibration_slice = data.loc[idx:end_idx, "vibration"]
            # ensure drift is trimmed to match slice exactly
            drift = drift[:len(temp_slice)]
            data.loc[idx:end_idx, "temperature"] += drift
            data.loc[idx:end_idx, "vibration"] += drift * 0.02  # smaller effect on vibration

        return data
    
    # simulate missing and delayed data
    def add_data_delays(self, data: pd.DataFrame, missing_rate: float = 0.02, delay_rate: float = 0.01) -> pd.DataFrame:
        """
        Incorporate delays and missing data.
        - Randomly drop records to simulate sensor outages.
        - Introduce time lags for certain records to mimic network delays.

        args:
            `data`: Pandas DataFrame containing the dataset.
            `missing_rate`: Probability of missing data.
            `delay_rate`: Data delay rate.

        return:
            `data`: Augmented Pandas DataFrame containing the dataset.
        """
        # drop some records
        data = data.sample(frac=1 - missing_rate).reset_index(drop=True)
        
        # add delays
        delay_indices = np.random.choice(data.index, size=int(len(data) * delay_rate), replace=False)
        data.loc[delay_indices, 'timestamp'] += pd.to_timedelta(np.random.randint(1, 60, len(delay_indices)), unit='s')
        
        return data


if __name__ == '__main__':
    generator = Generator()
    generator.generate_csv()
