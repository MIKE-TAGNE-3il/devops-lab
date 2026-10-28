"""Modèles SQLAlchemy : une classe = une table PostgreSQL."""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    # Rempli par PostgreSQL (now()) et non par Python : même horloge pour tous les clients.
    # timezone=True : on stocke un instant précis, sans ambiguïté entre PC et serveur.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
