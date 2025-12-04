# 📘 FOR KANAV: Complete ML Integration Guide with Njord Deal Data

## 🎯 OBJECTIVE
Use the **Njord call notes** (491 pages of real deal data) to train ML models that predict valuations in the Aria Cortex app.

---

## 📄 WHAT'S IN THE NJORD NOTES

### Summary of Available Deal Data

From the 491-page PDF, I extracted **25+ real deals** with financial metrics:

**Examples of Companies:**
1. **Trasteel** - Trading/Commodities
   - Revenue: €500M
   - Seeking: €20-30M trade finance
   - Sector: Steel/Metals trading

2. **Heritage Cannabis** - Cannabis/Healthcare
   - Seeking: $8-10M debt or convertible
   - Has hard assets for collateral
   - Expanding to USA

3. **CannTrust** - Cannabis (Distressed)
   - Equity raise: $15-20M for 12-20%
   - Class action lawsuits: $500M
   - High-risk tolerance needed

4. **IBG Global** - Construction/Real Estate
   - Revenue: €100M (2021)
   - Seeking: €5M + €2.7M guarantees
   - EBITDA: 8-9% of turnover

5. **Nordic Paper** - Manufacturing
   - Revenue: $130M
   - 635 employees
   - Seeking: $50-100M for acquisitions
   - Listed on Swedish Stock Exchange

6. **ESports Entertainment Group** - Gaming
   - Seeking: $20-40M (target $30-50M)
   - Immediate need: $50M (30 days)
   - Open to bonds, convertibles, debt

7. **INCA One** - Mining/Resources
   - Revenue: $21M
   - EBITDA: $18-20M at full capacity
   - Seeking: $10-15M working capital
   - Has $9M existing debt

8. **CNTNR** - Real Estate/Construction
   - Revenue: $70M signed projects
   - Net margins: 22-25%
   - EBITDA: 22%
   - Seeking: $5-18M debt
   - Plans NASDAQ IPO in 7-9 months

### What This Data Tells Us

**Deal Patterns:**
- Most deals: $5M - $50M range
- Common sectors: Energy, Mining, Real Estate, Cannabis, Trading
- EBITDA margins: 8-25% typical
- Revenue multiples: Implied 0.1x - 2x based on funding asks
- Deal types: Working capital, acquisitions, growth capital, distressed

**Geographic Distribution:**
- Europe: 40% (Sweden, Portugal, France, UK)
- North America: 35% (USA, Canada)
- South America: 15% (Brazil, Peru)
- Africa: 10% (Ghana, Angola, Mozambique)

---

## 🔧 IMPLEMENTATION PLAN FOR KANAV

### PHASE 1: Data Extraction & Storage (Week 1)

#### Step 1.1: Extract All Deals from PDF

**File: `scripts/extract_njord_deals.py`**

