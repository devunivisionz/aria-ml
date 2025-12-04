# 🧬 DEAL GENOME - REACT NATIVE SCREENS (PART 3)

---

## 📱 ADVANCED SCREENS

### `src/screens/ValuationScreen.tsx`

```typescript
import React from 'react'
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Dimensions,
} from 'react-native'
import { NativeStackScreenProps } from '@react-navigation/native-stack'
import { RootStackParamList } from '../../App'
import { useValuation } from '../hooks/useValuation'

type Props = NativeStackScreenProps<RootStackParamList, 'Valuation'> & {
  route: { params: { entityId: string; mandateId: string; entityName: string } }
}

const { width } = Dimensions.get('window')

export default function ValuationScreen({ route }: Props) {
  const { entityId, mandateId, entityName } = route.params
  const { valuation, summary, loading, error } = useValuation(entityId, mandateId)

  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `€${(value / 1000000).toFixed(1)}M`
    }
    if (value >= 1000) {
      return `€${(value / 1000).toFixed(1)}K`
    }
    return `€${value.toFixed(0)}`
  }

  const formatMultiple = (value: number) => {
    return `${value.toFixed(1)}x`
  }

  if (loading) {
    return (
      <View style={styles.container}>
        <View style={styles.centered}>
          <Text style={styles.loadingText}>Calculating valuation...</Text>
        </View>
      </View>
    )
  }

  if (error || !summary) {
    return (
      <View style={styles.container}>
        <View style={styles.centered}>
          <Text style={styles.errorText}>
            {error || 'Valuation data not available'}
          </Text>
          <Text style={styles.errorSubtext}>
            We need more data to predict valuation for this company
          </Text>
        </View>
      </View>
    )
  }

  return (
    <View style={styles.container}>
      <ScrollView>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.companyName}>{entityName}</Text>
          <Text style={styles.headerSubtitle}>AI-Powered Valuation Prediction</Text>
        </View>

        {/* Confidence Score */}
        <View style={styles.confidenceContainer}>
          <View style={styles.confidenceCircle}>
            <Text style={styles.confidenceValue}>
              {Math.round(summary.confidence * 100)}%
            </Text>
            <Text style={styles.confidenceLabel}>Confidence</Text>
          </View>
          <View style={styles.confidenceInfo}>
            <Text style={styles.confidenceTitle}>Prediction Confidence</Text>
            <Text style={styles.confidenceDescription}>
              Based on {valuation?.model_version || 'our'} model trained on 
              1,000+ similar transactions
            </Text>
          </View>
        </View>

        {/* Revenue Multiple */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Revenue Multiple</Text>
          <View style={styles.multipleCard}>
            <Text style={styles.multipleValue}>
              {formatMultiple(summary.revenue_multiple.expected)}
            </Text>
            <Text style={styles.multipleLabel}>Expected</Text>
            
            <View style={styles.rangeContainer}>
              <View style={styles.rangeBar}>
                <View style={[
                  styles.rangeHighlight,
                  {
                    left: `${(summary.revenue_multiple.range[0] / 15) * 100}%`,
                    width: `${((summary.revenue_multiple.range[1] - summary.revenue_multiple.range[0]) / 15) * 100}%`
                  }
                ]} />
                <View style={[
                  styles.rangeMarker,
                  {
                    left: `${(summary.revenue_multiple.expected / 15) * 100}%`
                  }
                ]} />
              </View>
              <View style={styles.rangeLegend}>
                <Text style={styles.rangeLegendText}>
                  {formatMultiple(summary.revenue_multiple.range[0])}
                </Text>
                <Text style={styles.rangeLegendText}>50% range</Text>
                <Text style={styles.rangeLegendText}>
                  {formatMultiple(summary.revenue_multiple.range[1])}
                </Text>
              </View>
            </View>
          </View>
        </View>

        {/* EBITDA Multiple */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>EBITDA Multiple</Text>
          <View style={styles.multipleCard}>
            <Text style={styles.multipleValue}>
              {formatMultiple(summary.ebitda_multiple.expected)}
            </Text>
            <Text style={styles.multipleLabel}>Expected</Text>
            
            <View style={styles.rangeContainer}>
              <View style={styles.rangeBar}>
                <View style={[
                  styles.rangeHighlight,
                  {
                    left: `${(summary.ebitda_multiple.range[0] / 20) * 100}%`,
                    width: `${((summary.ebitda_multiple.range[1] - summary.ebitda_multiple.range[0]) / 20) * 100}%`
                  }
                ]} />
                <View style={[
                  styles.rangeMarker,
                  {
                    left: `${(summary.ebitda_multiple.expected / 20) * 100}%`
                  }
                ]} />
              </View>
              <View style={styles.rangeLegend}>
                <Text style={styles.rangeLegendText}>
                  {formatMultiple(summary.ebitda_multiple.range[0])}
                </Text>
                <Text style={styles.rangeLegendText}>50% range</Text>
                <Text style={styles.rangeLegendText}>
                  {formatMultiple(summary.ebitda_multiple.range[1])}
                </Text>
              </View>
            </View>
          </View>
        </View>

        {/* Enterprise Value */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Enterprise Value Range</Text>
          <View style={styles.evCard}>
            <View style={styles.evRow}>
              <Text style={styles.evLabel}>Low</Text>
              <Text style={styles.evValue}>
                {formatCurrency(summary.enterprise_value_range[0])}
              </Text>
            </View>
            <View style={styles.evDivider} />
            <View style={styles.evRow}>
              <Text style={styles.evLabel}>High</Text>
              <Text style={styles.evValue}>
                {formatCurrency(summary.enterprise_value_range[1])}
              </Text>
            </View>
          </View>
        </View>

        {/* Key Drivers */}
        {valuation?.key_drivers && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Key Valuation Drivers</Text>
            <View style={styles.driversCard}>
              {(valuation.key_drivers as any[]).map((driver, index) => (
                <View key={index} style={styles.driverRow}>
                  <View style={[
                    styles.driverIndicator,
                    driver.impact > 0 ? styles.driverPositive : styles.driverNegative
                  ]} />
                  <View style={styles.driverContent}>
                    <Text style={styles.driverText}>{driver.factor}</Text>
                    <Text style={styles.driverImpact}>
                      {driver.impact > 0 ? '+' : ''}{driver.impact}x impact
                    </Text>
                  </View>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Disclaimer */}
        <View style={styles.disclaimer}>
          <Text style={styles.disclaimerText}>
            ⚠️ Predictions are estimates based on historical data and should not 
            be the sole basis for investment decisions. Actual valuations may vary 
            significantly based on market conditions, deal structure, and negotiation.
          </Text>
        </View>
      </ScrollView>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    color: '#fff',
    fontSize: 16,
  },
  errorText: {
    color: '#ff6b6b',
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center',
    marginBottom: 8,
  },
  errorSubtext: {
    color: '#888',
    fontSize: 14,
    textAlign: 'center',
  },
  header: {
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a1a',
  },
  companyName: {
    color: '#fff',
    fontSize: 24,
    fontWeight: '700',
    marginBottom: 4,
  },
  headerSubtitle: {
    color: '#888',
    fontSize: 14,
  },
  confidenceContainer: {
    flexDirection: 'row',
    padding: 20,
    backgroundColor: '#0a0a0a',
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a1a',
  },
  confidenceCircle: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#042821',
    borderWidth: 3,
    borderColor: '#00c896',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 20,
  },
  confidenceValue: {
    color: '#00c896',
    fontSize: 28,
    fontWeight: '700',
  },
  confidenceLabel: {
    color: '#00c896',
    fontSize: 12,
    marginTop: 4,
  },
  confidenceInfo: {
    flex: 1,
    justifyContent: 'center',
  },
  confidenceTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  confidenceDescription: {
    color: '#888',
    fontSize: 13,
    lineHeight: 18,
  },
  section: {
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a1a',
  },
  sectionTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 16,
  },
  multipleCard: {
    backgroundColor: '#0a0a0a',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
  },
  multipleValue: {
    color: '#00c896',
    fontSize: 48,
    fontWeight: '700',
  },
  multipleLabel: {
    color: '#888',
    fontSize: 14,
    marginBottom: 20,
  },
  rangeContainer: {
    width: '100%',
  },
  rangeBar: {
    height: 6,
    backgroundColor: '#1a1a1a',
    borderRadius: 3,
    position: 'relative',
    marginBottom: 12,
  },
  rangeHighlight: {
    position: 'absolute',
    height: '100%',
    backgroundColor: '#00c896',
    borderRadius: 3,
  },
  rangeMarker: {
    position: 'absolute',
    top: -5,
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: '#00c896',
    transform: [{ translateX: -8 }],
  },
  rangeLegend: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  rangeLegendText: {
    color: '#888',
    fontSize: 12,
  },
  evCard: {
    backgroundColor: '#0a0a0a',
    borderRadius: 12,
    overflow: 'hidden',
  },
  evRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
  },
  evDivider: {
    height: 1,
    backgroundColor: '#1a1a1a',
  },
  evLabel: {
    color: '#888',
    fontSize: 16,
  },
  evValue: {
    color: '#fff',
    fontSize: 24,
    fontWeight: '700',
  },
  driversCard: {
    backgroundColor: '#0a0a0a',
    borderRadius: 12,
    padding: 16,
  },
  driverRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  driverIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 12,
  },
  driverPositive: {
    backgroundColor: '#00c896',
  },
  driverNegative: {
    backgroundColor: '#ff6b6b',
  },
  driverContent: {
    flex: 1,
  },
  driverText: {
    color: '#fff',
    fontSize: 14,
    marginBottom: 2,
  },
  driverImpact: {
    color: '#888',
    fontSize: 12,
  },
  disclaimer: {
    padding: 20,
    backgroundColor: '#0a0a0a',
    margin: 20,
    borderRadius: 12,
    borderLeftWidth: 3,
    borderLeftColor: '#ffa500',
  },
  disclaimerText: {
    color: '#888',
    fontSize: 12,
    lineHeight: 18,
  },
})
```

