import { AnimatePresence, motion } from "framer-motion";
import { LocationProvider, useLocation } from "./components/layout/PageTransition";
import { LanguageProvider } from "./i18n";
import Navbar from "./components/layout/Navbar";
import Footer from "./components/layout/Footer";
import BreathingBackground from "./components/effects/BreathingBackground";
import MusicPlayer from "./components/MusicPlayer";
import AIChatAssistant from "./components/AIChatAssistant";
import GeneMap from "./pages/GeneMap";
import LifeSimulation from "./pages/LifeSimulation";
import ReportPage from "./pages/Report";
import HomePage from "./pages/HomePage";
import HealthyGrowthCenter from "./pages/HealthyGrowthCenter";
import GeneticAssistanceCenter from "./pages/GeneticAssistanceCenter";
import PrivacyCenter from "./pages/PrivacyCenter";
import EthicsReference from "./pages/EthicsReference";
import { useEffect, useRef } from "react";

const pages = {
  home: HomePage,
  "gene-map": GeneMap,
  simulation: LifeSimulation,
  report: ReportPage,
  "healthy-growth": HealthyGrowthCenter,
  "genetic-assistance": GeneticAssistanceCenter,
  privacy: PrivacyCenter,
  ethics: EthicsReference,
};

function PageRenderer() {
  const { currentPage, uploaded, consentCompleted } = useLocation();
  // 如果用户已上传过报告（localStorage 有 active report），自动跳转到基因分析页
  const initialPage = useRef(false);
  useEffect(() => {
    if (!initialPage.current && uploaded && currentPage === "home") {
      initialPage.current = true;
      // 不强制跳转 — 用户可能想留在首页
    }
  }, [currentPage, uploaded]);

  const Page = pages[currentPage] || HomePage;

  // 基因分析页面需要先完成知情同意（每次会话）
  const needsConsent = currentPage === "gene-map" && !consentCompleted;

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={currentPage}
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        transition={{ duration: 0.25, ease: "easeInOut" }}
      >
        {needsConsent ? (
          <GeneMap />
        ) : (
          <Page />
        )}
      </motion.div>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <LanguageProvider>
      <LocationProvider>
        <BreathingBackground />
        <Navbar />
        <main className="min-h-screen">
          <PageRenderer />
        </main>
        <Footer />
        <MusicPlayer />
        <AIChatAssistant />
      </LocationProvider>
    </LanguageProvider>
  );
}