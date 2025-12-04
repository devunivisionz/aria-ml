# 📘 FOR KANAV: ML Integration Part 3 - Testing & Examples

---

## 🧪 TESTING THE ML INTEGRATION

### Test Case 1: Technology Company (High Multiple)

**Company Profile:**
- Name: "CloudTech Solutions"
- Sector: Technology
- Industry: SaaS
- Revenue: $50M
- Geography: United States
- Employees: 200

**Expected Prediction** (based on Njord patterns):
```json
{
  "revenue_multiple": {
    "expected": 5.4,
    "p25": 4.05,
    "p75": 6.75
  },
  "ebitda_multiple": {
    "expected": 10.8,
    "p25": 8.1,
    "p75": 13.5
  },
  "ev_range": [202500000, 337500000],
  "confidence": 0.85,
  "key_drivers": [
    { "factor": "Technology sector premium", "impact": "3.5" },
    { "factor": "United States market adjustment", "impact": "0.9" }
  ]
}
```

**Why these numbers?**
- Base multiple for Tech: 4.5x (from ESports/Gaming deals in Njord)
- US geography bonus: +20% → 5.4x
- EBITDA multiple: 2x revenue multiple → 10.8x
- EV range: $50M × 4.05x to $50M × 6.75x = $202.5M - $337.5M

---

### Test Case 2: Mining Company (Low Multiple)

**Company Profile:**
- Name: "Andean Gold Processing"
- Sector: Mining
- Industry: Gold Processing
- Revenue: $25M
- Geography: Peru
- Employees: 450

**Expected Prediction** (based on INCA One deal):
```json
{
  "revenue_multiple": {
    "expected": 0.84,
    "p25": 0.63,
    "p75": 1.05
  },
  "ebitda_multiple": {
    "expected": 1.43,
    "p25": 1.07,
    "p75": 1.78
  },
  "ev_range": [15750000, 26250000],
  "confidence": 0.7,
  "key_drivers": [
    { "factor": "Mining/Resources sector premium", "impact": "0.2" },
    { "factor": "Peru market adjustment", "impact": "-0.36" }
  ]
}
```

**Why these numbers?**
- Base multiple for Mining: 1.2x (from INCA One deal in Njord)
- Peru (emerging market) discount: -30% → 0.84x
- EBITDA multiple: 1.7x revenue multiple → 1.43x
- EV range: $25M × 0.63x to $25M × 1.05x = $15.75M - $26.25M

---

### Test Case 3: Construction Company (Medium Multiple)

**Company Profile:**
- Name: "Nordic Build Group"
- Sector: Construction
- Industry: General Contractor
- Revenue: $100M
- Geography: Sweden
- Employees: 635

**Expected Prediction** (based on IBG Global + Nordic Paper deals):
```json
{
  "revenue_multiple": {
    "expected": 0.77,
    "p25": 0.58,
    "p75": 0.96
  },
  "ebitda_multiple": {
    "expected": 1.31,
    "p25": 0.98,
    "p75": 1.63
  },
  "ev_range": [58000000, 96000000],
  "confidence": 0.65,
  "key_drivers": [
    { "factor": "Construction/Real Estate sector premium", "impact": "-0.3" },
    { "factor": "Sweden market adjustment", "impact": "0.07" }
  ]
}
```

**Why these numbers?**
- Base multiple for Construction: 0.7x (from IBG Global deal)
- Sweden (Nordic) bonus: +10% → 0.77x
- EBITDA multiple: 1.7x revenue multiple → 1.31x
- EV range: $100M × 0.58x to $100M × 0.96x = $58M - $96M

---

## 🎮 HOW TO TEST IN THE APP

### Step-by-Step Testing Process

**1. Insert Test Companies into Supabase**

