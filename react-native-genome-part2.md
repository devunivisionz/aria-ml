# 🧬 DEAL GENOME - REACT NATIVE SCREENS & COMPONENTS (PART 2)

---

## 📱 PART 4: REACT NATIVE SCREENS

### `src/screens/DealGenomeScreen.tsx`

```typescript
import React, { useState } from 'react'
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  FlatList
} from 'react-native'
import { NativeStackScreenProps } from '@react-navigation/native-stack'
import { RootStackParamList } from '../../App'
import { useDealOutcomes } from '../hooks/useDealOutcomes'
import ScoreBadge from '../components/ScoreBadge'

type Props = NativeStackScreenProps<RootStackParamList, 'DealGenome'>

export default function DealGenomeScreen({ navigation }: Props) {
  const { outcomes, loading, error } = useDealOutcomes()
  const [filter, setFilter] = useState<'all' | 'closed' | 'lost'>('all')

  const filteredOutcomes = outcomes.filter(outcome => {
    if (filter === 'all') return true
    if (filter === 'closed') return outcome.deal_outcome === 'closed'
    if (filter === 'lost') return outcome.deal_outcome === 'lost_to_competitor' || outcome.deal_outcome === 'passed_ic'
    return true
  })

  const stats = {
    total: outcomes.length,
    closed: outcomes.filter(o => o.deal_outcome === 'closed').length,
    lost: outcomes.filter(o => o.deal_outcome !== 'closed').length,
    closeRate: outcomes.length > 0 
      ? Math.round((outcomes.filter(o => o.deal_outcome === 'closed').length / outcomes.length) * 100)
      : 0
  }

  if (loading) {
    return (
      <View style={styles.container}>
        <View style={styles.centered}>
          <Text style={styles.loadingText}>Loading Deal Genome...</Text>
        </View>
      </View>
    )
  }

  if (error) {
    return (
      <View style={styles.container}>
        <View style={styles.centered}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      </View>
    )
  }

  return (
    <View style={styles.container}>
      <ScrollView>
        {/* Header Stats */}
        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{stats.total}</Text>
            <Text style={styles.statLabel}>Total Deals</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={[styles.statValue, styles.successText]}>{stats.closed}</Text>
            <Text style={styles.statLabel}>Closed</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={[styles.statValue, styles.dangerText]}>{stats.lost}</Text>
            <Text style={styles.statLabel}>Lost</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={[styles.statValue, styles.primaryText]}>{stats.closeRate}%</Text>
            <Text style={styles.statLabel}>Close Rate</Text>
          </View>
        </View>

        {/* Filter Tabs */}
        <View style={styles.filterContainer}>
          <TouchableOpacity
            style={[styles.filterTab, filter === 'all' && styles.filterTabActive]}
            onPress={() => setFilter('all')}
          >
            <Text style={[styles.filterText, filter === 'all' && styles.filterTextActive]}>
              All ({outcomes.length})
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.filterTab, filter === 'closed' && styles.filterTabActive]}
            onPress={() => setFilter('closed')}
          >
            <Text style={[styles.filterText, filter === 'closed' && styles.filterTextActive]}>
              Closed ({stats.closed})
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.filterTab, filter === 'lost' && styles.filterTabActive]}
            onPress={() => setFilter('lost')}
          >
            <Text style={[styles.filterText, filter === 'lost' && styles.filterTextActive]}>
              Lost ({stats.lost})
            </Text>
          </TouchableOpacity>
        </View>

        {/* Deal List */}
        <View style={styles.listContainer}>
          {filteredOutcomes.map(outcome => (
            <TouchableOpacity
              key={outcome.id}
              style={styles.dealCard}
              onPress={() => navigation.navigate('DealOutcomeDetail', { outcomeId: outcome.id })}
            >
              <View style={styles.dealHeader}>
                <Text style={styles.dealTitle}>{outcome.entity?.name || 'Unknown'}</Text>
                <View style={[
                  styles.outcomeBadge,
                  outcome.deal_outcome === 'closed' && styles.outcomeBadgeSuccess,
                  outcome.deal_outcome !== 'closed' && styles.outcomeBadgeDanger
                ]}>
                  <Text style={styles.outcomeBadgeText}>
                    {outcome.deal_outcome === 'closed' ? '✓ Closed' : '✗ Lost'}
                  </Text>
                </View>
              </View>

              <View style={styles.dealMeta}>
                <Text style={styles.dealMetaText}>{outcome.sector}</Text>
                <Text style={styles.dealMetaSeparator}>•</Text>
                <Text style={styles.dealMetaText}>{outcome.target_geography}</Text>
                <Text style={styles.dealMetaSeparator}>•</Text>
                <Text style={styles.dealMetaText}>{outcome.target_revenue_range}</Text>
              </View>

              {outcome.revenue_multiple_bucket && (
                <View style={styles.dealDetails}>
                  <Text style={styles.dealDetailsText}>
                    Multiple: {outcome.revenue_multiple_bucket}
                  </Text>
                </View>
              )}

              {outcome.what_went_well && (
                <Text style={styles.learningText} numberOfLines={2}>
                  💡 {outcome.what_went_well}
                </Text>
              )}
            </TouchableOpacity>
          ))}
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
  },
  loadingText: {
    color: '#fff',
    fontSize: 16,
  },
  errorText: {
    color: '#ff6b6b',
    fontSize: 16,
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 20,
    gap: 10,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#0a0a0a',
    padding: 15,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#1a1a1a',
  },
  statValue: {
    color: '#fff',
    fontSize: 24,
    fontWeight: '700',
    marginBottom: 4,
  },
  statLabel: {
    color: '#888',
    fontSize: 12,
  },
  successText: {
    color: '#00c896',
  },
  dangerText: {
    color: '#ff6b6b',
  },
  primaryText: {
    color: '#4a9eff',
  },
  filterContainer: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    gap: 10,
    marginBottom: 20,
  },
  filterTab: {
    flex: 1,
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderRadius: 8,
    backgroundColor: '#0a0a0a',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#1a1a1a',
  },
  filterTabActive: {
    backgroundColor: '#0f3d33',
    borderColor: '#00c896',
  },
  filterText: {
    color: '#888',
    fontSize: 14,
    fontWeight: '600',
  },
  filterTextActive: {
    color: '#00c896',
  },
  listContainer: {
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  dealCard: {
    backgroundColor: '#0a0a0a',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#1a1a1a',
  },
  dealHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  dealTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    flex: 1,
  },
  outcomeBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  outcomeBadgeSuccess: {
    backgroundColor: '#042821',
  },
  outcomeBadgeDanger: {
    backgroundColor: '#2a0a0a',
  },
  outcomeBadgeText: {
    fontSize: 12,
    fontWeight: '600',
  },
  dealMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  dealMetaText: {
    color: '#888',
    fontSize: 13,
  },
  dealMetaSeparator: {
    color: '#444',
    marginHorizontal: 8,
  },
  dealDetails: {
    marginBottom: 8,
  },
  dealDetailsText: {
    color: '#aaa',
    fontSize: 13,
  },
  learningText: {
    color: '#00c896',
    fontSize: 13,
    fontStyle: 'italic',
    marginTop: 8,
  },
})
```

