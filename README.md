# Strava commute namer

This is a little script that runs on AWS Lambda to name and tag my commutes properly
on [Strava](https://www.strava.com/).

## Environment variables

- `STRAVA_API_TOKEN`: an API token with write access to your Strava account

## Development

```
pip install -r requirements.txt
lambda invoke
```

## Deployment

Copy and paste it into the AWS Lambda web interface.

### Scheduling

Use CloudWatch Events to trigger it periodically.
