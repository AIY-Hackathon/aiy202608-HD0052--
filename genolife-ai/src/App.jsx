import { AnimatePresence, motion } from "framer-motion";
import { LocationProvider, useLocation } from "./components/layout/PageTransition";
import { LanguageProvider } from "./i18n";
import Navbar from "./components/layout/Navbar";
import Footer from "./components/layout/Footer";
import BreathingBackground from "./components/effects/BreathingBackground";
import MusicPlayer from "./components/MusicPlayer";
import AIChatAssistant from "./components/AIChatAssistant";
import GeneMap from "./pages/GeneMap";
import GeneticActionMap from "./components/GeneticActionMap";
import ReportPage from "./pages/Report";
import HomePage from "./pages/HomePage";
import HealthyGrowthCenter from "./pages/HealthyGrowthCenter";
import GeneticAssistanceCenter from "./pages/GeneticAssistanceCenter";
import PrivacyCenter from "./pages/PrivacyCenter";
import EthicsReference from "./pages/EthicsReference";
import { Component, useEffect, useRef } from "react";

/* ── Error Boundary: catches ReactMarkdown / React 19 crashes ── */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center px-6">
            <p className="text-[16px] font-bold text-text mb-2">页面渲染出错</p>
            <p className="text-[13px] text-text-tertiary mb-4">
              {this.state.error?.message || "未知错误"}
            </p>
            <button
              onClick={() => { this.setState({ hasError: false, error: null }); window.location.reload(); }}
              className="px-4 py-2 rounded-full bg-primary text-white text-[13px] font-semibold cursor-pointer"
              style={{ border: "none" }}
            >
              刷新页面
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

const pages = {
  home: HomePage,
  "gene-map": GeneMap,
  "action-map": GeneticActionMap,
  report: ReportPage,
  "healthy-growth": HealthyGrowthCenter,
  "genetic-assistance": GeneticAssistanceCenter,
  privacy: PrivacyCenter,
  ethics: EthicsReference,
};

function PageRenderer() {
  const { currentPage, uploaded, consentCompleted } = useLocation();
  const initialPage = useRef(false);
  useEffect(() => {
    if (!initialPage.current && uploaded && currentPage === "home") {
      initialPage.current = true;
    }
  }, [currentPage, uploaded]);

  const Page = pages[currentPage] || HomePage;
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

function AppInner() {
  const { currentPage } = useLocation();

  return (
    <>
      <BreathingBackground />
      <Navbar />
      <main className="min-h-screen">
        <ErrorBoundary key={currentPage}>
          <PageRenderer />
        </ErrorBoundary>
      </main>
      <Footer />
      <MusicPlayer />
      <AIChatAssistant />
    </>
  );
}

export default function App() {
  return (
    <LanguageProvider>
      <LocationProvider>
        <AppInner />
      </LocationProvider>
    </LanguageProvider>
  );
}