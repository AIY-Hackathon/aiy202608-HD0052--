import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Info, Dna, Loader2, ExternalLink } from "lucide-react";
import PDB_MAPPING from "../data/pdbMapping";

/**
 * Gene3DViewer — 基因蛋白结构 3D 可视化（Mol* iframe 嵌入）
 * ============================================================
 * 使用 RCSB PDB 官方 Mol* 查看器，通过 iframe 嵌入蛋白 3D 结构。
 * 对于无实验结构的基因，自动回退到 AlphaFold DB 预测结构。
 *
 * Props:
 *   gene: { symbol, variants_found, function }
 *   onClose: () => void
 */
export default function Gene3DViewer({ gene, onClose }) {
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [selectedVariant, setSelectedVariant] = useState(null);
  const iframeRef = useRef(null);

  const symbol = gene?.symbol || "GENE";
  const pdb = PDB_MAPPING[symbol];
  const variants = gene?.variants_found?.length ? gene.variants_found : [];

  // Mol* viewer URL
  const getMolstarUrl = () => {
    if (!pdb) return null;
    const { pdbId, source } = pdb;
    if (source?.startsWith("AlphaFold")) {
      // AlphaFold: use UniProt-based URL
      const uniprot = pdb.uniprot || pdbId.replace("AF-", "").split("-")[0];
      return `https://alphafold.ebi.ac.uk/entry/${uniprot}`;
    }
    return `https://www.rcsb.org/3d-view/${pdbId}`;
  };

  const viewerUrl = getMolstarUrl();

  // iframe 加载完成
  const handleIframeLoad = () => {
    setLoading(false);
    setLoadError(false);
  };

  const handleIframeError = () => {
    setLoading(false);
    setLoadError(true);
  };

  // 超时保护：10秒后若仍未加载完成则显示回退
  useEffect(() => {
    if (!viewerUrl) {
      setLoading(false);
      setLoadError(true);
      return;
    }
    const timer = setTimeout(() => {
      if (loading) {
        setLoading(false);
        // 不标记为错误 — iframe 可能仍在加载
      }
    }, 12000);
    return () => clearTimeout(timer);
  }, [viewerUrl]);

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
                {symbol} — {pdb?.name || "蛋白 3D 结构"}
              </h3>
              <p className="text-[11px] text-text-tertiary">
                {pdb ? `${pdb.source} · 拖动旋转 · 滚轮缩放` : "蛋白结构 3D 可视化"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {viewerUrl && (
              <a
                href={viewerUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-semibold text-primary hover:bg-primary/5 transition-colors cursor-pointer"
                style={{ textDecoration: "none" }}
              >
                <ExternalLink size={12} />
                新窗口打开
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
        <div className="relative" style={{ height: 480 }}>
          {/* 加载中 */}
          {loading && viewerUrl && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-50 z-10">
              <div className="text-center">
                <Loader2 size={32} className="mx-auto mb-3 animate-spin text-primary" />
                <p className="text-[13px] text-text-tertiary">加载 {pdb?.name} 蛋白结构...</p>
                <p className="text-[11px] text-text-tertiary mt-1">来源：{pdb?.source}</p>
              </div>
            </div>
          )}

          {/* 无结构数据 */}
          {(!viewerUrl || loadError) && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-50">
              <div className="text-center max-w-md px-6">
                <Dna size={32} className="mx-auto mb-3 text-text-tertiary opacity-40" />
                <p className="text-[14px] font-semibold text-text mb-1">
                  {symbol} 暂无 3D 蛋白结构
                </p>
                <p className="text-[12px] text-text-tertiary leading-relaxed">
                  {pdb
                    ? "该蛋白结构暂无法加载。您可以点击下方链接在新窗口中查看。"
                    : "该基因目前没有公开的蛋白结构数据（RCSB PDB / AlphaFold DB）。"}
                </p>
                {gene?.function && (
                  <p className="mt-3 text-[12px] text-text-secondary bg-gray-100 rounded-xl p-3 text-left">
                    {gene.function}
                  </p>
                )}
                {viewerUrl && (
                  <a
                    href={viewerUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 mt-4 px-4 py-2 rounded-full bg-primary text-white text-[13px] font-semibold hover:bg-primary-600 transition-colors cursor-pointer"
                    style={{ textDecoration: "none" }}
                  >
                    <ExternalLink size={14} />
                    在新窗口中查看
                  </a>
                )}
              </div>
            </div>
          )}

          {/* iframe */}
          {viewerUrl && !loadError && (
            <iframe
              ref={iframeRef}
              src={viewerUrl}
              className="w-full h-full border-0"
              title={`${symbol} 3D Protein Structure`}
              onLoad={handleIframeLoad}
              onError={handleIframeError}
              loading="lazy"
            />
          )}
        </div>

        {/* 科普区域 */}
        <div className="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
          {/* 结构科普 */}
          {pdb?.description && (
            <div className="flex items-start gap-2 mb-3">
              <Info size={15} className="text-primary mt-0.5 flex-shrink-0" />
              <p className="text-[13px] text-text-secondary leading-relaxed">
                {pdb.description}
              </p>
            </div>
          )}

          {/* 变异位点标签 */}
          {variants.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3">
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
                className="bg-white rounded-xl border-l-4 border-red-400 p-3"
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
            <p className="text-[13px] text-text-secondary leading-relaxed mt-2">
              {gene.function}
            </p>
          )}

          {/* 数据来源 */}
          {pdb && (
            <p className="text-[10px] text-text-tertiary mt-3 flex items-center gap-1">
              <Info size={10} />
              结构数据来源：{pdb.source} · PDB ID: {pdb.pdbId}
              {pdb.uniprot && ` · UniProt: ${pdb.uniprot}`}
            </p>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
