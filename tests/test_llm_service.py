from unittest.mock import Mock

from app.llm_service import create_client, generate_response


def test_create_client():
    client = create_client("test-api-key")

    assert client is not None


def test_generate_response():
    mock_client = Mock()

    mock_response = Mock()
    mock_response.output_text = (
        "RAG stands for Retrieval-Augmented Generation."
    )

    mock_response.usage.input_tokens = 10
    mock_response.usage.output_tokens = 8
    mock_response.usage.total_tokens = 18

    mock_client.responses.create.return_value = mock_response

    result = generate_response(
        mock_client,
        "What is RAG?",
        "test-request-123",
    )

    assert result == (
        "RAG stands for Retrieval-Augmented Generation."
    )

    mock_client.responses.create.assert_called_once_with(
        model="gpt-5-mini",
        input="What is RAG?",
    )
