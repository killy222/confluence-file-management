# [Concept Paper] Identifying and Merging Duplicates

Confluence Page ID: 144183800

Dealing with duplicate data is a common challenge for businesses, especially as they grow and collect information from various sources. A robust system for **duplicate identification and merging** is crucial for maintaining data integrity and ensuring accurate reporting, streamlined operations, and effective decision-making.

### Algorithm for Duplicate Identification

To ensure a reliable and scalable approach to identifying duplicate businesses, the system will use **GMB-enriched data** as the primary, authoritative source. After enrichment, businesses that share key GMB-verified properties can be safely evaluated for duplication.

We can use a **weighted scoring system** to evaluate the likelihood that two business records represent the same entity. Each shared data point contributes to a combined duplicate score. The more attributes match, the higher the confidence.

| Data Point | Description | Weight |
| --- | --- | --- |
| **GMB CID** | Unique Google identifier, strongest possible indicator | +100 |
| **Business Name** |  | + 30 |
| **Phone** | Standardized format (E.164), strong identity indicator | + 40 |
| **Address** | Normalized street, ZIP, and city | + 15 |
| **Website** |  | + 15 |

**Total possible score: 200 points**

#### **Phase 1 Matching Criteria (100% Confidence Score)**

To minimize risk and ensure perfect accuracy in the first rollout, Phase 1 will only merge business records that share **all five GMB-verified fields**:

* GMB CID
* Business Name
* Phone Number
* Address
* Website

This guarantees a **100% confidence score (200/200 points)**.

#### **Future Expansion (Configurable Threshold Matching)**

Use different approaches to compare strings, like:

* Business name - compare normalized, case-insensitive, legal suffixes removed
* Website - root domain comparison, ignoring protocol, www, and deep links

After Phase 1 is completed and the merging procedure is validated, we can gradually expand duplicate detection to include **lower but still reliable confidence levels**. For example: **≥ 80% confidence** (≥ 160 points) = records with partial but strong identity matches (e.g., same name + phone + address). This will allow the system to detect and merge more duplicates over time while maintaining control over risk.

Weights and thresholds can be discussed and decided in the future.

### Phased Strategy for Duplicate Merging Implementation

The team agreed on a **phased, risk-minimized strategy**, starting with the simplest and safest cases and progressively expanding toward more complex scenarios. This ensures that we improve data quality without interrupting ongoing Sales workflows or interfering with external systems.

Phased Strategy for Duplicate Merging Implementation1

#### **Phase 1 – Low-Risk, High-Impact Cleanup (In Progress)**

Phase 1 focuses exclusively on businesses that:

* are **not blacklisted**,
* have **no existing pipeline history**,
* match across **strict, GMB-verified attributes** (share the same GMB verified CID + name + address + phone + website)
* are **not used in external systems** (e.g., E-Sign, Success Story).

This covers more than **1 million businesses** that have never been contacted or assigned to employees. Cleaning these records provides a significant impact with minimal operational risk and allows us to validate the merging process safely.

In this phase, we are building the core merging framework that consolidates:

* business properties,
* state,
* notes, and
* full activity history.

#### **Phase 2 – Cleanup of Historical but Inactive Businesses**

Once Phase 1 is complete, we will extend the logic to handle duplicates that:

* had pipelines, calls, appointments or events in the past,
* but are **no longer assigned** and have **no active sales activity**.

This phase introduces merging of:

* closed deals,
* closed pipelines,
* completed appointments,
* historical calls and events.

With this logic in place, we can begin triggering duplicate merging automatically during specific system events (e.g., when a business is released from a list or after ZIP/List-release/clean operations).

#### **Phase 3 – Sales-Aware Merging**

The final step is to apply merging safely during defined points in the Sales funnel where communication has fully ended (e.g., deal closed, no active pipeline, no scheduled appointments). This allows us to gradually clean duplicates without affecting active communication with businesses.

We won’t clean all duplicates at once. Instead, the system will continuously evaluate unassigned businesses and automatically trigger merging whenever duplicates are identified. This ensures ongoing data quality improvement while keeping Sales operations uninterrupted.