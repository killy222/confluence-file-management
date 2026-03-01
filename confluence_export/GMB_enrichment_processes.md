# GMB enrichment processes

Confluence Page ID: 139267016

The GMB (Google My Business) enrichment process ensures business data in Phonix is accurate, verified, and enriched based on the business information (if found) for the business in Google location.

## What is Enriched?

* Account Name
* GMB Category
* GMB CID
* Business Status (Permanently Closed)
* Address
* Phone
* Website

## Enrichment workflow

### Entry points

GMB enrichment processes will be triggered in the following cases:

* **[One-time Bulk processes]** We will begin enriching all relevant businesses (skip these that are*already in stage “Introduction to Decision Maker” or further)*. Segment the businesses into groups based on strategic importance and execute the process on the different groups by priority:
  1. Accounts with an existing category (skip blacklisted, marked as permanently closed, already our clients)
  2. Accounts without a category (skip blacklisted, marked as permanently closed, already our clients)
  3. All businesses that are not in stage "Introduction to Decision Maker" or further and are still not enriched (= blacklisted, permanently closed accounts or our clients)

* **[Manual trigger]** A manual “Enrich via GMB” button in the interface, available to MCs and above. This will allow for targeted data updates when needed. On click the system will initiate the GMB enrichment scraping asynchronous process and will update the business data based on the response from EYE.

* **[Automatic trigger]** Additionally, every new business entered into the system will automatically be enriched via the GMB process to ensure it enters our ecosystem with the most accurate and complete information possible.

### Specific workflow

When started, the system tries to find a match in GMB for the business in Phonix based on the following logic:

