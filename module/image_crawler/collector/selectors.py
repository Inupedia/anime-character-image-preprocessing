from typing import Set
from requests.models import Response


def selectPage(response: Response) -> Set[str]:
    """[summary]
    url: https://www.pixiv.net/ajax/illust/xxxx/pages?lang=zh
    collect all image urls from (page.json)

    Returns:
        Set[str]: urls
    """
    group = set()
    for url in response.json()["body"]:
        group.add(url["urls"]["original"])
    return group


def selectUser(response: Response) -> Set[str]:
    """[summary]
    url: https://www.pixiv.net/ajax/user/23945843/profile/all?lang=zh
    collect all illust_id (image_id) from (user.json)

    Returns:
        Set[str]: illust_id (image_id)
    """
    return set(response.json()["body"]["illusts"].keys())


def selectKeyword(response: Response) -> Set[str]:
    """[summary]
    url: https://www.pixiv.net/ajax/search/artworks/{xxxxx}?word={xxxxx}&order=popular_d&mode=all&p=1&s_mode=s_tag_full&type=all&lang=zh"
    collect all illust_id (image_id) from (keyword.json)

    Returns:
        Set[str]: illust_id (image_id)
    """
    # NOTE: id of disable artwork is int (not str)
    id_group: Set[str] = set()
    for artwork in response.json()["body"]["illustManga"]["data"]:
        id_group.add(artwork["id"])
    return id_group