### `src/screens/IntroRequestsScreen.tsx`

```typescript
import React from 'react'
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
} from 'react-native'
import { NativeStackScreenProps } from '@react-navigation/native-stack'
import { RootStackParamList } from '../../App'
import { useIntroRequests } from '../hooks/useIntroRequests'

type Props = NativeStackScreenProps<RootStackParamList, 'IntroRequests'>

export default function IntroRequestsScreen({ navigation }: Props) {
  const { requests, loading, error } = useIntroRequests()

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return '#ffa500'
      case 'intro_made': return '#4a9eff'
      case 'meeting_scheduled': return '#00c896'
      case 'declined': return '#ff6b6b'
      default: return '#888'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending': return 'Pending'
      case 'intro_made': return 'Intro Made'
      case 'meeting_scheduled': return 'Meeting Set'
      case 'declined': return 'Declined'
      default: return status
    }
  }

  if (loading) {
    return (
      <View style={styles.container}>
        <View style={styles.centered}>
          <Text style={styles.loadingText}>Loading intro requests...</Text>
        </View>
      </View>
    )
  }

  if (error) {
    return (
      <View style={styles.container}>
        <View style={styles.centered}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      </View>
    )
  }

  if (requests.length === 0) {
    return (
      <View style={styles.container}>
        <View style={styles.centered}>
          <Text style={styles.emptyText}>No intro requests yet</Text>
          <Text style={styles.emptySubtext}>
            Request an intro from entity details screen
          </Text>
        </View>
      </View>
    )
  }

  return (
    <View style={styles.container}>
      <ScrollView>
        <View style={styles.header}>
          <Text style={styles.title}>Intro Requests</Text>
          <Text style={styles.subtitle}>{requests.length} total requests</Text>
        </View>

        <View style={styles.listContainer}>
          {requests.map(request => (
            <TouchableOpacity
              key={request.id}
              style={styles.requestCard}
            >
              <View style={styles.requestHeader}>
                <View style={styles.requestInfo}>
                  <Text style={styles.contactName}>
                    {request.target_contact?.first_name} {request.target_contact?.last_name}
                  </Text>
                  <Text style={styles.contactTitle}>
                    {request.target_contact?.title}
                  </Text>
                  <Text style={styles.companyName}>
                    {request.target_contact?.entity?.name}
                  </Text>
                </View>

                <View style={[
                  styles.statusBadge,
                  { backgroundColor: getStatusColor(request.status) + '20' }
                ]}>
                  <Text style={[
                    styles.statusText,
                    { color: getStatusColor(request.status) }
                  ]}>
                    {getStatusText(request.status)}
                  </Text>
                </View>
              </View>

              {request.intro_path && (
                <View style={styles.pathContainer}>
                  <Text style={styles.pathLabel}>Intro path:</Text>
                  <Text style={styles.pathText}>
                    You → {(request.intro_path as string[]).length - 1} connection(s) → Contact
                  </Text>
                </View>
              )}

              {request.meeting_happened && (
                <View style={styles.successBanner}>
                  <Text style={styles.successText}>✓ Meeting happened!</Text>
                </View>
              )}

              <View style={styles.requestFooter}>
                <Text style={styles.dateText}>
                  Requested {new Date(request.requested_at).toLocaleDateString()}
                </Text>
              </View>
            </TouchableOpacity>
          ))}
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
    fontSize: 16,
  },
  emptyText: {
    color: '#888',
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 8,
  },
  emptySubtext: {
    color: '#666',
    fontSize: 14,
    textAlign: 'center',
  },
  header: {
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a1a',
  },
  title: {
    color: '#fff',
    fontSize: 24,
    fontWeight: '700',
    marginBottom: 4,
  },
  subtitle: {
    color: '#888',
    fontSize: 14,
  },
  listContainer: {
    padding: 20,
  },
  requestCard: {
    backgroundColor: '#0a0a0a',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#1a1a1a',
  },
  requestHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  requestInfo: {
    flex: 1,
  },
  contactName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  contactTitle: {
    color: '#aaa',
    fontSize: 14,
    marginBottom: 2,
  },
  companyName: {
    color: '#888',
    fontSize: 13,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
  },
  pathContainer: {
    backgroundColor: '#050505',
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  pathLabel: {
    color: '#888',
    fontSize: 12,
    marginBottom: 4,
  },
  pathText: {
    color: '#00c896',
    fontSize: 14,
  },
  successBanner: {
    backgroundColor: '#042821',
    padding: 10,
    borderRadius: 8,
    marginBottom: 12,
  },
  successText: {
    color: '#00c896',
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
  },
  requestFooter: {
    borderTopWidth: 1,
    borderTopColor: '#1a1a1a',
    paddingTop: 12,
  },
  dateText: {
    color: '#666',
    fontSize: 12,
  },
})
```

