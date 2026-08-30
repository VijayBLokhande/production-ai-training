from unittest.mock import Mock

from app.llm_service import create_client, generate_response

def test_create_client():
    client = create_client("test-api-key")

    assert client is not None


def test_generate_response():
    mock_client = Mock()

    mock_response = Mock()
    mock_response.output_text = "RAG stands for Retrieval-Augmented Generation."

    mock_client.responses.create.return_value = mock_response

    result = generate_response(mock_client, "What is RAG?")

    assert result == "RAG stands for Retrieval-Augmented Generation."

    mock_client.responses.create.assert_called_once_with(
        model="gpt-5-mini",
        input="What is RAG?",
    )
    