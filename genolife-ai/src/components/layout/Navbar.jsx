import { motion } from "framer-motion";
import { useLocation } from "./PageTransition";

/**
 * Glass-morphism fixed top navigation bar.
 */
export default function Navbar() {
  const { currentPage, goTo } = useLocation();

  const links = [
    { id: "gene-map", label: "Gene Map" },
    { id: "simulation", label: "Simulation" },
    { id: "planner", label: "Planner" },
  ];

  return (
    <nav className="glass-nav fixed top-0 inset-x-0 z-50">
      <div className="max-w-6xl mx-auto flex items-center justify-between px-6 h-16">
        {/* Logo */}
        <button
          onClick={() => goTo("gene-map")}
          className="flex items-center gap-2.5 group cursor-pointer"
          style={{ background: "none", border: "none" }}
        >
          <span className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white text-sm font-semibold font-display">
            G
          </span>
          <span className="font-display font-semibold text-[17px] text-text tracking-tight">
            GenoLife <span className="text-ai font-medium">AI</span>
          </span>
        </button>

        {/* Nav links */}
        <div className="flex items-center gap-1">
          {links.map((link) => {
            const isActive = currentPage === link.id;
            return (
              <button
                key={link.id}
                onClick={() => goTo(link.id)}
                className={`relative px-4 py-2 text-[15px] font-medium rounded-full transition-colors duration-200 cursor-pointer ${
                  isActive
                    ? "text-primary"
                    : "text-text-secondary hover:text-text"
                }`}
                style={{ background: "none", border: "none" }}
              >
                {link.label}
                {isActive && (
                  <motion.div
                    layoutId="nav-indicator"
                    className="absolute bottom-0 inset-x-2 h-0.5 rounded-full bg-primary"
                    transition={{ type: "spring", stiffness: 400, damping: 30 }}
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
