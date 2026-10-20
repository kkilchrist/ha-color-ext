function t(t,e,i,s){var o,r=arguments.length,n=r<3?e:null===s?s=Object.getOwnPropertyDescriptor(e,i):s;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)n=Reflect.decorate(t,e,i,s);else for(var a=t.length-1;a>=0;a--)(o=t[a])&&(n=(r<3?o(n):r>3?o(e,i,n):o(e,i))||n);return r>3&&n&&Object.defineProperty(e,i,n),n}"function"==typeof SuppressedError&&SuppressedError;const e=globalThis,i=e.ShadowRoot&&(void 0===e.ShadyCSS||e.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,s=Symbol(),o=new WeakMap;let r=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==s)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(i&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=o.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&o.set(e,t))}return t}toString(){return this.cssText}};const n=i?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new r("string"==typeof t?t:t+"",void 0,s))(e)})(t):t,{is:a,defineProperty:l,getOwnPropertyDescriptor:h,getOwnPropertyNames:c,getOwnPropertySymbols:d,getPrototypeOf:p}=Object,u=globalThis,_=u.trustedTypes,f=_?_.emptyScript:"",$=u.reactiveElementPolyfillSupport,m=(t,e)=>t,y={toAttribute(t,e){switch(e){case Boolean:t=t?f:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},g=(t,e)=>!a(t,e),v={attribute:!0,type:String,converter:y,reflect:!1,useDefault:!1,hasChanged:g};Symbol.metadata??=Symbol("metadata"),u.litPropertyMetadata??=new WeakMap;let b=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=v){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){const i=Symbol(),s=this.getPropertyDescriptor(t,i,e);void 0!==s&&l(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){const{get:s,set:o}=h(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get:s,set(e){const r=s?.call(this);o?.call(this,e),this.requestUpdate(t,r,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??v}static _$Ei(){if(this.hasOwnProperty(m("elementProperties")))return;const t=p(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(m("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(m("properties"))){const t=this.properties,e=[...c(t),...d(t)];for(const i of e)this.createProperty(i,t[i])}const t=this[Symbol.metadata];if(null!==t){const e=litPropertyMetadata.get(t);if(void 0!==e)for(const[t,i]of e)this.elementProperties.set(t,i)}this._$Eh=new Map;for(const[t,e]of this.elementProperties){const i=this._$Eu(t,e);void 0!==i&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(n(t))}else void 0!==t&&e.push(n(t));return e}static _$Eu(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=new Map,e=this.constructor.elementProperties;for(const i of e.keys())this.hasOwnProperty(i)&&(t.set(i,this[i]),delete this[i]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((t,s)=>{if(i)t.adoptedStyleSheets=s.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const i of s){const s=document.createElement("style"),o=e.litNonce;void 0!==o&&s.setAttribute("nonce",o),s.textContent=i.cssText,t.appendChild(s)}})(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$ET(t,e){const i=this.constructor.elementProperties.get(t),s=this.constructor._$Eu(t,i);if(void 0!==s&&!0===i.reflect){const o=(void 0!==i.converter?.toAttribute?i.converter:y).toAttribute(e,i.type);this._$Em=t,null==o?this.removeAttribute(s):this.setAttribute(s,o),this._$Em=null}}_$AK(t,e){const i=this.constructor,s=i._$Eh.get(t);if(void 0!==s&&this._$Em!==s){const t=i.getPropertyOptions(s),o="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:y;this._$Em=s;const r=o.fromAttribute(e,t.type);this[s]=r??this._$Ej?.get(s)??r,this._$Em=null}}requestUpdate(t,e,i,s=!1,o){if(void 0!==t){const r=this.constructor;if(!1===s&&(o=this[t]),i??=r.getPropertyOptions(t),!((i.hasChanged??g)(o,e)||i.useDefault&&i.reflect&&o===this._$Ej?.get(t)&&!this.hasAttribute(r._$Eu(t,i))))return;this.C(t,e,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(t,e,{useDefault:i,reflect:s,wrapped:o},r){i&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,r??e??this[t]),!0!==o||void 0!==r)||(this._$AL.has(t)||(this.hasUpdated||i||(e=void 0),this._$AL.set(t,e)),!0===s&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}const t=this.constructor.elementProperties;if(t.size>0)for(const[e,i]of t){const{wrapped:t}=i,s=this[e];!0!==t||this._$AL.has(e)||void 0===s||this.C(e,void 0,i,s)}}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(e){throw t=!1,this._$EM(),e}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(t){}firstUpdated(t){}};b.elementStyles=[],b.shadowRootOptions={mode:"open"},b[m("elementProperties")]=new Map,b[m("finalized")]=new Map,$?.({ReactiveElement:b}),(u.reactiveElementVersions??=[]).push("2.1.2");const A=globalThis,w=t=>t,x=A.trustedTypes,E=x?x.createPolicy("lit-html",{createHTML:t=>t}):void 0,S="$lit$",C=`lit$${Math.random().toFixed(9).slice(2)}$`,k="?"+C,P=`<${k}>`,U=document,H=()=>U.createComment(""),O=t=>null===t||"object"!=typeof t&&"function"!=typeof t,T=Array.isArray,M="[ \t\n\f\r]",N=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,R=/-->/g,K=/>/g,j=RegExp(`>|${M}(?:([^\\s"'>=/]+)(${M}*=${M}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),I=/'/g,D=/"/g,z=/^(?:script|style|textarea|title)$/i,L=(t=>(e,...i)=>({_$litType$:t,strings:e,values:i}))(1),W=Symbol.for("lit-noChange"),B=Symbol.for("lit-nothing"),q=new WeakMap,F=U.createTreeWalker(U,129);function V(t,e){if(!T(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==E?E.createHTML(e):e}const J=(t,e)=>{const i=t.length-1,s=[];let o,r=2===e?"<svg>":3===e?"<math>":"",n=N;for(let e=0;e<i;e++){const i=t[e];let a,l,h=-1,c=0;for(;c<i.length&&(n.lastIndex=c,l=n.exec(i),null!==l);)c=n.lastIndex,n===N?"!--"===l[1]?n=R:void 0!==l[1]?n=K:void 0!==l[2]?(z.test(l[2])&&(o=RegExp("</"+l[2],"g")),n=j):void 0!==l[3]&&(n=j):n===j?">"===l[0]?(n=o??N,h=-1):void 0===l[1]?h=-2:(h=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?j:'"'===l[3]?D:I):n===D||n===I?n=j:n===R||n===K?n=N:(n=j,o=void 0);const d=n===j&&t[e+1].startsWith("/>")?" ":"";r+=n===N?i+P:h>=0?(s.push(a),i.slice(0,h)+S+i.slice(h)+C+d):i+C+(-2===h?e:d)}return[V(t,r+(t[i]||"<?>")+(2===e?"</svg>":3===e?"</math>":"")),s]};class Z{constructor({strings:t,_$litType$:e},i){let s;this.parts=[];let o=0,r=0;const n=t.length-1,a=this.parts,[l,h]=J(t,e);if(this.el=Z.createElement(l,i),F.currentNode=this.el.content,2===e||3===e){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(s=F.nextNode())&&a.length<n;){if(1===s.nodeType){if(s.hasAttributes())for(const t of s.getAttributeNames())if(t.endsWith(S)){const e=h[r++],i=s.getAttribute(t).split(C),n=/([.?@])?(.*)/.exec(e);a.push({type:1,index:o,name:n[2],strings:i,ctor:"."===n[1]?tt:"?"===n[1]?et:"@"===n[1]?it:X}),s.removeAttribute(t)}else t.startsWith(C)&&(a.push({type:6,index:o}),s.removeAttribute(t));if(z.test(s.tagName)){const t=s.textContent.split(C),e=t.length-1;if(e>0){s.textContent=x?x.emptyScript:"";for(let i=0;i<e;i++)s.append(t[i],H()),F.nextNode(),a.push({type:2,index:++o});s.append(t[e],H())}}}else if(8===s.nodeType)if(s.data===k)a.push({type:2,index:o});else{let t=-1;for(;-1!==(t=s.data.indexOf(C,t+1));)a.push({type:7,index:o}),t+=C.length-1}o++}}static createElement(t,e){const i=U.createElement("template");return i.innerHTML=t,i}}function G(t,e,i=t,s){if(e===W)return e;let o=void 0!==s?i._$Co?.[s]:i._$Cl;const r=O(e)?void 0:e._$litDirective$;return o?.constructor!==r&&(o?._$AO?.(!1),void 0===r?o=void 0:(o=new r(t),o._$AT(t,i,s)),void 0!==s?(i._$Co??=[])[s]=o:i._$Cl=o),void 0!==o&&(e=G(t,o._$AS(t,e.values),o,s)),e}class Y{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:i}=this._$AD,s=(t?.creationScope??U).importNode(e,!0);F.currentNode=s;let o=F.nextNode(),r=0,n=0,a=i[0];for(;void 0!==a;){if(r===a.index){let e;2===a.type?e=new Q(o,o.nextSibling,this,t):1===a.type?e=new a.ctor(o,a.name,a.strings,this,t):6===a.type&&(e=new st(o,this,t)),this._$AV.push(e),a=i[++n]}r!==a?.index&&(o=F.nextNode(),r++)}return F.currentNode=U,s}p(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}}class Q{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,i,s){this.type=2,this._$AH=B,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=G(this,t,e),O(t)?t===B||null==t||""===t?(this._$AH!==B&&this._$AR(),this._$AH=B):t!==this._$AH&&t!==W&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):(t=>T(t)||"function"==typeof t?.[Symbol.iterator])(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==B&&O(this._$AH)?this._$AA.nextSibling.data=t:this.T(U.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:i}=t,s="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=Z.createElement(V(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(e);else{const t=new Y(s,this),i=t.u(this.options);t.p(e),this.T(i),this._$AH=t}}_$AC(t){let e=q.get(t.strings);return void 0===e&&q.set(t.strings,e=new Z(t)),e}k(t){T(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,s=0;for(const o of t)s===e.length?e.push(i=new Q(this.O(H()),this.O(H()),this,this.options)):i=e[s],i._$AI(o),s++;s<e.length&&(this._$AR(i&&i._$AB.nextSibling,s),e.length=s)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){const e=w(t).nextSibling;w(t).remove(),t=e}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t))}}class X{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,i,s,o){this.type=1,this._$AH=B,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=o,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=B}_$AI(t,e=this,i,s){const o=this.strings;let r=!1;if(void 0===o)t=G(this,t,e,0),r=!O(t)||t!==this._$AH&&t!==W,r&&(this._$AH=t);else{const s=t;let n,a;for(t=o[0],n=0;n<o.length-1;n++)a=G(this,s[i+n],e,n),a===W&&(a=this._$AH[n]),r||=!O(a)||a!==this._$AH[n],a===B?t=B:t!==B&&(t+=(a??"")+o[n+1]),this._$AH[n]=a}r&&!s&&this.j(t)}j(t){t===B?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}}class tt extends X{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===B?void 0:t}}class et extends X{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==B)}}class it extends X{constructor(t,e,i,s,o){super(t,e,i,s,o),this.type=5}_$AI(t,e=this){if((t=G(this,t,e,0)??B)===W)return;const i=this._$AH,s=t===B&&i!==B||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,o=t!==B&&(i===B||s);s&&this.element.removeEventListener(this.name,this,i),o&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}}class st{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){G(this,t)}}const ot=A.litHtmlPolyfillSupport;ot?.(Z,Q),(A.litHtmlVersions??=[]).push("3.3.3");const rt=globalThis;class nt extends b{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{const s=i?.renderBefore??e;let o=s._$litPart$;if(void 0===o){const t=i?.renderBefore??null;s._$litPart$=o=new Q(e.insertBefore(H(),t),t,void 0,i??{})}return o._$AI(t),o})(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return W}}nt._$litElement$=!0,nt.finalized=!0,rt.litElementHydrateSupport?.({LitElement:nt});const at=rt.litElementPolyfillSupport;at?.({LitElement:nt}),(rt.litElementVersions??=[]).push("4.2.2");const lt={attribute:!0,type:String,converter:y,reflect:!1,hasChanged:g},ht=(t=lt,e,i)=>{const{kind:s,metadata:o}=i;let r=globalThis.litPropertyMetadata.get(o);if(void 0===r&&globalThis.litPropertyMetadata.set(o,r=new Map),"setter"===s&&((t=Object.create(t)).wrapped=!0),r.set(i.name,t),"accessor"===s){const{name:s}=i;return{set(i){const o=e.get.call(this);e.set.call(this,i),this.requestUpdate(s,o,t,!0,i)},init(e){return void 0!==e&&this.C(s,void 0,t,e),e}}}if("setter"===s){const{name:s}=i;return function(i){const o=this[s];e.call(this,i),this.requestUpdate(s,o,t,!0,i)}}throw Error("Unsupported decorator location: "+s)};function ct(t){return(e,i)=>"object"==typeof i?ht(t,e,i):((t,e,i)=>{const s=e.hasOwnProperty(i);return e.constructor.createProperty(i,t),s?Object.getOwnPropertyDescriptor(e,i):void 0})(t,e,i)}function dt(t){return ct({...t,state:!0,attribute:!1})}const pt="input-color-card";const ut=/^#([0-9a-fA-F]{6})$/,_t=2e3,ft=6500;class $t extends nt{setConfig(t){if(!t||"object"!=typeof t)throw new Error("Invalid configuration");if(!t.entity||"string"!=typeof t.entity)throw new Error("You must specify an `entity` (an color entity).");if(!t.entity.startsWith("color."))throw new Error(`Entity must be from the color domain. Got: ${t.entity}`);this._config={...t},this._localHex=void 0,this._localKelvin=void 0,this._localKind=void 0}getCardSize(){return 3}static getStubConfig(){return{entity:""}}shouldUpdate(t){if(t.has("_config")||t.has("_localHex")||t.has("_localKelvin")||t.has("_localKind"))return!0;if(t.has("hass")){const e=t.get("hass"),i=this._config?.entity;if(!i)return!0;const s=e?.states?.[i],o=this.hass?.states?.[i];return s!==o}return!1}_getEntityState(){if(this.hass&&this._config?.entity)return this.hass.states[this._config.entity]}_currentKind(){if(this._localKind)return this._localKind;const t=this._getEntityState()?.attributes;return"white"===t?.kind?"white":"chromatic"}_currentHex(){if(this._localHex)return this._localHex;const t=this._getEntityState(),e=t?.state??"";return ut.test(e)?e.toUpperCase():"#FFFFFF"}_currentKelvin(){if(null!=this._localKelvin)return this._localKelvin;const t=this._getEntityState()?.attributes,e=t?.color_temp_kelvin;return"number"==typeof e&&e>=_t&&e<=ft?e:4e3}_scheduleCommit(t){this._commitTimer&&window.clearTimeout(this._commitTimer),this._commitTimer=window.setTimeout(()=>{this._commitTimer=void 0,this._callSetColor(t)},150)}async _callSetColor(t){if(this.hass&&this._config?.entity)try{await this.hass.callService("color","set_color",t,{entity_id:this._config.entity})}catch(t){console.error("[input-color-card] set_color failed:",t)}}_onKindChange(t){if(t!==this._currentKind())if(this._localKind=t,"white"===t){const t=this._currentKelvin();this._localKelvin=t,this._scheduleCommit({color_temp_kelvin:t})}else{const t=this._currentHex();this._localHex=t,this._scheduleCommit({hex_value:t})}}_onColorInput(t){const e=(t.target.value||"").toUpperCase();ut.test(e)&&(this._localHex=e,this._localKind="chromatic",this._scheduleCommit({hex_value:e}))}_onKelvinInput(t){const e=t.target,i=parseInt(e.value,10);Number.isNaN(i)||(this._localKelvin=i,this._localKind="white",this._scheduleCommit({color_temp_kelvin:i}))}_onSwatchClick(){const t=this.renderRoot.querySelector("input#color-picker");t?.click()}_onSwatchKeydown(t){"Enter"!==t.key&&" "!==t.key||(t.preventDefault(),this._onSwatchClick())}render(){if(!this._config||!this.hass)return B;const t=this._config.entity,e=this._getEntityState();if(!e)return L`
        <ha-card>
          <div class="warning">
            Entity not found: <code>${t}</code>
          </div>
        </ha-card>
      `;const i=this._currentKind(),s=this._currentHex(),o=this._currentKelvin(),r=this._config.name||e.attributes.friendly_name||t;return L`
      <ha-card>
        <div class="header">
          <div class="title">${r}</div>
          <div class="toggle" role="tablist" aria-label="Color mode">
            <button
              role="tab"
              type="button"
              aria-selected=${"chromatic"===i}
              class=${"chromatic"===i?"active":""}
              @click=${()=>this._onKindChange("chromatic")}
            >
              Color
            </button>
            <button
              role="tab"
              type="button"
              aria-selected=${"white"===i}
              class=${"white"===i?"active":""}
              @click=${()=>this._onKindChange("white")}
            >
              White
            </button>
          </div>
        </div>

        <div class="body">
          ${"chromatic"===i?this._renderColor(s):this._renderWhite(o)}
        </div>
      </ha-card>
    `}_renderColor(t){return L`
      <div class="color-row">
        <div
          class="swatch"
          role="button"
          tabindex="0"
          aria-label="Open color picker"
          style=${`background:${t}`}
          @click=${this._onSwatchClick}
          @keydown=${this._onSwatchKeydown}
        ></div>
        <label class="hex-label">
          <span>${t}</span>
          <input
            id="color-picker"
            type="color"
            .value=${t}
            @input=${this._onColorInput}
            @change=${this._onColorInput}
          />
        </label>
      </div>
    `}_renderWhite(t){return L`
      <div class="white-row">
        <div class="kelvin-readout">
          <span class="kelvin-value">${t} K</span>
        </div>
        <input
          class="kelvin-slider"
          type="range"
          min=${_t}
          max=${ft}
          step=${100}
          .value=${String(t)}
          @input=${this._onKelvinInput}
          @change=${this._onKelvinInput}
          aria-label="Color temperature in kelvin"
        />
        <div class="kelvin-scale">
          <span>${_t} K</span>
          <span>${ft} K</span>
        </div>
      </div>
    `}}$t.styles=((t,...e)=>{const i=1===t.length?t[0]:e.reduce((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1],t[0]);return new r(i,t,s)})`
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
  `,t([ct({attribute:!1})],$t.prototype,"hass",void 0),t([dt()],$t.prototype,"_config",void 0),t([dt()],$t.prototype,"_localHex",void 0),t([dt()],$t.prototype,"_localKelvin",void 0),t([dt()],$t.prototype,"_localKind",void 0),customElements.get(pt)||(customElements.define(pt,$t),"undefined"!=typeof window&&(window.customCards=window.customCards||[],window.customCards.some(t=>t.type===pt)||(window.customCards.push({type:pt,name:"Input Color Card",description:"Tap a swatch to pick a color, or toggle to White and set a kelvin temperature. Companion to the color integration.",preview:!0,documentationURL:"https://github.com/kkilchrist/ha-color-ext#dashboard-card"}),console.info("%c input-color-card %c v0.3.1 ","color: white; background: #2d8cf0; font-weight: 700;","color: #2d8cf0; background: white; font-weight: 700;"))));export{$t as InputColorCard};
