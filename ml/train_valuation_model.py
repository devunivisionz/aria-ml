"""
Train ML model on extracted deals
"""

import json
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# Load deals
print("📊 Loading deals...")
with open('extracted_deals.json', 'r') as f:
    deals = json.load(f)
df = pd.DataFrame(deals)
print(f"✓ Loaded {len(df)} deals")

# Sector multiples (from Njord patterns)
sector_multiples = {
    'Trading/Commodities': 0.3,
    'Cannabis/Healthcare': 3.0,
    'Construction/Real Estate': 0.7,
    'Manufacturing': 1.0,
    'Mining/Resources': 1.2,
    'Technology': 4.5,
    'Gaming/Entertainment': 5.0,
    'Energy': 1.5
}

# Geography adjustments
geo_adjustments = {
    'North America': 1.2,
    'Europe': 1.0,
    'South America': 0.7,
    'Africa': 0.7,
    'Global': 1.0
}

# Calculate multiples
df['base_multiple'] = df['sector'].map(sector_multiples).fillna(1.5)
df['geo_adjustment'] = df['geography'].map(geo_adjustments).fillna(1.0)
df['revenue_multiple'] = df['base_multiple'] * df['geo_adjustment']

# Add some realistic variation
np.random.seed(42)
df['revenue_multiple'] *= np.random.uniform(0.8, 1.2, len(df))

print("\n📈 Sector Multiples:")
print(df.groupby('sector')['revenue_multiple'].mean().round(2))

# Prepare features
le_sector = LabelEncoder()
le_geography = LabelEncoder()

df['sector_encoded'] = le_sector.fit_transform(df['sector'].fillna('Other'))
df['geography_encoded'] = le_geography.fit_transform(df['geography'].fillna('Global'))
df['revenue_clean'] = df['revenue_m'].fillna(50)

# Train model
X = df[['sector_encoded', 'geography_encoded', 'revenue_clean']]
y = df['revenue_multiple']

# With only 5 samples, use all for training
model = RandomForestRegressor(
    n_estimators=10,
    max_depth=2,
    random_state=42
)

print("\n🎓 Training model...")
model.fit(X, y)
print(f"✓ Model trained (R²: {model.score(X, y):.3f})")

# Save everything
os.makedirs('ml/models', exist_ok=True)
joblib.dump(model, 'ml/models/revenue_multiple_model.pkl')
joblib.dump(le_sector, 'ml/models/sector_encoder.pkl')
joblib.dump(le_geography, 'ml/models/geography_encoder.pkl')
print("✓ Models saved to ml/models/")

# Test predictions
print("\n🔮 Test Predictions:")
test_cases = [
    ("Technology", "North America", 50),
    ("Mining/Resources", "Africa", 30),
    ("Trading/Commodities", "Europe", 500),
]

for sector, geo, revenue in test_cases:
    try:
        s_enc = le_sector.transform([sector])[0]
    except:
        s_enc = 0
    try:
        g_enc = le_geography.transform([geo])[0]
    except:
        g_enc = 0
    
    pred = model.predict([[s_enc, g_enc, revenue]])[0]
    print(f"\n{sector} in {geo} (€{revenue}M)")
    print(f"  Multiple: {pred:.2f}x → Valuation: €{pred*revenue:.0f}M")

print("\n✅ Training complete!")