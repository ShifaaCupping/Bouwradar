# Bouwradar — v1

Nederlandse tracker voor LEGO-sets die eind 2026 uit productie gaan.

## Wat erin zit
- `index.html` — de hele site (mobile-first, geen build-stap). De setlijst staat bovenin het script als `SETS`.
- `functions/api/subscribe.js` — slaat aanmeldingen (e-mail + lijstje) op in Cloudflare D1.
- `schema.sql` — de databasetabel.

## Live zetten (Cloudflare Pages via GitHub)
1. Maak een nieuwe GitHub-repo en zet deze bestanden erin.
2. Cloudflare → Workers & Pages → Create → Pages → koppel de repo. Build command: leeg. Output directory: `/`.
3. Maak een D1-database: Workers & Pages → D1 → Create → naam `bouwradar`.
4. Open de database → Console → plak de inhoud van `schema.sql` → Execute.
5. Pages-project → Settings → Bindings → Add → D1 database → variabelenaam `DB` → kies `bouwradar`.
6. Opnieuw deployen. Klaar: het aanmeldformulier werkt nu.

Aanmeldingen bekijken: D1 → Console → `SELECT * FROM subscribers;`

## Voordat je promoot
- Zet een privacyverklaring online (welke data, waarom, hoe afmelden) — AVG.
- Meld je aan bij het bol partnerprogramma en vervang de bol-links door je affiliate-links. Doe hetzelfde bij Amazon.nl als je wilt.
- Controleer de stopdata: ze zijn verwachtingen en kunnen veranderen.
- Gebruik geen LEGO-logo of officiële productfoto's, en noem de site niet "LEGO-iets".
