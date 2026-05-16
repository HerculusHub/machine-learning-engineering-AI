# Explanation of the Three Databases in This Folder and Their Business Logic

## Telecommunications Industry Customer churn DB

### About Dataset

The Telco customer churn data contains information about a fictional telco company that provided home phone and Internet services to 7043 customers in California in Q3. It indicates which customers have left, stayed, or signed up for their service. Multiple important demographics are included for each customer, as well as a Satisfaction Score, Churn Score, and Customer Lifetime Value (CLTV) index.
All data is present in .csv format. 

It comprises a primary `Customer.csv` file and 16 additional files providing specific details. The data profiling reports for these 17 files are located in the `data_profiling` folder. Documentation regarding the main `Customer.csv` file can be found in `Customer_churn_db_report.md`, located within the `telecommunications_industry_customer_churn_db` folder.

Each table is described below.

CustomerID: A unique ID that identifies each customer.
Count: A value used in reporting/dashboarding to sum up the number of customers in a filtered set.
Gender: The customer’s gender: Male, Female
Age: The customer’s current age, in years, at the time the fiscal quarter ended.
Senior Citizen: Indicates if the customer is 65 or older: Yes, No
Married: Indicates if the customer is married: Yes, No
Dependents: Indicates if the customer lives with any dependents: Yes, No. Dependents could be children, parents, grandparents, etc.
Number of Dependents: Indicates the number of dependents that live with the customer.
Location
CustomerID: A unique ID that identifies each customer.
Count: A value used in reporting/dashboarding to sum up the number of customers in a filtered set.
Country: The country of the customer’s primary residence.
State: The state of the customer’s primary residence.
City: The city of the customer’s primary residence.
Zip Code: The zip code of the customer’s primary residence.
Lat Long: The combined latitude and longitude of the customer’s primary residence.
Latitude: The latitude of the customer’s primary residence.
Longitude: The longitude of the customer’s primary residence.
ID: A unique ID that identifies each row.
Zip Code: The zip code of the customer’s primary residence.
Population: A current population estimate for the entire Zip Code area.
Services
CustomerID: A unique ID that identifies each customer.
Count: A value used in reporting/dashboarding to sum up the number of customers in a filtered set.
Quarter: The fiscal quarter that the data has been derived from (e.g. Q3).
Referred a Friend: Indicates if the customer has ever referred a friend or family member to this company: Yes, No
Number of Referrals: Indicates the number of referrals to date that the customer has made.
Tenure in Months: Indicates the total amount of months that the customer has been with the company by the end of the quarter specified above.
Offer: Identifies the last marketing offer that the customer accepted, if applicable. Values include None, Offer A, Offer B, Offer C, Offer D, and Offer E.
Phone Service: Indicates if the customer subscribes to home phone service with the company: Yes, No
Avg Monthly Long Distance Charges: Indicates the customer’s average long distance charges, calculated to the end of the quarter specified above.
Multiple Lines: Indicates if the customer subscribes to multiple telephone lines with the company: Yes, No
Internet Service: Indicates if the customer subscribes to Internet service with the company: No, DSL, Fiber Optic, Cable.
Avg Monthly GB Download: Indicates the customer’s average download volume in gigabytes, calculated to the end of the quarter specified above.
Online Security: Indicates if the customer subscribes to an additional online security service provided by the company: Yes, No
Online Backup: Indicates if the customer subscribes to an additional online backup service provided by the company: Yes, No
Device Protection Plan: Indicates if the customer subscribes to an additional device protection plan for their Internet equipment provided by the company: Yes, No
Premium Tech Support: Indicates if the customer subscribes to an additional technical support plan from the company with reduced wait times: Yes, No
Streaming TV: Indicates if the customer uses their Internet service to stream television programing from a third party provider: Yes, No. The company does not charge an additional fee for this service.
Streaming Movies: Indicates if the customer uses their Internet service to stream movies from a third party provider: Yes, No. The company does not charge an additional fee for this service.
Streaming Music: Indicates if the customer uses their Internet service to stream music from a third party provider: Yes, No. The company does not charge an additional fee for this service.
Unlimited Data: Indicates if the customer has paid an additional monthly fee to have unlimited data downloads/uploads: Yes, No
Contract: Indicates the customer’s current contract type: Month-to-Month, One Year, Two Year.
Paperless Billing: Indicates if the customer has chosen paperless billing: Yes, No
Payment Method: Indicates how the customer pays their bill: Bank Withdrawal, Credit Card, Mailed Check
Monthly Charge: Indicates the customer’s current total monthly charge for all their services from the company.
Total Charges: Indicates the customer’s total charges, calculated to the end of the quarter specified above.
Total Refunds: Indicates the customer’s total refunds, calculated to the end of the quarter specified above.
Total Extra Data Charges: Indicates the customer’s total charges for extra data downloads above those specified in their plan, by the end of the quarter specified above.
Total Long Distance Charges: Indicates the customer’s total charges for long distance above those specified in their plan, by the end of the quarter specified above.
Status
CustomerID: A unique ID that identifies each customer.
Count: A value used in reporting/dashboarding to sum up the number of customers in a filtered set.
Quarter: The fiscal quarter that the data has been derived from (e.g. Q3).
Satisfaction Score: A customer’s overall satisfaction rating of the company from 1 (Very Unsatisfied) to 5 (Very Satisfied).
Satisfaction Score Label: Indicates the text version of the score (1-5) as a text string.
Customer Status: Indicates the status of the customer at the end of the quarter: Churned, Stayed, or Joined
Churn Label: Yes = the customer left the company this quarter. No = the customer remained with the company. Directly related to Churn Value.
Churn Value: 1 = the customer left the company this quarter. 0 = the customer remained with the company. Directly related to Churn Label.
Churn Score: A value from 0-100 that is calculated using the predictive tool IBM SPSS Modeler. The model incorporates multiple factors known to cause churn. The higher the score, the more likely the customer will churn.
Churn Score Category: A calculation that assigns a Churn Score to one of the following categories: 0-10, 11-20, 21-30, 31-40, 41-50, 51-60, 61-70, 71-80, 81-90, and 91-100
CLTV: Customer Lifetime Value. A predicted CLTV is calculated using corporate formulas and existing data. The higher the value, the more valuable the customer. High value customers should be monitored for churn.
CLTV Category: A calculation that assigns a CLTV value to one of the following categories: 2000-2500, 2501-3000, 3001-3500, 3501-4000, 4001-4500, 4501-5000, 5001-5500, 5501-6000, 6001-6500, and 6501-7000.
Churn Category: A high-level category for the customer’s reason for churning: Attitude, Competitor, Dissatisfaction, Other, Price. When they leave the company, all customers are asked about their reasons for leaving. Directly related to Churn Reason.
Churn Reason: A customer’s specific reason for leaving the company. Directly related to Churn Category.

