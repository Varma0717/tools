# utils/payment.py
# Suppress pkg_resources deprecation warnings from razorpay
import warnings

warnings.filterwarnings(
    "ignore", message="pkg_resources is deprecated as an API.*", category=UserWarning
)

import razorpay

razorpay_client = razorpay.Client(auth=("rzp_test_yourkey", "your_secret"))


def create_order(amount):
    return razorpay_client.order.create(
        {"amount": int(amount * 100), "currency": "INR", "payment_capture": 1}
    )
