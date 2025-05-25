from django.db import models
from treebeard.models import Node
from collections.abc import Iterable
from typing import Any, Self

class MP_NodeQuerySet(models.query.QuerySet):
    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]: ...

class MP_NodeManager(models.Manager):
    def get_queryset(self) -> MP_NodeQuerySet: ...

class MP_AddHandler:
    stmts: list

class MP_ComplexAddMoveHandler(MP_AddHandler):
    def run_sql_stmts(self) -> None: ...
    def get_sql_update_numchild(self, path, incdec="inc") -> tuple[str, list[str]]: ...
    def reorder_nodes_before_add_or_move(
        self,
        pos: str,
        newpos: str,
        newdepth: int,
        target: Any,
        siblings: models.QuerySet,
        oldpath: Any | None,
        movebranch: bool,
    ) -> tuple[Iterable, Iterable]: ...

    # Suspect oldpath and newpath are str
    def get_sql_newpath_in_branches(self, oldpath: Iterable, newpath: Iterable) -> tuple[str, list]: ...

class MP_AddRootHandler(MP_AddHandler):
    kwargs: dict

    # returns the type of object this whole thing is a queryset or whatever of
    # possibly return type is MP_Node
    def process(self) -> "MP_Node": ...

class MP_AddChildHandler(MP_AddHandler):
    node: "MP_Node"
    node_cls: Any
    kwargs: dict

class MP_AddSiblingHandler(MP_ComplexAddMoveHandler):
    node: "MP_Node"
    node_cls: Any
    pos: Any
    kwargs: dict

class MP_MoveHandler(MP_ComplexAddMoveHandler):
    node: "MP_Node"
    node_cls: Any
    target: Any
    pos: str  # maybe get actual value options

    def sanity_updates_after_move(self, oldpath: Any, newpath: Any) -> None: ...
    def update_move_to_child_vars(self) -> tuple[Any, MP_NodeQuerySet, int]: ...
    def get_mysql_update_depth_in_branch(self, path: Any) -> tuple[str, list]: ...

class MP_Node(Node, models.Model):
    steplen: int
    alphabet: str
    node_order_by: list
    path: models.CharField
    depth: models.PositiveIntegerField
    numchild: models.PositiveIntegerField
    objects: MP_NodeManager

    @classmethod
    def add_root(cls, **kwargs) -> Self: ...
