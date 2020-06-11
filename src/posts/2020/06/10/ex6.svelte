<script>
  let threshold = 5;
  let counter = 0;

  $: if (counter < threshold) {
    console.log(`counter: ${counter}`);
  }

  function countUp() {
    if (counter < threshold) {
      counter++;
    }
  }

  function incrementThreshold() {
    threshold++;
  }
</script>

<main>
  { counter } <button on:click={countUp}>+</button><br>
  <button on:click={incrementThreshold}>increment threshold</button>
</main>
