# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
Domain: on-campus housing experiences at Boston University. This knowledge is valuable for students who want to make more informed decisions when applying for and choosing their on-campus housing for future semesters. While plenty of objective information exists in official channels, reviews and experiences are more subjective, informal and sentiment-based. Official channels also won't be informative about negative aspects of each campus housing, and tend to be overly positive. Including informal student reviews is a way to obtain balanced feedback.
---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Short description | Markdown file path |
|---|--------------------|-------------------|--------------------|
| 1 | Freshman Dorm: Warren v. The Towers | A Reddit post comparing Warren and The Towers for an incoming BU freshman, with comments on convenience, social life, West Campus, dining, and housing odds. | `documents/warren_v_towers.md` |
| 2 | Deciding between Warren, Fenway, and The Towers | A Reddit post discussing whether freshmen should choose Warren, Fenway, or The Towers, with comments on community, distance from campus, dining, bathrooms, and social life. | `documents/warren_towers_fenway.md` |
| 3 | BU Dorms: Warren vs. West and Other First-Year Options | A Reddit post from an incoming CAS student asking about Warren and West, with comments comparing room quality, location, common spaces, dining access, and East Campus alternatives. | `documents/bu_dorms.md` |
| 4 | Best and Worst Residences/Dorms at BU | A Reddit post asking where freshmen usually stay and which dorms are best or worst, with comments on Warren, West, Towers, Bay State brownstones, Danielsen, and freshman social life. | `documents/bestworst_dorms.md` |
| 5 | Choosing Housing: Warren vs. West for Questrom | A Reddit post from an incoming Questrom student deciding between Warren and West, with comments on Warren renovations, construction noise, social life, gym access, and class proximity. | `documents/choosing_housing.md` |
| 6 | StuVi Honest Review: Pros, Cons, and Value | A Reddit post asking whether Student Village is worth the price, with comments on AC, bathrooms, room quality, noise, appliances, storage, gym proximity, and cost tradeoffs. | `documents/stuvi_honestreview.md` |
| 7 | BU Housing Advice for Incoming Students | A Reddit post from a prospective student researching housing, with comments explaining realistic freshman options, private bathrooms, AC, brownstones, 610 Beacon, apartments, Kilachand, HoJo, Riverway, and Fenway. | `documents/housing_advice.md` |
| 8 | Best Freshman Dorms at BU | A Reddit post from an incoming CAS student asking which freshman dorms are best, with comments on making friends, bugs, Fenway, Warren, West, Towers, Bay State, and freshman placement odds. | `documents/best_freshman_dorms.md` |
| 9 | Housing Ranking: Modern Two-Person Suite Near CAS | A Reddit post asking about a modern two-person suite near CAS, with comments ranking realistic freshman options such as Warren, West, Fenway, HoJo, Towers, brownstones, and Kilachand. | `documents/housing_ranking.md` |
| 10 | HoJo for Socializing as a Freshman | A Reddit post asking whether HoJo is good for socializing, with comments comparing HoJo, Warren, and West for freshman community, private bathrooms, location, dining, and meeting people. | `documents/hojo_1.md` |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**
500 characters

**Overlap:**
100 characters

**Why these choices fit your documents:**
These numbers should enable us to capture entire comments as well as some relevant replies, or relevant chunks of the post content itself.


**Final chunk count:**
131
---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**
The all-MiniLM-L6-v2 model will be used via sentence-transformers.


**Production tradeoff reflection:**
If cost wasn't a concern, a more complex embedding model would probably be able to handle larger context lengths better, enabling more accurate responses. Since this domain is fairly specific, a more powerful embedding model might also be more accurate in retrieving relevant info and context from the chunks.
---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
In query.py, the LLM is instructed to only answer questions relevant to the sources. The way this is determined is that, if the top k chunks retrieved from the database all have very low similarity scores, then we know that the prompt by the user is quite relevant to the domain. In that case, the LLM will simply output a generic response that it cannot answer the question that it was given. 