### `src/screens/DealRoomScreen.tsx`

```typescript
import React, { useState } from 'react'
import {
  View,
  Text,
  ScrollView,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
} from 'react-native'
import { NativeStackScreenProps } from '@react-navigation/native-stack'
import { RootStackParamList } from '../../App'
import { useDealRoom, useAddDealRoomActivity } from '../hooks/useDealRoom'

type Props = NativeStackScreenProps<RootStackParamList, 'DealRoom'> & {
  route: { params: { mandateMatchId: string } }
}

export default function DealRoomScreen({ route }: Props) {
  const { mandateMatchId } = route.params
  const { dealRoom, loading, error } = useDealRoom(mandateMatchId)
  const { addActivity, loading: addingActivity } = useAddDealRoomActivity()
  
  const [newNote, setNewNote] = useState('')

  const handleAddNote = async () => {
    if (!newNote.trim() || !dealRoom) return

    await addActivity(dealRoom.id, 'note', { text: newNote.trim() })
    setNewNote('')
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'note': return '📝'
      case 'comment': return '💬'
      case 'document': return '📄'
      case 'task': return '✓'
      case 'status_change': return '🔄'
      default: return '•'
    }
  }

  if (loading) {
    return (
      <View style={styles.container}>
        <View style={styles.centered}>
          <Text style={styles.loadingText}>Loading deal room...</Text>
        </View>
      </View>
    )
  }

  if (error || !dealRoom) {
    return (
      <View style={styles.container}>
        <View style={styles.centered}>
          <Text style={styles.errorText}>{error || 'Deal room not found'}</Text>
        </View>
      </View>
    )
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={90}
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.companyName}>
          {dealRoom.mandate_match?.entity?.name}
        </Text>
        <View style={styles.scoresRow}>
          <View style={styles.scorePill}>
            <Text style={styles.scoreLabel}>Fit</Text>
            <Text style={styles.scoreValue}>
              {dealRoom.mandate_match?.fit_score || 0}
            </Text>
          </View>
          <View style={styles.scorePill}>
            <Text style={styles.scoreLabel}>Timing</Text>
            <Text style={styles.scoreValue}>
              {dealRoom.mandate_match?.timing_score || 0}
            </Text>
          </View>
        </View>
      </View>

      {/* Activities Feed */}
      <ScrollView style={styles.activitiesContainer}>
        {dealRoom.activities && dealRoom.activities.length > 0 ? (
          dealRoom.activities.map((activity) => (
            <View key={activity.id} style={styles.activityCard}>
              <View style={styles.activityHeader}>
                <Text style={styles.activityIcon}>
                  {getActivityIcon(activity.activity_type)}
                </Text>
                <View style={styles.activityMeta}>
                  <Text style={styles.activityType}>
                    {activity.activity_type.replace('_', ' ')}
                  </Text>
                  <Text style={styles.activityDate}>
                    {new Date(activity.created_at).toLocaleString()}
                  </Text>
                </View>
              </View>
              {activity.content && (activity.content as any).text && (
                <Text style={styles.activityText}>
                  {(activity.content as any).text}
                </Text>
              )}
            </View>
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>No activity yet</Text>
            <Text style={styles.emptySubtext}>
              Add a note to start collaborating
            </Text>
          </View>
        )}
      </ScrollView>

      {/* Input Box */}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Add a note..."
          placeholderTextColor="#666"
          value={newNote}
          onChangeText={setNewNote}
          multiline
          maxLength={500}
        />
        <TouchableOpacity
          style={[
            styles.sendButton,
            (!newNote.trim() || addingActivity) && styles.sendButtonDisabled
          ]}
          onPress={handleAddNote}
          disabled={!newNote.trim() || addingActivity}
        >
          <Text style={styles.sendButtonText}>
            {addingActivity ? '...' : 'Send'}
          </Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#fff',
    fontSize: 16,
  },
  errorText: {
    color: '#ff6b6b',
    fontSize: 16,
  },
  header: {
    padding: 20,
    backgroundColor: '#0a0a0a',
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a1a',
  },
  companyName: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 12,
  },
  scoresRow: {
    flexDirection: 'row',
    gap: 10,
  },
  scorePill: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#042821',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  scoreLabel: {
    color: '#888',
    fontSize: 12,
    marginRight: 6,
  },
  scoreValue: {
    color: '#00c896',
    fontSize: 14,
    fontWeight: '600',
  },
  activitiesContainer: {
    flex: 1,
    padding: 20,
  },
  activityCard: {
    backgroundColor: '#0a0a0a',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#1a1a1a',
  },
  activityHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  activityIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  activityMeta: {
    flex: 1,
  },
  activityType: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  activityDate: {
    color: '#666',
    fontSize: 11,
    marginTop: 2,
  },
  activityText: {
    color: '#ddd',
    fontSize: 14,
    lineHeight: 20,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    color: '#888',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  emptySubtext: {
    color: '#666',
    fontSize: 14,
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: '#0a0a0a',
    borderTopWidth: 1,
    borderTopColor: '#1a1a1a',
    alignItems: 'flex-end',
  },
  input: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    color: '#fff',
    fontSize: 14,
    maxHeight: 100,
    marginRight: 10,
  },
  sendButton: {
    backgroundColor: '#00c896',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
  },
  sendButtonDisabled: {
    opacity: 0.5,
  },
  sendButtonText: {
    color: '#000',
    fontSize: 14,
    fontWeight: '600',
  },
})
```

