import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Info, Dna, Loader2, ExternalLink, RotateCcw, ZoomIn, ZoomOut } from "lucide-react";
import * as THREE from "three";
import PDB_MAPPING from "../data/pdbMapping";

const COLORS = {
  primary: 0x4F46E5,
  accent: 0x10B981,
  backbone: 0x94A3B8,
  backbone2: 0x64748B,
  variant: 0xEF4444,
  pairA: 0x3B82F6,
  pairT: 0xF59E0B,
  pairC: 0x10B981,
  pairG: 0xEF4444,
  glow: 0x818CF8,
};

/**
 * 创建 DNA 双螺旋 3D 可视化 — 使用 Three.js 本地渲染
 * 用于替代被 X-Frame-Options 阻止的外部 iframe 嵌入方案
 */
export default function Gene3DViewer({ gene, onClose }) {
  const [loading, setLoading] = useState(true);
  const [selectedVariant, setSelectedVariant] = useState(null);
  const [hoveredSegment, setHoveredSegment] = useState(null);
  const [autoRotate, setAutoRotate] = useState(true);
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const helixGroupRef = useRef(null);
  const animationIdRef = useRef(null);
  const variantMarkersRef = useRef([]);

  const symbol = gene?.symbol || "GENE";
  const pdb = PDB_MAPPING[symbol];
  const variants = gene?.variants_found?.length ? gene.variants_found : [];
  const variantPositions = new Set(variants);

  // ── 场景初始化 ──
  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = 480;

    // 渲染器
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    container.appendChild(renderer.domElement);

    // 场景
    const scene = new THREE.Scene();
    scene.fog = new THREE.Fog(0xf8fafc, 8, 30);
    sceneRef.current = scene;

    // 相机
    const camera = new THREE.PerspectiveCamera(50, width / height, 0.5, 50);
    camera.position.set(4, 1.5, 8);
    camera.lookAt(0, 0, 0);

    // 灯光
    const ambient = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambient);

    const keyLight = new THREE.DirectionalLight(0xffffff, 1.5);
    keyLight.position.set(8, 6, 4);
    keyLight.castShadow = true;
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0x818CF8, 0.5);
    fillLight.position.set(-4, -1, -2);
    scene.add(fillLight);

    const rimLight = new THREE.DirectionalLight(0x10B981, 0.4);
    rimLight.position.set(0, -3, 6);
    scene.add(rimLight);

    // 地面参考平面
    const gridHelper = new THREE.PolarGridHelper(5, 32, 24, 64, 0xe2e8f0, 0xe2e8f0);
    gridHelper.position.y = -3.5;
    scene.add(gridHelper);

    // ── DNA 双螺旋主体 ──
    const helixGroup = new THREE.Group();
    helixGroupRef.current = helixGroup;
    scene.add(helixGroup);

    const segments = 60;
    const turns = 3;
    const radius = 1.0;
    const totalHeight = 6;
    const segmentHeight = totalHeight / segments;

    // 存储每个片段的位置（用于标记变异位点）
    const segmentPositions = [];

    // 碱基对颜色映射
    const basePairs = ["A", "T", "C", "G", "A", "T", "G", "C"];
    const baseColors = { A: COLORS.pairA, T: COLORS.pairT, C: COLORS.pairC, G: COLORS.pairG };

    for (let i = 0; i < segments; i++) {
      const t = i / segments;
      const angle = t * Math.PI * 2 * turns;
      const y = -totalHeight / 2 + i * segmentHeight;

      // 两股螺旋主链节点
      const angle1 = angle;
      const angle2 = angle + Math.PI;

      const x1 = Math.cos(angle1) * radius;
      const z1 = Math.sin(angle1) * radius;
      const x2 = Math.cos(angle2) * radius;
      const z2 = Math.sin(angle2) * radius;

      // 是变异位点段吗？
      const isVariant = i % 7 === 0 || i % 13 === 0; // 标记一些段为变异位点
      const segmentIdx = i;

      // ── 主链节点球（两股） ──
      const sphereGeo = new THREE.SphereGeometry(0.12, 16, 16);
      const material1 = new THREE.MeshStandardMaterial({
        color: COLORS.backbone,
        roughness: 0.3,
        metalness: 0.1,
      });
      const material2 = new THREE.MeshStandardMaterial({
        color: COLORS.backbone2,
        roughness: 0.3,
        metalness: 0.1,
      });

      const node1 = new THREE.Mesh(sphereGeo, material1);
      node1.position.set(x1, y, z1);
      node1.castShadow = true;
      helixGroup.add(node1);

      const node2 = new THREE.Mesh(sphereGeo, material2);
      node2.position.set(x2, y, z2);
      node2.castShadow = true;
      helixGroup.add(node2);

      // ── 碱基对连接柱 ──
      const midX = (x1 + x2) / 2;
      const midZ = (z1 + z2) / 2;
      const bp = basePairs[i % basePairs.length];
      const pairColor = baseColors[bp] || COLORS.pairA;

      const barLength = Math.sqrt((x2 - x1) ** 2 + (z2 - z1) ** 2);
      const barGeo = new THREE.CylinderGeometry(0.035, 0.035, barLength, 8);
      const barMat = new THREE.MeshStandardMaterial({
        color: isVariant ? COLORS.variant : pairColor,
        roughness: 0.4,
        metalness: 0.05,
        emissive: isVariant ? COLORS.variant : pairColor,
        emissiveIntensity: isVariant ? 0.35 : 0.15,
      });
      const bar = new THREE.Mesh(barGeo, barMat);
      bar.position.set(midX, y, midZ);
      bar.rotation.z = Math.PI / 2;
      bar.rotation.y = -Math.atan2(z2 - z1, x2 - x1);
      bar.userData = { segmentIndex: segmentIdx, isVariant, y };
      helixGroup.add(bar);

      // ── 连接主链的纵向柱（糖-磷酸骨架） ──
      if (i < segments - 1) {
        const nextT = (i + 1) / segments;
        const nextAngle = nextT * Math.PI * 2 * turns;
        const nextY = -totalHeight / 2 + (i + 1) * segmentHeight;
        const nextX1 = Math.cos(nextAngle) * radius;
        const nextZ1 = Math.sin(nextAngle) * radius;
        const nextX2 = Math.cos(nextAngle + Math.PI) * radius;
        const nextZ2 = Math.sin(nextAngle + Math.PI) * radius;

        const createBackboneConn = (x, y, z, nx, ny, nz, color) => {
          const dx = nx - x;
          const dy = ny - y;
          const dz = nz - z;
          const len = Math.sqrt(dx * dx + dy * dy + dz * dz);
          const midPt = new THREE.Vector3((x + nx) / 2, (y + ny) / 2, (z + nz) / 2);
          const dir = new THREE.Vector3(dx, dy, dz).normalize();

          const connGeo = new THREE.CylinderGeometry(0.04, 0.04, len, 6);
          const connMat = new THREE.MeshStandardMaterial({ color, roughness: 0.35, metalness: 0.08 });
          const conn = new THREE.Mesh(connGeo, connMat);
          conn.position.copy(midPt);

          const quaternion = new THREE.Quaternion();
          quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
          conn.setRotationFromQuaternion(quaternion);

          return conn;
        };

        helixGroup.add(createBackboneConn(x1, y, z1, nextX1, nextY, nextZ1, COLORS.backbone));
        helixGroup.add(createBackboneConn(x2, y, z2, nextX2, nextY, nextZ2, COLORS.backbone2));
      }

      // 记录片段位置
      segmentPositions.push({
        index: segmentIdx,
        y,
        midX,
        midZ,
        isVariant,
        basePair: bp,
        worldPos: new THREE.Vector3(midX, y, midZ),
      });
    }

    // ── 中心光柱 ──
    const coreGeo = new THREE.CylinderGeometry(0.06, 0.06, totalHeight, 16);
    const coreMat = new THREE.MeshStandardMaterial({
      color: COLORS.glow,
      roughness: 0.2,
      metalness: 0.3,
      emissive: COLORS.glow,
      emissiveIntensity: 0.5,
      transparent: true,
      opacity: 0.5,
    });
    const core = new THREE.Mesh(coreGeo, coreMat);
    helixGroup.add(core);

    // ── 顶部和底部装饰环 ──
    const ringGeo = new THREE.TorusGeometry(radius, 0.04, 16, 48);
    const ringMat = new THREE.MeshStandardMaterial({
      color: COLORS.primary,
      roughness: 0.2,
      metalness: 0.5,
      emissive: COLORS.primary,
      emissiveIntensity: 0.3,
    });

    const topRing = new THREE.Mesh(ringGeo, ringMat);
    topRing.position.y = totalHeight / 2;
    topRing.rotation.x = Math.PI / 2;
    helixGroup.add(topRing);

    const bottomRing = new THREE.Mesh(ringGeo, ringMat);
    bottomRing.position.y = -totalHeight / 2;
    bottomRing.rotation.x = Math.PI / 2;
    helixGroup.add(bottomRing);

    // ── 粒子环绕 ──
    const particleCount = 200;
    const particleGeo = new THREE.BufferGeometry();
    const particlePositionsArr = new Float32Array(particleCount * 3);
    const particleColorsArr = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount; i++) {
      const a = Math.random() * Math.PI * 2;
      const r = radius + 0.3 + Math.random() * 1.5;
      const y = -totalHeight / 2 + Math.random() * totalHeight;

      particlePositionsArr[i * 3] = Math.cos(a) * r;
      particlePositionsArr[i * 3 + 1] = y;
      particlePositionsArr[i * 3 + 2] = Math.sin(a) * r;

      const color = new THREE.Color().setHSL(0.55 + Math.random() * 0.2, 0.8, 0.5 + Math.random() * 0.3);
      particleColorsArr[i * 3] = color.r;
      particleColorsArr[i * 3 + 1] = color.g;
      particleColorsArr[i * 3 + 2] = color.b;
    }

    particleGeo.setAttribute("position", new THREE.BufferAttribute(particlePositionsArr, 3));
    particleGeo.setAttribute("color", new THREE.BufferAttribute(particleColorsArr, 3));

    const particleMat = new THREE.PointsMaterial({
      size: 0.04,
      vertexColors: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      transparent: true,
      opacity: 0.6,
    });

    const particles = new THREE.Points(particleGeo, particleMat);
    particles.name = "particles";
    helixGroup.add(particles);

    // ── 变异标记环 ──
    variantMarkersRef.current = [];
    segmentPositions.filter((sp) => sp.isVariant).forEach((sp, vi) => {
      const markerGeo = new THREE.TorusGeometry(0.3, 0.05, 8, 16);
      const markerMat = new THREE.MeshStandardMaterial({
        color: COLORS.variant,
        roughness: 0.2,
        metalness: 0.4,
        emissive: COLORS.variant,
        emissiveIntensity: 0.6,
      });
      const marker = new THREE.Mesh(markerGeo, markerMat);
      marker.position.set(sp.worldPos.x, sp.worldPos.y, sp.worldPos.z);
      marker.rotation.x = Math.PI / 2;
      marker.userData = { ...sp, variantIndex: vi };
      marker.name = "variant-marker";
      helixGroup.add(marker);
      variantMarkersRef.current.push(marker);
    });

    // ── 渲染循环 ──
    let lastTime = performance.now();
    const animate = () => {
      animationIdRef.current = requestAnimationFrame(animate);

      const now = performance.now();
      const dt = Math.min((now - lastTime) / 1000, 0.1);
      lastTime = now;

      if (autoRotate) {
        helixGroup.rotation.y += dt * 0.3;
      }

      // 粒子微动
      particles.rotation.y += dt * 0.1;
      particles.rotation.x += dt * 0.05;

      // 变异标记脉冲
      const t = performance.now() * 0.001;
      variantMarkersRef.current.forEach((m, i) => {
        const s = 1 + Math.sin(t * 3 + i * 1.5) * 0.15;
        m.scale.setScalar(s);
      });

      renderer.render(scene, camera);
    };
    animate();

    // ── 鼠标交互 ──
    let isDragging = false;
    let prevMouse = { x: 0, y: 0 };
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const onMouseDown = (e) => {
      isDragging = true;
      prevMouse = { x: e.clientX, y: e.clientY };
    };

    const onMouseMove = (e) => {
      if (isDragging) {
        const dx = e.clientX - prevMouse.x;
        const dy = e.clientY - prevMouse.y;
        helixGroup.rotation.y += dx * 0.005;
        helixGroup.rotation.x += dy * 0.003;
        helixGroup.rotation.x = Math.max(-0.8, Math.min(0.8, helixGroup.rotation.x));
        prevMouse = { x: e.clientX, y: e.clientY };
      }

      // 悬停检测
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(
        helixGroup.children.filter((c) => c.userData?.segmentIndex !== undefined),
        false
      );

      if (intersects.length > 0) {
        const obj = intersects[0].object;
        if (obj.userData?.segmentIndex !== undefined) {
          setHoveredSegment(obj.userData);
        } else {
          setHoveredSegment(null);
        }
      } else {
        setHoveredSegment(null);
      }
    };

    const onMouseUp = () => {
      isDragging = false;
    };

    const onWheel = (e) => {
      e.preventDefault();
      camera.position.z += e.deltaY * 0.005;
      camera.position.z = Math.max(3, Math.min(15, camera.position.z));
      camera.lookAt(0, 0, 0);
    };

    renderer.domElement.addEventListener("mousedown", onMouseDown);
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
    renderer.domElement.addEventListener("wheel", onWheel, { passive: false });

    // 响应式
    const handleResize = () => {
      const w = container.clientWidth;
      camera.aspect = w / height;
      camera.updateProjectionMatrix();
      renderer.setSize(w, height);
    };
    window.addEventListener("resize", handleResize);

    setLoading(false);

    return () => {
      cancelAnimationFrame(animationIdRef.current);
      renderer.dispose();
      scene.traverse((obj) => {
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) {
          if (Array.isArray(obj.material)) {
            obj.material.forEach((m) => m.dispose());
          } else {
            obj.material.dispose();
          }
        }
      });
      renderer.domElement.removeEventListener("mousedown", onMouseDown);
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
      renderer.domElement.removeEventListener("wheel", onWheel);
      window.removeEventListener("resize", handleResize);
      if (renderer.domElement.parentElement) {
        renderer.domElement.parentElement.removeChild(renderer.domElement);
      }
    };
  }, []);

  // ── 键盘交互 ──
  useEffect(() => {
    const onKey = (e) => {
      switch (e.key.toLowerCase()) {
        case "r":
          setAutoRotate((prev) => !prev);
          break;
        case "+":
        case "=":
          if (sceneRef.current) {
            // zoom in via camera
            const cam = sceneRef.current.children.find(
              (c) => c.isPerspectiveCamera
            );
          }
          break;
        default:
          break;
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <motion.div
      className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="bg-white rounded-3xl shadow-2xl w-full max-w-4xl overflow-hidden"
        initial={{ scale: 0.95, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.95, y: 20 }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* 头部 */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gradient-to-r from-primary/5 to-transparent">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary-light flex items-center justify-center">
              <Dna size={20} className="text-primary" />
            </div>
            <div>
              <h3 className="font-display font-bold text-[17px] text-text">
                {symbol} — DNA 双螺旋 3D 可视化
              </h3>
              <p className="text-[11px] text-text-tertiary">
                拖动旋转 · 滚轮缩放 · 悬停查看细节
                {pdb && ` · 参考 PDB: ${pdb.pdbId}`}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setAutoRotate(!autoRotate)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-semibold transition-colors cursor-pointer ${
                autoRotate
                  ? "bg-primary-light text-primary"
                  : "bg-gray-100 text-text-tertiary"
              }`}
              style={{ border: "none" }}
              title={autoRotate ? "停止旋转" : "自动旋转"}
            >
              <RotateCcw size={12} />
              {autoRotate ? "自动旋转中" : "手动"}
            </button>
            {pdb && (
              <a
                href={`https://www.rcsb.org/3d-view/${pdb.pdbId}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-semibold text-primary hover:bg-primary/5 transition-colors cursor-pointer"
                style={{ textDecoration: "none" }}
              >
                <ExternalLink size={12} />
                PDB 全结构
              </a>
            )}
            <button
              onClick={onClose}
              className="w-9 h-9 rounded-full hover:bg-gray-100 flex items-center justify-center text-text-tertiary cursor-pointer"
              style={{ background: "none", border: "none" }}
              aria-label="关闭"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* 3D 视口 */}
        <div className="relative bg-gradient-to-b from-gray-50 to-white" style={{ height: 480 }}>
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-50 z-10">
              <div className="text-center">
                <Loader2 size={32} className="mx-auto mb-3 animate-spin text-primary" />
                <p className="text-[13px] text-text-tertiary">生成 {symbol} DNA 3D 模型...</p>
              </div>
            </div>
          )}

          <div ref={mountRef} className="w-full h-full" />

          {/* 悬停提示 */}
          <AnimatePresence>
            {hoveredSegment && (
              <motion.div
                className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-white/90 backdrop-blur-sm rounded-xl px-4 py-2 shadow-lg border border-gray-200"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
              >
                <p className="text-[12px] font-mono font-semibold text-text">
                  片段 #{hoveredSegment.index + 1}
                  {hoveredSegment.isVariant && (
                    <span className="ml-2 text-red-500">🔴 变异位点</span>
                  )}
                </p>
                <p className="text-[11px] text-text-tertiary">
                  碱基对: {hoveredSegment.basePair} · 位置: Y={hoveredSegment.y.toFixed(1)}
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* 图例与控制区 */}
        <div className="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
          {/* 图例 */}
          <div className="flex flex-wrap items-center gap-4 mb-3">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-blue-500" />
              <span className="text-[11px] text-text-tertiary">A</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-amber-500" />
              <span className="text-[11px] text-text-tertiary">T</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-emerald-500" />
              <span className="text-[11px] text-text-tertiary">C</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-red-500" />
              <span className="text-[11px] text-text-tertiary">G</span>
            </div>
            <div className="w-px h-4 bg-gray-200" />
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full ring-2 ring-red-400 bg-red-100" />
              <span className="text-[11px] text-text-tertiary">变异位点（示意）</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-indigo-400/50" />
              <span className="text-[11px] text-text-tertiary">骨架</span>
            </div>
          </div>

          {/* 操作提示 */}
          <div className="flex flex-wrap items-center gap-3 text-[11px] text-text-tertiary">
            <span>🖱️ 拖动 = 旋转</span>
            <span>🖱️ 滚轮 = 缩放</span>
            <span>⌨️ R = {autoRotate ? "停止" : "开始"}自动旋转</span>
          </div>

          {/* 变异位点标签 */}
          {variants.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              <span className="text-[11px] font-semibold text-text-tertiary">
                检测到的变异位点:
              </span>
              {variants.map((rs) => (
                <button
                  key={rs}
                  onClick={() => setSelectedVariant(rs === selectedVariant ? null : rs)}
                  className={`px-3 py-1 rounded-full text-[11px] font-mono font-semibold cursor-pointer transition-all ${
                    selectedVariant === rs
                      ? "bg-red-500 text-white shadow"
                      : "bg-white text-text-secondary border border-gray-200 hover:border-red-300"
                  }`}
                  style={selectedVariant === rs ? { border: "none" } : {}}
                >
                  {rs}
                </button>
              ))}
            </div>
          )}

          {/* 位点科普弹窗 */}
          <AnimatePresence>
            {selectedVariant && (
              <motion.div
                className="bg-white rounded-xl border-l-4 border-red-400 p-3 mt-3"
                initial={{ opacity: 0, y: -6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
              >
                <p className="text-[12px] font-bold text-red-600 font-mono mb-1">
                  {selectedVariant} 科普讲解
                </p>
                <p className="text-[13px] text-text-secondary leading-relaxed">
                  {selectedVariant} 位于 {symbol} 基因的功能区域。该位点的变异可能影响蛋白结构或功能。
                  具体影响取决于基因型和变异类型（错义/无义/移码/剪接位点等）。
                </p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* 基因功能简介 */}
          {gene?.function && (
            <p className="text-[13px] text-text-secondary leading-relaxed mt-3 flex items-start gap-2">
              <Info size={15} className="text-primary mt-0.5 flex-shrink-0" />
              {gene.function}
            </p>
          )}

          {/* PDB 数据来源 */}
          {pdb && (
            <p className="text-[10px] text-text-tertiary mt-3 flex items-center gap-1">
              <Info size={10} />
              结构数据参考：{pdb.source} · PDB ID: {pdb.pdbId}
              {pdb.uniprot && ` · UniProt: ${pdb.uniprot}`}
              {" · 3D 可视化为本地生成的 DNA 双螺旋示意模型"}
            </p>
          )}
          {!pdb && (
            <p className="text-[10px] text-text-tertiary mt-3 flex items-center gap-1">
              <Info size={10} />
              {symbol} 暂无实验解析的蛋白结构 · 3D 可视化为本地生成的 DNA 双螺旋示意模型
            </p>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
