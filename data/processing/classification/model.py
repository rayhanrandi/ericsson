import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler


class Model:
    """
    Handles loading the model, preprocessing data, and making predictions.
    """

    def __init__(self, model_path: str, scaler_path: str):
        """
        Initialize the Model class with the path to the saved model and scaler.

        :param model_path: Path to the saved model file.
        :param scaler_path: Path to the saved scaler file.
        """
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model = None
        self.scaler = None

    def load_model(self):
        """Loads the trained model and scaler."""
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)

    def preprocess_data(self, data: dict) -> pd.DataFrame:
        """
        Preprocess the data received from Kafka.

        :param data: Dictionary containing machine sensor data.
        :return: Preprocessed pandas DataFrame.
        """
        features = {
            'temperature': float(data['temperature']),
            'humidity': float(data['humidity']),
            'vibration': float(data['vibration']),
            'gyro_x': float(data['gyro_x']),
            'gyro_y': float(data['gyro_y']),
            'gyro_z': float(data['gyro_z']),
            'accel_x': float(data['accel_x']),
            'accel_y': float(data['accel_y']),
            'accel_z': float(data['accel_z']),
            'cycle_time': float(data['cycle_time']),
            'machine_age': float(data['machine_age']),
            'days_since_last_maintenance': float(data['days_since_last_maintenance'])
        }
        df = pd.DataFrame([features])
        return df

    def predict(self, data: pd.DataFrame) -> pd.Series:
        """
        Make predictions on the preprocessed data.

        :param data: Preprocessed pandas DataFrame.
        :return: Predictions as a pandas Series.
        """
        data_scaled = self.scaler.transform(data)
        predictions = self.model.predict(data_scaled)
        return pd.Series(predictions, name="prediction")

    def process_message(self, message: dict) -> int:
        """
        Process a single message from Kafka: preprocess and predict.

        :param message: Kafka message containing machine sensor data.
        :return: A dictionary with the necessary values for the output.
        """
        try:
            preprocessed_data = self.preprocess_data(message)
            prediction = self.predict(preprocessed_data).iloc[0]

            return int(prediction)

        except Exception as e:
            print(f"Error processing message: {e}")
            return {}
