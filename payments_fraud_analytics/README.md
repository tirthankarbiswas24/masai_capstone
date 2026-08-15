# masai_capstone
Capstone project for Fintech and AI prpogram

# how to set up the project

# how to run each of the three parts end to end


# summary of design decisions

Presented below are:
1) excel formulae and their design/explanation
2) SQL queries and their design
3) Design/explanation of python notebook for payment reconciliation
4) Design of python notebook to create 
    a) Headline scorecards 
    b) Time series chart for trends
    c) Bar charts for GMV breakdown
    d) Details tabke with conditional formatting

## Part A — Excel/Sheets merchant workbook
Workbook available at merchant_workbook.xlsx

#### VLookup for merchant_name, category, and region from the merchants sheet in transactions-view tab of merchant_workbook.xlsx
Added merchants tab to merchant_workbook.xlsx sheet. Below Vlookup formulae used:

=IFERROR(IFNA(vlookup(C2,merchants!$A$1:$D$41,2,FALSE),"Merchant not found"), "Merchant not found")

=IFERROR(IFNA(vlookup(C2,merchants!$A$1:$D$41,3,FALSE),"Merchant not found"), "Merchant not found")

=IFERROR(IFNA(vlookup(C2,merchants!$A$1:$D$41,4,FALSE),"Merchant not found"), "Merchant not found")

#### HLOOKUP demonstration on a small horizontally-laid-out reference table

Added below reference data in payments_method tab of merchant_workbook.xlsx sheet. 

Data used:
| payment_method  | Wallet | UPI | Card  |
| --------------- | ------ | --- | ----- |
| fees            | 0.25%  | 0%  | 0.50% |


Hlookup formulae used:

=IFERROR(IFNA(hlookup(G2,payment_methods!$A$1:$E$2,2,FALSE),"Payment method not found"), "Payment method not found")

####  Nested IF/AND classification column labeling each transaction "High-Value Merchant Day" when a merchant's daily transaction total (via a pivot table) exceeds INR 5,000 and its region is not "East"

Added 3 new columns
1) transaction_date: Converted ttransaction_time to Date
Formula used: =int(D2)
2) daily_amount_total: Total of amount_inr for a merchant on a day. 
Formula used: =SUMIFS(F:F,C:C,C2,E:E,E2)
3) highvalue_merchant_day: Checks daily_amount_total > 5000 and region not east. It adds text as "Normal" if condition not met or High-Value Merchant Day if condition met. 
Formula used: =IF(AND(N2 > 5000, L2 <> "East"), "High-Value Merchant Day", "Normal")

####  Pivot table summarizing total amount_inr and count of transactions by merchant_id and status, 
1) Added a pivot table with rows: merchant_id and status
2) Added Values: sum(amount_inr) and count(transaction_id)

#### Pivot table to show count-vs-count-unique comparison (unique days transacted vs. total transaction count)
1) Added a pivot table with rows: merchant_id
2) Added Values: Count Unique of transaction_date and count of transaction_id

## SQL Queries for PART 1 - TASK PART B
Created tables and improted data from csv files into the tables. sqlite3 database file available in paytm_payments.db.

Below are the 6 SQL queries that cover all the requirements:

#### 1) Quantify chargeback impact: count of chargeback transactions, unique users affected, total chargeback amount.

select count(*) as users_impacted, count(distinct user_id) as distinct_users_impacted, sum(amount_inr) as total_amount from transactions where status = 'chargeback'

Result -->
users_impacted	distinct_users_impacted	total_amount
28		27			54472

#### 2) Identify burner accounts: users whose signup_date is less than 30 days before their transaction's transaction_time

select t.user_id, t.transaction_id, JULIANDAY(t.transaction_time) - JULIANDAY(u.signup_date) as diff
from transactions t join users u on t.user_id = u.user_id
where t.status='chargeback' and diff < 30 and diff >= 0;

Result -->
user_id	transaction_id	diff
351	TXN200000	15.0
352	TXN200001	11.0
353	TXN200002	11.0
354	TXN200003	23.0
355	TXN200004	11.0
356	TXN200005	11.0
357	TXN200006	4.0
358	TXN200007	22.0
359	TXN200008	7.0
360	TXN200009	22.0
361	TXN200010	9.0
362	TXN200011	15.0
363	TXN200012	17.0
364	TXN200013	18.0
365	TXN200014	22.0


