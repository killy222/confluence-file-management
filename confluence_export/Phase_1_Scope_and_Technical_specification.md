# [Phase 1] Scope and Technical specification

Confluence Page ID: 144183831

**Phase 1** focuses exclusively on the simplest and safest merge cases to avoid conflicts with pipelines, appointments, and active sales processes.

This initial phase targets businesses that:

* Are **not blacklisted**
* Have **no existing pipeline history**
* Match across **strict, verified attributes**
* Are not actively used in other internal systems

This scope covers **~1+ million businesses**, providing high-impact cleanup with low operational risk.

Merging processesMerging processes4

### Matching Criteria (Strict Mode)

For duplicates in Phase 1 are considered only businesses that are **not blacklisted**, that have **never had any pipeline** and meet strict matching criteria - shares the same GMB verified:

* CID (GMB verified)
* Name (GMB verified)
* Address (GMB verified)
* Phone (GMB verified)
* Website (GMB verified)

This represents ~1 million+ businesses available for initial cleanup.

PROS:

* **Minimal risk** - won't disrupt active sales work or external systems
* **No pipeline conflicts** - avoids complex merge logic
* **No appointment system impact** - these businesses have no meetings scheduled
* **Safe learning opportunity** - can test the process before tackling harder cases

### General Workflow for the Merge Process

Merge process general steps:

1. Identify duplicates
2. Select the master account.
3. Merge all data from other duplicates into the master.
4. Delete non-master duplicates, so that they won't be available anymore in the system.

#### Step 1: Identify duplicate businesses

For each business included in the Phase 1 scope, the system scans all other Phase 1–eligible businesses and identifies duplicates based on strict matching of GMB-verified properties (CID, name, phone number, address, and website).

#### Step 2: Master Business Selection

Among all identified duplicates, the **oldest business record** (=earliest `created_at` timestamp) becomes the **master account**. All other businesses become **non-master duplicates**.

#### Step 3: Data Merging Logic

Multi-Value Properties (union logic)

* **Union all unique values** from all duplicates
* Copy all existing activity logs from all duplicates into a single chronological timeline. Maintain original timestamps and user attributions. **Accept redundancy** (e.g., "phone 123 added" may appear 3 times). No attempt is made to rewrite or sanitize history.
* **Add new logs for merge operations** on these properties (e.g. "phone 456 added during merge processes")

Scope: Properties where multiple values are allowed:

* phone numbers
* addresses
* emails
* websites
* representatives
* categories
* tags
* branches
* Notes

Single-Value Properties (selection logic)

* Description: **Concatenate** all non-empty descriptions from duplicates separated with special symbols "===".
* No of employees: Take **non-null** value from thenewest business
* Revenue: Take **non-null** value from the newest business
* Open/Closed status: Parse activity logs for status change entries. Sort chronologically across all duplicates and apply **most recent status** to master account. Keep comment associated with the most recent status change.
* `is_of_interest` flag: **Preferential YES selection**. If any duplicate has YES → master gets YES. If all has Unknown → master gest UNKNOWN. Else: NO.

Logs for these changes are added only when the value in the master account changes.

Activity Log Handling

All logs from all duplicates are copied into a unified chronological timeline:

* full timestamp fidelity
* original user attribution
* original action

New log types need to be created to mark begin/end of merge process + if a property in the master account was added/revised during merge processes.

Activity Log for Duplicates Merge

These ensure a clear audit trail of the merge event.

#### Step 4: Cleanup of Duplicates

Delete non-master duplicates, so that they won't be available anymore in the system. 

**Preserve references to old business IDs after merge**

```
old_business_id → current_master_id mapping table
```

* All API entry points accepting business\_id
* All API entry points accepting pipeline\_id
* External system integrations

### Statistical information

Show history from made duplicate merging processes to demonstrate to management that duplicate cleanup is happening and effective.Need to track:

1. **Number of merge operations performed** (e.g., "2 merge operations")
2. **Total businesses processed** (e.g., "5 businesses merged")
3. **Businesses eliminated** (implicit: total - remaining)

**Example:**

* 2 merge operations performed
* 5 businesses involved (2 + 3)
* Result: 2 master businesses remain
* **3 businesses eliminated** from system