"""Chunk-based 目录对齐服务（简版：仅保留必要说明）"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import re
import difflib


class MappingService:
    @staticmethod
    def build_chunks(docx_structure: Dict[str, Any], target_chars: int = 800, overlap_chars: int = 200) -> List[Dict[str, Any]]:
        """按字符滑窗切块（返回 index/start_para/end_para/text）。"""
        # 取段落数组
        paragraphs: List[Dict[str, Any]] = docx_structure.get("paragraphs", [])
        # 提取纯文本并去掉首尾空白
        texts: List[str] = [(p.get("text") or "").strip() for p in paragraphs]
        chunks: List[Dict[str, Any]] = []   # 输出的块集合
        buf: List[str] = []                 # 当前窗口缓冲文本
        buf_len = 0                         # 当前窗口累计字符数
        start_idx = 0                       # 当前窗口起始段落索引
        for i, t in enumerate(texts):
            # 跳过空段
            if not t:
                continue
            # 新窗口记录起点
            if buf_len == 0:
                start_idx = i
            # 累加文本与长度
            buf.append(t)
            buf_len += len(t)
            # 达到目标长度则切块
            if buf_len >= target_chars:
                chunks.append({
                    "index": len(chunks),
                    "start_para": start_idx,
                    "end_para": i,
                    "text": "\n".join(buf),
                })
                # 构造重叠窗口尾巴，保留 overlap_chars 个字符
                overlap_text = "\n".join(buf)[-overlap_chars:]
                buf = [overlap_text]
                buf_len = len(overlap_text)
                start_idx = max(i, 0)
        # 收尾：缓冲区剩余内容也作为一个块
        if buf_len > 0:
            chunks.append({
                "index": len(chunks),
                "start_para": start_idx,
                "end_para": len(texts) - 1,
                "text": "\n".join(buf),
            })
        return chunks

    @staticmethod
    def map_outline_to_chunks(outline: Dict[str, Any], chunks: List[Dict[str, Any]], top_k: int = 3, min_score: float = 0.35) -> Dict[str, Any]:
        """节点↔块 多对多匹配，兜底保证全覆盖。"""
        outline_items: List[Dict[str, Any]] = outline.get("outline", [])
        flat_nodes: List[Dict[str, Any]] = []

        def flatten(items: List[Dict[str, Any]]):
            for item in items:
                # 扁平化目录树，取 id/title/description 用于匹配
                flat_nodes.append({
                    "id": item.get("id"),
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                })
                if item.get("children"):
                    flatten(item["children"]) 

        flatten(outline_items)

        node_to_chunks: Dict[str, List[Dict[str, Any]]] = {}   # 输出映射

        # 预计算：块的规范化文本
        norm_chunks = [MappingService._normalize_text(c.get("text", "")) for c in chunks]

        for node in flat_nodes:
            # 构造节点查询串：标题 + 描述
            title = node.get("title", "") or ""
            desc = node.get("description", "") or ""
            query = MappingService._normalize_text(f"{title} {desc}")
            scored: List[Tuple[int, float]] = []  # (chunk_index, score)
            for idx, cand in enumerate(norm_chunks):
                best_idx, score = MappingService._best_match(query, [cand])
                scored.append((idx, score))
            # 评分倒序
            scored.sort(key=lambda x: x[1], reverse=True)
            picks = [{"chunk_index": i, "score": round(s, 3)} for i, s in scored[:top_k] if s >= min_score]
            node_to_chunks[node["id"]] = picks

        # 统计已覆盖块
        covered = set()
        for picks in node_to_chunks.values():
            for p in picks:
                covered.add(p["chunk_index"])
        uncovered = [i for i in range(len(chunks)) if i not in covered]

        if uncovered and flat_nodes:
            # 兜底：为每个未覆盖块找最佳节点
            for idx in uncovered:
                cand = norm_chunks[idx]
                best_node_id: Optional[str] = None
                best_score: float = 0.0
                for node in flat_nodes:
                    query = MappingService._normalize_text(f"{node.get('title','')} {node.get('description','')}")
                    _, score = MappingService._best_match(query, [cand])
                    if score > best_score:
                        best_score = score
                        best_node_id = node["id"]
                if best_node_id is not None:
                    node_to_chunks.setdefault(best_node_id, []).append({
                        "chunk_index": idx,
                        "score": round(best_score, 3),
                    })

        # 重新计算覆盖集，确保返回的未覆盖块准确
        covered = set()
        for picks in node_to_chunks.values():
            for p in picks:
                covered.add(p["chunk_index"])

        return {
            "node_to_chunks": node_to_chunks,
            "uncovered_chunks": [i for i in range(len(chunks)) if i not in covered],
        }

    @staticmethod
    def map_outline_to_chunks_with_embeddings(
        outline: Dict[str, Any],
        chunks: List[Dict[str, Any]],
        embed_fn,  # Callable[[List[str]], List[List[float]]]
        top_k: int = 3,
        min_score: float = 0.45,
    ) -> Dict[str, Any]:
        """基于向量余弦相似度的节点↔块匹配。"""
        from math import sqrt

        def cosine(a, b):
            # 向量已归一化则可直接点积
            return sum(x * y for x, y in zip(a, b))

        outline_items: List[Dict[str, Any]] = outline.get("outline", [])
        flat_nodes: List[Dict[str, Any]] = []

        def flatten(items: List[Dict[str, Any]]):
            for item in items:
                flat_nodes.append({
                    "id": item.get("id"),
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                })
                if item.get("children"):
                    flatten(item["children"])

        flatten(outline_items)

        # 嵌入块
        chunk_texts = [(c.get("text") or "").strip() for c in chunks]
        chunk_vecs = embed_fn(chunk_texts) if chunk_texts else []

        node_to_chunks: Dict[str, List[Dict[str, Any]]] = {}

        for node in flat_nodes:
            query = f"{node.get('title','')} {node.get('description','')}".strip()
            if not query:
                node_to_chunks[node["id"]] = []
                continue
            q_vec = embed_fn([query])[0]

            scored: List[Tuple[int, float]] = []
            for idx, v in enumerate(chunk_vecs):
                s = cosine(q_vec, v)
                scored.append((idx, float(s)))
            scored.sort(key=lambda x: x[1], reverse=True)
            picks = [{"chunk_index": i, "score": round(s, 3)} for i, s in scored[:top_k] if s >= min_score]
            node_to_chunks[node["id"]] = picks

        # 覆盖统计与兜底同原逻辑
        covered = set()
        for picks in node_to_chunks.values():
            for p in picks:
                covered.add(p["chunk_index"])
        uncovered = [i for i in range(len(chunks)) if i not in covered]

        if uncovered and flat_nodes:
            for idx in uncovered:
                # 为未覆盖块找相似度最高的节点
                best_node_id: Optional[str] = None
                best_score: float = 0.0
                cand_vec = chunk_vecs[idx]
                for node in flat_nodes:
                    query = f"{node.get('title','')} {node.get('description','')}".strip()
                    if not query:
                        continue
                    q_vec = embed_fn([query])[0]
                    s = cosine(q_vec, cand_vec)
                    if s > best_score:
                        best_score = float(s)
                        best_node_id = node["id"]
                if best_node_id is not None:
                    node_to_chunks.setdefault(best_node_id, []).append({
                        "chunk_index": idx,
                        "score": round(best_score, 3),
                    })

        covered = set()
        for picks in node_to_chunks.values():
            for p in picks:
                covered.add(p["chunk_index"])

        return {
            "node_to_chunks": node_to_chunks,
            "uncovered_chunks": [i for i in range(len(chunks)) if i not in covered],
        }

    @staticmethod
    def merge_chunk_alignment_into_outline(outline: Dict[str, Any], chunks: List[Dict[str, Any]], mapping: Dict[str, Any]) -> Dict[str, Any]:
        """把映射结果写回目录节点，生成 assigned_chunks 与 source_content。"""
        node_to_chunks: Dict[str, List[Dict[str, Any]]] = mapping.get("node_to_chunks", {})

        import copy
        result = {"outline": copy.deepcopy(outline.get("outline", []))}

        def apply(items: List[Dict[str, Any]]):
            for item in items:
                cid = item.get("id")                      # 节点ID
                picks = node_to_chunks.get(cid, [])        # 节点对应的块列表
                item["assigned_chunks"] = picks           # 注入映射
                # 拼接已分配块文本（按块索引升序）
                texts: List[str] = []
                for p in sorted(picks, key=lambda x: x.get("chunk_index", 0)):
                    idx = p.get("chunk_index")
                    if isinstance(idx, int) and 0 <= idx < len(chunks):
                        t = (chunks[idx].get("text") or "").strip()
                        if t:
                            texts.append(t)
                if texts:
                    item["source_content"] = "\n\n".join(texts)
                if item.get("children"):
                    apply(item["children"]) 

        apply(result["outline"]) 
        return result

    @staticmethod
    def _normalize_text(text: str) -> str:
        """规范化文本（去编号/去符号/压缩空白/小写）。"""
        t = text.lower().strip()
        # 去常见编号前缀：1. / 1) / （一）/ IV. 等
        t = re.sub(r"^[\(（\[]?[\d一二三四五六七八九十ivxIVX\.\-\)）\]]+\s*", "", t)
        # 去标点与符号（保留字母/数字/中文/空格）
        t = re.sub(r"[^\w\u4e00-\u9fa5\s]+", " ", t)
        return re.sub(r"\s+", " ", t).strip()

    @staticmethod
    def _best_match(query: str, candidates: List[str]) -> Tuple[Optional[int], float]:
        """返回最佳匹配 (index, score)，分数=0.7*SequenceMatcher+0.3*Jaccard。"""
        best_idx: Optional[int] = None
        best_score: float = 0.0
        q_set = set(query.split()) if query else set()  # 查询词集合
        for idx, cand in enumerate(candidates):
            ratio = difflib.SequenceMatcher(None, query, cand).ratio()  # 序列相似度
            c_set = set(cand.split()) if cand else set()               # 候选词集合
            jaccard = (len(q_set & c_set) / len(q_set | c_set)) if (q_set or c_set) else 0.0
            score = 0.7 * ratio + 0.3 * jaccard                        # 融合得分
            if score > best_score:
                best_score = score
                best_idx = idx
        return best_idx, best_score