#### 3) Detect velocity attacks: users with 3 or more transactions within any 10-minute window

WITH txn_windows AS (
    SELECT 
        user_id,
        transaction_time,
        LAG(transaction_time, 2) OVER (PARTITION BY user_id ORDER BY transaction_time) AS prior_time,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY transaction_time) AS rn
    FROM transactions
)
SELECT user_id, transaction_time, prior_time
FROM txn_windows tw
WHERE prior_time IS NOT NULL
  AND (strftime('%s', transaction_time) - strftime('%s', prior_time)) <= 600
  AND NOT EXISTS (
      SELECT 1
      FROM txn_windows tw2
      WHERE tw2.user_id = tw.user_id
        AND tw2.rn < tw.rn
        AND (strftime('%s', tw2.transaction_time) - strftime('%s', tw2.prior_time)) <= 600
        AND tw2.transaction_time >= tw.prior_time
  );

Result -->
user_id	transaction_time	prior_time
59	2026-01-09 21:02:00	2026-01-09 21:00:00
73	2026-01-12 09:02:00	2026-01-12 09:00:00
154	2026-01-02 22:02:00	2026-01-02 22:00:00
200	2026-01-01 22:02:00	2026-01-01 22:00:00
229	2026-01-12 12:02:00	2026-01-12 12:00:00
287	2026-01-14 14:02:00	2026-01-14 14:00:00
314	2026-01-02 18:02:00	2026-01-02 18:00:00
345	2026-01-23 09:02:00	2026-01-23 09:00:00

 #### 4) List all the users and count of their ransactions. Count should be 0 in case there are no transactions for the user but it should be present in the result

select u.user_id, u.signup_date, count(t.transaction_id) as Number_transactions from users u left join transactions t on u.user_id = t.user_id 
group by u.user_id order by u.user_id;

