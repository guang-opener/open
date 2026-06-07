"""
多源检索模块 - 专利 + 期刊文献搜索
支持: Semantic Scholar, arXiv, CrossRef, Google Patents
"""

import json
import time
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional
from urllib.parse import quote, urlencode

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ============================================================
# 数据模型
# ============================================================

@dataclass
class SearchResult:
    """统一检索结果"""
    id: str                          # 唯一标识
    title: str                       # 标题
    title_cn: str = ""               # 中文标题 (如有)
    abstract: str = ""               # 摘要
    authors: list[str] = field(default_factory=list)
    year: int = 0
    source: str = ""                 # 来源: patent / journal
    source_name: str = ""            # 来源库名
    source_url: str = ""             # 原文链接
    patent_number: str = ""          # 专利号 (专利)
    patent_office: str = ""          # 专利局
    journal: str = ""                # 期刊名 (论文)
    doi: str = ""                    # DOI
    keywords: list[str] = field(default_factory=list)
    citation_count: int = 0
    relevance_score: float = 0.0     # 相关性评分 (后续填充)
    raw_data: dict = field(default_factory=dict)  # 原始数据

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================
# 基类
# ============================================================

class BaseSearcher:
    """检索器基类"""
    name: str = "base"
    base_url: str = ""
    session: requests.Session = None

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "TechReportBot/1.0 (mailto:research@example.com)"
        })

    def search(self, query: str, max_results: int = 15, **kwargs) -> list[SearchResult]:
        raise NotImplementedError

    def _safe_get(self, url: str, params: dict = None, **kwargs) -> Optional[requests.Response]:
        """带重试的 GET 请求"""
        for attempt in range(3):
            try:
                resp = self.session.get(url, params=params, timeout=15, **kwargs)
                if resp.status_code == 429:
                    wait = min(2 ** attempt, 10)
                    logger.warning(f"{self.name}: rate limited, waiting {wait}s...")
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                return resp
            except requests.RequestException as e:
                logger.warning(f"{self.name}: attempt {attempt+1}/3 failed: {e}")
                time.sleep(1)
        return None


# ============================================================
# Semantic Scholar
# ============================================================

class SemanticScholarSearcher(BaseSearcher):
    """Semantic Scholar API - 免费，无需 API Key"""
    name = "semanticscholar"
    base_url = "https://api.semanticscholar.org/graph/v1"

    def search(self, query: str, max_results: int = 15, year_from: int = None, year_to: int = None, **kwargs) -> list[SearchResult]:
        url = f"{self.base_url}/paper/search"
        params = {
            "query": query,
            "limit": min(max_results, 100),
            "fields": "paperId,title,abstract,year,authors,journal,externalIds,citationCount,url"
        }
        if year_from:
            params["year"] = f"{year_from}-{year_to or ''}"

        resp = self._safe_get(url, params=params)
        if not resp:
            return []

        results = []
        data = resp.json()
        for paper in data.get("data", []):
            ext_ids = paper.get("externalIds", {}) or {}
            authors_list = [a.get("name", "") for a in (paper.get("authors") or [])]

            result = SearchResult(
                id=f"ss_{paper.get('paperId', '')}",
                title=paper.get("title", ""),
                abstract=paper.get("abstract", "") or "",
                authors=authors_list,
                year=paper.get("year", 0) or 0,
                source="journal",
                source_name="Semantic Scholar",
                source_url=paper.get("url", ""),
                doi=ext_ids.get("DOI", ""),
                citation_count=paper.get("citationCount", 0) or 0,
                raw_data=paper
            )
            results.append(result)

        logger.info(f"Semantic Scholar: found {len(results)} results for '{query}'")
        return results


# ============================================================
# arXiv
# ============================================================

