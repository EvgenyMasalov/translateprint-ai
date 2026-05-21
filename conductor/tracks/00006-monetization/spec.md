# Specification: MVP Monetization

## Goal
Implement a "fake" monetization system for the MVP that provides a realistic user experience and can be easily converted to a real payment gateway during deployment.

## Requirements
1.  **Donate Button:**
    -   Location: Top header of the Editor page (`index.html`).
    -   Visibility: Only visible to authorized users.
    -   Style: Modern, "clay" style to match the existing UI.
2.  **Monetization Modal:**
    -   Triggered by the Donate button.
    -   Displays tiered support options (e.g., Supporter, Artist, Label).
    -   Realistic pricing and descriptions.
    -   "Payment" process: A fake successful payment experience with a thank-you message.
3.  **Realistic Architecture:**
    -   Use a placeholder endpoint in the backend for "processing" payments.
    -   Store "Premium" status in the database (even if just a flag).

## UI/UX
-   The button should be eye-catching but non-intrusive.
-   The modal should look trustworthy and professional.
