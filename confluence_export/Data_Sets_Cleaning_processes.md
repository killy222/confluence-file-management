# Data Sets Cleaning processes

Confluence Page ID: 139267236

### [1] One time processes

#### 1.1. Blacklists

Bulk blacklisting process based on:

* GMB category → The blacklist is made only for businesses with an address in Germany. The process is done several times because the mapping was extended twice -> last blacklist is finished on 24.06.2025
  + unconditional blacklisting based on GMB category (blacklisted in total 734 131 Data Sets)
  + legal-form blacklisting based on GMB category and HRA/HRB scraped from website's Impressum page (blacklisted in total 227 318 Data Sets)
  + additional legal-form blacklisting based on GMB category and legal form matched from Northdata (blacklisted 207 880 based from the list) → finished on 05.08.2025
* Domain (39 048 affected businesses) → finished on 26.06.2025

#### 1.2. Identify & Remove incorrect data

Clean data base from not working websites (finished on 27.06.2025):

* Remove websites that are with not working DNS (765 527 websites affected)
* Delete deprecated google related websites (1 214 websites affected)

### [2] Continuous/Ongoing processes

#### 2.1. Automatic blacklist

* Automatic blacklisting process triggered on each newly added category and/or website into the system based on:

+ GMB category 

  If the newly added category is in the mapping for unconditional blacklist, then the system will immediately blacklist the business for all Brands with:

  - reason = "category-forbidden"
  - comment = "Blacklisting due to GMB Category. Requested from M.Koehler on 25.03.2025"
