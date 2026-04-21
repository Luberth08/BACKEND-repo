from typing import Optional
from app.crud.base import CRUDBase
from app.models.incidente import Incidente


class CRUDIncidente(CRUDBase[Incidente]):
    """CRUD mínimo para `Incidente`."""
    pass


incidente = CRUDIncidente(Incidente)
