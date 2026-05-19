from __future__ import annotations

import mimetypes
from pathlib import Path
from threading import Lock

import curl_cffi
from cloakbrowser import launch
from curl_cffi import requests

from openai_verify_api.config import settings
from openai_verify_api.models import OpenAIUpstreamResponse, VerificationResponse


class OpenAIVerifyError(RuntimeError):
    """Raised when the OpenAI verification flow fails."""


def is_openai_generated(payload: OpenAIUpstreamResponse) -> bool:
    return any(result.outcome == "detected" for result in payload.results)


class OpenAIVerifier:
    def __init__(self) -> None:
        self._browser = None
        self._lock = Lock()

    def _get_browser(self):
        if self._browser is None:
            self._browser = launch(
                headless=settings.browser_headless,
                humanize=settings.browser_humanize,
            )
        return self._browser

    def close(self) -> None:
        if self._browser is not None:
            self._browser.close()
            self._browser = None

    def _mint_turnstile_token_and_cookies(self) -> tuple[str, list[dict]]:
        browser = self._get_browser()
        page = browser.new_page()
        context = page.context
        try:
            page.goto(
                settings.openai_verify_page_url,
                wait_until="networkidle",
                timeout=settings.navigation_timeout_ms,
            )
            token = page.evaluate(
                """async (timeoutMs) => {
                    window.turnstile.execute(0);
                    const input = () => document.querySelector('input[name="cf-turnstile-response"]');
                    const start = Date.now();
                    while (Date.now() - start < timeoutMs) {
                        const value = input()?.value;
                        if (value) return value;
                        await new Promise((resolve) => setTimeout(resolve, 250));
                    }
                    return null;
                }""",
                settings.token_timeout_ms,
            )
            if not token:
                raise OpenAIVerifyError("Failed to mint a Turnstile token.")
            cookies = context.cookies()
            return token, cookies
        finally:
            context.close()

    def _submit_upload(self, image_path: Path, media_type: str | None, token: str, cookies: list[dict]) -> OpenAIUpstreamResponse:
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie["name"], cookie["value"], domain=cookie["domain"], path=cookie["path"])

        content_type = media_type or mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"
        multipart = curl_cffi.CurlMime()
        multipart.addpart(
            name="file",
            filename=image_path.name,
            content_type=content_type,
            local_path=str(image_path),
        )
        try:
            response = session.post(
                settings.openai_verify_api_url,
                multipart=multipart,
                headers={
                    "Origin": "https://openai.com",
                    "Referer": settings.openai_verify_page_url,
                    "X-Turnstile-Token": token,
                },
                impersonate=settings.curl_impersonate,
                timeout=settings.upload_timeout_seconds,
            )
        finally:
            multipart.close()

        if response.status_code != 200:
            raise OpenAIVerifyError(f"OpenAI verify upload failed with status {response.status_code}.")
        return OpenAIUpstreamResponse.model_validate(response.json())


def verify_image(path: Path, media_type: str | None = None) -> VerificationResponse:
    with verifier._lock:
        token, cookies = verifier._mint_turnstile_token_and_cookies()
        upstream = verifier._submit_upload(path, media_type, token, cookies)
    return VerificationResponse(
        filename=path.name,
        media_type=media_type,
        openai_generated=is_openai_generated(upstream),
        upstream=upstream,
    )


verifier = OpenAIVerifier()
