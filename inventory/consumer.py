import time

from main import redis, Product

key = 'order_completed'
consumer_group = 'inventory_group'

try:
    redis.xgroup_create(name=key, groupname=consumer_group)
except:
    print("Group already exists!!")

while True:
    try:
        results = redis.xreadgroup(groupname=consumer_group, consumername=key, streams={key: '>'})
        for result in results:
            obj = result[1][0][1]
            try:
                product = Product.get(obj['product_id'])
                if product.avail_qty < int(obj['qty_purchased']):
                    x = 1 / 0
                product.avail_qty -= int(obj['qty_purchased'])
                product.save()
            except:
                redis.xadd('refund_order', obj, '*')
    except Exception as e:
        print(str(e))
    time.sleep(1)