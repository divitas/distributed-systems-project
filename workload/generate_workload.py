from __future__ import annotations

from dataclasses import dataclass

from workload.documents import BASE_DOCUMENTS, QUESTIONS, build_prompt


@dataclass
class WorkloadRequest:
    request_id: int
    document_id: int
    round_id: int
    question: str
    prompt: str


def generate_reuse_workload(rounds: int = 3) -> list[WorkloadRequest]:
    requests: list[WorkloadRequest] = []
    request_id = 0

    for round_id in range(rounds):
        for document_id, document in enumerate(BASE_DOCUMENTS):
            for question in QUESTIONS:
                requests.append(
                    WorkloadRequest(
                        request_id=request_id,
                        document_id=document_id,
                        round_id=round_id,
                        question=question,
                        prompt=build_prompt(document, question),
                    )
                )
                request_id += 1

    return requests