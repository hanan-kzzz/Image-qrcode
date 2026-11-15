# ScanLink V1 — Image to Scannable QR

A responsive browser app that embeds a QR code into an uploaded image. Scanning the QR code with a phone camera opens the assigned website.

## Run
1. Open `index.html` in a modern browser, or deploy this repository as a static site.
2. Internet access is needed to load QRCode.js from cdnjs.

## Use
1. Upload a JPG, PNG or WebP image.
2. Enter a complete URL beginning with `https://`.
3. Generate the scannable image.
4. Download the PNG and test it with a phone camera.

## V1 limitations
- Uses a visible QR code, not invisible image recognition.
- QR code is placed in the lower-right corner with a white quiet-zone border.
- No accounts, link management, or scan analytics in V1.
