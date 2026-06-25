# Daily Commute Notifier

An automation that runs every morning. Texts me (using email-to-SMS forwarding) an overview of the weather for the day and what time my bus is expected to arrive for my daily morning commute for summer 2026.

Tech stack:
- GitHub Actions for running script every morning at the same time
- OpenMeteo API for retrieving weather info
- MBTA V3 API for retrieving transit info
- Python SMTP server and email libraries for using GMail + Google app password to programatically send email to a receipient.

Other potential future expansions:
- Avoiding sending notifications on scheduled holidays and other days that I'm not working
- Comparison of multiple commute options to see which is the fastest
