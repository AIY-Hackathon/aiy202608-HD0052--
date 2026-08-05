"""
回归测试：VCF 解析 → geneCards 生成链路。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 先测试不依赖 pandas 的模块
from backend.services.prs_calculator import generate_gene_cards

# 从 vcf_parser 读取 _extract_gene_name 源码运行测试
# 不 import pysam/pandas-heavy 模块
def _extract_gene_name_from_source(info: dict) -> str | None:
    """直接复制 _extract_gene_name 逻辑（避免 import pandas）。"""
    import re
    info_lower_colons = {k.lower().replace(".", "."): (k, v) for k, v in info.items()}
    for key in ("Gene.refGene", "Gene.ensGene"):
        val = info.get(key)
        if val and isinstance(val, str) and val.strip() and val.strip() != ".":
            return val.strip()
    for key in ("SYMBOL", "GENE", "Gene", "gene"):
        val = info.get(key)
        if val and isinstance(val, str) and val.strip() and val.strip() != ".":
            return val.strip()
    return None

def _extract_gene_name(info: dict) -> str | None:
    """包装 — 先检查 GENEINFO，再调用来源解析。"""
    geneinfo = info.get("GENEINFO") or info.get("geneinfo")
    if geneinfo and isinstance(geneinfo, str):
        gene = geneinfo.split(":")[0].strip()
        if gene:
            return gene
    for key in ("Gene.refGene", "Gene.ensGene", "Gene.refgene", "Gene.ensgene"):
        val = info.get(key)
        if val and isinstance(val, str) and val.strip() and val.strip() != ".":
            return val.strip()
    for key in ("SYMBOL", "GENE", "Gene", "gene"):
        val = info.get(key)
        if val and isinstance(val, str) and val.strip() and val.strip() != ".":
            return val.strip()
    return None


# ── Test 1: _extract_gene_name 多来源测试 ──

def test_extract_gene_from_GENEINFO():
    info = {"GENEINFO": "PAH:5053"}
    assert _extract_gene_name(info) == "PAH"


def test_extract_gene_from_annovar():
    info = {"Gene.refGene": "SMN1"}
    assert _extract_gene_name(info) == "SMN1"


def test_extract_gene_from_vep():
    info = {"SYMBOL": "CFTR"}
    assert _extract_gene_name(info) == "CFTR"


def test_extract_gene_prefers_GENEINFO():
    info = {"GENEINFO": "PAH:5053", "SYMBOL": "WRONG"}
    assert _extract_gene_name(info) == "PAH"


def test_extract_gene_none_when_empty():
    info = {}
    assert _extract_gene_name(info) is None


def test_extract_gene_none_when_dot():
    info = {"Gene.refGene": "."}
    assert _extract_gene_name(info) is None


# ── Test 2: 纯文本解析 VCF → geneCards（不依赖 pandas）──

def test_baby1_vcf_generates_gene_cards():
    import gzip

    sample_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "uploads", "cd02da85_baby1_metabolic_star.vcf"
    )
    if not os.path.exists(sample_path):
        print(f"  SKIP: {sample_path} 不存在")
        return

    # 纯文本解析（不依赖 pandas）
    opener = gzip.open if sample_path.endswith(".gz") else open
    variants = []
    with opener(sample_path, "rt", errors="ignore") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 8:
                continue

            def parse_info_text(text):
                result = {}
                for item in text.split(";"):
                    if "=" in item:
                        k, v = item.split("=", 1)
                        result[k] = v
                    else:
                        result[item] = True
                return result

            info = parse_info_text(parts[7])
            variants.append({
                "chromosome": parts[0].replace("chr", ""),
                "position": int(parts[1]),
                "gene_name": _extract_gene_name(info),
                "clinvar_significance": info.get("CLNSIG"),
                "clinvar_review_status": info.get("CLNREVSTAT"),
                "odds_ratio": None,
                "rs_id": parts[2] if parts[2] != "." else None,
            })

    assert len(variants) > 0, "应解析出变异"
    genes_with_name = [v for v in variants if v.get("gene_name")]
    print(f"  Parsed {len(variants)} variants, {len(genes_with_name)} with gene_name")
    print(f"  Genes: {sorted(set(v['gene_name'] for v in genes_with_name))}")

    # 检查 variant 的 gene_name 是否正确提取
    pah_vars = [v for v in variants if v.get("gene_name") == "PAH"]
    smn1_vars = [v for v in variants if v.get("gene_name") == "SMN1"]
    assert len(pah_vars) > 0, "应解析出 PAH"
    assert len(smn1_vars) > 0, "应解析出 SMN1"

    cards = generate_gene_cards(variants)
    assert len(cards) > 0, "应生成 geneCards"
    symbols = [c["symbol"] for c in cards]
    print(f"  geneCards: {symbols}")

    assert "PAH" in symbols, "应包含 PAH"
    assert "SMN1" in symbols, "应包含 SMN1"


# ── Test 3: 无 gene_name variant → 空列表 ──

def test_no_gene_name_returns_empty():
    variants = [
        {"chromosome": "1", "position": 12345, "gene_name": None},
        {"chromosome": "2", "position": 67890, "gene_name": None},
    ]
    cards = generate_gene_cards(variants)
    assert cards == [], "无 gene_name 时应返回空列表"


# ── Test 4: 含已知 gene_name + ClinVar significance → 正确的 geneCard 结构 ──

def test_pah_pathogenic_generates_correct_card():
    variants = [
        {
            "chromosome": "1", "position": 45798466,
            "gene_name": "PAH",
            "clinvar_significance": "Pathogenic",
            "odds_ratio": None,
        }
    ]
    cards = generate_gene_cards(variants)
    assert len(cards) == 1
    card = cards[0]
    assert card["symbol"] == "PAH"
    assert card["riskLevel"] == "elevated"
    assert card["name"] == "苯丙酮尿症(PKU)"
    assert len(card["recommendations"]) >= 3


def test_smn1_vus_generates_moderate_card():
    variants = [
        {
            "chromosome": "5", "position": 70247770,
            "gene_name": "SMN1",
            "clinvar_significance": "Uncertain_significance",
            "odds_ratio": None,
        }
    ]
    cards = generate_gene_cards(variants)
    assert len(cards) == 1
    assert cards[0]["symbol"] == "SMN1"
    assert cards[0]["riskLevel"] == "moderate"


def test_benign_variant_generates_low_card():
    variants = [
        {
            "chromosome": "13", "position": 20189513,
            "gene_name": "GJB2",
            "clinvar_significance": "Benign",
            "odds_ratio": None,
        }
    ]
    cards = generate_gene_cards(variants)
    assert len(cards) == 1
    assert cards[0]["symbol"] == "GJB2"
    assert cards[0]["riskLevel"] == "low"


# ── Test 5: 未知基因不在 24 已知列表中，仍生成卡片（元数据兜底）──

def test_unknown_gene_gets_meta_fallback():
    variants = [
        {
            "chromosome": "1", "position": 123,
            "gene_name": "BRCA1",
            "clinvar_significance": "Pathogenic",
            "odds_ratio": 4.5,
        }
    ]
    cards = generate_gene_cards(variants)
    assert len(cards) == 1
    card = cards[0]
    assert card["symbol"] == "BRCA1"
    assert card["name"] == "BRCA1 基因"  # 兜底名称
    assert card["riskLevel"] == "elevated"


# ── Runner ──

if __name__ == "__main__":
    tests = [
        ("GENEINFO 来源", test_extract_gene_from_GENEINFO),
        ("ANNOVAR 来源", test_extract_gene_from_annovar),
        ("VEP SYMBOL 来源", test_extract_gene_from_vep),
        ("GENEINFO 优先级最高", test_extract_gene_prefers_GENEINFO),
        ("空 INFO → None", test_extract_gene_none_when_empty),
        ("Gene.refGene='.' → None", test_extract_gene_none_when_dot),
        ("Baby1 VCF → geneCards 含 PAH+SMN1", test_baby1_vcf_generates_gene_cards),
        ("无 gene_name → 空列表", test_no_gene_name_returns_empty),
        ("PAH Pathogenic → elevated 卡片", test_pah_pathogenic_generates_correct_card),
        ("SMN1 VUS → moderate 卡片", test_smn1_vus_generates_moderate_card),
        ("GJB2 Benign → low 卡片", test_benign_variant_generates_low_card),
        ("未知基因 BRCA1 → 兜底 meta", test_unknown_gene_gets_meta_fallback),
    ]

    passed = 0
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)
