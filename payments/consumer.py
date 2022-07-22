import time

from main import redis, Order

key = 'refund_order'
consumer_group = 'payment_group'

try:
    redis.xgroup_create(name=key, groupname=consumer_group)
except:
    print("Group already exists!!")

while True:
    try:
        results = redis.xreadgroup(groupname=consumer_group, consumername=key, streams={key: '>'})
        for result in results:
            obj = result[1][0][1]
            order = Order.get(obj['pk'])
            time.sleep(1)
            order.status = 'REFUNDED'
            order.save()
    except Exception as e:
        print(str(e))
    time.sleep(1)