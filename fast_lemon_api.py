#!/usr/bin/env python3

# or run as: uvicorn fast_lemon_api:app

# std python-3.9
from datetime import datetime
from enum import Enum
from typing import List, Optional
import time
import uuid

# python3-pydantic
from pydantic import BaseModel, PositiveFloat, PositiveInt, UUID4, ValidationError, conint, constr, validator

# python3-fastapi
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import PlainTextResponse

# python3-uvicorn
import uvicorn

# pydantic model:


class OrderSide(str, Enum):
    buy = 'buy'
    sell = 'sell'


class OrderStatus(str, Enum):
    open = 'open',
    executed = 'executed',
    # more statuseses?


class BaseOrder(BaseModel):
    isin: constr(min_length=12, max_length=12)
    limit_price: PositiveFloat
    side: OrderSide
    valid_until: datetime
    quantity: conint(gt=0, strict=True)


class NewOrder(BaseOrder):
    # make 'side' case insensitive
    @validator('side', pre=True)
    def validate_side(cls, s):
        return s.lower()

    @validator('valid_until', pre=True)
    def validate_valid_until(cls, vu):
        if vu <= time.time():
            raise ValueError('valid_until cannot be in the past')
        dt = datetime.fromtimestamp(vu)
        return dt


class Order(BaseOrder):
    uuid: UUID4
    status: OrderStatus

    class Config:
        json_encoders = {
            datetime: lambda v: int(v.timestamp()),
        }


# orders 'database'
orders = {}

# now build the fastapi app
app = FastAPI()


@app.get("/", response_class=PlainTextResponse)
def read_root():
    return "Welcome to the fast-lemon-api!\n"


@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: uuid.UUID, q: Optional[str] = None):
    #return {"order_id": order_id, "q": q}
    if order_id in orders:
        return orders[order_id]
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No such order")


@app.post("/orders/",
          response_model=Order,
          status_code=status.HTTP_201_CREATED)
def put_order(new_order: NewOrder):
    print(repr(new_order))
    order_id = uuid.uuid4()
    order = new_order.dict()
    order['uuid'] = order_id
    order['status'] = OrderStatus.open
    orders[order_id] = order
    return order


# start uvicorn when executed:
if __name__ == "__main__":
    uvicorn.run("fast_lemon_api:app",
                host="127.0.0.1",
                port=8000,
                log_level="info")
