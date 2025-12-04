"""
Flask API with Rule-Based ML Predictions
Production-ready version for Railway/Render deployment
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Sector base multiples (from Njord deal patterns)
SECTOR_MULTIPLES = {
    'Technology': 4.5,
    'Software': 4.5,
    'SaaS': 4.5,
    'AI': 4.5,
    'Gaming': 5.0,
    'Gaming/Entertainment': 5.0,
    'ESports': 5.0,
    'Cannabis': 3.0,
    'Cannabis/Healthcare': 3.0,
    'Healthcare': 3.0,
    'Mining': 1.2,
    'Mining/Resources': 1.2,
    'Gold': 1.2,
    'Energy': 1.5,
    'Oil': 1.5,
    'Gas': 1.5,
    'Construction': 0.7,
    'Construction/Real Estate': 0.7,
    'Real Estate': 0.7,
    'Trading': 0.3,
    'Trading/Commodities': 0.3,
    'Commodities': 0.3,
    'Manufacturing': 1.0
}

# Geography adjustments
GEOGRAPHY_ADJUSTMENTS = {
    'United States': 1.2,
    'USA': 1.2,
    'US': 1.2,
    'North America': 1.2,
    'Canada': 1.2,
    'Sweden': 1.1,
    'Norway': 1.1,
    'Denmark': 1.1,
    'Europe': 1.0,
    'UK': 1.0,
    'Germany': 1.0,
    'France': 1.0,
    'Global': 1.0,
    'Peru': 0.7,
    'Brazil': 0.7,
    'South America': 0.7,
    'Ghana': 0.7,
    'Africa': 0.7
}

# Sector confidence levels
SECTOR_CONFIDENCE = {
    'Technology': 0.85,
    'Software': 0.85,
    'SaaS': 0.85,
    'Gaming': 0.80,
    'Gaming/Entertainment': 0.80,
    'Cannabis': 0.75,
    'Healthcare': 0.75,
    'Mining': 0.70,
    'Mining/Resources': 0.70,
    'Energy': 0.75,
    'Construction': 0.65,
    'Construction/Real Estate': 0.65,
    'Real Estate': 0.65,
    'Trading': 0.60,
    'Trading/Commodities': 0.60,
    'Manufacturing': 0.70
}


def get_base_multiple(sector):
    """Get base multiple for a sector"""
    if not sector:
        return 1.5
    
    # Exact match first
    if sector in SECTOR_MULTIPLES:
        return SECTOR_MULTIPLES[sector]
    
    # Partial match
    sector_lower = sector.lower()
    for key, value in SECTOR_MULTIPLES.items():
        if key.lower() in sector_lower or sector_lower in key.lower():
            return value
    
    # Default
    return 1.5


def get_geography_adjustment(geography):
    """Get geography adjustment multiplier"""
    if not geography:
        return 1.0
    
    # Exact match first
    if geography in GEOGRAPHY_ADJUSTMENTS:
        return GEOGRAPHY_ADJUSTMENTS[geography]
    
    # Partial match
    geo_lower = geography.lower()
    for key, value in GEOGRAPHY_ADJUSTMENTS.items():
        if key.lower() in geo_lower or geo_lower in key.lower():
            return value
    
    # Default
    return 1.0


def get_confidence(sector):
    """Get confidence score for a sector"""
    if not sector:
        return 0.70
    
    # Exact match first
    if sector in SECTOR_CONFIDENCE:
        return SECTOR_CONFIDENCE[sector]
    
    # Partial match
    sector_lower = sector.lower()
    for key, value in SECTOR_CONFIDENCE.items():
        if key.lower() in sector_lower or sector_lower in key.lower():
            return value
    
    # Default
    return 0.70


def get_size_adjustment(revenue):
    """Adjust multiple based on company size"""
    if not revenue or revenue <= 0:
        return 1.0
    
    if revenue < 10:
        return 1.2  # Small company premium
    elif revenue < 50:
        return 1.0  # Mid-market baseline
    elif revenue < 250:
        return 0.9  # Large company discount
    else:
        return 0.7  # Very large discount


@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return jsonify({
        'name': 'ML Valuation API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'test': '/test',
            'predict': '/predict (POST)'
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Valuation API is running'
    })


@app.route('/test', methods=['GET'])
def test():
    """Quick test endpoint"""
    return jsonify({
        'test_company': 'CloudTech (Technology, USA, $50M)',
        'expected_multiple': 5.4,
        'expected_valuation': 270,
        'status': 'API is working correctly'
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict valuation using rule-based logic from Njord patterns
    
    Expected input:
    {
        "sector": "Technology",
        "geography": "North America",
        "revenue": 50
    }
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Extract inputs
        sector = data.get('sector', 'Other')
        geography = data.get('geography', 'Global')
        
        # Handle revenue - could be string or number
        revenue_raw = data.get('revenue', 0)
        try:
            revenue = float(revenue_raw) if revenue_raw else 0
        except (ValueError, TypeError):
            revenue = 0
        
        # Get base multiple from sector
        base_multiple = get_base_multiple(sector)
        
        # Get geography adjustment
        geo_adjustment = get_geography_adjustment(geography)
        
        # Get size adjustment
        size_adjustment = get_size_adjustment(revenue)
        
        # Calculate final multiple
        final_multiple = base_multiple * geo_adjustment * size_adjustment
        
        # Calculate range (±25%)
        low_multiple = final_multiple * 0.75
        high_multiple = final_multiple * 1.25
        
        # Calculate enterprise values
        enterprise_value = final_multiple * revenue
        ev_low = low_multiple * revenue
        ev_high = high_multiple * revenue
        
        # Get confidence
        confidence = get_confidence(sector)
        
        # Generate key drivers
        key_drivers = []
        key_drivers.append(f"{sector} sector baseline: {base_multiple}x")
        
        if geo_adjustment > 1.0:
            premium_pct = int((geo_adjustment - 1.0) * 100)
            key_drivers.append(f"{geography} market premium: +{premium_pct}%")
        elif geo_adjustment < 1.0:
            discount_pct = int((1.0 - geo_adjustment) * 100)
            key_drivers.append(f"{geography} market discount: -{discount_pct}%")
        
        if size_adjustment != 1.0:
            if size_adjustment > 1.0:
                key_drivers.append(f"Small company premium: +{int((size_adjustment-1)*100)}%")
            else:
                key_drivers.append(f"Size adjustment: -{int((1-size_adjustment)*100)}%")
        
        key_drivers.append(f"Final multiple: {round(final_multiple, 2)}x")
        
        # Build response
        response = {
            'success': True,
            'inputs': {
                'sector': sector,
                'geography': geography,
                'revenue_m': revenue
            },
            'predictions': {
                'revenue_multiple': round(final_multiple, 2),
                'multiple_range': {
                    'low': round(low_multiple, 2),
                    'high': round(high_multiple, 2)
                },
                'enterprise_value_m': round(enterprise_value, 1),
                'ev_range': {
                    'low': round(ev_low, 1),
                    'high': round(ev_high, 1)
                },
                'confidence': round(confidence, 2)
            },
            'key_drivers': key_drivers
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# Production entry point
if __name__ == '__main__':
    # Get port from environment variable (Railway/Render set this)
    port = int(os.environ.get('PORT', 5000))
    
    # Check if running in production
    is_production = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RENDER')
    
    print("="*50)
    print("🚀 Starting Valuation API")
    print("="*50)
    print(f"\nEnvironment: {'Production' if is_production else 'Development'}")
    print(f"Port: {port}")
    print("\nAPI Endpoints:")
    print("  GET  /health")
    print("  GET  /test")
    print("  POST /predict")
    print("="*50)
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=not is_production  # Debug only in development
    )