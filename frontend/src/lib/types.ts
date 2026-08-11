export interface Oscilloscope {
    resStr: string,
    manufacturer: string,
    model: string,
    serialNumber: string,
    firmwareRevision: string,
}

export interface Cosine {
    amplitude: number,
    frequency: number,
    phase: number,
}