import config from "./rollup.config.js";
import { watch } from 'rollup';

const watcher = watch(config);

watcher.on('event', event => {
  console.log(event);
});
