# 🧬 DEAL GENOME - REACT NATIVE IMPLEMENTATION
## Complete Code for aria-cortex-strategic-enhancement-plan.md Features

---

## 📋 PART 1: EXTENDED SUPABASE SCHEMA

### Run this SQL in Supabase SQL Editor

```sql
-- ============================================
-- DEAL GENOME SCHEMA EXTENSION
-- ============================================

-- Deal Outcomes Database
CREATE TABLE deal_outcomes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL,
  entity_id UUID REFERENCES entities(id),
  mandate_id UUID REFERENCES mandates(id),
  
  -- Deal basics
  sector TEXT NOT NULL,
  subsector TEXT,
  target_revenue_range TEXT NOT NULL,
  target_geography TEXT NOT NULL,
  deal_type TEXT NOT NULL,
  
  -- Deal process
  first_contact_date DATE NOT NULL,
  loi_date DATE,
  close_date DATE,
  deal_outcome TEXT NOT NULL,
  
  -- Deal terms (bucketed for privacy)
  revenue_multiple_bucket TEXT,
  ebitda_multiple_bucket TEXT,
  equity_percentage_bucket TEXT,
  debt_percentage_bucket TEXT,
  
  -- Deal dynamics
  competitive_situation TEXT,
  seller_motivation TEXT,
  diligence_findings JSONB,
  
  -- Outcome metrics
  actual_revenue_growth_y1 NUMERIC,
  actual_ebitda_margin_y1 NUMERIC,
  integration_success_score INTEGER,
  
  -- Learning
  signals_present JSONB,
  red_flags_present JSONB,
  relationship_quality TEXT,
  what_went_well TEXT,
  what_went_wrong TEXT,
  would_do_again BOOLEAN,
  
  -- Privacy
  is_anonymous BOOLEAN DEFAULT true,
  shared_with_network BOOLEAN DEFAULT false,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Relationships tracking
CREATE TABLE relationships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_contact_id UUID REFERENCES contacts(id),
  target_contact_id UUID REFERENCES contacts(id),
  
  relationship_type TEXT,
  strength INTEGER CHECK (strength >= 0 AND strength <= 100),
  last_interaction TIMESTAMPTZ,
  interaction_count INTEGER DEFAULT 0,
  successful_intros INTEGER DEFAULT 0,
  total_intro_requests INTEGER DEFAULT 0,
  
  -- Context
  how_they_know TEXT,
  metadata JSONB,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Intro paths and tracking
CREATE TABLE intro_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  requester_user_id UUID NOT NULL,
  target_contact_id UUID REFERENCES contacts(id),
  mandate_match_id UUID REFERENCES mandate_matches(id),
  
  -- Path
  intro_path JSONB, -- Array of contact IDs
  path_strength INTEGER,
  
  -- Status
  status TEXT DEFAULT 'pending',
  requested_at TIMESTAMPTZ DEFAULT NOW(),
  intro_made_at TIMESTAMPTZ,
  meeting_scheduled_at TIMESTAMPTZ,
  
  -- Outcome
  meeting_happened BOOLEAN DEFAULT false,
  deal_progressed BOOLEAN DEFAULT false,
  
  -- Message
  intro_message TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Outreach campaigns
CREATE TABLE outreach_campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mandate_id UUID REFERENCES mandates(id),
  name TEXT NOT NULL,
  
  target_entity_ids UUID[], -- Array of entity IDs
  
  status TEXT DEFAULT 'draft',
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  launched_at TIMESTAMPTZ
);

-- Outreach activities
CREATE TABLE outreach_activities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id UUID REFERENCES outreach_campaigns(id),
  entity_id UUID REFERENCES entities(id),
  contact_id UUID REFERENCES contacts(id),
  
  sequence_step INTEGER DEFAULT 1,
  channel TEXT, -- email, linkedin, call
  message TEXT,
  
  sent_at TIMESTAMPTZ,
  opened_at TIMESTAMPTZ,
  replied_at TIMESTAMPTZ,
  meeting_booked BOOLEAN DEFAULT false,
  
  metadata JSONB,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Deal rooms for collaboration
CREATE TABLE deal_rooms (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mandate_match_id UUID REFERENCES mandate_matches(id),
  
  members UUID[], -- Array of user IDs
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Deal room activities
CREATE TABLE deal_room_activities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  deal_room_id UUID REFERENCES deal_rooms(id),
  user_id UUID NOT NULL,
  
  activity_type TEXT NOT NULL, -- note, comment, document, task, status_change
  content JSONB,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Valuation predictions
CREATE TABLE valuation_predictions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  entity_id UUID REFERENCES entities(id),
  mandate_id UUID REFERENCES mandates(id),
  
  -- Predictions
  revenue_multiple_expected NUMERIC,
  revenue_multiple_p25 NUMERIC,
  revenue_multiple_p75 NUMERIC,
  
  ebitda_multiple_expected NUMERIC,
  ebitda_multiple_p25 NUMERIC,
  ebitda_multiple_p75 NUMERIC,
  
  enterprise_value_low NUMERIC,
  enterprise_value_high NUMERIC,
  
  -- Metadata
  model_version TEXT,
  confidence_score NUMERIC,
  key_drivers JSONB,
  
  -- Actual outcome (if known)
  actual_revenue_multiple NUMERIC,
  actual_ebitda_multiple NUMERIC,
  prediction_error NUMERIC,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_deal_outcomes_entity ON deal_outcomes(entity_id);
CREATE INDEX idx_deal_outcomes_mandate ON deal_outcomes(mandate_id);
CREATE INDEX idx_deal_outcomes_outcome ON deal_outcomes(deal_outcome);
CREATE INDEX idx_relationships_source ON relationships(source_contact_id);
CREATE INDEX idx_relationships_target ON relationships(target_contact_id);
CREATE INDEX idx_intro_requests_status ON intro_requests(status);
CREATE INDEX idx_outreach_campaign ON outreach_activities(campaign_id);
CREATE INDEX idx_outreach_entity ON outreach_activities(entity_id);
CREATE INDEX idx_valuation_entity ON valuation_predictions(entity_id);

-- RLS Policies
ALTER TABLE deal_outcomes ENABLE ROW LEVEL SECURITY;
ALTER TABLE relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE intro_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE outreach_campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE outreach_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE deal_rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE deal_room_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE valuation_predictions ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users see outcomes from their org
CREATE POLICY "org_deal_outcomes"
ON deal_outcomes FOR SELECT
USING (
  organization_id IN (
    SELECT organization_id FROM team_members
    WHERE user_id = auth.uid()
  )
  OR shared_with_network = true
);

-- RLS Policy: Users see their intro requests
CREATE POLICY "user_intro_requests"
ON intro_requests FOR SELECT
USING (requester_user_id = auth.uid());

-- RLS Policy: Users see outreach for their mandates
CREATE POLICY "mandate_outreach_campaigns"
ON outreach_campaigns FOR SELECT
USING (
  mandate_id IN (
    SELECT mandate_id FROM mandate_members
    WHERE user_id = auth.uid()
  )
);

-- RLS Policy: Users see outreach activities for their campaigns
CREATE POLICY "campaign_outreach_activities"
ON outreach_activities FOR SELECT
USING (
  campaign_id IN (
    SELECT id FROM outreach_campaigns
    WHERE mandate_id IN (
      SELECT mandate_id FROM mandate_members
      WHERE user_id = auth.uid()
    )
  )
);

-- Helper function to calculate intro path effectiveness
CREATE OR REPLACE FUNCTION calculate_intro_effectiveness(path_contact_ids UUID[])
RETURNS NUMERIC AS $$
DECLARE
  effectiveness NUMERIC := 1.0;
  contact_id UUID;
  rel RECORD;
BEGIN
  FOREACH contact_id IN ARRAY path_contact_ids
  LOOP
    SELECT * INTO rel FROM relationships 
    WHERE source_contact_id = contact_id OR target_contact_id = contact_id
    LIMIT 1;
    
    IF rel IS NOT NULL THEN
      -- Discount by relationship strength and success rate
      effectiveness := effectiveness * (rel.strength / 100.0);
      IF rel.total_intro_requests > 0 THEN
        effectiveness := effectiveness * (1.0 + (rel.successful_intros::NUMERIC / rel.total_intro_requests));
      END IF;
    END IF;
  END LOOP;
  
  RETURN effectiveness;
END;
$$ LANGUAGE plpgsql;

-- Function to record deal outcome
CREATE OR REPLACE FUNCTION record_deal_outcome(
  p_entity_id UUID,
  p_mandate_id UUID,
  p_outcome TEXT,
  p_details JSONB
)
RETURNS UUID AS $$
DECLARE
  outcome_id UUID;
  org_id UUID;
BEGIN
  -- Get org from mandate
  SELECT organization_id INTO org_id
  FROM mandates
  WHERE id = p_mandate_id;
  
  INSERT INTO deal_outcomes (
    organization_id,
    entity_id,
    mandate_id,
    deal_outcome,
    sector,
    target_geography,
    deal_type,
    first_contact_date
  ) VALUES (
    org_id,
    p_entity_id,
    p_mandate_id,
    p_outcome,
    COALESCE(p_details->>'sector', 'unknown'),
    COALESCE(p_details->>'geography', 'unknown'),
    COALESCE(p_details->>'deal_type', 'acquisition'),
    COALESCE((p_details->>'first_contact_date')::DATE, CURRENT_DATE)
  )
  RETURNING id INTO outcome_id;
  
  RETURN outcome_id;
END;
$$ LANGUAGE plpgsql;
```

