<script lang="ts">
    import type { Oscilloscope } from "$lib/types";

    let oscopes = $state<Oscilloscope[]>([]);
    let selectedOscope = $state<Oscilloscope | null>(null);
    let lastStr = $state<string | null>(null);

    const updateOscopes = async () => {
        if (selectedOscope != null) {
            lastStr = selectedOscope.resStr;
        }

        const response_json = await fetch("http://localhost:8000/oscopes")
            .then((r) => r.json());
        const { selected, oscopes: o } = JSON.parse(response_json);
        oscopes = o;
        selectedOscope = selected !== -1 ? oscopes[selected] : null;
    };

    const updateSelectedOscope = async () => {
        const res_str = selectedOscope != null ? selectedOscope.resStr : "null";
        await fetch("http://localhost:8000/put-oscope/" + res_str, { method: "PUT" });
    }

    // Update oscopes every 3 seconds
    $effect(() => {
        const interval = setInterval(updateOscopes, 3000);

        if ((selectedOscope != null && lastStr != selectedOscope.resStr) || (selectedOscope == null && lastStr != null)) {
            updateSelectedOscope();
        }

        // Avoids memory leaks
        return () => clearInterval(interval);
    })

</script>

<div>Select Oscilloscope</div>
<select bind:value={selectedOscope}>
{#if selectedOscope == null}
    <option value={null} disabled selected hidden placeholder="Choose a scope...">Choose a scope...</option>
{/if}
{#each oscopes as oscope}
    <option value={oscope}>{oscope.manufacturer} {oscope.model}</option>
{/each}
</select>
{#if selectedOscope != null}
<div>{selectedOscope.model}</div>
{/if}