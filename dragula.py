import os
import sys

from langchain.chains import LLMChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.globals import set_debug
from langchain.prompts import ChatPromptTemplate
from langchain.retrievers.multi_query import (
    MultiQueryRetriever,
    LineListOutputParser,
)
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.pgvector import PGVector
from langchain.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from templates import passage_query_template, response_query_template

set_debug(os.environ.get("DEBUG", "").lower() == "true")


class Dragula:
    """
    Class representing the core functionality of the Dragula application.

    This class encapsulates methods for ingesting data, processing queries, and
    handling user interaction through a chat interface.
    """

    def __init__(self):
        """
        Initialize the Dragula application.

        Set the vector store details on this class isntance to be used later
        by langchain.
        """
        if not os.environ.get("OPENAI_API_KEY"):
            raise EnvironmentError(
                "OPENAI_API_KEY environment variable not set."
            )

        connection_string = PGVector.connection_string_from_db_params(
            driver=os.environ.get("PGVECTOR_DRIVER", "psycopg2"),
            host=os.environ.get("PGVECTOR_HOST", "pgvector"),
            port=int(os.environ.get("PGVECTOR_PORT_NUMBER", "5432")),
            database=os.environ.get("PGVECTOR_DATABASE", "postgres"),
            user=os.environ.get("PGVECTOR_USER", "postgres"),
            password=os.environ.get("PGVECTOR_PASSWORD", "password"),
        )
        self.vector_store = PGVector.from_existing_index(
            connection_string=connection_string,
            embedding=OpenAIEmbeddings(),
            collection_name="dracula_passages",
        )

    def chat(self):
        """
        Chat method to interact with the user in a loop.

        This method continuously takes user input and provides responses
        until the program is exited. It serves as the main interface for user
        interaction.
        """
        try:
            while True:
                user_input = input("Enter your question: ")
                output_stream = self._query(user_input)

                for chunk in output_stream:
                    print(chunk, end="", flush=True)

                print("\n")
        # Handle KeyboardInterrupt (e.g., Ctrl+C) to exit the chat loop
        except KeyboardInterrupt:
            print("\n")
            print("Farewell.")

    def _query(self, user_input):
        """
        Query method to process user input and retrieve relevant information.

        This method takes a user input string, processes it to find relevant
        text excerpts using vector space search, and then forms a response
        based on the findings.
        """
        passage_vector_store = self.vector_store.as_retriever(
            # Return the top three similar results per query
            search_kwargs={"k": 3}
        )
        passage_query_prompt = ChatPromptTemplate.from_template(
            passage_query_template
        )

        # Outputs a list of different phrases used to query the vector store
        passage_query_chain = LLMChain(
            llm=ChatOpenAI(),
            prompt=passage_query_prompt,
            output_parser=LineListOutputParser(),
        )

        # Returns a unique list of passages given a list of query phrases
        passage_retriever = MultiQueryRetriever(
            retriever=passage_vector_store,
            llm_chain=passage_query_chain,
        )

        # Use the provided passages as context to respond to the user's input
        response_query_prompt = ChatPromptTemplate.from_template(
            response_query_template
        )
        response_query_chain = (
            {"context": passage_retriever, "question": RunnablePassthrough()}
            | response_query_prompt
            | ChatOpenAI(model_name="gpt-4")
            | StrOutputParser()
        )

        return response_query_chain.stream(user_input)

    def ingest(
        self,
        file_path="./data/dracula.txt",
        chunk_size=1500,
        chunk_overlap=200,
    ):
        """
        Load, split, and store text from a file.

        Args:
            file_path: Where to find the text file.
            chunk_size: How big each text piece should be.
            chunk_overlap: How much overlap between text pieces.
        """
        self.vector_store.delete_collection()

        self.vector_store.create_collection()
        with open(file_path, "r") as file:
            text = file.read()
            text_splitter = CharacterTextSplitter(
                chunk_size=int(os.environ.get("CHUNK_SIZE", chunk_size)),
                chunk_overlap=int(
                    os.environ.get("CHUNK_OVERLAP", chunk_overlap)
                ),
            )
            texts = text_splitter.split_text(text)
            self.vector_store.add_texts(texts=texts)


"""
This conditional statement checks if the script is being run directly (not
imported as a module).

If it is run directly, it creates an instance of the Dragula class and starts
the chat interface. Alternatively, it can re-ingest the story based on the
command line argument provided.
"""
if __name__ == "__main__":
    dragula_instance = Dragula()
    if "ingest" in sys.argv:
        dragula_instance.ingest()
    else:
        dragula_instance.chat()
