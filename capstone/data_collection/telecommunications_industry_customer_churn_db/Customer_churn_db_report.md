# Data Profile Report
Telecommunications Industry Customer churn DB

About Dataset
The Telco customer churn data contains information about a fictional telco company that provided home phone and Internet services to 7043 customers in California in Q3. It indicates which customers have left, stayed, or signed up for their service. Multiple important demographics are included for each customer, as well as a Satisfaction Score, Churn Score, and Customer Lifetime Value (CLTV) index.
All data is present in both .csv and .xlsx file format.

This dataset contains 2 main files: 1 with less features / columns about customers (WA_Fn-UseC_-Telco-Customer-Chur table in CustomerChurn.xlsx) and one with more details (CustomerChurn.xlsx in Telco_customer_churn.xlsx), other than that it contains 5 tables:

Demographics
Location
Population
Services
Status

Each table is described below.
Demographics
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
Population
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


## Overview
- Number of rows: 7043
- Number of columns: 23
- Missing cells: 22

## Columns

### CustomerID
- Type: Numeric
- Mean: 4521.0
- Min: 1000
- Max: 8042

### Age
- Type: Numeric
- Mean: 46.50972596904728
- Min: 19
- Max: 80

### Number_of_Dependents
- Type: Numeric
- Mean: 0.4686923186142269
- Min: 0
- Max: 9

### JoinDate
- Type: DateTime
- Min: 2015-01-01 00:00:00
- Max: 2020-12-01 00:00:00

### Tenure
- Type: Numeric
- Mean: 32.37114865824223
- Min: 0
- Max: 72

### Avg_Monthly_GB_Download
- Type: Numeric
- Mean: 20.515405367031093
- Min: 0
- Max: 85

### Monthly_Charges
- Type: Numeric
- Mean: 64.76169248137157
- Min: 18.25
- Max: 118.75

### Total_Charges
- Type: Numeric
- Mean: 2283.3004413818944
- Min: 18.79999924
- Max: 8684.799805

### Total_Refunds
- Type: Numeric
- Mean: 1.9621823065882436
- Min: 0.0
- Max: 49.79000092

### Total_Extra_Data_Charges
- Type: Numeric
- Mean: 6.860712764446968
- Min: 0
- Max: 150

### Avg_Monthly_Long_Distance_Charges
- Type: Numeric
- Mean: 22.958953571299162
- Min: 0.0
- Max: 49.99000168

### Total_Long_Distance_Charges
- Type: Numeric
- Mean: 749.099261397996
- Min: 0.0
- Max: 3564.719971

### Total_Revenue
- Type: Numeric
- Mean: 3038.163729318147
- Min: 21.36000061
- Max: 11979.33984

### Satisfaction_Score
- Type: Categorical

### DependencyID
- Type: Categorical

### Marital_Status_ID
- Type: Categorical

### LocationID
- Type: Numeric
- Mean: 784.8012210705665
- Min: 1
- Max: 1670

### Customer_Status_ID
- Type: Categorical

### Internet_Service_ID
- Type: Categorical

### BillingID
- Type: Categorical

### paymentID
- Type: Categorical

### ContractID
- Type: Categorical

### Phone_Service_ID
- Type: Categorical