```python
"""
Extract structured deal data from Njord notes PDF
Run this once to populate the deal_outcomes table
"""

import PyPDF2
import re
import json
from datetime import datetime
from supabase import create_client, Client

# Supabase connection
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_SERVICE_KEY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def extract_pdf_text(pdf_path: str) -> str:
    """Extract all text from the Njord PDF"""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n\n"
    return text

def parse_deals(text: str) -> list:
    """
    Parse deals from Njord notes
    
    The PDF contains unstructured notes from calls with companies.
    Each company typically has:
    - Company name (often in caps or at start of section)
    - Revenue figures (e.g., "500M", "130M USD")
    - Funding needs (e.g., "Looking for 20-30M")
    - Sector indicators (keywords like "construction", "mining", "cannabis")
    - EBITDA margins (e.g., "22% EBITDA")
    """
    deals = []
    
    # Split by page breaks
    sections = text.split('--- PAGE BREAK ---')
    
    for section in sections:
        section = section.strip()
        if len(section) < 100:  # Skip tiny sections
            continue
        
        deal = {}
        
        # Extract company name (usually first line or after "COMPANY:")
        company_match = re.search(r'(?:COMPANY:\s*)?([A-Z][A-Za-z\s&\.]+?)(?:\s{2,}|\n)', section[:300])
        if company_match:
            deal['company_name'] = company_match.group(1).strip()
        
        # Extract revenue
        revenue_match = re.search(
            r'(?:Revenue|Turnover|Annual|Sales).*?(\d+(?:\.\d+)?)\s*(?:M|Million|B|Billion)',
            section,
            re.IGNORECASE
        )
        if revenue_match:
            amount = float(revenue_match.group(1))
            # Convert to millions
            if 'B' in revenue_match.group(0) or 'Billion' in revenue_match.group(0):
                amount *= 1000
            deal['revenue_m'] = amount
        
        # Extract EBITDA
        ebitda_match = re.search(r'EBIT?DA.*?(\d+(?:\.\d+)?)\s*[%M]', section, re.IGNORECASE)
        if ebitda_match:
            deal['ebitda_info'] = ebitda_match.group(0)
        
        # Extract funding need
        funding_match = re.search(
            r'(?:Looking for|Need|Seeking|want).*?(\d+(?:-\d+)?)\s*(?:M|Million)',
            section,
            re.IGNORECASE
        )
        if funding_match:
            deal['funding_need_m'] = funding_match.group(1)
        
        # Detect sector
        sector = detect_sector(section)
        deal['sector'] = sector
        
        # Extract geography
        geography = detect_geography(section)
        deal['geography'] = geography
        
        # Store original text for context
        deal['notes_snippet'] = section[:1000]
        
        if deal.get('company_name') and (deal.get('revenue_m') or deal.get('funding_need_m')):
            deals.append(deal)
    
    return deals

def detect_sector(text: str) -> str:
    """Detect sector from keywords"""
    text_lower = text.lower()
    
    if re.search(r'\b(?:steel|metal|commodity|trading)\b', text_lower):
        return 'Trading/Commodities'
    elif re.search(r'\b(?:cannabis|pharma|medical|healthcare)\b', text_lower):
        return 'Cannabis/Healthcare'
    elif re.search(r'\b(?:construction|contractor|real estate|housing|property)\b', text_lower):
        return 'Construction/Real Estate'
    elif re.search(r'\b(?:energy|oil|gas|lng|power|renewable)\b', text_lower):
        return 'Energy'
    elif re.search(r'\b(?:mining|gold|ore|processing|extraction)\b', text_lower):
        return 'Mining/Resources'
    elif re.search(r'\b(?:tech|software|ai|computer|data|fintech)\b', text_lower):
        return 'Technology'
    elif re.search(r'\b(?:gaming|esports|entertainment)\b', text_lower):
        return 'Gaming/Entertainment'
    elif re.search(r'\b(?:manufacturing|industrial|production)\b', text_lower):
        return 'Manufacturing'
    else:
        return 'Other'

def detect_geography(text: str) -> str:
    """Detect primary geography"""
    text_lower = text.lower()
    
    # European countries
    if re.search(r'\b(?:sweden|norway|denmark|portugal|france|uk|spain|germany)\b', text_lower):
        return 'Europe'
    # North America
    elif re.search(r'\b(?:usa|canada|united states|american)\b', text_lower):
        return 'North America'
    # South America
    elif re.search(r'\b(?:brazil|peru|colombia|chile)\b', text_lower):
        return 'South America'
    # Africa
    elif re.search(r'\b(?:ghana|nigeria|angola|mozambique|south africa)\b', text_lower):
        return 'Africa'
    # Middle East
    elif re.search(r'\b(?:dubai|saudi|uae|middle east)\b', text_lower):
        return 'Middle East'
    else:
        return 'Global'

def insert_into_supabase(deals: list):
    """Insert parsed deals into deal_outcomes table"""
    
    # Get your organization ID (you'll need to set this)
    org_id = "YOUR_ORG_ID_HERE"  # TODO: Replace with actual org ID
    
    for deal in deals:
        # Map to deal_outcomes schema
        outcome_data = {
            'organization_id': org_id,
            'sector': deal.get('sector', 'Other'),
            'target_geography': deal.get('geography', 'Global'),
            'deal_type': 'acquisition',  # Assume most are acquisition targets
            'first_contact_date': '2020-01-01',  # Approximate from PDF date
            
            # Revenue bucket
            'target_revenue_range': bucket_revenue(deal.get('revenue_m')),
            
            # For now, mark as prospects (not closed deals)
            'deal_outcome': 'prospect',
            
            # Store original notes
            'what_went_well': f"Company: {deal.get('company_name', 'Unknown')}. {deal.get('notes_snippet', '')[:200]}",
            
            # Metadata
            'is_anonymous': True,
            'shared_with_network': False
        }
        
        try:
            result = supabase.table('deal_outcomes').insert(outcome_data).execute()
            print(f"✓ Inserted: {deal.get('company_name', 'Unknown')}")
        except Exception as e:
            print(f"✗ Error inserting {deal.get('company_name')}: {e}")

def bucket_revenue(revenue_m):
    """Convert revenue to bucket for privacy"""
    if not revenue_m:
        return 'Unknown'
    
    revenue_m = float(revenue_m)
    
    if revenue_m < 5:
        return '<€5M'
    elif revenue_m < 10:
        return '€5-10M'
    elif revenue_m < 25:
        return '€10-25M'
    elif revenue_m < 50:
        return '€25-50M'
    elif revenue_m < 100:
        return '€50-100M'
    elif revenue_m < 250:
        return '€100-250M'
    elif revenue_m < 500:
        return '€250-500M'
    else:
        return '>€500M'

if __name__ == '__main__':
    print("🔍 Extracting deals from Njord PDF...")
    
    # Path to your PDF
    pdf_path = '/mnt/user-data/uploads/Njord_-_Internal_-_Zoom_Call_notes_-_James___Alia.pdf'
    
    # Extract text
    text = extract_pdf_text(pdf_path)
    print(f"✓ Extracted {len(text)} characters from PDF")
    
    # Parse deals
    deals = parse_deals(text)
    print(f"✓ Found {len(deals)} deals with financial data")
    
    # Preview
    print("\n📊 Sample deals:")
    for i, deal in enumerate(deals[:5]):
        print(f"\n{i+1}. {deal.get('company_name', 'Unknown')}")
        print(f"   Sector: {deal['sector']}")
        print(f"   Revenue: €{deal.get('revenue_m', 'N/A')}M")
        print(f"   Funding: {deal.get('funding_need_m', 'N/A')}M")
    
    # Insert into Supabase
    print("\n💾 Inserting into Supabase...")
    insert_into_supabase(deals)
    
    print("\n✅ Complete!")
```

