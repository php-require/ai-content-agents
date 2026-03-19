# Copilot Instructions for Shorts Agent

## Project Overview

**Shorts Agent** is a Python-based AI content generation system that produces structured YouTube Shorts scripts using OpenAI's GPT-4o model with JSON schema enforcement. It's designed as the **first stage of an automated video production pipeline**.

### Key Architectural Pattern

The pipeline follows a **three-layer separation**:
1. **Schema Definition** (`src/schemas/`) - Strict JSON structure enforced by OpenAI's `json_schema` response format
2. **Prompt Engineering** (`src/prompts/`) - Detailed system instructions guiding the LLM behavior
3. **Agent Execution** (`src/agents/script_agent.py`) - Orchestrates the API call with environment management

This separation allows prompt updates and schema changes without touching agent logic.

## Critical Data Flow

```
main.py → generate_shorts_script(topic, niche, tone, language)
  → OpenAI API (gpt-4o with SHORTS_SCHEMA)
  → JSON output → output/result.json
```

**Input Parameters** (all strings):
- `topic` - Content subject
- `niche` - Content category (default: "tech")
- `tone` - Emotional delivery (default: "exciting")
- `target_language` - Output language (default: "English")

**Output Structure** - All fields required in JSON:
- `hook` - <10 word attention grabber
- `title` - <60 character, clickable headline
- `hashtags` - Array of 3-8 hashtags with # prefix
- `voiceover` - Array of 4-8 short lines for TTS
- `scenes` - Array of 4-6 scenes with timing and prompts
- `cta` - Call-to-action sentence

## Critical Constraints (Enforced by Schema)

### Scene Timing Rules
- **Total duration**: 20-30 seconds only
- **Per-scene**: 3-5 seconds (final scene can extend)
- **No gaps or overlaps** - scenes must form continuous timeline
- Scene progression must be **logical and sequential**

### Image Generation Requirements
- **Always include**: "cinematic lighting", "high detail", "vertical composition (9:16)"
- **Avoid abstract concepts** - Use concrete subjects (developer, screen, action)
- **Structure**: subject → action → environment → style
- **Forbidden patterns**: Symbolic AI brains, abstract data flows, vague backgrounds

### Voiceover Rules
- One line per new idea
- TTS-friendly (short, natural phrasing)
- No filler or repetition
- Captions should be **shorter than voiceover** text

## Development Workflow

### Running the Agent
```bash
python src/main.py
```
Output saved to `output/result.json` and printed to console.

### Debugging
```bash
python src/tools/list_models.py  # Verify available OpenAI models
```

### Environment Setup
- Create `.env` file (see `.env.example`)
- Set `OPENAI_API_KEY`
- Agent validates key exists, raises `ValueError` if missing

## Key Integration Points

### OpenAI Client Configuration
- Uses `gpt-4o` model (hardcoded in `script_agent.py`)
- Temperature set to `0.9` for creative variation
- Response format: `json_schema` with `strict: True`
- **Cost tracking built-in** - displays token usage and USD cost

### Cost Calculation Logic
```python
input_cost = input_tokens * 0.000005
output_cost = output_tokens * 0.000015
total_cost = input_cost + output_cost
```
(Approximate GPT-4o pricing - verify against current rates)

## Common Patterns & Conventions

### Prompt Engineering
- System role: "developer" (sends `IT_SHORTS_PROMPT`)
- User role: Contains variables injected at runtime
- Prompt emphasizes **viral metrics** (hook strength, retention, pacing)
- Includes **concrete bad examples** to prevent abstract visuals

### JSON Schema Enforcement
- Uses OpenAI's strict mode (`"strict": True`)
- All properties have `additionalProperties: False` - rejects unknown fields
- Min/max constraints on array lengths (hashtags, voiceover, scenes)
- Required fields enforced at schema level

### Module Imports
- Relative imports used throughout (`from agents.script_agent import ...`)
- `load_dotenv()` called at module level in `script_agent.py`
- `os.getenv()` with fallback validation pattern

## When Adding Features

### To Add a New Output Field
1. Add to schema in `src/schemas/it_shorts_schema.py` (properties + required array)
2. Add corresponding instruction in `IT_SHORTS_PROMPT`
3. Include concrete examples of good/bad outputs in prompt
4. Test against schema strict mode

### To Modify Prompt Behavior
- Edit `IT_SHORTS_PROMPT` in `src/prompts/it_shorts_prompt.py`
- Document visual constraints explicitly (the codebase heavily emphasizes concrete visuals over abstract)
- Always test output against schema validation
- Remember: LLM must generate valid JSON matching schema exactly

### To Support New Niches
- Extend `IT_SHORTS_PROMPT` with niche-specific guidance
- No code changes needed - system uses string variables, not hardcoded lists
- Validate output against existing schema (schema is niche-agnostic)

## Testing Output Quality

Key metrics from README workflow:
- Hook must work for TTS (test pronunciation)
- Image prompts must generate usable visuals (test specificity)
- Scene timings must not overlap (validate mathematically)
- All hashtags must start with #

The agent outputs consumable structure for:
- **TTS pipelines** - voiceover lines are the primary input
- **Image generation** - scenes[].image_prompt feeds to AI image models
- **Video assembly** - scenes with timing enables automated subtitle/video sync