+ GMB category and specific legal form (HRA-HRB in Impressum) +  fallback to Northdata matching in case HRA/HRB can not be identified. The improved algorithm with Northdata exports has been working since 08.10.2025. Since 17.11.2025 the "is\_of\_interest" calculation logic is changed to use specific address related Nortdata exports for AT businesses and for all others.

  The conditional blacklist procedure can be triggered from two events - on add category and on add new website from type "Company" or "Unknown".

  (1) If the newly added category is in the mapping for conditional blacklist and is\_of\_interest = "no", then the system will immediately blacklist the business for all Brands with:

  - reason = "category-forbidden"
  - comment = "Legal-form blacklisting due to GMB Category. Requested from M.Koehler on 25.03.2025"

  (2) If the newly added website is from type "Company" or "Unknown", then the system calculates the "`is_of_interest`" state based on the following algorithm:

  is of interest logic

  Is of interest LogicIs of interest Logic3

  - In case the Impressum is scraped and **`HRA` or `HRB` number is identified**in the scraped content:

    * **`is_of_interest` = "yes"**
  - in case Impressum is scraped but HRA-HRB is not identified OR in case Impressum can not be scraped (error when searched for Impressum, the website don't have Impressum page, the website is forbidden for scraping Impressum), **fallback to Nortdata matching** algorithm to calculate "is\_of\_interest".

    * If a match is found and the legal-form is important for Sales, then **`is_of_interest` = "yes"**
    * If a match is found and the legal-form is not important for Sales, then **`is_of_intrerest` = "no"**
    * If no match is found by any of the criteria, then **`is_of_interest` = "no"**

  If `is_of_interest` is changed to "no" and the business has a category in the mapping for conditional blacklist and is\_of\_interest = "no", then the system will immediately blacklist the business for all Brands with:

  - reason = "category-forbidden"
  - comment = "Legal-form blacklisting due to GMB Category. Requested from M.Koehler on 25.03.2025"
+ Working since June 2025 and providing results daily => the amount of blacklisted records is raised (due to manually enriched records from the employees) and will continue to raise due to the automatically made solution with GMB enrichment that is already processing Data Sets

Important specific on the blacklisting procedure:

**General blacklisting procedure**: When an account is blacklisted, all phone numbers and email addresses currently associated with it are also blacklisted. The system then identifies other accounts that share these contact details and recursively blacklists them as well → this is referred to as**chain blacklisting**. If the number of chained accounts exceeds 5, only the original account that triggered the blacklisting process will be blacklisted.

**Category-based blacklisting procedure**: In cases where a business category is eligible for blacklisting, the system won't execute chain blacklisting of all accounts sharing the same phone/email. Instead, only the original Data Set that directly meets the unconditional or legal-form category criteria will be blacklisted. **Effect:** If one Data Set is blacklisted by category and its phone is used in another account, the second account will not be blacklisted unless it independently meets category/legal-form criteria.

false

In order to keep our Data Sets clean and maintain that quality over time, we use a **constantly working logic** that is triggered on several events and could potentially blacklist a Data Set:

* on each new **Account creation**:

+ if the used phone number exists in the system and is already blacklisted for any other Data Sets => the new Data Set will be also automatically blacklisted for the same reason.  This chained blacklist is skipped if the blacklist reason is category-forbidden.
+ if the used mail exists in the system and is already blacklisted for any other Data Sets => the new Data Set will be also automatically blacklisted for the same reason.  This chained blacklist is skipped if the blacklist reason is category-forbidden.
+ if the used category is eligible for unconditional blacklisting => the new Data Set will be also automatically blacklisted with the reason 'category-forbidden' and the comment "Blacklisting due to GMB Category. Requested from M.Koehler on 25.03.2025"
+ if the Impressum of the used website is successfully scraped and we have not found HRA/HRB in it's content + the used category is eligible for legal-form blacklisting => the new Data Set will be also automatically blacklisted with the reason 'category-forbidden' and the comment "Legal-form blacklisting due to GMB Category. Requested from M.Koehler on 25.03.2025".

* on each **new category** for an Account

+ if the used category is eligible for unconditional blacklisting => the new Data Set will be also automatically blacklisted with the reason 'category-forbidden' and the comment "Blacklisting due to GMB Category. Requested from M.Koehler on 25.03.2025"
+ if the 'Business importance' = no (Impressum of the used website is successfully scraped and we have not found HRA/HRB in it's content or a user has manually changed this state to 'no') + the used category is eligible for legal-form blacklisting => the new Data Set will be also automatically blacklisted with the reason 'category-forbidden' and the comment "Legal-form blacklisting due to GMB Category. Requested from M.Koehler on 25.03.2025"

* an each **new website** for an Account

+ if the Impressum of the new website is successfully scraped and we have not found HRA/HRB in it's content + the Account has a category eligible for legal-form blacklisting => the new Data Set will be also automatically blacklisted with the reason "Legal-form blacklisting due to GMB Category. Requested from M.Koehler on 25.03.2025"

* on each **new phone** for an Account

+ if the new phone number exists in the system and is already blacklisted for any other Data Sets => the new Data Set will be also automatically blacklisted for the same reason.  This chained blacklist is skipped if the blacklist reason is category-forbidden.

* on each **new mail** for an Account

+ if the new mail exists in the system and is already blacklisted for any other Data Sets => the new Data Set will be also automatically blacklisted for the same reason.  This chained blacklist is skipped if the blacklist reason is category-forbidden.

Once the GMB enrichment is executed on an existing Data Set, each new category/phone/website in the system could potentially blacklist the business based on the above described rules.

#### 2.2. Websites URL validation

Prevent inserting non working websites via new account form creation, add/edit website widget or GMB enrichment processes. The system will allow only websites with verified/working DNS records to enter in the Data Base. 

#### 2.3. Filter eligible for ZIP assign Data Sets

Limit the eligible for assignment businesses in order to provide in the ZIP lists only Data Sets with more quality (skip businesses without category and/or without a website):

* Exclude businesses without a website during the ZIP assignment process -> on LIVE since 04.07.2025
* Exclude businesses without a category during the ZIP assignment process -> on LIVE since 09.07.2025

The amount of businesses eligible for ZIP assignment based on the above limitations is changed progressively due to the continuous GMB enrichment processes:

1
complete
Business that received a category and a website becomes worthy for Sales and on next ZIP assignment will be included in the newly created ZIP lists

2
incomplete
Business that received a category/phone/website that triggers the blacklisting procedure will be excluded from all lists automatically and won't be present on next ZIP assignment