```sql
-- Insert test tech company
INSERT INTO entities (
  name,
  domain,
  industry,
  sector,
  country,
  revenue,
  employee_count,
  founded_year
) VALUES (
  'CloudTech Solutions',
  'cloudtech.example.com',
  'SaaS',
  'Technology',
  'United States',
  50000000,
  200,
  2015
) RETURNING id;

-- Insert test mining company
INSERT INTO entities (
  name,
  domain,
  industry,
  sector,
  country,
  revenue,
  employee_count,
  founded_year
) VALUES (
  'Andean Gold Processing',
  'andeangold.example.pe',
  'Gold Processing',
  'Mining/Resources',
  'Peru',
  25000000,
  450,
  2010
) RETURNING id;

-- Insert test construction company
INSERT INTO entities (
  name,
  domain,
  industry,
  sector,
  country,
  revenue,
  employee_count,
  founded_year
) VALUES (
  'Nordic Build Group',
  'nordicbuild.example.se',
  'General Contractor',
  'Construction/Real Estate',
  'Sweden',
  100000000,
  635,
  2005
) RETURNING id;
```

**2. Create Mandate Matches**

```sql
-- Get a mandate ID from your mandates table
SELECT id FROM mandates LIMIT 1;

-- Insert mandate matches for test companies
INSERT INTO mandate_matches (
  mandate_id,
  entity_id,
  fit_score,
  timing_score,
  overall_score
) VALUES 
  ('YOUR_MANDATE_ID', (SELECT id FROM entities WHERE name = 'CloudTech Solutions'), 85, 75, 80),
  ('YOUR_MANDATE_ID', (SELECT id FROM entities WHERE name = 'Andean Gold Processing'), 70, 60, 65),
  ('YOUR_MANDATE_ID', (SELECT id FROM entities WHERE name = 'Nordic Build Group'), 80, 70, 75);
```

**3. Test in React Native App**

Open the app and:

1. **Navigate to Mandate Details**
   - Should see 3 new test companies

2. **Open CloudTech Solutions**
   - Tap entity card
   - Scroll to valuation section
   - Tap "🤖 Generate AI Valuation"
   - Wait 2-3 seconds
   - Should see: Revenue Multiple ~5.4x, Confidence 85%

3. **Open Andean Gold Processing**
   - Tap entity card
   - Tap "🤖 Generate AI Valuation"
   - Should see: Revenue Multiple ~0.84x, Confidence 70%

4. **Open Nordic Build Group**
   - Tap entity card
   - Tap "🤖 Generate AI Valuation"
   - Should see: Revenue Multiple ~0.77x, Confidence 65%

**4. Verify Predictions Stored**

```sql
-- Check valuation_predictions table
SELECT 
  e.name,
  vp.revenue_multiple_expected,
  vp.ebitda_multiple_expected,
  vp.confidence_score,
  vp.created_at
FROM valuation_predictions vp
JOIN entities e ON e.id = vp.entity_id
ORDER BY vp.created_at DESC
LIMIT 10;
```

Expected output:
```
name                      | revenue_multiple | ebitda_multiple | confidence
--------------------------|------------------|-----------------|------------
CloudTech Solutions       | 5.40             | 10.80          | 0.85
Andean Gold Processing    | 0.84             | 1.43           | 0.70
Nordic Build Group        | 0.77             | 1.31           | 0.65
```

---

## 🐛 TROUBLESHOOTING

### Issue 1: "No valuation generated"

**Symptoms:**
- Tap "Generate AI Valuation" button
- Nothing happens or error message

**Debugging:**
```bash
# Check Edge Function logs
supabase functions logs predict-valuation

# Test Edge Function directly
curl -X POST https://YOUR_PROJECT.supabase.co/functions/v1/predict-valuation \
  -H "Authorization: Bearer YOUR_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"ENTITY_ID","mandate_id":"MANDATE_ID"}'
```

**Common causes:**
- Edge function not deployed
- Missing entity data (no revenue, sector, etc.)
- Wrong Supabase URL/keys

**Fix:**
```bash
# Redeploy edge function
supabase functions deploy predict-valuation

# Check entity has required fields
SELECT id, name, industry, sector, country, revenue 
FROM entities 
WHERE id = 'ENTITY_ID';
```

---

### Issue 2: "Predictions seem wrong"

**Symptoms:**
- All companies get same multiple
- Tech companies get 0.5x (should be 4-5x)
- Mining companies get 10x (should be 1-2x)

**Debugging:**
```typescript
// Add console.log to Edge Function
console.log('Features:', features)
console.log('Base multiple:', baseRevMultiple)
console.log('Final prediction:', prediction)
```

**Common causes:**
- Sector not being detected correctly
- Revenue not being passed
- Logic error in prediction function

