"""Routes CRUD de la ressource Item."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Item
from app.schemas import ItemCreate, ItemRead, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])

DbSession = Annotated[Session, Depends(get_db)]


def get_item_or_404(item_id: int, db: DbSession) -> Item:
    """Dépendance : retrouve l'élément ou renvoie 404.

    Factorisée ici pour ne pas recopier la même vérification dans GET, PUT et DELETE.
    """
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item introuvable")
    return item


ExistingItem = Annotated[Item, Depends(get_item_or_404)]


@router.get("", response_model=list[ItemRead])
def list_items(
    db: DbSession,
    # Liste bornée : une route qui renverrait "tout" saturerait le serveur avec une grosse table.
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Item]:
    requete = select(Item).order_by(Item.id).limit(limit).offset(offset)
    return list(db.scalars(requete))


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, db: DbSession) -> Item:
    item = Item(name=payload.name)
    db.add(item)
    db.commit()
    # refresh : relit la ligne pour récupérer l'id et le created_at fabriqués par PostgreSQL.
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=ItemRead)
def read_item(item: ExistingItem) -> Item:
    return item


@router.put("/{item_id}", response_model=ItemRead)
def update_item(payload: ItemUpdate, item: ExistingItem, db: DbSession) -> Item:
    item.name = payload.name
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item: ExistingItem, db: DbSession) -> Response:
    db.delete(item)
    db.commit()
    # 204 : succès sans contenu à renvoyer.
    return Response(status_code=status.HTTP_204_NO_CONTENT)
