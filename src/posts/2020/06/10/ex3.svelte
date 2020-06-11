<script>
  import { onMount } from 'svelte';

  let foo = 0;

  $: {
    foo++;
    console.log(`foo: ${foo}`);
  }

  onMount(() => {
    setTimeout(()=> { foo = 10; }, 1000);
  });
</script>

<main>
</main>
