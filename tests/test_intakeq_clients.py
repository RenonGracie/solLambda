from unittest.mock import Mock, patch

import pytest

from src.utils.intakeq.clients import search_client


@pytest.fixture
def mock_search_clients():
    with patch("src.utils.intakeq.clients.search_clients") as mock:
        yield mock


def test_search_client_by_email_success(mock_search_clients):
    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"Email": "test@example.com", "Name": "John Doe", "PractitionerId": "123"}
    ]
    mock_search_clients.return_value = mock_response

    # Test the function
    result = search_client("test@example.com", "John Doe")

    # Verify the result
    assert result is not None
    assert result["Email"] == "test@example.com"
    assert result["Name"] == "John Doe"

    # Verify mock was called correctly
    mock_search_clients.assert_called_once_with(
        {"search": "test@example.com", "includeProfile": True}
    )


def test_search_client_by_name_success(mock_search_clients):
    # Setup mock response for email search (not found)
    mock_response_email = Mock()
    mock_response_email.status_code = 200
    mock_response_email.json.return_value = []

    # Setup mock response for name search (found)
    mock_response_name = Mock()
    mock_response_name.status_code = 200
    mock_response_name.json.return_value = [
        {"Email": "test@example.com", "Name": "John Doe", "PractitionerId": "123"}
    ]

    # Configure mock to return different responses
    mock_search_clients.side_effect = [mock_response_email, mock_response_name]

    # Test the function
    result = search_client("test@example.com", "John Doe")

    # Verify the result
    assert result is not None
    assert result["Email"] == "test@example.com"
    assert result["Name"] == "John Doe"

    # Verify mock was called twice
    assert mock_search_clients.call_count == 2
    mock_search_clients.assert_any_call(
        {"search": "test@example.com", "includeProfile": True}
    )
    mock_search_clients.assert_any_call({"search": "John Doe", "includeProfile": True})


def test_search_client_not_found(mock_search_clients):
    # Setup mock response for both searches
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    mock_search_clients.return_value = mock_response

    # Test the function
    result = search_client("nonexistent@example.com", "Nonexistent User")

    # Verify the result
    assert result is None

    # Verify mock was called twice
    assert mock_search_clients.call_count == 2


def test_search_client_api_error(mock_search_clients):
    # Setup mock response with error
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"error": "Internal Server Error"}
    mock_search_clients.return_value = mock_response

    # Test the function
    result = search_client("test@example.com", "John Doe")

    # Verify the result
    assert result is None

    # Verify mock was called twice (once for email search, once for name search)
    assert mock_search_clients.call_count == 2
    mock_search_clients.assert_any_call(
        {"search": "test@example.com", "includeProfile": True}
    )
    mock_search_clients.assert_any_call({"search": "John Doe", "includeProfile": True})


def test_search_client_case_insensitive(mock_search_clients):
    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"Email": "TEST@example.com", "Name": "JOHN DOE", "PractitionerId": "123"}
    ]
    mock_search_clients.return_value = mock_response

    # Test the function with lowercase input
    result = search_client("test@example.com", "john doe")

    # Verify the result
    assert result is not None
    assert result["Email"] == "TEST@example.com"
    assert result["Name"] == "JOHN DOE"
