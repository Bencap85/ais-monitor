from enum import Enum
import uuid


# Stage enum
class PipelineStage(Enum):
    FETCHING = "Fetching tiles"
    DETECTING = "Detecting ships"
    CLASSIFYING = "Classifying detections"  
    COMPLETED = "Completed"
    FAILED = "Failed"


# Maps for pipeline status information now, can change to use Redis as needed
id_to_status = {} # { id -> { stage: PipelineStage, progress: float }}
id_to_result = {} # { id -> result<dict> }


def create_new_pipeline_id():
    unique_id = str(uuid.uuid4())
    return unique_id

    
# Statuses and results should only be mutated and accessed via the below predefined interface
def update_pipeline_status(id: str, stage: PipelineStage, current_step: int, total_steps: int) -> bool:
    if id not in id_to_status:
        id_to_status[id] = {}

    progress = round(float(current_step / total_steps), 2)

    current_status = id_to_status[id]
    current_status["stage"] = stage
    current_status["progress"] = progress

    id_to_status[id] = current_status
    return True

def get_pipeline_status(id: str):
    if id in id_to_status:
        return id_to_status[id]

    return None

def set_pipeline_result(id: str, result: dict) -> bool:
    if not id in id_to_result:
        id_to_result[id] = {}
        
    id_to_result[id] = result
    return True


def get_pipeline_result(id: str) -> dict:
    if id in id_to_result:
        return id_to_result[id]

    return None



    