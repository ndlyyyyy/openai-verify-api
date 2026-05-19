from __future__ import annotations

import argparse

import uvicorn

from openai_verify_api.api import app
from openai_verify_api.config import settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the OpenAI Verify API server.")
    parser.add_argument("--host", default=settings.host)
    parser.add_argument("--port", type=int, default=settings.port)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
