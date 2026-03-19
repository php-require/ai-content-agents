import json
from agents.script_agent import generate_shorts_script

result = generate_shorts_script(
    topic="Why AI agents will change programming forever",
    niche="AI / programming",
    tone="dramatic",
    target_language="English"
)

print(json.dumps(result, indent=2, ensure_ascii=False))