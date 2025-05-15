# Data Annotation Watcher

This app watches [dataannotation.tech](https://www.dataannotation.tech) for new tasks and notifies you via WhatsApp using Twilio.

## Setup

### Secrets to Configure (in GitHub)

| Secret Name        | Description                      |
|--------------------|----------------------------------|
| `TWILIO_SID`       | Twilio SID                       |
| `TWILIO_AUTH_TOKEN`| Twilio Auth Token                |
| `TWILIO_FROM`      | WhatsApp `from` (Twilio sandbox) |
| `TWILIO_TO`        | Your WhatsApp number             |
| `SESSION_COOKIE`   | Full session cookie string       |
| `ANNOTATION_URL`   | Task page URL                    |

### How to get `SESSION_COOKIE`

1. Log in to `https://www.dataannotation.tech`.
2. Open Developer Tools > Network.
3. Refresh the page and click any request to `/tasks`.
4. Copy the full value of the `cookie` request header.
5. Paste this into GitHub Secrets under `SESSION_COOKIE`.

**Example value:**
_secure_session=abcd123; other_cookie=xyz;


Don't include the `Cookie:` part — only the raw value.

## Strategy for Keeping the Cookie Fresh

- Cookies expire periodically or when you log out.
- If your GitHub Action fails with a 302 or 403 error, your session has likely expired.
- To refresh:
  - Log back in
  - Repeat the copy-paste step for the cookie
  - Update the GitHub Secret `SESSION_COOKIE`

## Deployment

1. Push this repo to GitHub
2. Set all required secrets under **Settings > Secrets and Variables > Actions**
3. The watcher will run every 5 minutes via GitHub Actions

## Next

- Replace `.task-item` in `watcher.py` with the actual selector once confirmed.
