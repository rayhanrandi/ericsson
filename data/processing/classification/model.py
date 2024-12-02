import pandas as pd
import joblib

class Model:
    """
    Handles loading the model, preprocessing data, and making predictions.
    """

    def __init__(self, model_path: str, scaler_path: str):
        """
        Initialize the Model class with the path to the saved model and the database client.

        :param model_path: Path to the saved model file.
        :param scaler_path: Path to the saved scaler file.
        """
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model = None
        self.scaler = None

    def load_model(self):
        """Loads the trained model."""
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)

    def preprocess_data(self, data: dict) -> pd.DataFrame:
        """
        Preprocess the data received from Kafka.

        :param data: Dictionary containing sensor data.
        :return: Preprocessed pandas DataFrame.
        """
        features = {
            'temp': float(data['temp']),
            'hum': float(data['hum']),
            'gyro_x': float(data['gyro'][0]),
            'gyro_y': float(data['gyro'][1]),
            'gyro_z': float(data['gyro'][2]),
            'accel_x': float(data['accel'][0]),
            'accel_y': float(data['accel'][1]),
            'accel_z': float(data['accel'][2]),
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

    def process_message(self, message: dict) -> dict:
        """
        Process a single message from Kafka: preprocess and predict.

        :param message: Kafka message containing sensor data.
        :return: A dictionary with the necessary values for the table.
        """
        try:
            preprocessed_data = self.preprocess_data(message)
            prediction = self.predict(preprocessed_data).iloc[0]

            result = {
                'timestamp': message['time'],
                'sensor': int(message['sensor']),
                'temp': float(message['temp']),
                'hum': float(message['hum']),
                'gyro_x': float(message['gyro'][0]),
                'gyro_y': float(message['gyro'][1]),
                'gyro_z': float(message['gyro'][2]),
                'accel_x': float(message['accel'][0]),
                'accel_y': float(message['accel'][1]),
                'accel_z': float(message['accel'][2]),
                'prediction': int(prediction)
            }
            return result
        
        except Exception as e:
            print(f"Error processing message: {e}")
            return {}
