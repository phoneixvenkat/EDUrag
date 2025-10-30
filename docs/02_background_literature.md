🧠 Section 2 – Background / Literature Review

2.1 Introduction to RAG (Retrieval-Augmented Generation)



Retrieval-Augmented Generation (RAG) is an advanced approach in Natural Language Processing (NLP) that combines information retrieval with text generation to enhance the factual accuracy and contextual depth of AI responses.



Traditional large language models (LLMs) such as GPT or BERT generate answers purely from their pre-trained data, which can lead to outdated or hallucinated information. RAG addresses this limitation by integrating real-time document retrieval from an external knowledge base (e.g., research papers, corporate reports, PDFs).



In RAG, when a user asks a question:



The query is converted into a vector embedding (numerical representation of meaning).



The system retrieves most relevant text chunks from the indexed document database.



The LLM uses these retrieved passages as context to generate a fact-based, contextualized answer.



This hybrid of retrieval and generation ensures accuracy, traceability, and adaptability — critical features for academic and research applications like EduRAG.



2.2 Role of RAG in Education and Research



In the educational and research domains, students and researchers often need to extract key insights from lengthy technical documents or reports. Traditional search methods (keyword-based) are inefficient for understanding complex relationships within data.



EduRAG leverages RAG to create a personalized learning assistant capable of:



Understanding uploaded research documents.



Answering conceptual and analytical questions directly from source materials.



Generating practice quizzes to test comprehension.



This transforms static learning resources into interactive and adaptive knowledge systems.

Such systems support self-learning, assist researchers in literature reviews, and improve accessibility to dense academic materials.



2.3 Supporting Technologies and Frameworks



The EduRAG system integrates several modern AI and software components that support the RAG architecture:



Technology	Purpose / Function

FastAPI	Lightweight, high-performance backend for serving RAG endpoints.

Streamlit	Interactive frontend for users to upload, query, and visualize document responses.

Sentence Transformers (BERT-based)	Used to create semantic embeddings for documents and queries.

ChromaDB	Vector database for efficient retrieval and similarity search.

PyTorch	Deep learning framework for handling embeddings and neural computations.

PyPDF2	Library for extracting text from uploaded PDF files.



Each of these frameworks plays a key role in enabling the seamless flow of data — from document ingestion to contextual answer generation.



2.4 Related Works



Several studies and open-source implementations have inspired the design of EduRAG:



Lewis et al. (2020) introduced RAG models combining retrieval and generation to enhance knowledge grounding in NLP tasks.



Reimers \& Gurevych (2019) developed Sentence-BERT, which revolutionized semantic similarity search by producing high-quality embeddings.



Wolf et al. (2020) created the Transformers library that provides reusable architectures for text generation and embeddings.



ChromaDB (2023) and LangChain (2023) made it easier to build modular retrieval pipelines with persistent memory layers.



EduRAG adapts these ideas into a lightweight, domain-specific RAG framework tailored for academic use — enabling fast retrieval, meaningful answers, and automatic quiz generation from educational materials.



2.5 Literature Gap



Despite the advancements in RAG and educational AI, most existing tools either:



Lack interactive interfaces for non-technical users.



Do not support document-specific reasoning (e.g., querying inside user-provided PDFs).



Ignore learning assessment through dynamic quizzes.



EduRAG bridges this gap by:



Integrating multi-document retrieval and QA into one system.



Generating personalized quizzes to reinforce knowledge retention.



Enabling real-time feedback collection for continuous improvement.



2.6 Summary



In summary, this literature review establishes the foundation for EduRAG as an educational RAG-based system that merges modern NLP frameworks, interactive UI design, and adaptive learning strategies.

The background research demonstrates that the integration of retrieval-based knowledge grounding with generative reasoning is the most effective way to enhance learning and information accessibility in academic environments.



📚 Citations



Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS.



Reimers, N., \& Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. ACL.



Wolf, T. et al. (2020). Transformers: State-of-the-Art Natural Language Processing. EMNLP.



ChromaDB Documentation (2023). https://docs.trychroma.com/



Streamlit Documentation (2023). https://streamlit.io/



FastAPI Documentation (2023). https://fastapi.tiangolo.com/

