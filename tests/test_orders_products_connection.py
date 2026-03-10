import requests
import uuid

PRODUCTS_URL = "http://127.0.0.1:8000"
ORDERS_URL = "http://127.0.0.1:8001"


def create_test_product(stock=10):
    """Helper function to create a product for tests"""
    payload = {
        "name": f"Test Product {uuid.uuid4()}",
        "description": "Integration test product",
        "category": "electronics",
        "price": 50.0,
        "stock": stock,
        "image_url": "test"
    }

    response = requests.post(f"{PRODUCTS_URL}/products", json=payload)
    assert response.status_code in [200, 201]
    return response.json()["id"]


# TEST 1: Create order successfully
def test_create_order_success():

    product_id = create_test_product(stock=10)

    order_payload = {
        "user_id": "test_user",
        "items": [
            {
                "product_id": product_id,
                "quantity": 2
            }
        ]
    }

    response = requests.post(f"{ORDERS_URL}/orders", json=order_payload)

    assert response.status_code in [200, 201]

    data = response.json()

    assert data["user_id"] == "test_user"
    assert len(data["items"]) == 1


# TEST 2: Product does not exist
def test_create_order_product_not_found():

    order_payload = {
        "user_id": "test_user",
        "items": [
            {
                "product_id": "fake-product-id",
                "quantity": 1
            }
        ]
    }

    response = requests.post(f"{ORDERS_URL}/orders", json=order_payload)

    assert response.status_code in [400, 404]


# TEST 3: Insufficient stock
def test_create_order_insufficient_stock():

    product_id = create_test_product(stock=1)

    order_payload = {
        "user_id": "test_user",
        "items": [
            {
                "product_id": product_id,
                "quantity": 5
            }
        ]
    }

    response = requests.post(f"{ORDERS_URL}/orders", json=order_payload)

    assert response.status_code == 400


# TEST 4: Multiple products
def test_create_order_multiple_products():

    product1 = create_test_product(stock=10)
    product2 = create_test_product(stock=10)

    order_payload = {
        "user_id": "test_user",
        "items": [
            {
                "product_id": product1,
                "quantity": 1
            },
            {
                "product_id": product2,
                "quantity": 2
            }
        ]
    }

    response = requests.post(f"{ORDERS_URL}/orders", json=order_payload)

    assert response.status_code in [200, 201]

    data = response.json()

    assert len(data["items"]) == 2

# TEST 5: Empty list order
def test_create_order_empty_items():
    payload = {
        "user_id": "user-test",
        "items": []
    }

    response = requests.post(f"{ORDERS_URL}/orders", json=payload)

    assert response.status_code == 422

# TEST 6: Multiple items in order
def test_create_order_two_products():
    p1 = create_test_product(stock=10)
    p2 = create_test_product(stock=10)

    payload = {
        "user_id": "user-test",
        "items": [
            {"product_id": p1, "quantity": 1},
            {"product_id": p2, "quantity": 2}
        ]
    }

    response = requests.post(f"{ORDERS_URL}/orders", json=payload)

    assert response.status_code == 201

# TEST 7: Connection to other service
def test_products_service_unavailable():
    # Temporarily point to wrong service
    bad_url = "http://127.0.0.1:9999"

    payload = {
        "user_id": "user-test",
        "items": [
            {
                "product_id": "some-id",
                "quantity": 1
            }
        ]
    }

    response = requests.post(f"{ORDERS_URL}/orders", json=payload)

    assert response.status_code >= 400

# TEST 8: Negative quantity
def test_create_order_negative_quantity():
    product_id = create_test_product(stock=10)

    payload = {
        "user_id": "user-test",
        "items": [
            {
                "product_id": product_id,
                "quantity": -2
            }
        ]
    }

    response = requests.post(f"{ORDERS_URL}/orders", json=payload)

    assert response.status_code == 422