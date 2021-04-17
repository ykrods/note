<script>
  let counter = 0;

  $: {
    sleep(1).then(() => {
      counter++;
    });
  }

  function sleep(s) {
    return new Promise(resolve => setTimeout(resolve, s * 1000));
  }
</script>

<main>
  <p>{ counter }</p>
</main>