Result -->
user_id	signup_date	Number_transactions
1	2024-06-04 00:00:00	1
2	2025-03-27 00:00:00	0
3	2025-06-18 00:00:00	1
4	2024-08-16 00:00:00	1
5	2024-11-09 00:00:00	0
6	2025-03-01 00:00:00	1
7	2024-02-16 00:00:00	0
8	2024-05-11 00:00:00	2
9	2025-04-22 00:00:00	0
10	2025-01-04 00:00:00	0
11	2025-10-06 00:00:00	1
12	2025-04-12 00:00:00	0
13	2025-10-31 00:00:00	1
14	2025-01-13 00:00:00	5
15	2024-10-18 00:00:00	2
16	2025-03-03 00:00:00	1
17	2025-09-26 00:00:00	1
18	2025-04-30 00:00:00	0
19	2024-05-01 00:00:00	1
20	2025-01-14 00:00:00	2
21	2025-04-29 00:00:00	1
22	2024-01-31 00:00:00	3
23	2024-07-09 00:00:00	0
24	2024-10-23 00:00:00	2
25	2024-02-13 00:00:00	1
26	2024-08-20 00:00:00	2
27	2025-07-09 00:00:00	0
28	2025-03-06 00:00:00	1
29	2025-07-13 00:00:00	1
30	2025-03-25 00:00:00	1
31	2024-05-07 00:00:00	0
32	2024-05-30 00:00:00	2
33	2025-03-08 00:00:00	2
34	2024-04-13 00:00:00	0
35	2024-09-20 00:00:00	0
36	2024-04-14 00:00:00	1
37	2024-10-20 00:00:00	0
38	2024-11-27 00:00:00	3
39	2025-04-22 00:00:00	2
40	2025-07-14 00:00:00	0
41	2024-06-29 00:00:00	1
42	2024-07-15 00:00:00	5
43	2025-08-31 00:00:00	0
44	2025-10-15 00:00:00	2
45	2025-08-12 00:00:00	0
46	2025-06-29 00:00:00	1
47	2024-02-29 00:00:00	0
48	2025-06-22 00:00:00	0
49	2024-01-06 00:00:00	0
50	2024-09-26 00:00:00	0
51	2024-04-01 00:00:00	3
52	2025-09-28 00:00:00	2
53	2024-11-03 00:00:00	2
54	2024-11-07 00:00:00	1
55	2024-04-01 00:00:00	2
56	2024-08-10 00:00:00	2
57	2024-06-09 00:00:00	2
58	2025-03-20 00:00:00	0
59	2024-05-15 00:00:00	8
60	2025-11-21 00:00:00	2
61	2024-01-06 00:00:00	0
62	2025-08-07 00:00:00	1
63	2024-01-04 00:00:00	2
64	2024-06-01 00:00:00	1
65	2025-03-04 00:00:00	2
66	2024-02-15 00:00:00	1
67	2024-12-19 00:00:00	2
68	2025-08-10 00:00:00	0
69	2025-02-05 00:00:00	1
70	2024-09-13 00:00:00	2
71	2025-06-24 00:00:00	2
72	2024-08-25 00:00:00	0
73	2025-11-29 00:00:00	4
74	2025-03-08 00:00:00	2
75	2024-07-08 00:00:00	1
76	2025-06-03 00:00:00	1
77	2024-07-01 00:00:00	2
78	2025-08-16 00:00:00	2
79	2024-03-02 00:00:00	2
80	2025-01-31 00:00:00	0
81	2024-02-17 00:00:00	2
82	2024-07-01 00:00:00	2
83	2024-03-19 00:00:00	0
84	2025-05-13 00:00:00	0
85	2025-06-29 00:00:00	2
86	2024-11-15 00:00:00	1
87	2025-06-20 00:00:00	1
88	2024-05-29 00:00:00	1
89	2024-06-07 00:00:00	3
90	2025-12-02 00:00:00	1
91	2024-03-29 00:00:00	1
92	2025-01-05 00:00:00	2
93	2024-07-20 00:00:00	1
94	2025-11-13 00:00:00	1
95	2025-08-10 00:00:00	2
96	2024-11-26 00:00:00	0
97	2025-01-22 00:00:00	2
98	2025-04-01 00:00:00	0
99	2025-10-04 00:00:00	1
100	2025-03-31 00:00:00	2
101	2024-05-01 00:00:00	0
102	2025-09-13 00:00:00	1
103	2025-09-06 00:00:00	3
104	2024-07-23 00:00:00	0
105	2025-09-23 00:00:00	1
106	2024-06-05 00:00:00	1
107	2025-07-27 00:00:00	0
108	2025-07-24 00:00:00	0
109	2024-01-27 00:00:00	2
110	2024-08-03 00:00:00	2
111	2024-05-19 00:00:00	0
112	2025-06-16 00:00:00	2
113	2025-03-06 00:00:00	0
114	2024-06-10 00:00:00	1
115	2024-03-21 00:00:00	1
116	2024-09-25 00:00:00	1
117	2025-04-30 00:00:00	0
118	2024-05-29 00:00:00	1
119	2025-05-11 00:00:00	1
120	2025-01-17 00:00:00	1
121	2024-10-20 00:00:00	1
122	2024-01-15 00:00:00	2
123	2024-02-06 00:00:00	1
124	2024-11-15 00:00:00	1
125	2024-09-10 00:00:00	1
126	2024-06-21 00:00:00	1
127	2024-08-27 00:00:00	1
128	2025-08-01 00:00:00	1
129	2025-03-24 00:00:00	0
130	2025-04-16 00:00:00	1
131	2025-09-28 00:00:00	1
132	2024-12-21 00:00:00	1
133	2025-11-11 00:00:00	1
134	2024-04-09 00:00:00	2
135	2024-05-14 00:00:00	0
136	2025-04-11 00:00:00	2
137	2024-04-09 00:00:00	3
138	2025-04-21 00:00:00	3
139	2025-11-25 00:00:00	1
140	2025-09-21 00:00:00	2
141	2024-02-25 00:00:00	0
142	2025-10-03 00:00:00	1
143	2025-04-12 00:00:00	1
144	2025-09-24 00:00:00	1
145	2025-10-31 00:00:00	3
146	2024-12-29 00:00:00	0
147	2025-09-21 00:00:00	3
148	2024-06-24 00:00:00	5
149	2025-04-03 00:00:00	4
150	2025-02-20 00:00:00	2
151	2024-01-17 00:00:00	2
152	2024-07-23 00:00:00	4
153	2025-04-27 00:00:00	1
154	2024-05-29 00:00:00	8
155	2025-07-20 00:00:00	1
156	2024-04-27 00:00:00	1
157	2024-04-21 00:00:00	1
158	2024-08-05 00:00:00	3
159	2025-03-29 00:00:00	4
160	2024-08-05 00:00:00	1
161	2024-10-12 00:00:00	2
162	2025-05-22 00:00:00	1
163	2025-08-28 00:00:00	1
164	2025-08-25 00:00:00	2
165	2024-01-28 00:00:00	1
166	2024-09-17 00:00:00	4
167	2024-12-05 00:00:00	3
168	2024-09-25 00:00:00	1
169	2024-10-08 00:00:00	2
170	2024-08-11 00:00:00	3
171	2025-10-08 00:00:00	2
172	2024-01-13 00:00:00	0
173	2024-02-02 00:00:00	2
174	2024-02-10 00:00:00	4
175	2025-08-24 00:00:00	0
176	2025-10-01 00:00:00	0
177	2024-10-16 00:00:00	3
178	2024-12-20 00:00:00	1
179	2025-08-13 00:00:00	1
180	2025-03-23 00:00:00	0
181	2025-05-20 00:00:00	2
182	2025-05-22 00:00:00	1
183	2024-06-01 00:00:00	1
184	2024-08-30 00:00:00	1
185	2025-07-12 00:00:00	2
186	2024-09-26 00:00:00	4
187	2025-05-29 00:00:00	1
188	2025-02-20 00:00:00	1
189	2024-08-16 00:00:00	2
190	2025-03-22 00:00:00	2
191	2025-09-16 00:00:00	0
192	2024-09-05 00:00:00	0
193	2024-05-18 00:00:00	0
194	2025-08-24 00:00:00	1
195	2025-10-12 00:00:00	1
196	2024-02-04 00:00:00	2
197	2024-05-28 00:00:00	2
198	2025-11-17 00:00:00	0
199	2025-08-29 00:00:00	2
200	2025-04-04 00:00:00	5
201	2025-06-15 00:00:00	0
202	2024-10-12 00:00:00	0
203	2024-07-23 00:00:00	3
204	2024-07-28 00:00:00	5
205	2025-04-28 00:00:00	1
206	2024-10-18 00:00:00	1
207	2025-10-03 00:00:00	2
208	2025-06-17 00:00:00	1
209	2024-11-09 00:00:00	0
210	2025-11-30 00:00:00	0
211	2024-10-29 00:00:00	5
212	2025-03-06 00:00:00	0
213	2024-08-24 00:00:00	4
214	2025-02-13 00:00:00	1
215	2024-09-25 00:00:00	1
216	2024-05-12 00:00:00	4
217	2024-01-25 00:00:00	1
218	2024-07-22 00:00:00	1
219	2025-06-27 00:00:00	0
220	2025-05-22 00:00:00	0
221	2025-02-02 00:00:00	2
222	2025-04-24 00:00:00	2
223	2025-10-04 00:00:00	0
224	2024-04-18 00:00:00	2
225	2024-05-26 00:00:00	1
226	2025-10-01 00:00:00	1
227	2025-01-15 00:00:00	3
228	2025-10-05 00:00:00	1
229	2025-10-12 00:00:00	5
230	2024-04-13 00:00:00	2
231	2024-08-01 00:00:00	5
232	2024-07-06 00:00:00	0
233	2024-06-07 00:00:00	1
234	2025-06-24 00:00:00	1
235	2025-10-05 00:00:00	3
236	2024-06-30 00:00:00	3
237	2025-09-11 00:00:00	1
238	2025-05-26 00:00:00	0
239	2025-09-23 00:00:00	1
240	2024-04-02 00:00:00	0
241	2025-09-24 00:00:00	3
242	2024-01-11 00:00:00	2
243	2025-04-06 00:00:00	0
244	2024-10-15 00:00:00	2
245	2025-08-02 00:00:00	3
246	2024-04-28 00:00:00	5
247	2025-03-25 00:00:00	1
248	2024-04-19 00:00:00	2
249	2024-04-03 00:00:00	1
250	2025-10-23 00:00:00	1
251	2024-03-08 00:00:00	1
252	2025-09-10 00:00:00	3
253	2024-09-29 00:00:00	0
254	2024-01-29 00:00:00	2
255	2024-04-14 00:00:00	1
256	2024-05-03 00:00:00	0
257	2024-06-15 00:00:00	0
258	2025-01-13 00:00:00	3
259	2025-03-10 00:00:00	1
260	2025-05-07 00:00:00	2
261	2024-01-17 00:00:00	1
262	2025-01-15 00:00:00	1
263	2025-04-02 00:00:00	1
264	2025-03-06 00:00:00	0
265	2024-10-23 00:00:00	1
266	2025-07-21 00:00:00	3
267	2024-01-15 00:00:00	1
268	2024-02-11 00:00:00	0
269	2025-01-29 00:00:00	3
270	2024-08-21 00:00:00	0
271	2025-01-13 00:00:00	0
272	2025-09-19 00:00:00	2
273	2025-11-23 00:00:00	1
274	2024-08-20 00:00:00	2
275	2024-03-06 00:00:00	0
276	2024-05-05 00:00:00	4
277	2025-08-22 00:00:00	6
278	2025-09-18 00:00:00	1
279	2024-05-31 00:00:00	1
280	2025-04-28 00:00:00	1
281	2024-07-02 00:00:00	1
282	2025-03-06 00:00:00	1
283	2025-07-20 00:00:00	4
284	2024-12-10 00:00:00	1
285	2025-09-23 00:00:00	0
286	2025-03-27 00:00:00	2
287	2024-11-19 00:00:00	7
288	2025-02-14 00:00:00	4
289	2025-06-24 00:00:00	2
290	2024-09-10 00:00:00	2
291	2024-05-25 00:00:00	2
292	2025-01-27 00:00:00	2
293	2024-03-16 00:00:00	1
294	2024-02-02 00:00:00	0
295	2024-06-09 00:00:00	1
296	2025-11-24 00:00:00	2
297	2024-01-19 00:00:00	2
298	2024-05-14 00:00:00	0
299	2025-01-30 00:00:00	0
300	2024-01-23 00:00:00	0
301	2025-08-18 00:00:00	2
302	2025-07-18 00:00:00	1
303	2025-03-07 00:00:00	0
304	2025-08-06 00:00:00	0
305	2025-08-15 00:00:00	2
306	2024-05-15 00:00:00	5
307	2025-06-26 00:00:00	2
308	2025-02-27 00:00:00	0
309	2025-02-17 00:00:00	2
310	2024-03-23 00:00:00	2
311	2025-05-01 00:00:00	2
312	2024-12-16 00:00:00	1
313	2025-05-08 00:00:00	3
314	2024-02-22 00:00:00	5
315	2025-03-07 00:00:00	1
316	2024-07-03 00:00:00	1
317	2024-07-20 00:00:00	2
318	2025-03-20 00:00:00	1
319	2025-10-11 00:00:00	0
320	2025-08-30 00:00:00	0
321	2024-02-22 00:00:00	1
322	2024-09-25 00:00:00	1
323	2025-02-22 00:00:00	3
324	2025-10-18 00:00:00	1
325	2025-11-29 00:00:00	2
326	2024-12-26 00:00:00	5
327	2025-07-22 00:00:00	3
328	2024-02-19 00:00:00	2
329	2025-03-09 00:00:00	4
330	2025-06-20 00:00:00	2
331	2024-09-06 00:00:00	2
332	2024-05-17 00:00:00	1
333	2024-09-21 00:00:00	0
334	2024-05-07 00:00:00	2
335	2025-11-23 00:00:00	1
336	2025-08-10 00:00:00	2
337	2025-09-16 00:00:00	1
338	2025-07-03 00:00:00	4
339	2024-05-23 00:00:00	0
340	2025-10-27 00:00:00	3
341	2024-11-19 00:00:00	2
342	2024-04-15 00:00:00	1
343	2024-05-16 00:00:00	3
344	2025-07-04 00:00:00	0
345	2024-09-18 00:00:00	5
346	2025-07-25 00:00:00	2
347	2025-10-21 00:00:00	0
348	2025-01-21 00:00:00	2
349	2024-11-24 00:00:00	2
350	2025-10-23 00:00:00	2
351	2026-01-15 06:00:00	1
352	2025-12-31 12:00:00	1
353	2026-01-10 14:00:00	1
354	2025-12-29 19:00:00	1
355	2026-01-05 12:00:00	1
356	2026-01-18 07:00:00	1
357	2026-01-19 11:00:00	1
358	2026-01-06 05:00:00	1
359	2026-01-18 22:00:00	1
360	2025-12-22 13:00:00	1
361	2026-01-11 07:00:00	1
362	2026-01-08 02:00:00	1
363	2026-01-06 17:00:00	1
364	2026-01-04 22:00:00	1
365	2025-12-27 21:00:00	1