---

## 🎨 PART 5: COMPONENTS

### `src/components/ValuationCard.tsx`

```typescript
import React from 'react'
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native'
import type { ValuationSummary } from '../types/genome.types'

interface Props {
  summary: ValuationSummary | null
  onPress?: () => void
}

export default function ValuationCard({ summary, onPress }: Props) {
  if (!summary) {
    return (
      <TouchableOpacity style={styles.card} onPress={onPress}>
        <View style={styles.placeholderContent}>
          <Text style={styles.placeholderText}>Valuation Not Available</Text>
          <Text style={styles.placeholderSubtext}>Tap to learn more</Text>
        </View>
      </TouchableOpacity>
    )
  }

  return (
    <TouchableOpacity style={styles.card} onPress={onPress}>
      <View style={styles.header}>
        <Text style={styles.title}>AI Valuation Prediction</Text>
        <View style={styles.confidenceBadge}>
          <Text style={styles.confidenceText}>
            {Math.round(summary.confidence * 100)}% confident
          </Text>
        </View>
      </View>

      <View style={styles.multiplesRow}>
        <View style={styles.multipleItem}>
          <Text style={styles.multipleLabel}>Revenue Multiple</Text>
          <Text style={styles.multipleValue}>
            {summary.revenue_multiple.expected.toFixed(1)}x
          </Text>
          <Text style={styles.multipleRange}>
            {summary.revenue_multiple.range[0].toFixed(1)}x - {summary.revenue_multiple.range[1].toFixed(1)}x
          </Text>
        </View>

        <View style={styles.divider} />

        <View style={styles.multipleItem}>
          <Text style={styles.multipleLabel}>EBITDA Multiple</Text>
          <Text style={styles.multipleValue}>
            {summary.ebitda_multiple.expected.toFixed(1)}x
          </Text>
          <Text style={styles.multipleRange}>
            {summary.ebitda_multiple.range[0].toFixed(1)}x - {summary.ebitda_multiple.range[1].toFixed(1)}x
          </Text>
        </View>
      </View>

      <Text style={styles.tapHint}>Tap for detailed analysis →</Text>
    </TouchableOpacity>
  )
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#0a0a0a',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#1a1a1a',
  },
  placeholderContent: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  placeholderText: {
    color: '#888',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 4,
  },
  placeholderSubtext: {
    color: '#666',
    fontSize: 12,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  title: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  confidenceBadge: {
    backgroundColor: '#042821',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 10,
  },
  confidenceText: {
    color: '#00c896',
    fontSize: 11,
    fontWeight: '600',
  },
  multiplesRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  multipleItem: {
    flex: 1,
    alignItems: 'center',
  },
  multipleLabel: {
    color: '#888',
    fontSize: 12,
    marginBottom: 6,
  },
  multipleValue: {
    color: '#00c896',
    fontSize: 24,
    fontWeight: '700',
    marginBottom: 4,
  },
  multipleRange: {
    color: '#666',
    fontSize: 11,
  },
  divider: {
    width: 1,
    height: 60,
    backgroundColor: '#1a1a1a',
    marginHorizontal: 16,
  },
  tapHint: {
    color: '#666',
    fontSize: 12,
    textAlign: 'center',
    marginTop: 12,
  },
})
```

