-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create oil_prices table with hypertable
CREATE TABLE IF NOT EXISTS oil_prices (
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    PRIMARY KEY (timestamp, symbol)
);

SELECT create_hypertable('oil_prices', 'timestamp', if_not_exists => TRUE);

-- Create technical_indicators table with hypertable
CREATE TABLE IF NOT EXISTS technical_indicators (
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    indicator_name VARCHAR(50) NOT NULL,
    value DECIMAL(15,6),
    PRIMARY KEY (timestamp, symbol, indicator_name)
);

SELECT create_hypertable('technical_indicators', 'timestamp', if_not_exists => TRUE);

-- Create predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    model_version VARCHAR(50),
    prediction_for TIMESTAMPTZ,
    horizon VARCHAR(10),
    predicted_price DECIMAL(10,2),
    confidence_lower DECIMAL(10,2),
    confidence_upper DECIMAL(10,2),
    actual_price DECIMAL(10,2),
    error DECIMAL(10,2)
);

CREATE INDEX IF NOT EXISTS idx_predictions_for ON predictions(prediction_for);
CREATE INDEX IF NOT EXISTS idx_predictions_created ON predictions(created_at);
CREATE INDEX IF NOT EXISTS idx_predictions_horizon ON predictions(horizon);

-- Create model_metadata table
CREATE TABLE IF NOT EXISTS model_metadata (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) UNIQUE,
    trained_at TIMESTAMPTZ DEFAULT NOW(),
    architecture JSONB,
    hyperparameters JSONB,
    training_metrics JSONB,
    is_active BOOLEAN DEFAULT false
);

-- Create sentiment_data table with hypertable
CREATE TABLE IF NOT EXISTS sentiment_data (
    timestamp TIMESTAMPTZ NOT NULL,
    source VARCHAR(50),
    article_url TEXT,
    headline TEXT,
    sentiment_score DECIMAL(5,4),
    credibility_weight DECIMAL(3,2),
    PRIMARY KEY (timestamp, source, article_url)
);

SELECT create_hypertable('sentiment_data', 'timestamp', if_not_exists => TRUE);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_oil_prices_symbol ON oil_prices(symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_technical_indicators_symbol ON technical_indicators(symbol, indicator_name, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sentiment_data_timestamp ON sentiment_data(timestamp DESC);

-- Insert initial model metadata placeholder
INSERT INTO model_metadata (version, architecture, hyperparameters, training_metrics, is_active)
VALUES ('v1.0.0-init', '{}', '{}', '{}', false)
ON CONFLICT (version) DO NOTHING;
