from openai_verify_api.models import OpenAIUpstreamResponse
from openai_verify_api.services.verifier import is_openai_generated


def test_detected_payload_is_classified_as_openai_generated() -> None:
    payload = OpenAIUpstreamResponse.model_validate(
        {
            "object": "provenance_check",
            "created_at": 1,
            "results": [
                {"type": "c2pa", "issuer": "OpenAI OpCo, LLC", "outcome": "detected", "validation_state": "trusted"},
                {"type": "synthid", "outcome": "detected"},
            ],
        }
    )
    assert is_openai_generated(payload) is True


def test_negative_payload_is_classified_as_not_generated() -> None:
    payload = OpenAIUpstreamResponse.model_validate(
        {
            "object": "provenance_check",
            "created_at": 1,
            "results": [
                {"type": "c2pa", "issuer": None, "outcome": "not_detected", "validation_state": "not_present"},
                {"type": "synthid", "outcome": "not_detected"},
            ],
        }
    )
    assert is_openai_generated(payload) is False
