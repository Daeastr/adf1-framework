class TaskType(str, Enum):
    TEXT_GENERATION = 'text_generation'
    QUESTION_ANSWERING = 'question_answering'
    YOUTUBEING = 'youtubeing'  # Keep if actually needed, match naming convention
    CREATIVE_WRITING = 'creative_writing'
    CODE_ASSISTANCE = 'code_assistance'
    ANALYSIS = 'analysis'
    SUMMARIZATION = 'summarization'

