![Screenshot from 2024-01-13 10-45-09](https://github.com/SpaceFozzy/dRAGula/assets/10606414/5c456bcf-f718-4fcf-bc3b-75b144305717)

## Overview
Current LLMs can output a vast breadth of information regarding books or famous literary works, but don't store the verbatum texts needed to make accurate, specific references supporting their responses. This project explores the possibility of using semantic search to provide the LLM with the most relevant quotations to support its response. I've used Bram Stoker's Dracula as the subject because it's in the public domain, relatively modern, and generally good stuff.

[dRAGula interaction exam](https://github.com/SpaceFozzy/dRAGula/assets/10606414/7145fe7b-f8e6-4c81-b339-06f4a53da9c0)

## Running The Project
I've been developing the project using Kubernetes (minikube) and Devspace to make orchestrating the containers easy while staying focusing on k8s resources. You'll need to have Helm and Devspace installed, as well as access to a Kubernetes cluster (or minikube). Then just

`devspace dev`

You'll need to add your `OPENAI_API_KEY` as an env variable inside your dev container, then you can start the chat loop with:

`python dragula.py`

## How It Works
The project comes with a dataset of passages from the novel that are chunked and ingested into the postgres database when you start developing. Each passage also has an associated vector: a numeric representation of the passage capturing the semantic meaning in a way that similar passages have similar numeric representations. I generated these _embeddings_ using OpenAI's `text-embedding-ada-002` model and included them in the project files as a postgres dump so you don't have to re-generate them every run (which would incur a small cost). The postgres database uses the pgvector extension so it can effectively query for passages using the semantic similarity captured in the vectors. This is how the retrieval system works to find relevant passages, and it is a common pattern in "retrieval augmented generation".

When you provide a prompt about the novel, the following happens:

1. ChatGPT is asked to consider your prompt and generate queries for the vector store to find relevant passages. ChatGPT produces multiple queries to allow for a diversity in the supporting passages.
2. The multiple queries produced by ChatGPT are fed into PGVector to find relevant passages. Results are reduced to a unique set.
3. The relevant passages are passed as context to ChatGPT along with the original question. ChatGPT is prompted to refer to the passages in its response.


## Re-Ingesting The Text

If you want to re-ingest the text to experiment with different chunk sizes and overlap values in pgvector, you can run the following with your desired numbers:

`CHUNK_SIZE=2000 CHUNK_OVERLAP=100 python dragula.py ingest`

Smaller chunks will result in better matching, but less passage context provided to ChatGPT. 
