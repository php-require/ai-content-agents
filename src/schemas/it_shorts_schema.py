SHORTS_SCHEMA = {
    "name": "shorts_script_package",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "hook": {"type": "string"},
            "title": {"type": "string"},
            "hashtags": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 3,
                "maxItems": 8
            },
            "voiceover": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 4,
                "maxItems": 8
            },
            "scenes": {
                "type": "array",
                "minItems": 4,
                "maxItems": 6,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "scene_number": {"type": "integer"},
                        "start_sec": {"type": "integer"},
                        "end_sec": {"type": "integer"},
                        "caption": {"type": "string"},
                        "image_prompt": {"type": "string"}
                    },
                    "required": [
                        "scene_number",
                        "start_sec",
                        "end_sec",
                        "caption",
                        "image_prompt"
                    ]
                }
            },
            "cta": {"type": "string"}
        },
        "required": [
            "hook",
            "title",
            "hashtags",
            "voiceover",
            "scenes",
            "cta"
        ]
    }
}