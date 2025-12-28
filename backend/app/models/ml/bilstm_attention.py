"""
BiLSTM-Attention model for high-frequency IMF prediction.
"""
import numpy as np
from typing import Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

from app.core import settings, get_logger


logger = get_logger(__name__)


class BiLSTMAttentionModel:
    """
    Bidirectional LSTM with Multi-head Attention for high-frequency IMFs.
    
    Architecture:
    - Input shape: (sequence_length, n_features)
    - BiLSTM: 256 units with dropout 0.2
    - Multi-head Attention: 8 heads, key_dim=32
    - Dense layers: [128, 64, 1]
    """
    
    def __init__(
        self,
        sequence_length: int = 60,
        n_features: int = 1,
        lstm_units: int = 256,
        attention_heads: int = 8,
        dropout: float = 0.2,
        learning_rate: float = 0.001
    ):
        """
        Initialize BiLSTM-Attention model.
        
        Args:
            sequence_length: Length of input sequence
            n_features: Number of input features
            lstm_units: Number of LSTM units
            attention_heads: Number of attention heads
            dropout: Dropout rate
            learning_rate: Learning rate for optimizer
        """
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.lstm_units = lstm_units
        self.attention_heads = attention_heads
        self.dropout = dropout
        self.learning_rate = learning_rate
        
        self.model = None
        self.framework = self._detect_framework()
        
        logger.info(f"Initializing BiLSTM-Attention with {self.framework}")
    
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
                logger.warning("No deep learning framework available")
                return "none"
    
    def build_model(self):
        """Build the BiLSTM-Attention model."""
        if self.framework == "tensorflow":
            self._build_tensorflow_model()
        elif self.framework == "pytorch":
            self._build_pytorch_model()
        else:
            raise RuntimeError("No deep learning framework available. Install TensorFlow or PyTorch.")
    
    def _build_tensorflow_model(self):
        """Build model using TensorFlow/Keras."""
        try:
            import tensorflow as tf
            from tensorflow import keras
            from tensorflow.keras import layers
            
            # Input layer
            inputs = keras.Input(shape=(self.sequence_length, self.n_features))
            
            # Bidirectional LSTM
            x = layers.Bidirectional(
                layers.LSTM(
                    self.lstm_units,
                    return_sequences=True,
                    dropout=self.dropout,
                    recurrent_dropout=self.dropout
                )
            )(inputs)
            
            # Multi-head Attention
            attention_output = layers.MultiHeadAttention(
                num_heads=self.attention_heads,
                key_dim=32,
                dropout=self.dropout
            )(x, x)
            
            # Add & Norm
            x = layers.Add()([x, attention_output])
            x = layers.LayerNormalization()(x)
            
            # Global pooling
            x = layers.GlobalAveragePooling1D()(x)
            
            # Dense layers
            x = layers.Dense(128, activation='relu')(x)
            x = layers.Dropout(self.dropout)(x)
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
            
            logger.info("TensorFlow BiLSTM-Attention model built successfully")
            
        except Exception as e:
            logger.error(f"Failed to build TensorFlow model: {e}")
            raise
    
    def _build_pytorch_model(self):
        """Build model using PyTorch."""
        try:
            import torch
            import torch.nn as nn
            
            class PyTorchBiLSTMAttention(nn.Module):
                def __init__(
                    self,
                    input_size,
                    lstm_units,
                    attention_heads,
                    dropout
                ):
                    super(PyTorchBiLSTMAttention, self).__init__()
                    
                    self.lstm = nn.LSTM(
                        input_size=input_size,
                        hidden_size=lstm_units,
                        num_layers=1,
                        batch_first=True,
                        bidirectional=True,
                        dropout=dropout if dropout > 0 else 0
                    )
                    
                    self.attention = nn.MultiheadAttention(
                        embed_dim=lstm_units * 2,  # Bidirectional
                        num_heads=attention_heads,
                        dropout=dropout,
                        batch_first=True
                    )
                    
                    self.layer_norm = nn.LayerNorm(lstm_units * 2)
                    
                    self.fc1 = nn.Linear(lstm_units * 2, 128)
                    self.fc2 = nn.Linear(128, 64)
                    self.fc3 = nn.Linear(64, 1)
                    
                    self.dropout = nn.Dropout(dropout)
                    self.relu = nn.ReLU()
                
                def forward(self, x):
                    # LSTM
                    lstm_out, _ = self.lstm(x)
                    
                    # Attention
                    attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
                    
                    # Residual connection + Layer norm
                    x = self.layer_norm(lstm_out + attn_out)
                    
                    # Global average pooling
                    x = torch.mean(x, dim=1)
                    
                    # Dense layers
                    x = self.dropout(self.relu(self.fc1(x)))
                    x = self.dropout(self.relu(self.fc2(x)))
                    x = self.fc3(x)
                    
                    return x
            
            self.model = PyTorchBiLSTMAttention(
                input_size=self.n_features,
                lstm_units=self.lstm_units,
                attention_heads=self.attention_heads,
                dropout=self.dropout
            )
            
            # Set device
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            
            logger.info(f"PyTorch BiLSTM-Attention model built successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to build PyTorch model: {e}")
            raise
    
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
        """
        Train the model.
        
        Args:
            X_train: Training sequences
            y_train: Training targets
            X_val: Validation sequences
            y_val: Validation targets
            epochs: Number of epochs
            batch_size: Batch size
            early_stopping_patience: Patience for early stopping
        
        Returns:
            Training history
        """
        if self.model is None:
            self.build_model()
        
        if self.framework == "tensorflow":
            return self._train_tensorflow(
                X_train, y_train, X_val, y_val,
                epochs, batch_size, early_stopping_patience
            )
        else:
            return self._train_pytorch(
                X_train, y_train, X_val, y_val,
                epochs, batch_size, early_stopping_patience
            )
    
    def _train_tensorflow(
        self,
        X_train,
        y_train,
        X_val,
        y_val,
        epochs,
        batch_size,
        patience
    ):
        """Train with TensorFlow."""
        import tensorflow as tf
        from tensorflow import keras
        
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=patience,
                restore_best_weights=True,
                verbose=1
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=10,
                min_lr=1e-6,
                verbose=1
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
        
        logger.info("Training completed")
        return history.history
    
    def _train_pytorch(
        self,
        X_train,
        y_train,
        X_val,
        y_val,
        epochs,
        batch_size,
        patience
    ):
        """Train with PyTorch."""
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, TensorDataset
        
        # Convert to tensors
        X_train_tensor = torch.FloatTensor(X_train).to(self.device)
        y_train_tensor = torch.FloatTensor(y_train).to(self.device)
        
        train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        if X_val is not None:
            X_val_tensor = torch.FloatTensor(X_val).to(self.device)
            y_val_tensor = torch.FloatTensor(y_val).to(self.device)
        
        # Optimizer and loss
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        criterion = nn.HuberLoss()
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=10
        )
        
        history = {'loss': [], 'val_loss': []}
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(epochs):
            # Training
            self.model.train()
            train_loss = 0
            for batch_X, batch_y in train_loader:
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()
            
            train_loss /= len(train_loader)
            history['loss'].append(train_loss)
            
            # Validation
            if X_val is not None:
                self.model.eval()
                with torch.no_grad():
                    val_outputs = self.model(X_val_tensor)
                    val_loss = criterion(val_outputs, y_val_tensor).item()
                    history['val_loss'].append(val_loss)
                    
                    scheduler.step(val_loss)
                    
                    # Early stopping
                    if val_loss < best_val_loss:
                        best_val_loss = val_loss
                        patience_counter = 0
                        # Save best model
                        torch.save(self.model.state_dict(), 'best_bilstm_model.pt')
                    else:
                        patience_counter += 1
                    
                    if patience_counter >= patience:
                        logger.info(f"Early stopping at epoch {epoch+1}")
                        break
                
                if (epoch + 1) % 10 == 0:
                    logger.info(
                        f"Epoch {epoch+1}/{epochs} - "
                        f"Loss: {train_loss:.4f} - Val Loss: {val_loss:.4f}"
                    )
        
        # Load best model
        if X_val is not None:
            self.model.load_state_dict(torch.load('best_bilstm_model.pt'))
        
        logger.info("Training completed")
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
        """Save model to disk."""
        if self.framework == "tensorflow":
            self.model.save(filepath)
        else:
            import torch
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'config': {
                    'sequence_length': self.sequence_length,
                    'n_features': self.n_features,
                    'lstm_units': self.lstm_units,
                    'attention_heads': self.attention_heads,
                    'dropout': self.dropout,
                    'learning_rate': self.learning_rate
                }
            }, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load(self, filepath: str):
        """Load model from disk."""
        if self.framework == "tensorflow":
            import tensorflow as tf
            self.model = tf.keras.models.load_model(filepath)
        else:
            import torch
            checkpoint = torch.load(filepath)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.eval()
        logger.info(f"Model loaded from {filepath}")
