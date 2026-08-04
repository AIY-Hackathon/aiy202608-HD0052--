import { AnimatePresence, motion } from "framer-motion";
import { LocationProvider, useLocation } from "./components/layout/PageTransition";
import Navbar from "./components/layout/Navbar";
import Footer from "./components/layout/Footer";
import BreathingBackground from "./components/effects/BreathingBackground";
import GeneMap from "./pages/GeneMap";
import LifeSimulation from "./pages/LifeSimulation";
import LifestylePlanner from "./pages/LifestylePlanner";

const pages = {
  "gene-map": GeneMap,
  simulation: LifeSimulation,
  planner: LifestylePlanner,
};

function PageRenderer() {
  const { currentPage } = useLocation();
  const Page = pages[currentPage] || GeneMap;

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={currentPage}
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        transition={{ duration: 0.25, ease: "easeInOut" }}
      >
        <Page />
      </motion.div>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <LocationProvider>
      <BreathingBackground />
      <Navbar />
      <main className="min-h-screen">
        <PageRenderer />
      </main>
      <Footer />
    </LocationProvider>
  );
}
