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
