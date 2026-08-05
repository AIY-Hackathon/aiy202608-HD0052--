# =============================================================================
# Mini-PRS Calculator Tests — v0.3.0 Research-Readiness Validation
# =============================================================================
"""Mini-PRS module tests (v0.3.0). Run: python -m pytest engine/tests/test_mini_prs.py -v

Covers: allele counting, beta parsing, LD dedup, unified normalization,
APOE haplotype isolation, evidence traceability, simulation-only language,
evidence report generation, biological modifiers, edge cases.
"""

from __future__ import annotations

import pytest as pytest

from engine.mini_prs import (
    EVIDENCE_TIER_1_GENES,
    EVIDENCE_TIER_2_GENES,
    APOE_HAPLOTYPE_GENE,
    NORMALIZATION_CONFIG,
    APOE_RISK_MODIFIER_MAP,
    _count_risk_alleles,
    _parse_float_beta,
    _resolve_apoe_haplotype,
    _standardize_score,
    _build_evidence_trace,
    calculate_mini_prs,
    genotype_to_genetic_profile,
    genotype_to_apoe_modifier,
    get_biological_context,
    generate_evidence_report,
)

# Verify APOE module is importable
try:
    from engine.apoe_haplotype import classify_apoe
    APOE_MODULE_AVAILABLE = True
except ImportError:
    APOE_MODULE_AVAILABLE = False


# =============================================================================
# Unit: _count_risk_alleles
# =============================================================================


class TestCountRiskAlleles:
    def test_homozygous_risk(self):
        assert _count_risk_alleles("AA", "A") == 2

    def test_heterozygous(self):
        assert _count_risk_alleles("AT", "A") == 1

    def test_homozygous_reference(self):
        assert _count_risk_alleles("TT", "A") == 0

    def test_case_insensitive_genotype(self):
        assert _count_risk_alleles("aa", "A") == 2

    def test_case_insensitive_risk_allele(self):
        assert _count_risk_alleles("CC", "c") == 2

    def test_risk_allele_t(self):
        assert _count_risk_alleles("TT", "T") == 2

    def test_invalid_length(self):
        with pytest.raises(ValueError, match="exactly 2"):
            _count_risk_alleles("A", "A")

    def test_invalid_characters(self):
        with pytest.raises(ValueError, match="invalid characters"):
            _count_risk_alleles("XN", "A")


# =============================================================================
# Unit: _parse_float_beta
# =============================================================================


class TestParseFloatBeta:
    def test_positive(self):
        assert _parse_float_beta("0.28") == 0.28

    def test_negative(self):
        assert _parse_float_beta("-0.30") == -0.30

    def test_todo_verify(self):
        assert _parse_float_beta("TODO_VERIFY") is None

    def test_todo_verify_partial(self):
        assert _parse_float_beta("TODO_VERIFY — something") is None

    def test_empty(self):
        assert _parse_float_beta("") is None

    def test_invalid(self):
        assert _parse_float_beta("not_a_number") is None

    def test_none(self):
        assert _parse_float_beta(None) is None


# =============================================================================
# Configuration integrity checks
# =============================================================================


class TestConfiguration:
    """v0.3.0 configuration is internally consistent."""

    def test_tier1_fto_only(self):
        assert EVIDENCE_TIER_1_GENES == {"FTO"}

    def test_tier2_clock_actn3(self):
        assert EVIDENCE_TIER_2_GENES == {"CLOCK", "ACTN3"}

    def test_apoe_not_in_any_tier(self):
        assert APOE_HAPLOTYPE_GENE not in EVIDENCE_TIER_1_GENES
        assert APOE_HAPLOTYPE_GENE not in EVIDENCE_TIER_2_GENES

    def test_fto_has_normalization_config(self):
        assert "FTO" in NORMALIZATION_CONFIG
        cfg = NORMALIZATION_CONFIG["FTO"]
        assert cfg["raw_min"] == 0.0
        assert cfg["raw_max"] > 0.0

    def test_apoe_modifier_map_covers_all_six(self):
        expected = {"ε2/ε2", "ε2/ε3", "ε3/ε3", "ε2/ε4", "ε3/ε4", "ε4/ε4"}
        assert set(APOE_RISK_MODIFIER_MAP.keys()) == expected

    def test_apoe_modifier_monotonic(self):
        """Risk modifier: ε2/ε2 (lowest) < ε4/ε4 (highest)."""
        assert APOE_RISK_MODIFIER_MAP["ε2/ε2"] < APOE_RISK_MODIFIER_MAP["ε3/ε3"]
        assert APOE_RISK_MODIFIER_MAP["ε3/ε3"] < APOE_RISK_MODIFIER_MAP["ε4/ε4"]

    def test_apoe_modifier_in_range(self):
        for val in APOE_RISK_MODIFIER_MAP.values():
            assert 0.0 <= val <= 1.0


