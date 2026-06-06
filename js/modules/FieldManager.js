import * as THREE from 'three';

export class FieldManager {
    constructor(scene, name, color, offset, size) {
        this.scene = scene;
        this.name = name;
        this.color = color;
        this.offset = offset;
        this.size = size;
        this.mesh = this.createField();
    }

    createField() {
        const geometry = new THREE.PlaneGeometry(this.size * 2.5, this.size * 2.5, 40, 40); // Even wider radar
        const material = new THREE.MeshBasicMaterial({
            color: this.color,
            transparent: true,
            opacity: 0.1,
            side: THREE.DoubleSide,
            wireframe: true
        });
        const mesh = new THREE.Mesh(geometry, material);
        
        mesh.rotation.x = Math.random() * Math.PI;
        mesh.rotation.y = Math.random() * Math.PI;
        mesh.rotation.z = Math.random() * Math.PI;
        
        mesh.position.set(0, 0, 0); 
        this.scene.add(mesh);
        return mesh;
    }

    update(freq, time) {
        const positions = this.mesh.geometry.attributes.position.array;
        for (let i = 0; i < positions.length; i += 3) {
            const x = positions[i];
            const y = positions[i + 1];
            // Higher intensity ripples
            positions[i + 2] = Math.sin(x * 0.08 + time * freq) * 12 + 
                               Math.cos(y * 0.08 + time * freq) * 12;
        }
        this.mesh.geometry.attributes.position.needsUpdate = true;

        this.mesh.rotation.x += 0.003 * freq;
        this.mesh.rotation.y += 0.004 * freq;
        this.mesh.rotation.z += 0.002 * freq;
    }
}
