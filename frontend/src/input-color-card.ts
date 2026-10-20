import { LitElement, html, css, PropertyValues, TemplateResult, nothing } from "lit";
import { property, state } from "lit/decorators.js";
import { CARD_TYPE, registerCardInfo } from "./card-info";
import type {
  HomeAssistant,
  HassEntity,
  InputColorAttributes,
  InputColorCardConfig,
} from "./types";

type Kind = "chromatic" | "white";

const HEX_RE = /^#([0-9a-fA-F]{6})$/;
const DEFAULT_KELVIN = 4000;
const MIN_KELVIN = 2000;
const MAX_KELVIN = 6500;
const KELVIN_STEP = 100;
const DEBOUNCE_MS = 150;

export class InputColorCard extends LitElement {
  @property({ attribute: false }) public hass?: HomeAssistant;

  @state() private _config?: InputColorCardConfig;

  // Locally-staged UI state, allows smooth dragging before debounced commit.
  @state() private _localHex?: string;
  @state() private _localKelvin?: number;
  @state() private _localKind?: Kind;

  private _commitTimer: number | undefined;

  public setConfig(config: InputColorCardConfig): void {
    if (!config || typeof config !== "object") {
      throw new Error("Invalid configuration");
    }
    if (!config.entity || typeof config.entity !== "string") {
      throw new Error("You must specify an `entity` (an color entity).");
    }
    if (!config.entity.startsWith("color.")) {
      throw new Error(
        `Entity must be from the color domain. Got: ${config.entity}`
      );
    }
    this._config = { ...config };
    // Clear any stale local state when reconfigured.
    this._localHex = undefined;
    this._localKelvin = undefined;
    this._localKind = undefined;
  }

  public getCardSize(): number {
    return 3;
  }

  public static getStubConfig(): Partial<InputColorCardConfig> {
    return { entity: "" };
  }

  protected shouldUpdate(changedProps: PropertyValues): boolean {
    if (
      changedProps.has("_config") ||
      changedProps.has("_localHex") ||
      changedProps.has("_localKelvin") ||
      changedProps.has("_localKind")
    ) {
      return true;
    }
    if (changedProps.has("hass")) {
      const oldHass = changedProps.get("hass") as HomeAssistant | undefined;
      const entityId = this._config?.entity;
      if (!entityId) return true;
      const oldState = oldHass?.states?.[entityId];
      const newState = this.hass?.states?.[entityId];
      return oldState !== newState;
    }
    return false;
  }

  private _getEntityState(): HassEntity | undefined {
    if (!this.hass || !this._config?.entity) return undefined;
    return this.hass.states[this._config.entity];
  }

  private _currentKind(): Kind {
    if (this._localKind) return this._localKind;
    const attrs = this._getEntityState()?.attributes as
      | InputColorAttributes
      | undefined;
    return attrs?.kind === "white" ? "white" : "chromatic";
  }

  private _currentHex(): string {
    if (this._localHex) return this._localHex;
    const state = this._getEntityState();
    const raw = state?.state ?? "";
    return HEX_RE.test(raw) ? raw.toUpperCase() : "#FFFFFF";
  }

  private _currentKelvin(): number {
    if (this._localKelvin != null) return this._localKelvin;
    const attrs = this._getEntityState()?.attributes as
      | InputColorAttributes
      | undefined;
    const k = attrs?.color_temp_kelvin;
    if (typeof k === "number" && k >= MIN_KELVIN && k <= MAX_KELVIN) {
      return k;
    }
    return DEFAULT_KELVIN;
  }

  private _scheduleCommit(data: Record<string, unknown>): void {
    if (this._commitTimer) {
      window.clearTimeout(this._commitTimer);
    }
    this._commitTimer = window.setTimeout(() => {
      this._commitTimer = undefined;
      this._callSetColor(data);
    }, DEBOUNCE_MS);
  }

  private async _callSetColor(data: Record<string, unknown>): Promise<void> {
    if (!this.hass || !this._config?.entity) return;
    try {
      await this.hass.callService("color", "set_color", data, {
        entity_id: this._config.entity,
      });
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error("[input-color-card] set_color failed:", err);
    }
  }

  private _onKindChange(kind: Kind): void {
    if (kind === this._currentKind()) return;
    this._localKind = kind;
    if (kind === "white") {
      const k = this._currentKelvin();
      this._localKelvin = k;
      this._scheduleCommit({ color_temp_kelvin: k });
    } else {
      const hex = this._currentHex();
      this._localHex = hex;
      this._scheduleCommit({ hex_value: hex });
    }
  }

  private _onColorInput(ev: Event): void {
    const target = ev.target as HTMLInputElement;
    const value = (target.value || "").toUpperCase();
    if (!HEX_RE.test(value)) return;
    this._localHex = value;
    this._localKind = "chromatic";
    this._scheduleCommit({ hex_value: value });
  }

  private _onKelvinInput(ev: Event): void {
    const target = ev.target as HTMLInputElement;
    const k = parseInt(target.value, 10);
    if (Number.isNaN(k)) return;
    this._localKelvin = k;
    this._localKind = "white";
    this._scheduleCommit({ color_temp_kelvin: k });
  }

  private _onSwatchClick(): void {
    const input =
      this.renderRoot.querySelector<HTMLInputElement>("input#color-picker");
    input?.click();
  }

  private _onSwatchKeydown(ev: KeyboardEvent): void {
    if (ev.key === "Enter" || ev.key === " ") {
      ev.preventDefault();
      this._onSwatchClick();
    }
  }