---

## 📱 PART 2: TYPESCRIPT TYPES

### `src/types/genome.types.ts`

```typescript
import { Database } from './database.types'

export type DealOutcome = Database['public']['Tables']['deal_outcomes']['Row']
export type Relationship = Database['public']['Tables']['relationships']['Row']
export type IntroRequest = Database['public']['Tables']['intro_requests']['Row']
export type OutreachCampaign = Database['public']['Tables']['outreach_campaigns']['Row']
export type OutreachActivity = Database['public']['Tables']['outreach_activities']['Row']
export type DealRoom = Database['public']['Tables']['deal_rooms']['Row']
export type DealRoomActivity = Database['public']['Tables']['deal_room_activities']['Row']
export type ValuationPrediction = Database['public']['Tables']['valuation_predictions']['Row']

// Extended types with joins
export interface DealOutcomeWithEntity extends DealOutcome {
  entity: {
    id: string
    name: string
    domain: string
    industry: string
  }
}

export interface IntroRequestWithDetails extends IntroRequest {
  target_contact: {
    id: string
    first_name: string
    last_name: string
    title: string
    entity: {
      name: string
    }
  }
  mandate_match: {
    entity: {
      name: string
    }
  }
}

export interface OutreachActivityWithDetails extends OutreachActivity {
  entity: {
    name: string
    domain: string
  }
  contact: {
    first_name: string
    last_name: string
    email: string
  }
}

export interface DealRoomWithActivities extends DealRoom {
  mandate_match: {
    entity: {
      name: string
    }
    fit_score: number
    timing_score: number
  }
  activities: DealRoomActivity[]
}

// UI types
export interface IntroPath {
  contacts: string[] // Array of contact IDs
  effectiveness: number // 0-100
  description: string
}

export interface ValuationSummary {
  revenue_multiple: {
    expected: number
    range: [number, number]
  }
  ebitda_multiple: {
    expected: number
    range: [number, number]
  }
  enterprise_value_range: [number, number]
  confidence: number
}
```

