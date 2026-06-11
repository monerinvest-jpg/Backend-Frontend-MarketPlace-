from app.tasks.celery_app import celery_app


@celery_app.task
def simulate_delivery_progress(order_id: int, current_status: str) -> dict:
    transitions = {
        "shipped": "delivered",
        "delivered": "completed",
    }
    return {"order_id": order_id, "next_status": transitions.get(current_status, current_status)}
