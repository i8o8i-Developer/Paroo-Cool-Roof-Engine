"""
Title Case Logger Utility Module For PARoo Satellite Rooftop Heat Vulnerability Classifier
"""

import sys
import logging
import re

def ToTitleCase(Text: str) -> str:
    """Convert Input String To Title Case Formatting While Preserving Acronyms And Numbers."""
    if not Text:
        return ""
    # List Of Acronyms To Preserve In Upper Case
    PreserveAcronyms = {"LST", "NDVI", "NDBI", "GLCM", "LLP", "NIR", "RGB", "SWIR", "RCC", "TIRS", "ECOSTRESS", "INR", "CSV", "JSON", "GEOJSON", "API", "OSM", "AI", "QA", "AOI", "ID", "OB", "REST", "HUD", "PDF"}
    
    Words = re.split(r'(\s+)', Text)
    FormattedWords = []
    for Word in Words:
        CleanWord = re.sub(r'[^A-Za-z0-9]', '', Word)
        UpperClean = CleanWord.upper()
        if UpperClean in PreserveAcronyms:
            # Replace The Word Part While Keeping Surrounding Punctuation
            FormattedWords.append(Word.replace(CleanWord, UpperClean))
        elif Word.strip():
            # Standard Title Case Word
            FormattedWords.append(Word.capitalize())
        else:
            FormattedWords.append(Word)
    return "".join(FormattedWords)

class TitleCaseFormatter(logging.Formatter):
    """Custom Logging Formatter That Transforms All Output Text To Title Case."""
    def format(self, record: logging.LogRecord) -> str:
        OriginalMessage = record.getMessage()
        RecordLevel = record.levelname.title()
        FormattedMessage = ToTitleCase(OriginalMessage)
        return f"[{RecordLevel}] {FormattedMessage}"

def SetupLogger(Name: str = "PARooLogger") -> logging.Logger:
    """Configure And Return A Standard Title Case Logger."""
    Logger = logging.getLogger(Name)
    Logger.setLevel(logging.INFO)
    
    if not Logger.handlers:
        StreamHandler = logging.StreamHandler(sys.stdout)
        StreamHandler.setFormatter(TitleCaseFormatter())
        # Safe Error Handling For Windows Legacy Consoles
        if hasattr(StreamHandler.stream, 'reconfigure'):
            try:
                StreamHandler.stream.reconfigure(errors='replace')
            except Exception:
                pass
        Logger.addHandler(StreamHandler)
        
    return Logger

# Export Global System Logger Instance
SystemLogger = SetupLogger()

def LogInfo(Message: str) -> None:
    """Log Informational Message In Title Case."""
    SystemLogger.info(ToTitleCase(Message))

def LogWarning(Message: str) -> None:
    """Log Warning Message In Title Case."""
    SystemLogger.warning(ToTitleCase(Message))

def LogError(Message: str) -> None:
    """Log Error Message In Title Case."""
    SystemLogger.error(ToTitleCase(Message))
