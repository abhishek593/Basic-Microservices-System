from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

redis = get_redis_connection(
    host="",
    port=12346,
    password="",
    decode_responses=True
)

class Product(HashModel):
    name: str
    price: float
    avail_qty: int

    class Meta:
        database = redis


@app.get('/products')
def all_products():
    products = []
    all_pks = Product.all_pks()
    for pk in all_pks:
        products.append(Product.get(pk))
    return products

@app.get('/product/{pk}')
def get_product(pk: str):
    return Product.get(pk)

@app.post('/create_product')
def create_product(product: Product):
    return product.save()

@app.delete('/delete_product/{pk}')
def delete_product(pk: str):
    return Product.delete(pk)