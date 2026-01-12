import json
from pathlib import Path


class ContextMemory:
    """
    Persistent, safe, non-hallucinating conversation memory.
    Stores ONLY analytical intent (never results).
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.memory_path = Path("sessions") / f"{session_id}.json"
        self.memory_path.parent.mkdir(exist_ok=True)

        if self.memory_path.exists():
            self.state = json.loads(self.memory_path.read_text())
        else:
            self.state = {}

    # ---------------------------
    # Store only intent
    # ---------------------------
    def update(self, plan: dict):
        """
        Save the last analytical intent.
        We store ONLY the semantic target (column) and operation.
        """
        intent = {}

        if "column" in plan:
            intent["entity"] = plan["column"]

        if "group_by" in plan:
            intent["entity"] = plan["group_by"]

        if "metric" in plan:
            intent["metric"] = plan["metric"]

        if intent:
            self.state["last_intent"] = intent
            self._persist()

    # ---------------------------
    # Follow-up resolution
    # ---------------------------
    def resolve_followup(self, question: str):
        """
        Handles:
        - "why?"
        - "name them"
        - "list them"
        - "those"
        - "what about Pune?"
        """

        q = question.lower().strip()

        # ---- WHY / EXPLAIN ----
        if q in ["why", "why?", "explain", "explain this"]:
            if "last_plan" in self.state:
                last = self.state["last_plan"]
                last["explanation_required"] = True
                self.state["last_plan"] = last
                self._persist()
            return question

        # ---- PRONOUN RESOLUTION ----
        if "last_intent" in self.state:
            entity = self.state["last_intent"].get("entity")

            if entity:
                trigger_words = ["them", "those", "these", "list them", "name them", "show them"]

                if any(word in q for word in trigger_words):
                    return f"{question} {entity}"

        return question

    # ---------------------------
    # Save to disk
    # ---------------------------
    def _persist(self):
        self.memory_path.write_text(json.dumps(self.state, indent=2))