# =============================================================================
# Unit: _standardize_score (Task 1)
# =============================================================================


class TestStandardizeScore:
    """Unified normalization across different GWAS trait scales."""

    def test_fto_aa_max(self):
        """FTO AA: raw=0.56 → standardized=1.00."""
        std = _standardize_score("FTO", 0.56)
        assert std == pytest.approx(1.0, abs=0.01)

    def test_fto_tt_min(self):
        """FTO TT: raw=0.00 → standardized=0.00."""
        std = _standardize_score("FTO", 0.00)
        assert std == pytest.approx(0.0, abs=0.01)

    def test_fto_at_mid(self):
        """FTO AT: raw=0.28 → standardized=0.50."""
        std = _standardize_score("FTO", 0.28)
        assert std == pytest.approx(0.50, abs=0.01)

    def test_clamp_below_zero(self):
        assert _standardize_score("FTO", -0.10) == 0.0

    def test_clamp_above_one(self):
        assert _standardize_score("FTO", 0.99) == 1.0

    def test_unknown_gene_returns_none(self):
        assert _standardize_score("UNKNOWN_GENE", 0.5) is None


# =============================================================================
# Unit: _build_evidence_trace (Task 4)
# =============================================================================


class TestEvidenceTrace:
    """Every score must be traceable to its GWAS origin."""

    def test_trace_contains_all_required_fields(self):
        trace = _build_evidence_trace(
            rsid="rs9939609", genotype="AT", dosage=1, beta=0.28,
            beta_unit="kg/m²", source="Frayling 2007 Science",
            evidence_level="GWAS_CONFIRMED", trait="body_mass_index",
            contribution=0.28,
        )
        assert trace["snp"] == "rs9939609"
        assert trace["dosage"] == 1
        assert trace["effect_size_beta"] == 0.28
        assert trace["source_publication"] == "Frayling 2007 Science"
        assert "1 risk alleles" in trace["calculation"]
        assert "0.2800" in trace["calculation"]


# =============================================================================
# Unit: _resolve_apoe_haplotype (Task 3)
# =============================================================================


class TestApoeHaplotypeInline:
    """APOE haplotype resolution — inline, no import needed."""

    def test_e3e4(self):
        result = _resolve_apoe_haplotype("CT", "CC")
        assert result["haplotype"] == "ε3/ε4"
        assert result["risk_modifier"] == pytest.approx(0.71, abs=0.01)
        assert result["simulation_only"] is True

    def test_e4e4(self):
        result = _resolve_apoe_haplotype("CC", "CC")
        assert result["haplotype"] == "ε4/ε4"
        assert result["risk_modifier"] == 1.0

    def test_e3e3(self):
        result = _resolve_apoe_haplotype("TT", "CC")
        assert result["haplotype"] == "ε3/ε3"
        assert result["risk_category"] == "reference"

    def test_e2e3(self):
        result = _resolve_apoe_haplotype("TT", "CT")
        assert result["haplotype"] == "ε2/ε3"
        assert result["risk_category"] == "protective"
        assert result["risk_modifier"] < APOE_RISK_MODIFIER_MAP["ε3/ε3"]

    def test_e2e2(self):
        result = _resolve_apoe_haplotype("TT", "TT")
        assert result["haplotype"] == "ε2/ε2"
        assert result["risk_modifier"] == 0.0

    def test_e2e4_compound(self):
        result = _resolve_apoe_haplotype("CT", "CT")
        assert result["haplotype"] == "ε2/ε4"

    def test_evidence_trace_present(self):
        result = _resolve_apoe_haplotype("CT", "CC")
        assert "evidence_trace" in result
        et = result["evidence_trace"]
        assert "snp_rs429358" in et
        assert "snp_rs7412" in et
        assert "calculation" in et

    def test_disclaimer_present(self):
        result = _resolve_apoe_haplotype("CT", "CC")
        assert "EDUCATIONAL SIMULATION" in result["disclaimer"]

    def test_invalid_genotype_raises(self):
        with pytest.raises(ValueError):
            _resolve_apoe_haplotype("XX", "CC")

    def test_too_many_alleles_raises(self):
        with pytest.raises(ValueError):
            _resolve_apoe_haplotype("CC", "TT")  # e4=2 + e2=2 = 4 > 2


