# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
Domain: on-campus housing experiences at Boston University. This knowledge is valuable for students who want to make more informed decisions when applying for and choosing their on-campus housing for future semesters. While plenty of objective information exists in official channels, reviews and experiences are more subjective, informal and sentiment-based. Official channels also won't be informative about negative aspects of each campus housing, and tend to be overly positive. Including informal student reviews is a way to obtain balanced feedback.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Reddit post/source | Short description | Markdown file path |
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

**Chunk size:**
500 characters

**Overlap:**
100 characters

**Reasoning:**
These numbers should enable us to capture entire comments as well as some relevant replies, or relevant chunks of the post content itself.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
The all-MiniLM-L6-v2 model will be used via sentence-transformers.

**Top-k:**
Top 5 related chunks will be retrieved.

**Production tradeoff reflection:**
If cost wasn't a concern, a more complex embedding model would probably be able to handle larger context lengths better, enabling more accurate responses. Since this domain is fairly specific, a more powerful embedding model might also be more accurate in retrieving relevant info and context from the chunks.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Which freshman dorm is the most convenient in BU? | Warren is usually described as the most convenient freshman dorm because it is central, close to many classes, and has a dining hall in the building. For Questrom students, The Towers may also be very convenient because it is right next to QST. |
| 2 | Which freshman dorm has the best social life in BU? | Warren is usually described as the best freshman dorm for social life because many freshmen live there and it is easy to meet people. West is also mentioned as social, but Warren comes up most often for making friends. |
| 3 | Which freshman dorm is the most suitable for introverts in BU? | Warren is probably best for an introvert who wants to meet people because there are many freshmen, common rooms, and a dining hall in the building. HoJo has better bathrooms but seems less social and more isolating. |
| 4 | Is StuVi worth the extra money to live at? | StuVi can be worth it if the student cares a lot about comfort, AC, singles, better bathrooms, storage, and being close to the gym. It is expensive, so it may not be worth it if cost is a major concern. |
| 5 | Is Fenway worth the additional distance from the main campus? | Fenway can be worth it because students mention better rooms, good dining, and private or individual bathrooms in some buildings. The downside is that it is far from main campus and can feel isolated, so it depends on whether the student values comfort more than location. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. The length of posts and comments may be inconsistent, so a fixed chunking might not work as effectively for all posts or sources.

2. Some portions of posts or comments, or some comments in a post, could be irrelevant due to various reasons (trolls, bots, etc.) and hence chunks containing these would be quite irrelevant and useless.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->
```text
        sources                       chunking                    embedding                     
  ┌─────────────────┐            ┌─────────────────┐          ┌─────────────────┐               
  │                 │            │                 │          │                 │               
  │                 │            │                 │          │all-MiniLM-L6-v2 │               
  │ documents/**.md ├───────────►│    ingest.py    ├─────────►│    model in     │               
  │                 │            │                 │          │    ingest.py    │               
  │                 │            │                 │          │                 │               
  └─────────────────┘            └─────────────────┘          └───────┬─────────┘               
                                                              │                         
                                                                      │                         
                                                                      │                         
                                                                      │                         
                                                                      │                         
       embedding                    user question                     │                         
   ┌─────────────────┐          ┌──────────────────┐          ┌───────▼────────┐                
   │                 │          │                  │          │                │                
   │all-MiniLM-L6-v2 │          │                  │          │ vectors stored │                
   │    model in     ◄──────────┼     query.py     │◄─────────┼                │                
   │    query.py     │          │                  │          │ in ChromaDB    │                
   │                 │          │                  │          │                │                
   └───────┬─────────┘          └──────────────────┘          └────────────────┘                
           │                                                                                    
           │                                                                                    
           │                                                                                    
           │                                                                                    
           │                                                                                    
           ▼                                                                                    
┌──────────────────────────┐                                                                    
│                          │                                                                    
│                          │            ┌──────────────────┐                                    
│   retreive chunks in     │            │                  │                ┌──────────────────┐
│   ChromaDB that have     │            │ LLM generation   │                │ output of final  |
│   greatest similarity    ┼───────────►│ of answer using  ┼───────────────►│  answer with     |
│   to the embedded        │            │ retrieved context│                │   sources        │
│   question vector as     │            │                  │                └──────────────────┘
│   context                │            └──────────────────┘                                    
│                          │                                                                    
└──────────────────────────┘                                                                    
```


---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

I intend to use Codex (powered by ChatGPT) to implement this pipeline. planning.md will be fed as context, in particular the implementation diagram. I will also manually input and clarify in my prompt the overall architecture I expect of the pipeline, such as what files will contain what methods or code blocks. I will implement each stage separately to prevent overwhelm of having to debug AI-generated code. I will probably start with the ingestion and chunking code, then to embedding, storage and retrieval, then to generation and user interfacing. At each stage I expect Codex to produce code that is organized and commented in the way I want it to be. I will verify manually by reading through the generated code, understanding what it does and verifying the overall architecture fits my vision. I will do this for each separate portion as well as for the whole pipeline to ensure everything integrates well with each other.

**Milestone 3 — Ingestion and chunking:**
Note on the script: I had actually written one and scraped my Reddit post sources using the free tier of Manus AI. It proved to be quite an effective way to automate the process of getting all the relevant info (post content, comments, etc.) without having to manually copy the stuff I wanted. Apologies if this is not allowed under the course syllabus.

The script is available in the file scrape.py. All the sources in the documents/ subdirectory are already loaded, cleaned and processed by this script, and hence need no further processing before ingestion and chunking.

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
