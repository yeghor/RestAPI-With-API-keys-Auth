from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Annotated

class Stats(BaseModel):
    requests_today: int
    requests_total: int
    