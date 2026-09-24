import re
import requests
from concurrent.futures import ThreadPoolExecutor


class DrugInteractionService:
    def __init__(self):
        self.rxcui_exact_url = "https://rxnav.nlm.nih.gov/REST/rxcui.json"
        self.rxcui_approx_url = "https://rxnav.nlm.nih.gov/REST/approximateTerm.json"
        self.openfda_label_url = "https://api.fda.gov/drug/label.json"

    def process_interactions(self, current_drugs: list[str], new_drugs: list[str]) -> dict:
        clean_current = [d.strip() for d in current_drugs if d.strip()]
        clean_new = [d.strip() for d in new_drugs if d.strip()]
        
        all_drugs = list(dict.fromkeys(clean_current + clean_new))

        if len(all_drugs) < 2:
            return {"status": "success", "total_checked": len(all_drugs), "interactions": []}

        with ThreadPoolExecutor(max_workers=min(8, len(all_drugs))) as executor:
            fetched = executor.map(self._fetch_drug_info, all_drugs)
        drug_info = dict(zip(all_drugs, fetched))

        unchecked_drugs = [d for d in all_drugs if not drug_info[d][2]]

        raw_interactions = []
        seen_pairs = set()

        for i in range(len(all_drugs)):
            for j in range(i + 1, len(all_drugs)):
                d1, d2 = all_drugs[i], all_drugs[j]
                pair_key = tuple(sorted([d1.lower(), d2.lower()]))
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                resolved1, text1, _ = drug_info.get(d1, (d1, None, False))
                resolved2, text2, _ = drug_info.get(d2, (d2, None, False))
                hit = self._check_pair(d1, resolved1, text1, d2, resolved2, text2)
                if hit:
                    raw_interactions.append(hit)

        formatted_interactions = []
        for item in raw_interactions:
            d1, d2 = item["drug1"], item["drug2"]

            if d1 in clean_new and d2 in clean_new:
                relation_type = "NEW_VS_NEW"
                relation_label = "تعارض بين أدوية جديدة"
            elif (d1 in clean_current and d2 in clean_new) or (d1 in clean_new and d2 in clean_current):
                relation_type = "CURRENT_VS_NEW"
                relation_label = "تعارض بين أدوية المريض الحالية والدواء الجديد"
            else:
                relation_type = "CURRENT_VS_CURRENT"
                relation_label = "تعارض قائم مسبقاً بين أدوية المريض الحالية"

            formatted_interactions.append({
                "drug1": d1,
                "drug2": d2,
                "severity": "غير مصنّف (نص نشرة FDA حر، راجع description)",
                "description": item["description"],
                "source": item["source"],
                "relation_type": relation_type,
                "relation_label": relation_label,
            })

        return {
            "status": "success",
            "total_checked": len(all_drugs),
            "interactions": formatted_interactions,
            "unchecked_drugs": unchecked_drugs,
        }

    def _check_pair(
        self,
        drug1: str, resolved1: str, text1: str | None,
        drug2: str, resolved2: str, text2: str | None,
    ) -> dict | None:
        names_for_drug2 = {drug2, resolved2}
        names_for_drug1 = {drug1, resolved1}

        if text1 and any(self._name_mentioned(name, text1) for name in names_for_drug2):
            return {
                "drug1": drug1,
                "drug2": drug2,
                "description": self._trim(text1),
                "source": f"FDA label of {drug1} (openFDA)",
            }
        if text2 and any(self._name_mentioned(name, text2) for name in names_for_drug1):
            return {
                "drug1": drug1,
                "drug2": drug2,
                "description": self._trim(text2),
                "source": f"FDA label of {drug2} (openFDA)",
            }
        return None

    def _fetch_drug_info(self, drug_name: str) -> tuple[str, str | None, bool]:
        resolved_name = self._resolve_search_term(drug_name)
        text, checked_ok = self._fetch_drug_interactions_text(resolved_name)
        return resolved_name, text, checked_ok

    def _fetch_drug_interactions_text(self, query_name: str) -> tuple[str | None, bool]:
        search = (
            f'(openfda.generic_name:"{query_name}" OR '
            f'openfda.brand_name:"{query_name}" OR '
            f'openfda.substance_name:"{query_name}") '
            f'AND _exists_:drug_interactions'
        )
        try:
            response = requests.get(
                self.openfda_label_url,
                params={"search": search, "limit": 1},
                timeout=(6, 6),
            )
            if response.status_code != 200:
                return None, response.status_code == 404
            results = response.json().get("results", [])
            if not results:
                return None, True
            interactions = results[0].get("drug_interactions", [])
            return (" ".join(interactions) if interactions else None), True
        except requests.exceptions.RequestException as e:
            print(f"[drug_interactions] فشل الاتصال بـ openFDA لأجل '{query_name}': {e}")
            return None, False
        except Exception as e:
            print(f"[drug_interactions] خطأ غير متوقع أثناء جلب openFDA لأجل '{query_name}': {e}")
            return None, False

    def _resolve_search_term(self, drug_name: str) -> str:
        try:
            response = requests.get(
                self.rxcui_approx_url,
                params={"term": drug_name, "maxEntries": 1},
                timeout=(6, 6),
            )
            if response.status_code == 200:
                candidates = response.json().get("approximateGroup", {}).get("candidate", [])
                if candidates:
                    name = candidates[0].get("name") or candidates[0].get("candidateName")
                    if name:
                        return name
        except Exception as e:
            print(f"[drug_interactions] فشل الاتصال بـ RxNorm لأجل '{drug_name}': {e}")
        return drug_name

    @staticmethod
    def _name_mentioned(drug_name: str, text: str) -> bool:
        pattern = re.escape(drug_name)
        return re.search(pattern, text, re.IGNORECASE) is not None

    @staticmethod
    def _trim(text: str, max_len: int = 600) -> str:
        text = text.strip()
        return text if len(text) <= max_len else text[:max_len].rsplit(" ", 1)[0] + "…"