**How source attribution is surfaced in the response:**
Source attribution in the UI is included in the form of a table below the response. Firstly, the UI will show which sources are cited, and the table will show what these sources are, as well as other useful metrics like the distance. 
---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which freshman dorm is the most convenient in BU? | Warren is usually described as the most convenient freshman dorm because it is central, close to many classes, and has a dining hall in the building. For Questrom students, The Towers may also be very convenient because it is right next to QST. | Based on the provided source chunks, Warren Towers appears to be a convenient freshman dorm due to its social environment, proximity to Central Campus locations, and having its own dining hall. However, other sources suggest that CCSR and Riverway may be better living spaces, despite being farther from campus. | Relevant | Accurate |
| 2 | Which freshman dorm has the best social life in BU? | Warren is usually described as the best freshman dorm for social life because many freshmen live there and it is easy to meet people. West is also mentioned as social, but Warren comes up most often for making friends. | Warren dorm is often considered to have a good social environment for freshmen due to its large size and proximity to Central Campus locations. However, other sources suggest that West or Bay State may have a better social life, with West being considered one of the top dorms in terms of socialization. It's worth noting that opinions on the best dorm for social life vary. | Relevant | Accurate |
| 3 | Which freshman dorm is the most suitable for introverts in BU? | Warren is probably best for an introvert who wants to meet people because there are many freshmen, common rooms, and a dining hall in the building. HoJo has better bathrooms but seems less social and more isolating. | Based on the source chunks, Warren Towers seems to be a better option for you as an introvert who wants to socialize. Multiple comments suggest that Warren is great for making friends and meeting people, with many freshmen in the same situation, and it's closer to CAS and CFA. HoJo, on the other hand, is described as isolating, despite having better facilities. | Relevant | Accurate |
| 4 | Is StuVi worth the extra money to live at? | StuVi can be worth it if the student cares a lot about comfort, AC, singles, better bathrooms, storage, and being close to the gym. It is expensive, so it may not be worth it if cost is a major concern. | Whether StuVi is worth the extra money depends on individual priorities and financial situations. Some students find the amenities, such as air conditioning, singles, and proximity to the gym, to be worth the higher cost. However, others consider it overpriced. | Relevant | Accurate |
| 5 | Is Fenway worth the additional distance from the main campus? | Fenway can be worth it because students mention better rooms, good dining, and private or individual bathrooms in some buildings. The downside is that it is far from main campus and can feel isolated, so it depends on whether the student values comfort more than location. | Whether Fenway is worth the additional distance from the main campus depends on individual preferences. Some students find the separation from the main campus to be isolating, especially during snowy and cold months, and believe it can hinder making friends. However, others appreciate the traditional campus living feel and the quality of the dining hall. It's a trade-off between the benefits of Fenway, such as a potentially nicer living environment, and the drawbacks of the commute. | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
All of the questions returned answers from the source channels that are pretty accurate and relevant, so I would say none of them actually failed. 

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
I would say that planning.md helped a lot. Firstly, it helped me to visualize the architecture of the whole pipeline, so it made sense that I was able to audit the implementations by coding agent effectively, even though I wasn't coding by hand. I was still able to check it. Secondly, just having everything documented comprehensively and well helped a lot for prompting the coding agent to do what I wanted to do effectively. Having all that architecture and structure in there helped prevent hallucinations or any inaccurate implementations that diverge from my vision and specs. 

**One way your implementation diverged from the spec, and why:**
When I asked the coding agent to implement source attribution in the Gradio UI, it didn't really do it in the way I thought it would. Most conventional LLMs would have citations next to the text that they generate. For example, Gemini Search with Google or other things. Initially, that was my vision, but eventually the UI simply returned a list of sources cited alongside the response and then also returned a table of resources and their distance scores from the prompt itself.

I believe this happened because I wasn't specific enough with what I wanted, so it kind of just generated something that still fit the criteria of the prompt that I gave it, but it wasn't exactly what I envisioned. That teaches me that I should be more specific in the future with my prompts and my specification documentation. 
---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
I gave the AI the sections of planning.md that were relevant to my chunking strategy and my retrieval approach. I use these as the basis for implementing chunking, ingestion, retrieval, and vector storage. 
- *What it produced:*
The output produced and the code produced by the AI was fairly accurate. It worked as intended, and structurally it made sense in terms of fitting in with the vision I had for the whole project. 
- *What I changed or overrode:*
I actually don't have to change anything. I was quite happy with how it turned out. 

**Instance 2**

- *What I gave the AI:*
For ingesting the documents and the sources, I actually use Manus.ai to write a script for me to effectively automate the scripting of Reddit posts and comments to provide a more consistent and usable format of source in Markdown files. I basically told it what I wanted out of the Reddit post: I wanted the posts and comments' content only and nothing else. I will use this for chunking. Also, I gave it all the links to the Reddit posts that I wanted to get.
- *What it produced:*
DAI generated for me, or rather, using the script that it made, it helped me generate a clean format for the original source, which is Reddit posts and comments. DAI was able to use the script to generate clean markdown files that contain only the contents of the posts and the comments that were then used for chunking and the rest of the RAG pipeline. 
- *What I changed or overrode:*
Initially, I wasn't specific enough. The knockdown output included things like headers or title of the post or the comment, or other metadata such as the username of the poster or the commenter. I had to iterate by specifying further that I only wanted posts and comment content and then no other metadata or other information from these Reddit posts. After that change, I got what I wanted. 