from redis import Redis, from_url, exceptions
import os


class RedisDAO:
    def connect(self):
        if os.environ.get('REDIS_URL'):
            return from_url(os.environ.get('REDIS_URL'))
        else:
            return Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'), decode_responses=True, charset="utf-8")

    def test_database(self):
        return self.db.dbsize() > 0

    def __init__(self):
        try:
            self.db = self.connect()
            if not self.test_database():
                print(f"Initiating database")
                import db.init_redis
            print("Connected to Redis")
        except exceptions.ConnectionError:
            print('Failed to connect to database')
            quit()

    def register(self, user_data):
        username = user_data['username']
        self.db.hmset("user:" + username, user_data)

    def check_username(self, username):
        user = self.db.hgetall("user:" + username)
        res = 'unavailable' if user else 'available'
        return {username: res}

    def get_username(self, sid):
        username = self.db.hget("session:" + sid, "username")
        return username

    def get_current_user(self, sid):
        username = self.get_username(sid)
        user = self.db.hgetall("user:" + username)
        return user

    def get_password(self, username):
        password = self.db.hget("user:" + username, 'password')
        return password

    def set_session(self, sid, username):
        self.db.hset("session:" + sid, "username", username)

    def delete_session(self, sid):
        self.db.delete("session:" + sid)

    def add_post(self, username, post):
        self.db.lpush("posts:" + username, post)

    def get_posts(self, username):
        posts = self.db.lrange("posts:" + username, 0, 3)
        if len(posts) == 0:
            return ["(nie masz postów)"]
        return posts

    def get_post(self, username, index):
        post = self.db.lindex("posts:" + username, index)
        return post

    def create_package(self, username, package):
        package['user'] = username
        self.db.lpush("packages:" + username, package['id'])
        self.db.hmset("package:" + package['id'], package)

    def delete_package(self, package_id):
        username = self.db.hget("package:" + package_id, 'user')
        self.db.lrem("packages:" + username, 0, package_id)
        self.db.delete("package:" + package_id)

    def get_packages(self, username):
        package_ids = self.db.lrange("packages:" + username, 0, -1)
        return [self.db.hgetall("package:" + package_id) for package_id in package_ids]