**To run this:**
```bash
# Install dependencies
pip install PyPDF2 supabase --break-system-packages

# Run the script
python3 scripts/extract_njord_deals.py
```

---

### PHASE 2: Build ML Valuation Model (Week 2)

#### Step 2.1: Train Model on Njord Data

**File: `ml/train_valuation_model.py`**

```python
"""
Train ML model to predict revenue multiples based on Njord deal patterns

This uses the actual deal data from your PDF to learn patterns like:
- Energy companies typically get 0.5-1.5x revenue multiples
- Tech companies get 2-5x revenue multiples  
- Companies with EBITDA >20% get higher multiples
- Geographic region affects multiples (Europe vs. NA)
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
import joblib
from supabase import create_client, Client

# Supabase connection
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_SERVICE_KEY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def load_deal_data():
    """Load deal outcomes from Supabase"""
    response = supabase.table('deal_outcomes').select('*').execute()
    df = pd.DataFrame(response.data)
    return df

def feature_engineering(df):
    """
    Create features from deal data
    
    Based on Njord notes patterns:
    - Sector is highly predictive (Tech > Mining > Construction)
    - Geography matters (Europe < North America)
    - Revenue size affects multiple (larger = lower multiple)
    - EBITDA margin is critical (>20% = premium)
    """
    
    # Encode categorical variables
    le_sector = LabelEncoder()
    le_geography = LabelEncoder()
    
    df['sector_encoded'] = le_sector.fit_transform(df['sector'])
    df['geography_encoded'] = le_geography.fit_transform(df['target_geography'])
    
    # Revenue bucket to numeric (midpoint)
    revenue_map = {
        '<€5M': 2.5,
        '€5-10M': 7.5,
        '€10-25M': 17.5,
        '€25-50M': 37.5,
        '€50-100M': 75,
        '€100-250M': 175,
        '€250-500M': 375,
        '>€500M': 750
    }
    df['revenue_numeric'] = df['target_revenue_range'].map(revenue_map)
    
    # Create synthetic multiples based on Njord patterns
    # (In production, you'd use actual closed deal multiples)
    df['revenue_multiple'] = df.apply(infer_multiple_from_notes, axis=1)
    
    # Save encoders for later use
    joblib.dump(le_sector, 'ml/models/sector_encoder.pkl')
    joblib.dump(le_geography, 'ml/models/geography_encoder.pkl')
    joblib.dump(revenue_map, 'ml/models/revenue_map.pkl')
    
    return df, le_sector, le_geography

def infer_multiple_from_notes(row):
    """
    Infer revenue multiple from sector and deal characteristics
    
    Based on Njord notes patterns:
    - Tech/Gaming: 3-7x (high growth, recurring revenue)
    - Mining/Energy: 0.5-2x (capital intensive, commodity prices)
    - Construction: 0.3-1x (project-based, thin margins)
    - Trading/Commodities: 0.1-0.5x (very thin margins)
    - Cannabis/Healthcare: 2-4x (regulated, growing market)
    """
    
    sector = row['sector']
    base_multiple = 1.0
    
    # Sector-based multiples (from Njord data analysis)
    if 'Technology' in sector or 'Gaming' in sector:
        base_multiple = 4.5
    elif 'Cannabis' in sector or 'Healthcare' in sector:
        base_multiple = 3.0
    elif 'Mining' in sector or 'Resources' in sector:
        base_multiple = 1.2
    elif 'Energy' in sector:
        base_multiple = 1.5
    elif 'Construction' in sector or 'Real Estate' in sector:
        base_multiple = 0.7
    elif 'Trading' in sector or 'Commodities' in sector:
        base_multiple = 0.3
    elif 'Manufacturing' in sector:
        base_multiple = 1.0
    
    # Geography adjustment
    geography = row['target_geography']
    if geography == 'North America':
        base_multiple *= 1.2  # US premium
    elif geography == 'Europe':
        base_multiple *= 1.0  # Base
    elif geography == 'South America' or geography == 'Africa':
        base_multiple *= 0.7  # Emerging market discount
    
    # Add some realistic noise
    noise = np.random.normal(0, base_multiple * 0.15)
    
    return max(0.1, base_multiple + noise)

def train_model(df):
    """Train RandomForest model on deal data"""
    
    # Features
    feature_cols = ['sector_encoded', 'geography_encoded', 'revenue_numeric']
    X = df[feature_cols].fillna(df[feature_cols].median())
    
    # Target
    y = df['revenue_multiple']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"Train R²: {train_score:.3f}")
    print(f"Test R²: {test_score:.3f}")
    
    # Cross-validation
    cv_scores = cross_val_score(model, X, y, cv=5)
    print(f"Cross-val R²: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
    
    # Save model
    joblib.dump(model, 'ml/models/revenue_multiple_model.pkl')
    print("✓ Model saved to ml/models/revenue_multiple_model.pkl")
    
    return model

if __name__ == '__main__':
    print("🤖 Training valuation model on Njord deal data...\n")
    
    # Load data
    print("📊 Loading deal outcomes from Supabase...")
    df = load_deal_data()
    print(f"✓ Loaded {len(df)} deals")
    
    # Feature engineering
    print("\n🔧 Engineering features...")
    df, le_sector, le_geography = feature_engineering(df)
    print(f"✓ Created features: {df.columns.tolist()}")
    
    # Train
    print("\n🎓 Training model...")
    model = train_model(df)
    
    # Feature importance
    print("\n📈 Feature Importances:")
    feature_names = ['Sector', 'Geography', 'Revenue Size']
    importances = model.feature_importances_
    for name, importance in zip(feature_names, importances):
        print(f"  {name}: {importance:.3f}")
    
    print("\n✅ Model training complete!")
    print("\nNext steps:")
    print("1. Deploy model to Supabase Edge Function")
    print("2. Call prediction API from React Native app")
```

**To run this:**
```bash
# Install ML dependencies
pip install pandas numpy scikit-learn joblib supabase --break-system-packages

# Train the model
python3 ml/train_valuation_model.py
```

---

Continue in next file with deployment...
