import logging
from sqlalchemy import (
    Table,
    MetaData,
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
    event,
)
from sqlalchemy.orm import mapper, relationship

from switchbot.domain import model

logger = logging.getLogger(__name__)


def start_mappers():
    # todo
    logger.info("Starting mappers")
    raise NotImplementedError
    # lines_mapper = mapper(model.OrderLine, order_lines)
    # batches_mapper = mapper(
    #     model.Batch,
    #     batches,
    #     properties={
    #         "_allocations": relationship(
    #             lines_mapper,
    #             secondary=allocations,
    #             collection_class=set,
    #         )
    #     },
    # )
    # mapper(
    #     model.Product,
    #     products,
    #     properties={"batches": relationship(batches_mapper)},
    # )