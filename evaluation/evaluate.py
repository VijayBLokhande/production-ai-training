import json
import time
from pathlib import Path

from app.config import load_config
from app.llm_service import create_client, generate_response


def load_evaluation_dataset():
    """Load evaluation questions from the JSON dataset."""

    dataset_path = Path(__file__).parent / "eval_dataset.json"

    with open(dataset_path, "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_response(client, question, expected_answer):
    """Generate an answer and calculate basic evaluation metrics."""

    start_time = time.perf_counter()

    actual_answer = generate_response(client, question)

    end_time = time.perf_counter()

    latency = end_time - start_time

    expected_words = set(expected_answer.lower().split())
    actual_words = set(actual_answer.lower().split())

    if expected_words:
        overlap = len(expected_words.intersection(actual_words))
        relevance_score = overlap / len(expected_words)
    else:
        relevance_score = 0.0

    return {
        "question": question,
        "expected_answer": expected_answer,
        "actual_answer": actual_answer,
        "latency_seconds": round(latency, 3),
        "relevance_score": round(relevance_score, 3),
    }


def main():
    """Run the evaluation pipeline."""

    api_key = load_config()

    client = create_client(api_key)

    dataset = load_evaluation_dataset()

    results = []

    for item in dataset:
        print(f"\nEvaluating: {item['question']}")

        result = evaluate_response(
            client,
            item["question"],
            item["expected_answer"],
        )

        results.append(result)

        print(f"Latency: {result['latency_seconds']} seconds")
        print(f"Relevance score: {result['relevance_score']}")
        print(f"Answer: {result['actual_answer']}")

    average_latency = (
        sum(result["latency_seconds"] for result in results) 
        / len(results)
    )

    average_relevance = (
        sum(item["relevance_score"] for item in results)
        / len(results)
    )

    print("\n===========Evaluation Summary============")
    print(f"Average Latency: {average_latency:.3f} seconds")
    print(f"Average Relevance: {average_relevance:.3f}")


if __name__ == "__main__":
    main()
