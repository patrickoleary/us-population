export default {
  base: "./",
  build: {
    lib: {
      entry: "./src/main.js",
      name: "us_population",
      formats: ["umd"],
      fileName: "us_population",
    },
    rollupOptions: {
      external: ["vue"],
      output: {
        globals: {
          vue: "Vue",
        },
      },
    },
    outDir: "../us_population/module/serve",
    assetsDir: ".",
  },
};
