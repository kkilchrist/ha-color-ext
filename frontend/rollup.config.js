import typescript from "@rollup/plugin-typescript";
import resolve from "@rollup/plugin-node-resolve";
import terser from "@rollup/plugin-terser";

const isRelease = process.env.RELEASE === "true";

export default {
  input: "src/input-color-card.ts",
  output: {
    // Served by the integration; see custom_components/color/card.py.
    file: "../custom_components/color/www/input-color-card.js",
    format: "es",
    sourcemap: isRelease ? false : "inline",
  },
  plugins: [
    resolve(),
    typescript({
      tsconfig: "./tsconfig.json",
      sourceMap: !isRelease,
      inlineSources: !isRelease,
    }),
    ...(isRelease ? [terser({ format: { comments: false } })] : []),
  ],
};
