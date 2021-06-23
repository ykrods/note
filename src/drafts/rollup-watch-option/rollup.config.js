import nodeResolve from '@rollup/plugin-node-resolve';

export default {
  input: 'src/main.js',
  output: {
    sourcemap: true,
    format: 'iife',
    name: 'app', // export window.app
    file: 'dist/bundle.js',
  },
  plugins: [
    // to resolve (import) thrid-party libs
    nodeResolve({
      browser: true,
    }),
  ],

  watch: {
    // include: ["./src/submod1.js"],
    // exclude: ["./src/submod1.js"],
    clearScreen: false,
  },
};
