import requests
import json
import time  # https://pbs.twimg.com/tweet_video_thumb/Emuy1VvW8AA-Lrg.jpg

from typing import Dict


class Constants:
    DEFAULT_NUM_TOKENS: int = 5
    DEFAULT_MAX_CREDITS: int = 100
    DEFAULT_MAX_TOKENS: int = 1000
    ORDER_COMPLETE_STATUS: str = "complete"
    ORDER_FAILED_STATUS: str = "failed"

    # Is it disgusting that these are not consistent? Yes.
    ORDER_COMPLETE_STATUS_MESSAGE: str = "Order complete"
    INSUFFICIENT_CREDITS_STATUS_MESSAGE: str = (
        "User has insufficient funds for purchase."
    )
    INSUFFICIENT_TOKENS_STATUS_MESSAGE: str = "Insufficient tokens to purchase."
    ORDER_FORCED_FAILURE_STATUS_MESSAGE: str = "Failure in order service!"
    PAYMENT_FORCED_FAILURE_STATUS_MESSAGE: str = "Failure in payment service!"
    INVENTORY_FORCED_FAILURE_STATUS_MESSAGE: str = "Failure in inventory service!"
    DELIVERY_FORCED_FAILURE_STATUS_MESSAGE: str = "Failure in delivery service!"


class ResponseCodes:
    CREATED = 201
    OK = 200


class URLs:
    CREATE_ORDER = "create-order"
    GET_ORDER = "get-order"


class NTRTestSuite:
    def __init__(self):
        self.user_id = 1
        self.order_id = 1

    def increment_ids(self):
        self.user_id += 1
        self.order_id += 1

    def GET(self, url: str, params: Dict):
        response = requests.get(f"http://localhost/{url}", params=params)
        return response

    def POST(self, url: str, data: Dict):
        response = requests.post(f"http://localhost/{url}", json=data)
        return response

    def create_order(
        self,
        num_tokens: int,
        order_fail=False,
        payment_fail=False,
        inventory_fail=False,
        delivery_fail=False,
    ):
        data = {
            "num_tokens": num_tokens,
            "order_fail": order_fail,
            "payment_fail": payment_fail,
            "inventory_fail": inventory_fail,
            "delivery_fail": delivery_fail,
        }

        response = self.POST(URLs.CREATE_ORDER, data)
        content = json.loads(response.content)

        assert response.status_code == ResponseCodes.CREATED
        assert content["message"] == "Order created"

        return response

    def get_order(self, order_id: int):
        data = {"order_id": order_id}
        response = self.GET(URLs.GET_ORDER, params=data)
        return response

    def verify_order_information(
        self,
        order_obj: Dict,
        user_id: int,
        order_id: int,
        num_tokens: int,
        status: str,
        status_message: str,
    ) -> None:
        assert order_obj["id"] == order_id
        assert order_obj["user_id"] == user_id
        assert order_obj["num_tokens"] == num_tokens
        assert order_obj["status"] == status
        assert order_obj["status_message"] == status_message

    def test_create_order(
        self,
        num_tokens: int,
        expected_status: str = Constants.ORDER_COMPLETE_STATUS,
        expected_status_message: str = Constants.ORDER_COMPLETE_STATUS_MESSAGE,
        order_fail=False,
        payment_fail=False,
        inventory_fail=False,
        delivery_fail=False,
    ):
        self.create_order(
            num_tokens=num_tokens,
            order_fail=order_fail,
            payment_fail=payment_fail,
            inventory_fail=inventory_fail,
            delivery_fail=delivery_fail,
        )

        time.sleep(1)  # sleepy time

        response = self.get_order(order_id=self.order_id)
        order_obj = json.loads(response.content)

        self.verify_order_information(
            order_obj=order_obj,
            user_id=self.user_id,
            order_id=self.order_id,
            num_tokens=num_tokens,
            status=expected_status,
            status_message=expected_status_message,
        )

        self.increment_ids()

    def test_create_order_with_insufficient_credits(self):
        num_tokens = Constants.DEFAULT_MAX_CREDITS + 1
        self.test_create_order(
            num_tokens=num_tokens,
            expected_status=Constants.ORDER_FAILED_STATUS,
            expected_status_message=Constants.INSUFFICIENT_CREDITS_STATUS_MESSAGE,
        )

    def test_create_order_with_insufficient_tokens(self):
        num_tokens = Constants.DEFAULT_MAX_TOKENS + 1
        self.test_create_order(
            num_tokens=num_tokens,
            expected_status=Constants.ORDER_FAILED_STATUS,
            expected_status_message=Constants.INSUFFICIENT_TOKENS_STATUS_MESSAGE,
        )

    def test_create_order_with_order_service_failure(self):
        num_tokens = Constants.DEFAULT_NUM_TOKENS
        self.test_create_order(
            num_tokens=num_tokens,
            expected_status=Constants.ORDER_FAILED_STATUS,
            expected_status_message=Constants.ORDER_FORCED_FAILURE_STATUS_MESSAGE,
            order_fail=True,
        )

    def test_create_order_with_payment_service_failure(self):
        num_tokens = Constants.DEFAULT_NUM_TOKENS
        self.test_create_order(
            num_tokens=num_tokens,
            expected_status=Constants.ORDER_FAILED_STATUS,
            expected_status_message=Constants.PAYMENT_FORCED_FAILURE_STATUS_MESSAGE,
            payment_fail=True,
        )

    def test_create_order_with_inventory_service_failure(self):
        num_tokens = Constants.DEFAULT_NUM_TOKENS
        self.test_create_order(
            num_tokens=num_tokens,
            expected_status=Constants.ORDER_FAILED_STATUS,
            expected_status_message=Constants.INVENTORY_FORCED_FAILURE_STATUS_MESSAGE,
            inventory_fail=True,
        )

    def test_create_order_with_delivery_service_failure(self):
        num_tokens = Constants.DEFAULT_NUM_TOKENS
        self.test_create_order(
            num_tokens=num_tokens,
            expected_status=Constants.ORDER_FAILED_STATUS,
            expected_status_message=Constants.DELIVERY_FORCED_FAILURE_STATUS_MESSAGE,
            delivery_fail=True,
        )


nts = NTRTestSuite()
nts.test_create_order(num_tokens=Constants.DEFAULT_NUM_TOKENS)
nts.test_create_order_with_insufficient_credits()
nts.test_create_order_with_order_service_failure()
nts.test_create_order_with_payment_service_failure()
nts.test_create_order_with_inventory_service_failure()
nts.test_create_order_with_delivery_service_failure()
