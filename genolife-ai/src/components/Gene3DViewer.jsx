import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Move3D, RotateCw, Info, Dna } from "lucide-react";

/**
 * Gene3DViewer — 基因三维可视化
 * =================================
 * 用 Canvas 绘制交互式 3D 风格的基因结构图：
 *   - DNA 双螺旋骨架（自动旋转 + 可拖动）
 *   - 关键变异位点（彩色球体，可点击查看科普讲解）
 *   - 染色体位置标注
 *
 * 交互：
 *   - 鼠标拖拽：旋转视角
 *   - 点击位点：弹出科普讲解
 *   - 滚轮：缩放
 */
export default function Gene3DViewer({ gene, onClose }) {
  const canvasRef = useRef(null);
  const [rotation, setRotation] = useState({ x: 0.4, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [dragging, setDragging] = useState(false);
  const [lastPos, setLastPos] = useState({ x: 0, y: 0 });
  const [selectedVariant, setSelectedVariant] = useState(null);
  const [autoRotate, setAutoRotate] = useState(true);

  // 关键变异位点（来自基因信息或默认示意）
  const variants = gene?.variants_found?.length
    ? gene.variants_found.map((rs, i) => ({
        rs,
        angle: (i / gene.variants_found.length) * Math.PI * 2,
        height: 0.4 + i * 0.25,
        info: getVariantInfo(gene.symbol, rs),
      }))
    : [
        { rs: "variant_1", angle: 0, height: 0.5, info: "关键功能位点" },
        { rs: "variant_2", angle: 2.1, height: 0.9, info: "调控区域" },
        { rs: "variant_3", angle: 4.2, height: 0.3, info: "编码区域" },
      ];

  // 绘制循环
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let raf;

    const draw = (time) => {
      const w = canvas.width;
      const h = canvas.height;
      ctx.clearRect(0, 0, w, h);

      const cx = w / 2;
      const cy = h / 2;
      const baseR = Math.min(w, h) * 0.28 * zoom;

      // 自动旋转
      let rotY = rotation.y;
      if (autoRotate && !dragging) {
        rotY += 0.008;
      }

      drawDnaHelix(ctx, cx, cy, baseR, rotY, rotation.x);
      drawVariantMarkers(ctx, cx, cy, baseR, rotY, variants, selectedVariant);
      drawLabels(ctx, cx, cy, baseR, gene?.symbol || "GENE");

      raf = requestAnimationFrame(draw);
    };

    raf = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(raf);
  }, [rotation, zoom, dragging, selectedVariant, variants, gene, autoRotate]);

  // 拖拽旋转
  const handlePointerDown = (e) => {
    setDragging(true);
    setAutoRotate(false);
    setLastPos({ x: e.clientX, y: e.clientY });
  };

  const handlePointerMove = (e) => {
    if (!dragging) return;
    const dx = e.clientX - lastPos.x;
    const dy = e.clientY - lastPos.y;
    setRotation((r) => ({ x: Math.max(-1.2, Math.min(1.2, r.x + dy * 0.01)), y: r.y + dx * 0.01 }));
    setLastPos({ x: e.clientX, y: e.clientY });
  };

  const handlePointerUp = () => setDragging(false);

  // 滚轮缩放
  const handleWheel = (e) => {
    e.preventDefault();
    setZoom((z) => Math.max(0.5, Math.min(2, z - e.deltaY * 0.001)));
  };

  // 点击位点检测（简化：点击画布任意位置模拟）
  const handleClick = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const baseR = Math.min(canvas.width, canvas.height) * 0.28 * zoom;

    // 检查是否点击到位点附近
    for (const v of variants) {
      const px = cx + baseR * Math.cos(v.angle) * 0.8;
      const py = cy - baseR * v.height * 0.9;
      if (Math.abs(x - px) < 30 && Math.abs(y - py) < 30) {
        setSelectedVariant(v);
        return;
      }
    }
    setSelectedVariant(null);
  };

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
        {/* 头部 */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gradient-to-r from-primary/5 to-transparent">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary-light flex items-center justify-center">
              <Dna size={20} className="text-primary" />
            </div>
            <div>
              <h3 className="font-display font-bold text-[17px] text-text">
                {gene?.symbol || "Gene"} 3D Structure
              </h3>
              <p className="text-[11px] text-text-tertiary">
                {gene?.name || "基因三维结构"} · 拖动旋转 · 滚轮缩放 · 点击位点查看讲解
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-9 h-9 rounded-full hover:bg-gray-100 flex items-center justify-center text-text-tertiary cursor-pointer"
            style={{ background: "none", border: "none" }}
            aria-label="关闭"
          >
            <X size={18} />
          </button>
        </div>

        {/* Canvas 3D */}
        <div
          className="relative"
          style={{ touchAction: "none" }}
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
          onPointerLeave={handlePointerUp}
          onWheel={handleWheel}
          onClick={handleClick}
        >
          <canvas
            ref={canvasRef}
            width={800}
            height={480}
            className="w-full block cursor-grab active:cursor-grabbing"
          />

          {/* 控制提示 */}
          <div className="absolute bottom-3 left-3 flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/80 backdrop-blur text-[11px] text-text-secondary shadow-sm">
            <Move3D size={12} className="text-primary" />
            拖动旋转
          </div>
          <button
            onClick={() => setAutoRotate((a) => !a)}
            className={`absolute bottom-3 right-3 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-semibold shadow-sm cursor-pointer ${
              autoRotate ? "bg-primary text-white" : "bg-white text-text-secondary"
            }`}
            style={{ border: "none" }}
          >
            <RotateCw size={12} />
            {autoRotate ? "自动旋转中" : "已暂停"}
          </button>

          {/* 位点科普弹出 */}
          <AnimatePresence>
            {selectedVariant && (
              <motion.div
                className="absolute top-3 left-1/2 -translate-x-1/2 max-w-md bg-white rounded-2xl shadow-xl border border-primary/10 p-4"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                <div className="flex items-center gap-2 mb-1.5">
                  <Info size={13} className="text-primary" />
                  <span className="font-mono text-[12px] font-bold text-primary">
                    {selectedVariant.rs}
                  </span>
                </div>
                <p className="text-[13px] text-text-secondary leading-relaxed">
                  {typeof selectedVariant.info === "string"
                    ? selectedVariant.info
                    : selectedVariant.info?.effect || "该位点参与基因功能调控。"}
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* 基因科普信息 */}
        <div className="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
          <div className="flex items-start gap-2">
            <Info size={15} className="text-primary mt-0.5 flex-shrink-0" />
            <p className="text-[13px] text-text-secondary leading-relaxed">
              {gene?.function || `该基因参与人体健康调控。不同变异位点影响不同的功能通路。`}
            </p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

/* ── 绘制 DNA 双螺旋 ── */
function drawDnaHelix(ctx, cx, cy, baseR, rotY, rotX) {
  const strands = 2;
  const turns = 3.5;
  const steps = 60;

  // 两条链 + 横档
  for (let s = 0; s < strands; s++) {
    ctx.beginPath();
    for (let i = 0; i <= steps; i++) {
      const t = i / steps;
      const y = cy - baseR * 1.6 + t * baseR * 3.2;
      const angle = t * turns * Math.PI * 2 + (s * Math.PI) + rotY;
      const r = baseR * 0.45 * Math.cos(angle);
      const depth = Math.sin(angle);
      const x = cx + r * Math.cos(rotX);

      const alpha = 0.35 + depth * 0.3;
      ctx.strokeStyle = s === 0 ? `rgba(30, 58, 95, ${alpha})` : `rgba(13, 148, 136, ${alpha})`;
      ctx.lineWidth = 2.5;

      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }

  // 横档（碱基对）
  for (let i = 0; i <= steps; i += 4) {
    const t = i / steps;
    const y = cy - baseR * 1.6 + t * baseR * 3.2;
    const angle = t * turns * Math.PI * 2 + rotY;
    const r = baseR * 0.45 * Math.cos(angle);
    const depth = Math.sin(angle);
    const x = cx + r * Math.cos(rotX);

    ctx.beginPath();
    ctx.strokeStyle = `rgba(100, 116, 139, ${0.3 + depth * 0.3})`;
    ctx.lineWidth = 1;
    ctx.moveTo(x, y);
    ctx.lineTo(cx - r * Math.cos(rotX), y);
    ctx.stroke();
  }
}

/* ── 绘制变异位点 ── */
function drawVariantMarkers(ctx, cx, cy, baseR, rotY, variants, selected) {
  variants.forEach((v) => {
    const y = cy - baseR * 1.6 + v.height * baseR * 3.2;
    const x = cx + baseR * 0.45 * Math.cos(v.angle + rotY) * 0.6;
    const isSelected = selected?.rs === v.rs;

    // 发光球
    const grad = ctx.createRadialGradient(x, y, 0, x, y, isSelected ? 16 : 12);
    grad.addColorStop(0, isSelected ? "rgba(16,185,129,0.9)" : "rgba(30,58,95,0.8)");
    grad.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(x, y, isSelected ? 16 : 12, 0, Math.PI * 2);
    ctx.fill();

    // 点击提示圆环
    if (isSelected) {
      ctx.beginPath();
      ctx.strokeStyle = "rgba(16,185,129,0.4)";
      ctx.lineWidth = 2;
      ctx.arc(x, y, 20, 0, Math.PI * 2);
      ctx.stroke();
    }
  });
}

/* ── 绘制染色体标签 ── */
function drawLabels(ctx, cx, cy, baseR, symbol) {
  // 底部染色体名
  ctx.fillStyle = "rgba(30, 58, 95, 0.5)";
  ctx.font = "bold 14px Inter, system-ui, sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(`${symbol} 基因结构示意`, cx, cy + baseR * 2.0);
}

/* ── 变异位点科普信息 ── */
function getVariantInfo(geneSymbol, rs) {
  const infos = {
    APOE: {
      rs429358: "该位点定义 APOE ε4 等位基因，与阿尔茨海默病风险升高相关。规律有氧运动可降低约 30% 认知风险。",
      rs7412: "该位点与 rs429358 共同决定 APOE ε2/ε3/ε4 基因型。ε2 通常具有保护作用。",
    },
    FTO: {
      rs9939609: "该位点影响食欲调控。A 等位基因携带者体重管理更具挑战，但规律运动可降低约 27% 影响。",
    },
    CLOCK: {
      rs1801260: "该位点影响昼夜节律稳定性。保持规律作息和固定就寝时间可优化生物钟。",
    },
    ACTN3: {
      rs1815739: "该位点决定快肌纤维功能。TT 基因型为耐力型，适合长距离有氧运动。",
    },
  };
  const geneInfo = infos[geneSymbol];
  if (geneInfo && geneInfo[rs]) return geneInfo[rs];
  return `该位点位于 ${geneSymbol} 基因的功能区域，参与蛋白编码或调控。`;
}
