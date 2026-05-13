from django.apps import AppConfig


class BillingConfig(AppConfig):
    name = "billing"

    def ready(self):
        # Import the signals module to ensure signal handlers are registered
        import billing.signals
