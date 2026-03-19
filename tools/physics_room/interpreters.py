from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict
import json
import math
from urllib import error, request


@dataclass
class OllamaToolExpert:
    """Base adapter for local Ollama-driven interpretation of probe outputs."""

    model: str = "llama3.1"
    endpoint: str = "http://localhost:11434/api/generate"
    timeout_seconds: float = 20.0

    def analyze(self, system_role: str, prompt: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = {
            "model": self.model,
            "stream": False,
            "prompt": f"ROLE: {system_role}\n{prompt}\nDATA:\n{json.dumps(payload)[:12000]}",
        }

        req = request.Request(
            self.endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as resp:
                raw = resp.read().decode("utf-8")
                parsed = json.loads(raw)
                response_text = parsed.get("response", "")
                return {
                    "ok": True,
                    "model": self.model,
                    "analysis": self._try_parse_json(response_text),
                    "raw_text": response_text,
                }
        except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            return {
                "ok": False,
                "model": self.model,
                "error": str(exc),
            }

    def _try_parse_json(self, text: str) -> Any:
        stripped = text.strip()
        if not stripped:
            return {}

        if stripped.startswith("{") and stripped.endswith("}"):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                return stripped

        return stripped


@dataclass
class MicroscopistExpert(OllamaToolExpert):
    """Analyzes STM output to detect emerging spatial signatures."""

    def assess_stm_scan(self, stm_scan: Dict[str, Any]) -> Dict[str, Any]:
        prompt = (
            "You are The Microscopist. Analyze STM `height_map` and `current_map`. "
            "Detect any spectral butterfly-like spatial pattern. "
            "Return STRICT JSON with keys: "
            "butterfly_emerging (bool), confidence (0..1), notes (string)."
        )
        return self.analyze("Microscopist", prompt, stm_scan)


@dataclass
class SpectroscopistExpert(OllamaToolExpert):
    """Interprets Raman/NMR spectral purity relative to harmonic constants."""

    def assess_spectrum(
        self,
        spectrum: Dict[str, Any],
        harmonic_constant: float = 198.0 * math.pi,
    ) -> Dict[str, Any]:
        payload = {
            **spectrum,
            "target_harmonic_constant": harmonic_constant,
        }
        prompt = (
            "You are The Spectroscopist. Compare spectral peaks to the target "
            "harmonic constant and its integer multiples/submultiples. "
            "Return STRICT JSON with keys: resonantly_pure (bool), "
            "confidence (0..1), matched_peaks (array), notes (string)."
        )
        return self.analyze("Spectroscopist", prompt, payload)
