# backend/src/models/user.py

from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: Optional[int] = None
    # Add other user-related fields here if necessary
