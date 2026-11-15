# ScanLink V1 — Invisible image recognition

ScanLink recognises registered photographs using ORB visual features (OpenCV). The original photo remains unchanged: no QR code, watermark, or hidden pixel payload is added. A visitor opens ScanLink, uses its camera scanner, and the server matches the image to its registered destination URL.

## Architecture
- FastAPI + OpenCV ORB matching on Render
- Supabase Postgres stores feature descriptors and destination URLs
- Admin registration protected by a server-side token
- Browser receiver submits camera frames to the recognition API

## Setup
1. Run `schema.sql` in the Supabase SQL Editor once the project database is available.
2. Set Render environment variables: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and `ADMIN_TOKEN`.
3. Deploy from `main` using `render.yaml`.
4. Open the site, register an image and its destination in Admin, then scan it from another device.

Never put the Supabase service-role key in browser code or GitHub.

## Limitations
- The phone's default camera app cannot identify these images. Users must open the ScanLink website and grant camera access.
- This V1 is a visual-matching prototype, not cryptographic proof of image authenticity.
- Similar-looking images, crops, low light, motion blur, and strong perspective changes can reduce recognition accuracy.
- Do not use this prototype for payments, identity checks, access control, or safety-critical decisions.
