# SKILL: scoutly-python-typing-standards

## Rules for Agents
1. STRICT ANTI-PATTERN: DO NOT use `from __future__ import annotations`. 
   - All models, schemas, and endpoints must use native runtime type evaluations.
2. Handling Circular Model & Schema References:
   - When a circular reference exists, wrap the ENTIRE generic type annotation in a string literal.
   - Bad: `programs: list["ProgramRead"] = []`
   - Bad: `from __future__ import annotations` -> `programs: list[ProgramRead] = []`
   - Good: `programs: "list[ProgramRead]" = []`
   - Good (Singular): `college: "CollegeRead"`
3. Static Analysis Protection:
   - Put cyclic imports inside `if TYPE_CHECKING:` blocks at the top of the file.
   - For Pydantic models requiring circular types, use bottom-level runtime imports paired with `.model_rebuild()`:
   ```python
   from typing import TYPE_CHECKING
   from pydantic import BaseModel, ConfigDict

   if TYPE_CHECKING:
       from app.schemas.program import ProgramRead

   class CollegeReadDetailed(BaseModel):
       unit_id: int
       programs: "list[ProgramRead]" = []
       model_config = ConfigDict(from_attributes=True)

   # Bottom deferred import & rebuild:
   from app.schemas.program import ProgramRead
   CollegeReadDetailed.model_rebuild()
   ```
4. Use standard Python 3.10+ native union types:
    - Bad: Optional[str], Union[int, float]
    - Good: str | None, int | float