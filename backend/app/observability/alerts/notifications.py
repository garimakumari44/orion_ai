"""
Notification Service

Routes alerts to:
- Console
- Slack
- Email
- Webhooks
- PagerDuty

Currently contains extensible adapters.
"""

from datetime import datetime
from typing import Any



class NotificationChannel:
    """
    Base notification interface.
    """


    def send(
        self,
        alert: Any
    ):
        raise NotImplementedError




class ConsoleNotifier(NotificationChannel):
    """
    Prints alerts locally.
    """


    def send(
        self,
        alert: Any
    ):

        print(
            "\n🚨 ALERT"
        )

        print(
            f"Severity: {alert.severity}"
        )

        print(
            f"Message: {alert.message}"
        )

        print(
            f"Time: {datetime.utcnow()}"
        )



class WebhookNotifier(NotificationChannel):
    """
    Placeholder webhook notifier.

    Later connect:
    - Slack
    - Discord
    - Teams
    - PagerDuty
    """

    def __init__(
        self,
        webhook_url: str
    ):

        self.webhook_url = webhook_url



    def send(
        self,
        alert: Any
    ):

        payload = {

            "severity": alert.severity,

            "message": alert.message,

            "timestamp": (
                datetime.utcnow()
                .isoformat()
            )

        }


        # HTTP request will be added later
        print(
            "Sending webhook:",
            payload
        )



class NotificationManager:
    """
    Central alert notification router.
    """


    def __init__(self):

        self.channels = []



    def register(
        self,
        channel: NotificationChannel
    ):

        self.channels.append(
            channel
        )



    def notify(
        self,
        alert: Any
    ):


        for channel in self.channels:

            try:

                channel.send(
                    alert
                )

            except Exception as e:

                print(
                    "Notification failed:",
                    e
                )