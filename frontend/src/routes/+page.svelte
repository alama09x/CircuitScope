<script lang="ts">
	import { type Device } from '$lib/types';

	const DEVICE_TYPES: DeviceIndex[] = ['oscope', 'fgen'] as const;
	type DeviceIndex = 'oscope' | 'fgen';

	let devices = $state<Record<DeviceIndex, Device[]>>({ oscope: [], fgen: [] });
	let selected = $state<Record<DeviceIndex, number>>({ oscope: -1, fgen: -1 });
	let lastStrs = $state<Record<DeviceIndex, string | null>>({ oscope: null, fgen: null });
	let circuitConnected = $state<boolean>(false);
	let data = $state<number[] | null>(null);
	let awaitingAnalysis = $state<boolean>(false);

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

	// Runs every 3 seconds
	const update = async () => {
		if (awaitingAnalysis) return;
		await updateDevices();
	};

	const analyzeCircuit = async () => {
		awaitingAnalysis = true;

		const response = JSON.parse(await fetch(`http://localhost:8000/analyze`).then((r) => r.json()));
		data = response.data;
		console.log(response.samplingPeriod);

		awaitingAnalysis = false;
	};

	// Update every 3 sec
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

<div>
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

	<div>
		<label for="circuitConnected">Circuit connected</label>
		<input
			bind:checked={circuitConnected}
			name="circuitConnected"
			title="Circuit connected"
			type="checkbox"
		/>
	</div>
	<button
		onclick={analyzeCircuit}
		disabled={selected.fgen === -1 || selected.oscope === -1 || !circuitConnected}
		>Analyze Circuit</button
	>
	{#if data !== null}
		<div>
			{data}
		</div>
	{/if}
</div>
