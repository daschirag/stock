"""
CNN-LSTM hybrid model for mid-frequency IMF prediction.
"""
import numpy as np
from typing import Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

from app.core import settings, get_logger


logger = get_logger(__name__)


class CNNLSTMModel:
    """
    CNN-LSTM hybrid model for mid-frequency IMFs.
    
    Architecture:
    - Conv1D: 64 filters, kernel_size=3
    - MaxPooling1D: pool_size=2
    - LSTM: 128 units with dropout 0.2
   - Dense layers: [64, 1]
    """
    
    def __init__(
        self,
        sequence_length: int = 60,
        n_features: int = 1,
        conv_filters: int = 64,
        kernel_size: int = 3,
        lstm_units: int = 128,
        dropout: float = 0.2,
        learning_rate: float = 0.001
    ):
        """
        Initialize CNN-LSTM model.
        
        Args:
            sequence_length: Length of input sequence
            n_features: Number of input features
            conv_filters: Number of convolutional filters
            kernel_size: Size of convolution kernel
            lstm_units: Number of LSTM units
            dropout: Dropout rate
            learning_rate: Learning rate
        """
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.conv_filters = conv_filters
        self.kernel_size = kernel_size
        self.lstm_units = lstm_units
        self.dropout = dropout
        self.learning_rate = learning_rate
        
        self.model = None
        self.framework = self._detect_framework()
        
        logger.info(f"Initializing CNN-LSTM with {self.framework}")
    
    def _detect_framework(self) -> str:
        """Detect available deep learning framework."""
        try:
            import tensorflow as tf
            return "tensorflow"
        except ImportError:
            try:
                import torch
                return "pytorch"
            except ImportError:
                return "none"
    
    def build_model(self):
        """Build the CNN-LSTM model."""
        if self.framework == "tensorflow":
            self._build_tensorflow_model()
        elif self.framework == "pytorch":
            self._build_pytorch_model()
        else:
            raise RuntimeError("No deep learning framework available")
    
    def _build_tensorflow_model(self):
        """Build model using TensorFlow/Keras."""
        import tensorflow as tf
        from tensorflow import keras
        from tensorflow.keras import layers
        
        # Input layer
        inputs = keras.Input(shape=(self.sequence_length, self.n_features))
        
        # Conv1D layers
        x = layers.Conv1D(
            filters=self.conv_filters,
            kernel_size=self.kernel_size,
            activation='relu',
            padding='same'
        )(inputs)
        x = layers.MaxPooling1D(pool_size=2)(x)
        x = layers.Dropout(self.dropout)(x)
        
        # LSTM layer
        x = layers.LSTM(
            self.lstm_units,
            dropout=self.dropout,
            recurrent_dropout=self.dropout
        )(x)
        
        # Dense layers
        x = layers.Dense(64, activation='relu')(x)
        x = layers.Dropout(self.dropout)(x)
        outputs = layers.Dense(1)(x)
        
        # Create model
        self.model = keras.Model(inputs=inputs, outputs=outputs)
        
        # Compile
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='huber',
            metrics=['mae', 'mse']
        )
        
        logger.info("TensorFlow CNN-LSTM model built successfully")
    
    def _build_pytorch_model(self):
        """Build model using PyTorch."""
        import torch
        import torch.nn as nn
        
        class PyTorchCNNLSTM(nn.Module):
            def __init__(
                self,
                input_size,
                conv_filters,
                kernel_size,
                lstm_units,
                dropout
            ):
                super(PyTorchCNNLSTM, self).__init__()
                
                self.conv1 = nn.Conv1d(
                    in_channels=input_size,
                    out_channels=conv_filters,
                    kernel_size=kernel_size,
                    padding=kernel_size // 2
                )
                self.pool = nn.MaxPool1d(kernel_size=2)
                self.dropout1 = nn.Dropout(dropout)
                
                self.lstm = nn.LSTM(
                    input_size=conv_filters,
                    hidden_size=lstm_units,
                    num_layers=1,
                    batch_first=True,
                    dropout=dropout if dropout > 0 else 0
                )
                
                self.fc1 = nn.Linear(lstm_units, 64)
                self.dropout2 = nn.Dropout(dropout)
                self.fc2 = nn.Linear(64, 1)
                
                self.relu = nn.ReLU()
            
            def forward(self, x):
                # Transpose for Conv1d (batch, features, seq_len)
                x = x.transpose(1, 2)
                
                # Conv layers
                x = self.relu(self.conv1(x))
                x = self.pool(x)
                x = self.dropout1(x)
                
                # Transpose back for LSTM (batch, seq_len, features)
                x = x.transpose(1, 2)
                
                # LSTM
                _, (hidden, _) = self.lstm(x)
                x = hidden[-1]
                
                # Dense layers
                x = self.dropout2(self.relu(self.fc1(x)))
                x = self.fc2(x)
                
                return x
        
        self.model = PyTorchCNNLSTM(
            input_size=self.n_features,
            conv_filters=self.conv_filters,
            kernel_size=self.kernel_size,
            lstm_units=self.lstm_units,
            dropout=self.dropout
        )
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        logger.info(f"PyTorch CNN-LSTM model built on {self.device}")
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        epochs: int = 100,
        batch_size: int = 32,
        early_stopping_patience: int = 20
    ) -> dict:
        """Train the model."""
        if self.model is None:
            self.build_model()
        
        if self.framework == "tensorflow":
            import tensorflow as tf
            from tensorflow import keras
            
            callbacks = [
                keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=early_stopping_patience,
                    restore_best_weights=True
                ),
                keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=10,
                    min_lr=1e-6
                )
            ]
            
            history = self.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val) if X_val is not None else None,
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=1
            )
            
            return history.history
        else:
            # Similar PyTorch training logic as BiLSTM
            import torch
            import torch.nn as nn
            from torch.utils.data import DataLoader, TensorDataset
            
            X_train_tensor = torch.FloatTensor(X_train).to(self.device)
            y_train_tensor = torch.FloatTensor(y_train).to(self.device)
            
            train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
            train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
            
            optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
            criterion = nn.HuberLoss()
            
            history = {'loss': [], 'val_loss': []}
            
            for epoch in range(epochs):
                self.model.train()
                train_loss = 0
                for batch_X, batch_y in train_loader:
                    optimizer.zero_grad()
                    outputs = self.model(batch_X)
                    loss = criterion(outputs, batch_y)
                    loss.backward()
                    optimizer.step()
                    train_loss += loss.item()
                
                history['loss'].append(train_loss / len(train_loader))
                
                if (epoch + 1) % 10 == 0:
                    logger.info(f"Epoch {epoch+1}/{epochs} - Loss: {history['loss'][-1]:.4f}")
            
            return history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if self.framework == "tensorflow":
            return self.model.predict(X)
        else:
            import torch
            self.model.eval()
            with torch.no_grad():
                X_tensor = torch.FloatTensor(X).to(self.device)
                predictions = self.model(X_tensor).cpu().numpy()
            return predictions
    
    def save(self, filepath: str):
        """Save model."""
        if self.framework == "tensorflow":
            self.model.save(filepath)
        else:
            import torch
            torch.save(self.model.state_dict(), filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load(self, filepath: str):
        """Load model."""
        if self.framework == "tensorflow":
            import tensorflow as tf
            self.model = tf.keras.models.load_model(filepath)
        else:
            import torch
            self.model.load_state_dict(torch.load(filepath))
            self.model.eval()
        logger.info(f"Model loaded from {filepath}")
