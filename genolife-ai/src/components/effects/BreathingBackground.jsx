import { motion } from "framer-motion";

/**
 * Breathing ambient background — two large blurred gradient orbs.
 */
export default function BreathingBackground() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
      {/* Top-left orb */}
      <div
        className="breathing-bg-1 absolute rounded-full"
        style={{
          width: "640px",
          height: "640px",
          background: "radial-gradient(circle, rgba(30,58,95,0.12) 0%, transparent 70%)",
          top: "-10%",
          left: "-10%",
          filter: "blur(80px)",
        }}
      />
      {/* Bottom-right orb */}
      <div
        className="breathing-bg-2 absolute rounded-full"
        style={{
          width: "560px",
          height: "560px",
          background: "radial-gradient(circle, rgba(13,148,136,0.10) 0%, transparent 70%)",
          bottom: "-5%",
          right: "-8%",
          filter: "blur(80px)",
        }}
      />
    </div>
  );
}