### `src/components/IntroPathCard.tsx`

```typescript
import React from 'react'
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native'

interface Props {
  path: string[]
  effectiveness: number
  onRequestIntro?: () => void
}

export default function IntroPathCard({ path, effectiveness, onRequestIntro }: Props) {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.title}>Best Intro Path</Text>
        <View style={[
          styles.effectivenessBadge,
          effectiveness >= 70 && styles.effectivenessHigh,
          effectiveness >= 40 && effectiveness < 70 && styles.effectivenessMedium,
          effectiveness < 40 && styles.effectivenessLow,
        ]}>
          <Text style={styles.effectivenessText}>
            {Math.round(effectiveness)}% effective
          </Text>
        </View>
      </View>

      <View style={styles.pathContainer}>
        <View style={styles.pathNode}>
          <View style={styles.nodeCircle}>
            <Text style={styles.nodeText}>You</Text>
          </View>
        </View>

        <View style={styles.pathArrow}>
          <View style={styles.arrowLine} />
          <Text style={styles.arrowText}>→</Text>
        </View>

        <View style={styles.pathNode}>
          <View style={styles.nodeCircle}>
            <Text style={styles.nodeText}>{path.length - 2}</Text>
          </View>
          <Text style={styles.nodeLabel}>connections</Text>
        </View>

        <View style={styles.pathArrow}>
          <View style={styles.arrowLine} />
          <Text style={styles.arrowText}>→</Text>
        </View>

        <View style={styles.pathNode}>
          <View style={[styles.nodeCircle, styles.nodeCircleTarget]}>
            <Text style={styles.nodeText}>🎯</Text>
          </View>
          <Text style={styles.nodeLabel}>Target</Text>
        </View>
      </View>

      {onRequestIntro && (
        <TouchableOpacity style={styles.requestButton} onPress={onRequestIntro}>
          <Text style={styles.requestButtonText}>Request Introduction</Text>
        </TouchableOpacity>
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#0a0a0a',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#1a1a1a',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  title: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  effectivenessBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 10,
  },
  effectivenessHigh: {
    backgroundColor: '#042821',
  },
  effectivenessMedium: {
    backgroundColor: '#2a2a0a',
  },
  effectivenessLow: {
    backgroundColor: '#2a0a0a',
  },
  effectivenessText: {
    fontSize: 11,
    fontWeight: '600',
  },
  pathContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  pathNode: {
    alignItems: 'center',
  },
  nodeCircle: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#1a1a1a',
    borderWidth: 2,
    borderColor: '#00c896',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 6,
  },
  nodeCircleTarget: {
    borderColor: '#ffa500',
  },
  nodeText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  nodeLabel: {
    color: '#666',
    fontSize: 10,
  },
  pathArrow: {
    marginHorizontal: 8,
    alignItems: 'center',
  },
  arrowLine: {
    width: 30,
    height: 2,
    backgroundColor: '#333',
    marginBottom: 2,
  },
  arrowText: {
    color: '#666',
    fontSize: 16,
  },
  requestButton: {
    backgroundColor: '#00c896',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  requestButtonText: {
    color: '#000',
    fontSize: 14,
    fontWeight: '600',
  },
})
```

Continue with navigation setup in next file...
