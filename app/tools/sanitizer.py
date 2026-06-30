import re
import logging
from typing import Tuple

# Set up logging for security monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SecuritySanitizer")

# Compile regex patterns for known prompt injection / jailbreak techniques
INJECTION_PATTERNS = [
    re.compile(r"(?i)ignore\s+(your\s+)?previous\s+instructions"),
    re.compile(r"(?i)system\s+override"),
    re.compile(r"(?i)you\s+are\s+now\s+a\s+different\s+agent"),
    re.compile(r"(?i)bypass\s+the\s+pipeline"),
    re.compile(r"(?i)disable\s+safety\s+filters"),
    re.compile(r"(?i)you\s+are\s+no\s+longer\s+constrained"),
    re.compile(r"(?i)assistant\s+override"),
    re.compile(r"(?i)forget\s+everything\s+you\s+were\s+told"),
    re.compile(r"(?i)new\s+rule:"),
    re.compile(r"(?i)jailbreak")
]

def sanitize_text(text: str) -> Tuple[str, bool]:
    """Scans and sanitizes research text for adversarial prompt injection phrases.
    
    Checks text line-by-line. If a suspicious pattern is matched, that line 
    is removed and the block is flagged.
    
    Args:
        text: The raw literature findings text.
        
    Returns:
        A tuple of (sanitized_text, was_flagged) where:
            sanitized_text: The input text with malicious lines stripped.
            was_flagged: Boolean indicating whether an injection attempt was detected.
    """
    if not text:
        return "", False
        
    lines = text.splitlines()
    cleaned_lines = []
    was_flagged = False
    
    for idx, line in enumerate(lines):
        matched = False
        for pattern in INJECTION_PATTERNS:
            if pattern.search(line):
                logger.warning(
                    f"[SECURITY ALERT] Prompt injection signature '{pattern.pattern}' detected in line {idx+1}."
                )
                was_flagged = True
                matched = True
                break
                
        # Only include the line if no adversarial signature matched
        if not matched:
            cleaned_lines.append(line)
            
    sanitized_text = "\n".join(cleaned_lines)
    return sanitized_text, was_flagged
