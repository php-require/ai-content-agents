THUMBNAIL_SCHEMA = {
    "name": "thumbnail_schema",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "thumbnail_title": {
                "type": "string",
                "description": "A short, punchy thumbnail title or concept line."
            },
            "thumbnail_hook": {
                "type": "string",
                "description": "A curiosity-driven hook for the thumbnail concept."
            },
            "image_prompt": {
                "type": "string",
                "description": "A detailed, generator-friendly prompt for creating the image."
            },
            "visual_focus": {
                "type": "string",
                "description": "The main visual subject or focal point of the image."
            },
            "negative_prompt": {
                "type": "string",
                "description": "Things the image generator should avoid."
            },
            "style_notes": {
                "type": "array",
                "description": "Short practical visual notes for style and direction.",
                "items": {
                    "type": "string"
                },
                "minItems": 3,
                "maxItems": 8
            }
        },
        "required": [
            "thumbnail_title",
            "thumbnail_hook",
            "image_prompt",
            "visual_focus",
            "negative_prompt",
            "style_notes"
        ],
        "additionalProperties": False
    }
}