import datetime

from pydantic import BaseModel
from typing import List, Optional


class SearchAndSortMy(BaseModel):
    author: int
    shift: int
    amount_per_page: int
    search: Optional[str] = None
    sort_type: Optional[str] = None
    search_author: Optional[str] = None
    hard_register: Optional[bool] = False
    fuzzy_search: Optional[bool] = False
    reverse: Optional[bool] = False

    def __str__(self):
        return f'{self.search}_{self.sort_type}_{int(self.search_author)}_{int(self.hard_register)}_{int(self.fuzzy_search)}_{int(self.reverse)}'


class SearchAndSortGlobal(BaseModel):
    shift: int
    amount_per_page: int
    search: Optional[str] = None
    sort_type: Optional[str] = None
    search_author: Optional[bool] = None
    hard_register: Optional[bool] = False
    fuzzy_search: Optional[bool] = False
    reverse: Optional[bool] = False

    def __str__(self):
        return f'{self.search}_{self.sort_type}_{1 if self.search_author else 0}_{1 if self.hard_register else 0}_{1 if self.fuzzy_search else 0}_{1 if self.reverse else 0}'


class SearchOut(BaseModel):
    id: int
    name: str
    author: int
    date_creation: datetime.datetime
    latest_update: datetime.datetime
    is_star: bool
    average_rating: float
    count_views: int
    src_icon: str
    description: str

