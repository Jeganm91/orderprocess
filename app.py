import logging
import threading
import time
import uuid
from queue import Queue
from flask import Flask, jsonify, request

app = Flask(__name__)

# --------------------------------------------------------
# Logging Configuration
# --------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger("order-processing-service")

# --------------------------------------------------------
# In-Memory Queue
# --------------------------------------------------------

order_queue = Queue()

# --------------------------------------------------------
# Metrics
# --------------------------------------------------------

processed_orders = 0
failed_orders = 0

# --------------------------------------------------------
# Background Worker
# --------------------------------------------------------

def process_orders():
    global processed_orders
    global failed_orders

    while True:
        try:
            if not order_queue.empty():
                order = order_queue.get()

                logger.info(f"Processing Order: {order['order_id']}")

                # Simulate processing workload
                time.sleep(5)

                processed_orders += 1

                logger.info(
                    f"Completed Order: {order['order_id']}"
                )

                order_queue.task_done()

            else:
                time.sleep(1)

        except Exception as ex:
            failed_orders += 1
            logger.error(f"Order Processing Failed: {str(ex)}")

# --------------------------------------------------------
# Start Worker Thread
# --------------------------------------------------------

worker_thread = threading.Thread(
    target=process_orders,
    daemon=True
)

worker_thread.start()

# --------------------------------------------------------
# Root Endpoint
# --------------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "Order Processing API",
        "status": "Running",
        "version": "1.0.0"
    })

# --------------------------------------------------------
# Health Check
# --------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "Healthy",
        "queue_depth": order_queue.qsize(),
        "processed_orders": processed_orders,
        "failed_orders": failed_orders
    })

# --------------------------------------------------------
# Metrics Endpoint
# --------------------------------------------------------

@app.route("/metrics", methods=["GET"])
def metrics():
    return jsonify({
        "queue_depth": order_queue.qsize(),
        "processed_orders": processed_orders,
        "failed_orders": failed_orders,
        "active_threads": threading.active_count()
    })

# --------------------------------------------------------
# Add Orders Endpoint
# --------------------------------------------------------

@app.route("/orders", methods=["POST"])
def add_orders():

    try:
        payload = request.json

        order_count = payload.get("count", 1)

        created_orders = []

        for _ in range(order_count):

            order = {
                "order_id": str(uuid.uuid4()),
                "created_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Queued"
            }

            order_queue.put(order)

            created_orders.append(order)

        logger.info(f"{order_count} Orders Added")

        return jsonify({
            "message": "Orders Added Successfully",
            "orders_added": order_count,
            "queue_depth": order_queue.qsize(),
            "sample_orders": created_orders[:3]
        }), 201

    except Exception as ex:

        logger.error(str(ex))

        return jsonify({
            "error": str(ex)
        }), 500

# --------------------------------------------------------
# Queue Status Endpoint
# --------------------------------------------------------

@app.route("/queue", methods=["GET"])
def queue_status():

    return jsonify({
        "queue_depth": order_queue.qsize(),
        "processed_orders": processed_orders,
        "failed_orders": failed_orders
    })

# --------------------------------------------------------
# Clear Queue Endpoint
# --------------------------------------------------------

@app.route("/queue/clear", methods=["DELETE"])
def clear_queue():

    global order_queue

    cleared = order_queue.qsize()

    order_queue = Queue()

    logger.warning("Queue Cleared")

    return jsonify({
        "message": "Queue Cleared Successfully",
        "messages_removed": cleared
    })

# --------------------------------------------------------
# Startup
# --------------------------------------------------------

if __name__ == "__main__":

    logger.info("Starting Order Processing API")

    app.run(
        host="0.0.0.0",
        port=8000
    )