  protected render(): TemplateResult | typeof nothing {
    if (!this._config || !this.hass) return nothing;
    const entity = this._config.entity;
    const state = this._getEntityState();

    if (!state) {
      return html`
        <ha-card>
          <div class="warning">
            Entity not found: <code>${entity}</code>
          </div>
        </ha-card>
      `;
    }

    const kind = this._currentKind();
    const hex = this._currentHex();
    const kelvin = this._currentKelvin();
    const name =
      this._config.name ||
      (state.attributes.friendly_name as string | undefined) ||
      entity;

    return html`
      <ha-card>
        <div class="header">
          <div class="title">${name}</div>
          <div class="toggle" role="tablist" aria-label="Color mode">
            <button
              role="tab"
              type="button"
              aria-selected=${kind === "chromatic"}
              class=${kind === "chromatic" ? "active" : ""}
              @click=${() => this._onKindChange("chromatic")}
            >
              Color
            </button>
            <button
              role="tab"
              type="button"
              aria-selected=${kind === "white"}
              class=${kind === "white" ? "active" : ""}
              @click=${() => this._onKindChange("white")}
            >
              White
            </button>
          </div>
        </div>

        <div class="body">
          ${kind === "chromatic"
            ? this._renderColor(hex)
            : this._renderWhite(kelvin)}
        </div>
      </ha-card>
    `;
  }

  private _renderColor(hex: string): TemplateResult {
    return html`
      <div class="color-row">
        <div
          class="swatch"
          role="button"
          tabindex="0"
          aria-label="Open color picker"
          style=${`background:${hex}`}
          @click=${this._onSwatchClick}
          @keydown=${this._onSwatchKeydown}
        ></div>
        <label class="hex-label">
          <span>${hex}</span>
          <input
            id="color-picker"
            type="color"
            .value=${hex}
            @input=${this._onColorInput}
            @change=${this._onColorInput}
          />
        </label>
      </div>
    `;
  }

  private _renderWhite(kelvin: number): TemplateResult {
    return html`
      <div class="white-row">
        <div class="kelvin-readout">
          <span class="kelvin-value">${kelvin} K</span>
        </div>
        <input
          class="kelvin-slider"
          type="range"
          min=${MIN_KELVIN}
          max=${MAX_KELVIN}
          step=${KELVIN_STEP}
          .value=${String(kelvin)}
          @input=${this._onKelvinInput}
          @change=${this._onKelvinInput}
          aria-label="Color temperature in kelvin"
        />
        <div class="kelvin-scale">
          <span>${MIN_KELVIN} K</span>
          <span>${MAX_KELVIN} K</span>
        </div>
      </div>
    `;
  }

  static styles = css`
    :host {
      display: block;
    }
    ha-card {
      padding: 16px;
    }
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }
    .title {
      font-weight: 500;
      color: var(--primary-text-color);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .toggle {
      display: inline-flex;
      background: var(--secondary-background-color, #e0e0e0);
      border-radius: 999px;
      padding: 2px;
    }
    .toggle button {
      border: none;
      background: transparent;
      padding: 4px 12px;
      border-radius: 999px;
      cursor: pointer;
      font-size: 0.85em;
      color: var(--primary-text-color);
      transition: background 0.15s ease;
    }
    .toggle button.active {
      background: var(--primary-color, #03a9f4);
      color: var(--text-primary-color, #fff);
    }
    .body {
      min-height: 80px;
      display: flex;
      align-items: center;
    }
    .color-row {
      display: flex;
      align-items: center;
      gap: 16px;
      width: 100%;
    }
    .swatch {
      width: 64px;
      height: 64px;
      border-radius: 12px;
      border: 1px solid var(--divider-color, rgba(0, 0, 0, 0.12));
      cursor: pointer;
      box-shadow: inset 0 0 0 2px rgba(255, 255, 255, 0.15);
      flex-shrink: 0;
    }
    .swatch:focus {
      outline: 2px solid var(--primary-color, #03a9f4);
      outline-offset: 2px;
    }
    .hex-label {
      display: flex;
      flex-direction: column;
      gap: 4px;
      font-family: var(--code-font-family, monospace);
      color: var(--primary-text-color);
    }
    .hex-label input[type="color"] {
      width: 0;
      height: 0;
      opacity: 0;
      position: absolute;
      pointer-events: none;
    }
    .white-row {
      display: flex;
      flex-direction: column;
      gap: 8px;
      width: 100%;
    }
    .kelvin-readout {
      text-align: center;
      color: var(--primary-text-color);
    }
    .kelvin-value {
      font-size: 1.4em;
      font-weight: 500;
    }
    .kelvin-slider {
      width: 100%;
      accent-color: var(--primary-color, #03a9f4);
    }
    .kelvin-scale {
      display: flex;
      justify-content: space-between;
      font-size: 0.75em;
      color: var(--secondary-text-color);
    }
    .warning {
      color: var(--error-color, #db4437);
      padding: 8px 0;
    }
    code {
      font-family: var(--code-font-family, monospace);
      background: var(--secondary-background-color, #eee);
      padding: 1px 4px;
      border-radius: 4px;
    }
  `;
}

// Guarded: a leftover copy from the old standalone card repo may also be
// loaded as a dashboard resource, and a second define() would throw.
if (!customElements.get(CARD_TYPE)) {
  customElements.define(CARD_TYPE, InputColorCard);
  registerCardInfo();
}

declare global {
  interface HTMLElementTagNameMap {
    "input-color-card": InputColorCard;
  }
}
