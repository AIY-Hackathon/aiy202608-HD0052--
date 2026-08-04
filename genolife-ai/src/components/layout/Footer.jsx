/**
 * Disclaimer bar shown at the bottom of every page.
 */
export default function Footer() {
  return (
    <footer className="border-t border-gray-200/60 bg-white/50 backdrop-blur-sm">
      <div className="max-w-6xl mx-auto px-6 py-4 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-text-tertiary">
        <p>
          <span className="font-medium text-risk-moderate">⚠️</span>{" "}
          This is an educational research project. It does not provide clinical diagnosis
          or medical advice. Consult a qualified healthcare professional for health concerns.
        </p>
        <p>GenoLife AI · Demo v1.0 · 2026</p>
      </div>
    </footer>
  );
}
