<script lang="ts">
	import { type Cosine, type Device } from '$lib/types';

	const DEVICE_TYPES: DeviceIndex[] = ['oscope', 'fgen'] as const;
	type DeviceIndex = 'oscope' | 'fgen';

	let cos1 = $state<Cosine | null>(null);
	let cos2 = $state<Cosine | null>(null);

	let devices = $state<Record<DeviceIndex, Device[]>>({ oscope: [], fgen: [] });
	let selected = $state<Record<DeviceIndex, number>>({ oscope: -1, fgen: -1 });
	let lastStrs = $state<Record<DeviceIndex, string | null>>({ oscope: null, fgen: null });

	const updateDevices = async () => {
		const response = JSON.parse(await fetch('http://localhost:8000/update').then((r) => r.json()));
		for (const type of DEVICE_TYPES) {
			if (selected[type] !== -1) {
				lastStrs[type] = devices[type][selected[type]].resStr;
			}

			selected[type] = response[type].selected;

			const newDevices = response[type].devices;
			// Add new devices
			for (const nd of newDevices) {
				let action = true;
				for (const od of devices[type]) {
					if (devices[type].find(() => nd.resStr === od.resStr) !== undefined) {
						action = false;
						break;
					}
				}
				if (action) {
					devices[type].push(nd);
				}
			}

			// Remove obsolete devices
			for (const od of devices[type]) {
				let action = true;
				for (const nd of newDevices) {
					if (devices[type].find(() => nd.resStr === od.resStr) !== undefined) {
						action = false;
					}
				}
				if (action) {
					devices[type].splice(devices[type].indexOf(od), 1);
				}
			}
		}
	};

	const updateSelected = async (type: DeviceIndex) => {
		const sel = selected[type];
		let res_str = encodeURIComponent(sel !== -1 ? devices[type][sel].resStr : 'null');
		await fetch(`http://localhost:8000/put/${type}/${res_str}`, { method: 'PUT' });
	};

	const updateCosines = async () => {
		if (selected.oscope === -1) return;

		const response1 = await fetch('http://localhost:8000/oscope/sinusoid/CHAN1').then((r) =>
			r.json()
		);
		cos1 = JSON.parse(response1);

		const response2 = await fetch('http://localhost:8000/oscope/sinusoid/CHAN2').then((r) =>
			r.json()
		);
		cos2 = JSON.parse(response2);
	};

	// Runs every 3 seconds
	const update = async () => {
		await updateDevices();
		await updateCosines();
	};

	// Update every 3 seconds
	$effect(() => {
		const interval = setInterval(update, 3000);

		for (const type of DEVICE_TYPES) {
			const sel = selected[type];

			if (
				(sel !== -1 && lastStrs[type] !== devices[type][sel].resStr) ||
				(sel === -1 && lastStrs[type] !== null)
			) {
				// Update backend
				updateSelected(type);
			}
		}

		// Avoids memory leaks
		return () => clearInterval(interval);
	});
</script>

{#each DEVICE_TYPES as type}
	<div>
		<div>Select {type === 'oscope' ? 'Oscilloscope' : 'Function Generator'}</div>
		<select bind:value={selected[type]}>
			{#if selected[type] === -1}
				<option
					value={-1}
					disabled
					selected
					hidden
					placeholder="Choose a {type === 'oscope' ? 'scope' : 'generator'}..."
					>Choose a {type === 'oscope' ? 'scope' : 'generator'}...</option
				>
			{/if}
			{#each devices[type] as device, i}
				<option value={i}>{device.manufacturer} {device.model}</option>
			{/each}
		</select>
	</div>
{/each}

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
