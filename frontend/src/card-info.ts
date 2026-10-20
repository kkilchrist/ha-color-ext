export const CARD_TYPE = "input-color-card";
// Tracks the integration version in manifest.json.
export const CARD_VERSION = "0.3.1";

export function registerCardInfo(): void {
  if (typeof window === "undefined") return;
  window.customCards = window.customCards || [];
  if (window.customCards.some((c) => c.type === CARD_TYPE)) return;
  window.customCards.push({
    type: CARD_TYPE,
    name: "Input Color Card",
    description:
      "Tap a swatch to pick a color, or toggle to White and set a kelvin temperature. Companion to the color integration.",
    preview: true,
    documentationURL: "https://github.com/kkilchrist/ha-color-ext#dashboard-card",
  });

  // Friendly console banner so users can confirm the resource loaded.
  /* eslint-disable no-console */
  console.info(
    `%c input-color-card %c v${CARD_VERSION} `,
    "color: white; background: #2d8cf0; font-weight: 700;",
    "color: #2d8cf0; background: white; font-weight: 700;"
  );
  /* eslint-enable no-console */
}
