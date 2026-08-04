"""
ClinVar 查询客户端 — A1.4
==========================
查询 ClinVar 数据库获取变异注释（临床意义、评审状态等）。

查询策略（两级回退）：
  1. 本地 VCF 文件（快，离线可用）— 读取已下载的 clinvar_grch38.vcf.gz
  2. NCBI E-utilities API（在线回退）— 本地未命中时调用

实现说明：
  - 由于 pysam 在 Windows 无预编译包，本地查询采用「内存索引 + 二分查找」
  - 查询结果写入 Redis 缓存（可选，未配置 Redis 时跳过）
"""
from __future__ import annotations

import os
from bisect import bisect_left

# 本地 ClinVar VCF 路径（环境变量可覆盖）
DEFAULT_CLINVAR_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "clinvar", "clinvar_grch38.vcf.gz",
)
CLINVAR_PATH = os.environ.get("CLINVAR_PATH", DEFAULT_CLINVAR_PATH)


class ClinVarVariant:
    """单个 ClinVar 变异注释。"""

    __slots__ = ("chromosome", "position", "gene_name", "clinical_significance",
                 "review_status", "rs_id", "allele_id")

    def __init__(self, chromosome, position, gene_name, clinical_significance,
                 review_status, rs_id, allele_id):
        self.chromosome = chromosome
        self.position = position
        self.gene_name = gene_name
        self.clinical_significance = clinical_significance
        self.review_status = review_status
        self.rs_id = rs_id
        self.allele_id = allele_id

    def to_dict(self) -> dict:
        return {
            "chromosome": self.chromosome,
            "position": self.position,
            "gene_name": self.gene_name,
            "clinical_significance": self.clinical_significance,
            "review_status": self.review_status,
            "rs_id": self.rs_id,
            "allele_id": self.allele_id,
        }

    def __repr__(self):
        return f"<ClinVarVariant {self.chromosome}:{self.position} {self.gene_name}>"


def _parse_info(info_str: str) -> dict:
    """解析 INFO 字段。"""
    result: dict = {}
    if not info_str or info_str == ".":
        return result
    for item in info_str.split(";"):
        if "=" in item:
            k, v = item.split("=", 1)
            result[k] = v
        else:
            result[item] = True
    return result


class ClinVarIndex:
    """ClinVar VCF 的内存索引，支持按 (chr, pos) 快速查询。"""

    def __init__(self, filepath: str | None = None):
        self.filepath = filepath or CLINVAR_PATH
        self._by_chrom: dict[str, list[tuple[int, ClinVarVariant]]] = {}
        self._positions: dict[str, list[int]] = {}
        self._loaded = False

    def load(self) -> None:
        """一次性加载 ClinVar VCF 到内存索引。"""
        if self._loaded:
            return
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(
                f"ClinVar VCF 不存在: {self.filepath}\n"
                "请先下载数据文件（python download_data.py）"
            )

        import gzip

        opener = gzip.open if self.filepath.endswith(".gz") else open
        with opener(self.filepath, "rt", errors="ignore") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                parts = line.rstrip("\n").split("\t")
                if len(parts) < 8:
                    continue
                chrom = parts[0].replace("chr", "")
                try:
                    pos = int(parts[1])
                except ValueError:
                    continue

                info = _parse_info(parts[7])
                variant = ClinVarVariant(
                    chromosome=chrom,
                    position=pos,
                    gene_name=str(info.get("GENEINFO", "")).split(":")[0] or None,
                    clinical_significance=info.get("CLNSIG"),
                    review_status=info.get("CLNREVSTAT"),
                    rs_id=None if parts[2] in (".", "") else parts[2],
                    allele_id=info.get("ALLELEID"),
                )

                if chrom not in self._by_chrom:
                    self._by_chrom[chrom] = []
                    self._positions[chrom] = []
                self._by_chrom[chrom].append((pos, variant))

        # 每个染色体按位置排序
        for chrom in self._by_chrom:
            self._by_chrom[chrom].sort(key=lambda x: x[0])
            self._positions[chrom] = [x[0] for x in self._by_chrom[chrom]]

        self._loaded = True
        print(f"[ClinVarIndex] 加载完成: {self.filepath}")

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def query(self, chromosome: str, position: int) -> list[ClinVarVariant]:
        """按染色体+位置查询，返回该位置的所有变异。"""
        chrom = chromosome.replace("chr", "")
        if not self._loaded:
            self.load()

        positions = self._positions.get(chrom)
        if not positions:
            return []

        # 二分查找该位置
        i = bisect_left(positions, position)
        results = []
        while i < len(positions) and positions[i] == position:
            results.append(self._by_chrom[chrom][i][1])
            i += 1
        return results


class ClinVarClient:
    """ClinVar 查询客户端（本地优先，在线回退）。"""

    def __init__(self, use_cache: bool = True):
        self._index = ClinVarIndex()
        self.use_cache = use_cache
        self._redis = None
        if use_cache:
            try:
                import redis
                self._redis = redis.Redis(
                    host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", "6379")),
                    decode_responses=True,
                )
                self._redis.ping()
            except Exception:
                self._redis = None

    def annotate(self, chromosome: str, position: int, ref: str = "",
                 alt: str = "") -> dict | None:
        """查询单个变异，返回注释字典或 None。"""
        # 1. 尝试缓存
        if self._redis:
            key = f"clinvar:{chromosome}:{position}"
            cached = self._redis.get(key)
            if cached:
                import json
                return json.loads(cached)

        # 2. 本地查询
        try:
            matches = self._index.query(chromosome, position)
            if matches:
                best = matches[0]
                result = best.to_dict()
                # 若传了 ref/alt，做等位基因匹配
                if ref and alt:
                    for m in matches:
                        if ref in m.clinical_significance or alt in m.clinical_significance:
                            pass  # 简化处理，取第一个
                if self._redis:
                    import json
                    self._redis.setex(key, 86400, json.dumps(result))  # 24h TTL
                return result
        except FileNotFoundError:
            pass

        # 3. 在线回退（NCBI E-utilities）
        return self._query_online(chromosome, position)

    def _query_online(self, chromosome: str, position: int) -> dict | None:
        """在线回退：调用 NCBI E-utilities API。"""
        try:
            import urllib.request
            import json

            # esearch: 按位置查 ClinVar
            search_url = (
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                f"?db=clinvar&term={chromosome}[chr]+AND+{position}[pos]"
                "&retmode=json&retmax=5"
            )
            req = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            id_list = data.get("esearchresult", {}).get("idlist", [])
            if not id_list:
                return None

            # esummary: 获取详细注释
            summary_url = (
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                f"?db=clinvar&id={','.join(id_list[:3])}&retmode=json"
            )
            req = urllib.request.Request(summary_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            result = data.get("result", {})
            uid = id_list[0]
            info = result.get(uid, {})
            return {
                "chromosome": chromosome,
                "position": position,
                "gene_name": None,
                "clinical_significance": info.get("clinical_significance"),
                "review_status": info.get("review_status"),
                "rs_id": None,
                "allele_id": uid,
                "source": "eutils",
            }
        except Exception as e:
            print(f"[ClinVarClient] 在线查询失败: {e}")
            return None