1. Search by business name + city.
   * If we have only 1 result returned and the returned result for "title" != searched {business.city} and the returned result for "category" is valid based on [Listing Tool API](https://wiki.dev.fb/display/LIS/API+%7C+Business+Portal+Categories), we will use the returned data from GMB to update/add business information in Phonix. Else go to 2)
2. Search by phone
   * The system searches for all phones assigned for the business in both e164 and national format (e.g. if the account has 3 phones => 6 searches will be made). If any of them returns only one result and the returned result for "title" != searched {business.city} and the returned result for "category" is valid based on [Listing Tool API](https://wiki.dev.fb/display/LIS/API+%7C+Business+Portal+Categories),, we will use the returned data from GMB to update/add business information in Phonix
3. If the scraping process could not identify a valid result from GMB for the business, then the system will mark the GMb enrichment process as successful finished with no result from GMB received.

EYE-GMB scraper1

Specific case when the business has more than one addresses in different cities (city1, city2, city3... cityN), the enrichment will be done based on the first found valid result, that we will receive from the GMB-EYE scraper based on the all possible combinations of business name + city and afterwards on the phones.

**Data handling rules**

The result from GMB will be sanitized and compared to the data in Phonix as follow:

| Property | Procedure | Details |
| --- | --- | --- |
| name | update | update only if the returned "title" != city/ZIP searched.  The system will compare both values normalized to small letters and will update only if there's a difference between them. For example if the difference is only in a capital letter, but the string is the same, the system won't make any change and will only mark the name in Phonix as GMB verified. |
| category | add | if different => add + mark it as "GMB verified"  If the returned category is not valid based on Listing Tool API, the system will skip the enrichment processes of the business as it was no result from GMB.  Each new category in the system triggers the processes for blacklisting (if the category is in the mapping) and Branch assignment |
| "permanentlyClosed": true | update | set "status": "permanently closed" with comment = "permanently closed location in GMB"  In case the business is set to "permanently closed" during GMB enrichment processes, the system will not close any open pipelines with the business. |
| address | add | get the full address object via Google Geocoding API. if different => add it as new + mark the new address as "GMB verified"  if same => mark it as "GMB verified"  Each validated address via Google Geocoding is compared to all existing addresses for the business (string match excluding the country from the comparison if it is present). The GMB address must be in one of the active countries of operation in the system. This is required because on some rare occasions GMB returns results that are from unexpected countries. So If the returned address is not from valid countries, the system will skip the enrichment processes of the business as it was no result from GMB.  Caveats of the chosen implementation: The check is done after a business is selected which means that technically there might be a viable result that will be ignored. For example, if a business has offices if two cities in Germany and the GMB search by the first address returns a single result with address in Belgium, the scrape will be marked as 'no business found', although there might be a chance that a search by the second address might yield a relevant result. |
| phone | add | if different => If verified as phone => and add it as new + mark the new phone as "GMB verified"  if same => mark it as "GMB verified"  Each new phone in the system is checked for blacklisting rules. If the phone number is blacklisted for whatever reason in any other Data Set in the system, the current business for which it is assigned will be also automatically blacklisted for the same reason. If the new phone is not in e164 format, the system use the address from GMB to change it from local/national to e164. If there's no address returned from GMB, then the phone could not be formatted properly and the system will consider it as like no phone is returned from GMB. |
| website | add | if different => add it as new + mark the new website as "GMB verified"  if same => mark it as "GMB verified"  The system will compare both values normalized to domain + deeplink and will add a new domain only if there's a difference between them. For example: [https://ina.de](https://ina.de/ "https://ina.de/") = [https://ina.de/](https://ina.de/ "https://ina.de/") = [http://ina.de](http://ina.de/ "http://ina.de/") = [http://www.ina.de](http://www.ina.de/ "http://www.ina.de/") = [http://www.ina.de/](http://www.ina.de/ "http://www.ina.de/") = [www.ina.de](https://www.ina.de/ "https://www.ina.de/") = [ina.de](http://ina.de/) , the system won't make any change and will only mark the website in Phonix as GMB verified. But [http://ina.de](http://ina.de/ "http://ina.de/")/ <> [http://ina.de/link1](http://ina.de/link1 "http://ina.de/link1") => will add new website and will mark it as GMB verified.  The system does not allow websites with non-working DNS on add new website in the system, so if the information from GMB can not be validated via DNS check, the system won't insert new website.  The system does not allow websites with domains in the mapping  to be inserted. In case the GMB location contains such website, it will be skipped during the enrichment.  Each new website in the system:   * triggers the process for Impressum scraping and potential legal form blacklisting. * The system automatically sets the appropriate website type based on the mapping . If not in the mapping => "Unknown". * The system checks the website domain against the mapping  and if present, then automatically blacklist the business for all Brands with reason "chainstore" and comment = "Marked as chain due to website. Requested from C.Stein on 16.09.2025." |
| cid | add | if different => add it as new |

## Changes in GUI

### Introduce new action button in the Centralized Account Page for processing manual GMB enrichment

Each user of the system from MC and above has access to **new action button** in the Centralized Account Page: 

- icon with text on hover "Request GMB enrichment" (germ. "GMB-Anreicherung anfordern"). On click the system will initiate the GMB enrichment scraping asynchronous process and will update the business data based on the response from EYE. Pop-up messages and notifications are provided for the initiator on start and finish of the process.

### **Present the state for each confirmed data from GMB**

The **GMB verified label** is shown next to each property (phone/address/website...) that is confirmed, directly in the Centralized Account Page in the corresponding widget:

* If the account property (e.g. phone number) is confirmed during the last GMB enrichment processes, the system will display an icon with label "GMB" next to it. On hover "GMB verified" (germ. "GMB verifiziert").
* If a user edits a GMB verified property, the label will be automatically removed.

### **Show new summary card from GMB enrichment processes in the All Activity Feed**

For each successfully processed through GMB enrichment account the system should present in the All activities a special summary card. Depending on the way the GMB enrichment process is triggered, the card will be from:

* **[bulk or automatic]** System → if the process is started through bulk command or automatically on create new account
* **[manual]** Initiator name → if the process is started from specific user via the button in the Centralized Account Page → "Request GMB enrichment"

If during the GMB enrichment the system successfully identifies the business in Google, then the summary card will present all properties of the account and their corresponding state in the result:

* - icon with text on hover "same" (germ. "gleich") indicating that the result from GMB is the same as the data in the system.
* - icon with text on hover "new" (germ. "neu") indicating that the result from GMB is different then the data in the system.
* - icon with text on hover "no info" (germ. "keine Infos") indicating that the result from GMB does not provide data for this property.

If during the GMB enrichment the system do not receive unique result via the EYE/GMB scraping, then the summary card will only display the text "not found in GMB" (germ. "nicht in GMB gefunden").

 

 