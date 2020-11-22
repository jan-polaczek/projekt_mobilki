from redis import Redis
import os

db = Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'))
db.flushall()
admin_data = {
    'username': 'admin',
    'firstname': 'Pan',
    'lastname': 'Admin',
    'password': '$2y$12$m8iMhkB8nsNjA0XcAK4u5.BH66ws.Nf1o4ahC1pY61Fq.wuNqjN1i',
    'addres': 'Pałac Adminowski'
}

package_id = '1c2d39a5-1317-41a3-8996-9a354f0383b7'
package = {
    'id': package_id,
    'receiver': 'Kolega Pana Admina',
    'cell': 'WAW-57',
    'size': '5kg',
    'user': 'admin'
}
db.hmset("user:admin", admin_data)
db.lpush("packages:admin", package_id)
db.hmset("package:" + package_id, package)
