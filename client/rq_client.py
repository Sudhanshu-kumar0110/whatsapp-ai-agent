from redis import Redis
from rq import Queue

connectin = Redis(
    host = "localhost",
    port = 6379 
)

queue = Queue(connection=connectin)