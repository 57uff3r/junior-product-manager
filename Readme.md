# AI junior product manager

When working on tech projects, we often spend significant time on tedious tasks, such as:

* Answering questions about the project
* Reminding team members about previous decisions and their rationale
* Clarifying and explaining the project's logic

To address this inefficiency, I decided to adopt a different approach. Now, whenever our team collaborates
on a task, we document all decisions thoroughly, including the reasoning behind them. Even decisions
made by AI systems are meticulously captured and stored in Notion. All product-related documentation
is centralized within dedicated Notion pages and subpages.

Additionally, we maintain plain text files for specific aspects of product management,
such as OpenAPI specifications and YAML examples for product configurations.

We then process this extensive documentation using Large Language Models (LLMs).
As a result, we effectively created a "junior AI product manager" that can:

* Provide detailed explanations about the project
* Write technical tasks
* Clarify information for developers and engineers

The more information we input into the system, the more effective it becomes. 
This AI-driven approach has significantly improved our team's productivity and efficiency,
allowing us to manage five times more tasks daily and save costs.

I could have used NotionAI instead, but building own thing is always fun.

## How to use

In order to use this thing, you have to be able to execute basic terminal commands, have Python and poetry 
package manager installed on your machine. 

You also will need to have Notion and Open API keys.

1. Clone the repository
2. Install dependencies with `poetry install`.
3. Make a copy of `.env.example` file and name it `.env`. Fill in all the necessary fields. The names of env
variables are self-explanatory. `LOCAL_FILES_DIR` and `DOCUMENT_STORE` require full paths to the directories.
3. Run data collection script with `make ingest` command. It will collect all data from Notion and your local files 
and make it accessible for the AI model. You have to run this command every time you want to have your data updated.
4. Then run AI chat interface with `make chat` command. It will start the chat interface in your browser.

When you ask a question, the system finds the most relevant chunks from your knowledge base.
The LLM (GPT-4o) generates an answer based on the retrieved information.
The conversation history is maintained for context.

## Under the hood

AI junior product manager relies on the following technologies:

* **chromadb** - a database for storing and retrieving information from data sources. It supports Embeddings, vector search 
which is crucial for all LLM based systems.
* **langchain** - a state-of-the-art toolkit for build LLM-based applications.
* **streamlit** - a Python library for building interactive web applications.

## Support and maintenance

I made this project entirely for my own needs. It comes as it is, with no warranty. But I am planning to work on it
whenever I have needs in additiolnal functionality. If you have any ideas or want to contribute, 
feel free to open an issue or reach out to me directly.

* [Linkedin](https://www.linkedin.com/in/a-korchak/)
* [me@akorchak.software](mailto:me@akorchak.software)

### Plans

However, I have some plans for the future. It is already clean that the system can be improved in many ways:

* Async support for data collection. The first implementatin of data scrappers was quick and dirty. It can be improved.
* The process of choosing the most relevant chunk of text can be improved. The current implementation is very basic.
* Basic commands supports, such as autocreation of new documents and product specs will be very useful.