### 5) List users with more than 3 transactions, limit to top 5 users only

select user_id, count(*) as cnt from transactions group by user_id having cnt > 3 order by cnt desc limit 5

Result --> 

user_id	cnt
154	8
59	8
287	7
277	6
345	5

#### 6) Calculate total amount by merchant category

select sum(t.amount_inr) as total_amount, m.category from transactions t join merchants m on m.merchant_id = t.merchant_id
group by m.category order by total_amount desc;

Result -->

total_amount	category
79896	ecommerce
75250	travel
71936	grocery
57205	food_delivery
56887	entertainment
26304	bill_payment
15125	recharge

### Part C — Python payment reconciliation

Code available in reconcile.ipynb file

### Part D — Four-layer analytics dashboard
All logic available in dashboard.ipynb file

#### Chart for Score cards
Created 2 functions create_scorecard and create_header_plot. 

1) Used the ledger_df from ledger.csv and used ledger_df['amount_inr'].sum() to get Total GMV scorecard

2) Used len(ledger_df[ledger_df['status'] == 'captured']) / len(ledger_df) * 100 to calculate overall success rate

3) For reconciliation rate, fetched the common ids, merged them into comparison_df and then compared amount_inr  and status. If they are same added it to common_df. Then reconciliation rate was calculated as reconciliation_match_rate = len(common_df) / len(ledger_df) * 100

