---
name: python-typing-standards
description: Type annotation rules for this Python 3.14 codebase — no `from __future__ import annotations`, forward references, TYPE_CHECKING imports, and union syntax. Use when writing or editing type hints, resolving circular imports between models or schemas, or debugging NameError / "not fully defined" errors from annotations.
---

# SKILL: python-typing-standards

## Context
Every package requires Python >= 3.14. Since 3.14, annotations are evaluated lazily by default (PEP 649 / PEP 749), which replaces the old `from __future__ import annotations` behaviour (PEP 563). Forward references therefore work WITHOUT string quotes, as long as the name can be resolved when a library (SQLAlchemy, Pydantic) inspects the annotation.

## Rules for Agents
1. NEVER add `from __future__ import annotations`. It is superseded on 3.14 and changes how SQLAlchemy and Pydantic resolve annotations.
2. Forward / circular references:
   - Put the cyclic import inside `if TYPE_CHECKING:` and write the annotation normally:
     - Good: `programs: Mapped[list[Program]] = relationship("Program", back_populates="college")`
     - Avoid (unneeded on 3.14): `Mapped[list["Program"]]`, `"list[ProgramRead]"`
   - SQLAlchemy resolves model names through its class registry, so `TYPE_CHECKING` imports are enough for models.
   - Pydantic needs the real class at runtime, so schemas also need a bottom-level import plus `.model_rebuild()`:
   ```python
   from typing import TYPE_CHECKING
   from pydantic import BaseModel, ConfigDict

   if TYPE_CHECKING:
       from app.schemas.program import ProgramRead

   class CollegeReadDetailed(CollegeRead):
       programs: list[ProgramRead] = []

   # bottom-of-file runtime import & rebuild
   from app.schemas.program import ProgramRead
   CollegeReadDetailed.model_rebuild()
   ```
3. Backend imports always start at `app.` (e.g. `from app.models.program import Program`), never `backend.app.`.
4. Use native syntax:
   - Unions: `str | None`, `int | float`, not `Optional[str]` / `Union[...]`.
   - Generics: `list[str]`, `dict[str, int]`, not `typing.List` / `typing.Dict`.
5. The scraper and scripts packages are mostly unannotated legacy code. Annotate functions you add or substantially change, but don't mass-annotate untouched code.