class ArxivSearcher(BaseSearcher):
    """arXiv API - 免费，无需 API Key"""
    name = "arxiv"
    base_url = "http://export.arxiv.org/api/query"

    def search(self, query: str, max_results: int = 15, **kwargs) -> list[SearchResult]:
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": min(max_results, 100),
            "sortBy": "relevance",
            "sortOrder": "descending"
        }

        resp = self._safe_get(self.base_url, params=params)
        if not resp:
            return []

        results = []
        soup = BeautifulSoup(resp.content, "xml")
        entries = soup.find_all("entry")

        for entry in entries[:max_results]:
            title = (entry.find("title") or {}).text.strip().replace("\n", " ") if entry.find("title") else ""
            abstract = (entry.find("summary") or {}).text.strip().replace("\n", " ") if entry.find("summary") else ""

            authors = []
            for author in entry.find_all("author"):
                name = author.find("name")
                if name:
                    authors.append(name.text.strip())

            arxiv_id = ""
            id_tag = entry.find("id")
            if id_tag:
                arxiv_id = id_tag.text.strip().split("/abs/")[-1]

            published = entry.find("published")
            year = int(published.text[:4]) if published else 0

            result = SearchResult(
                id=f"arxiv_{arxiv_id}",
                title=title,
                abstract=abstract,
                authors=authors,
                year=year,
                source="journal",
                source_name="arXiv",
                source_url=f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else "",
                raw_data={"arxiv_id": arxiv_id}
            )
            results.append(result)

        logger.info(f"arXiv: found {len(results)} results for '{query}'")
        return results


# ============================================================
# CrossRef
# ============================================================

class CrossrefSearcher(BaseSearcher):
    """CrossRef API - 免费，无需 API Key (礼貌使用即可)"""
    name = "crossref"
    base_url = "https://api.crossref.org/works"

    def search(self, query: str, max_results: int = 15, **kwargs) -> list[SearchResult]:
        params = {
            "query.bibliographic": query,
            "rows": min(max_results, 100),
            "sort": "relevance",
            "filter": "type:journal-article"
        }

        resp = self._safe_get(self.base_url, params=params)
        if not resp:
            return []

        results = []
        data = resp.json()
        items = data.get("message", {}).get("items", [])

        for item in items:
            title = ""
            title_list = item.get("title", [])
            if title_list:
                title = title_list[0]

            abstract = item.get("abstract", "") or ""
            # 清理 HTML 标签
            if abstract:
                abstract = BeautifulSoup(abstract, "html.parser").get_text()

            authors = []
            for author in item.get("author", []):
                given = author.get("given", "")
                family = author.get("family", "")
                if given or family:
                    authors.append(f"{given} {family}".strip())

            pub_parts = item.get("published", {}).get("date-parts", [[0]])
            year = pub_parts[0][0] if pub_parts and pub_parts[0] else 0

            journal = ""
            container = item.get("container-title", [])
            if container:
                journal = container[0]

            result = SearchResult(
                id=f"cr_{item.get('DOI', '')}",
                title=title,
                abstract=abstract,
                authors=authors,
                year=year,
                source="journal",
                source_name="CrossRef",
                source_url=f"https://doi.org/{item.get('DOI', '')}" if item.get("DOI") else "",
                doi=item.get("DOI", ""),
                journal=journal,
                citation_count=item.get("is-referenced-by-count", 0) or 0,
                raw_data=item
            )
            results.append(result)

        logger.info(f"CrossRef: found {len(results)} results for '{query}'")
        return results


# ============================================================
# Google Patents (通过网页搜索)
# ============================================================

class GooglePatentsSearcher(BaseSearcher):
    """Google Patents 检索 - 免费"""
    name = "google_patents"
    base_url = "https://patents.google.com/"

    def search(self, query: str, max_results: int = 15, **kwargs) -> list[SearchResult]:
        # 使用 Google Patents 的搜索 URL
        search_url = f"{self.base_url}?q={quote(query)}&num={min(max_results, 100)}&language=EN"

        resp = self._safe_get(search_url)
        if not resp:
            return []

        results = []
        soup = BeautifulSoup(resp.content, "html.parser")

        # 解析搜索结果
        result_items = soup.select("result") or soup.select(".result") or soup.select("[data-result]")

        if not result_items:
            # 尝试用结构化数据
            script_tags = soup.find_all("script", type="application/ld+json")
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and "itemListElement" in data:
                        for item in data["itemListElement"]:
                            item_data = item.get("item", item)
                            results.append(self._parse_patent_item(item_data, max_results))
                except (json.JSONDecodeError, AttributeError):
                    continue

        # 如果没解析到结构化数据，尝试 HTML 解析
        if not results:
            patent_links = soup.select("a[href*='/patent/']")
            seen = set()
            for link in patent_links[:max_results]:
                href = link.get("href", "")
                if "/patent/" not in href:
                    continue
                patent_num = href.split("/patent/")[-1].split("/")[0]
                if patent_num in seen:
                    continue
                seen.add(patent_num)

                title_el = link.select_one("h3, .title, [class*='title']")
                title = title_el.text.strip() if title_el else patent_num

                snippet_el = link.find_next("div", class_=lambda c: c and "snippet" in c.lower() if c else False)
                abstract = snippet_el.text.strip() if snippet_el else ""

                result = SearchResult(
                    id=f"gp_{patent_num}",
                    title=title,
                    abstract=abstract,
                    source="patent",
                    source_name="Google Patents",
                    source_url=f"https://patents.google.com/patent/{patent_num}/",
                    patent_number=patent_num,
                )
                results.append(result)

        logger.info(f"Google Patents: found {len(results)} results for '{query}'")
        return results

    def _parse_patent_item(self, item: dict, max_results: int) -> SearchResult:
        return SearchResult(
            id=f"gp_{item.get('name', '')}",
            title=item.get("name", ""),
            abstract=item.get("description", "")[:500] if item.get("description") else "",
            source="patent",
            source_name="Google Patents",
            source_url=item.get("url", ""),
            patent_number=item.get("name", ""),
            raw_data=item
        )