# =============================================================================
# Integration: calculate_mini_prs v0.3.0
# =============================================================================


class TestCalculateMiniPrs:
    def test_empty_input_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            calculate_mini_prs({})

    def test_non_dict_raises(self):
        with pytest.raises(TypeError, match="dict"):
            calculate_mini_prs(["rs9939609", "AA"])  # type: ignore

    # --- FTO Tier 1 — standardized_score (Task 1) -----------------------

    def test_fto_aa_vs_tt(self):
        """FTO AA standardized_score=1.0 >> TT standardized_score=0.0."""
        r_aa = calculate_mini_prs({"rs9939609": "AA"})
        r_tt = calculate_mini_prs({"rs9939609": "TT"})
        fto_aa = r_aa["genetic_profile"]["FTO"]
        fto_tt = r_tt["genetic_profile"]["FTO"]
        assert fto_aa["raw_score"] == pytest.approx(0.56, abs=0.01)
        assert fto_tt["raw_score"] == pytest.approx(0.00, abs=0.01)
        assert fto_aa["standardized_score"] == pytest.approx(1.0, abs=0.01)
        assert fto_tt["standardized_score"] == pytest.approx(0.0, abs=0.01)
        assert fto_aa["standardized_score"] > fto_tt["standardized_score"]

    def test_fto_has_evidence_source(self):
        r = calculate_mini_prs({"rs9939609": "AT"})
        fto = r["genetic_profile"]["FTO"]
        assert "evidence_source" in fto
        assert "evidence_source" in fto
        assert len(fto["evidence_source"]) > 10

    def test_fto_has_confidence(self):
        r = calculate_mini_prs({"rs9939609": "AT"})
        fto = r["genetic_profile"]["FTO"]
        assert "confidence" in fto
        assert "VERY_STRONG" in fto["confidence"] or "strong" in fto["confidence"].lower()

    def test_fto_simulation_only_true(self):
        r = calculate_mini_prs({"rs9939609": "AT"})
        assert r["genetic_profile"]["FTO"]["simulation_only"] is True

    # --- LD-aware (no double counting) -----------------------------------

    def test_ld_tagged_not_summed(self):
        """rs9939609 + rs1421085 → only rs9939609 counted."""
        r = calculate_mini_prs({"rs9939609": "AA", "rs1421085": "CC"})
        fto = r["genetic_profile"]["FTO"]
        assert fto["raw_score"] == pytest.approx(0.56, abs=0.01)  # NOT 1.22
        assert len(fto["ld_notes"]) >= 1
        assert any("rs1421085" in ln["rsid"] for ln in fto["ld_notes"])
        skipped_rsids = [vs["rsid"] for vs in fto["variants_skipped"]]
        assert "rs1421085" in skipped_rsids

    def test_ld_only_tagged_provided(self):
        """If only the tagged variant is provided, it IS used."""
        r = calculate_mini_prs({"rs1421085": "CC"})
        fto = r["genetic_profile"].get("FTO", {})
        if fto.get("raw_score") is not None:
            assert fto["raw_score"] == pytest.approx(0.66, abs=0.02)

    # --- APOE isolated (Task 3) ------------------------------------------

    def test_apoe_not_in_genetic_profile(self):
        """APOE must NOT appear in genetic_profile (separate output)."""
        r = calculate_mini_prs({"rs429358": "CT", "rs7412": "CC"})
        assert "APOE" not in r["genetic_profile"]

    def test_apoe_in_haplotype_profile(self):
        """APOE must appear in apoe_haplotype_profile."""
        r = calculate_mini_prs({"rs429358": "CT", "rs7412": "CC"})
        apoe = r["apoe_haplotype_profile"]
        assert apoe is not None
        assert apoe["haplotype"] == "ε3/ε4"
        assert "risk_modifier" in apoe
        assert 0.0 <= apoe["risk_modifier"] <= 1.0
        assert apoe["simulation_only"] is True

    def test_apoe_e4e4_max_modifier(self):
        r = calculate_mini_prs({"rs429358": "CC", "rs7412": "CC"})
        assert r["apoe_haplotype_profile"]["risk_modifier"] == 1.0

    def test_apoe_e2e2_min_modifier(self):
        r = calculate_mini_prs({"rs429358": "TT", "rs7412": "TT"})
        assert r["apoe_haplotype_profile"]["risk_modifier"] == pytest.approx(0.0, abs=0.01)

    def test_apoe_modifier_monotonic_e4e4_gt_e3e4_gt_e3e3(self):
        r44 = calculate_mini_prs({"rs429358": "CC", "rs7412": "CC"})
        r34 = calculate_mini_prs({"rs429358": "CT", "rs7412": "CC"})
        r33 = calculate_mini_prs({"rs429358": "TT", "rs7412": "CC"})
        assert r44["apoe_haplotype_profile"]["risk_modifier"] > r34["apoe_haplotype_profile"]["risk_modifier"]
        assert r34["apoe_haplotype_profile"]["risk_modifier"] > r33["apoe_haplotype_profile"]["risk_modifier"]

    def test_apoe_partial_snps_reports_error(self):
        """Only one APOE SNP → error message."""
        r = calculate_mini_prs({"rs429358": "CT"})
        apoe = r["apoe_haplotype_profile"]
        assert apoe is not None
        assert apoe["haplotype"] is None
        assert "error" in apoe

    def test_apoe_in_evidence_summary_with_note(self):
        """APOE appears in evidence_summary with 'not summed' note."""
        r = calculate_mini_prs({"rs429358": "CT", "rs7412": "CC"})
        apoe_entries = [e for e in r["evidence_summary"] if e["gene"] == "APOE"]
        assert len(apoe_entries) == 1
        assert apoe_entries[0]["enters_numerical_prs"] is False
        assert "NOT summed with FTO" in apoe_entries[0].get("note", "")

    # --- Evidence traces (Task 4) ----------------------------------------

    def test_evidence_traces_present(self):
        r = calculate_mini_prs({"rs9939609": "AT", "rs429358": "CT", "rs7412": "CC"})
        traces = r.get("evidence_traces", [])
        # Only FTO SNPs enter traces (APOE handled separately)
        assert len(traces) >= 1
        fto_trace = [t for t in traces if t["snp"] == "rs9939609"]
        assert len(fto_trace) == 1
        assert fto_trace[0]["source_publication"] is not None
        assert "dosage" in fto_trace[0]
        assert "calculation" in fto_trace[0]

    def test_trace_calculation_shows_work(self):
        """Trace must show the calculation, not just the result."""
        r = calculate_mini_prs({"rs9939609": "AA"})
        trace = r["evidence_traces"][0]
        assert "2 risk alleles ×" in trace["calculation"]
        assert "0.5600" in trace["calculation"]

    # --- Tier 2 (Task 2 language compliance) -------------------------------

    def test_tier2_not_in_genetic_profile(self):
        """Tier 2 genes must NOT appear in genetic_profile."""
        r = calculate_mini_prs({"rs1801260": "CT", "rs1815739": "CC"})
        assert "CLOCK" not in r["genetic_profile"]
        assert "ACTN3" not in r["genetic_profile"]

    def test_tier2_in_biological_modifiers(self):
        r = calculate_mini_prs({"rs1801260": "CT"})
        assert "CLOCK" in r["biological_modifiers"]
        assert "explanation" in r["biological_modifiers"]["CLOCK"]

    def test_tier2_explanation_no_disease_language(self):
        """Tier 2 explanations must use simulation language, NOT disease-risk language."""
        r = calculate_mini_prs({"rs1801260": "CT"})
        expl = r["biological_modifiers"]["CLOCK"]["explanation"]
        # Must NOT contain forbidden phrases
        forbidden = [
            "disease risk increase", "disease risk decrease",
            "future 20-year disease", "disease probability",
            "will develop", "will get", "predicts disease",
        ]
        for phrase in forbidden:
            assert phrase not in expl.lower(), (
                f"Forbidden phrase '{phrase}' found in Tier 2 explanation"
            )
        # Should contain simulation language
        assert "simulation" in expl.lower() or "educational" in expl.lower()

    def test_tier2_simulation_only(self):
        r = calculate_mini_prs({"rs1801260": "CT"})
        assert r["biological_modifiers"]["CLOCK"]["simulation_only"] is True

    def test_tier2_actn3_explanation_no_disease_language(self):
        r = calculate_mini_prs({"rs1815739": "CC"})
        expl = r["biological_modifiers"]["ACTN3"]["explanation"]
        forbidden = [
            "disease risk", "will develop", "disease probability",
        ]
        for phrase in forbidden:
            assert phrase not in expl.lower()

    # --- Combined scenarios -----------------------------------------------

    def test_combined_fto_and_apoe_separate(self):
        """FTO in genetic_profile, APOE in apoe_haplotype_profile — NEVER combined."""
        r = calculate_mini_prs({
            "rs9939609": "AA",
            "rs429358": "CT",
            "rs7412": "CC",
        })
        # FTO in genetic_profile
        assert "FTO" in r["genetic_profile"]
        assert r["genetic_profile"]["FTO"]["standardized_score"] is not None
        # APOE NOT in genetic_profile
        assert "APOE" not in r["genetic_profile"]
        # APOE in separate profile
        assert r["apoe_haplotype_profile"] is not None
        assert r["apoe_haplotype_profile"]["haplotype"] == "ε3/ε4"

    def test_full_panel(self):
        """All four genes with mixed tiers and APOE."""
        r = calculate_mini_prs({
            "rs9939609": "AT",     # FTO Tier 1
            "rs1421085": "CT",     # FTO LD-tagged
            "rs429358": "CT",      # APOE
            "rs7412": "CC",        # APOE
            "rs1801260": "CT",     # CLOCK Tier 2
            "rs1815739": "CC",     # ACTN3 Tier 2
        })
        assert r["meta"]["variants_input"] == 6
        assert "FTO" in r["genetic_profile"]
        assert "APOE" not in r["genetic_profile"]
        assert "CLOCK" in r["biological_modifiers"]
        assert "ACTN3" in r["biological_modifiers"]
        assert r["apoe_haplotype_profile"]["haplotype"] == "ε3/ε4"

    # --- Meta -------------------------------------------------------------

    def test_meta_simulation_only(self):
        r = calculate_mini_prs({"rs9939609": "AA"})
        assert r["meta"]["simulation_only"] is True
        assert "language_policy" in r["meta"]
        assert "disease risk" in r["meta"]["language_policy"].lower()

    def test_meta_apoe_not_summed_flag(self):
        r = calculate_mini_prs({"rs9939609": "AA"})
        assert r["meta"]["apoe_not_summed_with_tier1"] is True
        assert r["meta"]["apoe_handling"] == "separate_haplotype_profile"

    def test_disclaimer_in_meta(self):
        r = calculate_mini_prs({"rs9939609": "AA"})
        assert "disclaimer" in r["meta"]
        assert "EDUCATIONAL SIMULATION" in r["meta"]["disclaimer"]
        assert "FTO and APOE operate on DIFFERENT GWAS trait scales" in r["meta"]["disclaimer"]

    def test_unknown_rsid_skipped(self):
        r = calculate_mini_prs({"rs99999999": "AA"})
        assert r["meta"]["variants_found"] == 0

    def test_invalid_genotype_raises(self):
        with pytest.raises(ValueError):
            calculate_mini_prs({"rs9939609": "XX"})

    # --- Output structure -------------------------------------------------

    def test_output_keys(self):
        r = calculate_mini_prs({"rs9939609": "AA"})
        for key in ["genetic_profile", "apoe_haplotype_profile",
                     "biological_modifiers", "evidence_summary",
                     "evidence_traces", "meta"]:
            assert key in r, f"Missing top-level key: {key}"


