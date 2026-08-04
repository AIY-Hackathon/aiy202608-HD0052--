import { motion } from "framer-motion";
import { useLocation } from "./PageTransition";

const links = [
  { id: "gene-map", label: "Genetic Profile", step: "01", icon: "🧬" },
  { id: "simulation", label: "Risk Simulation", step: "02", icon: "📊" },
  { id: "planner", label: "Health Plan", step: "03", icon: "📋" },
];

export default function Navbar() {
  const { currentPage, goTo } = useLocation();

  return (
    <nav className="glass-nav fixed top-0 inset-x-0 z-50">
      <div className="max-w-6xl mx-auto flex items-center justify-between px-6 h-16">
        {/* Logo */}
        <button
          onClick={() => goTo("gene-map")}
          className="flex items-center gap-2.5 cursor-pointer"
          style={{ background: "none", border: "none" }}
        >
          <span className="relative flex items-center justify-center w-9 h-9 rounded-xl bg-primary overflow-hidden shadow-lg shadow-primary/20">
            <span className="font-display text-white font-bold text-[15px]">G</span>
            <span className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent" />
          </span>
          <div className="flex flex-col leading-none">
            <span className="font-display font-bold text-[16px] text-text tracking-tight">
              GenoLife<span className="text-ai font-semibold">AI</span>
            </span>
            <span className="text-[10px] text-text-tertiary tracking-[0.12em] uppercase font-medium">
              Genetic Health
            </span>
          </div>
        </button>

        {/* Nav pills — numbered workflow */}
        <div className="flex items-center gap-1 bg-gray-100/60 rounded-full p-1">
          {links.map((link) => {
            const isActive = currentPage === link.id;
            return (
              <button
                key={link.id}
                onClick={() => goTo(link.id)}
                style={{ border: "none", background: isActive ? "white" : "none" }}
                className={`relative flex items-center gap-1.5 px-4 py-2 rounded-full transition-all duration-200 cursor-pointer ${
                  isActive
                    ? "bg-white text-primary shadow-sm"
                    : "text-text-tertiary hover:text-text"
                }`}
              >
                {/* Step number — always visible */}
                <span
                  className={`text-[11px] font-mono font-bold ${
                    isActive ? "text-accent" : "text-text-tertiary/60"
                  }`}
                >
                  {link.step}
                </span>
                {/* Label */}
                <span className="text-[12px] font-semibold">{link.label}</span>
                {/* Active indicator dot */}
                {isActive && (
                  <motion.span
                    layoutId="nav-active-dot"
                    className="absolute bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-accent"
                    transition={{ type: "spring", stiffness: 400, damping: 28 }}
                  />
                )}
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
