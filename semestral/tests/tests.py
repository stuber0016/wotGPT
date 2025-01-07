import unittest
from unittest.mock import patch, MagicMock
import os
import shutil
import sys

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, r"D:/cvut/bi-pyt/semestral/")

from semestral.rag_create import create_rag_context, create_chroma_db, ApiKeyError, load_documents, split_documents
from semestral.rag_read import read_rag_context, FOUND_CONTEXT, NO_CONTEXT


class TestRagCreate(unittest.TestCase):
    @patch('rag_create.os.environ', {})
    def test_create_chroma_db_invalid_api_key(self):
        # Ensure the HFACE_API_KEY environment variable is not set
        with self.assertRaises(ApiKeyError):
            create_chroma_db(['chunk1', 'chunk2'])

    @patch('rag_create.DirectoryLoader.load')
    def test_load_documents(self, mock_load):
        # Mock the return value of the load method
        mock_load.return_value = ['doc1', 'doc2']

        # Call the function to test
        documents = load_documents()

        # Check that the load method was called once
        mock_load.assert_called_once()

        # Check that the documents were loaded correctly
        self.assertEqual(documents, ['doc1', 'doc2'])

    @patch('rag_create.RecursiveCharacterTextSplitter.split_documents')
    @patch('builtins.print')  # Suppress print statements
    def test_split_documents(self, mock_print, mock_split_documents):
        # Mock input documents
        documents = ['doc1', 'doc2']

        # Mock the return value of split_documents
        mock_split_documents.return_value = ['chunk1', 'chunk2', 'chunk3']

        # Call the function to test
        chunks = split_documents(documents)

        # Check that the split_documents method was called once
        mock_split_documents.assert_called_once_with(documents)

        # Check that the chunks were returned correctly
        self.assertEqual(chunks, ['chunk1', 'chunk2', 'chunk3'])


class TestRagRead(unittest.TestCase):

    def test_read_rag_context_found(self):
        # Define a query that should be found in the RAG context
        queries = [
            "Which tech tree to choose?",
            "How can I strategically use boosters for grinding?",
            "Tell me positions for Cliff map",
            "What is the best equipment for the T-100 LT?"
        ]

        for query in queries:
            # Call the function to test
            result, context = read_rag_context(query)

            # Check that the function returns FOUND_CONTEXT
            self.assertEqual(result, FOUND_CONTEXT)
            # Optionally, check that the context is not empty
            self.assertTrue(len(context) > 0)


if __name__ == '__main__':
    unittest.main()
