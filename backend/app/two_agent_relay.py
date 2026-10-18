"""Two-agent relay: ChatGPT reviewer <-> DeepSeek/Hermes execution partner.

The relay is durable, stateful, and bounded. It sends the project brief to the
existing ChatGPT thread, captures ChatGPT's review, asks DeepSeek to produce an
evidence-grounded response, then sends that response back to ChatGPT. It stops on
a stop condition or after MAX_ROUNDS; it never claims a commit/test it did not
observe.
"""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

CHATGPT = "http://127.0.0.1:8788/ask"
DEEPSEEK = "http://127.0.0.1:8787/ask"
STATE = Path.home() / ".local/state/pyschool-two-agent-relay.json"
MAX_ROUNDS = 12
THREAD = "College Project Report Review"


def call(url: str, prompt: str, timeout: int = 300) -> str:
    req = urllib.request.Request(url, data=json.dumps({"prompt": prompt, "timeout": timeout}).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout + 20) as response:
        data = json.load(response)
    if not data.get("ok"):
        raise RuntimeError(data.get("error", "relay provider error"))
    return data.get("text") or data.get("message", {}).get("text", "")


def load() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {"round": 0, "status": "idle", "last": None}


def save(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2) + "\n")
    tmp.replace(STATE)


def main() -> None:
    state = load()
    brief = """You are ChatGPT, the curriculum reviewer for a PySchool project. Hermes is the local implementation and verification agent in /mnt/storage/SCHOOL. PySchool is a Python learning-school MVP: 100 catalog paths; launch tracks are Web Development, Data Science, and Python for AI Research. Hermes has a durable lesson worker that generates content, validates theory/code/questions/homework, runs tests, and commits only verified lessons. Review batches, never claim unobserved execution, and give an actionable contract. We are now in a two-agent relay: your review is sent to Hermes/DeepSeek, then the response is returned here."""
    while state["round"] < MAX_ROUNDS:
        state["status"] = "chatgpt_review"; save(state)
        try:
            review = call(CHATGPT, brief if state["round"] == 0 else f"{brief}\n\nHermes/DeepSeek response to your previous review:\n{state.get('last','')}\n\nReview this response and state the single next action.", 300)
        except Exception as exc:
            state["status"] = "retrying_chatgpt"; state["last_error"] = repr(exc); save(state); time.sleep(10); continue
        state["last"] = review
        state["status"] = "deepseek_partner"; save(state)
        try:
            partner = call(DEEPSEEK, """You are Hermes' execution partner. A ChatGPT curriculum reviewer said:\n\n""" + review + """\n\nProject: /mnt/storage/SCHOOL, PySchool, 100 catalog paths, 3 existing launch tracks must remain untouched. Draft a concrete evidence-grounded response for the ChatGPT reviewer. Do not invent tests, commits, or files. Distinguish observed facts, required checks, and next action.""", 300)
        except Exception as exc:
            state["status"] = "retrying_deepseek"; state["last_error"] = repr(exc); save(state); time.sleep(10); continue
        state["round"] += 1
        state["status"] = "sending_back"; save(state)
        call(CHATGPT, f"Hermes/DeepSeek evidence-bound response:\n\n{partner}\n\nPlease review this response, identify any unsupported claim, and give the next single action.", 300)
        state["last"] = partner
        state["status"] = "idle"; save(state)
        time.sleep(2)
    state["status"] = "complete"; save(state)


if __name__ == "__main__":
    main()
