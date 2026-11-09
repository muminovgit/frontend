import * as THREE from 'three';

export type Zone = 'head' | 'hand' | 'body';

export interface Figure {
  root: THREE.Group;
  body: THREE.Group;
  head: THREE.Group;
  armL: THREE.Group;
  armR: THREE.Group;
  pickables: THREE.Mesh[];
}

/**
 * Stilizatsiyalangan bola modeli. Foto → 3D xizmat ulanganda shu o'rin
 * yaratilgan model bilan almashtiriladi. Hozircha qo'lda yasalgan figura.
 */
export function buildFigure(): Figure {
  const M = (c: number) => new THREE.MeshStandardMaterial({ color: c, roughness: 0.55 });
  const skin = M(0xffd2b0), hoodie = M(0x7a5cc7), pants = M(0x2b2640), white = M(0xffffff);
  const cap = M(0x3e7bd6), dark = M(0x2b2640), cheek = M(0xff9aae), coral = M(0xf2526f);

  const root = new THREE.Group();
  const body = new THREE.Group();
  root.add(body);
  const pickables: THREE.Mesh[] = [];

  const tag = (mesh: THREE.Mesh, zone: Zone) => {
    mesh.userData.zone = zone;
    pickables.push(mesh);
    return mesh;
  };

  [-0.22, 0.22].forEach((x) => {
    const leg = tag(new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.14, 0.9, 20), pants), 'body');
    leg.position.set(x, 0.45, 0);
    body.add(leg);
    const shoe = tag(new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.18, 0.44), white), 'body');
    shoe.position.set(x, 0.09, 0.06);
    body.add(shoe);
  });

  const torso = tag(new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.5, 24), hoodie), 'body');
  torso.position.set(0, 1.35, 0);
  body.add(torso);
  const pocket = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.22, 0.05), coral);
  pocket.position.set(0, 1.12, 0.38);
  body.add(pocket);

  const armL = new THREE.Group();
  armL.position.set(-0.5, 1.6, 0);
  const armR = new THREE.Group();
  armR.position.set(0.5, 1.6, 0);
  body.add(armL, armR);
  [armL, armR].forEach((a) => {
    const arm = tag(new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.45, 14), hoodie), 'body');
    arm.position.y = -0.35;
    a.add(arm);
    const hand = tag(new THREE.Mesh(new THREE.SphereGeometry(0.16, 16, 16), skin), 'hand');
    hand.position.y = -0.8;
    a.add(hand);
  });

  const head = new THREE.Group();
  head.position.set(0, 2.2, 0);
  body.add(head);
  head.add(tag(new THREE.Mesh(new THREE.SphereGeometry(0.62, 32, 24), skin), 'head'));
  const hat = tag(new THREE.Mesh(new THREE.SphereGeometry(0.64, 32, 16, 0, Math.PI * 2, 0, Math.PI * 0.45), cap), 'head');
  hat.position.y = 0.06;
  head.add(hat);
  [-0.22, 0.22].forEach((x) => {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.075, 14, 14), dark);
    eye.position.set(x, 0.02, 0.56);
    head.add(eye);
    const c = new THREE.Mesh(new THREE.SphereGeometry(0.09, 14, 14), cheek);
    c.position.set(x * 1.35, -0.14, 0.5);
    c.scale.set(1, 0.6, 0.5);
    head.add(c);
  });
  const smile = new THREE.Mesh(new THREE.TorusGeometry(0.1, 0.02, 8, 24, Math.PI), dark);
  smile.position.set(0, -0.16, 0.6);
  smile.rotation.z = Math.PI;
  head.add(smile);

  const ring = new THREE.Mesh(new THREE.RingGeometry(0.9, 1.0, 64), M(0xc9f7f1));
  ring.rotation.x = -Math.PI / 2;
  ring.position.y = 0.01;
  root.add(ring);

  return { root, body, head, armL, armR, pickables };
}

/** Tanlangan harakatga qarab figurani animatsiya qiladi. t — umumiy vaqt, e — harakat boshidan beri. */
export function animateFigure(f: Figure, mode: string, t: number, e: number) {
  const k = mode === 'idle' ? 0 : Math.max(0, 1 - e / 2.2);
  f.body.position.y = Math.sin(t * 2) * 0.02;
  f.head.rotation.set(0, 0, Math.sin(t * 1.4) * 0.03);
  f.armL.rotation.z = -0.12;
  f.armR.rotation.z = 0.12;
  if (mode === 'idle') f.head.rotation.x = 0;
  if (mode === 'wave') f.armR.rotation.z = 2.6 + Math.sin(e * 9) * 0.3;
  if (mode === 'nod') f.head.rotation.x = Math.sin(e * 7) * 0.35 * k;
  if (mode === 'jump') f.body.position.y = Math.abs(Math.sin(e * 5)) * 0.8 * k;
  if (mode === 'happy') {
    f.armL.rotation.z = -2.6 + Math.sin(e * 10) * 0.25;
    f.armR.rotation.z = 2.6 - Math.sin(e * 10) * 0.25;
    f.body.position.y = Math.abs(Math.sin(e * 6)) * 0.4 * k;
  }
}
