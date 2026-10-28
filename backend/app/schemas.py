"""Schémas Pydantic : ce que l'API accepte en entrée et renvoie en sortie.

Distincts du modèle SQLAlchemy (models.py) : on contrôle ce qui sort de l'API,
et le client ne peut jamais imposer un id ou un created_at.
"""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

# Nom : espaces retirés aux extrémités, 1 à 100 caractères. La limite de 100 reprend
# celle de la colonne String(100) : sans elle, un nom trop long ferait échouer la base
# (erreur 500) au lieu de renvoyer une erreur de validation claire (422).
ItemName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]


class ItemCreate(BaseModel):
    """Corps d'un POST : seul le nom est fourni par le client."""

    name: ItemName


class ItemUpdate(BaseModel):
    """Corps d'un PUT : remplacement complet des champs modifiables."""

    name: ItemName


class ItemRead(BaseModel):
    """Réponse de l'API : un élément tel que stocké en base."""

    # from_attributes : permet de construire ce schéma directement depuis un objet SQLAlchemy.
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
