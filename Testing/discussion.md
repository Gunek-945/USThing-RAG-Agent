# Content retrieval discussions
Implications revealed by tests

## amount of info --12 Sep, 2024
- works fine when only faculty related info - replication-faculty.json
- not so when we also include other info due to incorrect retreival - replication-all-content.json
- interestingly, in replication-all-content, test1, nothing is matched but the response is okay

## stop words?  --12 Sep, 2024
- removed stop words from user input before giving retriever: replication-all-content2.json
- improved response in tests 3 and 4.
- However, now test 1 suffers from incorrect matches and failed responses.
- Question: should we keep this approach?

## chunk size and overlap --18 Sep, 2024
- chunk size 4000, overlap 200: replication-all-content3.json, replication-all-content4.json
    - worse perforance than original setting
- chunk size 2000, overlap 100: replication-all-content5.json (with stop word technique)
    - improvement! now of the original 5 questions that the LLM is not able to respond properly, only one remains (Q4)