---

## 🎣 PART 3: REACT HOOKS

### `src/hooks/useDealOutcomes.ts`

```typescript
import { useEffect, useState } from 'react'
import { supabase } from '../services/supabase'
import type { DealOutcomeWithEntity } from '../types/genome.types'

export function useDealOutcomes() {
  const [outcomes, setOutcomes] = useState<DealOutcomeWithEntity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function loadOutcomes() {
      const { data, error } = await supabase
        .from('deal_outcomes')
        .select(`
          *,
          entity:entities (
            id,
            name,
            domain,
            industry
          )
        `)
        .order('created_at', { ascending: false })
        .limit(50)

      if (cancelled) return

      if (error) {
        setError(error.message)
      } else {
        setOutcomes((data || []) as unknown as DealOutcomeWithEntity[])
      }
      setLoading(false)
    }

    loadOutcomes()
    return () => { cancelled = true }
  }, [])

  return { outcomes, loading, error }
}

export function useRecordDealOutcome() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function recordOutcome(
    entityId: string,
    mandateId: string,
    outcome: string,
    details: any
  ) {
    setLoading(true)
    setError(null)

    const { data, error } = await supabase.rpc('record_deal_outcome', {
      p_entity_id: entityId,
      p_mandate_id: mandateId,
      p_outcome: outcome,
      p_details: details
    })

    setLoading(false)

    if (error) {
      setError(error.message)
      return null
    }

    return data
  }

  return { recordOutcome, loading, error }
}
```

