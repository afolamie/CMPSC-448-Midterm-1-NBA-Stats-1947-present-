# ChatGPT pilot collection

Three NBA examples grounded in the user-supplied Advanced.csv from [NBA Stats (1947–present)](https://www.kaggle.com/datasets/sumitrodatta/nba-aba-baa-stats).

## Files and required fields

[pilot.json](pilot.json) contains one record per response, including the required `LLM_name`, `LLM_Input`, and `LLM_output` fields. Each complete input includes its numerical source table. Prompt IDs preserve alignment when collecting other model families.

## Data preparation

- Seasons are identified by ending year: 2016, 2021, and 1996.
- Prompt 1 selects Stephen Curry and LeBron James in 2016.
- Prompt 2 selects the three highest-minute player rows separately for MIL and BRK in 2021. These are Middleton, Antetokounmpo, Holiday, Harris, Irving, and Green. These player rows are not team aggregates.
- Prompt 3 includes every CHI player row in 1996, ordered by minutes.
- Values are copied from the uploaded file; TS% is stored as a decimal fraction. The other percentage columns already contain percentage values.
- Actual on-court plus-minus, per-game statistics, and shooting percentages absent from this file are not supplied. BPM is not actual plus-minus.
- Source SHA-256: `e1616ffe7759c22b014cbbb7c7ce10a591615e7ef1e08cc0dba4d2a02872948d`.
- The source collection includes other leagues; these selected rows are NBA rows.

## Collection provenance and limitations

The responses were generated on October 8, 2026 by the assistant in the existing ChatGPT Work project conversation, with prior discussion and user writing preferences in context. They were not collected through isolated calls using only the recorded prompt. Exact backend model version and sampling settings were not available and are not invented. The label ChatGPT identifies the interface; GPT identifies the family.

These are newly generated responses to the revised, dataset-grounded questions, not the earlier web-supported answers. AI assisted with prompt preparation, extraction, response generation, and repository additions. Response lengths are 172, 170, 176 words; see the actual response text for counting conventions.

Treat this as a pilot for checking the schema and collection procedure, not the final training or evaluation corpus. Three responses from one family do not satisfy the three-family requirement or provide enough independent examples for credible CNN/LSTM evaluation.

## Next collection steps

Copy each full LLM_Input unchanged into a fresh conversation for each selected model, with browsing and personalization consistently disabled where possible. Record the actual model/version shown, collection date, settings when available, and the response without rewriting it. Recollect the GPT examples under this same protocol for the final corpus. Do not fabricate Claude or Gemini responses.

Expand to many distinct prompts and keep family counts balanced. Keep all responses to the same prompt, and close variants based on the same records, in the same train/validation/test partition. The three pilot categories are all basketball tasks; a later transfer experiment should clearly specify its held-out task.

## Rubric status

This section starts dataset curation and documents provenance. CNN and RNN implementation, the prompt-only/response-only/combined comparisons for RQ1–RQ2, evaluation results, analyses, lessons, and the final PDF report remain to be completed. No performance results are claimed.

## Prompts for collection

### nba_pilot_001

```text
Compare Stephen Curry and LeBron James during the 2015–16 NBA regular season using the supplied statistics. Analyze scoring efficiency, estimated assist and rebounding rates, offensive usage, and estimated overall contribution. Explain that AST% and TRB% are not per-game averages and that BPM is not actual on-court plus-minus. Support your comparison with specific numbers. Use only the supplied data. Write 150–200 words.

Data from Advanced.csv. ts_percent is a decimal fraction (0.669 = 66.9%); other percentage columns are already percentages. mp means total minutes; ws_48 means win shares per 48 minutes. MIL = Milwaukee; BRK = Brooklyn.

player,ts_percent,ast_percent,trb_percent,usg_percent,bpm,ws_48
Stephen Curry,0.669,33.7,8.6,32.6,11.9,0.318
LeBron James,0.588,36,11.8,31.4,9,0.242
```

### nba_pilot_002

```text
Compare the individual player profiles of the Milwaukee Bucks and Brooklyn Nets during the 2020–21 NBA regular season using the supplied player rows. Use minutes played, true shooting percentage (TS%), usage percentage (USG%), assist percentage (AST%), total rebound percentage (TRB%), and Box Plus/Minus (BPM). Focus on the three players with the most minutes for each team. Discuss how their statistical profiles differ. Do not add or average player percentages to claim team-level efficiency, and do not treat these six players as the complete rosters. Use only the supplied data, without referring to injuries or playoff results. Write 150–200 words.

Data from Advanced.csv. ts_percent is a decimal fraction (0.669 = 66.9%); other percentage columns are already percentages. mp means total minutes; ws_48 means win shares per 48 minutes. MIL = Milwaukee; BRK = Brooklyn.

player,team,mp,ts_percent,usg_percent,ast_percent,trb_percent,bpm
Khris Middleton,MIL,2269,0.588,25,23.2,9.4,1.3
Giannis Antetokounmpo,MIL,2013,0.633,32.5,28.7,17.5,9
Jrue Holiday,MIL,1907,0.592,22.2,26.3,7.4,3.4
Joe Harris,BRK,2141,0.663,16.2,8.4,6.4,0.4
Kyrie Irving,BRK,1886,0.614,30.4,28.6,7.5,5.5
Jeff Green,BRK,1835,0.624,15.6,7.8,7.9,-0.8
```

### nba_pilot_003

```text
Analyze Michael Jordan’s role on the Chicago Bulls during the 1995–96 NBA regular season using the supplied advanced statistics for Jordan and his teammates. Compare true shooting percentage (TS%), usage percentage (USG%), assist percentage (AST%), Box Plus/Minus (BPM), and win shares (WS). Use minutes played to provide context for differences in playing time. Explain what these measures suggest about Jordan’s offensive responsibilities and estimated contribution. Distinguish scoring efficiency from scoring volume: this data does not provide points per game. Explain why these statistics cannot establish how the Bulls would have performed without him. Use only the supplied data. Write 150–200 words.

Data from Advanced.csv. ts_percent is a decimal fraction (0.669 = 66.9%); other percentage columns are already percentages. mp means total minutes; ws_48 means win shares per 48 minutes. MIL = Milwaukee; BRK = Brooklyn.

player,mp,ts_percent,usg_percent,ast_percent,bpm,ws
Michael Jordan,3090,0.582,33.3,21.2,10.5,20.4
Scottie Pippen,2825,0.551,24.4,25.2,6.3,12.3
Toni Kukoč,2103,0.589,21.4,21,5.4,10.1
Dennis Rodman,2088,0.501,10.3,10,0,6.2
Steve Kerr,1919,0.663,12.9,14.1,3.4,8.3
Ron Harper,1886,0.528,14.9,15.5,2.6,6.3
Luc Longley,1641,0.515,17.8,10.6,-1.6,3.5
Bill Wennington,1065,0.519,16.5,6.4,-3.2,2.8
Jud Buechler,740,0.552,17.3,11.1,1.7,2.3
Dickey Simpkins,685,0.533,16.7,7.7,-3.7,1.2
Randy Brown,671,0.436,16,15.1,-0.2,1.5
Jason Caffey,545,0.474,19.4,6.3,-7.1,0.4
James Edwards,274,0.403,22.9,5.9,-12.2,-0.2
John Salley,191,0.411,13.8,10.2,-2.8,0.2
Jack Haley,7,0.363,49.6,0,-22.4,0
```
