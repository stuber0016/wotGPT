import pytest
from dotenv import load_dotenv
import os
import requests
from langchain_groq import ChatGroq
from unittest.mock import patch, MagicMock
import sys

# Load environment variables for testing
sys.path.insert(0, r"D:/cvut/bi-pyt/semestral/")
from semestral.model import Model, ApiKeyError

load_dotenv()  # Assuming a separate test env file


def test_model_init():
    model = Model()
    assert isinstance(model.llm, ChatGroq)
    assert model.user_context == {}
    assert model.players_id == {}
    assert model.players_data == {}


def test_model_init_api_key_error():
    with patch.dict('os.environ', {'GROQ_API_KEY': ''}):
        with pytest.raises(ApiKeyError):
            Model()


def test_get_player_id_found(mocker):
    model = Model()
    player_nickname = "TestPlayer"
    player_id = 12345
    mocker.patch('requests.get', return_value=MagicMock(
        json=lambda: {"data": [{"nickname": player_nickname, "account_id": player_id}]}))
    assert model.get_player_id(player_nickname) == player_id
    assert model.players_id[player_nickname] == player_id


def test_get_player_id_not_found(mocker):
    model = Model()
    player_nickname = "UnknownPlayer"
    mocker.patch('requests.get', return_value=MagicMock(json=lambda: {"data": []}))
    assert model.get_player_id(player_nickname) is None
    assert player_nickname not in model.players_id


def test_get_player_data(mocker):
    model = Model()
    player_id = 12345
    player_data = "Test Player Data"
    mocker.patch('requests.get', return_value=MagicMock(text=player_data))
    assert model.get_player_data(player_id) == player_data
    assert model.players_data[player_id] == player_data


def test_query(mocker):
    model = Model()
    user = "TestUser"
    query = "What is World of Tanks?"
    response_content = "A game about tanks."
    mocker.patch.object(model.llm, 'invoke', return_value=MagicMock(content=response_content))
    with patch('model.read_rag_context', return_value=query):
        assert model.query(query, user) == response_content
        assert len(model.user_context[user]) == 3  # System Message, Human Message, AI Message


def test_player_query_player_found(mocker):
    model = Model()
    player_nickname = "TestPlayer"
    player_id = 12345
    player_data = "Test Player Data"
    query_response = "Analysis and tips."
    user = "TestUser"

    mocker.patch.object(model, 'get_player_id', return_value=player_id)
    mocker.patch.object(model, 'get_player_data', return_value=player_data)
    mocker.patch.object(model.llm, 'invoke', return_value=MagicMock(content=query_response))
    with patch('model.read_rag_context', side_effect=[query_response, query_response + player_data]):
        assert model.player_query(player_nickname, user) == query_response
        assert len(model.user_context[user]) == 3  # System Message, Human Message, AI Message


def test_player_query_player_not_found(mocker):
    model = Model()
    player_nickname = "UnknownPlayer"
    user = "TestUser"

    mocker.patch.object(model, 'get_player_id', return_value=None)
    assert model.player_query(player_nickname, user) == "Player not found"