### `src/hooks/useIntroRequests.ts`

```typescript
import { useEffect, useState } from 'react'
import { supabase } from '../services/supabase'
import type { IntroRequestWithDetails } from '../types/genome.types'

export function useIntroRequests() {
  const [requests, setRequests] = useState<IntroRequestWithDetails[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function loadRequests() {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) return

      const { data, error } = await supabase
        .from('intro_requests')
        .select(`
          *,
          target_contact:contacts!target_contact_id (
            id,
            first_name,
            last_name,
            title,
            entity:entities (name)
          ),
          mandate_match:mandate_matches (
            entity:entities (name)
          )
        `)
        .eq('requester_user_id', user.id)
        .order('created_at', { ascending: false })

      if (cancelled) return

      if (error) {
        setError(error.message)
      } else {
        setRequests((data || []) as unknown as IntroRequestWithDetails[])
      }
      setLoading(false)
    }

    loadRequests()
    return () => { cancelled = true }
  }, [])

  return { requests, loading, error }
}

export function useRequestIntro() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function requestIntro(
    targetContactId: string,
    mandateMatchId: string,
    introPath: string[],
    message: string
  ) {
    setLoading(true)
    setError(null)

    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      setError('Not authenticated')
      setLoading(false)
      return null
    }

    const { data, error } = await supabase
      .from('intro_requests')
      .insert({
        requester_user_id: user.id,
        target_contact_id: targetContactId,
        mandate_match_id: mandateMatchId,
        intro_path: introPath,
        intro_message: message,
        status: 'pending'
      })
      .select()
      .single()

    setLoading(false)

    if (error) {
      setError(error.message)
      return null
    }

    return data
  }

  return { requestIntro, loading, error }
}
```

### `src/hooks/useOutreachCampaign.ts`

```typescript
import { useEffect, useState } from 'react'
import { supabase } from '../services/supabase'
import type { OutreachCampaign, OutreachActivityWithDetails } from '../types/genome.types'

export function useOutreachCampaigns(mandateId: string) {
  const [campaigns, setCampaigns] = useState<OutreachCampaign[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!mandateId) return
    let cancelled = false

    async function loadCampaigns() {
      const { data, error } = await supabase
        .from('outreach_campaigns')
        .select('*')
        .eq('mandate_id', mandateId)
        .order('created_at', { ascending: false })

      if (cancelled) return

      if (error) {
        setError(error.message)
      } else {
        setCampaigns(data || [])
      }
      setLoading(false)
    }

    loadCampaigns()
    return () => { cancelled = true }
  }, [mandateId])

  return { campaigns, loading, error }
}

export function useCampaignActivities(campaignId: string) {
  const [activities, setActivities] = useState<OutreachActivityWithDetails[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!campaignId) return
    let cancelled = false

    async function loadActivities() {
      const { data, error } = await supabase
        .from('outreach_activities')
        .select(`
          *,
          entity:entities (name, domain),
          contact:contacts (first_name, last_name, email)
        `)
        .eq('campaign_id', campaignId)
        .order('sent_at', { ascending: false })

      if (cancelled) return

      if (error) {
        setError(error.message)
      } else {
        setActivities((data || []) as unknown as OutreachActivityWithDetails[])
      }
      setLoading(false)
    }

    loadActivities()
    return () => { cancelled = true }
  }, [campaignId])

  return { activities, loading, error }
}

export function useCreateCampaign() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function createCampaign(
    mandateId: string,
    name: string,
    targetEntityIds: string[]
  ) {
    setLoading(true)
    setError(null)

    const { data, error } = await supabase
      .from('outreach_campaigns')
      .insert({
        mandate_id: mandateId,
        name,
        target_entity_ids: targetEntityIds,
        status: 'draft'
      })
      .select()
      .single()

    setLoading(false)

    if (error) {
      setError(error.message)
      return null
    }

    return data
  }

  return { createCampaign, loading, error }
}
```

