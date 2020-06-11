<script>
  import { onMount } from 'svelte';

  let a = 0;
  let b = 0;

  $: {
    console.log(`A: ${a}`);
    b = a;
  }

  $: console.log(`B: ${b}`);

  onMount(() => {
    const interval = setInterval(()=> {
      a++;
    }, 1000);

    return () => {
      clearInterval(interval);
    }
  });
</script>

<main>
A: {a}
B: {b}
</main>
