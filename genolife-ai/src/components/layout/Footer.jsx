/**
 * Disclaimer bar — premium glass styling to match navbar.
 */
export default function Footer() {
  return (
    <footer className="border-t border-black/5 bg-white/40 backdrop-blur-xl">
      <div className="max-w-6xl mx-auto px-6 py-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <p className="text-[12px] text-text-tertiary leading-relaxed text-center sm:text-left">
          <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-amber-100 text-amber-600 text-[11px] mr-1.5 align-middle">!</span>
          This is an educational research project. It does not provide clinical diagnosis
          or medical advice. Consult a qualified healthcare professional for health concerns.
        </p>
        <p className="text-[11px] text-text-tertiary/70 font-medium whitespace-nowrap">
          GenoLife AI · Demo v1.0 · 2026
        </p>
      </div>
    </footer>
  );
}