# ============================================================
# 统一搜索编排
# ============================================================

SEARCHER_MAP = {
    "semanticscholar": SemanticScholarSearcher,
    "arxiv": ArxivSearcher,
    "crossref": CrossrefSearcher,
    "google_patents": GooglePatentsSearcher,
}


def search_all(
    queries: list[str],
    sources: list[str] = None,
    max_per_source: int = 15,
    year_from: int = None,
    year_to: int = None,
    patent_queries: list[str] = None,
) -> list[SearchResult]:
    """
    执行多源多关键词检索

    Args:
        queries: 期刊检索关键词列表
        sources: 期刊检索源列表
        max_per_source: 每源每关键词最大结果数
        year_from: 起始年份
        year_to: 截止年份
        patent_queries: 专利检索关键词列表

    Returns:
        合并去重后的检索结果列表
    """
    all_results: list[SearchResult] = []
    seen_ids: set[str] = set()

    if sources is None:
        sources = ["semanticscholar", "arxiv", "crossref"]

    # 期刊检索
    for source_name in sources:
        searcher_cls = SEARCHER_MAP.get(source_name)
        if not searcher_cls:
            logger.warning(f"Unknown source: {source_name}, skipping")
            continue

        searcher = searcher_cls()
        for query in queries:
            try:
                results = searcher.search(
                    query,
                    max_results=max_per_source,
                    year_from=year_from,
                    year_to=year_to
                )
                for r in results:
                    key = r.id or r.title.lower().strip()
                    if key not in seen_ids:
                        seen_ids.add(key)
                        all_results.append(r)
                time.sleep(0.5)  # 礼貌间隔
            except Exception as e:
                logger.error(f"Error searching {source_name} for '{query}': {e}")

    # 专利检索
    patent_searcher = GooglePatentsSearcher()
    for pq in (patent_queries or []):
        try:
            results = patent_searcher.search(pq, max_results=max_per_source)
            for r in results:
                key = r.id or r.title.lower().strip()
                if key not in seen_ids:
                    seen_ids.add(key)
                    all_results.append(r)
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"Error searching patents for '{pq}': {e}")

    logger.info(f"Total unique results: {len(all_results)}")
    return all_results


def save_results(results: list[SearchResult], filepath: str):
    """将搜索结果保存为 JSON"""
    data = [r.to_dict() for r in results]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Results saved to {filepath}")


def load_results(filepath: str) -> list[SearchResult]:
    """从 JSON 加载搜索结果"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    results = []
    for d in data:
        # 处理 raw_data 中的 None 值
        d.pop("raw_data", None)
        results.append(SearchResult(**{k: v for k, v in d.items() if k in SearchResult.__dataclass_fields__}))
    return results


# ============================================================
# 便捷测试入口
# ============================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    # 测试检索
    results = search_all(
        queries=["REBCO coated conductor joint"],
        sources=["semanticscholar", "arxiv"],
        max_per_source=5,
        patent_queries=["superconducting tape joint"]
    )

    for r in results[:10]:
        print(f"[{r.source_name}] {r.title[:80]}... ({r.year})")
        if r.abstract:
            print(f"    {r.abstract[:150]}...")
        print()

    save_results(results, "test_results.json")
    print(f"Total: {len(results)} results saved.")
