# [Phase 2] Scope and Technical specification

Confluence Page ID: 144186413

Phase 2 focuses on the cleanup of **historical but inactive businesses**.  
This phase extends the duplicate merging framework introduced in Phase 1 to cover records that also contain **past sales activity**, while still strictly avoiding any impact on **active or upcoming Sales work**.

The primary objective is to consolidate historical interaction data into a single, consistent business record, thereby improving data quality and reporting accuracy, while preserving the **risk-minimized approach** established in Phase 1.

Phase 2 ensures that:

* historical Sales activity is not lost,
* employee progress and funnel stages are preserved,
* no active communication or ownership is disrupted.

### Scope Definition

Phase 2 targets **duplicate business records** that have **no active pipeline** and are **not** **blacklisted.**

This guarantees that Phase 2 remains **non-disruptive**.

The scope of merged businesses in Phase 2 will be extended to include those that were skipped during Phase 1 because they have **historical sales interactions**, including:

* pipelines,
* calls,
* appointments,
* events,
* deals.

### **Duplicate Identification & Merge Flow**

Identification Logic

There are **no changes** to the duplicate identification logic introduced in Phase 1.

Duplicates are still identified exclusively via:

* GMB-verified CID
* GMB-verified name
* GMB-verified address
* GMB-verified phone
* GMB-verified website

Merge Process

There are **no changes** to the existing **4-step merge workflow**:

1. Identify duplicates
2. Select master account
3. Merge data
4. Delete non-master duplicates

Phase 2 strictly builds on this existing foundation. The **only functional extension** introduced in Phase 2 is the **refinement of property consolidation logic** to support additional historical Sales data.

### Expanded Merging Capabilities

The new master account should preserve the progress of each employee previously worked with any of the merged accounts, keeping the corresponding Sales Funnel stage and the history of all interactions with the business (calls, events, appointments, deals). 

Phase 2 extends merging to include:

* closed pipelines,
* closed deals,
* appointments,
* events,
* calls.

General Rule

All historical records from duplicate businesses are copied into the master account and combined into a **single chronological timeline**, without rewriting or correcting historical inconsistencies.

Original metadata is preserved:

* timestamps,
* user attributions,
* specific call/appointment/event metadata.

Duplicate or contradictory entries are accepted.

Merging processes - Phase 2Merging processes - Phase 27

#### Historical calls

* Copy **all call-related activity logs** from all duplicates.
* Merge chronologically.
* Preserve original timestamps and user ownership, call direction and metadata.

Result:

* Master account contains the **complete historical call log** from all duplicates.
* All previous made Calls from all merged duplicates appear in both **Call Log** and **All Activity** in the master account.

#### Appointments

* Copy **all appointment-related logs** from all duplicates.
* Merge chronologically.
* Preserve original timestamps and user ownership

Result:

* Master account reflects the **full appointment history**.
* All previous made Appointments from all merged duplicates appear in both **Appointment Log** and **All Activity** in the master account.

#### Events

* Copy **all event-related activity logs** from all duplicates.
* Merge chronologically.
* Preserve original timestamps and user ownership and all metadata.
* The link and the account name in the notification for the event should be updated to correspond to the master account.

Result:

* Master account reflects the **full historical event context**.
* All previous made Events from all merged duplicates appear in both **Event Log** and **All Activity** in the master account.

#### Deals & Pipelines

* Copy **all deal-related and pipeline-related activity logs**.
* Preserve full history across duplicates.
* All deal and pipeline changes from merged duplicates are visible in **Deals Log** and **All Activity**.

#### **Data Consolidation Logic for pipelines and deals when multiple duplicate businesses contain overlapping **pipelines for the same user****

**For Pipelines:**

* **start date** = oldest pipeline start date across duplicates,
* **end date** = most recent pipeline end date across duplicates.

The final pipeline stage in the master account is determined as follows:

* If any pipeline is in stage Won

  + The master pipeline is set to **Won**.
* Otherwise

  + Select the **user-defined terminal stage** that ended most recently.

**Stage Priority**

* Preferred terminal stages (user-facing):

  + No interest
  + Pursue not worth
  + Blacklist
  + Wrong business
  + Business closed
* Lower-priority system stages (not user-facing):

  + Transferred to another employee
  + User left
  + Account released

  User-facing terminal stages always take precedence over system-only stages.

**For Deals:**

* Keep the deal that corresponds to the pipeline stage selected for the merged business

### Technical consideration

Appointments mapping → Take care to update the mapping to the business in the Appointment to the new master business ID (can be checked via [find-single API](https://wiki.viscomp.net/spaces/PHS/pages/89031274/Single+Business+Info))

Progress Trackers (ZipTracker) → Update references from old business accounts to the new master account

### Summary

Phase 2 guarantees:

* No impact on active pipelines, appointments, or ownership.
* No rewriting or normalization of historical data.
* Deterministic, auditable merge results.
* Full traceability through existing activity logs.

Phase 2 establishes a complete and accurate historical record per business and serves as the **technical prerequisite for Phase 3 automation**, where merges can be triggered by defined lifecycle events after business communication has ended.