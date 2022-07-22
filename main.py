import time

from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from fastapi.background import BackgroundTasks
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

redis = get_redis_connection(
    host="",
    port=12345,
    password="",
    decode_responses=True
)

class Order(HashModel):
    product_id: str
    price: float
    gst: float
    total_price: float
    qty_purchased: int
    status: str

    class Meta:
        database = redis


@app.get('/orders')
def all_orders():
    orders = []
    all_pks = Order.all_pks()
    for pk in all_pks:
        orders.append(Order.get(pk))
    return orders

@app.get('/orders/{pk}')
def get_order(pk: str):
    return Order.get(pk)

@app.post('/create_order')
async def create_order(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    req_url = "http://localhost:8000/product/{}".format(data['pk'])
    product = requests.get(req_url).json()

    order = Order(
        product_id=product['pk'],
        price=product['price'],
        gst=0.2 * product['price'] * data['qty_purchased'],
        total_price=1.2 * product['price'] * data['qty_purchased'],
        qty_purchased=data['qty_purchased'],
        status='PENDING'
    )
    order.save()

    background_tasks.add_task(order_completed, order)
    return order

def order_completed(order: Order):
    time.sleep(5)
    order.status = 'COMPLETED'
    order.save()
    redis.xadd('order_completed', order.dict(), '*')

@app.delete('/delete_order/{pk}')
def delete_order(pk: str):
    return Order.delete(pk)