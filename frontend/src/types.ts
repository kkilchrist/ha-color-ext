// Minimal subset of HA / Lovelace types we need.
// Kept local to avoid pulling in custom-card-helpers as a dependency for v1.

export interface HassEntityAttributeBase {
  friendly_name?: string;
  icon?: string;
  [key: string]: unknown;
}

export interface InputColorAttributes extends HassEntityAttributeBase {
  kind?: "chromatic" | "white";
  color_temp_kelvin?: number | null;
  rgb_color?: [number, number, number] | null;
  hs_color?: [number, number] | null;
  xy_color?: [number, number] | null;
}

export interface HassEntity {
  entity_id: string;
  state: string;
  attributes: HassEntityAttributeBase | InputColorAttributes;
  last_changed?: string;
  last_updated?: string;
}

export interface HomeAssistant {
  states: { [entity_id: string]: HassEntity };
  callService(
    domain: string,
    service: string,
    serviceData?: Record<string, unknown>,
    target?: { entity_id?: string | string[] }
  ): Promise<unknown>;
  themes?: { darkMode?: boolean };
  language?: string;
}

export interface LovelaceCardConfig {
  type: string;
  [key: string]: unknown;
}

export interface InputColorCardConfig extends LovelaceCardConfig {
  entity: string;
  name?: string;
}

export interface LovelaceCard extends HTMLElement {
  hass?: HomeAssistant;
  setConfig(config: LovelaceCardConfig): void;
  getCardSize?(): number | Promise<number>;
}

declare global {
  interface Window {
    customCards?: Array<{
      type: string;
      name: string;
      description?: string;
      preview?: boolean;
      documentationURL?: string;
    }>;
  }
}
