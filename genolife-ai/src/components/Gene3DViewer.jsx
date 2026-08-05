import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, RotateCw, Info, Dna, Loader2 } from "lucide-react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

/**
 * Gene3DViewer — 真实基因蛋白结构三维可视化
 * =========================================
 * 加载真实基因的 PDB 蛋白晶体结构（RCSB Protein Data Bank），
 * 用 Three.js 渲染真实的原子坐标。
 */
const PDB_DATA = {
  APOE: "/gene_APOE.json",
  FTO: "/gene_FTO.json",
};

const RESIDUE_COLORS = {
  ALA: 0x8c8c8c, ARG: 0x1457ff, ASN: 0x00dcdc, ASP: 0xe60a0a,
  CYS: 0xe6e600, GLN: 0x00dcdc, GLU: 0xe60a0a, GLY: 0xebebeb,
  HIS: 0x8282d2, ILE: 0x0f820f, LEU: 0x0f820f, LYS: 0x1457ff,
  MET: 0xe6e600, PHE: 0x3232aa, PRO: 0xdc9682, SER: 0xfa9600,
  THR: 0xfa9600, TRP: 0xb45ab4, TYR: 0x3232aa, VAL: 0x0f820f,
};

export default function Gene3DViewer({ gene, onClose }) {
  const mountRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [atomCount, setAtomCount] = useState(0);

  const symbol = gene?.symbol || "GENE";
  const pdbFile = PDB_DATA[symbol];
  const variants = gene?.variants_found?.length ? gene.variants_found : [];

  useEffect(() => {
    if (!pdbFile) {
      setLoading(false);
      setLoadError(true);
      return;
    }

    const mount = mountRef.current;
    if (!mount) return;

    let renderer, scene, camera, controls;
    let rafId;
    let disposed = false;

    fetch(pdbFile)
      .then((r) => {
        if (!r.ok) throw new Error("PDB 数据加载失败");
        return r.json();
      })
      .then((data) => {
        if (disposed) return;
        const atoms = data.atoms || [];

        scene = new THREE.Scene();
        scene.background = new THREE.Color(0xf8fafc);

        camera = new THREE.PerspectiveCamera(60, mount.clientWidth / mount.clientHeight, 0.1, 1000);
        camera.position.set(0, 0, 80);

        renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(mount.clientWidth, mount.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        mount.appendChild(renderer.domElement);

        controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.08;
        controls.autoRotate = true;
        controls.autoRotateSpeed = 1.2;

        scene.add(new THREE.AmbientLight(0xffffff, 0.7));
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(50, 50, 50);
        scene.add(dirLight);

        // 质心居中
        const cx = atoms.reduce((s, a) => s + a.x, 0) / atoms.length;
        const cy = atoms.reduce((s, a) => s + a.y, 0) / atoms.length;
        const cz = atoms.reduce((s, a) => s + a.z, 0) / atoms.length;

        // 按残基分组
        const residueGroups = {};
        atoms.forEach((atom) => {
          const key = atom.r || "UNK";
          if (!residueGroups[key]) residueGroups[key] = [];
          residueGroups[key].push(atom);
        });

        const group = new THREE.Group();
        Object.entries(residueGroups).forEach(([residue, resAtoms]) => {
          const color = RESIDUE_COLORS[residue] || 0x9ca3af;
          const geometry = new THREE.BufferGeometry();
          const positions = [];
          for (let i = 0; i < resAtoms.length; i += 6) {
            const a = resAtoms[i];
            positions.push(a.x - cx, a.y - cy, a.z - cz);
          }
          geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
          const material = new THREE.PointsMaterial({
            color, size: 1.6, sizeAttenuation: true, transparent: true, opacity: 0.95,
          });
          group.add(new THREE.Points(geometry, material));
        });

        // 骨架线
        const caPositions = [];
        atoms.forEach((a) => caPositions.push(a.x - cx, a.y - cy, a.z - cz));
        const lineGeo = new THREE.BufferGeometry();
        lineGeo.setAttribute("position", new THREE.Float32BufferAttribute(caPositions, 3));
        const lineMat = new THREE.LineBasicMaterial({ color: 0x1e3a5f, transparent: true, opacity: 0.25 });
        group.add(new THREE.Line(lineGeo, lineMat));

        scene.add(group);
        setAtomCount(atoms.length);
        setLoading(false);

        const animate = () => {
          rafId = requestAnimationFrame(animate);
          if (controls) controls.update();
          if (renderer && scene && camera) renderer.render(scene, camera);
        };
        animate();

        const onResize = () => {
          if (!mount) return;
          camera.aspect = mount.clientWidth / mount.clientHeight;
          camera.updateProjectionMatrix();
          renderer.setSize(mount.clientWidth, mount.clientHeight);
        };
        window.addEventListener("resize", onResize);

        return () => window.removeEventListener("resize", onResize);
      })
      .catch((err) => {
        console.error("PDB 加载失败:", err);
        setLoading(false);
        setLoadError(true);
      });

    return () => {
      disposed = true;
      if (rafId) cancelAnimationFrame(rafId);
      if (controls) controls.dispose();
      if (renderer) {
        renderer.dispose();
        if (renderer.domElement.parentNode) {
          renderer.domElement.parentNode.removeChild(renderer.domElement);
        }
      }
    };
  }, [pdbFile]);

  return (
    <motion.div
      className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="bg-white rounded-3xl shadow-2xl w-full max-w-3xl overflow-hidden"
        initial={{ scale: 0.95, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.95, y: 20 }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gradient-to-r from-primary/5 to-transparent">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary-light flex items-center justify-center">
              <Dna size={20} className="text-primary" />
            </div>
            <div>
              <h3 className="font-display font-bold text-[17px] text-text">{symbol} Protein 3D</h3>
              <p className="text-[11px] text-text-tertiary">真实蛋白结构（RCSB PDB）· 拖动旋转 · 滚轮缩放</p>
            </div>
          </div>
          <button onClick={onClose} className="w-9 h-9 rounded-full hover:bg-gray-100 flex items-center justify-center text-text-tertiary cursor-pointer" style={{ background: "none", border: "none" }} aria-label="关闭">
            <X size={18} />
          </button>
        </div>

        <div className="relative" style={{ height: 460 }}>
          <div ref={mountRef} className="w-full h-full" />

          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-50">
              <div className="text-center">
                <Loader2 size={32} className="mx-auto mb-3 animate-spin text-primary" />
                <p className="text-[13px] text-text-tertiary">加载真实蛋白结构...</p>
              </div>
            </div>
          )}

          {loadError && !loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-50">
              <div className="text-center max-w-md px-6">
                <Dna size={32} className="mx-auto mb-3 text-text-tertiary opacity-40" />
                <p className="text-[14px] font-semibold text-text mb-1">{symbol} 暂无公开蛋白结构</p>
                <p className="text-[12px] text-text-tertiary leading-relaxed">该基因目前没有已解析的晶体结构（RCSB PDB）。</p>
                {gene?.function && (
                  <p className="mt-3 text-[12px] text-text-secondary bg-gray-100 rounded-xl p-3 text-left">{gene.function}</p>
                )}
              </div>
            </div>
          )}

          {!loading && !loadError && (
            <div className="absolute top-3 left-3 flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/80 backdrop-blur text-[11px] text-text-secondary shadow-sm">
              <span className="w-2 h-2 rounded-full bg-primary" />
              {atomCount} 原子 · 真实蛋白结构
            </div>
          )}

          <div className="absolute bottom-3 right-3 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-semibold bg-white/80 backdrop-blur shadow-sm text-primary" style={{ border: "none" }}>
            <RotateCw size={12} />
            自动旋转
          </div>
        </div>

        <div className="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
          <div className="flex items-start gap-2 mb-2">
            <Info size={15} className="text-primary mt-0.5 flex-shrink-0" />
            <p className="text-[13px] text-text-secondary leading-relaxed">{gene?.function || `${symbol} 基因参与人体健康调控。`}</p>
          </div>
          {variants.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {variants.map((rs) => (
                <span key={rs} className="px-3 py-1 rounded-full text-[11px] font-mono font-semibold bg-gray-100 text-text-secondary">
                  {rs}
                </span>
              ))}
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
