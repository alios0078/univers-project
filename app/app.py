from flask import Flask, render_template_string  # Flask crée le site web

app = Flask(__name__)  # on crée l'application

# Données des planètes (tailles et distances NON réalistes, pour que ce soit visible)
# vitesse = vitesse de rotation autour du Soleil par rapport à la Terre (Terre = 1)
PLANETES = [
    {"nom": "Mercure", "rayon": 0.4, "distance": 8,  "vitesse": 4.15,  "couleur": "#b1b1b1"},
    {"nom": "Vénus",   "rayon": 0.9, "distance": 12, "vitesse": 1.62,  "couleur": "#e8cda2"},
    {"nom": "Terre",   "rayon": 1.0, "distance": 16, "vitesse": 1.0,   "couleur": "#2f6fdb"},
    {"nom": "Mars",    "rayon": 0.6, "distance": 20, "vitesse": 0.53,  "couleur": "#c1440e"},
    {"nom": "Jupiter", "rayon": 2.8, "distance": 28, "vitesse": 0.084, "couleur": "#d8ca9d"},
    {"nom": "Saturne", "rayon": 2.3, "distance": 36, "vitesse": 0.034, "couleur": "#e3d3a1", "anneau": True},
    {"nom": "Uranus",  "rayon": 1.6, "distance": 43, "vitesse": 0.012, "couleur": "#7de3f4"},
    {"nom": "Neptune", "rayon": 1.5, "distance": 50, "vitesse": 0.006, "couleur": "#3f54ba"},
]

# Page HTML + JavaScript (Three.js)
PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>Système solaire 3D</title>
  <style>
    body { margin: 0; overflow: hidden; background: #000; font-family: sans-serif; }
    #info { position: absolute; top: 10px; left: 10px; color: white; font-size: 14px; }
  </style>
  <script type="importmap">
  { "imports": {
      "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
      "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  } }
  </script>
</head>
<body>
  <div id="info">Souris : tourner / molette : zoom / clic droit : déplacer</div>
  <script type="module">
    import * as THREE from "three";
    import { OrbitControls } from "three/addons/controls/OrbitControls.js";

    // Les données viennent de Python
    const planetes = {{ planetes|tojson }};

    // Scène, caméra, rendu
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 3000);
    camera.position.set(0, 60, 90);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(innerWidth, innerHeight);
    document.body.appendChild(renderer.domElement);
    const controls = new OrbitControls(camera, renderer.domElement);

    // Étoiles en arrière-plan
    const positions = [];
    for (let i = 0; i < 3000; i++) {
      positions.push((Math.random() - 0.5) * 1800,
                     (Math.random() - 0.5) * 1800,
                     (Math.random() - 0.5) * 1800);
    }
    const etoilesGeo = new THREE.BufferGeometry();
    etoilesGeo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    scene.add(new THREE.Points(etoilesGeo, new THREE.PointsMaterial({ color: 0xffffff, size: 1.2 })));

    // Soleil (brille tout seul) + lumière au centre
    const soleil = new THREE.Mesh(
      new THREE.SphereGeometry(5, 64, 64),
      new THREE.MeshBasicMaterial({ color: 0xffcc33 })
    );
    scene.add(soleil);
    scene.add(new THREE.PointLight(0xffffff, 3, 0, 0));
    scene.add(new THREE.AmbientLight(0xffffff, 0.15));

    // Création des planètes
    const objets = [];
    planetes.forEach((p, i) => {
      // la sphère de la planète
      const mesh = new THREE.Mesh(
        new THREE.SphereGeometry(p.rayon, 32, 32),
        new THREE.MeshStandardMaterial({ color: p.couleur })
      );
      scene.add(mesh);

      // l'anneau de Saturne
      if (p.anneau) {
        const anneau = new THREE.Mesh(
          new THREE.RingGeometry(p.rayon * 1.3, p.rayon * 2.1, 64),
          new THREE.MeshBasicMaterial({ color: 0xcdb98a, side: THREE.DoubleSide })
        );
        anneau.rotation.x = Math.PI / 2.2;
        mesh.add(anneau);  // l'anneau suit la planète
      }

      // le cercle de l'orbite
      const orbite = new THREE.Mesh(
        new THREE.RingGeometry(p.distance - 0.05, p.distance + 0.05, 128),
        new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide, transparent: true, opacity: 0.25 })
      );
      orbite.rotation.x = -Math.PI / 2;
      scene.add(orbite);

      // angle de départ différent pour chaque planète
      objets.push({ mesh, p, depart: i * 1.3 });
    });

    // Animation
    const horloge = new THREE.Clock();
    function animer() {
      requestAnimationFrame(animer);
      const t = horloge.getElapsedTime();
      soleil.rotation.y = t * 0.1;
      objets.forEach(o => {
        const angle = o.depart + t * o.p.vitesse * 0.5;
        o.mesh.position.set(Math.cos(angle) * o.p.distance, 0, Math.sin(angle) * o.p.distance);
        o.mesh.rotation.y = t * 0.8;  // la planète tourne sur elle-même
      });
      controls.update();
      renderer.render(scene, camera);
    }
    animer();

    // Adapter à la taille de la fenêtre
    addEventListener("resize", () => {
      camera.aspect = innerWidth / innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(innerWidth, innerHeight);
    });
  </script>
</body>
</html>
"""

@app.route("/")  # page d'accueil
def accueil():
    return render_template_string(PAGE, planetes=PLANETES)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # lance le serveur