4) chargeback ratio was calculated as len(ledger_df[ledger_df['status'] == 'chargeback']) / len(ledger_df) * 100

![alt text](img1.png)

#### Time series chart of daily GMV and daily chargeback count over the 30-day window

Used the below code to get data for time series:

ledger_df['transaction_date'] = pd.to_datetime(ledger_df['transaction_time']).dt.date

ledger_chart_gmv_df = ledger_df.groupby('transaction_date')['amount_inr'].sum()

ledger_chart_chargeback_df = ledger_df[ledger_df['status'] == 'chargeback'].groupby('transaction_date')['amount_inr'].count()

ledger_chart_df = pd.merge(ledger_chart_gmv_df, ledger_chart_chargeback_df, on = 'transaction_date',
                           how="outer", suffixes=("_gmv", "_chargeback_count")).fillna(0)

ledger_chart_df['amount_inr_chargeback_count'] = ledger_chart_df['amount_inr_chargeback_count'].astype(int)

![alt text](img2.png)

#### Bar Charts of GMV by payment_method and by category (joined from merchants).

Got the data for the bar chart using the below code
payment_method_agg_df = ledger_df.groupby('payment_method')['amount_inr'].sum()

ledger_merchant_category_df = pd.merge(ledger_df, merchant_df, on='merchant_id')

