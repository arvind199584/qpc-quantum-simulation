import * as THREE from 'three';

export class AnimationEngine {
    constructor(scene, linePoolCount) {
        this.scene = scene;
        this.lines = [];
        this.createLinePool(linePoolCount);
    }

    createLinePool(count) {
        const material = new THREE.LineBasicMaterial({
            color: 0xffffff,
            transparent: true,
            opacity: 0.9,
            linewidth: 2
        });

        for (let i = 0; i < count; i++) {
            const points = [new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 0, 0)];
            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const line = new THREE.Line(geometry, material);
            line.visible = false;
            this.scene.add(line);
            this.lines.push(line);
        }
    }

    animateEntanglement(events, qubitCoords) {
        // Hide all lines first
        this.lines.forEach(l => l.visible = false);

        // Show and position lines for current events
        events.forEach((ev, i) => {
            if (i < this.lines.length) {
                const p1 = qubitCoords[ev.p1];
                const p2 = qubitCoords[ev.p2];
                const line = this.lines[i];
                line.geometry.setFromPoints([
                    new THREE.Vector3(...p1),
                    new THREE.Vector3(...p2)
                ]);
                line.visible = true;
            }
        });
    }
}