**Fix:**
```typescript
// Ensure sector mapping is correct
if (sector.toLowerCase().includes('tech') || 
    sector.toLowerCase().includes('software')) {
  baseRevMultiple = 4.5
}

// Log to debug
console.log(`Sector "${sector}" mapped to multiple ${baseRevMultiple}`)
```

---

### Issue 3: "Confidence always 0.7"

**Symptoms:**
- All predictions show 70% confidence
- No variation between companies

**Cause:**
Using default confidence instead of sector-specific

**Fix:**
```typescript
// Update confidence based on data quality
let confidence = 0.7 // default

// Higher confidence for well-represented sectors
if (sector.includes('Technology')) confidence = 0.85
else if (sector.includes('Mining')) confidence = 0.7
else if (sector.includes('Construction')) confidence = 0.65

// Adjust for data completeness
const hasRevenue = revenue_m !== null
const hasEmployees = employees !== null
const hasGrowthSignals = growth_signals?.length > 0

if (hasRevenue && hasEmployees && hasGrowthSignals) {
  confidence += 0.1 // Boost for complete data
}
```

---

### Issue 4: "React Native app crashes when opening valuation"

**Symptoms:**
- App crashes when navigating to ValuationScreen
- Error: "Cannot read property 'expected' of undefined"

**Cause:**
ValuationSummary is null but screen tries to access properties

**Fix:**
```typescript
// Add null checks in ValuationScreen
if (loading) {
  return <LoadingView />
}

if (error || !summary) {
  return (
    <View style={styles.centered}>
      <Text style={styles.errorText}>
        {error || 'Valuation not available'}
      </Text>
      <TouchableOpacity 
        style={styles.retryButton}
        onPress={generateNewValuation}
      >
        <Text>Generate Prediction</Text>
      </TouchableOpacity>
    </View>
  )
}

// Only render if summary exists
return (
  <ScrollView>
    <Text>{summary.revenue_multiple.expected}x</Text>
    ...
  </ScrollView>
)
```

---

## 📊 UNDERSTANDING THE NJORD DATA INFLUENCE

### How Each Deal Influences Predictions

**1. ESports Entertainment Group (Njord page 8)**
```
Sector: Gaming/Entertainment
Seeking: $30-50M for acquisitions

ML Learning:
→ Gaming companies seek 0.4-1.0x revenue in funding
→ Implies valuation of 4-5x revenue
→ Used to set base_multiple = 5.0 for Gaming sector
```

**2. INCA One (Njord page 9)**
```
Sector: Mining/Resources
Revenue: $21M
EBITDA: $18-20M
Seeking: $10-15M

ML Learning:
→ Mining companies have 0.5-0.7x revenue funding needs
→ EBITDA nearly equals revenue (unusual, high margin)
→ Implies valuation of 1-1.5x revenue
→ Used to set base_multiple = 1.2 for Mining
```

**3. CNTNR (Njord page 10)**
```
Sector: Construction/Real Estate
Revenue: $70M
EBITDA: 22%
Seeking: $5-18M

ML Learning:
→ Construction seeks 0.07-0.26x revenue in funding
→ But high EBITDA (22%) is premium
→ Implies valuation of 0.5-1.0x revenue
→ Used to set base_multiple = 0.7 for Construction
→ Added EBITDA boost: if margin > 20%, multiply by 1.3
```

**4. Nordic Paper (Njord page 7)**
```
Sector: Manufacturing
Revenue: ~$130M
Seeking: $50-100M for acquisitions

ML Learning:
→ Manufacturing companies seek 0.4-0.8x revenue
→ Implies valuation around 1x revenue
→ Used to set base_multiple = 1.0 for Manufacturing
```

**5. Trasteel (Njord page 1)**
```
Sector: Trading/Commodities
Revenue: €500M
Seeking: €20-30M trade finance

ML Learning:
→ Trading companies seek 0.04-0.06x revenue
→ Implies very low multiples (thin margins)
→ Used to set base_multiple = 0.3 for Trading
```

### Geographic Adjustments from Njord

**North American Premium (+20%)**
- Based on: ESports (USA), Heritage Cannabis (Canada)
- Reasoning: Larger market, higher valuations, more liquidity

**Nordic Premium (+10%)**
- Based on: Nordic Paper (Sweden)
- Reasoning: Stable economy, well-run companies, Nordic premium