### `src/screens/OutreachCampaignsScreen.tsx`

```typescript
import React from 'react'
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
} from 'react-native'
import { NativeStackScreenProps } from '@react-navigation/native-stack'
import { RootStackParamList } from '../../App'
import { useOutreachCampaigns } from '../hooks/useOutreachCampaign'

type Props = NativeStackScreenProps<RootStackParamList, 'OutreachCampaigns'> & {
  route: { params: { mandateId: string } }
}

export default function OutreachCampaignsScreen({ route, navigation }: Props) {
  const { mandateId } = route.params
  const { campaigns, loading, error } = useOutreachCampaigns(mandateId)

  if (loading) {
    return (
      <View style={styles.container}>
        <View style={styles.centered}>
          <Text style={styles.loadingText}>Loading campaigns...</Text>
        </View>
      </View>
    )
  }

  if (error) {
    return (
      <View style={styles.container}>
        <View style={styles.centered}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      </View>
    )
  }

  return (
    <View style={styles.container}>
      <ScrollView>
        <View style={styles.header}>
          <Text style={styles.title}>Outreach Campaigns</Text>
          <TouchableOpacity
            style={styles.createButton}
            onPress={() => navigation.navigate('CreateCampaign', { mandateId })}
          >
            <Text style={styles.createButtonText}>+ New Campaign</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.listContainer}>
          {campaigns.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={styles.emptyText}>No campaigns yet</Text>
              <Text style={styles.emptySubtext}>
                Create your first outreach campaign
              </Text>
            </View>
          ) : (
            campaigns.map(campaign => (
              <TouchableOpacity
                key={campaign.id}
                style={styles.campaignCard}
                onPress={() => navigation.navigate('CampaignDetails', { 
                  campaignId: campaign.id 
                })}
              >
                <View style={styles.campaignHeader}>
                  <Text style={styles.campaignName}>{campaign.name}</Text>
                  <View style={[
                    styles.statusBadge,
                    campaign.status === 'active' && styles.statusBadgeActive,
                    campaign.status === 'draft' && styles.statusBadgeDraft,
                    campaign.status === 'completed' && styles.statusBadgeCompleted,
                  ]}>
                    <Text style={styles.statusText}>
                      {campaign.status.toUpperCase()}
                    </Text>
                  </View>
                </View>

                <View style={styles.campaignMeta}>
                  <Text style={styles.metaText}>
                    {campaign.target_entity_ids?.length || 0} targets
                  </Text>
                  <Text style={styles.metaSeparator}>•</Text>
                  <Text style={styles.metaText}>
                    Created {new Date(campaign.created_at).toLocaleDateString()}
                  </Text>
                </View>

                {campaign.launched_at && (
                  <Text style={styles.launchedText}>
                    Launched {new Date(campaign.launched_at).toLocaleDateString()}
                  </Text>
                )}
              </TouchableOpacity>
            ))
          )}
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a1a',
  },
  title: {
    color: '#fff',
    fontSize: 24,
    fontWeight: '700',
  },
  createButton: {
    backgroundColor: '#00c896',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
  },
  createButtonText: {
    color: '#000',
    fontSize: 14,
    fontWeight: '600',
  },
  listContainer: {
    padding: 20,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    color: '#888',
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 8,
  },
  emptySubtext: {
    color: '#666',
    fontSize: 14,
  },
  campaignCard: {
    backgroundColor: '#0a0a0a',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#1a1a1a',
  },
  campaignHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  campaignName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    flex: 1,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 10,
  },
  statusBadgeActive: {
    backgroundColor: '#042821',
  },
  statusBadgeDraft: {
    backgroundColor: '#2a2a0a',
  },
  statusBadgeCompleted: {
    backgroundColor: '#0a0a2a',
  },
  statusText: {
    color: '#00c896',
    fontSize: 11,
    fontWeight: '600',
  },
  campaignMeta: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metaText: {
    color: '#888',
    fontSize: 13,
  },
  metaSeparator: {
    color: '#444',
    marginHorizontal: 8,
  },
  launchedText: {
    color: '#666',
    fontSize: 12,
    marginTop: 8,
  },
})
```

Continue with more screens in next file...
