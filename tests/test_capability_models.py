from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class TaskType(str, Enum):
    TEXT_GENERATION = 'text_generation'
    QUESTION_ANSWERING = 'question_answering'
    YOUTUBEING = 'youtubeing'  # keep if still needed
    CREATIVE_WRITING = 'creative_writing'
    CODE_ASSISTANCE = 'code_assistance'
    ANALYSIS = 'analysis'
    SUMMARIZATION = 'summarization'

