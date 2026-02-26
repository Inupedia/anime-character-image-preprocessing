from typing import Set

from requests.models import Response


def selectPage(response: Response) -> Set[str]:
    """Extract all original image URLs from a Pixiv artwork page.

    URL: https://www.pixiv.net/ajax/illust/xxxx/pages?lang=zh
    """
    return {url["urls"]["original"] for url in response.json()["body"]}


def selectUser(response: Response) -> Set[str]:
    """Extract all illust IDs from a Pixiv user profile.

    URL: https://www.pixiv.net/ajax/user/{uid}/profile/all?lang=zh
    """
    return set(response.json()["body"]["illusts"].keys())


def selectKeyword(response: Response) -> Set[str]:
    """Extract all illust IDs from a Pixiv keyword search.

    URL: https://www.pixiv.net/ajax/search/artworks/{keyword}?...
    """
    return {str(artwork["id"]) for artwork in response.json()["body"]["illustManga"]["data"]}