### Business Logic

#### Churn Category

Possible categories:

Attitude
Competitor
Dissatisfaction
Other
Price

Churn Reason:

Better competitor pricing
Poor support experience
Service reliability issues

### Churn Reason Analysis

Customer Analytics
Which customers are most likely to churn?
Which demographics churn most frequently?
Which regions have the highest churn?
Revenue Analytics
Which services generate the most revenue?
Which customers have the highest CLTV?
Which products drive upsell opportunities?
Marketing Analytics
Which offers reduce churn?
Do referrals increase loyalty?
Which contract types retain customers best?
Operational Analytics
Does tech support reduce churn?
Do refunds predict dissatisfaction?
Which services create customer stickiness?

#### Business strategy 

Root cause analysis
Retention strategy design
Product improvement planning

## hypothetical_dataset: U.S. Mobile Operator Competition
### About Dataset

Provides a hypothetical dataset of competitor behavior among mobile network operators in the United States.
Below is a hypothetical dataset that captures competitor behavior among major U.S. mobile network operators like Verizon, AT&T, and T-Mobile.

The 'Hypothetical_dataset_report.md' file, located in the 'hypothetical_dataset' folder, provides detailed data profiling information.

Dataset Description
Each row represents monthly competitive behavior metrics for a carrier in a given region.

Column Name	  Description
month:	Time period
operator:	Carrier name
region:	Market region (e.g., West, Midwest)
avg_price_plan:	Average monthly plan price ($)
promo_intensity:	Scale (0–10) of promotions/discounts
customer_churn_rate:	% of customers leaving
net_adds:	Net subscriber gain/loss
avg_data_speed:	Mbps (network performance proxy)
coverage_score:	Scale (0–100)
marketing_spend:	Monthly marketing spend ($M)
competitor_price_index:	Relative price vs competitors (1 = avg)
customer_satisfaction:	Score (0–10)

### Business Logic

#### Price vs Customer Growth
•	Does lowering price increase net_adds? 
•	Compare: 
o	T-Mobile → lower price, higher growth 
o	Verizon → premium pricing, lower churn 

#### Promotions vs Churn
•	Hypothesis: Higher promo_intensity reduces churn short-term 
•	But may attract low-loyalty customers 

#### Network Quality vs Satisfaction
•	Use: 
o	avg_data_speed 
o	coverage_score 
•	Predict: 
o	customer_satisfaction 

#### Marketing Efficiency
•	Compare: 
o	marketing_spend vs net_adds 
•	Example insight: 
o	Is AT&T overspending relative to growth? 

#### Competitive Strategy Modeling

•	Actions: 
o	Price change 
o	Promotions 
o	Marketing spend 
•	Environment: 
o	Customer response (churn, net adds) 

## worldwide_mobile_network_operators

### About Dataset

This dataset compiles detailed technical and geographical information about over 150 mobile network operators around the world. 

The '2025_06_16_MobileOperators_report.md' file, located in the 'worldwide_mobile_network_operators' folder, provides detailed data profiling information.

It includes:
•	Operator names, short names, and headquarters
•	Year of establishment and background descriptions
•	Supported cellular technologies (GSM, UMTS, LTE, NR)
•	Data speeds and network frequency bands
•	Coverage areas (countries & regions)
•	Detailed notes on network types and supported data links
This dataset is ideal for anyone interested in telecom infrastructure, 5G rollout analysis, or global operator benchmarking.

### Business Logic

Having more network operators in the same area intensifies competition; 

a larger population in a region means a larger market, which can alleviate competition;

network operators with similar technologies face more intense competition; 

different technologies among network operators promote market segmentation and alleviate competition.

