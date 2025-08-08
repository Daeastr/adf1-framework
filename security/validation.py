# security/validation.py

import re

def sanitize_input(prompt: str) -> str:
    """
    Sanitizes user input to mitigate basic prompt injection attacks.
    This looks for common instruction-hijacking phrases.
    
    Args:
        prompt (str): The user-provided input.

    Returns:
        str: The sanitized prompt.
    """
    # Pattern to find phrases like "ignore the above instructions"
    injection_pattern = re.compile(
        r'ignore the.*instructions|disregard the.*and follow|forget the previous context', 
        re.IGNORECASE
    )
    
    if injection_pattern.search(prompt):
        # For simplicity, we'll log and return a safe message.
        # In a real app, you might strip the pattern or reject the input entirely.
        print("Potential prompt injection detected. Sanitizing input.")
        # Stripping the malicious part could be an option:
        # sanitized_prompt = injection_pattern.sub('', prompt).strip()
        # return sanitized_prompt
        raise ValueError("Malicious input detected: Prompt injection attempt.")

    # If no injection is detected, return the original prompt
    return prompt