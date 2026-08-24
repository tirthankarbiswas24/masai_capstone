# masai_capstone
Capstone project for Fintech and AI prpogram.
This Read me file provides details for credit_risk_lending_ml modeule.

# how to run this project
1) After going to this folder using "cd credit_risk_lending_ml" execute the command "python generate_data.py" to create the data in the file credit_applicants.csv and txn_behaviour.csv files
2) Code for running the models - Logistic Regression, Decision Tree, Isolation forest along with creation evaluation metrices for them is available in the python notebook "credit_risk.ipynb". Execute this notebook to get the results and output required. Steps for the same are provided below:
    a) Install ipython
    b) Go the folder credit_risk_lending_ml as was done in step 1 above
    c) execute the command ipython -c "run credit_risk.ipynb"

### Decision on encoding for employment type column/feature
Since we have only 3 values for employment_type and these are not ordinal (no meaningful order between the values)
we will use One Hot encoding and no scaling will be needed

###  justify the stratification choice
Since our default data set is highly imbalanced (80% good and 20% default), estratification nsures that the exact proportion of non-defaulters to defaulters is preserved across both training and testing dataset. If we use a standard random split instead of a stratified split, we can run into serious structural issues like missing defaulters problem, Model Bias for non defaulting customers.

## Gender/Location bias
Even though we do not have any gender or location columns in our applicats data file, these fields can have corelation with 
other feilds in our file that are used in predicting defaults like:
1) monthly_income_inr: In the world today women generally have less monthly income and hence indirectly will reduce their credit score
2) emplyment_type: Mostly women will not be of Salaried type in employment who will have a higher credit score/lower defaut rate as per model
3) credit_bureau_score: Generally women will have a lower credit score that will impact them negatively

### Governance steps to be taken:
Have a human in the loop for rejected aplication if they are from women for borderline cases. Probabaly use a maker checker mechanism where the first step could be taken by the model while the checked should typically be human

## Final model-comparison table
Below are the comparison of the credit model built using Logistic regression and Decision tree.

| Metrices | Logistic Regression | Decision Tree |
| -------- | --------            | -------- |
| Accuracy | 0.700000            | 0.730000 |
| Precision| 0.368421            | 0.347826 |
| Recall   | 0.700000            | 0.400000 |
| F1-Score | 0.482759            | 0.372093 |
| AUC      | 0.721250            | 0.721250 |

### Recommendation of classifier
In Credit decisions Recall (TP / (TP + FN)) is the most critical parameter as incorrect credit decision (FN) can cost us heavily. Accuracy is generally misleading and hence we will ignore. 
If cost of losing good borrowers is high we can have a look at Precision also (TP/ (TP + FP)). 
As a balance measure we could use F1-score. Here also Logistic regression performs better. 

Due to these reasons **for Paytm I will recommend Logistic regression model.**

However, Decision Tree has a great explanability power for the decisions (Reason for loan rejections), and if that is important from a **regulatory perspective, we could use Decision tree model.**

### Isolation Forest model
Below are the evaluation metrices for the isolation Forest model

- Isolation Forest Recall: 73.33%
- Isolation Forest Precision: 73.33%
- Isolation Forest F1-Score: 73.33%