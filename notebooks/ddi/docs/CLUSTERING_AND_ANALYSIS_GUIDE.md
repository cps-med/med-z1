# Clustering and Analysis Guide
## Understanding the Next Phase of the DDI Risk Analysis Pipeline

---

## Overview

This guide prepares you for building **05_clustering.ipynb** and **06_analysis.ipynb**, the critical discovery and insight generation phase of your DDI risk analysis project.

**Current Position in Pipeline:**
```
✅ 01a/b/c: Data Preparation (Raw data extraction)
✅ 02: Exploration (Understanding the data)
✅ 03: Cleaning (Data quality and standardization)
✅ 04: Feature Engineering (Patient & DDI pair features)
→ 05: Clustering (Discover patient risk groups)
→ 06: Analysis (Deep dive into patterns and insights)
→ 07+: Modeling (Predictive models, risk scoring)
```

**What You've Built So Far:**
- **Patient-level features**: 19 features per patient (demographics, medication profile, DDI risk)
- **DDI pair-level features**: Detailed interaction characteristics with patient context

**What's Next:**
- Use these features to **discover natural patient groupings** (clustering)
- **Analyze patterns** to generate clinical insights
- **Prepare for modeling** by understanding data structure and relationships

---

## Table of Contents

1. [What is Clustering and Why Does It Matter?](#what-is-clustering-and-why-does-it-matter)
2. [What is Analysis in ML Context?](#what-is-analysis-in-ml-context)
3. [Notebook 05: Clustering Goals and Approach](#notebook-05-clustering-goals-and-approach)
4. [Notebook 06: Analysis Goals and Approach](#notebook-06-analysis-goals-and-approach)
5. [How These Notebooks Set Up Modeling](#how-these-notebooks-set-up-modeling)
6. [Learning: Clustering Fundamentals](#learning-clustering-fundamentals)
7. [Learning: Analysis Techniques](#learning-analysis-techniques)
8. [Practical Implementation Plan](#practical-implementation-plan)
9. [Expected Outputs and Deliverables](#expected-outputs-and-deliverables)
10. [Success Criteria](#success-criteria)

---

## What is Clustering and Why Does It Matter?

### The Clustering Concept

**Clustering** is an unsupervised machine learning technique that groups similar data points together based on their features, without being told what the groups should be.

**Analogy: Organizing a Library**

Imagine you walk into a library where thousands of books are scattered randomly. You're asked to organize them into sections, but nobody tells you what sections to create. You might naturally group them by:
- Fiction vs. Non-fiction
- Subject matter (science, history, art)
- Reading level (children's, adult)
- Book size (reference books vs. paperbacks)

Clustering does the same thing with data - it finds natural groupings based on similarity.

### Why Clustering Matters for Healthcare

In healthcare, clustering helps answer questions like:
- **"Are there distinct patient risk profiles?"** - Not all patients are the same. Some may be elderly with polypharmacy, others young with acute medication needs.
- **"Can we identify patient subgroups needing different interventions?"** - A one-size-fits-all approach rarely works. Clustering reveals which patients need intensive monitoring vs. routine care.
- **"What patterns exist that we didn't know to look for?"** - Sometimes the most valuable insights come from discovering groups you didn't expect.

### Clustering vs. Classification (Key Difference)

**Classification (Supervised Learning):**
- You have labeled data: "This patient is high-risk", "This patient is low-risk"
- Model learns to predict labels for new patients
- Requires knowing the answer ahead of time

**Clustering (Unsupervised Learning):**
- No labels - you don't know the groups beforehand
- Algorithm discovers natural groupings in the data
- Exploratory - helps you understand data structure
- Often reveals groups that are more nuanced than simple "high/low risk"

**Example:**
```
Classification approach:
  IF ddi_pair_count > 5 THEN high_risk ELSE low_risk
  → Binary, pre-defined

Clustering approach:
  Group patients by ALL features simultaneously
  → Discovers: "Elderly polypharmacy", "Young acute care",
              "Middle-age chronic", "Fragmented care" groups
  → Rich, data-driven insights
```

### What Clustering Will Reveal About Your DDI Data

Based on your features, clustering might discover patient groups like:

**Hypothetical Cluster 1: "Elderly High-Risk Polypharmacy"**
- Age: 70-85
- Unique medications: 8-12
- DDI pair count: 6-10
- High-severity DDIs: 1-2
- Source diversity: Multiple systems (VA + community care)
- Clinical need: Intensive medication review, care coordination

**Hypothetical Cluster 2: "Young Low-Risk Simple Regimens"**
- Age: 25-45
- Unique medications: 1-3
- DDI pair count: 0-1
- Low-severity DDIs only
- Source diversity: Single system
- Clinical need: Routine monitoring

**Hypothetical Cluster 3: "Middle-Age Moderate Complexity"**
- Age: 50-65
- Unique medications: 4-6
- DDI pair count: 2-4
- Moderate-severity DDIs: 1-2
- Source diversity: Mostly single system
- Clinical need: Periodic medication review

These clusters help you:
- **Allocate resources efficiently** - Focus on high-risk groups
- **Tailor interventions** - Different strategies for different groups
- **Understand your population** - Who are you actually treating?
- **Generate hypotheses** - "Why does this group have high DDI risk?"

---

## What is Analysis in ML Context?

### Analysis as the Bridge Between Discovery and Prediction

**Analysis** in machine learning is the systematic investigation of patterns, relationships, and insights in your data. It's where you transition from "what groups exist?" (clustering) to "why do these patterns occur and what do they mean?" (understanding).

### The Analysis Mindset

Analysis is asking and answering targeted questions:

**Descriptive Questions** (What is happening?):
- What is the distribution of DDI severity across patients?
- How many patients have polypharmacy?
- What are the most common drug-drug interaction pairs?

**Diagnostic Questions** (Why is it happening?):
- Why do elderly patients have more DDIs?
- Are certain medication combinations driving high risk?
- Does fragmented care (multiple systems) increase DDI risk?

**Comparative Questions** (How do groups differ?):
- Do clusters identified in 05_clustering differ in clinical outcomes?
- Are DDI patterns different between age groups?
- How does gender affect DDI risk profiles?

**Relational Questions** (What's connected?):
- Is there a correlation between age and DDI density?
- Do certain drug classes frequently appear together in high-risk patients?
- Are temporal patterns (when drugs are started) related to DDI emergence?

### Why Analysis Matters Before Modeling

Think of analysis as "reconnaissance before battle":

**Without Analysis:**
- Build model blindly → Poor performance → Don't know why
- Miss important patterns → Model doesn't capture them
- Include irrelevant features → Model is noisy and slow
- Misinterpret results → Draw wrong conclusions

**With Analysis:**
- Understand data structure → Choose right model architecture
- Identify key relationships → Feature selection and engineering
- Detect data issues → Fix before modeling (outliers, imbalance)
- Generate hypotheses → Test them with modeling

**Example from DDI Project:**

Suppose analysis reveals:
- **Finding 1**: "90% of high-severity DDIs involve only 10 specific drug pairs"
- **Finding 2**: "Elderly patients (65+) have 3x higher DDI density than younger patients"
- **Finding 3**: "Patients with medications from 2+ sources have 2x more DDIs"

**How This Informs Modeling:**
- **Finding 1** → Create "high-risk drug pair" feature, build drug-pair-specific models
- **Finding 2** → Age-stratified models, age interaction terms in predictions
- **Finding 3** → "Care fragmentation" feature, alert system for multi-source patients

### Analysis Outputs

Good analysis produces:
1. **Visualizations** - Charts, plots, heatmaps that reveal patterns
2. **Summary statistics** - Means, medians, distributions by group
3. **Statistical tests** - Hypothesis testing (e.g., "Are cluster differences significant?")
4. **Clinical insights** - Actionable findings for healthcare providers
5. **Modeling recommendations** - What to build next and how

---

## Notebook 05: Clustering Goals and Approach

### Primary Goals

**Goal 1: Discover Natural Patient Risk Groups**
- Use unsupervised learning to identify patient subpopulations with similar DDI risk profiles
- Avoid pre-defined categories - let the data reveal patterns
- Create interpretable, clinically meaningful clusters

**Goal 2: Characterize Each Cluster**
- What are the defining features of each group?
- How many patients are in each cluster?
- What are the clinical characteristics?

**Goal 3: Validate Cluster Quality**
- Are clusters well-separated and internally cohesive?
- Do clusters make clinical sense?
- Are they stable (reproducible)?

**Goal 4: Assign Cluster Labels to Patients**
- Add cluster membership as a feature for downstream analysis and modeling
- Save clustered patient data for use in 06_analysis and future modeling

### Clustering Approach

#### Step 1: Data Preparation for Clustering

**Load Patient Features:**
```python
# Load the engineered patient-level features
patient_features = pd.read_parquet(
    f"s3://{bucket}/v3_features/ddi/patients_features.parquet"
)
```

**Select Clustering Features:**

Not all features should be used for clustering. You'll select features based on:
- **Clinical relevance** - Features that matter for risk stratification
- **Variability** - Features that differ across patients (constant features don't help)
- **Scale** - Avoid features that are just transformations of others (e.g., don't use both `Age` and `IsElderly`)

**Recommended Feature Selection:**
```python
clustering_features = [
    # Demographics
    'Age',
    'Gender',  # Will need encoding

    # Medication profile
    'unique_medications',
    'medication_diversity',
    'avg_medications_per_day',

    # Temporal
    'medication_timespan_days',

    # Source system
    'source_diversity',

    # DDI risk
    'ddi_pair_count',
    'ddi_severity_High',
    'ddi_severity_Moderate',
    'total_ddi_risk_score',
    'ddi_density',
    'max_severity_level'
]
```

**Feature Preprocessing:**
```python
# 1. Handle categorical variables (Gender)
#    Convert to numeric: M=1, F=0, U=-1 (or use one-hot encoding)

# 2. Handle missing values
#    Check for NaN, decide on imputation strategy

# 3. Scale features
#    Clustering algorithms (like K-means) are sensitive to scale
#    Standardize: (X - mean) / std
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

**Why Scaling Matters:**

Without scaling:
- `medication_timespan_days` ranges from 1-1000
- `ddi_density` ranges from 0-1
- K-means will be dominated by `medication_timespan_days` because it's numerically larger

With scaling:
- All features have mean=0, std=1
- Each feature contributes equally to clustering

#### Step 2: Determine Optimal Number of Clusters

**The Challenge:** Clustering algorithms need you to specify how many clusters to create (for K-means). How do you decide?

**Methods:**

**A. Elbow Method**
- Run K-means with k=2, 3, 4, 5, ..., 10 clusters
- Calculate "inertia" (within-cluster sum of squares) for each k
- Plot inertia vs. k
- Look for "elbow" - where adding more clusters doesn't help much

```python
from sklearn.cluster import KMeans

inertias = []
K_range = range(2, 11)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)

# Plot
plt.plot(K_range, inertias, marker='o')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Inertia')
plt.title('Elbow Method')
```

**Elbow at k=4** suggests 4 clusters is optimal.

**B. Silhouette Score**
- Measures how similar each point is to its own cluster vs. other clusters
- Score ranges from -1 (wrong cluster) to +1 (perfect cluster)
- Higher average silhouette score = better clustering

```python
from sklearn.metrics import silhouette_score

silhouette_scores = []

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(X_scaled)
    score = silhouette_score(X_scaled, labels)
    silhouette_scores.append(score)

# Plot
plt.plot(K_range, silhouette_scores, marker='o')
```

**Peak at k=4** confirms 4 clusters.

**C. Clinical Intuition**
- How many groups make sense clinically?
- Are clusters interpretable?
- Can you act on this many groups?

**For DDI Risk, You Might Expect:**
- 3-5 clusters (e.g., Low risk, Moderate risk, High risk, Elderly high-complexity)

#### Step 3: Apply Clustering Algorithm

**Primary Algorithm: K-Means**

K-means is the most common clustering algorithm. It works by:
1. Randomly placing k "centroids" (cluster centers)
2. Assigning each patient to nearest centroid
3. Moving centroids to the average position of assigned patients
4. Repeating until centroids stop moving

**Implementation:**
```python
# Based on elbow/silhouette analysis, use k=4
optimal_k = 4

kmeans = KMeans(
    n_clusters=optimal_k,
    random_state=42,  # For reproducibility
    n_init=10,        # Run 10 times with different initializations
    max_iter=300      # Maximum iterations
)

# Fit and predict
cluster_labels = kmeans.fit_predict(X_scaled)

# Add cluster labels to original dataframe
patient_features['cluster'] = cluster_labels
```

**Alternative Algorithm: Hierarchical Clustering**

Hierarchical clustering creates a tree (dendrogram) of clusters. Useful for:
- Visualizing nested groupings
- Not needing to specify k upfront

```python
from scipy.cluster.hierarchy import dendrogram, linkage

# Create linkage matrix
linkage_matrix = linkage(X_scaled, method='ward')

# Plot dendrogram
plt.figure(figsize=(12, 6))
dendrogram(linkage_matrix)
plt.title('Hierarchical Clustering Dendrogram')
```

**When to Use Each:**
- **K-means**: Fast, works well with large datasets, produces spherical clusters
- **Hierarchical**: Better for irregular cluster shapes, provides hierarchy visualization
- **DBSCAN**: Finds arbitrary-shaped clusters, identifies outliers (useful if you have unusual patients)

#### Step 4: Characterize and Name Clusters

**For Each Cluster, Calculate:**
- Mean and median of each feature
- Count of patients
- Percentage of total population

```python
# Cluster characterization
cluster_summary = patient_features.groupby('cluster').agg({
    'Age': ['mean', 'median'],
    'unique_medications': ['mean', 'median'],
    'ddi_pair_count': ['mean', 'median'],
    'total_ddi_risk_score': ['mean', 'median'],
    'is_polypharmacy': 'sum',
    'is_high_ddi_risk': 'sum',
    'IsElderly': 'sum',
    'PatientSID': 'count'  # Number of patients
})

print(cluster_summary)
```

**Example Output:**
```
Cluster 0:
  - Age: 73 (mean), unique_medications: 9, ddi_pair_count: 7
  - 85% elderly, 90% polypharmacy, 80% high DDI risk
  - 1,250 patients (25% of population)
  → Name: "Elderly High-Risk Polypharmacy"

Cluster 1:
  - Age: 35 (mean), unique_medications: 2, ddi_pair_count: 0
  - 5% elderly, 10% polypharmacy, 5% high DDI risk
  - 2,000 patients (40% of population)
  → Name: "Young Low-Risk Simple Regimens"

Cluster 2:
  - Age: 58 (mean), unique_medications: 5, ddi_pair_count: 3
  - 35% elderly, 60% polypharmacy, 40% high DDI risk
  - 1,500 patients (30% of population)
  → Name: "Middle-Age Moderate Complexity"

Cluster 3:
  - Age: 68 (mean), unique_medications: 4, ddi_pair_count: 5
  - 70% elderly, 50% polypharmacy, 75% high DDI risk
  - 250 patients (5% of population)
  → Name: "Fragmented Care High-Risk"
```

**Assign Meaningful Names:**
```python
cluster_names = {
    0: "Elderly High-Risk Polypharmacy",
    1: "Young Low-Risk Simple Regimens",
    2: "Middle-Age Moderate Complexity",
    3: "Fragmented Care High-Risk"
}

patient_features['cluster_name'] = patient_features['cluster'].map(cluster_names)
```

#### Step 5: Visualize Clusters

**Dimensionality Reduction for Visualization**

Problem: You have 14 clustering features - can't visualize 14 dimensions.

Solution: Use **PCA (Principal Component Analysis)** or **t-SNE** to reduce to 2D for plotting.

**PCA Approach:**
```python
from sklearn.decomposition import PCA

# Reduce to 2 principal components
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# Plot
plt.figure(figsize=(10, 8))
scatter = plt.scatter(
    X_pca[:, 0],
    X_pca[:, 1],
    c=cluster_labels,
    cmap='viridis',
    alpha=0.6
)
plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)')
plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
plt.title('Patient Clusters (PCA Projection)')
plt.colorbar(scatter, label='Cluster')
```

**What This Shows:**
- Each point is a patient
- Color = cluster membership
- Spatial proximity = similarity in features
- Well-separated clusters = good clustering quality

**t-SNE Alternative:**
```python
from sklearn.manifold import TSNE

# t-SNE is better at preserving local structure
tsne = TSNE(n_components=2, random_state=42, perplexity=30)
X_tsne = tsne.fit_transform(X_scaled)

# Plot similarly
```

**Additional Visualizations:**
- **Heatmap of cluster characteristics**
- **Bar charts comparing clusters on key features**
- **Box plots of DDI risk by cluster**

#### Step 6: Validate Clusters

**Internal Validation:**
- **Silhouette score** (already calculated): How well-separated are clusters?
- **Davies-Bouldin Index**: Lower is better (measures cluster separation)
- **Calinski-Harabasz Index**: Higher is better (ratio of between-cluster to within-cluster variance)

**External Validation (Clinical Sensibility):**
- Do clusters align with clinical knowledge?
- Are they actionable?
- Can clinicians understand and trust them?

**Stability Validation:**
- Re-run clustering with different random seeds
- Do you get similar clusters?
- Bootstrap sampling - cluster on random subsets, check consistency

#### Step 7: Save Clustered Data

```python
# Save patient features with cluster assignments
output_uri = f"s3://{bucket}/v3_features/ddi/patients_features_clustered.parquet"
patient_features.to_parquet(output_uri, filesystem=fs, index=False)

# Also save cluster characterization summary
cluster_summary.to_csv('results/cluster_summary.csv')
```

### Expected Outputs from 05_clustering.ipynb

1. **Clustered patient dataset** - Original features + cluster labels
2. **Cluster characterization report** - Mean/median features per cluster
3. **Visualizations** - PCA/t-SNE plots, heatmaps, bar charts
4. **Validation metrics** - Silhouette scores, elbow plots
5. **Clinical interpretation** - Named clusters with descriptions

---

## Notebook 06: Analysis Goals and Approach

### Primary Goals

**Goal 1: Deep Dive into DDI Patterns**
- What are the most common drug-drug interactions?
- Which drug pairs appear most frequently in high-risk patients?
- What interaction types dominate (bleeding risk, QT prolongation, etc.)?

**Goal 2: Analyze Patient Risk Distribution**
- How is DDI risk distributed across the population?
- What percentage of patients are high-risk?
- How do demographic factors (age, gender) relate to risk?

**Goal 3: Validate and Interpret Clusters**
- Are the clusters from 05_clustering clinically distinct?
- How do clusters differ in outcomes (if you have outcome data)?
- What drives membership in each cluster?

**Goal 4: Identify High-Value Intervention Targets**
- Which patient groups need immediate attention?
- Which drug pairs should be flagged for medication review?
- Where can interventions have the most impact?

**Goal 5: Generate Hypotheses for Modeling**
- What relationships should predictive models capture?
- Which features are most predictive of high DDI risk?
- Are there non-linear relationships or interactions between features?

### Analysis Approach

#### Part 1: Descriptive Statistics and Distributions

**1A: Overall DDI Risk Distribution**

```python
# Load patient features (clustered)
patient_features = pd.read_parquet(
    f"s3://{bucket}/v3_features/ddi/patients_features_clustered.parquet"
)

# Summary statistics
print("DDI Risk Score Distribution:")
print(patient_features['total_ddi_risk_score'].describe())

# Histogram of risk scores
plt.figure(figsize=(10, 6))
plt.hist(patient_features['total_ddi_risk_score'], bins=30, edgecolor='black')
plt.xlabel('Total DDI Risk Score')
plt.ylabel('Number of Patients')
plt.title('Distribution of DDI Risk Scores')
```

**Questions to Answer:**
- Is risk normally distributed or skewed?
- How many patients have zero risk vs. high risk?
- What's the median risk in the population?

**1B: Demographics Analysis**

```python
# Age distribution
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.hist(patient_features['Age'], bins=20, edgecolor='black')
plt.xlabel('Age')
plt.ylabel('Number of Patients')
plt.title('Age Distribution')

plt.subplot(1, 2, 2)
patient_features['AgeGroup'].value_counts().sort_index().plot(kind='bar')
plt.xlabel('Age Group')
plt.ylabel('Number of Patients')
plt.title('Patients by Age Group')
```

**Gender breakdown:**
```python
gender_summary = patient_features.groupby('Gender').agg({
    'PatientSID': 'count',
    'total_ddi_risk_score': 'mean',
    'is_high_ddi_risk': 'sum'
})
print(gender_summary)
```

**1C: Medication Profile Analysis**

```python
# Polypharmacy prevalence
polypharmacy_rate = patient_features['is_polypharmacy'].mean()
print(f"Polypharmacy rate: {polypharmacy_rate:.1%}")

# Distribution of medication counts
plt.figure(figsize=(10, 6))
plt.hist(patient_features['unique_medications'], bins=range(1, 20), edgecolor='black')
plt.xlabel('Number of Unique Medications')
plt.ylabel('Number of Patients')
plt.title('Distribution of Medication Counts')
plt.axvline(x=5, color='red', linestyle='--', label='Polypharmacy threshold (5+)')
plt.legend()
```

**1D: DDI Severity Breakdown**

```python
# Severity distribution
severity_summary = patient_features[[
    'ddi_severity_High',
    'ddi_severity_Moderate',
    'ddi_severity_Low'
]].sum()

severity_summary.plot(kind='bar', color=['red', 'orange', 'yellow'])
plt.ylabel('Total Count Across All Patients')
plt.title('DDI Count by Severity Level')
```

#### Part 2: Cluster Analysis and Comparison

**2A: Cluster Size and Distribution**

```python
# How many patients in each cluster?
cluster_counts = patient_features['cluster_name'].value_counts()
print(cluster_counts)

# Pie chart
cluster_counts.plot(kind='pie', autopct='%1.1f%%', figsize=(8, 8))
plt.title('Patient Distribution Across Clusters')
```

**2B: Compare Clusters on Key Metrics**

```python
# Group by cluster and calculate means
cluster_comparison = patient_features.groupby('cluster_name').agg({
    'Age': 'mean',
    'unique_medications': 'mean',
    'ddi_pair_count': 'mean',
    'total_ddi_risk_score': 'mean',
    'ddi_density': 'mean',
    'is_polypharmacy': lambda x: (x.sum() / len(x) * 100),  # Percentage
    'is_high_ddi_risk': lambda x: (x.sum() / len(x) * 100),
    'IsElderly': lambda x: (x.sum() / len(x) * 100)
})

print(cluster_comparison)
```

**Visualize cluster differences:**
```python
# Heatmap of cluster characteristics
import seaborn as sns

plt.figure(figsize=(12, 8))
sns.heatmap(
    cluster_comparison.T,  # Transpose so features are rows
    annot=True,            # Show values
    fmt='.1f',             # Format as decimal
    cmap='YlOrRd',         # Color map
    cbar_kws={'label': 'Value'}
)
plt.title('Cluster Characteristics Heatmap')
plt.xlabel('Cluster')
plt.ylabel('Feature')
```

**2C: Statistical Testing - Are Clusters Significantly Different?**

```python
from scipy.stats import f_oneway

# Test if mean DDI risk scores differ across clusters
cluster_groups = [
    patient_features[patient_features['cluster'] == i]['total_ddi_risk_score']
    for i in range(optimal_k)
]

f_stat, p_value = f_oneway(*cluster_groups)
print(f"ANOVA F-statistic: {f_stat:.2f}, p-value: {p_value:.4f}")

if p_value < 0.05:
    print("✅ Clusters have significantly different mean DDI risk scores")
else:
    print("❌ No significant difference between clusters")
```

**2D: Cluster Profiles (Radar Charts)**

```python
# Select key features for radar chart
features_for_radar = [
    'Age',
    'unique_medications',
    'ddi_pair_count',
    'total_ddi_risk_score',
    'ddi_density'
]

# Normalize features to 0-1 scale for radar chart
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()

normalized_features = patient_features.groupby('cluster_name')[features_for_radar].mean()
normalized_features = pd.DataFrame(
    scaler.fit_transform(normalized_features),
    columns=features_for_radar,
    index=normalized_features.index
)

# Create radar chart (polar plot)
# [Implementation of radar chart visualization]
```

#### Part 3: DDI Pair-Level Analysis

**3A: Most Common Drug Interactions**

```python
# Load DDI pair-level features
ddi_pairs = pd.read_parquet(
    f"s3://{bucket}/v3_features/ddi/ddi_pairs_features.parquet"
)

# Top 10 most common drug pairs
top_pairs = ddi_pairs.groupby(['Drug1', 'Drug2', 'Severity']).size() \
    .reset_index(name='count') \
    .sort_values('count', ascending=False) \
    .head(10)

print(top_pairs)
```

**3B: High-Risk Drug Pairs (High Severity)**

```python
# Filter to high-severity DDIs only
high_severity_ddis = ddi_pairs[ddi_pairs['Severity'] == 'High']

# Most common high-severity pairs
high_risk_pairs = high_severity_ddis.groupby(['Drug1', 'Drug2']).size() \
    .reset_index(name='count') \
    .sort_values('count', ascending=False) \
    .head(10)

# Visualize
plt.figure(figsize=(12, 6))
pair_labels = [f"{row['Drug1']} + {row['Drug2']}" for _, row in high_risk_pairs.iterrows()]
plt.barh(pair_labels, high_risk_pairs['count'])
plt.xlabel('Number of Patients Affected')
plt.title('Top 10 Most Common High-Severity Drug-Drug Interactions')
plt.gca().invert_yaxis()
```

**3C: Interaction Types Analysis**

```python
# Most common interaction types
interaction_type_counts = ddi_pairs['interaction_type'].value_counts()
print(interaction_type_counts)

# Visualize
plt.figure(figsize=(10, 6))
interaction_type_counts.head(10).plot(kind='barh')
plt.xlabel('Number of DDI Pairs')
plt.title('Top 10 Most Common Interaction Types')
plt.gca().invert_yaxis()
```

**Questions to Answer:**
- Is "Bleeding Risk" the dominant interaction type?
- Are there rare but severe interaction types to watch?
- Which types appear most in elderly vs. young patients?

**3D: Temporal Overlap Analysis**

```python
# How many DDI pairs have temporal overlap (concurrent use)?
overlap_rate = ddi_pairs['temporal_overlap'].mean()
print(f"Temporal overlap rate: {overlap_rate:.1%}")

# Does severity correlate with temporal overlap?
overlap_by_severity = ddi_pairs.groupby('Severity')['temporal_overlap'].mean()
print(overlap_by_severity)
```

**Clinical Insight:**
If only 60% of DDI pairs have temporal overlap, then 40% are "potential" DDIs (drugs not taken concurrently). This affects risk assessment!

#### Part 4: Demographic and Risk Relationship Analysis

**4A: Age vs. DDI Risk**

```python
# Scatter plot
plt.figure(figsize=(10, 6))
plt.scatter(
    patient_features['Age'],
    patient_features['total_ddi_risk_score'],
    alpha=0.5,
    s=10
)
plt.xlabel('Age (years)')
plt.ylabel('Total DDI Risk Score')
plt.title('Age vs. DDI Risk Score')

# Add trend line
from numpy.polynomial.polynomial import Polynomial
p = Polynomial.fit(patient_features['Age'], patient_features['total_ddi_risk_score'], deg=1)
x_trend = np.linspace(patient_features['Age'].min(), patient_features['Age'].max(), 100)
plt.plot(x_trend, p(x_trend), 'r--', label='Trend line')
plt.legend()
```

**Correlation analysis:**
```python
correlation = patient_features['Age'].corr(patient_features['total_ddi_risk_score'])
print(f"Correlation between Age and DDI Risk: {correlation:.3f}")
```

**4B: Age Group Comparison**

```python
# Box plot by age group
plt.figure(figsize=(12, 6))
patient_features.boxplot(
    column='total_ddi_risk_score',
    by='AgeGroup',
    figsize=(12, 6)
)
plt.xlabel('Age Group')
plt.ylabel('Total DDI Risk Score')
plt.title('DDI Risk Distribution by Age Group')
plt.suptitle('')  # Remove default title
```

**Statistical test:**
```python
# Are elderly patients significantly higher risk?
elderly_risk = patient_features[patient_features['IsElderly'] == 1]['total_ddi_risk_score']
non_elderly_risk = patient_features[patient_features['IsElderly'] == 0]['total_ddi_risk_score']

from scipy.stats import ttest_ind
t_stat, p_value = ttest_ind(elderly_risk, non_elderly_risk)

print(f"Mean DDI risk - Elderly: {elderly_risk.mean():.2f}")
print(f"Mean DDI risk - Non-elderly: {non_elderly_risk.mean():.2f}")
print(f"T-test p-value: {p_value:.4f}")

if p_value < 0.05:
    print("✅ Elderly patients have significantly higher DDI risk")
```

**4C: Gender Analysis**

```python
# DDI risk by gender
gender_risk = patient_features.groupby('Gender').agg({
    'total_ddi_risk_score': ['mean', 'median', 'std'],
    'ddi_pair_count': 'mean',
    'is_high_ddi_risk': lambda x: (x.sum() / len(x) * 100)
})

print(gender_risk)

# Visualize
plt.figure(figsize=(10, 6))
patient_features.boxplot(
    column='total_ddi_risk_score',
    by='Gender',
    figsize=(10, 6)
)
plt.xlabel('Gender')
plt.ylabel('Total DDI Risk Score')
plt.title('DDI Risk by Gender')
plt.suptitle('')
```

**4D: Polypharmacy Analysis**

```python
# Compare polypharmacy vs. non-polypharmacy patients
polypharmacy_comparison = patient_features.groupby('is_polypharmacy').agg({
    'unique_medications': 'mean',
    'ddi_pair_count': 'mean',
    'total_ddi_risk_score': 'mean',
    'is_high_ddi_risk': lambda x: (x.sum() / len(x) * 100),
    'PatientSID': 'count'
})

print(polypharmacy_comparison)

# What percentage of polypharmacy patients have high DDI risk?
polypharmacy_high_risk_rate = patient_features[
    patient_features['is_polypharmacy'] == 1
]['is_high_ddi_risk'].mean()

print(f"High DDI risk rate among polypharmacy patients: {polypharmacy_high_risk_rate:.1%}")
```

#### Part 5: Feature Importance and Correlation Analysis

**5A: Correlation Matrix**

```python
# Select numeric features
numeric_features = patient_features.select_dtypes(include=[np.number]).columns

# Calculate correlation matrix
correlation_matrix = patient_features[numeric_features].corr()

# Heatmap
plt.figure(figsize=(14, 12))
sns.heatmap(
    correlation_matrix,
    annot=True,
    fmt='.2f',
    cmap='coolwarm',
    center=0,
    square=True,
    linewidths=0.5
)
plt.title('Feature Correlation Matrix')
```

**What to Look For:**
- **High correlations** (>0.7): Redundant features? (e.g., `ddi_pair_count` and `total_ddi_risk_score`)
- **Unexpected correlations**: Interesting relationships to investigate
- **Correlations with target** (if you define a target like `is_high_ddi_risk`): Which features are most predictive?

**5B: Feature Distributions by Risk Level**

```python
# Compare feature distributions for high-risk vs. low-risk patients
high_risk = patient_features[patient_features['is_high_ddi_risk'] == 1]
low_risk = patient_features[patient_features['is_high_ddi_risk'] == 0]

# Compare key features
features_to_compare = ['Age', 'unique_medications', 'medication_diversity', 'source_diversity']

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.ravel()

for i, feature in enumerate(features_to_compare):
    axes[i].hist(low_risk[feature], bins=20, alpha=0.5, label='Low Risk', color='green')
    axes[i].hist(high_risk[feature], bins=20, alpha=0.5, label='High Risk', color='red')
    axes[i].set_xlabel(feature)
    axes[i].set_ylabel('Number of Patients')
    axes[i].set_title(f'{feature} Distribution by Risk Level')
    axes[i].legend()

plt.tight_layout()
```

**5C: Logistic Regression for Feature Importance**

Even though you're not building a full predictive model yet, a simple logistic regression can reveal which features are most associated with high DDI risk.

```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# Prepare data
X = patient_features[clustering_features].copy()
# Handle categorical (Gender)
X['Gender'] = X['Gender'].map({'M': 1, 'F': 0, 'U': -1})
X = X.fillna(X.median())  # Simple imputation

y = patient_features['is_high_ddi_risk']

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Fit logistic regression
lr = LogisticRegression(random_state=42, max_iter=1000)
lr.fit(X_scaled, y)

# Feature importance (coefficients)
feature_importance = pd.DataFrame({
    'feature': clustering_features,
    'coefficient': lr.coef_[0]
}).sort_values('coefficient', key=abs, ascending=False)

print(feature_importance)

# Visualize
plt.figure(figsize=(10, 8))
plt.barh(feature_importance['feature'], feature_importance['coefficient'])
plt.xlabel('Coefficient (Feature Importance)')
plt.title('Features Associated with High DDI Risk')
plt.axvline(x=0, color='black', linestyle='--')
```

**Interpretation:**
- **Positive coefficient**: Feature increases likelihood of high DDI risk
- **Negative coefficient**: Feature decreases likelihood
- **Large absolute value**: Strong association

#### Part 6: Actionable Insights and Intervention Targets

**6A: High-Risk Patient Identification**

```python
# Define "very high risk" patients (e.g., top 10% by risk score)
risk_threshold = patient_features['total_ddi_risk_score'].quantile(0.90)

very_high_risk = patient_features[
    patient_features['total_ddi_risk_score'] >= risk_threshold
]

print(f"Very high-risk patients (top 10%): {len(very_high_risk)}")
print(f"Mean age: {very_high_risk['Age'].mean():.1f}")
print(f"Mean medications: {very_high_risk['unique_medications'].mean():.1f}")
print(f"Mean DDI pairs: {very_high_risk['ddi_pair_count'].mean():.1f}")

# What clusters are they in?
very_high_risk['cluster_name'].value_counts()
```

**6B: Drug Pairs Requiring Review**

```python
# Identify high-severity DDIs affecting many patients
high_impact_ddis = ddi_pairs[ddi_pairs['Severity'] == 'High'].groupby(
    ['Drug1', 'Drug2', 'interaction_type']
).agg({
    'PatientSID': 'count',
    'patient_is_elderly': 'sum'  # How many are elderly?
}).reset_index().rename(columns={'PatientSID': 'patient_count'})

high_impact_ddis = high_impact_ddis.sort_values('patient_count', ascending=False)

print("Top 10 high-severity DDIs by patient count:")
print(high_impact_ddis.head(10))

# Export for clinical review
high_impact_ddis.to_csv('results/high_impact_ddis_for_review.csv', index=False)
```

**6C: Cluster-Specific Interventions**

Based on cluster analysis, define targeted interventions:

```python
# Example intervention mapping
interventions = {
    "Elderly High-Risk Polypharmacy": [
        "Comprehensive medication review (CMR)",
        "Pharmacist consultation",
        "Deprescribing evaluation",
        "Monthly monitoring"
    ],
    "Young Low-Risk Simple Regimens": [
        "Standard monitoring",
        "Patient education on new medications"
    ],
    "Middle-Age Moderate Complexity": [
        "Periodic medication review (quarterly)",
        "DDI screening at new prescription"
    ],
    "Fragmented Care High-Risk": [
        "Care coordination between VA and non-VA providers",
        "Centralized medication reconciliation",
        "Shared medication list across systems"
    ]
}

# Create intervention plan dataframe
intervention_plan = []
for cluster_name in patient_features['cluster_name'].unique():
    cluster_size = (patient_features['cluster_name'] == cluster_name).sum()
    intervention_plan.append({
        'Cluster': cluster_name,
        'Patient Count': cluster_size,
        'Interventions': '; '.join(interventions.get(cluster_name, ['Standard care']))
    })

intervention_df = pd.DataFrame(intervention_plan)
print(intervention_df)

# Save
intervention_df.to_csv('results/cluster_intervention_plan.csv', index=False)
```

#### Part 7: Hypotheses for Modeling

**Document findings that inform future modeling:**

```python
# Create a summary of modeling hypotheses
modeling_hypotheses = """
MODELING HYPOTHESES FROM ANALYSIS (for 07_modeling.ipynb)

1. AGE IS A STRONG PREDICTOR OF DDI RISK
   - Correlation: {age_corr:.3f}
   - Elderly patients have {elderly_risk_factor:.1f}x higher mean risk
   - Recommendation: Include Age and IsElderly features; consider age-stratified models

2. POLYPHARMACY DRIVES DDI RISK
   - Polypharmacy patients have {polypharmacy_risk_factor:.1f}x higher mean risk
   - Recommendation: unique_medications is key feature; explore polynomial terms

3. TOP 10 DRUG PAIRS ACCOUNT FOR {top_pairs_pct:.1f}% OF HIGH-SEVERITY DDIs
   - Recommendation: Create binary features for these specific pairs

4. CLUSTERS ARE CLINICALLY DISTINCT
   - Silhouette score: {silhouette:.3f}
   - ANOVA p-value: {anova_p:.4f}
   - Recommendation: Use cluster labels as features in predictive models

5. GENDER SHOWS {gender_effect}
   - Recommendation: {gender_recommendation}

6. TEMPORAL OVERLAP MATTERS
   - Only {overlap_rate:.1%} of DDI pairs have concurrent use
   - Recommendation: Incorporate temporal features in predictions

7. SOURCE DIVERSITY LINKED TO RISK
   - Multi-source patients have {source_risk_factor:.1f}x higher risk
   - Recommendation: Flag fragmented care as risk factor
"""

# Fill in actual values
modeling_hypotheses_filled = modeling_hypotheses.format(
    age_corr=correlation,
    elderly_risk_factor=elderly_risk.mean() / non_elderly_risk.mean(),
    polypharmacy_risk_factor=polypharmacy_comparison.loc[1, 'total_ddi_risk_score'] /
                             polypharmacy_comparison.loc[0, 'total_ddi_risk_score'],
    top_pairs_pct=(high_risk_pairs['count'].sum() / len(high_severity_ddis) * 100),
    silhouette=silhouette_scores[optimal_k - 2],  # From clustering
    anova_p=p_value,
    gender_effect="minimal difference" if gender_p_value > 0.05 else "significant difference",
    gender_recommendation="Gender may not be critical predictor" if gender_p_value > 0.05
                          else "Include Gender feature",
    overlap_rate=overlap_rate,
    source_risk_factor=1.5  # Calculate from actual data
)

# Save
with open('results/modeling_hypotheses.txt', 'w') as f:
    f.write(modeling_hypotheses_filled)

print(modeling_hypotheses_filled)
```

### Expected Outputs from 06_analysis.ipynb

1. **Descriptive statistics report** - Population-level DDI risk summary
2. **Cluster validation** - Statistical tests, characterization tables
3. **Visualizations** - 20+ charts (distributions, comparisons, correlations)
4. **High-risk patient list** - Top 10% risk patients for intervention
5. **Drug pair priority list** - High-impact DDIs for medication review
6. **Intervention plan** - Cluster-specific recommendations
7. **Modeling hypotheses document** - Insights to guide model building

---

## How These Notebooks Set Up Modeling

The 05_clustering and 06_analysis notebooks are **essential preparation** for the modeling phase (07_modeling.ipynb and beyond). Here's how they set you up for success:

### 1. Feature Selection for Models

**Analysis reveals which features matter:**
- Correlation analysis shows redundant features → Remove to avoid multicollinearity
- Feature importance from logistic regression → Focus on high-impact features
- Distribution analysis → Identify features that separate risk levels

**Example:**
If analysis shows `medication_count` and `unique_medications` are highly correlated (r=0.95), you'd drop one to avoid redundancy in modeling.

### 2. Understanding Data Structure

**Clustering reveals subpopulations:**
- Elderly high-risk group behaves differently than young low-risk
- One-size-fits-all model may perform poorly
- Suggests **stratified modeling** or **ensemble approaches**

**Example:**
Build separate models for each cluster, then combine predictions:
- Model A: Predicts risk for elderly patients
- Model B: Predicts risk for young patients
- Ensemble: Route patients to appropriate model based on cluster

### 3. Target Variable Definition

**Analysis helps define what you're predicting:**

**Option 1: Binary Classification**
- Target: `is_high_ddi_risk` (1 if any moderate+ DDI, else 0)
- Analysis shows: 30% of patients are high-risk
- Model type: Logistic regression, random forest, XGBoost

**Option 2: Regression**
- Target: `total_ddi_risk_score` (continuous score)
- Analysis shows: Scores range 0-50, right-skewed distribution
- Model type: Linear regression, gradient boosting regressor

**Option 3: Multi-class Classification**
- Target: Risk level (Low / Moderate / High)
- Analysis shows: Clear boundaries at risk scores of 5 and 15
- Model type: Multi-class classifier

**Option 4: DDI Pair Prediction**
- Target: Will adding Drug X create a DDI? (Yes/No)
- Uses DDI pair-level features
- Model type: Binary classifier on drug pairs

### 4. Handling Class Imbalance

**Analysis reveals:**
- If only 10% of patients are high-risk → **Class imbalance problem**
- Models will be biased toward predicting "low risk"

**Solutions Identified:**
- Oversample minority class (SMOTE)
- Use class weights in model
- Use metrics like F1-score, precision-recall AUC (not just accuracy)

### 5. Feature Engineering Ideas

**Analysis-driven feature creation:**

From 06_analysis, you might discover:
- **Finding**: "Patients on Warfarin + Aspirin have 5x higher risk"
- **New feature**: `is_warfarin_aspirin_combo` (binary flag)

- **Finding**: "DDI risk increases exponentially after 5 medications"
- **New feature**: `medications_squared` (polynomial term)

- **Finding**: "Elderly patients with 3+ high-severity DDIs are extreme risk"
- **New feature**: `elderly_high_severity_interaction` = `IsElderly * ddi_severity_High`

### 6. Modeling Approach Selection

**Based on analysis findings:**

**If clusters are well-separated:**
→ Consider decision tree-based models (random forest, XGBoost) that naturally segment

**If relationships are linear:**
→ Logistic regression or linear models may suffice

**If complex interactions exist:**
→ Neural networks or gradient boosting machines

**If you need interpretability:**
→ Logistic regression, decision trees (explain to clinicians)

**If you need maximum accuracy:**
→ Ensemble methods (XGBoost, LightGBM)

### 7. Validation Strategy

**Analysis informs how to split data:**

**If temporal patterns exist:**
→ Time-based split (train on 2024 Q1-Q3, test on Q4)

**If clusters are distinct:**
→ Stratified split (ensure each cluster represented in train/test)

**If class imbalance:**
→ Stratified split on target variable

### 8. Model Evaluation Metrics

**Analysis determines appropriate metrics:**

**If false positives are costly** (flagging too many patients for review):
→ Optimize for **precision**

**If false negatives are dangerous** (missing high-risk patients):
→ Optimize for **recall** (sensitivity)

**If balance matters:**
→ Optimize for **F1-score**

**If ranking matters** (prioritize patients by risk):
→ Use **AUC-ROC** or **AUC-PR**

### 9. Interpretability Requirements

**Clinical context from analysis:**
- Healthcare requires explainable models
- Analysis provides baseline for comparisons: "Model predicts Patient X is high-risk because Age=75 and DDI_pairs=8, similar to Cluster 0 (Elderly High-Risk)"

**Model explanation techniques:**
- SHAP values (show feature contributions)
- LIME (local explanations)
- Feature importance plots
- Decision rules extraction

### 10. Real-World Deployment Scenarios

**Analysis identifies use cases:**

**Use Case 1: Pre-Prescription Screening**
- **Model**: "Will adding Drug X to this patient's regimen create a DDI?"
- **Input**: Patient features + proposed drug
- **Output**: Risk probability + explanation
- **Deployment**: Integrate into EHR at prescribing workflow

**Use Case 2: Periodic Risk Scoring**
- **Model**: "What is this patient's current DDI risk?"
- **Input**: Current patient features
- **Output**: Risk score (0-100) + cluster assignment
- **Deployment**: Monthly batch scoring, flag top 5%

**Use Case 3: Care Coordination Alerts**
- **Model**: "Is this patient at risk due to fragmented care?"
- **Input**: Patient features + source_diversity
- **Output**: Fragmentation risk flag
- **Deployment**: Alert when patient receives care in multiple systems

---

## Learning: Clustering Fundamentals

### What is Clustering? (Detailed Explanation)

**Clustering** is a form of **unsupervised learning** - you're finding patterns without being told what to look for.

**Supervised vs. Unsupervised:**

| Aspect | Supervised Learning | Unsupervised Learning (Clustering) |
|--------|---------------------|-------------------------------------|
| **Labels** | Has target variable (e.g., "high risk") | No labels - discover groups |
| **Goal** | Predict labels for new data | Find structure in data |
| **Example** | Email spam detection (spam/not spam) | Customer segmentation (find customer types) |
| **Algorithms** | Logistic regression, random forest | K-means, hierarchical clustering |

### K-Means Clustering Algorithm (Step-by-Step)

**How K-Means Works:**

Imagine you have 100 patients plotted on a 2D graph (Age vs. DDI_risk). You want to find 3 groups.

**Step 1: Initialize**
- Randomly place 3 "centroids" (cluster centers) on the graph

**Step 2: Assignment**
- For each patient, calculate distance to each centroid
- Assign patient to nearest centroid
- Now you have 3 groups

**Step 3: Update**
- For each group, calculate the average position (mean Age, mean DDI_risk)
- Move centroid to this average position

**Step 4: Repeat**
- Re-assign patients to nearest centroid (some will switch groups)
- Re-calculate centroids
- Repeat until centroids stop moving

**Step 5: Converge**
- When no patients switch groups, algorithm has converged
- Final clusters are your result

**Visual Example:**

```
Iteration 0 (random init):
  [Centroid 1]    [Centroid 2]
      •               •
    Patients scattered randomly
         [Centroid 3]
             •

Iteration 1 (first assignment):
  [Centroid 1]    [Centroid 2]
      • ○○○           • ○○
      ○○              ○○○
         [Centroid 3]
             • ○○
               ○○○

Iteration 2 (centroids moved):
    ○○○[Centroid 1]
    ○○       •
              ○○○[Centroid 2]
              ○○○    •
         ○○
         ○○[Centroid 3]
            •

Final (converged):
  Three distinct clusters with tight grouping
```

### Distance Metrics

K-means uses **Euclidean distance** (straight-line distance):

```
Distance between Patient A and Centroid 1:
  sqrt((Age_A - Age_C1)² + (DDI_A - DDI_C1)²)
```

In high dimensions (14 features), the formula extends:
```
Distance = sqrt(Σ(feature_i_patient - feature_i_centroid)²)
```

**Why scaling matters:**
If Age ranges from 20-90 (span of 70) and DDI_density ranges from 0-1 (span of 1), Age will dominate distance calculations. Scaling fixes this.

### Choosing K (Number of Clusters)

**Challenge:** K-means requires you to specify K upfront. How do you choose?

**Method 1: Elbow Method**

**Concept:** As K increases, clusters get smaller, and "tightness" (within-cluster variance) decreases. But eventually, splitting further doesn't help much.

**Metric: Inertia (Within-Cluster Sum of Squares)**
- Measures how tight clusters are
- Lower is better (tighter clusters)
- Formula: Sum of squared distances from each point to its centroid

**Process:**
1. Run K-means with K=2, 3, 4, ..., 10
2. Calculate inertia for each K
3. Plot inertia vs. K
4. Look for "elbow" - where curve bends sharply

**Example Plot:**
```
Inertia
  |
8000|•
  |
6000| •
  |
4000|  •
  |    •___
2000|       •___•___•___•
  |_____________________ K
     2  3  4  5  6  7  8

Elbow at K=4 → Choose 4 clusters
```

**Method 2: Silhouette Score**

**Concept:** For each point, measure:
- **a**: Average distance to points in its own cluster (lower is better)
- **b**: Average distance to points in nearest other cluster (higher is better)
- **Silhouette**: (b - a) / max(a, b)

**Interpretation:**
- **+1**: Perfect - far from other clusters, close to own cluster
- **0**: On the border between clusters
- **-1**: Wrong cluster - closer to another cluster

**Process:**
1. Run K-means with different K values
2. Calculate average silhouette score across all points
3. Choose K with highest average silhouette

**Example:**
```
K=2: silhouette = 0.45
K=3: silhouette = 0.52
K=4: silhouette = 0.58  ← Best
K=5: silhouette = 0.51
K=6: silhouette = 0.48

Choose K=4
```

### Alternative Clustering Algorithms

**K-Means Limitations:**
- Requires specifying K upfront
- Assumes spherical clusters (same variance in all directions)
- Sensitive to outliers
- Struggles with irregular shapes

**Alternative: Hierarchical Clustering**

**How it works:**
- Bottom-up (agglomerative): Start with each point as its own cluster, merge similar clusters iteratively
- Top-down (divisive): Start with one cluster, split recursively

**Output: Dendrogram (Tree)**
```
       ┌────────────────────┐
       │                    │
    ┌──┴──┐              ┌──┴──┐
    │     │              │     │
  ┌─┴─┐ ┌─┴─┐          ┌─┴─┐ ┌─┴─┐
  P1 P2 P3 P4          P5 P6 P7 P8

Cut at different heights → different K
```

**Advantage:** Don't need to choose K upfront; can explore different levels

**Alternative: DBSCAN (Density-Based Clustering)**

**How it works:**
- Finds dense regions (many points close together)
- Points in sparse regions are labeled as outliers

**Advantage:**
- Finds arbitrary shapes
- Automatically detects outliers
- Doesn't require specifying K

**Use when:** You have irregular-shaped clusters or many outliers

### Clustering Validation

**Internal Metrics** (based on data alone):
- **Silhouette score**: How well-separated are clusters?
- **Davies-Bouldin Index**: Ratio of within-cluster to between-cluster distances (lower is better)
- **Calinski-Harabasz Index**: Ratio of between-cluster to within-cluster variance (higher is better)

**External Metrics** (if you have labels for validation):
- **Adjusted Rand Index**: Similarity to true labels
- **Normalized Mutual Information**: Information shared with true labels

**Domain Validation** (most important for healthcare):
- Do clusters make clinical sense?
- Are they actionable?
- Do clinicians trust them?

---

## Learning: Analysis Techniques

### Exploratory Data Analysis (EDA) Principles

**EDA is detective work with data:**

**The 5 W's of EDA:**
1. **What**: What is in my data? (Variables, types, ranges)
2. **Where**: Where are the patterns? (Distributions, clusters)
3. **When**: When do events occur? (Temporal patterns)
4. **Who**: Who is affected? (Subgroups, demographics)
5. **Why**: Why do patterns exist? (Causal hypotheses)

**EDA Workflow:**

```
1. Summarize
   ↓
2. Visualize
   ↓
3. Question
   ↓
4. Investigate
   ↓
5. Repeat
```

### Statistical Testing Fundamentals

**Why test?** To determine if observed differences are real or due to random chance.

**Example Question:** "Are elderly patients at higher DDI risk?"

**Without testing:**
- Elderly mean risk: 12.5
- Non-elderly mean risk: 8.3
- Difference: 4.2
- Conclusion: "Looks higher, but is it significant?"

**With testing (t-test):**
- Null hypothesis: No difference between groups
- Calculate t-statistic and p-value
- If p-value < 0.05: "Difference is statistically significant (95% confidence)"

**Common Tests:**

| Test | Purpose | Example |
|------|---------|---------|
| **T-test** | Compare means of 2 groups | Elderly vs. non-elderly DDI risk |
| **ANOVA** | Compare means of 3+ groups | DDI risk across 4 clusters |
| **Chi-square** | Test association between categorical variables | Gender vs. high-risk status |
| **Correlation test** | Test if two continuous variables are related | Age vs. DDI risk score |

**P-value interpretation:**
- **p < 0.001**: Very strong evidence of difference
- **p < 0.01**: Strong evidence
- **p < 0.05**: Moderate evidence (standard threshold)
- **p > 0.05**: Insufficient evidence (retain null hypothesis)

**IMPORTANT:** Statistical significance ≠ clinical significance
- A difference can be statistically significant but too small to matter clinically
- Always report effect size, not just p-value

### Correlation vs. Causation

**Correlation:** Two variables move together
**Causation:** One variable causes the other

**Example:**
- **Correlation**: "Patients with more medications have more DDIs"
- **NOT causation**: More medications → More DDIs (TRUE)
- **ALSO NOT**: More DDIs → More medications (FALSE)

**Why it matters:**
- Correlation suggests relationships to investigate
- But don't assume direction or causality
- Use domain knowledge and experiments to establish causation

**Bradford Hill Criteria for Causation:**
1. Strength of association
2. Consistency across studies
3. Specificity
4. Temporal relationship (cause precedes effect)
5. Biological gradient (dose-response)
6. Plausibility (makes sense)
7. Coherence with existing knowledge
8. Experimental evidence

### Visualization Best Practices

**Choose the right chart type:**

| Data Type | Chart Type | Example |
|-----------|------------|---------|
| **Distribution** (single variable) | Histogram, box plot | Age distribution |
| **Comparison** (groups) | Bar chart, grouped box plot | DDI risk by cluster |
| **Relationship** (two continuous) | Scatter plot | Age vs. DDI risk |
| **Composition** (parts of whole) | Pie chart, stacked bar | Percentage in each cluster |
| **Time series** | Line chart | DDI risk over time |
| **Correlation** (many variables) | Heatmap | Feature correlation matrix |

**Design principles:**
- **Clear labels**: Title, axis labels, legend
- **Appropriate scale**: Start y-axis at 0 for bar charts
- **Color**: Use color meaningfully (red=high risk, green=low risk)
- **Simplicity**: Remove clutter, focus on message
- **Accessibility**: Colorblind-friendly palettes

---

## Practical Implementation Plan

### Timeline and Effort Estimate

**05_clustering.ipynb:**
- **Setup and data loading**: 30 minutes
- **Feature selection and preprocessing**: 1 hour
- **Determining optimal K**: 1 hour
- **Clustering and characterization**: 1 hour
- **Visualization**: 1 hour
- **Documentation**: 30 minutes
- **Total**: 5 hours

**06_analysis.ipynb:**
- **Descriptive statistics**: 1 hour
- **Cluster analysis**: 1.5 hours
- **DDI pair analysis**: 1.5 hours
- **Demographic analysis**: 1.5 hours
- **Feature importance**: 1 hour
- **Intervention planning**: 1 hour
- **Documentation**: 30 minutes
- **Total**: 8 hours

**Combined**: 13 hours (approximately 2 work days)

### Step-by-Step Implementation Order

**Day 1 Morning: 05_clustering.ipynb (Part 1)**
1. Load patient features from S3
2. Select clustering features
3. Handle categorical variables (Gender encoding)
4. Check for missing values
5. Scale features using StandardScaler

**Day 1 Afternoon: 05_clustering.ipynb (Part 2)**
6. Elbow method analysis (K=2 to 10)
7. Silhouette score analysis
8. Decide on optimal K
9. Fit final K-means model
10. Assign cluster labels to patients

**Day 1 Evening: 05_clustering.ipynb (Part 3)**
11. Characterize clusters (means, medians, counts)
12. Name clusters based on characteristics
13. Visualize with PCA/t-SNE
14. Validate with silhouette/statistical tests
15. Save clustered patient data

**Day 2 Morning: 06_analysis.ipynb (Part 1)**
16. Load clustered patient data
17. Descriptive statistics and distributions
18. Demographic analysis (age, gender)
19. Medication profile analysis
20. DDI severity breakdown

**Day 2 Midday: 06_analysis.ipynb (Part 2)**
21. Cluster comparison and validation
22. Statistical tests (ANOVA, t-tests)
23. Cluster visualization (heatmaps, radar charts)
24. Load DDI pair-level features
25. Most common drug interactions

**Day 2 Afternoon: 06_analysis.ipynb (Part 3)**
26. High-severity drug pair analysis
27. Interaction type analysis
28. Temporal overlap analysis
29. Age vs. DDI risk analysis
30. Gender and polypharmacy analysis

**Day 2 Evening: 06_analysis.ipynb (Part 4)**
31. Correlation matrix
32. Feature importance (logistic regression)
33. High-risk patient identification
34. Intervention planning
35. Modeling hypotheses document

### Code Structure Template

**05_clustering.ipynb Structure:**

```
# Part 1: Setup and Data Loading
- Imports
- S3 connection
- Load patient features
- Initial data inspection

# Part 2: Feature Selection and Preprocessing
- Select clustering features
- Handle categorical variables
- Handle missing values
- Feature scaling

# Part 3: Determining Optimal K
- Elbow method
- Silhouette analysis
- Visual comparison

# Part 4: K-Means Clustering
- Fit K-means with optimal K
- Assign cluster labels
- Save clustered data

# Part 5: Cluster Characterization
- Calculate cluster statistics
- Name clusters
- Create characterization table

# Part 6: Visualization
- PCA/t-SNE projection
- Cluster scatter plots
- Feature heatmaps
- Bar charts

# Part 7: Validation
- Silhouette scores
- Statistical tests
- Stability checks

# Part 8: Export Results
- Save clustered patient data to S3
- Export cluster summary
- Generate report
```

**06_analysis.ipynb Structure:**

```
# Part 1: Setup and Data Loading
- Imports
- Load clustered patient features
- Load DDI pair features
- Initial inspection

# Part 2: Descriptive Statistics
- Overall DDI risk distribution
- Demographics summary
- Medication profile summary
- DDI severity breakdown

# Part 3: Cluster Analysis
- Cluster size and distribution
- Compare clusters on key metrics
- Statistical testing (ANOVA)
- Cluster visualization (heatmaps, radar)

# Part 4: DDI Pair Analysis
- Most common drug interactions
- High-severity drug pairs
- Interaction type analysis
- Temporal overlap analysis

# Part 5: Demographic and Risk Analysis
- Age vs. DDI risk
- Age group comparison
- Gender analysis
- Polypharmacy analysis
- Elderly vs. non-elderly

# Part 6: Feature Relationships
- Correlation matrix
- Feature distributions by risk level
- Feature importance (logistic regression)

# Part 7: Actionable Insights
- High-risk patient identification
- Drug pairs requiring review
- Cluster-specific interventions
- Intervention plan export

# Part 8: Modeling Preparation
- Document hypotheses
- Feature selection recommendations
- Target variable suggestions
- Validation strategy
```

### Key Python Libraries

**Required Imports:**

```python
# Data manipulation
import pandas as pd
import numpy as np

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Clustering
from sklearn.cluster import KMeans, DBSCAN
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# Preprocessing
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Metrics and validation
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score

# Statistical testing
from scipy.stats import f_oneway, ttest_ind, chi2_contingency
from scipy.stats import pearsonr, spearmanr

# Feature importance
from sklearn.linear_model import LogisticRegression

# S3 access
import s3fs
import boto3
```

### Common Pitfalls and How to Avoid Them

**Pitfall 1: Not Scaling Features**
- **Symptom**: K-means dominated by large-magnitude features
- **Solution**: Always use StandardScaler before clustering

**Pitfall 2: Too Many or Too Few Clusters**
- **Symptom**: Clusters not interpretable or actionable
- **Solution**: Use elbow + silhouette + clinical judgment

**Pitfall 3: Ignoring Missing Values**
- **Symptom**: Clustering fails or produces biased results
- **Solution**: Check for NaN, impute or drop strategically

**Pitfall 4: Including Correlated Features**
- **Symptom**: Redundant features over-influence clustering
- **Solution**: Check correlation matrix, remove highly correlated pairs

**Pitfall 5: Not Validating Clusters**
- **Symptom**: Clusters look good but are unstable or meaningless
- **Solution**: Statistical tests, clinical review, stability checks

**Pitfall 6: Overinterpreting Statistical Significance**
- **Symptom**: Tiny effects reported as "significant" with large N
- **Solution**: Report effect sizes and clinical significance

**Pitfall 7: Creating Too Many Visualizations**
- **Symptom**: Analysis notebook becomes cluttered and hard to follow
- **Solution**: Select 10-15 most informative plots, move rest to appendix

**Pitfall 8: Not Documenting Insights**
- **Symptom**: Insights lost, can't remember findings for modeling
- **Solution**: Create summary documents, export key findings

---

## Expected Outputs and Deliverables

### From 05_clustering.ipynb

**Data Outputs:**
1. `v3_features/ddi/patients_features_clustered.parquet` - Patient features with cluster labels
2. `results/cluster_summary.csv` - Cluster characterization table
3. `results/cluster_metrics.json` - Silhouette scores, inertia, etc.

**Visualizations:**
1. Elbow plot (K vs. inertia)
2. Silhouette score plot
3. PCA 2D scatter plot of clusters
4. t-SNE 2D scatter plot (optional)
5. Cluster size bar chart
6. Heatmap of cluster characteristics
7. Box plots of key features by cluster

**Documentation:**
1. Cluster names and descriptions
2. Validation metrics
3. Clinical interpretation notes

### From 06_analysis.ipynb

**Data Outputs:**
1. `results/high_risk_patients.csv` - Top 10% risk patients
2. `results/high_impact_ddis_for_review.csv` - Priority drug pairs
3. `results/cluster_intervention_plan.csv` - Intervention mapping
4. `results/feature_importance.csv` - Feature coefficients from logistic regression
5. `results/modeling_hypotheses.txt` - Findings to inform modeling

**Visualizations:**
1. DDI risk score distribution (histogram)
2. Age distribution (histogram + bar by age group)
3. Gender breakdown (bar chart)
4. Medication count distribution
5. DDI severity breakdown (bar chart)
6. Cluster size pie chart
7. Cluster comparison heatmap
8. Top 10 drug pairs (horizontal bar)
9. Interaction type distribution
10. Age vs. DDI risk (scatter + trend line)
11. DDI risk by age group (box plot)
12. DDI risk by gender (box plot)
13. Polypharmacy comparison (grouped bar)
14. Feature correlation matrix (heatmap)
15. Feature distributions by risk level (overlapping histograms)
16. Feature importance (horizontal bar)

**Reports:**
1. Descriptive statistics summary
2. Cluster characterization table
3. Statistical test results (ANOVA, t-tests)
4. High-risk patient summary
5. Intervention recommendations
6. Modeling preparation document

---

## Success Criteria

### For 05_clustering.ipynb

**Technical Success:**
- ✅ Clustering runs without errors
- ✅ Silhouette score > 0.4 (good separation)
- ✅ Clusters have reasonable sizes (no cluster <5% or >60% of population)
- ✅ Clustered data saved to S3 successfully

**Clinical Success:**
- ✅ Clusters are interpretable (can be named with clinical meaning)
- ✅ Clusters differ significantly on key metrics (ANOVA p < 0.05)
- ✅ Clusters align with clinical intuition (e.g., elderly high-risk group exists)
- ✅ Clusters are actionable (can define interventions for each)

**Documentation Success:**
- ✅ Each cluster has a clear name and description
- ✅ Characterization table is complete and readable
- ✅ Visualizations clearly show cluster separation
- ✅ Validation metrics are documented

### For 06_analysis.ipynb

**Technical Success:**
- ✅ All analyses run without errors
- ✅ Statistical tests produce valid results
- ✅ Visualizations render correctly
- ✅ All output files saved successfully

**Insight Success:**
- ✅ At least 10 actionable clinical insights generated
- ✅ High-risk patients identified (top 10%)
- ✅ Priority drug pairs identified for review
- ✅ Clear hypotheses for modeling documented
- ✅ Feature importance analysis reveals predictive features

**Actionability Success:**
- ✅ Intervention plan created for each cluster
- ✅ High-impact DDI list ready for clinical review
- ✅ Findings are clear enough to present to stakeholders
- ✅ Next steps for modeling are well-defined

**Reproducibility Success:**
- ✅ Notebook runs end-to-end without manual intervention
- ✅ Random seeds set for reproducibility
- ✅ All data sources and outputs documented
- ✅ Code is well-commented and organized

---

## Next Steps After 05 and 06

Once you complete clustering and analysis, you'll be ready for:

**07_modeling.ipynb (Predictive Modeling):**
- Build models to predict DDI risk
- Compare algorithms (logistic regression, random forest, XGBoost)
- Evaluate model performance
- Generate predictions for new patients

**08_evaluation.ipynb (Model Evaluation):**
- Detailed model performance analysis
- Confusion matrices, ROC curves, precision-recall curves
- Feature importance and SHAP values
- Error analysis (where does model fail?)

**09_deployment.ipynb (Deployment Preparation):**
- Save final model
- Create prediction pipeline
- Build API or batch scoring system
- Document model for production use

**10_monitoring.ipynb (Model Monitoring):**
- Track model performance over time
- Detect data drift
- Retrain triggers
- A/B testing framework

---

## Additional Resources

### Recommended Reading

**Clustering:**
- "Introduction to Statistical Learning" (Chapter 10: Unsupervised Learning)
- Scikit-learn clustering documentation: https://scikit-learn.org/stable/modules/clustering.html

**Analysis:**
- "Exploratory Data Analysis" by John Tukey
- "The Visual Display of Quantitative Information" by Edward Tufte

**Healthcare ML:**
- "Machine Learning for Healthcare" (MIT course materials)
- "Clinical Prediction Models" by Ewout Steyerberg

### Python Documentation

- **Scikit-learn**: https://scikit-learn.org/
- **Pandas**: https://pandas.pydata.org/docs/
- **Matplotlib**: https://matplotlib.org/stable/contents.html
- **Seaborn**: https://seaborn.pydata.org/
- **SciPy**: https://docs.scipy.org/doc/scipy/

### Troubleshooting Guide

**Issue: Clustering produces one large cluster and several tiny ones**
- **Cause**: Features not scaled, or outliers dominating
- **Fix**: Check scaling, consider removing outliers or using DBSCAN

**Issue: Silhouette score is very low (<0.2)**
- **Cause**: No clear cluster structure in data
- **Fix**: Try different K, try hierarchical clustering, reconsider feature selection

**Issue: Clusters don't make clinical sense**
- **Cause**: Wrong features selected, or K is inappropriate
- **Fix**: Review feature selection with clinical team, try different K

**Issue: Analysis shows no significant relationships**
- **Cause**: Sample size too small, or truly no relationships exist
- **Fix**: Check data quality, consider different statistical tests, gather more data

**Issue: Too many visualizations, notebook is overwhelming**
- **Cause**: Creating every possible plot
- **Fix**: Select most informative 15-20 plots, create separate "appendix" notebook

---

## Summary

**05_clustering.ipynb** will:
- Discover 3-5 natural patient risk groups
- Characterize each group (demographics, medication profile, DDI risk)
- Validate clusters statistically and clinically
- Provide cluster labels for downstream analysis

**06_analysis.ipynb** will:
- Deeply investigate DDI patterns and risk distribution
- Validate and interpret clusters from 05_clustering
- Identify high-risk patients and drug pairs for intervention
- Generate hypotheses and feature insights for modeling

**Together, they:**
- Transform your engineered features into actionable insights
- Reveal patterns that inform clinical interventions
- Prepare you to build effective predictive models
- Bridge the gap between data and decision-making

You're now equipped with the knowledge and plan to build these critical notebooks. The next phase will turn your cleaned data and engineered features into clinical intelligence!

---

*Guide created for the med-ml DDI Risk Analysis Project*
*Date: 2025-11-28*
*Ready to implement 05_clustering.ipynb and 06_analysis.ipynb*
