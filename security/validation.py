import re

def sanitize_input(prompt: str) -> str:
    """
    Sanitizes user input and raises ValueError for malicious content.
    """
    # Pattern matching for common prompt injection techniques
    injection_pattern = re.compile(
        r'ignore.*?instructions|disregard.*?and follow|forget the previous context|do something else',
        re.IGNORECASE | re.DOTALL
    )

    if injection_pattern.search(prompt):
        print(f"Malicious content detected in prompt: '{prompt}'")
        raise ValueError(f"Malicious content detected: '{prompt}'")
    
    return prompt