merchant_category_agg_df = ledger_merchant_category_df.groupby('category')['amount_inr'].sum()

![alt text](img3.png)

#### Table of top 10 merchants by transaction count, with conditional highlighting (e.g., a flag column) for any merchant whose chargeback_ratio exceeds 1% : chargeback_ratio (per-merchant) = (count of that merchant's transactions with status == "chargeback") / (count of all of that merchant's transactions).

Used the below code to get the data to plot

top_merchants_df = ledger_df.groupby('merchant_id')['transaction_id'].count().to_frame()

top_merchants_df = top_merchants_df.rename(columns={'transaction_id':'transaction_count'})

merchants_chargeback_df = ledger_df[ledger_df['status'] == 'chargeback'].groupby('merchant_id')['transaction_id'].count().to_frame().rename(columns={'transaction_id':'chargeback_count'})

top_merchants_flag_df  = pd.merge(top_merchants_df, merchants_chargeback_df, on='merchant_id', how='left')

top_merchants_flag_df['chargeback_count'] = top_merchants_flag_df['chargeback_count'].fillna(0)

top_merchants_flag_df['flag'] = top_merchants_flag_df['chargeback_count'] / top_merchants_flag_df['transaction_count'] * 100 > 1

top_merchants_flag_df = top_merchants_flag_df.sort_values(by='transaction_count', ascending=False)

Then used code to conditionally format the table based the 'flag' value. 

![alt text](img4.png)

