import pytest
from akita.reasoning.engine import ReasoningEngine
from akita.reasoning.session import ConversationSession
from akita.models.base import AIModel

class MockModel(AIModel):
    def chat(self, messages):
        # Respond with a fixed diff
        return type('obj', (object,), {
            'content': '--- a/f.py\n+++ b/f.py\n@@ -1,1 +1,1 @@\n-old\n+new'
        })()

def test_interactive_session_state():
    model = MockModel(model_name="test")
    engine = ReasoningEngine(model)
    
    # 1. First call creates session
    engine.run_solve("Initial task")
    assert engine.session is not None
    assert len(engine.session.messages) == 3 # system, user, assistant
    
    # 2. Second call with session refinement
    engine.run_solve("Refinement task", session=engine.session)
    assert len(engine.session.messages) == 5 # prev + user + assistant
    assert engine.session.messages[3].content == "Refinement task"

def test_trace_collection():
    model = MockModel(model_name="test")
    engine = ReasoningEngine(model)
    engine.run_solve("Test trace")
    
    assert len(engine.trace.steps) > 0
    assert any(step.action == "LLM Response" for step in engine.trace.steps)
