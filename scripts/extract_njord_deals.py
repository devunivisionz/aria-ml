"""
Extract structured deal data from Njord notes PDF
"""

import PyPDF2
import re
import json
from datetime import datetime

# ============================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================
SUPABASE_URL = "YOUR_SUPABASE_URL_HERE"
SUPABASE_KEY = "YOUR_SUPABASE_SERVICE_KEY_HERE"
PDF_PATH = r"C:\Users\Univisionz Win5\Desktop\Company Projects\Extra Files\Aria\Machine learning based on notes\test_deals.txt"

# ============================================
# TRY TO IMPORT SUPABASE (optional for now)
# ============================================
try:
    from supabase import create_client, Client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    SUPABASE_ENABLED = True
except Exception as e:
    print(f"⚠️ Supabase not connected: {e}")
    print("Will save to JSON file instead.\n")
    SUPABASE_ENABLED = False

# ============================================
# EXTRACTION FUNCTIONS
# ============================================


def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from file (PDF or TXT)"""
    try:
        # Check if it's a text file
        if pdf_path.endswith('.txt'):
            with open(pdf_path, 'r', encoding='utf-8') as file:
                return file.read()
        
        # Otherwise try PDF
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- PAGE {i+1} ---\n"
                    text += page_text
            return text
    except FileNotFoundError:
        print(f"❌ File not found at: {pdf_path}")
        return ""

def detect_sector(text: str) -> str:
    """Detect sector from keywords"""
    text_lower = text.lower()
    
    if re.search(r'\b(?:steel|metal|commodity|trading)\b', text_lower):
        return 'Trading/Commodities'
    elif re.search(r'\b(?:cannabis|pharma|medical|healthcare|cbd)\b', text_lower):
        return 'Cannabis/Healthcare'
    elif re.search(r'\b(?:construction|contractor|real estate|housing|property|cntnr)\b', text_lower):
        return 'Construction/Real Estate'
    elif re.search(r'\b(?:energy|oil|gas|lng|power|renewable|solar)\b', text_lower):
        return 'Energy'
    elif re.search(r'\b(?:mining|gold|ore|processing|extraction|inca)\b', text_lower):
        return 'Mining/Resources'
    elif re.search(r'\b(?:tech|software|ai|computer|data|fintech|saas)\b', text_lower):
        return 'Technology'
    elif re.search(r'\b(?:gaming|esports|entertainment)\b', text_lower):
        return 'Gaming/Entertainment'
    elif re.search(r'\b(?:manufacturing|industrial|production|paper)\b', text_lower):
        return 'Manufacturing'
    else:
        return 'Other'

def detect_geography(text: str) -> str:
    """Detect primary geography"""
    text_lower = text.lower()
    
    if re.search(r'\b(?:sweden|norway|denmark|portugal|france|uk|spain|germany|europe)\b', text_lower):
        return 'Europe'
    elif re.search(r'\b(?:usa|canada|united states|american|nasdaq)\b', text_lower):
        return 'North America'
    elif re.search(r'\b(?:brazil|peru|colombia|chile|latin)\b', text_lower):
        return 'South America'
    elif re.search(r'\b(?:ghana|nigeria|angola|mozambique|south africa|africa)\b', text_lower):
        return 'Africa'
    elif re.search(r'\b(?:dubai|saudi|uae|middle east)\b', text_lower):
        return 'Middle East'
    else:
        return 'Global'

def bucket_revenue(revenue_m):
    """Convert revenue to bucket for privacy"""
    if not revenue_m:
        return 'Unknown'
    
    try:
        revenue_m = float(revenue_m)
    except:
        return 'Unknown'
    
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

def parse_deals(text: str) -> list:
    """Parse deals from Njord notes"""
    deals = []
    
    # Split by page markers
    pages = re.split(r'--- PAGE \d+ ---', text)
    
    for page_num, section in enumerate(pages):
        section = section.strip()
        if len(section) < 50:
            continue
        
        deal = {
            'page': page_num,
            'company_name': None,
            'revenue_m': None,
            'funding_need_m': None,
            'sector': None,
            'geography': None,
            'ebitda_info': None,
            'notes_snippet': section[:500]
        }
        
        # Extract company name (look for capitalized words at start or after common patterns)
        company_patterns = [
            r'^([A-Z][A-Za-z0-9\s&\.\-]+?)(?:\s{2,}|\n)',
            r'(?:Company|Client|Deal):\s*([A-Za-z0-9\s&\.\-]+)',
            r'(?:Call with|Meeting with|Re:)\s*([A-Za-z0-9\s&\.\-]+)',
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, section[:300])
            if match:
                name = match.group(1).strip()
                if len(name) > 2 and len(name) < 50:
                    deal['company_name'] = name
                    break
        
        # Extract revenue
        revenue_patterns = [
            r'(?:Revenue|Turnover|Annual|Sales)[:\s]*[\$€]?(\d+(?:\.\d+)?)\s*(?:M|Million|MM)',
            r'[\$€](\d+(?:\.\d+)?)\s*(?:M|Million)\s*(?:revenue|turnover)',
            r'(\d+(?:\.\d+)?)\s*(?:M|Million)\s*(?:in revenue|annual)',
        ]
        
        for pattern in revenue_patterns:
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                deal['revenue_m'] = float(match.group(1))
                break
        
        # Extract funding need
        funding_patterns = [
            r'(?:Looking for|Need|Seeking|Raise|Raising)[:\s]*[\$€]?(\d+(?:-\d+)?)\s*(?:M|Million)',
            r'[\$€](\d+(?:-\d+)?)\s*(?:M|Million)\s*(?:funding|raise|loan|debt)',
        ]
        
        for pattern in funding_patterns:
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                deal['funding_need_m'] = match.group(1)
                break
        
        # Extract EBITDA
        ebitda_match = re.search(r'EBIT?DA[:\s]*(\d+(?:\.\d+)?)[%M]', section, re.IGNORECASE)
        if ebitda_match:
            deal['ebitda_info'] = ebitda_match.group(0)
        
        # Detect sector and geography
        deal['sector'] = detect_sector(section)
        deal['geography'] = detect_geography(section)
        
        # Only keep deals with some useful info
        if deal['company_name'] or deal['revenue_m'] or deal['funding_need_m']:
            deals.append(deal)
    
    return deals

def save_to_json(deals: list, filename: str = "extracted_deals.json"):
    """Save deals to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(deals, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved {len(deals)} deals to {filename}")

def insert_into_supabase(deals: list):
    """Insert parsed deals into Supabase"""
    if not SUPABASE_ENABLED:
        print("Supabase not enabled, skipping...")
        return
    
    org_id = "YOUR_ORG_ID_HERE"  # TODO: Replace
    
    for deal in deals:
        outcome_data = {
            'organization_id': org_id,
            'sector': deal.get('sector', 'Other'),
            'target_geography': deal.get('geography', 'Global'),
            'deal_type': 'acquisition',
            'first_contact_date': '2020-01-01',
            'target_revenue_range': bucket_revenue(deal.get('revenue_m')),
            'deal_outcome': 'prospect',
            'what_went_well': f"Company: {deal.get('company_name', 'Unknown')}",
            'is_anonymous': True,
            'shared_with_network': False
        }
        
        try:
            result = supabase.table('deal_outcomes').insert(outcome_data).execute()
            print(f"✓ Inserted: {deal.get('company_name', 'Unknown')}")
        except Exception as e:
            print(f"✗ Error: {e}")

# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == '__main__':
    print("=" * 50)
    print("🔍 NJORD DEAL EXTRACTOR")
    print("=" * 50)
    
    # Extract text
    print(f"\n📄 Reading PDF: {PDF_PATH}")
    text = extract_pdf_text(PDF_PATH)
    
    if not text:
        print("\n❌ Could not read PDF. Check the path.")
        exit(1)
    
    print(f"✓ Extracted {len(text):,} characters from PDF")
    
    # Parse deals
    print("\n🔍 Parsing deals...")
    deals = parse_deals(text)
    print(f"✓ Found {len(deals)} potential deals")
    
    # Preview
    print("\n" + "=" * 50)
    print("📊 EXTRACTED DEALS:")
    print("=" * 50)
    
    for i, deal in enumerate(deals[:10]):  # Show first 10
        print(f"\n{i+1}. {deal.get('company_name') or 'Unknown Company'}")
        print(f"   Page: {deal['page']}")
        print(f"   Sector: {deal['sector']}")
        print(f"   Geography: {deal['geography']}")
        if deal['revenue_m']:
            print(f"   Revenue: €{deal['revenue_m']}M")
        if deal['funding_need_m']:
            print(f"   Funding Need: €{deal['funding_need_m']}M")
        if deal['ebitda_info']:
            print(f"   EBITDA: {deal['ebitda_info']}")
    
    if len(deals) > 10:
        print(f"\n... and {len(deals) - 10} more deals")
    
    # Save to JSON
    print("\n" + "=" * 50)
    print("💾 SAVING DATA")
    print("=" * 50)
    save_to_json(deals)
    
    # Insert to Supabase if enabled
    if SUPABASE_ENABLED:
        print("\n📤 Inserting into Supabase...")
        insert_into_supabase(deals)
    
    print("\n" + "=" * 50)
    print("✅ COMPLETE!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Review extracted_deals.json")
    print("2. Update Supabase credentials if needed")
    print("3. Run train_valuation_model.py")