**Emerging Market Discount (-30%)**
- Based on: INCA One (Peru), Prosfetur (Brazil), IBG Global (Ghana/Angola)
- Reasoning: Country risk, currency risk, lower liquidity

---

## 📈 EXPECTED RESULTS

After implementing everything, you should see:

### In Supabase Dashboard

**deal_outcomes table:**
- 25+ rows with company data from Njord notes
- Sectors: Trading, Cannabis, Construction, Energy, Mining, Tech, Gaming
- Revenue ranges: €5M to €500M+

**valuation_predictions table:**
- Predictions for every entity you tested
- Revenue multiples: 0.3x to 7.0x depending on sector
- EBITDA multiples: 0.5x to 14x
- Confidence scores: 60% to 90%

### In React Native App

**Entity Details Screen:**
- "🤖 Generate AI Valuation" button appears
- Button works when tapped
- Success message after generation

**Valuation Screen:**
- Beautiful visualization of predictions
- Confidence score prominently displayed
- Revenue multiple with range bars
- EBITDA multiple with range bars
- Enterprise value range
- Key drivers listed with impact

**User Experience:**
1. User views "TechStartup Inc" (Technology, USA, $30M revenue)
2. Taps "Generate AI Valuation"
3. Sees loading state (2 seconds)
4. Prediction appears:
   - Revenue Multiple: 4.8x (expected), 3.6x-6.0x (range)
   - EBITDA Multiple: 9.6x (expected), 7.2x-12.0x (range)
   - Enterprise Value: $108M - $180M
   - Confidence: 85%
   - Key Drivers:
     * Technology sector premium: +3.5x
     * United States market: +0.9x

---

## ✅ FINAL CHECKLIST

### Data Setup
- [ ] Njord PDF extracted (25+ deals)
- [ ] Deals inserted into deal_outcomes table
- [ ] Sector distribution looks good (Tech, Mining, Construction, etc.)
- [ ] Geography distribution looks good (Europe, NA, SA, Africa)

### ML Model
- [ ] Python training script runs without errors
- [ ] Model accuracy >0.7 R²
- [ ] Feature importances make sense (Sector > Geography > Revenue)
- [ ] Model files saved (.pkl files exist)

### API Deployment
- [ ] Edge Function deployed to Supabase
- [ ] Function appears in Supabase dashboard
- [ ] curl test returns prediction
- [ ] Prediction stored in valuation_predictions table

### React Native Integration
- [ ] ValuationScreen has "Generate" button
- [ ] EntityDetailsScreen has valuation card
- [ ] Tapping button calls API
- [ ] Loading states work
- [ ] Error handling works
- [ ] Success messages appear

### Testing
- [ ] Tech company predicts 4-7x multiple ✓
- [ ] Mining company predicts 1-2x multiple ✓
- [ ] Construction company predicts 0.5-1x multiple ✓
- [ ] Confidence varies by sector ✓
- [ ] Key drivers are meaningful ✓

### Production Ready
- [ ] Error handling for network failures
- [ ] Retry logic for failed predictions
- [ ] User-friendly error messages
- [ ] Analytics tracking (optional)
- [ ] Documentation for future updates

---

## 🎓 WHAT KANAV LEARNED

By completing this implementation, Kanav now knows:

1. **How to extract structured data from PDFs** using Python
2. **How to train ML models** on real business data
3. **How to deploy ML as an API** using Supabase Edge Functions
4. **How to integrate ML predictions** into React Native apps
5. **How deal patterns** vary by sector, geography, and size
6. **How to explain predictions** with key drivers for users

**Most importantly:** Kanav understands that the **Njord notes contain real deal intelligence** that makes predictions **10x more valuable** than generic formulas.

---

## 🚀 NEXT STEPS FOR KANAV

### Immediate (This Week)
1. Run the extraction script
2. Verify 25+ deals in database
3. Test predictions on 5 companies
4. Show results to team

### Short-term (Next Month)
1. Add more deals as they close
2. Retrain model monthly
3. Track prediction accuracy vs. actual outcomes
4. Improve confidence scoring

### Long-term (Next Quarter)
1. Add EBITDA prediction model
2. Add timing prediction model
3. Add deal probability scoring
4. Build recommendation engine

**The foundation is ready. Now go execute.** 💪

