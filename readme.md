# Hello, NYC!

This repository contains the files for Team 2's Programming Generative AI course application. The application uses OpenAI, langchain, and FAISS to create a basic RAG chatbot designed to help you navigate the process of starting a new business in New York City. 

## Getting Started
- Install the necessary libraries from `requirements.txt`
- Put your OpenAI API key into the app.py and rag.py files
- `python3 app.py` will launch the application on port 5000

## About the data
The project includes embeddings for the data that was used to generate the contextualized information for the application. The data store for the RAG functionality is compiled of 70 PDF files about entrepreneurship and New York City business resources. 