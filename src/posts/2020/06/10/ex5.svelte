<script>
  let counter = 0;

  $: {
    sleep(1).then(() => {
      countUp();
    });
  }

  function sleep(s) {
    return new Promise(resolve => setTimeout(resolve, s * 1000));
  }

  function countUp() {
    counter++;
  }

</script>

<main>
  <p>{ counter }</p>
</main>