### `src/hooks/useValuation.ts`

```typescript
import { useEffect, useState } from 'react'
import { supabase } from '../services/supabase'
import type { ValuationPrediction, ValuationSummary } from '../types/genome.types'

export function useValuation(entityId: string, mandateId: string) {
  const [valuation, setValuation] = useState<ValuationPrediction | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!entityId || !mandateId) return
    let cancelled = false

    async function loadValuation() {
      const { data, error } = await supabase
        .from('valuation_predictions')
        .select('*')
        .eq('entity_id', entityId)
        .eq('mandate_id', mandateId)
        .order('created_at', { ascending: false })
        .limit(1)
        .maybeSingle()

      if (cancelled) return

      if (error) {
        setError(error.message)
      } else {
        setValuation(data)
      }
      setLoading(false)
    }

    loadValuation()
    return () => { cancelled = true }
  }, [entityId, mandateId])

  const summary: ValuationSummary | null = valuation ? {
    revenue_multiple: {
      expected: valuation.revenue_multiple_expected || 0,
      range: [
        valuation.revenue_multiple_p25 || 0,
        valuation.revenue_multiple_p75 || 0
      ]
    },
    ebitda_multiple: {
      expected: valuation.ebitda_multiple_expected || 0,
      range: [
        valuation.ebitda_multiple_p25 || 0,
        valuation.ebitda_multiple_p75 || 0
      ]
    },
    enterprise_value_range: [
      valuation.enterprise_value_low || 0,
      valuation.enterprise_value_high || 0
    ],
    confidence: valuation.confidence_score || 0
  } : null

  return { valuation, summary, loading, error }
}
```

### `src/hooks/useDealRoom.ts`

```typescript
import { useEffect, useState } from 'react'
import { supabase } from '../services/supabase'
import type { DealRoomWithActivities } from '../types/genome.types'

export function useDealRoom(mandateMatchId: string) {
  const [dealRoom, setDealRoom] = useState<DealRoomWithActivities | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!mandateMatchId) return
    let cancelled = false

    async function loadDealRoom() {
      // First, check if deal room exists
      let { data: room, error: roomError } = await supabase
        .from('deal_rooms')
        .select(`
          *,
          mandate_match:mandate_matches (
            entity:entities (name),
            fit_score,
            timing_score
          )
        `)
        .eq('mandate_match_id', mandateMatchId)
        .maybeSingle()

      // If doesn't exist, create it
      if (!room && !roomError) {
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) return

        const { data: newRoom, error: createError } = await supabase
          .from('deal_rooms')
          .insert({
            mandate_match_id: mandateMatchId,
            members: [user.id]
          })
          .select(`
            *,
            mandate_match:mandate_matches (
              entity:entities (name),
              fit_score,
              timing_score
            )
          `)
          .single()

        if (createError) {
          setError(createError.message)
          setLoading(false)
          return
        }

        room = newRoom
      }

      if (roomError) {
        setError(roomError.message)
        setLoading(false)
        return
      }

      // Load activities
      const { data: activities, error: activitiesError } = await supabase
        .from('deal_room_activities')
        .select('*')
        .eq('deal_room_id', room!.id)
        .order('created_at', { ascending: true })

      if (cancelled) return

      if (activitiesError) {
        setError(activitiesError.message)
      } else {
        setDealRoom({
          ...room!,
          activities: activities || []
        } as unknown as DealRoomWithActivities)
      }
      setLoading(false)
    }

    loadDealRoom()
    return () => { cancelled = true }
  }, [mandateMatchId])

  return { dealRoom, loading, error }
}

export function useAddDealRoomActivity() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function addActivity(
    dealRoomId: string,
    activityType: string,
    content: any
  ) {
    setLoading(true)
    setError(null)

    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      setError('Not authenticated')
      setLoading(false)
      return null
    }

    const { data, error } = await supabase
      .from('deal_room_activities')
      .insert({
        deal_room_id: dealRoomId,
        user_id: user.id,
        activity_type: activityType,
        content
      })
      .select()
      .single()

    setLoading(false)

    if (error) {
      setError(error.message)
      return null
    }

    return data
  }

  return { addActivity, loading, error }
}
```

---

Continue in next file...
