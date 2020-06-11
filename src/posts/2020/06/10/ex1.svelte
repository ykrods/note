<script>
  let a = 0;
  let b = 0;

  $: console.log(`A: ${a}`);
  $: console.log(`B: ${b}`);

  function onAButtonPushed() {
    a++;
  }
  function onBButtonPushed() {
    b++;
  }
</script>

<main>
  A: {a} <button on:click={onAButtonPushed}>A</button><br>
  B: {b} <button on:click={onBButtonPushed}>B</button>
</main>
