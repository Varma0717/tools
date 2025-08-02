# utils/payment.py
import razorpay

razorpay_client = razorpay.Client(auth=("rzp_test_yourkey", "your_secret"))

def create_order(amount):
    return razorpay_client.order.create({
        "amount": int(amount * 100),
        "currency": "INR",
        "payment_capture": 1
    })
