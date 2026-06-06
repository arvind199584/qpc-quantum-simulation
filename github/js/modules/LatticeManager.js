import * as THREE from 'three';

export class LatticeManager {
    constructor(scene, size) {
        this.scene = scene;
        this.size = size;
        this.createLattice();
    }

    createLattice() {
        // Create the 3D Chamber Box Edges
        const geometry = new THREE.BoxGeometry(this.size, this.size, this.size);
        const edges = new THREE.EdgesGeometry(geometry);
        const material = new THREE.LineBasicMaterial({ color: 0x004400, linewidth: 2 });
        const chamber = new THREE.LineSegments(edges, material);
        this.scene.add(chamber);

        // Add a subtle grid floor
        const gridHelper = new THREE.GridHelper(this.size, 10, 0x002200, 0x001100);
        gridHelper.position.y = -this.size / 2;
        this.scene.add(gridHelper);
    }
}
