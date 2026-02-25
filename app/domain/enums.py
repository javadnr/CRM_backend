from enum import Enum

class LeadStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    CONVERTED = "converted"
    LOST = "lost"
    
    