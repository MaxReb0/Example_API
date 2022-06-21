from .health import health_blueprint
from .loan import loan_blueprint
from .payment import payment_blueprint
from .refund import refund_blueprint

blueprints = (health_blueprint, loan_blueprint, payment_blueprint, refund_blueprint)