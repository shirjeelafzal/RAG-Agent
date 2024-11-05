Here's an updated version of the README file that reflects the changes made to your `Basic-RAG` project and the introduction of the `agent.py` file. The new README includes a description of the conversation feature and the use of the `create_react_agent` functionality.

---

# Basic-RAG

This project, "Basic-RAG" (Retrieval-Augmented Generation), is a Python-based implementation that uses LangChain to build a simple Retrieval-Augmented Generation pipeline. The pipeline utilizes a language model to answer questions by retrieving relevant documents from a knowledge source (in this case, a web article) and augmenting responses with contextual information.

## Project Structure

- **app.py**: Main script that sets up the RAG pipeline and runs it with a sample question. It includes conversation features that maintain chat history for better context in responses.
- **agent.py**: An alternative script that utilizes a React agent to handle conversation and retrieval tasks interactively.
- **requirements.txt**: Lists all required Python packages.
- **sample.env**: Example environment variables needed for the project, which you can rename to `.env` after configuring.

## Prerequisites

1. **Python**: Make sure you have Python 3.8 or later installed.
2. **Virtual Environment**: Set up a virtual environment (optional but recommended).
3. **API Key**: You'll need an API key for Groq language models (GROQ_API_KEY), which should be added to a `.env` file based on `sample.env`.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/shirjeelafzal/Basic-Rag.git
   cd Basic-RAG
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**:
   - Copy `sample.env` to `.env` and configure your API key.

5. **Set the User Agent Variable**:
   - Set the `USER_AGENT` environment variable to allow `WebBaseLoader` to access web content. Here are examples for setting it on different systems and browsers:

   ### Linux / macOS (Chrome User Agent)
   ```bash
   export USER_AGENT="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
   ```

   ### Windows (Chrome User Agent)
   ```powershell
   $Env:USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
   ```

   ### macOS (Safari User Agent)
   ```bash
   export USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
   ```

## Running the Project

### Using `app.py`

Run the project using the following command:

```bash
python app.py
```

This will initiate a conversation where you can ask questions, and the system will respond using the context retrieved from the specified web source.

### Using `agent.py`

Alternatively, you can run the agent script, which also allows for interactive questioning:

```bash
python agent.py
```

This script uses a React agent to stream responses to your queries in real-time.

## Code Walkthrough

- **Document Loading**: Loads a web document using `WebBaseLoader`.
- **Document Splitting**: Splits the document into manageable chunks.
- **Vector Store Setup**: Embeds the document chunks using `SentenceTransformer` and stores them in a `Chroma` vector store.
- **Retriever Setup**: Uses the vector store to retrieve relevant document chunks based on a similarity search.
- **Pipeline Configuration**: Sets up a LangChain pipeline using a retrieval-augmented generation approach.
- **Pipeline Execution**: Invokes the pipeline with a sample question and outputs the response.
- **Conversation Feature**: Both scripts maintain chat history, allowing the AI to provide context-aware answers based on previous interactions.

## Cleanup

The script deletes the vector store collection at the end to free up resources.

