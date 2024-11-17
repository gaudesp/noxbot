import difflib
import re

class Matcher:
  """Classe utilitaire pour rechercher et trier des éléments dans une liste par proximité avec une chaîne donnée."""

  # Static methods

  @staticmethod
  def normalize_text(text: str) -> str:
    """
    Normalise le texte en enlevant les caractères spéciaux et en réduisant les espaces multiples.

    :param text: Texte à normaliser.
    :type text: str
    :return: Texte normalisé.
    :rtype: str
    """
    normalized_text: str = re.sub(r"[-–_:,.]", " ", text).lower()  # Remplacer les symboles par des espaces.
    normalized_text = re.sub(r"\s+", " ", normalized_text).strip()  # Remplacer les espaces multiples par un seul.
    return normalized_text

  @staticmethod
  def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calcule la similarité entre deux chaînes de caractères.

    :param str1: Première chaîne.
    :type str1: str
    :param str2: Deuxième chaîne.
    :type str2: str
    :return: Un score de similarité entre 0 et 1.
    :rtype: float
    """
    return difflib.SequenceMatcher(None, str1, str2).ratio()

  @staticmethod
  def search_and_sort_by_string(
    search_string: str, 
    items: list[dict[str, str]], 
    key: str = 'name', 
    threshold: float = 0.4
  ) -> list[dict[str, str]]:
    """
    Recherche dans une liste d'éléments, normalise les chaînes de caractères et trie les résultats par similarité.

    :param search_string: La chaîne de recherche.
    :type search_string: str
    :param items: La liste d'éléments (dictionnaires) à comparer.
    :type items: list[dict[str, str]]
    :param key: La clé dans chaque dictionnaire dont la valeur sera comparée (par défaut 'name').
    :type key: str
    :param threshold: Le seuil de similarité minimum pour qu'un élément soit inclus.
    :type threshold: float
    :return: La liste triée d'éléments.
    :rtype: list[dict[str, str]]
    """
    normalized_search_string: str = Matcher.normalize_text(search_string)
    matched_items: dict[str, tuple[float, dict[str, str]]] = {}

    # Comparaison des éléments avec le texte de recherche
    for item in items:
      item_value: str = item.get(key, '')
      normalized_item_value: str = Matcher.normalize_text(item_value)

      # Comparaison de la chaîne recherchée avec celle de l'élément
      if normalized_search_string in normalized_item_value:
        similarity: float = Matcher.calculate_similarity(normalized_search_string, normalized_item_value)
        if similarity >= threshold:
          matched_items[item_value] = (similarity, item)

    # Tri des éléments en fonction de la similarité
    sorted_items: list[tuple[float, dict[str, str]]] = sorted(matched_items.values(), key=lambda x: x[0], reverse=True)
    return [item[1] for item in sorted_items]
