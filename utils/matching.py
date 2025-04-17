import difflib
import re

class Matcher:
  @staticmethod
  def normalize_text(text: str) -> str:
    normalized_text: str = re.sub(r"[-–_:,.]", " ", text).lower() 
    normalized_text = re.sub(r"\s+", " ", normalized_text).strip()
    return normalized_text

  @staticmethod
  def calculate_similarity(str1: str, str2: str) -> float:
    return difflib.SequenceMatcher(None, str1, str2).ratio()

  @staticmethod
  def search_and_sort_by_string(
    search_string: str, 
    items: list[dict[str, str]], 
    key: str = 'name', 
    threshold: float = 0.4
  ) -> list[dict[str, str]]:
    normalized_search_string: str = Matcher.normalize_text(search_string)
    matched_items: dict[str, tuple[float, dict[str, str]]] = {}
    for item in items:
      item_value: str = item.get(key, '')
      normalized_item_value: str = Matcher.normalize_text(item_value)
      if normalized_search_string in normalized_item_value:
        similarity: float = Matcher.calculate_similarity(normalized_search_string, normalized_item_value)
        if similarity >= threshold:
          matched_items[item_value] = (similarity, item)
    sorted_items: list[tuple[float, dict[str, str]]] = sorted(matched_items.values(), key=lambda x: x[0], reverse=True)
    return [item[1] for item in sorted_items]
