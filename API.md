# API wiring

The console uses the Control Server as its only business API.

Uses:
- GET /v1/devices
- GET /v1/devices/{device_id}
- POST /v1/devices/{device_id}/commands
- GET,PUT /v1/devices/{device_id}/policies
- POST /v1/devices/{device_id}/sync/contacts
- POST /v1/devices/{device_id}/sync/media
- GET /v1/audit/events

Do not call devices or vendor gateways directly from the browser.