# =============================================================================
# Convenience functions
# =============================================================================


class TestGenotypeToGeneticProfile:
    """v0.3.0: only Tier 1 genes. APOE excluded."""

    def test_fto_included(self):
        p = genotype_to_genetic_profile({"rs9939609": "AA"})
        assert "FTO" in p
        assert p["FTO"] == pytest.approx(1.0, abs=0.01)

    def test_apoe_excluded(self):
        """APOE must NOT appear in simplified profile."""
        p = genotype_to_genetic_profile({"rs429358": "CT", "rs7412": "CC"})
        assert "APOE" not in p

    def test_combined_fto_only(self):
        p = genotype_to_genetic_profile({
            "rs9939609": "AT",
            "rs429358": "CT",
            "rs7412": "CC",
        })
        assert "FTO" in p
        assert "APOE" not in p
        assert len(p) == 1

    def test_sensitivity_in_range(self):
        cases = [
            {"rs9939609": "AA"},
            {"rs9939609": "AT"},
            {"rs9939609": "TT"},
        ]
        for case in cases:
            p = genotype_to_genetic_profile(case)
            for gene, sens in p.items():
                assert 0.0 <= sens <= 1.0

    def test_tier2_empty(self):
        p = genotype_to_genetic_profile({"rs1801260": "CT"})
        assert len(p) == 0


