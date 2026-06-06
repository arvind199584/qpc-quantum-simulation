import * as THREE from 'three';

export class QubitManager {
    constructor(scene, count, size) {
        this.scene = scene;
        this.count = count;
        this.size = size;
        this.qubits = [];
        this.createQubits();
    }

    createQubits() {
        // Clear existing if any
        this.qubits.forEach(q => this.scene.remove(q));
        this.qubits = [];

        const geometry = new THREE.SphereGeometry(2.0, 16, 16); // Slightly larger for visibility
        const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });

        for (let i = 0; i < this.count; i++) {
            const qubit = new THREE.Mesh(geometry, material.clone());
            this.scene.add(qubit);
            this.qubits.push(qubit);
        }
    }

    updatePositions(coords) {
        // If count changed in sim, re-sync manager
        if (coords.length !== this.qubits.length) {
            this.count = coords.length;
            this.createQubits();
        }

        coords.forEach((pos, i) => {
            if (this.qubits[i]) {
                this.qubits[i].position.set(pos[0], pos[1], pos[2]);
            }
        });
    }
}
