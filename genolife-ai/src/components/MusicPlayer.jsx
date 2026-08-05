import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Music, Volume2, VolumeX } from "lucide-react";

/**
 * Helix Sunrise — 背景音乐播放器
 * 右下角悬浮玻璃态按钮，可开关背景音乐。
 * 关闭态：简洁音符图标；开启态：旋转唱片 + 音量控制。
 */
export default function MusicPlayer() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(0.35);
  const [showPanel, setShowPanel] = useState(false);
  const audioRef = useRef(null);
  const hideTimerRef = useRef(null);

  useEffect(() => {
    // 创建 Audio 实例（懒加载，避免首屏阻塞）
    audioRef.current = new Audio("/helix-sunrise.mp3");
    audioRef.current.loop = true;
    audioRef.current.volume = volume;
    return () => {
      audioRef.current?.pause();
      audioRef.current = null;
      clearTimeout(hideTimerRef.current);
    };
  }, []);

  useEffect(() => {
    if (audioRef.current) audioRef.current.volume = volume;
  }, [volume]);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      // 浏览器要求用户手势后才能播放
      audio.play().catch(() => {});
    }
    setIsPlaying(!isPlaying);
  };

  // 鼠标进入容器：显示面板，取消隐藏定时器
  const handleMouseEnter = () => {
    clearTimeout(hideTimerRef.current);
    setShowPanel(true);
  };

  // 鼠标离开容器：延迟隐藏（给用户时间把鼠标移回面板）
  const handleMouseLeave = () => {
    clearTimeout(hideTimerRef.current);
    hideTimerRef.current = setTimeout(() => setShowPanel(false), 300);
  };

  return (
    <div
      className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {/* 扩展面板：音量控制 */}
      <AnimatePresence>
        {showPanel && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.95 }}
            transition={{ duration: 0.18, ease: "easeOut" }}
            className="glass-nav rounded-2xl px-4 py-3 shadow-xl"
          >
            <div className="flex items-center gap-3">
              {/* 歌曲名 */}
              <div className="flex flex-col">
                <span className="text-[11px] font-bold text-text tracking-wide">
                  Helix Sunrise
                </span>
                <span className="text-[10px] text-text-tertiary">
                  {isPlaying ? "♪ Playing" : "Paused"}
                </span>
              </div>

              {/* 音量滑条 */}
              <div className="flex items-center gap-2">
                <VolumeX size={14} className="text-text-tertiary" />
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={volume}
                  onChange={(e) => setVolume(parseFloat(e.target.value))}
                  className="w-24 h-1 accent-accent cursor-pointer"
                  aria-label="音量"
                />
                <Volume2 size={14} className="text-text-tertiary" />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 主按钮：播放/暂停 */}
      <motion.button
        onClick={togglePlay}
        whileTap={{ scale: 0.92 }}
        className="relative flex items-center justify-center w-12 h-12 rounded-full glass-nav shadow-lg shadow-black/10 cursor-pointer group"
        style={{ background: "none", border: "none" }}
        aria-label={isPlaying ? "暂停背景音乐" : "播放背景音乐"}
        title={isPlaying ? "暂停背景音乐" : "播放背景音乐"}
      >
        {/* 开启时：旋转唱片 */}
        {isPlaying && (
          <motion.span
            className="absolute w-12 h-12 rounded-full border-2 border-accent/40"
            animate={{ rotate: 360 }}
            transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
          >
            <span className="absolute inset-0 rounded-full border border-accent/20" style={{ borderStyle: "dashed" }} />
          </motion.span>
        )}

        {/* 图标 */}
        <span className={`relative transition-colors duration-200 ${isPlaying ? "text-accent" : "text-text-secondary group-hover:text-text"}`}>
          <Music size={20} />
        </span>

        {/* 小圆点指示 */}
        <span
          className={`absolute top-0 right-0 w-3 h-3 rounded-full border-2 border-white transition-colors duration-200 ${
            isPlaying ? "bg-accent" : "bg-gray-300"
          }`}
        />
      </motion.button>
    </div>
  );
}
