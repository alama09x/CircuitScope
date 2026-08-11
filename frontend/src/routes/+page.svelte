<script lang="ts">
	import type { Cosine, Oscilloscope } from '$lib/types';
	import { onMount } from 'svelte';

	let oscopes = $state<Oscilloscope[]>([]);
	let selectedOscope = $state<Oscilloscope | null>(null);
	let lastStr = $state<string | null>(null);

	let cos1 = $state<Cosine | null>(null);
	let cos2 = $state<Cosine | null>(null);

	const updateOscopes = async () => {
		if (selectedOscope != null) {
			lastStr = selectedOscope.resStr;
		}

		const response_json = await fetch('http://localhost:8000/oscopes').then((r) => r.json());
		const { selected, oscopes: o } = JSON.parse(response_json);
		oscopes = o;
		selectedOscope = selected !== -1 ? oscopes[selected] : null;
	};

	const updateCosines = async () => {
		if (selectedOscope === null) return;

		const response1 = await fetch('http://localhost:8000/sinusoid/CHAN1').then((r) => r.json());
		cos1 = JSON.parse(response1);

		const response2 = await fetch('http://localhost:8000/sinusoid/CHAN2/CHAN1').then((r) =>
			r.json()
		);
		cos2 = JSON.parse(response2);
	};

	const updateSelectedOscope = async () => {
		const res_str = selectedOscope != null ? selectedOscope.resStr : 'null';
		await fetch('http://localhost:8000/put-oscope/' + res_str, { method: 'PUT' });
	};

	// Runs every 3 seconds
	const update = async () => {
		await updateOscopes();
		await updateCosines();
	};

	// Update oscopes every 3 seconds
	$effect(() => {
		const interval = setInterval(update, 3000);

		if (
			(selectedOscope != null && lastStr != selectedOscope.resStr) ||
			(selectedOscope === null && lastStr != null)
		) {
			updateSelectedOscope();
		}

		// Avoids memory leaks
		return () => clearInterval(interval);
	});
</script>

<div>Select Oscilloscope</div>
<select bind:value={selectedOscope}>
	{#if selectedOscope === null}
		<option value={null} disabled selected hidden placeholder="Choose a scope..."
			>Choose a scope...</option
		>
	{/if}
	{#each oscopes as oscope}
		<option value={oscope}>{oscope.manufacturer} {oscope.model}</option>
	{/each}
</select>
	{#each [cos1, cos2] as cos, i}
		{#if cos !== null}
			<div>
				<math>
					<msub>
						<mi>V</mi>
						<mn>{i + 1}</mn>
					</msub>
					<mo>=</mo>
					<mi>{cos?.amplitude}cos</mi>
					<mo>(</mo>
					<mi>2&pi;</mi>
					<mo>*</mo>
					<mi>{cos?.frequency}t</mi>
					<mo>+</mo>
					<mi>{cos?.phase}</mi>
					<mo>)</mo>
				</math>
			</div>
		{/if}
	{/each}
