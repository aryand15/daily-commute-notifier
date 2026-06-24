# Morning Commute Notifier

An automation that runs every morning. Texts me an overview of the weather for the day and in the future will also tell me what time my bus is expected to arrive for my daily morning commute for summer 2026.

Tech stack:
- GitHub Actions for running script every morning at the same time
- OpenMeteo API for retrieving weather info
- MBTA V3 API for retrieving transit info (coming in the future)
- Python SMTP server and email libraries to facilitate email-to-SMS forwarding

Other future fixes:
- Avoiding sending notifications on scheduled holidays and the days in August when I'm not working
