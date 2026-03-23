# 🍅 KETCHUP PMS - Rova Edition
**Projekt Äppelskrutt | The Flagship Release**

En ultra-optimerad, lokalt körd PWA (Progressive Web App) designad exklusivt för att spåra kliniska medicin-protokoll (med fokus på Slinda/Drospirenon). Byggd för att leverera extrem prestanda, 100% integritet och ett "Ollat-för-speed" premium-gränssnitt som utmanar branschstandarden för moderna smartphones.

![Version](https://img.shields.io/badge/Version-5.0_Ultimate-e63946)
![Platform](https://img.shields.io/badge/Platform-iOS_%7C_Android_%7C_Web-black)
![Tech](https://img.shields.io/badge/Tech-React_%7C_Tailwind_%7C_PWA-blue)

## ✨ Flaggskeppsfunktioner

* 🏎️ **Extrem Prestanda (120Hz-redo):** Hårdvaruaccelererade (GPU) animationer, `useMemo`-optimerad React-rendering och raderad "overscroll" för en laggfri upplevelse.
* 💎 **Premium Glassmorphism & True Dark:** Djup OLED-svärta (`#030303`) kombinerat med dynamiska, frostade glaspaneler, glanseffekter ("shine") och mjuka pulserande skuggor.
* 📡 **100% Offline-First:** En robust Service Worker (`sw.js`) cachar hela ramverket lokalt. Appen startar blixtsnabbt och fungerar fullt ut i flygplansläge.
* 🔒 **Säker Lokal Lagring:** All känslig hälsodata sparas exklusivt på enhetens interna minne (`localStorage`). Ingen data lämnar någonsin telefonen.
* 📍 **Smart Geolokalisering & Taktil Haptik:** Registrerar diskret plats vid intag. Bekräftar inmatningar med kontextuell fysisk haptisk feedback (vibrationer).
* 🎉 **Micro-Interactions:** Belönar användaren med konfetti vid intagen dos och ger direkt visuell feedback på alla knapptryck (`active:scale`).
* 🧠 **Avancerad Heuristik & Kinetik:** Spåra dagsform (1-10), spotting och specifika PMS-symtom, vilket visualiseras i realtid via en inbyggd trendgraf (Recharts).

## 🛠️ Teknisk Stack
Appen är byggd som en modern "Zero-Build" React-app. Inga Node-servrar eller Webpack behövs – allt kompileras blixtsnabbt direkt i webbläsaren via CDN.
* **Core:** React 18, Babel (Standalone)
* **Styling:** Tailwind CSS (via CDN med custom config)
* **Ikoner & Visuals:** Lucide Icons, Canvas-Confetti
* **Data Visualisering:** Recharts
* **PWA:** Vanilla JavaScript Service Worker (Stale-while-revalidate)

## 🚀 Driftsättning (GitHub Pages)
1. Ladda upp `index.html`, `manifest.json` och `sw.js` till ditt repo (main branch).
2. Navigera till **Settings -> Pages** i GitHub.
3. Välj **Deploy from a branch** och ställ in på `main`. Spara.
4. Öppna länken i Safari (iOS) eller Chrome (Android).
5. Välj **"Lägg till på hemskärmen"** för att installera appen och låsa upp PWA-funktionerna.

---

## ⚠️ ROVA ENCRYPTION ENGINE (Admin Mode)
Appen innehåller en dold, matrix-inspirerad administratörsterminal för direkt insyn i databasen.

**Hur du öppnar portalen:**
1. I appens huvudvy, klicka **exakt 4 gånger** snabbt (inom 1.5 sekunder) på "🍅 KETCHUP"-logotypen (texten uppe till vänster).
2. Systemet bekräftar med en tung vibration och öppnar Terminal Mode.
3. **Passkey:** Ange `rova6666` för att dekryptera systemet.

**God Mode-verktyg:**
* **RAW_LOCALSTORAGE_DUMP:** Visar en snyggt formatterad JSON-sträng av de senaste loggarna direkt från enhetens minne.
* **NUKE DATABASE:** Möjlighet att oåterkalleligen radera all lokal patientdata (används för felsökning/nollställning).

---
*Designad och utvecklad av Rova Systems | 2026*