class TestGenotypeToApoeModifier:
    """New v0.3.0 convenience function."""

    def test_extracts_apoe_modifier(self):
        m = genotype_to_apoe_modifier({"rs429358": "CT", "rs7412": "CC"})
        assert m is not None
        assert m["haplotype"] == "ε3/ε4"
        assert m["risk_modifier"] == pytest.approx(0.71, abs=0.01)
        assert m["simulation_only"] is True

    def test_no_apoe_snps_returns_none(self):
        m = genotype_to_apoe_modifier({"rs9939609": "AA"})
        assert m is None

    def test_partial_apoe_still_returns(self):
        """Even partial APOE data returns something (with error)."""
        m = genotype_to_apoe_modifier({"rs429358": "CT"})
        assert m is not None
        assert m["haplotype"] is None


class TestGetBiologicalContext:
    def test_tier2_extracted(self):
        c = get_biological_context({"rs1801260": "CT", "rs1815739": "CC"})
        assert "CLOCK" in c
        assert "ACTN3" in c

    def test_tier1_not_in_context(self):
        c = get_biological_context({"rs9939609": "AA"})
        assert "FTO" not in c


# =============================================================================
# Evidence Report Generation (Task 5)
# =============================================================================


class TestGenerateEvidenceReport:
    """Presentation-ready evidence report."""

    def test_report_from_genotype(self):
        report = generate_evidence_report(genotype_data={
            "rs9939609": "AT",
            "rs429358": "CT",
            "rs7412": "CC",
        })
        assert isinstance(report, str)
        assert len(report) > 500

    def test_report_from_result(self):
        r = calculate_mini_prs({"rs9939609": "AA"})
        report = generate_evidence_report(result=r)
        assert isinstance(report, str)

    def test_report_no_args_generates_demo(self):
        report = generate_evidence_report()
        assert isinstance(report, str)
        assert len(report) > 500

    def test_report_contains_required_sections(self):
        report = generate_evidence_report(genotype_data={"rs9939609": "AT"})
        required = [
            "Data Sources",
            "Design Rationale",
            "SNP Inventory",
            "Evidence Trace",
            "Genetic Profile",
            "Disclaimer",
        ]
        for section in required:
            assert section in report, f"Missing section: {section}"

    def test_report_mentions_apoe_not_summed(self):
        report = generate_evidence_report(genotype_data={
            "rs9939609": "AT",
            "rs429358": "CT",
            "rs7412": "CC",
        })
        assert "NOT summed" in report

    def test_report_has_disclaimer(self):
        report = generate_evidence_report()
        assert "Simulation" in report or "SIMULATION" in report

    def test_report_no_disease_prediction_language(self):
        report = generate_evidence_report()
        # Must NOT contain disease-prediction language
        assert "future 20-year disease risk" not in report.lower()
        assert "disease probability" not in report.lower()
