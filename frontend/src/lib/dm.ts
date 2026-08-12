import type { Device } from "./types";

export const DEVICE_TYPES: DeviceIndex[] = ['oscope', 'fgen'] as const;
export type DeviceIndex = 'oscope' | 'fgen';
export class DeviceManager {
    devices: Record<DeviceIndex, Device[]>;
    lastStrs: Record<DeviceIndex, string | null>;

    constructor(
        devices: Record<DeviceIndex, Device[]> = { 'oscope': [], 'fgen': [] },
    ) {
        this.devices = devices;
        this.lastStrs = { 'oscope': null, 'fgen': null };
    }

	update(selected: Record<DeviceIndex, number>, response: any): Record<DeviceIndex, number> {
		for (const type of DEVICE_TYPES) {
			if (selected[type] !== -1) {
				this.lastStrs[type] = this.devices[type][selected[type]].resStr;
			}

            selected[type] = response[type].selected;
            // this.devices[type] = response[type].devices;

            const newDevices = response[type].devices;
            if (newDevices.length === 0) continue;
            for (const nd of newDevices) {
                let action = true;
                for (const od of this.devices[type]) {
                    if (this.devices[type].find(() => nd.resStr === od.resStr) !== undefined) {
                        action = false;
                        break;
                    }
                }
                if (action) {
                    this.devices[type].push(nd);
                }
            }

            for (const od of this.devices[type]) {
                let action = true;
                for (const nd of newDevices) {
                    if (this.devices[type].find(() => nd.resStr === od.resStr) !== undefined) {
                        action = false;
                    }
                }
                if (action) {
                    this.devices[type].splice(this.devices[type].indexOf(od), 1);
                }
            }
		}
        return selected;
	}
}