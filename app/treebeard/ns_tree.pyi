from django.db import models
from treebeard.models import Node
from collections.abc import Iterable

class NS_NodeQuerySet(models.query.QuerySet):
    def delete(
        self,
        *args,
        removed_ranges: Iterable | None = None,
        deleted_counter: tuple[int, dict[str, int]] | None = None,
        **kwargs,
    ) -> tuple[int, dict[str, int]]: ...

class NS_NodeManager(models.Manager):
    def get_queryset(self) -> NS_NodeQuerySet: ...

class NS_Node(Node, models.Model):
    lft: models.PositiveIntegerField
    rgt: models.PositiveIntegerField
    tree_id: models.PositiveIntegerField
    depth: models.PositiveIntegerField

    objects: NS_NodeManager
