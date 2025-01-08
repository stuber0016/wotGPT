import unittest
from unittest.mock import patch, MagicMock
import os
import shutil
import sys

from dotenv import load_dotenv

load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
current_dir = current_dir[:-5]
sys.path.insert(0, current_dir)

from semestral.rag_create import create_chroma_db, ApiKeyError, load_documents, split_documents
from semestral.rag_read import read_rag_context, FOUND_CONTEXT, OTHER_ERROR
from semestral.model import Model
from unittest.mock import AsyncMock, MagicMock, call
from semestral.discord_bot import split_send, MAX_MESSAGE_LENGTH


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
            "Tell me positions for Cliff map"
        ]

        for query in queries:
            # Call the function to test
            result, context = read_rag_context(query)

            # Check that the function returns FOUND_CONTEXT
            self.assertEqual(FOUND_CONTEXT, result)
            # Optionally, check that the context is not empty
            self.assertTrue(len(context) > 0)

    @patch('semestral.rag_read.HuggingFaceEndpointEmbeddings')
    @patch('semestral.rag_read.Chroma')
    @patch.dict(os.environ, {}, clear=True)
    def test_invalid_api_key(self, mock_chroma, mock_embeddings):
        # Se tup the mock to simulate an invalid API key response
        mock_embeddings.side_effect = Exception("Invalid API Key")

        # Define a query
        query = "What is the capital of France?"

        # Call the function and assert that it returns OTHER_ERROR
        result, message = read_rag_context(query)
        self.assertEqual(result, OTHER_ERROR)
        self.assertIn("RAG context database error", message)


class TestModel(unittest.TestCase):

    def setUp(self):
        """Set up the test environment."""
        self.model = Model()

    @patch('semestral.model.requests.get')
    def test_get_player_id_found(self, mock_get):
        """Test get_player_id when player is found."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "ok",
            "data": [{"nickname": "player1", "account_id": "12345"}]
        }
        mock_get.return_value = mock_response

        player_id = self.model.get_player_id("player1")
        self.assertEqual(player_id, "12345")

    @patch('semestral.model.requests.get')
    def test_get_player_id_not_found(self, mock_get):
        """Test get_player_id when player is not found."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "ok",
            "data": []
        }
        mock_get.return_value = mock_response

        player_id = self.model.get_player_id("unknown_player")
        self.assertIsNone(player_id)

    @patch('semestral.model.requests.get')
    def test_get_player_data(self, mock_get):
        """Test get_player_data."""
        mock_response = MagicMock()
        mock_response.text = "player_data"
        mock_get.return_value = mock_response

        player_data = self.model.get_player_data("12345")
        self.assertEqual(player_data, "player_data")

    @patch('semestral.model.Model.invoke')
    def test_query(self, mock_invoke):
        """Test query function."""
        mock_invoke.return_value = (True, MagicMock(content="response"))
        response = self.model.query("How to improve my game?", "user1")
        self.assertEqual(response, "response")

    @patch('semestral.model.Model.invoke')
    @patch('semestral.model.Model.get_player_id')
    @patch('semestral.model.Model.get_player_data')
    def test_player_query(self, mock_get_player_data, mock_get_player_id, mock_invoke):
        """Test player_query function."""
        mock_get_player_id.return_value = "12345"
        mock_get_player_data.return_value = "player_data"
        mock_invoke.return_value = (True, MagicMock(content="analysis"))

        response = self.model.player_query("player1", "user1")
        self.assertEqual(response, "analysis")


class TestDiscordBot(unittest.IsolatedAsyncioTestCase):

    async def test_split_send_short_message(self):
        """Test split_send with a message shorter than MAX_MESSAGE_LENGTH."""
        short_message = "This is a short message."
        interaction = AsyncMock()

        await split_send(short_message, interaction)

        # Check that the message is sent without splitting
        interaction.followup.send.assert_called_once_with(short_message, ephemeral=True)

    async def test_split_send_long_message(self):
        """Test split_send with a message longer than MAX_MESSAGE_LENGTH."""
        long_message = "A" * (MAX_MESSAGE_LENGTH + 10)  # Create a message slightly longer than MAX_MESSAGE_LENGTH
        interaction = AsyncMock()

        await split_send(long_message, interaction)

        # Check that the message is split and sent in parts
        expected_calls = [
            call(long_message[:MAX_MESSAGE_LENGTH], ephemeral=True),
            call(long_message[MAX_MESSAGE_LENGTH:], ephemeral=True)
        ]
        actual_calls = interaction.followup.send.call_args_list
        self.assertEqual(actual_calls, expected_calls)

    async def test_split_send_with_file_and_embed(self):
        """Test split_send with a file and embed."""
        message = "This is a message with a file and embed."
        interaction = AsyncMock()
        file = MagicMock()
        embed = MagicMock()

        await split_send(message, interaction, file=file, embed=embed)

        # Check that the file and embed are sent first
        interaction.followup.send.assert_any_call(file=file, embed=embed, ephemeral=True)

        # Check that the message is sent after the file and embed
        interaction.followup.send.assert_any_call(message, ephemeral=True)


if __name__ == '__main__':
    unittest.main()
